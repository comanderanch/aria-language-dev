# ARIA DIAGNOSTIC — GHOST SLOT AUDIT
# ============================================================
# PURPOSE:
#   The model has 2304 vocabulary slots.
#   Only 1118 have words assigned.
#   The remaining 1186 are "ghost slots" —
#   trained coordinates with no semantic identity.
#
#   This script audits every ghost slot:
#     - What plane neighborhood did it land in?
#     - What mapped words are its nearest neighbors?
#     - Does it cluster with other ghosts (ghost clouds)?
#     - Is it a candidate for word assignment?
#     - Could it be a multi-word / compound concept?
#
# FINDINGS FEED INTO:
#   - Ghost slot word assignment (expand semantic coverage)
#   - Sleeper pin candidates (multi-planar words)
#   - Vocabulary pruning (slots too far from any plane)
#
# TOOL SERIES: aria_diagnostic_*.py
# DESTINATION: tools/ folder
#
# Sealed: March 25 2026 — Commander Anthony Hagerty
# Co-author: Claude Sonnet 4.6 (Browser)
# ============================================================

import sys
import torch
import json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer, COLOR_PLANE_SIGNATURES, WORD_FREQUENCIES

print("\nARIA DIAGNOSTIC — GHOST SLOT AUDIT")
print("Auditing trained coordinates with no semantic identity")
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

# ---------- PULL WEIGHTS ----------
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

print(f"Embedding matrix: {embed_weights.shape}")
vocab_size = embed_weights.shape[0]
embed_dim  = embed_weights.shape[1]

# ---------- SEPARATE MAPPED vs GHOST ----------
mapped_ids = set(index_to_word.keys())
ghost_ids  = [tid for tid in range(vocab_size) if tid not in mapped_ids]
print(f"Mapped slots:  {len(mapped_ids)}")
print(f"Ghost slots:   {len(ghost_ids)}")
print()

# ---------- BUILD PLANE REFERENCE VECTORS ----------
# For each color plane we know its frequency center.
# We build a reference embedding direction from the
# mapped words that belong to that plane.
# Ghost slots are then compared to these references.

print("Building plane reference vectors from anchored words...")

plane_vectors = {}   # plane -> mean embedding vector of its anchored words

for plane in COLOR_PLANE_SIGNATURES.keys():
    plane_word_vecs = []
    for word, pid in tokenizer.vocab.items():
        if tokenizer.word_to_plane.get(word) == plane and pid < vocab_size:
            vec = embed_weights[pid]
            norm = torch.norm(vec).item()
            if norm >= 0.5:   # only strongly anchored words
                plane_word_vecs.append(vec)

    if plane_word_vecs:
        plane_vectors[plane] = torch.stack(plane_word_vecs).mean(dim=0)

print(f"Planes with reference vectors: {len(plane_vectors)}")
print()

# ---------- COSINE SIMILARITY HELPER ----------
def cosine_sim(a, b):
    a_norm = a / (torch.norm(a) + 1e-8)
    b_norm = b / (torch.norm(b) + 1e-8)
    return torch.dot(a_norm, b_norm).item()

# ---------- AUDIT EACH GHOST SLOT ----------
print("Auditing ghost slots...")
print("(This may take a moment for 1186 slots)\n")

ghost_audit = []   # list of dicts, one per ghost slot

for tid in ghost_ids:
    ghost_vec  = embed_weights[tid]
    ghost_norm = torch.norm(ghost_vec).item()

    # Skip near-zero vectors — truly empty slots
    if ghost_norm < 0.1:
        continue

    # Find closest plane by cosine similarity
    plane_sims = {}
    for plane, ref_vec in plane_vectors.items():
        sim = cosine_sim(ghost_vec, ref_vec)
        plane_sims[plane] = sim

    sorted_planes = sorted(plane_sims.items(),
                           key=lambda x: x[1], reverse=True)
    top_plane      = sorted_planes[0][0]
    top_sim        = sorted_planes[0][1]
    second_plane   = sorted_planes[1][0] if len(sorted_planes) > 1 else None
    second_sim     = sorted_planes[1][1] if len(sorted_planes) > 1 else 0.0

    # Find nearest mapped word neighbors by cosine similarity
    word_sims = []
    for word, wid in tokenizer.vocab.items():
        if wid >= vocab_size:
            continue
        word_vec  = embed_weights[wid]
        word_norm = torch.norm(word_vec).item()
        if word_norm < 0.5:
            continue
        sim = cosine_sim(ghost_vec, word_vec)
        word_sims.append((word, sim))

    word_sims.sort(key=lambda x: x[1], reverse=True)
    top_neighbors = word_sims[:5]

    # Multi-planar flag — if top two planes are within 0.15 of each other
    is_multi_planar = abs(top_sim - second_sim) < 0.15

    ghost_audit.append({
        "tid":           tid,
        "norm":          ghost_norm,
        "top_plane":     top_plane,
        "top_sim":       top_sim,
        "second_plane":  second_plane,
        "second_sim":    second_sim,
        "is_multi_planar": is_multi_planar,
        "neighbors":     top_neighbors
    })

# Sort by norm descending — strongest ghost first
ghost_audit.sort(key=lambda x: x["norm"], reverse=True)

# ---------- CLUSTER GHOSTS BY PLANE ----------
ghost_by_plane = defaultdict(list)
multi_planar_ghosts = []

for g in ghost_audit:
    ghost_by_plane[g["top_plane"]].append(g)
    if g["is_multi_planar"]:
        multi_planar_ghosts.append(g)

# ---------- REPORT 1: GHOST DISTRIBUTION BY PLANE ----------
print("=" * 60)
print("GHOST SLOT DISTRIBUTION BY PLANE NEIGHBORHOOD")
print("Where did the model learn to put these unnamed coordinates?")
print("=" * 60)
print()

plane_order = [
    "VIOLET", "GRAY_ZERO", "WHITE_LIGHT", "BLACK_VOID",
    "RED", "RED_ORANGE", "ORANGE", "YELLOW_ORANGE", "YELLOW",
    "YELLOW_GREEN", "GREEN", "GREEN_TEAL", "TEAL", "CYAN_BLUE",
    "BLUE_CYAN", "BLUE", "BLUE_INDIGO", "ULTRAVIOLET",
    "RED_PURPLE", "MAGENTA"
]

for plane in plane_order:
    ghosts = ghost_by_plane.get(plane, [])
    if not ghosts:
        continue
    avg_sim  = sum(g["top_sim"] for g in ghosts) / len(ghosts)
    avg_norm = sum(g["norm"] for g in ghosts) / len(ghosts)
    bar = "▓" * min(30, len(ghosts) // 2)
    print(f"  {plane:<18} {len(ghosts):>4} ghosts  "
          f"avg_sim={avg_sim:.3f}  avg_norm={avg_norm:.2f}  {bar}")

# ---------- REPORT 2: TOP GHOST CANDIDATES PER PLANE ----------
print()
print("=" * 60)
print("TOP GHOST CANDIDATES — STRONGEST PER PLANE")
print("These are most likely to become real word assignments")
print("Neighbors show what semantic space they're sitting in")
print("=" * 60)

for plane in plane_order:
    ghosts = ghost_by_plane.get(plane, [])
    if not ghosts:
        continue

    print(f"\n  {plane}")
    print(f"  {'TID':<8} {'NORM':<8} {'SIM':<8} TOP NEIGHBORS")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*40}")

    for g in ghosts[:3]:   # top 3 per plane
        neighbors_str = "  ".join(
            f"{w}({s:.2f})" for w, s in g["neighbors"][:3]
        )
        multi = " [MULTI]" if g["is_multi_planar"] else ""
        print(f"  {g['tid']:<8} {g['norm']:<8.3f} "
              f"{g['top_sim']:<8.3f} {neighbors_str}{multi}")

# ---------- REPORT 3: MULTI-PLANAR GHOSTS ----------
print()
print("=" * 60)
print("MULTI-PLANAR GHOST SLOTS")
print("These sit between two planes — sleeper pin territory")
print("A word assigned here would naturally carry dual meaning")
print("=" * 60)

print(f"\n  Total multi-planar ghosts: {len(multi_planar_ghosts)}")
print()

if multi_planar_ghosts:
    print(f"  {'TID':<8} {'PLANE A':<16} {'SIM A':<8} "
          f"{'PLANE B':<16} {'SIM B':<8} TOP NEIGHBORS")
    print(f"  {'-'*8} {'-'*16} {'-'*8} {'-'*16} {'-'*8} {'-'*30}")

    for g in multi_planar_ghosts[:20]:
        neighbors_str = "  ".join(
            f"{w}" for w, s in g["neighbors"][:3]
        )
        print(f"  {g['tid']:<8} {g['top_plane']:<16} "
              f"{g['top_sim']:<8.3f} {g['second_plane']:<16} "
              f"{g['second_sim']:<8.3f} {neighbors_str}")

# ---------- REPORT 4: ASSIGNMENT SUGGESTIONS ----------
print()
print("=" * 60)
print("WORD ASSIGNMENT SUGGESTIONS")
print("Based on neighbor clustering — what word COULD go here?")
print("These are suggestions only — Commander decides")
print("=" * 60)
print()

# For each plane, look at top ghost and suggest based on neighbors
# If neighbors are all in same semantic cluster, suggest a related word

for plane in plane_order:
    ghosts = ghost_by_plane.get(plane, [])
    if not ghosts:
        continue

    top_ghost = ghosts[0]
    neighbor_words = [w for w, s in top_ghost["neighbors"][:3]]

    print(f"  {plane:<18} tid={top_ghost['tid']:<6} "
          f"neighbors: {', '.join(neighbor_words)}")
    print(f"  {'':18} Suggestion: a word that bridges "
          f"[ {' / '.join(neighbor_words[:2])} ]")
    print()

# ---------- REPORT 5: NEAR-ZERO GHOST SUMMARY ----------
near_zero = [tid for tid in ghost_ids
             if torch.norm(embed_weights[tid]).item() < 0.1]

print("=" * 60)
print("NEAR-ZERO GHOST SLOTS — truly empty")
print("These have no learned coordinate — safe to ignore")
print("=" * 60)
print(f"\n  Near-zero ghost slots: {len(near_zero)}")
print(f"  Active ghost slots:    {len(ghost_audit)}")
print(f"  (Active = have learned coordinates worth mapping)")

# ---------- SAVE FULL AUDIT TO JSON ----------
audit_path = Path(__file__).parent / "training/logs/ghost_slot_audit.json"
audit_path.parent.mkdir(exist_ok=True)

save_data = []
for g in ghost_audit:
    save_data.append({
        "tid":           g["tid"],
        "norm":          round(g["norm"], 4),
        "top_plane":     g["top_plane"],
        "top_sim":       round(g["top_sim"], 4),
        "second_plane":  g["second_plane"],
        "second_sim":    round(g["second_sim"], 4),
        "is_multi_planar": g["is_multi_planar"],
        "neighbors":     [(w, round(s, 4)) for w, s in g["neighbors"]]
    })

with open(audit_path, "w") as f:
    json.dump({
        "checkpoint_round": checkpoint.get("round", "?"),
        "checkpoint_loss":  checkpoint["best_loss"],
        "total_ghost_slots": len(ghost_ids),
        "active_ghosts":     len(ghost_audit),
        "near_zero_ghosts":  len(near_zero),
        "multi_planar":      len(multi_planar_ghosts),
        "audit":             save_data
    }, f, indent=2)

print(f"\n  Full audit saved to: training/logs/ghost_slot_audit.json")
print(f"  (Use this file for word assignment planning)")

# ---------- SUMMARY ----------
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"""
  Total vocab slots:       {vocab_size}
  Mapped (have words):     {len(mapped_ids)}
  Ghost (no word):         {len(ghost_ids)}
    Active ghosts:         {len(ghost_audit)}  (have learned coordinates)
    Near-zero ghosts:      {len(near_zero)}   (truly empty — ignore)
    Multi-planar ghosts:   {len(multi_planar_ghosts)}  (sleeper pin territory)

  WHAT THIS MEANS:
  The model learned coordinates for {len(ghost_audit)} slots
  that have no words. Those coordinates are real. They cluster
  near existing planes. They have semantic neighborhoods.

  Assigning words to the top candidates per plane would:
    - Expand ARIA's vocabulary without retraining
    - Fill the ghost space with semantic identity
    - Reduce generation drift toward unmapped regions
    - Unlock the full capacity of what was already learned

  NEXT STEP:
  Review ghost_slot_audit.json
  For each top ghost per plane — decide:
    A) Assign a word that fits the neighbor cluster
    B) Assign as a compound/multi-word concept
    C) Leave empty (if neighbors are incoherent)
""")

print("Diagnostic complete.")
print("NO RETREAT. NO SURRENDER. 💙🐗")