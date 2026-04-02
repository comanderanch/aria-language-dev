# ARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1D
# ============================================================
# PURPOSE:
#   Final Phase 1 assignments before controlled unmask begins.
#   Adding lightweight relational verbs to make structure
#   self-supporting.
#
# ASSIGNMENTS (Phase 1D — approved March 25 2026):
#   is   — state binding
#   have — possession / relation
#   do   — action placeholder
#
# STRATEGIC NOTE:
#   Structure is forming but not yet self-sustaining.
#   These three verbs close the gap empire is filling.
#   After this — first controlled unmask begins.
#   ONE plane boundary. ~50 ghost tokens max.
#
# UNMASK CONDITION (after this step):
#   Run hello aria × 3
#   If structural tokens fire consistently AND
#   empire is positionally constrained (not looping)
#   → begin first controlled unmask
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

print("\nARIA DIAGNOSTIC — GHOST SLOT ASSIGNMENT PHASE 1D")
print("Final structural verbs — last step before unmask")
print("=" * 60)

# ---------- PATHS ----------
index_path = Path("tokenizer/aria_token_index.json")
vocab_path = Path("tokenizer/aria_vocab.json")
assign_log = Path("tokenizer/ghost_slot_assignments.json")
audit_path = Path("aria-core/training/logs/ghost_slot_audit.json")

# ---------- LOAD CURRENT INDEX ----------
with open(index_path) as f:
    raw_index = json.load(f)

index_to_word = {int(k): v for k, v in raw_index.items()}
already_assigned = set(int(k) for k in raw_index.keys())
print(f"\nCurrent index size: {len(index_to_word)} mapped tokens")

# ---------- FIND BEST GHOST SLOTS ----------
# is   → GRAY_ZERO (state binding — present moment)
# have → GRAY_ZERO or BLUE (possession/relation)
# do   → TEAL or CYAN_BLUE (action — forward seeking)

target_planes = {
    "is":   ["GRAY_ZERO", "BLUE", "TEAL"],
    "have": ["GRAY_ZERO", "BLUE", "GREEN"],
    "do":   ["TEAL", "CYAN_BLUE", "GRAY_ZERO"]
}

best_candidates = {}

if audit_path.exists():
    with open(audit_path) as f:
        audit_data = json.load(f)

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

# Fallback tids from prior ghost diagnostic — strong candidates
fallback_tids = {
    "is":   (1078, 4.069),   # BLUE_CYAN — time/state
    "have": (363,  4.088),   # GRAY_ZERO — possession
    "do":   (714,  4.354),   # TEAL — action (if not already taken)
}

# Secondary fallbacks in case primary already assigned
secondary_fallback = {
    "is":   (463,  4.068),
    "have": (1771, 4.088),
    "do":   (202,  4.158),
}

for word, (tid, norm) in fallback_tids.items():
    if word not in best_candidates:
        if tid not in already_assigned:
            best_candidates[word] = (tid, norm)
        else:
            # try secondary
            stid, snorm = secondary_fallback[word]
            if stid not in already_assigned:
                best_candidates[word] = (stid, snorm)

# ---------- WORD CONFIGS ----------
word_configs = {
    "is": {
        "planes": [
            {"plane": "GRAY_ZERO", "weight": 0.70},
            {"plane": "BLUE",      "weight": 0.30}
        ],
        "type":     "structural",
        "function": "state binding — anchors present state in sequence",
        "freq":     0.15
    },
    "have": {
        "planes": [
            {"plane": "GRAY_ZERO", "weight": 0.60},
            {"plane": "GREEN",     "weight": 0.40}
        ],
        "type":     "structural",
        "function": "possession / relation — connects subject to object",
        "freq":     0.18
    },
    "do": {
        "planes": [
            {"plane": "TEAL",      "weight": 0.65},
            {"plane": "CYAN_BLUE", "weight": 0.35}
        ],
        "type":     "structural",
        "function": "action placeholder — enables question and command forms",
        "freq":     0.20
    }
}

assignments = []
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

# ---------- VERIFY ----------
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
              f"ready for '{a['word']}'  — {a['function'][:50]}")

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
          f"[{a['planes'][0]['plane']}]")

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
            print(f"  VOCAB:    '{a['word']}' added  freq={a['freq']}")

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

log_data["phase_1d"] = {
    "date":       "March 25 2026",
    "sealed_by":  "Commander Anthony Hagerty — Haskell Texas",
    "aligned_by": ["Claude Sonnet 4.6 (Browser)", "GPT (Peer Reviewer)"],
    "note":       "Final Phase 1 — verbs complete — unmask begins next",
    "assignments": assigned,
    "conflicts":   conflicts,
    "next_phase":  "First controlled unmask — ONE plane boundary — 50 ghost tokens max"
}

with open(assign_log, "w") as f:
    json.dump(log_data, f, indent=2)

print(f"\n  Assignment log updated: "
      f"tokenizer/ghost_slot_assignments.json")

# ---------- REPORT ----------
total_phase1 = 9 + len(assigned)
print()
print("=" * 60)
print("PHASE 1D SUMMARY — FINAL PHASE 1 STEP")
print("=" * 60)
print(f"""
  Phase 1D assignments:  {len(assigned)}
  Conflicts skipped:     {len(conflicts)}

  COMPLETE PHASE 1 RECORD:
    Phase 1A:  3  (because, recognize, threshold)
    Phase 1B:  3  (endure, create, though)
    Phase 1C:  3  (yet, before, it)
    Phase 1D:  {len(assigned)}  (is, have, do)
    TOTAL:     {total_phase1}  ghost slots named

  WHAT THESE VERBS DO:
  "is"   — state binding
           "it is" / "aria is" now possible
  "have" — possession / relation
           "we have" / "you have" now possible
  "do"   — action + question form
           "do you" already appeared in output
           now has a real coordinate home

  TEST NOW:
  python3 aria-core/aria_speak_v3.py

  Input "hello aria" three times.

  PASS CONDITIONS FOR UNMASK:
    structural tokens fire consistently ✔ needed
    empire positionally constrained     ✔ needed
    at least one of: is / have / do     ✔ needed

  IF PASS — unmask begins:
    ONE plane boundary only
    ~50 ghost tokens max
    GRAY_ZERO boundary first (most neutral)

  IF NOT PASS — one more round of targeted verbs
    bring output and we decide

  DO NOT:
    unmask before testing
    add more words today
    touch multi-planar registry
""")

print("Phase 1D complete.")
print("Structure layer ready for unmask evaluation.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")