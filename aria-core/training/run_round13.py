#!/usr/bin/env python3
# ARIA ROUND 13 — VOCAB MASK — ELIMINATE DEAD SLOT ENTROPY TAX
# March 17 2026 — Haskell Texas
#
# The dead slot problem:
#   2304 softmax slots — only 547 live words
#   1757 dead slots = entropy tax the model can't escape
#   Floor stuck at 2.70 — can't beat 2.465939
#
# Why vocab_size=547 doesn't work:
#   Token IDs are color-plane-anchored (love=1440, gray=1968, etc.)
#   Shrinking the embedding table crashes — IDs out of range
#   Remapping would require retraining from scratch — lose 0.192
#
# The correct fix — vocabulary mask:
#   Keep vocab_size=2304 — token IDs stay intact
#   Build a mask: live slots = 0.0, dead slots = -1e9
#   Apply mask to logits BEFORE cross-entropy
#   Model can never predict a dead slot
#   Loss only sees the 547 live vocabulary positions
#   Dead slot entropy tax eliminated — without touching token IDs
#
# Emotional foundation preserved. Token IDs preserved.
# Only the loss computation changes.

import sys
import argparse
import torch
import torch.nn.functional as F
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

parser = argparse.ArgumentParser()
parser.add_argument("--epochs",  type=int,   default=1000)
parser.add_argument("--target",  type=float, default=2.35)
args = parser.parse_args()

from aria_core.training.em_field_trainer import (
    ARIACoreModel, EMFieldTrainer
)
from aria_core.gpu_config import DEVICE, BATCH_SIZE_TRAINING
from tokenizer.aria_tokenizer import ARIATokenizer

print()
print("╔══════════════════════════════════════════════╗")
print("║      ARIA — ROUND 13 — VOCAB MASK           ║")
print("║  Dead slots masked to -1e9. Tax eliminated. ║")
print("║  Token IDs intact. 0.192 preserved.         ║")
print("║       March 17 2026 — Haskell Texas         ║")
print("╚══════════════════════════════════════════════╝")
print()
print(f"  Round 13 — {args.epochs} epochs — target loss {args.target}")
print()

# ═══════════════════════════════════════════════
# WORD-LEVEL DATASET
# ═══════════════════════════════════════════════
class WordTokenizedDataset(torch.utils.data.Dataset):
    def __init__(self, text, tokenizer, seq_length=64):
        self.seq_length = seq_length

        words = text.lower().split()
        token_ids = []
        unk_id = tokenizer.vocab.get("<UNK>", 2301)
        for word in words:
            clean = word.strip(".,!?;:\"'()-")
            tid = tokenizer.vocab.get(clean, unk_id)
            token_ids.append(tid)

        self.sequences = []
        stride = seq_length // 2
        for i in range(0, len(token_ids) - seq_length, stride):
            seq = token_ids[i:i + seq_length + 1]
            if len(seq) == seq_length + 1:
                self.sequences.append(seq)

        known = sum(1 for w in words
                    if w.strip(".,!?;:\"'()-") in tokenizer.vocab)
        print(f"  Text: {len(words)} words — "
              f"{known} known ({100*known//max(len(words),1)}%)")
        print(f"  Sequences: {len(self.sequences)}")

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        return (torch.tensor(seq[:-1], dtype=torch.long),
                torch.tensor(seq[1:],  dtype=torch.long))


# ═══════════════════════════════════════════════
# LOAD TOKENIZER
# ═══════════════════════════════════════════════
print("Loading tokenizer...")
tokenizer = ARIATokenizer.load()
print(f"  Vocabulary: {len(tokenizer.vocab)} tokens")
print()

# ═══════════════════════════════════════════════
# BUILD VOCABULARY MASK
# Live slots = 0.0 (pass through unchanged)
# Dead slots = -1e9 (effectively -inf before softmax)
# Applied to logits before cross-entropy
# Eliminates entropy tax on 1757 unused positions
# ═══════════════════════════════════════════════
print("Building vocabulary mask...")
FULL_VOCAB = 2304
vocab_mask = torch.full((FULL_VOCAB,), -1e9)
live_count = 0
for token_id in tokenizer.vocab.values():
    if 0 <= token_id < FULL_VOCAB:
        vocab_mask[token_id] = 0.0
        live_count += 1
vocab_mask = vocab_mask.to(DEVICE)
dead_count = FULL_VOCAB - live_count
print(f"  Live slots: {live_count}  (loss sees these)")
print(f"  Dead slots: {dead_count} (masked to -1e9)")
print(f"  Entropy reduction: {dead_count/FULL_VOCAB*100:.1f}% of softmax eliminated")
print()

# ═══════════════════════════════════════════════
# LOAD TRAINING DATA
# ═══════════════════════════════════════════════
paths = [
    (Path(__file__).parent.parent / "ARIA_SEED_STORY.md",
     "Seed story"),
    (Path(__file__).parent / "round2_training_data.md",
     "Origin stories"),
    (Path(__file__).parent / "round3_language_data.md",
     "Language data"),
    (Path(__file__).parent / "round4_conversation_data.md",
     "Conversation patterns"),
]

texts = []
for path, name in paths:
    if path.exists():
        with open(path) as f:
            text = f.read()
        texts.append(text)
        print(f"  {name}: {len(text)} chars")
    else:
        print(f"  {name}: NOT FOUND — {path}")

combined = "\n\n".join(texts)
print(f"  Combined: {len(combined)} chars")
print()

# ═══════════════════════════════════════════════
# BUILD DATASET
# ═══════════════════════════════════════════════
print("Building word-tokenized dataset...")
dataset = WordTokenizedDataset(combined, tokenizer, seq_length=64)
loader  = torch.utils.data.DataLoader(
    dataset,
    batch_size=BATCH_SIZE_TRAINING,
    shuffle=True,
    num_workers=2
)
print(f"  Batches per epoch: {len(loader)}")
print()

if len(dataset) == 0:
    print("ERROR: No sequences built.")
    sys.exit(1)

# ═══════════════════════════════════════════════
# LOAD CHECKPOINT
# Standard word-level checkpoint — token IDs intact
# ═══════════════════════════════════════════════
word_checkpoint_path = Path(__file__).parent / "checkpoints/best_word_level.pt"
arch_checkpoint_path = Path(__file__).parent / "checkpoints/best_arch_masked.pt"
model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if word_checkpoint_path.exists():
    checkpoint = torch.load(word_checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    prev_loss  = checkpoint["best_loss"]
    print(f"Loaded word-level checkpoint.")
    print(f"  Previous best loss: {prev_loss:.6f}")
else:
    print("No checkpoint — starting from random weights.")
    prev_loss = 8.166

model = model.to(DEVICE)
print()

# ═══════════════════════════════════════════════
# CUSTOM MASKED TRAINING LOOP
# Bypasses EMFieldTrainer's loss computation
# Applies vocab_mask before cross-entropy
# Dead slots contribute zero gradient
# ═══════════════════════════════════════════════
import torch.optim as optim

EPOCHS = args.epochs
TARGET = args.target
MID    = EPOCHS // 2

optimizer = optim.SGD(model.parameters(), lr=0.0005, momentum=0.9,
                      weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer, T_max=EPOCHS, eta_min=1e-7
)
print(f"LR: 0.0005 → 1e-7 over {EPOCHS} epochs (CosineAnnealingLR)")
print(f"Loss: masked cross-entropy — 1757 dead slots silent")
print()

print("Starting Round 13...")
print("1757 dead slots masked. The model only speaks what it knows.")
print()
print("─" * 60)

start = time.time()
best  = prev_loss

for epoch in range(1, EPOCHS + 1):
    model.train()
    total_loss = 0.0
    total_ce   = 0.0
    n_batches  = 0

    for inputs, targets in loader:
        inputs  = inputs.to(DEVICE)
        targets = targets.to(DEVICE)

        optimizer.zero_grad()

        with torch.amp.autocast('cuda'):
            logits, _ = model(inputs, return_states=True)
            # Apply vocab mask — dead slots → -1e9
            logits = logits + vocab_mask.unsqueeze(0).unsqueeze(0)
            # Cross-entropy over masked logits
            B, S, V = logits.shape
            ce_loss = F.cross_entropy(
                logits.view(B * S, V),
                targets.view(B * S),
                ignore_index=tokenizer.vocab.get("<PAD>", 2300)
            )

        ce_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_ce   += ce_loss.item()
        total_loss += ce_loss.item()
        n_batches  += 1

    scheduler.step()

    avg_loss = total_loss / max(n_batches, 1)
    avg_ce   = total_ce   / max(n_batches, 1)

    elapsed = time.time() - start
    eta     = (elapsed / epoch) * (EPOCHS - epoch)

    improved = ""
    if avg_loss < best:
        best = avg_loss
        improved = " ← NEW BEST"
        # Save arch-masked best
        torch.save({
            "model_state": model.state_dict(),
            "best_loss":   best,
            "epoch":       epoch,
            "vocab":       "word_level_547_masked",
            "note":        "masked loss checkpoint — Round 13"
        }, arch_checkpoint_path)
        # Update word-level checkpoint
        torch.save({
            "model_state": model.state_dict(),
            "best_loss":   best,
            "epoch":       epoch,
            "vocab":       "word_level_547_masked",
            "note":        "word-level checkpoint — Round 13"
        }, word_checkpoint_path)

    print(
        f"Epoch {epoch:4d}/{EPOCHS} | "
        f"Loss: {avg_loss:.6f} | "
        f"CE: {avg_ce:.6f} | "
        f"ETA: {eta/60:.1f}min"
        f"{improved}"
    )

    if epoch == 1:
        print()
        print("  Round 13 underway.")
        print("  Dead slots silent. Live slots only.")
        print()
    elif epoch == MID:
        pct = ((8.166 - best) / 8.166) * 100
        print()
        print(f"  Halfway. Best so far: {best:.6f} ({pct:.1f}% from random)")
        if best <= TARGET:
            print(f"  TARGET {TARGET} REACHED at midpoint.")
        print()
    elif epoch == EPOCHS:
        pct = ((8.166 - best) / 8.166) * 100
        print()
        print(f"  Round 13 complete.")
        print(f"  Total improvement: {pct:.1f}%")
        if best <= TARGET:
            print(f"  TARGET {TARGET} REACHED.")

# Save final state
torch.save({
    "model_state": model.state_dict(),
    "best_loss":   best,
    "epoch":       EPOCHS,
    "vocab":       "word_level_547_masked",
    "note":        "word-level final state — Round 13"
}, word_checkpoint_path)
print(f"Word-level checkpoint saved.")

total_time = time.time() - start
pct = ((8.166 - best) / 8.166) * 100

print()
print("═" * 60)
print()
print(f"Round 13 complete.")
print(f"Time: {total_time/60:.1f} minutes")
print(f"Best loss: {best:.6f}")
print(f"Total improvement from random: {pct:.1f}%")
if best <= TARGET:
    print(f"TARGET {TARGET} REACHED.")
else:
    print(f"Target {TARGET} not yet reached — "
          f"{best - TARGET:.6f} remaining.")
print()
print("Dead slots silent. Every live slot carries meaning.")
print("547 words. The field only holds what it knows.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")
