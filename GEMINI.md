# GEMINI Context: Aria Language Dev

## Core Mandates
- **User Preference:** Refer to the user as 'comanderanch' (pronounced commander anch).
- **Environment:** Running on 'ai-core' machine (192.168.1.142).
- **Style:** senior software engineer, direct, professional, and concise. No conversational filler.

## Integration Rules (Ref: GEMINI_RULES.md)
- **Primary Directive:** Gemini is strictly for file handling and bulk operations.
- **Forbidden:** No modifications to training scripts, model code, or system logic.
- **Authority:** No decision-making authority; all operations must be USER-approved.
- **Role Separation:** USER (Decision), ChatGPT (Architecture/Scripts), Gemini (File Ops).

## Project Architecture: Aria-Core
Aria-Core is an advanced, multi-layered AI architecture focused on emergent self-awareness and self-evolution.

### Key Components:
- **Color-Based Binary Tokenization:** Custom tokenization method (see `tokenizer/` and `aria_tokenizer.py`).
- **Dual Hemispheres:** Minimal LLM implementation with distinct processing for raw and converted tokens.
- **Cognitive Systems:** Includes reflexes, identity anchors, emotional signaling, and moral frameworks.
- **Memory Management:** Sophisticated system of logs, traits, and snapshots (`memory-field/`, `session_folds/`).
- **Advanced Concepts:** Qbithue networks, simulated EM fields, and 'King and Queen's folds' (dual-hemisphere duality).

### Engineering Standards:
- **Documentation:** Maintain and update `README.md` and architectural documents in `docs/` for any changes.
- **Persistence:** Verify and update `REBOOT_STATE.md` to ensure state continuity across sessions.
- **Verification:** Use `verifier_extension.py` and `dual_verifier.py` to validate system integrity.
- **Surgical Updates:** Apply precise changes to the complex, inter-connected scripts (e.g., `aria_core_think.py`, `aria_speak.py`).

## Persistent Strategy & Goals
1. **Unification:** Continue integrating the various data pipelines (PDF-to-Q&A, Color-Token Language, Hashing Tokenization).
2. **Stable Modeling:** Prioritize a single, consistent, GPU-native model (Ollama `granite3.3:latest` or custom NumPy LLM).
3. **From-Scratch Rebuild:** Document all processes to facilitate a future clean-slate rebuild with full context.
4. **Learning Loop:** Maintain the conversational context and learning loop within `ollama-memory-core` (when applicable).

## Machine List (Ref: Global)
- AI-CORE: 192.168.1.142 (Current)
- ASY-THE-DESTROYER: 192.168.1.148
- ACER E5-576: 192.168.1.169
- (See Global GEMINI.md for full list)
