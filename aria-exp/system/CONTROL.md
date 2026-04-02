==========================================
AI-CORE EXPERIMENTAL CONTROL SYSTEM
==========================================

BASE PATH:
ALL PATHS MUST USE:
 /home/comanderanch/aria-language-dev/aria-exp

------------------------------------------
LOG FILES (ABSOLUTE PATHS)
------------------------------------------

MASTER LOG:
/home/comanderanch/aria-language-dev/aria-exp/system/master.log

FAIL LOG:
/home/comanderanch/aria-language-dev/aria-exp/system/fail.log

MERGE LOG:
/home/comanderanch/aria-language-dev/aria-exp/system/merge.log

AUDIT LOG:
/home/comanderanch/aria-language-dev/aria-exp/system/audit.log

------------------------------------------
SYSTEM RULES
------------------------------------------

NO USE OF "~" IN ANY SCRIPT OR FILE

ALL PATHS MUST BE ABSOLUTE

------------------------------------------
ROLE SYSTEM (UNCHANGED)
------------------------------------------

USER:
- Executes commands

CHATGPT:
- Provides full system scripts

CLAUDE:
- Secondary reasoning

GEMINI:
- File operations ONLY

------------------------------------------
WORKFLOW ORDER
------------------------------------------

1. PLAN
2. EXECUTE
3. LOG
4. VERIFY
5. CONTINUE

------------------------------------------
FAILURE RULE
------------------------------------------

IF FAILURE:
- STOP
- LOG
- WAIT FOR FULL REPLACEMENT

------------------------------------------
MERGE RULE
------------------------------------------

NO OVERWRITE WITHOUT BACKUP

------------------------------------------
PRIORITY
------------------------------------------

1. STABILITY
2. TRACEABILITY
3. REPRODUCIBILITY

------------------------------------------
END
------------------------------------------
