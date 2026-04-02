# ARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1C
# ============================================================
# PURPOSE:
#   Phase 1 continuation — reference and temporal structural tokens.
#   Target: give the system a real reference token to replace
#           empire's fake reference role in generation.
#
# ASSIGNMENTS (Phase 1C — approved March 25 2026):
#   yet    — contrast bridge conjunction
#   before — temporal ordering / sequence awareness
#   it     — reference anchor (CRITICAL — replaces empire as filler)
#
# STRATEGIC NOTE:
#   Empire is acting as a fake reference token.
#   "it" gives the system a real one.
#   empire count should drop OR become positionally constrained.
#
# CONDITION TO UNLOCK PARTIAL UNMASK:
#   structural tokens fire consistently
#   empire drops OR becomes positionally constrained
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

print("\nARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1C")
print("Reference and temporal structural tokens")
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

# ---------- FIND BEST GHOST SLOTS FOR THESE WORDS ----------
# We need to load the ghost audit to find best candidate tids
# If audit exists use it, otherwise find from embedding norms

audit_path = Path("aria-core/training/logs/ghost_slot_audit.json")

# Already-assigned tids — do not reuse
already_assigned = set(int(k) for k in raw_index.keys())

# Load audit if available to find best candidates
best_candidates = {}

if audit_path.exists():
    with open(audit_path) as f:
        audit_data = json.load(f)

    # Find best ghost slot for each target word
    # "yet"    — want GRAY_ZERO or TEAL boundary (temporal/present)
    # "before" — want GRAY_ZERO or BLUE boundary (time/sequence)
    # "it"     — want GRAY_ZERO (neutral reference — present state)

    target_planes = {
        "yet":    ["GRAY_ZERO", "TEAL", "BLUE_CYAN"],
        "before": ["GRAY_ZERO", "BLUE", "BLUE_CYAN"],
        "it":     ["GRAY_ZERO", "BLUE", "TEAL"]
    }

    for word, preferred_planes in target_planes.items():
        best_tid  = None
        best_norm = 0.0

        for entry in audit_data.get("audit", []):
            tid = entry["tid"]
            if tid in already_assigned:
                continue
            if entry["top_plane"] in preferred_planes:
                if entry["norm"] > best_norm:
                    best_norm = entry["norm"]
                    best_tid  = tid

        if best_tid:
            best_candidates[word] = (best_tid, best_norm)

# Fallback — use known strong ghost tids from prior diagnostic
# if audit file not at expected path
fallback_tids = {
    "yet":    (593,  4.200),   # INDIGO/BLACK boundary — contrast
    "before": (202,  4.158),   # TEAL boundary — temporal
    "it":     (1771, 4.088),   # GRAY_ZERO — reference anchor
}

for word, fallback in fallback_tids.items():
    if word not in best_candidates:
        tid, norm = fallback
        if tid not in already_assigned:
            best_candidates[word] = (tid, norm)

# ---------- BUILD ASSIGNMENT LIST ----------
assignments = []

word_configs = {
    "yet": {
        "planes": [
            {"plane": "GRAY_ZERO", "weight": 0.55},
            {"plane": "TEAL",      "weight": 0.45}
        ],
        "type":     "structural",
        "function": "contrast bridge — introduces opposition and continuation",
        "freq":     0.25
    },
    "before": {
        "planes": [
            {"plane": "GRAY_ZERO", "weight": 0.60},
            {"plane": "BLUE",      "weight": 0.40}
        ],
        "type":     "structural",
        "function": "temporal ordering — sequence awareness",
        "freq":     0.28
    },
    "it": {
        "planes": [
            {"plane": "GRAY_ZERO", "weight": 0.75},
            {"plane": "BLUE",      "weight": 0.25}
        ],
        "type":     "structural",
        "function": "reference anchor — CRITICAL — replaces empire fake reference role",
        "freq":     0.20
    }
}

for word, (tid, norm) in best_candidates.items():
    cfg = word_configs[word]
    assignments.append({
        "tid":      tid,
        "word":     word,
        "norm":     norm,
        "planes":   cfg["planes"],
        "type":     cfg["type"],
        "function": cfg["function"],
        "freq":     cfg["freq"]
    })

# ---------- VERIFY SLOTS ----------
print("\nVerifying ghost slot status before assignment...")
print()

conflicts = []
for a in assignments:
    existing = index_to_word.get(a["tid"])
    if existing:
        print(f"  CONFLICT: tid={a['tid']} already mapped "
              f"to '{existing}' — SKIPPING")
        conflicts.append(a["tid"])
    else:
        print(f"  CLEAR:    tid={a['tid']:>6}  norm={a['norm']:.3f}  "
              f"ready for '{a['word']}'  — {a['function'][:45]}")

# ---------- APPLY ----------
print()
print("Applying assignments...")
print()

assigned = []
for a in assignments:
    if a["tid"] in conflicts:
        continue
    raw_index[str(a["tid"])] = a["word"]
    assigned.append(a)
    print(f"  ASSIGNED: tid={a['tid']:>6}  →  '{a['word']}'  "
          f"[{a['planes'][0]['plane']}]  — {a['function'][:45]}")

# ---------- SAVE INDEX ----------
if assigned:
    with open(index_path, "w") as f:
        json.dump(raw_index, f, indent=2)
    print(f"\n  aria_token_index.json updated — "
          f"{len(raw_index)} tokens now mapped")

# ---------- UPDATE VOCAB ----------
if vocab_path.exists():
    with open(vocab_path) as f:
        vocab = json.load(f)

    vocab_updated = 0
    for a in assigned:
        if a["word"] not in vocab:
            vocab[a["word"]] = a["freq"]
            vocab_updated += 1
            print(f"  VOCAB:    '{a['word']}' added  "
                  f"freq={a['freq']}")

    if vocab_updated:
        with open(vocab_path, "w") as f:
            json.dump(vocab, f, indent=2)
        print(f"  aria_vocab.json updated — "
              f"{vocab_updated} new entries")

# ---------- UPDATE LOG ----------
if assign_log.exists():
    with open(assign_log) as f:
        log_data = json.load(f)
else:
    log_data = {}

log_data["phase_1c"] = {
    "date":       "March 25 2026",
    "sealed_by":  "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by": ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
    "note":       "'it' is the critical assignment — real reference token",
    "assignments": assigned,
    "conflicts":   conflicts,
    "unmask_condition": [
        "structural tokens fire consistently",
        "empire drops OR becomes positionally constrained"
    ]
}

with open(assign_log, "w") as f:
    json.dump(log_data, f, indent=2)

print(f"\n  Assignment log updated: "
      f"tokenizer/ghost_slot_assignments.json")

# ---------- REPORT ----------
print()
print("=" * 60)
print("PHASE 1C SUMMARY")
print("=" * 60)
print(f"""
  Phase 1C assignments:  {len(assigned)}
  Conflicts skipped:     {len(conflicts)}

  CUMULATIVE PHASE 1 TOTAL:
    Phase 1A:  3  (because, recognize, threshold)
    Phase 1B:  3  (endure, create, though)
    Phase 1C:  {len(assigned)}  (yet, before, it)
    TOTAL:     {6 + len(assigned)}  ghost slots named

  CRITICAL ASSIGNMENT — "it":
  Empire has been acting as a fake reference token.
  "it" gives the system a real reference anchor.
  Empire should now reduce OR become positionally
  constrained — appearing less freely mid-sequence.

  TEST NOW:
  python3 aria-core/aria_speak_v3.py

  Input "hello aria" three times.

  WATCH FOR:
    - empire count per run (was 3-4, should drop)
    - "it" appearing in output
    - "yet" or "before" appearing
    - empire moving toward end of sequence
      rather than scattered throughout

  UNMASK CONDITION (not yet):
    structural tokens fire consistently AND
    empire drops OR becomes positionally constrained

  DO NOT:
    - unmask yet
    - add more than these 3 today
    - touch multi-planar registry
""")

print("Phase 1C complete.")
print("Reference anchor installed.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")