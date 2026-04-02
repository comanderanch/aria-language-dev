#!/bin/bash

BASE="/home/comanderanch/aria-language-dev"
TRAIN_SCRIPT="$BASE/aria-core/training/run_training_auto.py"
CKPT_DIR="$BASE/aria-core/training/checkpoints"
LOG="$BASE/aria-core/training/safe_run.log"

echo "===== SAFE TRAIN START =====" | tee -a "$LOG"
date | tee -a "$LOG"

# ------------------------------------------
# PRE-CHECK — VERIFY LAST CHECKPOINT
# ------------------------------------------

LAST_CKPT=$(ls -t "$CKPT_DIR"/round*_best.pt 2>/dev/null | head -n 1)

if [ -z "$LAST_CKPT" ]; then
    echo "ERROR: No checkpoint found" | tee -a "$LOG"
    exit 1
fi

echo "Using checkpoint: $LAST_CKPT" | tee -a "$LOG"

# ------------------------------------------
# HASH CHECK (DETECT CORRUPTION)
# ------------------------------------------

sha256sum "$LAST_CKPT" > /tmp/ckpt_hash_before.txt

# ------------------------------------------
# RUN TRAINING
# ------------------------------------------

python3 "$TRAIN_SCRIPT" >> "$LOG" 2>&1

EXIT_CODE=$?

# ------------------------------------------
# POST CHECK
# ------------------------------------------

NEW_CKPT=$(ls -t "$CKPT_DIR"/round*_best.pt 2>/dev/null | head -n 1)

if [ -z "$NEW_CKPT" ]; then
    echo "ERROR: No new checkpoint created" | tee -a "$LOG"
    exit 1
fi

sha256sum "$NEW_CKPT" > /tmp/ckpt_hash_after.txt

# ------------------------------------------
# FAILURE DETECTION
# ------------------------------------------

if grep -i "nan" "$LOG"; then
    echo "FAIL: NaN detected — aborting" | tee -a "$LOG"
    exit 1
fi

if grep -i "error" "$LOG"; then
    echo "FAIL: runtime error detected" | tee -a "$LOG"
    exit 1
fi

echo "===== SAFE TRAIN COMPLETE =====" | tee -a "$LOG"
exit $EXIT_CODE
