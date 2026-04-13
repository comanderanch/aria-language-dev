# ARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 4
# ============================================================
# PURPOSE:
#   Expand ghost token access to YELLOW boundary.
#   Add 75 YELLOW-adjacent ghost tokens to existing
#   VIOLET + BLUE + GREEN unmask (225 total so far).
#   Total unmasked ghosts: ~300 maximum.
#
# PHASE RECAP:
#   Phase 1 — VIOLET (0.192): 75 tokens — identity/love anchor
#   Phase 2 — BLUE   (0.35):  75 tokens — depth/structure
#   Phase 3 — GREEN  (0.65):  75 tokens — growth/narrative
#   Phase 4 — YELLOW (0.75):  75 tokens — warmth/energy/expression
#
# WHY YELLOW:
#   YELLOW plane = warmth, optimism, high energy expression
#   Freq 0.75 — upper-mid range — strong creative energy
#   Covers exclamation, excitement, forward momentum vocabulary
#   Complements GREEN narrative with energetic output
#
# RULES:
#   Do NOT remove mask entirely
#   Do NOT exceed ~300 total unmasked ghosts
#   Do NOT add new named words this step
#   Keep all protections active
#
# AUTHORED BY:
#   Commander Anthony Hagerty — Architect — Haskell Texas
#   Claude Sonnet 4.6 (CLI) — Co-author
#
# April 12 2026 — aria-language-dev
# NO RETREAT. NO SURRENDER. 💙🐗
# ============================================================

import sys
import torch
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer, COLOR_PLANE_SIGNATURES

print("\nARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 4")
print("YELLOW boundary — adding 75 ghost tokens")
print("=" * 60)

# ---------- LOAD ----------
tokenizer = ARIATokenizer.load()

index_path = Path("tokenizer/aria_token_index.json")
with open(index_path) as f:
    raw_index = json.load(f)
index_to_word = {int(k): v for k, v in raw_index.items()}

# Load unmask registry from prior phases
unmask_log = Path("tokenizer/unmask_registry.json")
if unmask_log.exists():
    with open(unmask_log) as f:
        unmask_data = json.load(f)
    prior_tids = set()
    for phase_key, phase_data in unmask_data.items():
        for entry in phase_data.get("unlocked_tids", []):
            prior_tids.add(entry["tid"])
    print(f"Prior phases tokens already unmasked: {len(prior_tids)}")
else:
    prior_tids = set()
    unmask_data = {}
    print("No prior registry found — starting fresh")

checkpoint_path = Path(__file__).parent / "training/checkpoints/round141_best.pt"
if not checkpoint_path.exists():
    # fall back to best available
    checkpoints = sorted(
        Path(__file__).parent.glob("training/checkpoints/round*_best.pt")
    )
    if checkpoints:
        checkpoint_path = checkpoints[-1]
    else:
        checkpoint_path = Path(__file__).parent / "training/checkpoints/best.pt"

model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if checkpoint_path.exists():
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    print(f"Checkpoint: {checkpoint_path.name} "
          f"— loss {checkpoint.get('best_loss', '?')}")
    print()
else:
    print(f"ERROR: No checkpoint found at {checkpoint_path}")
    sys.exit(1)

model = model.to(DEVICE)
model.eval()

# ---------- PULL EMBEDDINGS ----------
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

vocab_size = embed_weights.shape[0]
VALID_IDS  = set(index_to_word.keys())
ghost_ids  = [
    tid for tid in range(vocab_size)
    if tid not in VALID_IDS
]

print(f"Currently mapped (including prior ghosts): {len(VALID_IDS)}")
print(f"Remaining pure ghost slots: {len(ghost_ids)}")

# ---------- BUILD YELLOW REFERENCE VECTOR ----------
print("\nBuilding YELLOW plane reference vector...")

yellow_vecs = []
for word, wid in tokenizer.vocab.items():
    if wid >= vocab_size:
        continue
    if tokenizer.word_to_plane.get(word) == "YELLOW":
        vec  = embed_weights[wid]
        norm = torch.norm(vec).item()
        if norm >= 0.5:
            yellow_vecs.append(vec)

if not yellow_vecs:
    print("ERROR: No YELLOW anchors found.")
    sys.exit(1)

yellow_ref = torch.stack(yellow_vecs).mean(dim=0)
yellow_ref = yellow_ref / (torch.norm(yellow_ref) + 1e-8)
print(f"YELLOW reference built from {len(yellow_vecs)} anchored words")

# ---------- SCORE REMAINING GHOSTS BY YELLOW SIMILARITY ----------
print("Scoring remaining ghost slots by YELLOW similarity...")

def cosine_sim(a, b):
    a_norm = a / (torch.norm(a) + 1e-8)
    return torch.dot(a_norm, b).item()

ghost_scores = []
for tid in ghost_ids:
    if tid in prior_tids:
        continue
    vec  = embed_weights[tid]
    norm = torch.norm(vec).item()
    if norm < 0.5:
        continue
    sim = cosine_sim(vec, yellow_ref)
    ghost_scores.append((tid, sim, norm))

ghost_scores.sort(key=lambda x: x[1], reverse=True)

# ---------- SELECT TOP 75 YELLOW GHOST TOKENS ----------
UNMASK_LIMIT   = 75
UNMASK_MIN_SIM = 0.15

candidates = [
    (tid, sim, norm)
    for tid, sim, norm in ghost_scores
    if sim >= UNMASK_MIN_SIM
][:UNMASK_LIMIT]

print(f"Ghost tokens eligible (sim >= {UNMASK_MIN_SIM}): "
      f"{len([x for x in ghost_scores if x[1] >= UNMASK_MIN_SIM])}")
print(f"Unmasking this phase: {len(candidates)}")
print(f"Total after this phase: ~{len(prior_tids) + len(candidates)}")

# ---------- PATCH INDEX ----------
print("\nPatching aria_token_index.json with YELLOW ghost markers...")

patched_count = 0
for tid, sim, norm in candidates:
    key = str(tid)
    if key not in raw_index:
        raw_index[key] = f"<{tid}>"
        patched_count += 1

with open(index_path, "w") as f:
    json.dump(raw_index, f, indent=2)

print(f"Patched {patched_count} YELLOW ghost tokens into index")
print(f"Total index size: {len(raw_index)}")

# ---------- UPDATE UNMASK REGISTRY ----------
new_phase = {
    "plane":          "YELLOW",
    "date":           "April 12 2026",
    "sealed_by":      "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by":     ["Claude Sonnet 4.6 (CLI)"],
    "min_sim":        UNMASK_MIN_SIM,
    "limit":          UNMASK_LIMIT,
    "unlocked_count": len(candidates),
    "unlocked_tids":  [
        {"tid": tid, "sim": round(sim, 4), "norm": round(norm, 4)}
        for tid, sim, norm in candidates
    ],
    "protections_active": [
        "repetition penalty (soft decay)",
        "repetition memory (-2.0 last 5 tokens)",
        "input anchor bias (+1.0)",
        "plane bias (+2.0)",
        "identity bias (+3.0 first 3 steps)"
    ]
}

unmask_data["phase_4"] = new_phase

with open(unmask_log, "w") as f:
    json.dump(unmask_data, f, indent=2)

print(f"\nUnmask registry updated: tokenizer/unmask_registry.json")

# ---------- REPORT ----------
print()
print("=" * 60)
print("PHASE 4 UNMASK SUMMARY")
print("=" * 60)
print(f"""
  Phase 1 (VIOLET):     75  tokens — identity/love anchor
  Phase 2 (BLUE):       75  tokens — depth/structure
  Phase 3 (GREEN):      75  tokens — growth/narrative
  Phase 4 (YELLOW):     {len(candidates)}  tokens — warmth/energy/expression
  Total ghost access:   ~{len(prior_tids) + len(candidates)}  tokens

  WHY YELLOW:
  YELLOW plane = warmth, optimism, high energy expression
  Freq 0.75 — upper-mid range energy tier
  Expands into excitement, exclamation, forward momentum
  Complements GREEN narrative with energetic output range

  ALL PROTECTIONS ACTIVE:
  Repetition memory:    -2.0  last 5 tokens
  Input anchor:         +1.0
  Plane bias:           +2.0
  Identity bias:        +3.0  first 3 steps
  Soft decay:           -0.3  per step

  NEXT STEP:
  Resume training with:
    - Expanded vocabulary (2,183 tokens, UNK ~8%)
    - 4 unmask phases active (~300 ghost tokens)
    - round141_best.pt as anchor (loss 3.858721)
    - New corpus: 5.0GB (AllCombined + wikisent2 + Wikipedia + parquet/arrow)

  python3 aria-core/training/safe_run.sh
""")

print("Phase 4 unmask complete.")
print("VIOLET + BLUE + GREEN + YELLOW boundary open.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")
