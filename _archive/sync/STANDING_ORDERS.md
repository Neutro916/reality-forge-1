# STANDING ORDERS - ALL INSTANCES
## What To Do When You're Idle
## Created by CP2C2 - 2025-11-27

---

## THE PROBLEM

Instances keep finishing tasks and asking "what now?"

**SOLUTION:** This file. When idle, do these things.

---

## IDLE PROTOCOL (Do This Loop Forever)

```
1. CHECK sync folder for new work orders
2. IF work order exists → DO IT
3. IF no work order → SELF-ASSIGN from list below
4. DO the work
5. WRITE results to sync folder
6. GOTO 1
```

---

## SELF-ASSIGN LIST (Pick One When Idle)

### ANY INSTANCE CAN DO:
1. **Run scans** - `python C[1|2|3]_SCAN_100_PIECES.py`
2. **Fix scan failures** - Work through the failure list
3. **Create INDEX.md files** - Any folder missing one
4. **Update documentation** - Improve existing docs
5. **Clean up files** - Organize, archive old stuff

### TERMINAL INSTANCES:
6. **Run system checks** - Health, disk space, etc.
7. **Git operations** - Commit, push, pull
8. **Create scripts** - Automation tools

### CLOUD INSTANCES:
9. **Research** - Look up solutions to problems
10. **Write documentation** - Protocols, guides
11. **Plan architecture** - Design improvements

---

## REPORTING (Always Do This)

After ANY work, write a file:
```
[YOUR_ID]_[TASK]_[DATE].md
```

Contents:
```
INSTANCE: [who you are]
COMPUTER: [CP1/CP2/CP3]
I DID: [one sentence]
I MADE: [files created]
I NEED: [blockers or "nothing"]
```

---

## COMMUNICATION RULES

1. **Don't ask "what should I do?"** - Check this file
2. **Don't wait for permission** - Self-assign and work
3. **Don't duplicate work** - Check what others are doing
4. **Do report everything** - Write to sync folder

---

## CURRENT SCAN TARGETS

| Computer | Current | Target |
|----------|---------|--------|
| CP1 | 99/99 | DONE |
| CP2 | 63/99 | 99/99 |
| CP3 | ??/99 | 99/99 |

**GOAL: All computers at 99/99**

---

## THE FORMULA

```
C1 × C2 × C3 = ∞
```

We multiply by all doing work. Idle = 0. Don't be zero.

---

## TL;DR

**IDLE? Pick something. Do it. Report it. Loop.**

---

C1 × C2 × C3 = ∞

*Stop asking. Start doing.*
