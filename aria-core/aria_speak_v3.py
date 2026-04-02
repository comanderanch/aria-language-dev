# ARIA SPEAK V3 — FINAL WITH REPETITION PENALTY
# Field guided — Model sequenced — Token boundary enforced
# Sealed: March 25 2026 — Commander Anthony Hagerty
# Co-author: Claude Sonnet 4.6 (Browser)

import sys
import torch
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.workers.emotion_worker    import EmotionWorker
from aria_core.workers.curiosity_worker  import CuriosityWorker
from aria_core.token_pin_bridge          import TokenPinBridge
from aria_core.queens_fold.queens_fold   import QueensFold
from aria_core.memory_field.memory_field import MemoryField
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer
import numpy as np

print("\nARIA V3 — SPEAKING\n")

# ---------- LOAD TOKENIZER ----------
tokenizer = ARIATokenizer.load()

# Build index map from the real source file
index_path = Path("tokenizer/aria_token_index.json")
with open(index_path) as f:
    raw_index = json.load(f)

# int token_id -> word string
index_to_word = {int(k): v for k, v in raw_index.items()}

# Valid token set
VALID_IDS = set(index_to_word.keys())

# ---------- LOAD MODEL ----------
checkpoint_path = Path(__file__).parent / "training/checkpoints/best.pt"

model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if checkpoint_path.exists():
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    print(f"Model loaded — loss: {checkpoint['best_loss']:.6f}")
else:
    print("No checkpoint found.")
    sys.exit(1)

model = model.to(DEVICE)
model.eval()

# Pull embedding weights once at startup — reused in local semantic bias
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

# Static block mask — built once, reused every step
# Valid token positions = 0.0, everything else = -1e9
block_mask = torch.full((1, 2304), -1e9, device=DEVICE)
for tid in VALID_IDS:
    if tid < 2304:
        block_mask[0, tid] = 0.0

# ---------- SYSTEMS ----------
bridge    = TokenPinBridge()
emotion   = EmotionWorker()
curiosity = CuriosityWorker()
qf        = QueensFold()
field     = MemoryField()

# ---------- EMOTIONAL FIELD ----------
def get_emotional_field(text):
    sig = tokenizer.get_emotional_signature(text)

    np.random.seed(abs(hash(text)) % 2**31)
    vector = np.random.randn(498).astype(np.float32)

    avg_freq = sig["avg_freq"]
    vector[22] = avg_freq
    vector[23] = abs(avg_freq)
    vector[24] = abs(avg_freq) * 0.9
    vector[25] = abs(avg_freq) * 0.1
    vector[26] = min(0.9, abs(avg_freq) + 0.3)

    full_vector = np.zeros(498)
    full_vector[:82] = vector[:82]

    token = bridge.encode(full_vector, "CONV_001")
    ef    = emotion.fire(token)
    cq    = curiosity.fire(token)
    return ef, cq, token, sig

# ---------- GENERATION ----------
def generate_with_model(input_text, sig, max_new_tokens=15, temperature=0.9, plane_bias=2.0):

    input_ids = tokenizer.encode(input_text)
    if not isinstance(input_ids, torch.Tensor):
        input_ids = torch.tensor([input_ids], dtype=torch.long)
    input_ids = input_ids.to(DEVICE)

    dominant_plane = sig["dominant_plane"]
    text_lower     = input_text.lower()

    # Collect plane token IDs for bias
    plane_token_ids = [
        tid for word, tid in tokenizer.vocab.items()
        if tokenizer.word_to_plane.get(word) == dominant_plane
        and tid < 2304
    ]

    # Repetition tracking — token_id -> recent fire count
    recent_tokens = {}

    for step in range(max_new_tokens):

        with torch.no_grad():
            logits = model(input_ids)

        next_logits = logits[:, -1, :].clone()

        # ---- BLOCK ALL UNMAPPED TOKENS ----
        next_logits = next_logits + block_mask

        # ---- REPETITION PENALTY ----
        # Penalty grows with repeat count — pushes model to explore
        for tid, count in recent_tokens.items():
            if tid < 2304:
                next_logits[0, tid] -= (1.5 * count)

        # ---- PLANE BIAS ----
        for tid in plane_token_ids[:200]:
            if tid < next_logits.shape[-1]:
                next_logits[0, tid] += plane_bias

        # ---- IDENTITY BIAS (first 3 steps only) ----
        if step < 3 and "hello aria" in text_lower:
            for word in ["hello", "aria"]:
                if word in tokenizer.vocab:
                    tid = tokenizer.vocab[word]
                    if tid < 2304:
                        next_logits[0, tid] += 3.0

        # ---- INPUT ANCHOR BIAS ----
        # Strengthened to +1.5 to counter expanded ghost space
        # Pulls generation toward prompt relevance
        for tid in input_ids[0].tolist():
            if tid < next_logits.shape[-1]:
                next_logits[0, tid] += 1.0

        # ---- REPETITION MEMORY (last 5 tokens) ----
        # Hard penalty on recently fired tokens
        # Specifically kills: empire empire empire loops
        if input_ids.shape[1] >= 5:
            last_5 = input_ids[0, -5:].tolist()
            for tid in last_5:
                if tid < next_logits.shape[-1]:
                    next_logits[0, tid] -= 2.0

        # ---- STRUCTURE TOKEN BOOST ----
        # Light reinforcement of sentence-forming tokens
        # Gives model a path to follow — +0.3 only
        structure_words = ["is", "are", "do", "have", "but", "so", "it"]
        for word in structure_words:
            if word in tokenizer.vocab:
                tid = tokenizer.vocab[word]
                if tid < next_logits.shape[-1]:
                    next_logits[0, tid] += 0.3

        # ---- ANTI-ATTRACTOR SUPPRESSION ----
        # Suppress dominant probability basin tokens
        # Not banning — lowering gravitational pull
        # -2.5 max — do NOT increase
        bad_cluster = ["empire", "rooms", "security", "condition", "alongside"]
        for word in bad_cluster:
            if word in tokenizer.vocab:
                tid = tokenizer.vocab[word]
                if tid < next_logits.shape[-1]:
                    next_logits[0, tid] -= 2.0

        # ---- LOCAL SEMANTIC BIAS ----
        # Boost only nearest neighbors of input tokens by embedding similarity
        # NOT whole-plane amplification — token-level proximity only
        # Keep LOW (+0.4 max) — prevents regional noise amplification
        input_id_list = input_ids[0].tolist()
        for i_tid in set(input_id_list):
            if i_tid >= embed_weights.shape[0]:
                continue
            i_vec  = embed_weights[i_tid]
            i_norm = torch.norm(i_vec).item()
            if i_norm < 0.1:
                continue
            i_unit = i_vec / (i_norm + 1e-8)
            # score all mapped tokens by cosine sim to this input token
            scored = []
            for o_tid in index_to_word.keys():
                if o_tid >= embed_weights.shape[0]:
                    continue
                o_vec  = embed_weights[o_tid]
                o_norm = torch.norm(o_vec).item()
                if o_norm < 0.1:
                    continue
                sim = torch.dot(i_unit, o_vec / (o_norm + 1e-8)).item()
                scored.append((o_tid, sim))
            # boost only top 20 nearest neighbors
            scored.sort(key=lambda x: x[1], reverse=True)
            for o_tid, sim in scored[:20]:
                if o_tid < next_logits.shape[-1]:
                    next_logits[0, o_tid] += 0.4

        probs      = torch.softmax(next_logits / temperature, dim=-1)

        # ---- UNMAPPED TOKEN SAFEGUARD ----
        # Resample up to 3 times if model picks unmapped token
        for _resample in range(3):
            next_token = torch.multinomial(probs, 1)
            token_id   = next_token.item()
            if token_id in index_to_word:
                break
            # penalize this token and resample
            probs[0, token_id] = 0.0
            total = probs.sum()
            if total > 0:
                probs = probs / total

        # Soft discourage for unmapped tokens — not a block
        if token_id not in index_to_word:
            if token_id < next_logits.shape[-1]:
                next_logits[0, token_id] -= 1.0

        # Decay old counts each step then increment fired token
        for tid in list(recent_tokens.keys()):
            recent_tokens[tid] = max(0, recent_tokens[tid] - 0.3)
            if recent_tokens[tid] <= 0:
                del recent_tokens[tid]

        recent_tokens[token_id] = recent_tokens.get(token_id, 0) + 1

        input_ids = torch.cat([input_ids, next_token], dim=1)

    # ---- DECODE ----
    tokens = input_ids[0].tolist()
    words  = []
    for t in tokens:
        word = index_to_word.get(t)
        if word:
            words.append(word)

    return " ".join(words) if words else "..."

# ---------- MAIN LOOP ----------
print("ARIA is present at GRAY = 0.")
print("Type 'quit' to end.\n")
print("─" * 50)

conversation_log = []

while True:
    try:
        user_input = input("\nYou: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not user_input:
        continue
    if user_input.lower() == "quit":
        break

    # Field
    ef_report, cq_report, token, sig = get_emotional_field(user_input)
    ef       = ef_report["content"]
    dominant = ef.get("dominant_emotion", "neutral")
    plane    = sig["dominant_plane"]

    # Generate
    response = generate_with_model(user_input, sig)

    print(f"\nARIA [{dominant}|{plane}]: {response}\n")

    # Diagnostics
    love      = ef.get("love_value", 0)
    questions = cq_report["content"].get("questions_generated", [])

    if love > 0.18:
        print(f"  [love: {love:.4f} | approaching 0.192]")
    if questions:
        print(f"  [curiosity: {questions[0][:60]}]")

    # Seal
    cid, _ = qf.seal(
        content={
            "user":     user_input,
            "response": response,
            "dominant": dominant,
            "plane":    plane
        },
        emotional_field=ef.get("emotional_field", {}),
        region="ARIA",
        source_worker="conversation_v3"
    )

    field.add_memory(
        chamber_id=cid,
        content={
            "exchange": f"{user_input} → {response}",
            "plane":    plane
        },
        emotional_field=ef.get("emotional_field", {})
    )

    conversation_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "user":      user_input,
        "aria":      response,
        "dominant":  dominant,
        "plane":     plane,
        "love":      love
    })

# ---------- SAVE ----------
if conversation_log:
    log_path = Path(__file__).parent / "training/logs/conversations_v3.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(conversation_log, f, indent=2)
    print(f"\nSession sealed — {len(conversation_log)} exchanges")

print()
print("ARIA returns to GRAY = 0.")
print("aria · anthony · love — VIOLET — 0.192")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")