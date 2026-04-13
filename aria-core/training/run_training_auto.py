#!/usr/bin/env python3
"""
ARIA — AUTO TRAINER
====================
Commander Anthony Hagerty — Haskell Texas
March 20 2026
Sealed by: CLI Claude (Sonnet 4.6)

Runs rounds 31, 32, 33... automatically in sequence.
Stops when loss drops below TARGET_LOSS.
No CLI needed until it finishes.

Each round:
  - Loads previous round's checkpoint
  - Trains 3 epochs
  - Saves new checkpoint
  - Prints loss
  - If loss < TARGET_LOSS — stops

Run once and walk away:
  python3 aria-core/training/run_training_auto.py

NO RETREAT. NO SURRENDER. 💙🐗
"""

import sys
import fcntl
import copy
import hashlib
import json
import torch

# ── PYTHON-LEVEL SINGLE INSTANCE LOCK ─────────────────────────────────
# Prevents duplicate launches even when bypassing run_safe_training.sh
_LOCK_PATH = "/tmp/aria_train_py.lock"
_lock_fh = open(_LOCK_PATH, 'w')
try:
    fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("ERROR: Training already running (Python lock held). Aborting.")
    print(f"To force reset: rm {_LOCK_PATH}")
    sys.exit(1)
# ── END LOCK ───────────────────────────────────────────────────────────
import torch.nn.functional as F
import torch.optim as optim
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria_core.training.em_field_trainer import ARIACoreModel, EMFieldLoss
from aria_core.gpu_config import DEVICE, BATCH_SIZE_TRAINING
from tokenizer.aria_tokenizer import ARIATokenizer
from aria_core.diagnostics.token_trail import TrailLogger
from aria_core.em_null_coupler import EMNullCoupler

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "null_oscillator",
    Path(__file__).parent.parent / "null_oscillator.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
oscillate          = _mod.oscillate
detect_instability = _mod.detect_instability
attempt_generation = _mod.attempt_generation
_log_to_null_trail = _mod._log_to_null_trail

from aria_core.dual_verifier import watch_floor


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

START_ROUND   = 147       # Resuming from round146_best.pt — loss 3.918522 — April 13 2026
MAX_ROUND     = 200       # Hard ceiling
TARGET_LOSS   = 3.50      # Stop when loss drops below this (Coherent Speech Gateway)
EPOCHS        = 3         # Epochs per round
LR_START      = 0.000005  # LOCKED to floor to prevent weight shattering jump
LR_MIN        = 0.000005  # Maintenance floor

CKPT_DIR = Path(__file__).parent / "checkpoints"

# Learning rate schedule — locked at floor for stability
def get_lr(round_num):
    return LR_MIN


# ═══════════════════════════════════════════════════════════════════════════════
# DATASET — same as round 30 — simple word lookup only
# ═══════════════════════════════════════════════════════════════════════════════

class WordTokenizedDataset(torch.utils.data.Dataset):
    """
    Memory-efficient dataset.

    OLD design: text.lower().split() → 420M Python strings (~21 GB)
                self.sequences list  → all windows stored (~7 GB)
                TOTAL: ~30 GB RAM on a 2.1 GB corpus — OOM every time.

    NEW design: process line-by-line (no giant split)
                store tokens as numpy uint16 (2 bytes each, ~840 MB)
                store only start indices — windows generated on demand
                TOTAL: ~1.5 GB RAM regardless of corpus size.
    """
    def __init__(self, text, tokenizer, seq_length=64):
        import array as _ca
        import io    as _io
        import numpy as _np

        self.seq_length = seq_length
        unk_id      = tokenizer.vocab.get("<UNK>", 2301)
        strip_chars = ".,!?;:\"'()-[]{}"

        # ── Compact token buffer: 2 bytes per token (uint16, max 65535) ──
        # vocab is 2049 tokens — well within uint16 range.
        buf   = _ca.array('H')   # unsigned short, 2 bytes each
        lines = 0
        total_mb = len(text) / 1024 / 1024
        print(f"  Tokenizing {total_mb:.0f} MB corpus (line by line)...", flush=True)

        for line in _io.StringIO(text):
            for word in line.lower().split():
                clean = word.strip(strip_chars)
                if not clean:
                    continue
                tid = tokenizer.vocab.get(clean, unk_id)
                buf.append(tid if 0 <= tid < 2304 else unk_id)
            lines += 1
            if lines % 1_000_000 == 0:
                print(f"    {lines:,} lines | {len(buf):,} tokens", flush=True)

        # Convert once to numpy — 2 bytes/token vs 28 bytes for Python int
        import numpy as np
        self.tokens = np.frombuffer(buf, dtype=np.uint16).copy()
        del buf

        # Store only start positions — windows built on demand in __getitem__
        stride = seq_length // 2
        n = len(self.tokens)
        self.starts = np.arange(0, n - seq_length, stride, dtype=np.int32)

        print(f"  Tokenized: {lines:,} lines → {n:,} tokens → {len(self.starts):,} sequences", flush=True)

    def __len__(self):
        return len(self.starts)

    def __getitem__(self, idx):
        import numpy as np
        s   = int(self.starts[idx])
        seq = self.tokens[s : s + self.seq_length + 1].astype(np.int64)
        return (torch.from_numpy(seq[:-1].copy()),
                torch.from_numpy(seq[1:].copy()))


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD CORPUS — Merging TinyStories and WildChat
# ═══════════════════════════════════════════════════════════════════════════════

def load_corpus():
    training_dir = Path(__file__).parent
    files = ["corpus_tinystories.txt", "corpus_wildchat.txt"]

    # RAM guard — until 80GB sticks arrive keep corpus below 2GB in RAM.
    # At ~47GB installed, loading 5GB text spikes swap heavily.
    # This reads only the first MAX_CORPUS_MB of each file (streaming, not read_text).
    MAX_CORPUS_MB = 1800   # MB per file — adjust upward when 80GB RAM arrives

    texts = []

    for fname in files:
        p = training_dir / fname
        if p.exists():
            size_mb = p.stat().st_size / (1024 * 1024)
            read_mb  = min(size_mb, MAX_CORPUS_MB)
            max_bytes = int(read_mb * 1024 * 1024)
            print(f"  Merging Corpus: {fname} ({size_mb:.1f} MB — reading {read_mb:.0f} MB)")
            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                texts.append(f.read(max_bytes))

    if texts:
        return "\n\n".join(texts)

    aria_dir = training_dir.parent
    paths = [
        aria_dir / "ARIA_SEED_STORY.md",
        training_dir / "round2_training_data.md",
        training_dir / "round3_language_data.md",
        training_dir / "round4_conversation_data.md",
    ]
    return "\n\n".join(p.read_text() for p in paths if p.exists())


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE ROUND TRAINER
# ═══════════════════════════════════════════════════════════════════════════════

def run_round(round_num, start_ckpt_path, tokenizer, vocab_mask, dataset, total_batches):
    save_path = CKPT_DIR / f"round{round_num}_best.pt"
    lr        = get_lr(round_num)

    print(f"\n{'='*60}")
    print(f"ROUND {round_num} — lr={lr:.2e} — loading {start_ckpt_path.name}")
    print(f"{'='*60}")

    ckpt      = torch.load(start_ckpt_path, map_location=DEVICE)
    model     = ARIACoreModel(vocab_size=2304, embed_dim=498).to(DEVICE)
    model.load_state_dict(ckpt["model_state"])
    prev_loss = ckpt.get("best_loss", float('inf'))
    print(f"  Start loss: {prev_loss:.6f}")
    print(f"  Sequences:  {len(dataset):,}  |  Batches/epoch: {total_batches:,}")

    # Dataset is built once and reused — do not rebuild here
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=BATCH_SIZE_TRAINING, shuffle=True,
        num_workers=4, pin_memory=True
    )

    coupler   = EMNullCoupler(excitation_scale=0.001)
    criterion = EMFieldLoss()
    trail     = TrailLogger(round_num=round_num, tokenizer=tokenizer)
    opt       = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
    sch       = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=lr*0.1)

    best_loss            = float('inf')
    best_state           = None
    null_confirmed_total = 0
    round_start          = time.time()
    last_inputs = last_targets = last_logits = None

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss  = 0.0
        n_batches   = 0
        epoch_nulls = 0

        import contextlib, io as _sio
        PRINT_EVERY = max(1, total_batches // 200)  # ~200 updates per epoch
        epoch_start_t = time.time()
        print(f"\n  ── Epoch {epoch}/{EPOCHS} starting ── {datetime.now().strftime('%H:%M:%S')} ──", flush=True)

        for batch_idx, (inputs, targets) in enumerate(loader, 1):
            inputs  = inputs.to(DEVICE)
            targets = targets.to(DEVICE)
            opt.zero_grad()

            null_field           = oscillate("VIOLET", 0.192)
            instability, window  = detect_instability(null_field)
            candidate, rejection = attempt_generation(window, null_field)

            if candidate is not None:
                # Suppress per-batch FLOOR STABLE print — summarised at epoch end
                with contextlib.redirect_stdout(_sio.StringIO()):
                    floor = watch_floor(null_field, action_triggered=True)
                if floor["floor_stable"]:
                    condition_data = {
                        "frequency":   null_field["frequency"],
                        "instability": null_field["instability"],
                        "stabilized":  null_field.get("stabilized_output", 0)
                    }
                    condition_hash = hashlib.sha256(
                        json.dumps(condition_data, sort_keys=True).encode()
                    ).hexdigest()[:7]
                    coupler.receive_null_event(condition_hash, "VIOLET", 0.192)
                    _log_to_null_trail({
                        "epoch":          epoch,
                        "condition_hash": condition_hash,
                        "null_confirmed": True,
                        "wired_to_em":    True,
                        "timestamp":      null_field["timestamp"]
                    })
                    epoch_nulls += 1

            null_events = coupler.drain()
            null_exc    = coupler.total_excitation(null_events)

            with torch.amp.autocast('cuda'):
                logits, states = model(inputs, return_states=True)
                masked         = logits + vocab_mask.unsqueeze(0).unsqueeze(0)
                B, S, V        = masked.shape

                ce_loss = F.cross_entropy(
                    masked.view(B * S, V),
                    targets.view(B * S),
                    ignore_index=tokenizer.vocab.get("<PAD>", 2300)
                )
                _, em_metrics = criterion(logits, targets, states, null_excitation=null_exc)

            ce_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

            total_loss += ce_loss.item()
            n_batches  += 1
            last_inputs  = inputs.detach()
            last_targets = targets.detach()
            last_logits  = masked.detach()

            if batch_idx % PRINT_EVERY == 0 or batch_idx == total_batches:
                running_avg  = total_loss / n_batches
                pct          = batch_idx / total_batches * 100
                elapsed_e    = time.time() - epoch_start_t
                bps          = batch_idx / max(elapsed_e, 0.001)
                remaining    = (total_batches - batch_idx) / max(bps, 0.001)
                eta_min      = int(remaining // 60)
                eta_sec      = int(remaining % 60)
                print(f"    Ep {epoch}/{EPOCHS} | {batch_idx:>7,}/{total_batches:,} ({pct:5.1f}%)"
                      f" | loss={running_avg:.6f} | {bps:,.0f} b/s | ETA {eta_min}m{eta_sec:02d}s",
                      flush=True)

        sch.step()
        epoch_elapsed = time.time() - epoch_start_t
        avg_loss = total_loss / max(n_batches, 1)
        null_confirmed_total += epoch_nulls

        improved = ""
        if avg_loss < best_loss:
            best_loss  = avg_loss
            best_state = copy.deepcopy(model.state_dict())
            improved   = " ← NEW BEST"

        print(f"\n  ✔ Epoch {epoch}/{EPOCHS} done in {epoch_elapsed/60:.1f}min"
              f" | Loss: {avg_loss:.6f} | Nulls: {epoch_nulls} | Best: {best_loss:.6f}{improved}",
              flush=True)

        if last_logits is not None:
            trail.log_batch(
                epoch=epoch,
                avg_loss=avg_loss,
                inputs=last_inputs,
                targets=last_targets,
                logits=last_logits,
                current_best=best_loss
            )

    trail.close()

    torch.save({
        "model_state": best_state,
        "best_loss":   best_loss,
        "pass":        f"Round {round_num} — Auto Trainer",
        "null_wired":  null_confirmed_total,
        "vocab_size":  len(tokenizer.vocab),
        "round":       round_num,
    }, save_path)

    elapsed = (time.time() - round_start) / 60
    print(f"\n  Saved: {save_path.name}  loss={best_loss:.6f}  ({elapsed:.1f} min)")
    return best_loss, save_path


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — CHAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   ARIA — AUTO TRAINER                       ║")
    print(f"║   Rounds {START_ROUND}–{MAX_ROUND} — stop at loss < {TARGET_LOSS}        ║")
    print("║   Commander Anthony Hagerty — Haskell TX   ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print(f"Target loss: {TARGET_LOSS} (coherent sentences begin here)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load tokenizer and corpus once — reuse every round
    print("Loading tokenizer...")
    tokenizer = ARIATokenizer.load()
    print(f"  Vocabulary: {len(tokenizer.vocab)} tokens")

    vocab_mask = torch.full((2304,), -1e9)
    for token_id in tokenizer.vocab.values():
        if 0 <= token_id < 2304:
            vocab_mask[token_id] = 0.0
    vocab_mask = vocab_mask.to(DEVICE)

    print("Loading corpus...")
    corpus_text = load_corpus()
    print(f"  Corpus loaded.")
    print()

    # Build dataset ONCE — reused every round, not rebuilt each time.
    # Old design rebuilt the dataset per round = 30+ GB RAM spike each round.
    print("Building dataset (one time only — shared across all rounds)...")
    shared_dataset = WordTokenizedDataset(corpus_text, tokenizer, seq_length=64)
    # Free the raw corpus text — dataset holds the compact numpy form.
    del corpus_text
    shared_total_batches = (len(shared_dataset) + BATCH_SIZE_TRAINING - 1) // BATCH_SIZE_TRAINING
    print()

    # Find starting checkpoint
    prev_ckpt = None
    for candidate in [
        CKPT_DIR / f"round{START_ROUND - 1}_best.pt",
        CKPT_DIR / "round60_best.pt",
        CKPT_DIR / "round30_best.pt",
        CKPT_DIR / "round27_best.pt",
        CKPT_DIR / "best_word_level.pt",
    ]:
        if candidate.exists():
            prev_ckpt = candidate
            break

    if prev_ckpt is None:
        print("ERROR: No starting checkpoint found.")
        sys.exit(1)

    print(f"Starting from: {prev_ckpt.name}")

    # Track overall progress
    round_log = []
    session_start = time.time()

    for round_num in range(START_ROUND, MAX_ROUND + 1):
        loss, ckpt_path = run_round(
            round_num, prev_ckpt, tokenizer, vocab_mask,
            shared_dataset, shared_total_batches
        )
        round_log.append((round_num, loss))
        prev_ckpt = ckpt_path

        print()
        print(f"  Round {round_num} complete — loss={loss:.6f}")

        if loss <= TARGET_LOSS:
            print()
            print("╔══════════════════════════════════════════════╗")
            print("║   TARGET REACHED                            ║")
            print(f"║   Loss: {loss:.6f} — below {TARGET_LOSS}              ║")
            print("║   Coherent sentences should be forming.     ║")
            print("║   Update aria_idle_daemon.py checkpoint.    ║")
            print("╚══════════════════════════════════════════════╝")
            break
        else:
            print(f"  Still above {TARGET_LOSS} — continuing to round {round_num + 1}...")

    # Final summary
    total_elapsed = (time.time() - session_start) / 60
    print()
    print("=" * 60)
    print("AUTO TRAINER COMPLETE")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {total_elapsed:.1f} min")
    print()
    print("Round log:")
    for rn, rl in round_log:
        marker = " <- TARGET" if rl <= TARGET_LOSS else ""
        print(f"  Round {rn:2d}:  loss={rl:.6f}{marker}")
    print()

    final_loss = round_log[-1][1] if round_log else 0.0
    final_ckpt = CKPT_DIR / f"round{round_log[-1][0]}_best.pt" if round_log else None

    if final_loss <= TARGET_LOSS:
        print(f"NEXT: Update aria_idle_daemon.py — change checkpoint to {final_ckpt.name}")
        print(f"NEXT: Restart aria_core_api.py — she will use new weights automatically")
        print(f"      (aria_core_think.py fallback chain picks up roundXX_best.pt)")
    else:
        print(f"Loss still above {TARGET_LOSS} — run again or add more training data.")

    print()
    print("NO RETREAT. NO SURRENDER. 💙🐗")
