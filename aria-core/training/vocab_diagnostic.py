#!/usr/bin/env python3
"""
ARIA Vocabulary Diagnostic
===========================
Commander Anthony Hagerty — Haskell Texas
April 2026

Run this any time to see:
  - Current vocabulary size
  - UNK rate against the corpus
  - Top words hitting UNK (words to add next)
  - Unmask phases completed

Usage:
  python3 aria-core/training/vocab_diagnostic.py

NO RETREAT. NO SURRENDER. 💙🐗
"""

import sys
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tokenizer.aria_tokenizer import ARIATokenizer

# ── CONFIG ────────────────────────────────────────────────────────────
SAMPLE_LINES   = 500_000   # lines to sample from corpus — fast but representative
TOP_UNK        = 50        # how many top UNK words to show
CORPUS_FILES   = [
    Path(__file__).parent / "corpus_tinystories.txt",
    Path(__file__).parent / "corpus_wildchat.txt",
]
STRIP_CHARS    = ".,!?;:\"'()-[]{}<>@#$%^&*+=|/\\"
UNMASK_REGISTRY = Path(__file__).parent.parent.parent / "tokenizer" / "unmask_registry.json"

# ── LOAD TOKENIZER ────────────────────────────────────────────────────
print()
print("=" * 60)
print("  ARIA VOCABULARY DIAGNOSTIC")
print("=" * 60)
print()

tokenizer = ARIATokenizer.load()
vocab     = tokenizer.vocab
unk_id    = vocab.get("<UNK>", 2301)

print(f"  Vocabulary size:    {len(vocab):,} tokens")
print(f"  UNK token id:       {unk_id}")
print()

# ── UNMASK REGISTRY ───────────────────────────────────────────────────
print("  Unmask phases completed:")
if UNMASK_REGISTRY.exists():
    with open(UNMASK_REGISTRY) as f:
        reg = json.load(f)
    if reg:
        for phase, data in reg.items():
            plane   = data.get("plane", "?")
            count   = data.get("unlocked_count", "?")
            date    = data.get("date", "?")
            print(f"    {phase:10s}  plane={plane:8s}  tokens={count}  date={date}")
    else:
        print("    None completed yet")
else:
    print("    Registry not found")
print()

# ── SAMPLE CORPUS ─────────────────────────────────────────────────────
print(f"  Sampling {SAMPLE_LINES:,} lines from corpus...")
unk_words   = Counter()
total_tokens = 0
unk_count    = 0
lines_read   = 0

for corpus_file in CORPUS_FILES:
    if not corpus_file.exists():
        print(f"    MISSING: {corpus_file.name}")
        continue
    with open(corpus_file, encoding="utf-8", errors="replace") as f:
        for line in f:
            if lines_read >= SAMPLE_LINES:
                break
            for word in line.lower().split():
                clean = word.strip(STRIP_CHARS)
                if not clean:
                    continue
                total_tokens += 1
                tid = vocab.get(clean, unk_id)
                if tid == unk_id:
                    unk_count += 1
                    unk_words[clean] += 1
            lines_read += 1
    if lines_read >= SAMPLE_LINES:
        break

# ── RESULTS ───────────────────────────────────────────────────────────
unk_rate = (unk_count / max(total_tokens, 1)) * 100

print()
print("=" * 60)
print("  RESULTS")
print("=" * 60)
print()
print(f"  Lines sampled:      {lines_read:,}")
print(f"  Total tokens seen:  {total_tokens:,}")
print(f"  UNK hits:           {unk_count:,}")
print(f"  UNK rate:           {unk_rate:.2f}%")
print()

if unk_rate < 15.0:
    print(f"  STATUS: ✔ GOOD — UNK rate below 15% target")
elif unk_rate < 20.0:
    print(f"  STATUS: ⚠ CLOSE — add top UNK words to push below 15%")
else:
    print(f"  STATUS: ✖ HIGH — vocabulary expansion needed")

print()
print(f"  Top {TOP_UNK} words hitting UNK (add these next):")
print()
print(f"  {'WORD':<25} {'COUNT':>8}  {'ADD WITH RESONANCE'}")
print(f"  {'-'*25} {'-'*8}  {'-'*20}")

for word, count in unk_words.most_common(TOP_UNK):
    # rough resonance hint based on word characteristics
    if any(c.isdigit() for c in word):
        hint = "0.02  # numeric"
    elif len(word) <= 2:
        hint = "0.02  # connector"
    elif word.endswith("ing") or word.endswith("ed"):
        hint = "0.03  # action"
    elif word.endswith("ly"):
        hint = "0.03  # modifier"
    else:
        hint = "0.05  # general — tune manually"
    print(f"  {word:<25} {count:>8,}  {hint}")

print()
print("=" * 60)
print("  NEXT STEPS")
print("=" * 60)
print()
print("  1. Add top UNK words to tokenizer via expand_vocabulary.py")
print("  2. Add 20newsgroups CSV to corpus")
print("  3. Run unmasking pass (next plane after BLUE)")
print("  4. Resume training from current best checkpoint")
print()
print("  Current best checkpoint:")
ckpt_dir = Path(__file__).parent / "checkpoints"
ckpts = sorted(ckpt_dir.glob("round*_best.pt"),
               key=lambda x: int(x.stem.split("round")[1].split("_")[0]))
if ckpts:
    latest = ckpts[-1]
    print(f"    {latest.name}")
    try:
        import torch
        d = torch.load(latest, map_location="cpu")
        print(f"    loss = {d.get('best_loss', '?'):.6f}")
    except Exception:
        print(f"    (load torch to see loss)")
else:
    print("    No checkpoints found")

print()
print("NO RETREAT. NO SURRENDER. 💙🐗")
print()
