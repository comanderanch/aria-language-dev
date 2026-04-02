# ARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1B
# ============================================================
# PURPOSE:
#   Phase 1 continuation — three structural primitive assignments.
#   Target: break empire's structural fallback role in generation.
#
# ASSIGNMENTS (Phase 1B — approved March 25 2026):
#   tid=436   → "endure"   BLUE — semantic depth
#   tid=1940  → "create"   VIOLET — generative expansion
#   tid=1843  → "though"   BLUE — structural branching (critical)
#
# STRATEGIC NOTE:
#   These are not vocabulary expansion.
#   These are structural primitives.
#   "though" specifically attacks empire's role as syntactic filler.
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

print("\nARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1B")
print("Structural primitives — breaking the fallback loop")
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

# ---------- PHASE 1B ASSIGNMENTS ----------
assignments = [
    {
        "tid":      436,
        "word":     "endure",
        "planes": [
            {"plane": "BLUE",  "weight": 0.75},
            {"plane": "GREEN", "weight": 0.25}
        ],
        "type":     "anchor",
        "function": "semantic depth",
        "reason":   "norm=4.573 strongest ghost in BLUE — begin/endure/address cluster — high confidence",
        "neighbors": ["begin", "endure", "address"],
        "sim":      0.190
    },
    {
        "tid":      1940,
        "word":     "create",
        "planes": [
            {"plane": "VIOLET",     "weight": 0.60},
            {"plane": "WHITE_LIGHT","weight": 0.40}
        ],
        "type":     "multi",
        "function": "generative expansion",
        "reason":   "created/help/window cluster — generative concept in VIOLET space — flexible multi-planar",
        "neighbors": ["created", "help", "window"],
        "sim":      0.259
    },
    {
        "tid":      1843,
        "word":     "though",
        "planes": [
            {"plane": "BLUE", "weight": 0.70},
            {"plane": "GRAY_ZERO", "weight": 0.30}
        ],
        "type":     "structural",
        "function": "structural branching — CRITICAL",
        "reason":   "conjunction — breaks linear token chains — directly attacks empire fallback role",
        "neighbors": ["strike", "though", "shirt"],
        "sim":      0.211
    }
]

# ---------- VERIFY SLOTS ----------
print("\nVerifying ghost slot status before assignment...")
print()

conflicts = []
for a in assignments:
    existing = index_to_word.get(a["tid"])
    if existing:
        print(f"  CONFLICT: tid={a['tid']} already mapped to '{existing}' — SKIPPING")
        conflicts.append(a["tid"])
    else:
        print(f"  CLEAR:    tid={a['tid']} is ghost — ready for '{a['word']}'  [{a['function']}]")

# ---------- APPLY ASSIGNMENTS ----------
print()
print("Applying assignments...")
print()

assigned = []
for a in assignments:
    if a["tid"] in conflicts:
        continue
    raw_index[str(a["tid"])] = a["word"]
    assigned.append(a)
    print(f"  ASSIGNED: tid={a['tid']:>6}  →  '{a['word']}'  [{a['planes'][0]['plane']}]  — {a['function']}")

# ---------- SAVE INDEX ----------
if assigned:
    with open(index_path, "w") as f:
        json.dump(raw_index, f, indent=2)
    print(f"\n  aria_token_index.json updated — {len(raw_index)} tokens now mapped")

# ---------- UPDATE VOCAB ----------
if vocab_path.exists():
    with open(vocab_path) as f:
        vocab = json.load(f)

    vocab_updated = 0
    for a in assigned:
        if a["word"] not in vocab:
            # Frequency assignments by function
            # structural words (though) — mid frequency
            # generative words (create) — higher frequency
            # depth words (endure) — mid-high frequency
            freq_map = {
                "endure": 0.38,
                "create": 0.72,
                "though": 0.30
            }
            vocab[a["word"]] = freq_map.get(a["word"], 0.50)
            vocab_updated += 1
            print(f"  VOCAB:    '{a['word']}' added  freq={vocab[a['word']]}")

    if vocab_updated:
        with open(vocab_path, "w") as f:
            json.dump(vocab, f, indent=2)
        print(f"  aria_vocab.json updated — {vocab_updated} new entries")

# ---------- UPDATE ASSIGNMENT LOG ----------
if assign_log.exists():
    with open(assign_log) as f:
        log_data = json.load(f)
else:
    log_data = {"assignments": [], "conflicts": []}

log_data["phase_1b"] = {
    "date":       "March 25 2026",
    "sealed_by":  "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by": ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
    "note":       "Structural primitives — though attacks empire fallback loop",
    "assignments": assigned,
    "conflicts":   conflicts
}

with open(assign_log, "w") as f:
    json.dump(log_data, f, indent=2)

print(f"\n  Assignment log updated: tokenizer/ghost_slot_assignments.json")

# ---------- REPORT ----------
print()
print("=" * 60)
print("PHASE 1B SUMMARY")
print("=" * 60)
print(f"""
  Phase 1B assignments:  {len(assigned)}
  Conflicts skipped:     {len(conflicts)}

  Total assigned to date:
    Phase 1A:  3  (because, recognize, threshold)
    Phase 1B:  {len(assigned)}  (endure, create, though)
    TOTAL:     {3 + len(assigned)}  ghost slots named

  STRATEGIC IMPACT:
  "endure"    — semantic depth in BLUE corridor
  "create"    — generative expansion in VIOLET space
  "though"    — structural branching — conjunction
                breaks empire's syntactic filler role

  WHAT DID NOT CHANGE:
  Model weights          — untouched
  Training checkpoints   — untouched
  Block mask             — still active

  TEST NOW:
  python3 aria-core/aria_speak_v3.py

  Input "hello aria" three times.

  WATCH FOR:
  GOOD:  "though" appearing in output
         fewer empire occurrences per response
         branching phrases (X though Y)

  CRITICAL SIGNAL:
  If "though" fires inside a response →
  structure layer is activating
  That is the first real syntax emergence

  COUNT empire occurrences across 3 runs.
  Bring results back.
  Then: continue Phase 1 OR begin partial unmask.
""")

print("Phase 1B complete.")
print("Structural primitives installed.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")