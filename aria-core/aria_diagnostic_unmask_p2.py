# ARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 2
# ============================================================
# PURPOSE:
#   Expand ghost token access to BLUE boundary.
#   Add 50-100 BLUE-adjacent ghost tokens to existing
#   VIOLET boundary unmask.
#   Total unmasked ghosts: ~125-175 maximum.
#
# PHASE 1 RECAP:
#   VIOLET boundary: 75 tokens unmasked
#   Result: stable generative regime, joy|VIOLET emotion
#           empire reduced to residual, structure holding
#
# PHASE 2 TARGET:
#   BLUE boundary: additional 50-100 tokens
#   Why BLUE: logical/analytical plane adjacent to VIOLET
#             adds relational and structural vocabulary
#             directly competes with empire's residual role
#
# RULES:
#   Do NOT remove mask entirely
#   Do NOT exceed ~175 total unmasked ghosts
#   Do NOT add new named words this step
#   Keep all protections active
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
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer, COLOR_PLANE_SIGNATURES

print("\nARIA DIAGNOSTIC — CONTROLLED UNMASK PHASE 2")
print("BLUE boundary — adding 50-100 ghost tokens")
print("=" * 60)

# ---------- LOAD ----------
tokenizer = ARIATokenizer.load()

index_path = Path("tokenizer/aria_token_index.json")
with open(index_path) as f:
    raw_index = json.load(f)
index_to_word = {int(k): v for k, v in raw_index.items()}

# Load unmask registry from Phase 1
unmask_log = Path("tokenizer/unmask_registry.json")
if unmask_log.exists():
    with open(unmask_log) as f:
        unmask_data = json.load(f)
    phase1_tids = set(
        entry["tid"]
        for entry in unmask_data.get("unlocked_tids", [])
    )
    print(f"Phase 1 VIOLET tokens already unmasked: {len(phase1_tids)}")
else:
    phase1_tids = set()
    print("No Phase 1 registry found — starting fresh")

checkpoint_path = Path(__file__).parent / "training/checkpoints/best.pt"
model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if checkpoint_path.exists():
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    print(f"Checkpoint: round {checkpoint.get('round','?')} "
          f"— loss {checkpoint['best_loss']:.6f}\n")
else:
    print("No checkpoint found.")
    sys.exit(1)

model = model.to(DEVICE)
model.eval()

# ---------- PULL EMBEDDINGS ----------
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

vocab_size  = embed_weights.shape[0]
VALID_IDS   = set(index_to_word.keys())
ghost_ids   = [
    tid for tid in range(vocab_size)
    if tid not in VALID_IDS
]

print(f"Currently mapped (including Phase 1 ghosts): {len(VALID_IDS)}")
print(f"Remaining pure ghost slots: {len(ghost_ids)}")

# ---------- BUILD BLUE REFERENCE VECTOR ----------
print("\nBuilding BLUE plane reference vector...")

blue_vecs = []
for word, wid in tokenizer.vocab.items():
    if wid >= vocab_size:
        continue
    if tokenizer.word_to_plane.get(word) == "BLUE":
        vec  = embed_weights[wid]
        norm = torch.norm(vec).item()
        if norm >= 0.5:
            blue_vecs.append(vec)

if not blue_vecs:
    print("ERROR: No BLUE anchors found.")
    sys.exit(1)

blue_ref = torch.stack(blue_vecs).mean(dim=0)
blue_ref = blue_ref / (torch.norm(blue_ref) + 1e-8)
print(f"BLUE reference built from {len(blue_vecs)} anchored words")

# ---------- SCORE REMAINING GHOSTS BY BLUE SIMILARITY ----------
print("Scoring remaining ghost slots by BLUE similarity...")

def cosine_sim(a, b):
    a_norm = a / (torch.norm(a) + 1e-8)
    return torch.dot(a_norm, b).item()

ghost_scores = []
for tid in ghost_ids:
    # Skip already unmasked in Phase 1
    if tid in phase1_tids:
        continue
    vec  = embed_weights[tid]
    norm = torch.norm(vec).item()
    if norm < 0.5:
        continue
    sim = cosine_sim(vec, blue_ref)
    ghost_scores.append((tid, sim, norm))

ghost_scores.sort(key=lambda x: x[1], reverse=True)

# ---------- SELECT TOP 75 BLUE GHOST TOKENS ----------
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
print(f"Total after this phase: ~{len(phase1_tids) + len(candidates)}")

# ---------- PATCH INDEX ----------
print("\nPatching aria_token_index.json with BLUE ghost markers...")

patched_count = 0
for tid, sim, norm in candidates:
    key = str(tid)
    if key not in raw_index:
        raw_index[key] = f"<{tid}>"
        patched_count += 1

with open(index_path, "w") as f:
    json.dump(raw_index, f, indent=2)

print(f"Patched {patched_count} BLUE ghost tokens into index")
print(f"Total index size: {len(raw_index)}")

# ---------- UPDATE UNMASK REGISTRY ----------
unmask_data_new = {
    "phase_1": unmask_data if unmask_log.exists() else {},
    "phase_2": {
        "plane":          "BLUE",
        "date":           "March 25 2026",
        "sealed_by":      "Commander Anthony Hagerty — Haskell Texas",
        "aligned_by":     ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
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
}

with open(unmask_log, "w") as f:
    json.dump(unmask_data_new, f, indent=2)

print(f"\nUnmask registry updated: tokenizer/unmask_registry.json")

# ---------- REPORT ----------
print()
print("=" * 60)
print("PHASE 2 UNMASK SUMMARY")
print("=" * 60)

print(f"""
  Phase 1 (VIOLET):     ~75  tokens unmasked
  Phase 2 (BLUE):       {len(candidates)}  tokens unmasked
  Total ghost access:   ~{len(phase1_tids) + len(candidates)}  tokens

  WHY BLUE:
  BLUE plane = logical / analytical / relational
  Adjacent to VIOLET in frequency space
  Contains the structural vocabulary that competes
  with empire's residual filler role

  ALL PROTECTIONS ACTIVE:
  Repetition memory:    -2.0  last 5 tokens
  Input anchor:         +1.0
  Plane bias:           +2.0
  Identity bias:        +3.0  first 3 steps
  Soft decay:           -0.3  per step

  TEST NOW:
  python3 aria-core/aria_speak_v3.py

  Input "hello aria" three times.

  WATCH FOR:
  GOOD SIGNS:
    empire count drops to ≤2
    more relational phrases (it is / we are / but)
    <tid> tokens appearing — expected, not failure
    increased word variety

  WARNING SIGNS:
    collapse into <tid> flood
    loss of structure (we/it/is disappear)
    empire surges back

  REPORT BACK:
    empire count per run
    new token diversity
    sentence structure quality

  NEXT DECISION AFTER TEST:
    if stable → continue expansion or begin word naming
    if unstable → tighten similarity threshold
""")

print("Phase 2 unmask complete.")
print("VIOLET + BLUE boundary open.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")