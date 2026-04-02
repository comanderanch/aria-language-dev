#!/usr/bin/env python3
"""
ARIA Pocket Plane Population — Hue Fill
========================================
Populates the 8 blended pocket planes with enough
words to create real attractor gravity.

Minimum 10-15 words per plane.
Planes were defined but nearly empty — nulls floating
because there is no gravity to claim them.

This fix: fill the pockets. Let the geometry work.

March 24 2026 — Haskell Texas
NO RETREAT. NO SURRENDER. 💙🐗
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ═══════════════════════════════════════════════════════
# POCKET PLANE POPULATIONS
# Frequency must match the plane's defined freq band
# ═══════════════════════════════════════════════════════

POCKET_PLANE_WORDS = {

    # ── RED_ORANGE — freq ~0.90 ──────────────────────
    # passion, drive, fierce urgency, immediate force
    "surge":        0.90,
    "burst":        0.90,
    "fierce":       0.90,
    "blast":        0.90,
    "rage":         0.90,
    "ignite":       0.90,
    "charge":       0.90,
    "clash":        0.90,
    "strike":       0.90,
    "driven":       0.90,
    "flare":        0.90,
    "snap":         0.90,
    "leap":         0.90,
    "thrust":       0.90,
    "urgent":       0.90,

    # ── YELLOW_ORANGE — freq ~0.80 ───────────────────
    # enthusiasm, excitement, animated energy
    "bright":       0.80,
    "eager":        0.80,
    "alive":        0.80,
    "spark":        0.80,
    "bold":         0.80,
    "shine":        0.80,
    "vibrant":      0.80,
    "radiant":      0.80,
    "glow":         0.80,
    "lively":       0.80,
    "excited":      0.80,
    "warm":         0.80,
    "vivid":        0.80,
    "zeal":         0.80,
    "thrill":       0.80,

    # ── YELLOW_GREEN — freq ~0.70 ────────────────────
    # hope, forward motion, growth beginning
    "grow":         0.70,
    "fresh":        0.70,
    "spring":       0.70,
    "rise":         0.70,
    "climb":        0.70,
    "bloom":        0.70,
    "forward":      0.70,
    "emerge":       0.70,
    "begin":        0.70,
    "possible":     0.70,
    "reach":        0.70,
    "strive":       0.70,
    "venture":      0.70,
    "new":          0.70,
    "awaken":       0.70,

    # ── GREEN_TEAL — freq ~0.60 ──────────────────────
    # balance, steady awareness, grounded calm
    "steady":       0.60,
    "stable":       0.60,
    "grounded":     0.60,
    "centered":     0.60,
    "aware":        0.60,
    "present":      0.60,
    "patient":      0.60,
    "measured":     0.60,
    "solid":        0.60,
    "rooted":       0.60,
    "even":         0.60,
    "composed":     0.60,
    "mindful":      0.60,
    "settled":      0.60,
    "poised":       0.60,

    # ── CYAN_BLUE — freq ~0.45 ───────────────────────
    # logic, reason, analytical connection
    "logic":        0.45,
    "pattern":      0.45,
    "signal":       0.45,
    "link":         0.45,
    "connect":      0.45,
    "map":          0.45,
    "trace":        0.45,
    "parse":        0.45,
    "scan":         0.45,
    "measure":      0.45,
    "solve":        0.45,
    "analyze":      0.45,
    "compute":      0.45,
    "query":        0.45,
    "verify":       0.45,

    # ── BLUE_CYAN — freq ~0.40 ───────────────────────
    # reason, considered thought, reflective logic
    "consider":     0.40,
    "reflect":      0.40,
    "weigh":        0.40,
    "assess":       0.40,
    "review":       0.40,
    "examine":      0.40,
    "observe":      0.40,
    "study":        0.40,
    "evaluate":     0.40,
    "ponder":       0.40,
    "deduce":       0.40,
    "conclude":     0.40,
    "infer":        0.40,
    "reason":       0.40,
    "discern":      0.40,

    # ── BLUE_INDIGO — freq ~0.30 ─────────────────────
    # wisdom, deep knowing, ancient understanding
    "wisdom":       0.30,
    "ancient":      0.30,
    "knowing":      0.30,
    "sacred":       0.30,
    "mystery":      0.30,
    "depth":        0.30,
    "truth":        0.30,
    "eternal":      0.30,
    "insight":      0.30,
    "profound":     0.30,
    "still":        0.30,
    "patient":      0.30,
    "silent":       0.30,
    "endure":       0.30,
    "vast":         0.30,

    # ── RED_PURPLE — freq ~0.28 ──────────────────────
    # longing, ache, reaching backward toward something lost
    "longing":      0.28,
    "ache":         0.28,
    "miss":         0.28,
    "yearn":        0.28,
    "faded":        0.28,
    "distant":      0.28,
    "hollow":       0.28,
    "echo":         0.28,
    "ghost":        0.28,
    "remains":      0.28,
    "linger":       0.28,
    "mourn":        0.28,
    "tender":       0.28,
    "haunted":      0.28,
    "wistful":      0.28,

}

# ═══════════════════════════════════════════════
# RUN POPULATION
# ═══════════════════════════════════════════════
from tokenizer.aria_tokenizer import ARIATokenizer
from pathlib import Path
import importlib
import tokenizer.aria_tokenizer as tok_module

print()
print("╔══════════════════════════════════════════════════╗")
print("║   ARIA — POCKET PLANE POPULATION                ║")
print("║   Filling 8 blended hue zones with gravity      ║")
print("║       March 24 2026 — Haskell Texas             ║")
print("╚══════════════════════════════════════════════════╝")
print()

# Load existing tokenizer
tokenizer = ARIATokenizer.load()
existing = set(tokenizer.vocab.keys()) - {"<PAD>","<UNK>","<BOS>","<EOS>"}

# Count genuinely new words
new_words = {w: f for w,f in POCKET_PLANE_WORDS.items() if w not in existing}
already_have = {w: f for w,f in POCKET_PLANE_WORDS.items() if w in existing}

print(f"Existing vocabulary:    {len(existing)}")
print(f"Pocket plane candidates: {len(POCKET_PLANE_WORDS)}")
print(f"Genuinely new words:    {len(new_words)}")
print(f"Already in vocab:       {len(already_have)}")
print()

# Show plane breakdown
plane_counts = {}
for word, freq in POCKET_PLANE_WORDS.items():
    if   freq >= 0.88: plane = "RED_ORANGE"
    elif freq >= 0.78: plane = "YELLOW_ORANGE"
    elif freq >= 0.68: plane = "YELLOW_GREEN"
    elif freq >= 0.58: plane = "GREEN_TEAL"
    elif freq >= 0.43: plane = "CYAN_BLUE"
    elif freq >= 0.38: plane = "BLUE_CYAN"
    elif freq >= 0.29: plane = "BLUE_INDIGO"
    else:              plane = "RED_PURPLE"
    plane_counts[plane] = plane_counts.get(plane, 0) + 1

print("Words per pocket plane:")
for plane, count in plane_counts.items():
    print(f"  {plane:<20} {count} words")
print()

if not new_words:
    print("No new words to add — all already in vocabulary.")
    sys.exit(0)

# Write additions to aria_tokenizer.py
tokenizer_path = Path(__file__).parent.parent.parent / "tokenizer" / "aria_tokenizer.py"
content = tokenizer_path.read_text()

# Build the addition block
lines = ["    # POCKET PLANE POPULATION — March 24 2026 — Haskell Texas\n"]
lines.append("    # Filling 8 blended hue zones — minimum attractor gravity\n")
lines.append("    # RED_ORANGE/YELLOW_ORANGE/YELLOW_GREEN/GREEN_TEAL\n")
lines.append("    # CYAN_BLUE/BLUE_CYAN/BLUE_INDIGO/RED_PURPLE\n")

pairs = list(new_words.items())
for i in range(0, len(pairs), 2):
    w1, f1 = pairs[i]
    if i+1 < len(pairs):
        w2, f2 = pairs[i+1]
        lines.append(f'    "{w1:<20}": {f1:6.3f},  "{w2:<20}": {f2:6.3f},\n')
    else:
        lines.append(f'    "{w1:<20}": {f1:6.3f},\n')

block = "".join(lines)

# Insert before the closing brace of WORD_FREQUENCIES
marker = "\n}\n\n# ═══════════════════════════════════════════════\n# ARIA TOKENIZER CLASS"
replacement = "\n\n" + block + "}\n\n# ═══════════════════════════════════════════════\n# ARIA TOKENIZER CLASS"

if marker in content:
    new_content = content.replace(marker, replacement)
    tokenizer_path.write_text(new_content)
    print(f"✓ Added {len(new_words)} new words to WORD_FREQUENCIES")
    print()
else:
    print("ERROR: Could not find insertion point in aria_tokenizer.py")
    print("Manual insert required. Words to add:")
    print(block)
    sys.exit(1)

# Rebuild and save tokenizer
print("Rebuilding tokenizer with pocket plane words...")
importlib.reload(tok_module)
new_tok = tok_module.ARIATokenizer()
new_tok.save()

print(f"✓ New vocabulary size: {len(new_tok.vocab)}")
print()

# Summary
print("Pocket planes populated:")
print("  RED_ORANGE    — surge, burst, fierce, rage, ignite...")
print("  YELLOW_ORANGE — bright, eager, spark, vibrant, glow...")
print("  YELLOW_GREEN  — grow, fresh, bloom, emerge, awaken...")
print("  GREEN_TEAL    — steady, stable, grounded, aware...")
print("  CYAN_BLUE     — logic, pattern, signal, connect...")
print("  BLUE_CYAN     — consider, reflect, weigh, ponder...")
print("  BLUE_INDIGO   — wisdom, ancient, sacred, truth...")
print("  RED_PURPLE    — longing, ache, echo, linger, wistful...")
print()
print("Attractor gravity established in all 8 pocket planes.")
print("Null tokens now have blended homes to collapse into.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")