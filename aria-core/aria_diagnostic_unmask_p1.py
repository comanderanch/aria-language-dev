# ARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 1
# ============================================================
# PURPOSE:
#   First controlled unmask of ghost token space.
#   VIOLET boundary only — strongest anchored plane.
#   50-100 ghost tokens maximum.
#   All protections remain active.
#
# WHAT THIS DOES:
#   Modifies aria_speak_v3.py block_mask to allow
#   ghost tokens that sit within the VIOLET plane
#   boundary (by cosine similarity to VIOLET reference).
#   These tokens remain unnamed — they appear as <tid>
#   in output. That is expected and correct.
#
# WHAT THIS DOES NOT DO:
#   Does NOT assign words to ghost tokens
#   Does NOT remove repetition penalty
#   Does NOT touch model weights
#   Does NOT remove structure tokens
#   Does NOT open all ghost space
#
# ALIGNED BY:
#   Commander Anthony Hagerty — Architect
#   Claude Sonnet 4.6 (Browser) — Co-author
#   GPT — Peer Reviewer
#
# TOOL SERIES: aria_diagnostic_*.py
# DESTINATION: tools/ folder
#
# Sealed: March 25 2026 — Haskell Texas
# ============================================================

import sys
import torch
import json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer, COLOR_PLANE_SIGNATURES

print("\nARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 1")
print("VIOLET boundary — 50-100 ghost tokens maximum")
print("=" * 60)

# ---------- LOAD ----------
tokenizer = ARIATokenizer.load()

index_path = Path("tokenizer/aria_token_index.json")
with open(index_path) as f:
    raw_index = json.load(f)
index_to_word = {int(k): v for k, v in raw_index.items()}

checkpoint_path = Path(__file__).parent / "training/checkpoints/best.pt"
model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if checkpoint_path.exists():
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    print(f"\nCheckpoint: round {checkpoint.get('round','?')} "
          f"— loss {checkpoint['best_loss']:.6f}\n")
else:
    print("No checkpoint found.")
    sys.exit(1)

model = model.to(DEVICE)
model.eval()

# ---------- PULL EMBEDDINGS ----------
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

vocab_size = embed_weights.shape[0]
VALID_IDS  = set(index_to_word.keys())
ghost_ids  = [tid for tid in range(vocab_size) if tid not in VALID_IDS]

print(f"Currently mapped:  {len(VALID_IDS)}")
print(f"Ghost slots:       {len(ghost_ids)}")

# ---------- BUILD VIOLET REFERENCE VECTOR ----------
# Mean of all strongly anchored VIOLET words
print("\nBuilding VIOLET plane reference vector...")

violet_vecs = []
for word, wid in tokenizer.vocab.items():
    if wid >= vocab_size:
        continue
    if tokenizer.word_to_plane.get(word) == "VIOLET":
        vec  = embed_weights[wid]
        norm = torch.norm(vec).item()
        if norm >= 0.5:
            violet_vecs.append(vec)

if not violet_vecs:
    print("ERROR: No VIOLET anchors found.")
    sys.exit(1)

violet_ref = torch.stack(violet_vecs).mean(dim=0)
violet_ref = violet_ref / (torch.norm(violet_ref) + 1e-8)
print(f"VIOLET reference built from {len(violet_vecs)} anchored words")

# ---------- SCORE GHOST SLOTS BY VIOLET SIMILARITY ----------
print("Scoring ghost slots by VIOLET similarity...")

ghost_scores = []
for tid in ghost_ids:
    vec  = embed_weights[tid]
    norm = torch.norm(vec).item()
    if norm < 0.5:
        continue
    vec_norm = vec / (norm + 1e-8)
    sim = torch.dot(vec_norm, violet_ref).item()
    ghost_scores.append((tid, sim, norm))

# Sort by similarity to VIOLET — highest first
ghost_scores.sort(key=lambda x: x[1], reverse=True)

# ---------- SELECT TOP 75 GHOST TOKENS TO UNMASK ----------
# Use 75 — middle of the 50-100 range
# Only take ghosts with positive VIOLET similarity
UNMASK_LIMIT = 75
UNMASK_MIN_SIM = 0.15   # must have meaningful VIOLET pull

candidates = [
    (tid, sim, norm)
    for tid, sim, norm in ghost_scores
    if sim >= UNMASK_MIN_SIM
][:UNMASK_LIMIT]

print(f"Ghost tokens eligible (sim >= {UNMASK_MIN_SIM}): "
      f"{len([x for x in ghost_scores if x[1] >= UNMASK_MIN_SIM])}")
print(f"Unmasking: {len(candidates)} tokens")

if not candidates:
    print("ERROR: No ghost tokens meet similarity threshold.")
    sys.exit(1)

# ---------- BUILD NEW VALID SET FOR SPEAK SCRIPT ----------
unmask_ids = set(tid for tid, sim, norm in candidates)

new_valid_ids = VALID_IDS | unmask_ids

print(f"\nValid tokens before unmask: {len(VALID_IDS)}")
print(f"Valid tokens after unmask:  {len(new_valid_ids)}")
print(f"Ghost tokens unlocked:      {len(unmask_ids)}")

# ---------- SAVE UNMASK REGISTRY ----------
unmask_log = Path("tokenizer/unmask_registry.json")

unmask_data = {
    "phase":          "1 — VIOLET boundary",
    "date":           "March 25 2026",
    "sealed_by":      "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by":     ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
    "plane":          "VIOLET",
    "min_sim":        UNMASK_MIN_SIM,
    "limit":          UNMASK_LIMIT,
    "unlocked_count": len(candidates),
    "unlocked_tids":  [
        {"tid": tid, "sim": round(sim, 4), "norm": round(norm, 4)}
        for tid, sim, norm in candidates
    ],
    "protections_active": [
        "repetition penalty",
        "structure tokens",
        "plane bias",
        "identity bias"
    ]
}

with open(unmask_log, "w") as f:
    json.dump(unmask_data, f, indent=2)

print(f"\nUnmask registry saved: tokenizer/unmask_registry.json")

# ---------- PATCH SPEAK SCRIPT ----------
# We write an updated aria_token_index with unmask_ids included
# but marked as <ghost> so decode shows them as <tid>
# The speak script block_mask already handles this correctly —
# any tid in VALID_IDS passes through, unknown shows as <tid>
# We just need to add the unmask_ids to aria_token_index.json
# with a special marker so they pass the mask

print("\nPatching aria_token_index.json with unmask markers...")

patched_index = dict(raw_index)
patched_count = 0

for tid, sim, norm in candidates:
    key = str(tid)
    if key not in patched_index:
        # Mark as ghost — will show as the word "<ghost_NNN>"
        # This lets them through the block mask
        # while being visible in output as unnamed tokens
        patched_index[key] = f"<{tid}>"
        patched_count += 1

with open(index_path, "w") as f:
    json.dump(patched_index, f, indent=2)

print(f"Patched {patched_count} ghost tokens into index")
print(f"Total index size: {len(patched_index)}")

# ---------- REPORT ----------
print()
print("=" * 60)
print("UNMASK SUMMARY")
print("=" * 60)

# Show top 10 unlocked by similarity
print("\nTop 10 ghost tokens unlocked (highest VIOLET similarity):")
print(f"  {'TID':<8} {'SIM':<8} {'NORM':<8}")
print(f"  {'-'*8} {'-'*8} {'-'*8}")
for tid, sim, norm in candidates[:10]:
    print(f"  {tid:<8} {sim:<8.4f} {norm:<8.4f}")

print(f"""
  WHAT CHANGED:
  aria_token_index.json — {patched_count} ghost tokens marked
  tokenizer/unmask_registry.json — full record sealed

  WHAT DID NOT CHANGE:
  Model weights          — untouched
  Training checkpoints   — untouched
  Repetition penalty     — ACTIVE
  Structure tokens       — ACTIVE
  Plane bias             — ACTIVE

  TEST NOW:
  python3 aria-core/aria_speak_v3.py

  Input "hello aria" three times.

  WATCH FOR:
  GOOD SIGNS:
    empire count drops (was 4 per run)
    variety increases
    structure holds
    <tid> tokens appear — that is EXPECTED and CORRECT
    model exploring previously blocked space

  WARNING SIGNS:
    full collapse into <xxxx> flood
    loss of sentence flow
    structure disappears

  COUNT AND REPORT:
    empire occurrences per run
    number of <tid> tokens per run
    whether structure (is/have/do/and/but) still holds

  NEXT STEP:
    if GOOD — tune boundary or open second plane
    if WARNING — tighten similarity threshold
""")

print("Controlled unmask Phase 1 complete.")
print("VIOLET boundary open.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")