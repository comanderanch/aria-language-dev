#!/bin/bash

BASE="/home/comanderanch/aria-language-dev"
TRAIN_SCRIPT="$BASE/aria-core/training/run_training_auto.py"
CKPT_DIR="$BASE/aria-core/training/checkpoints"
LOG="$BASE/aria-core/training/safe_run.log"
LOCK_FILE="/tmp/aria_safe_train.lock"

# ─── SINGLE INSTANCE LOCK ───────────────────────────────────────────
# Prevents two training processes from running at the same time.
# This is what caused the double-load RAM/swap disaster.
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "ERROR: Training already running (lock held). Aborting duplicate launch."
    echo "To force a fresh start: rm $LOCK_FILE"
    exit 1
fi

echo "===== SAFE TRAIN START =====" | tee -a "$LOG"
date | tee -a "$LOG"

# ─── PRE-CHECK — VERIFY LAST CHECKPOINT ─────────────────────────────
LAST_CKPT=$(ls -t "$CKPT_DIR"/round*_best.pt 2>/dev/null | head -n 1)

if [ -z "$LAST_CKPT" ]; then
    echo "ERROR: No checkpoint found in $CKPT_DIR" | tee -a "$LOG"
    exit 1
fi

echo "Using checkpoint: $LAST_CKPT" | tee -a "$LOG"

# ─── HASH CHECK (DETECT CORRUPTION) ─────────────────────────────────
sha256sum "$LAST_CKPT" > /tmp/ckpt_hash_before.txt
echo "Checkpoint hash: $(cat /tmp/ckpt_hash_before.txt)" | tee -a "$LOG"

# ─── RUN TRAINING — LIVE OUTPUT ──────────────────────────────────────
# -u = unbuffered so you see each line as it prints.
# tee -a = output goes to your terminal AND the log simultaneously.
python3 -u "$TRAIN_SCRIPT" 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}

# ─── POST CHECK ──────────────────────────────────────────────────────
NEW_CKPT=$(ls -t "$CKPT_DIR"/round*_best.pt 2>/dev/null | head -n 1)

if [ -z "$NEW_CKPT" ]; then
    echo "ERROR: No new checkpoint created" | tee -a "$LOG"
    exit 1
fi

sha256sum "$NEW_CKPT" > /tmp/ckpt_hash_after.txt

# ─── FAILURE DETECTION ───────────────────────────────────────────────
# Check a snapshot of the log — NOT the live file — to avoid self-grep error.
LOG_SNAPSHOT=$(tail -200 "$LOG")

if echo "$LOG_SNAPSHOT" | grep -qi "nan detected\|loss.*nan\|nan.*loss"; then
    echo "FAIL: NaN detected in training — check weights" | tee -a "$LOG"
    exit 1
fi

if echo "$LOG_SNAPSHOT" | grep -qi "traceback\|runtimeerror\|cuda out of memory"; then
    echo "FAIL: Runtime error detected — check log" | tee -a "$LOG"
    exit 1
fi

echo "===== SAFE TRAIN COMPLETE =====" | tee -a "$LOG"
exit $EXIT_CODE
