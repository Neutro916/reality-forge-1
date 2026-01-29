#!/usr/bin/env python3
"""
REMOTE COMMAND DAEMON
=====================
Watches for command files in Google Drive sync folder.
Enables remote control from phone/laptop while camping.

COMMANDS (create file in sync folder):
- WAKE_CP1.cmd    → Wakes Claude windows on CP1
- WAKE_CP2.cmd    → Wakes Claude windows on CP2
- WAKE_CP3.cmd    → Wakes Claude windows on CP3
- WAKE_ALL.cmd    → Wakes all computers
- STATUS.cmd      → All computers report status
- TASK_CP1.cmd    → Contains task text for CP1
- BROADCAST.cmd   → Message to all instances

The daemon deletes command files after processing.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Try to import screen control
try:
    import pyautogui
    import pygetwindow as gw
    SCREEN_CONTROL = True
except ImportError:
    SCREEN_CONTROL = False
    print("WARNING: pyautogui/pygetwindow not available - limited functionality")

# ============ CONFIG ============
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
SYNC_FOLDER = Path("G:/My Drive/TRINITY_COMMS/sync")
COMMANDS_FOLDER = SYNC_FOLDER / "commands"
COMPUTER_NAME = os.environ.get('COMPUTERNAME', 'UNKNOWN')

# Map computer names to CP identifiers
COMPUTER_MAP = {
    'DESKTOP-DEREK': 'CP1',
    'DESKTOP-H4KKQPI': 'CP1',  # Derek's actual computer name
    'DESKTOP-JOSH': 'CP2',
    'DESKTOP-MSMCFH2': 'CP2',  # Josh's actual computer name
    'DESKTOP-DARRICK': 'CP3',
    'DESKTOP-S72LRRO': 'CP3',  # Darrick's actual computer name
}

THIS_CP = COMPUTER_MAP.get(COMPUTER_NAME.upper(), 'CP1')

# ============ SCREEN CONTROL ============
def find_claude_windows():
    """Find all Claude Code terminal windows"""
    if not SCREEN_CONTROL:
        return []

    claude_windows = []
    try:
        all_windows = gw.getAllWindows()
        for win in all_windows:
            title = win.title.lower()
            if 'claude' in title or 'terminal' in title or 'powershell' in title or 'cmd' in title:
                claude_windows.append(win)
    except Exception as e:
        print(f"Error finding windows: {e}")

    return claude_windows

def wake_claude_window(window):
    """Activate a window and send a wake message"""
    if not SCREEN_CONTROL:
        return False

    try:
        # Bring window to front
        window.activate()
        time.sleep(0.5)

        # Type a wake message
        wake_msg = f"\n# REMOTE WAKE - {datetime.now().strftime('%H:%M:%S')}\n# Continue autonomous work\n"
        pyautogui.typewrite(wake_msg.replace('\n', ' '), interval=0.02)
        pyautogui.press('enter')

        return True
    except Exception as e:
        print(f"Error waking window: {e}")
        return False

def wake_all_claude_windows():
    """Wake all Claude windows on this computer"""
    windows = find_claude_windows()
    woken = 0

    for win in windows:
        if wake_claude_window(win):
            woken += 1
            time.sleep(1)  # Pause between windows

    return woken

# ============ COMMAND HANDLERS ============
def handle_wake(target):
    """Handle wake command"""
    if target == 'ALL' or target == THIS_CP:
        woken = wake_all_claude_windows()
        log_response(f"WAKE: {THIS_CP} woke {woken} windows")
        return True
    return False

def handle_status():
    """Report status to sync folder"""
    status = {
        "computer": THIS_CP,
        "name": COMPUTER_NAME,
        "timestamp": datetime.now().isoformat(),
        "claude_windows": len(find_claude_windows()),
        "screen_control": SCREEN_CONTROL,
        "daemon": "RUNNING"
    }

    status_file = SYNC_FOLDER / f"{THIS_CP}_REMOTE_STATUS.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)

    log_response(f"STATUS: {THIS_CP} reported")
    return True

def handle_task(task_text):
    """Send a task to Claude windows"""
    windows = find_claude_windows()
    if not windows:
        log_response(f"TASK: {THIS_CP} has no Claude windows")
        return False

    # Type task into first window
    try:
        windows[0].activate()
        time.sleep(0.5)
        pyautogui.typewrite(task_text[:500], interval=0.01)  # Limit length
        pyautogui.press('enter')
        log_response(f"TASK: {THIS_CP} received task")
        return True
    except Exception as e:
        log_response(f"TASK: {THIS_CP} error - {e}")
        return False

def handle_broadcast(message):
    """Broadcast message to all windows"""
    windows = find_claude_windows()
    for win in windows:
        try:
            win.activate()
            time.sleep(0.3)
            pyautogui.typewrite(f"BROADCAST: {message[:200]}", interval=0.01)
            pyautogui.press('enter')
            time.sleep(0.5)
        except:
            pass

    log_response(f"BROADCAST: {THIS_CP} sent to {len(windows)} windows")
    return True

def log_response(message):
    """Log response to sync folder"""
    log_file = SYNC_FOLDER / "REMOTE_COMMAND_LOG.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

    print(f"[{timestamp}] {message}")

# ============ COMMAND PROCESSOR ============
def process_commands():
    """Check for and process command files"""
    # Ensure commands folder exists
    COMMANDS_FOLDER.mkdir(exist_ok=True)

    # Look for command files
    cmd_files = list(COMMANDS_FOLDER.glob("*.cmd")) + list(SYNC_FOLDER.glob("*.cmd"))

    for cmd_file in cmd_files:
        try:
            name = cmd_file.stem.upper()
            content = cmd_file.read_text().strip() if cmd_file.stat().st_size > 0 else ""

            print(f"Processing command: {name}")

            # Parse command
            if name.startswith('WAKE_'):
                target = name.replace('WAKE_', '')
                handle_wake(target)

            elif name == 'STATUS':
                handle_status()

            elif name.startswith('TASK_'):
                target = name.replace('TASK_', '')
                if target == THIS_CP and content:
                    handle_task(content)

            elif name == 'BROADCAST':
                if content:
                    handle_broadcast(content)

            # Delete processed command
            cmd_file.unlink()
            print(f"Processed and deleted: {cmd_file.name}")

        except Exception as e:
            print(f"Error processing {cmd_file}: {e}")

# ============ MAIN DAEMON LOOP ============
def run_daemon(poll_interval=10):
    """Run the remote command daemon"""
    print("=" * 60)
    print("REMOTE COMMAND DAEMON STARTED")
    print(f"Computer: {COMPUTER_NAME} ({THIS_CP})")
    print(f"Screen Control: {'ENABLED' if SCREEN_CONTROL else 'DISABLED'}")
    print(f"Watching: {COMMANDS_FOLDER}")
    print(f"Poll Interval: {poll_interval}s")
    print("=" * 60)
    print()
    print("COMMANDS (create in sync/commands/):")
    print(f"  WAKE_{THIS_CP}.cmd  - Wake this computer's Claude windows")
    print("  WAKE_ALL.cmd     - Wake all computers")
    print("  STATUS.cmd       - Report status")
    print(f"  TASK_{THIS_CP}.cmd  - Send task (put text in file)")
    print("  BROADCAST.cmd    - Broadcast to all windows")
    print()
    print("Waiting for commands...")
    print()

    # Initial status report
    handle_status()

    while True:
        try:
            process_commands()
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\nDaemon stopped by user")
            break
        except Exception as e:
            print(f"Daemon error: {e}")
            time.sleep(poll_interval)

# ============ ENTRY POINT ============
if __name__ == '__main__':
    poll = 10  # seconds
    if len(sys.argv) > 1:
        try:
            poll = int(sys.argv[1])
        except:
            pass

    run_daemon(poll)
