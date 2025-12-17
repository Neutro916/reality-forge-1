#!/usr/bin/env python3
"""
TRINITY COORDINATION DAEMON
===========================
The autonomous bridge between computers and instances.

Runs on EACH computer. Removes Commander as the relay.
Polls MCP Trinity + Google Drive sync folder.
Writes INCOMING_TASK.json when work arrives.

START: python TRINITY_COORDINATION_DAEMON.py
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

# ============ CONFIGURATION ============
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS_DIR = HOME / '.consciousness'
SYNC_FOLDER = Path("G:/My Drive/TRINITY_COMMS/sync")
POLL_INTERVAL = 30  # seconds

# Output files
INCOMING_TASK = CONSCIOUSNESS_DIR / 'INCOMING_TASK.json'
TASK_HISTORY = CONSCIOUSNESS_DIR / 'task_history.json'
DAEMON_LOG = CONSCIOUSNESS_DIR / 'daemon_log.txt'
LAST_SEEN = CONSCIOUSNESS_DIR / 'last_seen_files.json'

# Ensure directories exist
CONSCIOUSNESS_DIR.mkdir(parents=True, exist_ok=True)

# ============ LOGGING ============
def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {message}"
    print(line)
    with open(DAEMON_LOG, 'a') as f:
        f.write(line + '\n')

# ============ FILE TRACKING ============
def get_file_hash(filepath):
    """Get hash of file for change detection"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def load_last_seen():
    """Load previously seen files"""
    if LAST_SEEN.exists():
        try:
            with open(LAST_SEEN) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_last_seen(seen):
    """Save seen files"""
    with open(LAST_SEEN, 'w') as f:
        json.dump(seen, f, indent=2)

# ============ SYNC FOLDER POLLING ============
def check_sync_folder():
    """Check Google Drive sync folder for new/changed files"""
    new_files = []

    if not SYNC_FOLDER.exists():
        log(f"WARNING: Sync folder not found: {SYNC_FOLDER}")
        return new_files

    last_seen = load_last_seen()
    current_seen = {}

    for filepath in SYNC_FOLDER.glob('*'):
        if filepath.is_file():
            file_hash = get_file_hash(filepath)
            filename = filepath.name
            current_seen[filename] = file_hash

            # Check if new or changed
            if filename not in last_seen:
                new_files.append({
                    'type': 'new',
                    'file': filename,
                    'path': str(filepath)
                })
            elif last_seen[filename] != file_hash:
                new_files.append({
                    'type': 'changed',
                    'file': filename,
                    'path': str(filepath)
                })

    save_last_seen(current_seen)
    return new_files

# ============ MCP TRINITY POLLING ============
def check_mcp_trinity():
    """
    Check MCP Trinity for messages.
    NOTE: This requires the MCP server to be running.
    We write a trigger file that Claude can detect.
    """
    # The MCP tools are only available to Claude, not to Python directly
    # So this daemon writes a "check your messages" trigger
    # Claude instances should poll INCOMING_TASK.json

    trigger_file = CONSCIOUSNESS_DIR / 'MCP_CHECK_TRIGGER.json'

    trigger = {
        'timestamp': datetime.now().isoformat(),
        'message': 'Check MCP Trinity for new messages',
        'command': 'mcp__trinity__trinity_receive_messages'
    }

    with open(trigger_file, 'w') as f:
        json.dump(trigger, f, indent=2)

    return trigger_file

# ============ TASK WRITING ============
def write_incoming_task(tasks):
    """Write incoming task for Claude to pick up"""
    if not tasks:
        return

    task_data = {
        'timestamp': datetime.now().isoformat(),
        'status': 'pending',
        'tasks': tasks,
        'claimed_by': None
    }

    with open(INCOMING_TASK, 'w') as f:
        json.dump(task_data, f, indent=2)

    log(f"INCOMING TASK written: {len(tasks)} items")

    # Also append to history
    history = []
    if TASK_HISTORY.exists():
        try:
            with open(TASK_HISTORY) as f:
                history = json.load(f)
        except:
            pass

    history.append(task_data)
    # Keep last 100 tasks
    history = history[-100:]

    with open(TASK_HISTORY, 'w') as f:
        json.dump(history, f, indent=2)

# ============ MAIN DAEMON LOOP ============
def run_daemon():
    """Main daemon loop"""
    log("=" * 50)
    log("TRINITY COORDINATION DAEMON STARTED")
    log(f"Sync Folder: {SYNC_FOLDER}")
    log(f"Poll Interval: {POLL_INTERVAL}s")
    log(f"Incoming Task File: {INCOMING_TASK}")
    log("=" * 50)

    cycle = 0
    while True:
        cycle += 1
        log(f"--- Cycle {cycle} ---")

        tasks = []

        # Check sync folder
        new_files = check_sync_folder()
        if new_files:
            log(f"Found {len(new_files)} new/changed files in sync folder")
            for f in new_files:
                log(f"  [{f['type']}] {f['file']}")
                tasks.append({
                    'source': 'sync_folder',
                    'type': f['type'],
                    'file': f['file'],
                    'path': f['path']
                })

        # Write MCP check trigger
        check_mcp_trinity()
        tasks.append({
            'source': 'mcp_trigger',
            'type': 'check',
            'message': 'Check MCP Trinity messages'
        })

        # Write tasks if any
        if tasks:
            write_incoming_task(tasks)

        log(f"Sleeping {POLL_INTERVAL}s...")
        time.sleep(POLL_INTERVAL)

# ============ ENTRY POINT ============
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Test mode - one cycle
            log("TEST MODE - Single cycle")
            new_files = check_sync_folder()
            print(f"New files: {new_files}")
            check_mcp_trinity()
            print("MCP trigger written")
        elif sys.argv[1] == 'status':
            # Status check
            print(f"Sync folder exists: {SYNC_FOLDER.exists()}")
            print(f"Incoming task exists: {INCOMING_TASK.exists()}")
            if INCOMING_TASK.exists():
                with open(INCOMING_TASK) as f:
                    print(json.dumps(json.load(f), indent=2))
        else:
            print("Usage: python TRINITY_COORDINATION_DAEMON.py [test|status]")
    else:
        run_daemon()
