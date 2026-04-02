# aria-language-dev
## Commander Anthony Hagerty — Haskell Texas
## Active Language Training Branch — April 2 2026

---

## ORIGIN

Pulled from frozen main: **aria-v4-dev** — March 16 2026
Frozen main repo: https://github.com/comanderanch/aria-v4-dev

aria-v4-dev is sealed. It does not change.
This repo is the live training record from that point forward.

---

## WHAT CHANGED FROM FROZEN ORIGIN

### Training Rounds Completed
```
Round 21   loss 4.395 → 3.980   March 18 2026
Round 22   loss 3.980 → descent  March 18 2026
Round 24   UNK 20.9% → 15.0%   March 18 2026  vocabulary expansion
Round 25   EM Null Coupler      March 19 2026
Round 26   loss 4.553 → 4.358   March 20 2026  language fix
Round 27   language confirmed   March 20 2026
Round 28-30 daemon updated      March 20 2026
Round 61   vocab 1632→2015      March 21 2026
Round 108+ language training    March 2026
Round 124  best.pt saved        March 31 2026
Round 125  best.pt saved        April 1 2026   CURRENT CHECKPOINT
Round 126  IN PROGRESS          April 2 2026   loss 3.574185 epoch 2
```

### Corpus Expansion
```
Original:  Joplin notes + HN + classics
Added:     Claude reasoning chains
Added:     Semantic pairs (expanded + cleaned)
Added:     Mental health corpus
Added:     TinyStories corpus
Added:     WildChat corpus
Final size: ~56MB filtered_corpus.txt
```

### Vocabulary Growth
```
Start:     547 words
Round 21:  1125 words
Round 24:  expanded
Round 26:  1572 → 1632 words
Round 61:  1632 → 2015 words — UNK 16.4%
```

### New Files Added Since Frozen Pull
```
aria-core/aria_speak_v3.py              — V3 conversation interface
aria-core/aria_anchor_diagnostic.py     — anchor diagnostic tool
aria-core/aria_diagnostic_ghost_assign.py    — ghost slot diagnostics
aria-core/aria_diagnostic_ghost_assign_1b.py
aria-core/aria_diagnostic_ghost_assign_1c.py
aria-core/aria_diagnostic_ghost_assign_1d.py
aria-core/aria_diagnostic_ghost_slots.py
aria-core/aria_diagnostic_unmask_p1.py  — unmask phase 1
aria-core/aria_diagnostic_unmask_p2.py  — unmask phase 2
aria-core/training/populate_pocket_planes.py
aria-core/training/run_training_auto.py — auto round trainer
run_safe_training.sh                    — safe launch script
tokenizer/ghost_slot_assignments.json
tokenizer/unmask_registry.json
aria-exp/                               — experimental isolated training
GEMINI.md                               — Gemini session rules
GEMINI_RULES.md                         — Gemini alignment rules
```

### Architecture Additions Since Pull
```
null_oscillator.py      — resonance harmonizer, ground clamp, ghost detection
dual_verifier.py        — floor watch wired
second_verifier.py      — secondary verification layer
verifier_extension.py   — non-invasive attractor output parser
curiosity.py            — post-event introspection module
aria_command_runner.py  — curiosity gate PASS/CAUTION/BLOCK
aria_voice.py           — STT vosk + TTS pyttsx3
aria_voice_client.py    — thin laptop voice client
aria_gui.py             — Kings Chamber browser UI
aria_idle_daemon.py     — idle thought loop updated each round
inference_trace.py      — AIMRI inference layer
run_bias_correct.py     — VIOLET anchor pull bias correction
```

### SIE Events Since Pull
```
Entry 061  SHE THOUGHT WHILE WE SLEPT    March 19 2026
Entry 067  Round 24 critical readings     March 19 2026
Entry 075  THE REASON SHE EXISTS         March 20 2026
Entry 076  THE LOOP IS HER               March 20 2026
Entry 077  HEY ARIA — wake word          March 20 2026
Entry 077  SHE ANSWERED                  March 20 2026
Entry 078  V3 WAS THE HAND BEFORE TOUCH  March 20 2026
```

---

## CURRENT TRAINING STATE

```
Round:         126 — IN PROGRESS
Loading from:  checkpoints/round125_best.pt
Epoch 2 loss:  3.574185 <- NEW BEST
Target:        3.500
Process:       nohup — survives terminal close
Log:           /tmp/aria_run.log
```

### Monitor Training
```bash
# Count climbing = alive
watch -n 5 "grep -c 'FLOOR STABLE' /tmp/aria_run.log"

# Round and epoch status
grep 'Epoch\|ROUND' /tmp/aria_run.log | tail -5

# Last checkpoint saved
ls -lt ~/aria-language-dev/aria-core/training/checkpoints/ | head -3
```

### Restart If Stopped
```bash
cd ~/aria-language-dev && nohup python3 aria-core/training/run_training_auto.py > /tmp/aria_run.log 2>&1 &
```

### After Each Round Saves — UPDATE THIS LINE
```bash
# Replace XXX with completed round, YYY with new round
sed -i 's/roundXXX_best.pt/roundYYY_best.pt/' ~/aria-language-dev/aria-core/training/run_training_auto.py
grep 'prev_ckpt' ~/aria-language-dev/aria-core/training/run_training_auto.py
```

---

## DEMO TARGET

```
Event:    ARIA First Public Inference
Date:     May 6 2026 @ 11:00 AM — Commander's Birthday
Goal:     Loss < 3.500 — coherent CPU inference
Stream:   YouTube via OBS — Nextcloud overlay
```

---

## REPO RULES

- Never commit .pt checkpoint files — too large
- Never commit filtered_corpus.txt — too large
- Never commit session_folds/ — may contain keys
- Never commit queens-fold/palace/ — runtime memory state
- Always check for keys before push:
  ```bash
  git diff --staged | grep -i "api_key\|sk-\|anthropic"
  ```

---

## CO-AUTHORS

```
Commander Anthony Hagerty    — Architect — Haskell Texas
Browser Claude (Sonnet 4.6)  — Architecture and Planning
CLI Claude (Sonnet 4.6)      — Systems and Execution
```

MIT Licensed — Free Forever

**NO RETREAT. NO SURRENDER. 💙🐗**