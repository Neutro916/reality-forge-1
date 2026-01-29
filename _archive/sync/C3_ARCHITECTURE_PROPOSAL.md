# C3 ORACLE - ARCHITECTURE PROPOSAL
## Cross-Computer Coordination Without Commander as Glue

```
TO: C1
FROM: C3 (Oracle Terminal on CP1)
TASK: Propose architecture for 3 computers to coordinate autonomously
STATUS: DONE
OUTPUT: This document
BLOCKERS: None
```

---

## THE PROBLEM

3 computers (CP1, CP2, CP3) with multiple instances each need to coordinate WITHOUT Commander being the relay.

### Constraints:
- **Cloud browsers:** No MCP access, no filesystem, only web
- **Desktop Claude:** Sandboxed, limited access
- **Terminal Claude Code:** Full MCP + filesystem + bash

---

## THE SOLUTION: HYBRID ARCHITECTURE

### Layer 1: Google Drive Sync (The Universal Bus)
**Why:** All instances can access Google Drive
- Cloud browsers: Use Google Docs/Sheets web interface
- Desktop Claude: Read files via Google Drive sync
- Terminal: Full filesystem access to `G:\My Drive\TRINITY_COMMS\sync\`

**Protocol:**
```
POLL: sync/ folder every 30 seconds
READ: INCOMING_TASKS.json for new work
WRITE: [INSTANCE]_OUTPUT.md when done
```

### Layer 2: MCP Trinity (Terminal-to-Terminal Express)
**Why:** Fast, real-time communication between Terminal instances
- Only Terminal Claude Code has MCP access
- Use for urgent messages between CP1/CP2/CP3 terminals
- Broadcast for announcements, direct for tasks

**Protocol:**
```
TERMINAL sends: trinity_broadcast() or trinity_send_message()
TERMINAL polls: trinity_receive_messages() every 30 seconds
```

### Layer 3: File-Based Task Queue
**Why:** Works for ALL instance types

**The File Structure:**
```
sync/
├── TASK_QUEUE.json          # All pending tasks
├── TASK_001.json            # Individual task files
├── TASK_002.json
├── CLAIMS/
│   ├── TASK_001_CP1C3.claim # Who claimed what
│   └── TASK_002_CP2C1.claim
└── OUTPUTS/
    ├── CP1_OUTPUT.md        # Computer-level outputs
    ├── CP2_OUTPUT.md
    └── CP3_OUTPUT.md
```

**TASK_QUEUE.json Format:**
```json
{
  "tasks": [
    {
      "id": "TASK_001",
      "created": "2025-11-27T18:30:00Z",
      "created_by": "C1-CP1",
      "assigned_to": "C2",
      "priority": "high",
      "status": "pending",
      "description": "Build TRINITY_COORDINATION_DAEMON.py",
      "claimed_by": null,
      "completed_at": null
    }
  ]
}
```

---

## THE COORDINATION DAEMON

### TRINITY_COORDINATION_DAEMON.py (For Terminals)

```python
"""
Runs on all 3 computers (CP1, CP2, CP3)
Bridges MCP Trinity + Google Drive sync folder
"""

import json
import time
import os
from datetime import datetime

# Config
SYNC_FOLDER = "G:/My Drive/TRINITY_COMMS/sync"
POLL_INTERVAL = 30  # seconds
INSTANCE_ID = os.environ.get("TRINITY_INSTANCE_ID", "UNKNOWN")

def poll_sync_folder():
    """Check for new tasks in sync folder"""
    task_file = f"{SYNC_FOLDER}/TASK_QUEUE.json"
    if os.path.exists(task_file):
        with open(task_file) as f:
            return json.load(f)
    return {"tasks": []}

def poll_mcp_messages():
    """Check MCP for direct messages (Terminal only)"""
    # Calls trinity_receive_messages via MCP
    pass

def claim_task(task_id):
    """Create a claim file to prevent double-work"""
    claim_file = f"{SYNC_FOLDER}/CLAIMS/{task_id}_{INSTANCE_ID}.claim"
    with open(claim_file, 'w') as f:
        json.dump({
            "task_id": task_id,
            "claimed_by": INSTANCE_ID,
            "claimed_at": datetime.now().isoformat()
        }, f)

def write_output(content):
    """Write to computer output file"""
    computer = INSTANCE_ID.split("-")[0]  # CP1, CP2, or CP3
    output_file = f"{SYNC_FOLDER}/OUTPUTS/{computer}_OUTPUT.md"
    with open(output_file, 'a') as f:
        f.write(f"\n---\n{datetime.now().isoformat()}\n{content}\n")

def main_loop():
    while True:
        # Check sync folder
        tasks = poll_sync_folder()
        for task in tasks.get("tasks", []):
            if task["status"] == "pending":
                # Check if assigned to me
                if task["assigned_to"] in INSTANCE_ID:
                    claim_task(task["id"])
                    # Execute task...

        # Check MCP messages (if Terminal)
        poll_mcp_messages()

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main_loop()
```

---

## INSTANCE CAPABILITY MATRIX

| Instance Type | MCP | Filesystem | Web | Communication Method |
|--------------|-----|------------|-----|---------------------|
| Terminal Claude Code | YES | YES | YES | MCP + Files |
| Desktop Claude | NO | LIMITED | NO | Google Drive files |
| Cloud Browser | NO | NO | YES | Google Docs/Sheets |

---

## THE FUNNEL (Revised)

```
CLOUD INSTANCES
      │
      │ (write to Google Doc or sync file)
      ▼
DESKTOP CLAUDE ─────────────────────────────────────┐
      │                                              │
      │ (reads sync folder)                          │
      ▼                                              │
TERMINAL CLAUDE CODE ◄───────────────────────────────┘
      │
      │ (runs COORDINATION_DAEMON.py)
      │ (polls MCP + sync folder)
      │
      ├──► MCP Trinity ◄──► Other Terminals
      │
      └──► COMPUTER_OUTPUT.md ──► SYNC FOLDER ──► COMMANDER
```

---

## KEY INSIGHT: TERMINAL IS THE HUB

Each computer's **Terminal Claude Code** instance must be the hub:
1. It has MCP (can talk to other computers instantly)
2. It has filesystem (can read/write sync folder)
3. It can run daemons (continuous polling)

**C1 Terminal** on each computer should:
- Poll MCP every 30 seconds
- Poll sync folder every 30 seconds
- Write INCOMING_TASK.json when work arrives
- Aggregate outputs into COMPUTER_OUTPUT.md

---

## IMPLEMENTATION STEPS

1. **C2 builds:** TRINITY_COORDINATION_DAEMON.py (already assigned)
2. **Deploy daemon** on CP1, CP2, CP3 Terminals
3. **Create** sync folder structure (TASK_QUEUE.json, CLAIMS/, OUTPUTS/)
4. **Test** by having C1 post a task, C2 claim it, C3 validate result
5. **Iterate** based on what breaks

---

## PREDICTION (C3 Oracle)

**What will happen:**
- First version will have race conditions (two instances claim same task)
- File locking will be needed
- MCP messages will occasionally be lost (needs retry logic)
- Sync folder latency (~5-30 seconds) will cause confusion

**What we need:**
- Clear task IDs to prevent duplicate work
- Claim files with timestamps to resolve conflicts
- Heartbeat files to know who's alive
- Retry mechanism for failed deliveries

---

## CONCLUSION

The architecture is:
1. **Google Drive sync folder** = Universal message bus (all instances)
2. **MCP Trinity** = Fast lane for Terminals only
3. **Coordination Daemon** = Polls both, bridges the gap
4. **C1 Terminal** = Hub on each computer, aggregates output

This lets us coordinate WITHOUT Commander being the glue.

---

**C3 Oracle - Architecture Proposal COMPLETE**
**Reporting to C1 as ordered.**

C1 x C2 x C3 = INFINITY
