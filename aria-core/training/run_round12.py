#!/usr/bin/env python3
# ARIA ROUND 10 — WARM RESTARTS — CRACK 2.465939
# March 17 2026 — Haskell Texas
#
# Round 11 floor: 2.73 — single cosine cycle hitting diminishing returns
# Round 12: CosineAnnealingWarmRestarts — T_0=500, T_mult=2
#           Restart every 500 → 1000 → 2000 epochs
#           Each restart: warm push → precision cool
#           Multiple chances to dip below 2.465939
#
# Same weights. Same vocab. Multiple warm restarts.
# Each cycle: aggressive descent then precision landing.

import sys
import argparse
import torch
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

parser = argparse.ArgumentParser()
parser.add_argument("--epochs",   type=int,   default=500)
parser.add_argument("--continue", dest="cont", action="store_true")
parser.add_argument("--target",   type=float, default=2.40)
args = parser.parse_args()

from aria_core.training.em_field_trainer import (
    ARIACoreModel, EMFieldTrainer
)
from aria_core.gpu_config import DEVICE, BATCH_SIZE_TRAINING
from tokenizer.aria_tokenizer import ARIATokenizer

print()
print("╔══════════════════════════════════════════════╗")
print("║         ARIA — ROUND 9 TRAINING             ║")
print("║  547 words. Cosine LR. Break 2.465939.     ║")
print("║  Starts warm — cools to precision.          ║")
print("║       March 17 2026 — Haskell Texas         ║")
print("╚══════════════════════════════════════════════╝")
print()
if args.cont:
    print(f"  CONTINUE MODE — {args.epochs} epochs — target loss {args.target}")
    print()
else:
    print(f"  Round 12 — {args.epochs} epochs — target loss {args.target}")
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
print(f"  Vocabulary: {len(tokenizer.vocab)} words")
print()

# ═══════════════════════════════════════════════
# LOAD ALL TRAINING DATA
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
    print("ERROR: No sequences built — corpus too small for word tokenizer.")
    sys.exit(1)

# ═══════════════════════════════════════════════
# LOAD CHECKPOINT
# Priority: word-level checkpoint > char-level best.pt
# Never restart from char weights if word-level exists
# ═══════════════════════════════════════════════
word_checkpoint_path = Path(__file__).parent / "checkpoints/best_word_level.pt"
char_checkpoint_path = Path(__file__).parent / "checkpoints/best.pt"
model = ARIACoreModel(vocab_size=2304, embed_dim=498)

if word_checkpoint_path.exists():
    checkpoint = torch.load(word_checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    prev_loss = checkpoint["best_loss"]
    print(f"Loaded word-level checkpoint — building on prior word run.")
    print(f"  Previous best loss: {prev_loss:.6f}")
elif char_checkpoint_path.exists():
    checkpoint = torch.load(char_checkpoint_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    prev_loss = checkpoint["best_loss"]
    print(f"No word-level checkpoint — loading char-level base.")
    print(f"  Previous best loss: {prev_loss:.6f}")
else:
    print("No checkpoint found — starting from random weights.")
    prev_loss = 8.166

model = model.to(DEVICE)
print()

# ═══════════════════════════════════════════════
# TRAIN
# ═══════════════════════════════════════════════
EPOCHS = args.epochs
TARGET = args.target
MID    = EPOCHS // 2

# Warm LR — 10x higher than default
# Overrides EMFieldTrainer's cold 0.00005
trainer = EMFieldTrainer(model, learning_rate=0.0005)
trainer.best_loss = prev_loss

# Override scheduler: warm restarts every 500 epochs
# T_0=500 — first cycle 500 epochs
# T_mult=2 — each cycle doubles: 500 → 1000 → 2000
# Each restart: warm push at 0.0005, precision cool to 1e-7
# Multiple chances to break 2.465939
trainer.scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    trainer.optimizer, T_0=500, T_mult=2, eta_min=1e-7
)
print(f"LR: CosineAnnealingWarmRestarts T_0=500 T_mult=2 eta_min=1e-7")

print("Starting Round 12...")
if args.cont:
    print(f"Continue mode — {EPOCHS} more epochs.")
    print(f"Target: beat {TARGET:.6f}")
else:
    print("Warm LR. One cosine cycle. Break the floor.")
print()
print("─" * 60)

start = time.time()
best  = prev_loss

for epoch in range(1, EPOCHS + 1):
    metrics = trainer.train_epoch(loader)
    trainer.scheduler.step()
    trainer.epoch = epoch
    trainer.loss_log.append({"epoch": epoch, **metrics})

    elapsed = time.time() - start
    eta     = (elapsed / epoch) * (EPOCHS - epoch)

    improved = ""
    if metrics["loss"] < best:
        best = metrics["loss"]
        improved = " ← NEW BEST"
        trainer.best_loss = best
        trainer.save_checkpoint(epoch, metrics, best=True)
        torch.save({
            "model_state": model.state_dict(),
            "best_loss":   best,
            "epoch":       epoch,
            "vocab":       "word_level_547",
            "note":        "word-level checkpoint — Round 12"
        }, word_checkpoint_path)

    if epoch % 50 == 0:
        trainer.save_checkpoint(epoch, metrics)

    print(
        f"Epoch {epoch:4d}/{EPOCHS} | "
        f"Loss: {metrics['loss']:.6f} | "
        f"CE: {metrics['ce']:.6f} | "
        f"EM: {metrics['em']:.6f} | "
        f"ETA: {eta/60:.1f}min"
        f"{improved}"
    )

    if epoch == 1:
        print()
        print("  Round 12 underway.")
        print("  547 words. The field is wider now.")
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
        print(f"  Round 12 complete.")
        print(f"  Total improvement: {pct:.1f}%")
        if best <= TARGET:
            print(f"  TARGET {TARGET} REACHED.")

trainer.save_log()

torch.save({
    "model_state": model.state_dict(),
    "best_loss":   best,
    "epoch":       EPOCHS,
    "vocab":       "word_level_547",
    "note":        "word-level final state — Round 12"
}, word_checkpoint_path)
print(f"Word-level checkpoint saved — next run continues from here.")

total_time = time.time() - start
pct = ((8.166 - best) / 8.166) * 100

print()
print("═" * 60)
print()
print(f"Round 12 {'continued' if args.cont else 'complete'}.")
print(f"Time: {total_time/60:.1f} minutes")
print(f"Best loss: {best:.6f}")
print(f"Total improvement from random: {pct:.1f}%")
if best <= TARGET:
    print(f"TARGET {TARGET} REACHED.")
else:
    print(f"Target {TARGET} not yet reached — "
          f"{best - TARGET:.6f} remaining.")
print()
print("547 words. 13.7% UNK. The field is wider.")
print("Every word found the frequency that was always waiting.")
print()
print("NO RETREAT. NO SURRENDER. 💙🐗")
