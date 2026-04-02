==========================================
GEMINI INTEGRATION RULES — AI-CORE
==========================================

PURPOSE:
Gemini is used strictly for file handling and bulk operations.
It does NOT control training, logic, or system state.

------------------------------------------
ROLE SEPARATION
------------------------------------------

USER:
- Executes commands
- Makes final decisions

CHATGPT:
- Provides deterministic scripts
- Controls system architecture
- Defines execution flow

CLAUDE:
- Secondary reasoning / comparison (non-authoritative)

GEMINI:
- File operations ONLY
- No decision-making authority

------------------------------------------
ALLOWED OPERATIONS (GEMINI)
------------------------------------------

- Move files
- Copy datasets
- Rename files
- Validate file presence
- Organize directories

------------------------------------------
FORBIDDEN OPERATIONS (GEMINI)
------------------------------------------

- Modifying training scripts
- Writing or editing model code
- Changing checkpoints
- Interacting with GPU processes
- Altering running environments
- Auto-generating logic for AI-Core

------------------------------------------
DIRECTORY BOUNDARIES
------------------------------------------

ALLOWED:
~/projects/gemini/
~/aria-exp/data/

READ-ONLY:
~/aria-exp/model/
~/aria-exp/logs/

STRICT NO ACCESS:
~/aria-exp/model/checkpoints/

------------------------------------------
FAILURE RULE
------------------------------------------

If Gemini produces:
- unexpected output
- incorrect file movement
- logic suggestions

THEN:
- IGNORE output completely
- DO NOT attempt partial fixes
- RETURN control to ChatGPT

------------------------------------------
EXECUTION RULE
------------------------------------------

NO operation from Gemini is executed unless:
- explicitly approved by USER
- verified against this rule file

------------------------------------------
SYSTEM PRIORITY
------------------------------------------

1. Stability
2. Determinism
3. Reproducibility

NOT priority:
- speed via automation
- convenience over control

------------------------------------------
END OF FILE
------------------------------------------
