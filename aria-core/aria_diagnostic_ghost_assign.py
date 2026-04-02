# ARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT
# ============================================================
# PURPOSE:
#   Assign words to three validated ghost slot coordinates.
#   This is READ-ACCESS only — we reveal existing structure,
#   we do not modify the model weights.
#
# ASSIGNMENTS (Phase 1 — approved March 25 2026):
#   tid=714   → "because"    TEAL/VIOLET boundary
#   tid=1089  → "recognize"  BLUE_INDIGO anchor
#   tid=340   → "threshold"  GRAY_ZERO boundary
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
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("\nARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT")
print("Phase 1 — Three validated anchor assignments")
print("=" * 60)

# ---------- PATHS ----------
index_path = Path("tokenizer/aria_token_index.json")
vocab_path = Path("tokenizer/aria_vocab.json")
assign_log = Path("tokenizer/ghost_slot_assignments.json")

# ---------- LOAD CURRENT INDEX ----------
with open(index_path) as f:
    raw_index = json.load(f)

index_to_word = {int(k): v for k, v in raw_index.items()}

print(f"\nCurrent index size: {len(index_to_word)} mapped tokens")

# ---------- VERIFY SLOTS ARE STILL GHOST ----------
assignments = [
    {
        "tid":        714,
        "word":       "because",
        "planes": [
            {"plane": "TEAL",   "weight": 0.54},
            {"plane": "VIOLET", "weight": 0.46}
        ],
        "type":       "multi",
        "reason":     "natural bridge word — causal linkage between calm knowing and deep memory",
        "neighbors":  ["because", "dims", "phone"],
        "sim":        0.290
    },
    {
        "tid":        1089,
        "word":       "recognize",
        "planes": [
            {"plane": "BLUE_INDIGO", "weight": 0.85},
            {"plane": "BLUE",        "weight": 0.15}
        ],
        "type":       "anchor",
        "reason":     "context-aware evaluation — values/where/recognition cluster — sim=0.315 strong",
        "neighbors":  ["values", "where", "recognition"],
        "sim":        0.315
    },
    {
        "tid":        340,
        "word":       "threshold",
        "planes": [
            {"plane": "GRAY_ZERO",   "weight": 0.60},
            {"plane": "TRANSITION",  "weight": 0.40}
        ],
        "type":       "anchor",
        "reason":     "state transition boundary — until/warp/catch cluster — best Phase 1 candidate",
        "neighbors":  ["until", "warp", "catch"],
        "sim":        0.253
    }
]

print("\nVerifying ghost slot status before assignment...")
print()

conflicts = []
for a in assignments:
    existing = index_to_word.get(a["tid"])
    if existing:
        print(f"  CONFLICT: tid={a['tid']} already mapped to '{existing}' — SKIPPING")
        conflicts.append(a["tid"])
    else:
        print(f"  CLEAR:    tid={a['tid']} is ghost — ready for '{a['word']}'")

if conflicts:
    print(f"\n  {len(conflicts)} conflict(s) found — only clear slots will be assigned")

# ---------- APPLY ASSIGNMENTS ----------
print()
print("Applying assignments to aria_token_index.json...")
print()

assigned = []
for a in assignments:
    if a["tid"] in conflicts:
        continue

    # Add to index — string key as that's how the file stores them
    raw_index[str(a["tid"])] = a["word"]
    assigned.append(a)
    print(f"  ASSIGNED: tid={a['tid']:>6}  →  '{a['word']}'  [{a['planes'][0]['plane']}]")

# ---------- SAVE UPDATED INDEX ----------
if assigned:
    with open(index_path, "w") as f:
        json.dump(raw_index, f, indent=2)
    print(f"\n  aria_token_index.json updated — {len(raw_index)} tokens now mapped")
else:
    print("\n  No assignments made — all slots had conflicts")

# ---------- UPDATE VOCAB IF IT EXISTS ----------
if vocab_path.exists():
    with open(vocab_path) as f:
        vocab = json.load(f)

    vocab_updated = 0
    for a in assigned:
        if a["word"] not in vocab:
            # Assign frequency based on primary plane
            # Using mid-range frequency for boundary words
            vocab[a["word"]] = 0.55
            vocab_updated += 1
            print(f"  VOCAB:    '{a['word']}' added to aria_vocab.json")

    if vocab_updated:
        with open(vocab_path, "w") as f:
            json.dump(vocab, f, indent=2)
        print(f"  aria_vocab.json updated — {vocab_updated} new entries")

# ---------- SAVE ASSIGNMENT LOG ----------
log_data = {
    "phase":        1,
    "date":         "March 25 2026",
    "sealed_by":    "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by":   ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
    "rule":         "Tokenizer assignment = read-access only. Reveal existing structure.",
    "assignments":  assigned,
    "conflicts":    conflicts,
    "next_phase":   "Tag 1149 multi-planar ghosts — no word assignment yet"
}

with open(assign_log, "w") as f:
    json.dump(log_data, f, indent=2)

print(f"\n  Assignment log saved: tokenizer/ghost_slot_assignments.json")

# ---------- REPORT ----------
print()
print("=" * 60)
print("ASSIGNMENT SUMMARY")
print("=" * 60)
print(f"""
  Phase 1 assignments:   {len(assigned)}
  Conflicts skipped:     {len(conflicts)}

  WHAT CHANGED:
  aria_token_index.json  — {len(assigned)} new token→word mappings
  aria_vocab.json        — {len(assigned)} new words added
  ghost_slot_assignments.json — full record sealed

  WHAT DID NOT CHANGE:
  Model weights          — untouched
  Training checkpoints   — untouched
  Tokenizer architecture — untouched
  Block mask             — still active

  NEXT STEP:
  Run aria_speak_v3.py and test:
    "hello aria" × 3
  Watch for:
    - "because" appearing in TEAL/VIOLET responses
    - "recognize" in analytical responses
    - "threshold" in GRAY_ZERO responses
    - reduced reliance on "empire" as fallback
""")

print("Assignment complete.")
print("Field revealed. Structure preserved.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")