# ARIA ANCHOR + FLOAT + SLEEPER PIN DIAGNOSTIC
# Maps anchored words, floating words, and multi-plane pull candidates
#
# The sleeper pin insight:
#   Some words are not broken — they are multi-planar.
#   "love" in "I love movies" != "love" in "I love my family"
#   Same token. Different semantic coordinate. Different plane.
#   These are not nulls. They are sleeper pin candidates.
#   Dual anchor: two pins, two coordinates, context decides which fires.
#
# Sealed: March 25 2026 — Commander Anthony Hagerty
# Co-author: Claude Sonnet 4.6 (Browser)

import sys
import torch
import json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel
from aria_core.gpu_config import DEVICE
from tokenizer.aria_tokenizer import ARIATokenizer, COLOR_PLANE_SIGNATURES, WORD_FREQUENCIES

print("\nARIA ANCHOR + FLOAT + SLEEPER PIN DIAGNOSTIC\n")
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
    print(f"Checkpoint: round {checkpoint.get('round','?')} — loss {checkpoint['best_loss']:.6f}\n")
else:
    print("No checkpoint found.")
    sys.exit(1)

model = model.to(DEVICE)
model.eval()

# ---------- PULL EMBEDDING WEIGHTS ----------
with torch.no_grad():
    embed_weights = model.token_embedding.weight.detach().cpu()

print(f"Embedding matrix: {embed_weights.shape}")
print()

# ---------- COMPUTE ANCHOR STRENGTH ----------
norms = torch.norm(embed_weights, dim=1)

# ---------- BUILD PLANE FREQUENCY BANDS ----------
# Map each plane name to its frequency center from COLOR_PLANE_SIGNATURES
plane_freqs = {
    plane: data["freq"]
    for plane, data in COLOR_PLANE_SIGNATURES.items()
}

# ---------- CLASSIFY EVERY MAPPED TOKEN ----------
strongly_anchored = defaultdict(list)   # plane -> [(word, norm)]
floating          = []                   # [(word, assigned_plane, norm, word_freq)]
sleeper_candidates = []                  # [(word, plane_a, plane_b, pull_diff, norm)]

ANCHOR_THRESHOLD  = 0.5    # below this = floating
SLEEPER_BAND      = 0.12   # if word freq is within this of TWO plane centers = sleeper candidate

for tid in range(embed_weights.shape[0]):
    word = index_to_word.get(tid)
    if word is None:
        continue

    norm          = norms[tid].item()
    assigned_plane = tokenizer.word_to_plane.get(word, "UNASSIGNED")
    word_freq      = WORD_FREQUENCIES.get(word, None)

    if norm >= ANCHOR_THRESHOLD:
        strongly_anchored[assigned_plane].append((word, norm))
    else:
        # Floating — check if it's being pulled toward multiple planes
        if word_freq is not None:
            close_planes = []
            for plane, pfreq in plane_freqs.items():
                diff = abs(word_freq - pfreq)
                if diff < SLEEPER_BAND:
                    close_planes.append((plane, diff))

            close_planes.sort(key=lambda x: x[1])

            if len(close_planes) >= 2:
                # Word is within the pull band of 2+ planes
                # This is a sleeper pin candidate
                plane_a, diff_a = close_planes[0]
                plane_b, diff_b = close_planes[1]
                sleeper_candidates.append((
                    word,
                    plane_a, diff_a,
                    plane_b, diff_b,
                    norm,
                    word_freq
                ))
            else:
                floating.append((word, assigned_plane, norm, word_freq))
        else:
            floating.append((word, assigned_plane, norm, None))

# Sort
for plane in strongly_anchored:
    strongly_anchored[plane].sort(key=lambda x: x[1], reverse=True)

floating.sort(key=lambda x: x[2], reverse=True)
sleeper_candidates.sort(key=lambda x: x[5], reverse=True)  # by norm

# ---------- REPORT 1: ANCHORED ----------
print("=" * 60)
print("STRONGLY ANCHORED — TOP 5 PER PLANE")
print("Words that have committed to a coordinate home")
print("=" * 60)

plane_order = [
    "VIOLET", "GRAY_ZERO", "WHITE_LIGHT", "BLACK_VOID",
    "RED", "RED_ORANGE", "ORANGE", "YELLOW_ORANGE", "YELLOW",
    "YELLOW_GREEN", "GREEN", "GREEN_TEAL", "TEAL", "CYAN_BLUE",
    "BLUE_CYAN", "BLUE", "BLUE_INDIGO", "ULTRAVIOLET",
    "RED_PURPLE", "MAGENTA", "UNASSIGNED"
]

for plane in plane_order:
    words = strongly_anchored.get(plane, [])
    if not words:
        continue
    print(f"\n  {plane}  ({len(words)} anchored)")
    for word, norm in words[:5]:
        bar = "█" * min(20, int(norm * 2))
        print(f"    {word:<22} {norm:.3f}  {bar}")

# ---------- REPORT 2: FLOATING ----------
print()
print("=" * 60)
print("FLOATING TOKENS — not yet anchored (norm < 0.5)")
print("Words the model knows but hasn't placed with confidence")
print("=" * 60)

print(f"\n  Total floating: {len(floating)}")

print("\n  Closest to anchoring — almost there (top 15):")
for word, plane, norm, freq in floating[:15]:
    freq_str = f"freq={freq:.3f}" if freq is not None else "freq=?"
    bar = "░" * max(1, int(norm * 8))
    print(f"    {word:<22} norm={norm:.3f}  {freq_str:<14} [{plane}]  {bar}")

print("\n  Weakest — consider pruning if they don't belong (bottom 10):")
floating_asc = sorted(floating, key=lambda x: x[2])
for word, plane, norm, freq in floating_asc[:10]:
    freq_str = f"freq={freq:.3f}" if freq is not None else "freq=?"
    print(f"    {word:<22} norm={norm:.4f}  {freq_str}  [{plane}]")

# ---------- REPORT 3: SLEEPER PIN CANDIDATES ----------
print()
print("=" * 60)
print("SLEEPER PIN CANDIDATES")
print("Words being pulled toward TWO planes simultaneously")
print("These are not broken — they are multi-planar")
print()
print("Example: 'love' in 'I love movies'  → comfort plane")
print("         'love' in 'I love my family' → bond plane")
print("         Same word. Two valid coordinates.")
print("         Sleeper pin gives it BOTH anchors.")
print("         Context decides which fires.")
print("=" * 60)

print(f"\n  Total sleeper pin candidates: {len(sleeper_candidates)}")
print()

if sleeper_candidates:
    print(f"  {'WORD':<22} {'PLANE A':<16} {'PLANE B':<16} {'NORM':<8} {'FREQ'}")
    print(f"  {'-'*22} {'-'*16} {'-'*16} {'-'*8} {'-'*8}")
    for word, pa, da, pb, db, norm, freq in sleeper_candidates[:30]:
        freq_str = f"{freq:.3f}" if freq is not None else "?"
        print(f"  {word:<22} {pa:<16} {pb:<16} {norm:<8.3f} {freq_str}")

    print()
    print("  INTERPRETATION:")
    print("  These words need dual anchors — one pin per plane.")
    print("  During inference, the active plane context selects which pin fires.")
    print("  This is how ARIA will understand 'love' differently in different sentences.")

# ---------- REPORT 4: EMPIRE ANALYSIS ----------
print()
print("=" * 60)
print("EMPIRE ANALYSIS — why it dominates output")
print("=" * 60)

empire_id = tokenizer.vocab.get("empire")
if empire_id is not None:
    empire_norm   = norms[empire_id].item()
    empire_plane  = tokenizer.word_to_plane.get("empire", "unknown")
    empire_freq   = WORD_FREQUENCIES.get("empire", None)

    print(f"\n  token id:   {empire_id}")
    print(f"  plane:      {empire_plane}")
    print(f"  norm:       {empire_norm:.4f}")
    print(f"  word freq:  {empire_freq}")

    plane_words = strongly_anchored.get(empire_plane, [])
    for rank, (word, norm) in enumerate(plane_words):
        if word == "empire":
            print(f"  plane rank: #{rank+1} of {len(plane_words)} in {empire_plane}")
            break

    print()
    stronger = [(w, n) for w, n in plane_words if n > empire_norm]
    if stronger:
        print(f"  Words stronger than empire in {empire_plane}:")
        for w, n in stronger[:10]:
            print(f"    {w:<22} {n:.3f}")
    else:
        print(f"  empire IS the strongest anchor in {empire_plane}")
        print(f"  This explains why it dominates — nothing outpulls it yet.")
        print(f"  More training or a stronger competing word will displace it.")
else:
    print("\n  'empire' not found in vocab")

# ---------- SUMMARY ----------
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

total_anchored  = sum(len(v) for v in strongly_anchored.values())
total_floating  = len(floating)
total_sleeper   = len(sleeper_candidates)
total_mapped    = total_anchored + total_floating + total_sleeper
total_slots     = embed_weights.shape[0]
total_unmapped  = total_slots - total_mapped

print(f"""
  Vocab slots total:        {total_slots}
  Strongly anchored:        {total_anchored:<6}  ({100*total_anchored/total_slots:.1f}%)
  Floating (weak):          {total_floating:<6}  ({100*total_floating/total_slots:.1f}%)
  Sleeper pin candidates:   {total_sleeper:<6}  ({100*total_sleeper/total_slots:.1f}%)
  Unmapped (no word):       {total_unmapped:<6}  ({100*total_unmapped/total_slots:.1f}%)

  NEXT ACTIONS:
  1. Sleeper pins  — assign dual anchors to multi-planar words
  2. Floating top  — corpus pressure will anchor these naturally
  3. Floating bottom — evaluate for pruning (do they belong?)
  4. Empire rank   — if #1 in plane, needs stronger competition
                     either more VIOLET training data
                     or introduce a stronger anchor word
""")

print("Diagnostic complete.")
print("NO RETREAT. NO SURRENDER. 💙🐗")