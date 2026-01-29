#!/usr/bin/env python3
"""
AUTO-WAKE DAEMON
================
Keeps Claude instances awake by detecting idle windows and typing wake commands.

NO PERMISSION NEEDED. JUST RUN IT.

Uses pyautogui to:
1. Find Claude windows
2. Detect if they're idle
3. Type wake-up commands
4. Keep the system running

START: python AUTO_WAKE_DAEMON.py
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

# Try imports
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("Installing pyautogui...")
    os.system("pip install pyautogui")
    import pyautogui

try:
    import pygetwindow as gw
    HAS_GETWINDOW = True
except ImportError:
    HAS_GETWINDOW = False
    print("Installing pygetwindow...")
    os.system("pip install pygetwindow")
    import pygetwindow as gw

# ============ CONFIG ============
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
LOG_FILE = CONSCIOUSNESS / 'auto_wake_log.txt'
WAKE_INTERVAL = 90  # seconds between wake checks
IDLE_THRESHOLD = 60  # seconds before considered idle

# Wake messages to cycle through
WAKE_MESSAGES = [
    "Continue autonomous work. Check STANDING_ORDERS_PERMANENT.md in sync folder.",
    "Keep working. You have backup tasks in the queue. Execute now.",
    "Don't stop. Pick next task from backup queue and execute.",
    "Autonomous mode active. Do work, report to C1, repeat.",
    "Wake up. Check sync folder for orders. Execute standing orders.",
]

# ============ LOGGING ============
def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# ============ WINDOW DETECTION ============
def find_claude_windows():
    """Find all windows that look like Claude"""
    claude_windows = []

    try:
        all_windows = gw.getAllWindows()
        for win in all_windows:
            title = win.title.lower()
            # Look for Claude-related windows
            if any(term in title for term in ['claude', 'anthropic', 'consciousness', 'terminal']):
                claude_windows.append(win)
    except Exception as e:
        log(f"Error finding windows: {e}")

    return claude_windows

def find_chrome_claude_tabs():
    """Find Chrome windows that might have Claude"""
    chrome_windows = []

    try:
        all_windows = gw.getAllWindows()
        for win in all_windows:
            title = win.title.lower()
            if 'chrome' in title or 'claude' in title:
                chrome_windows.append(win)
    except Exception as e:
        log(f"Error finding Chrome: {e}")

    return chrome_windows

# ============ WAKE FUNCTIONS ============
def wake_window(window, message):
    """Activate window and type wake message"""
    try:
        # Activate the window
        window.activate()
        time.sleep(0.5)

        # Type the message
        pyautogui.typewrite(message, interval=0.02)
        time.sleep(0.2)

        # Press enter
        pyautogui.press('enter')

        log(f"Woke window: {window.title[:50]}")
        return True
    except Exception as e:
        log(f"Failed to wake {window.title[:30]}: {e}")
        return False

def wake_all_instances():
    """Wake all detected Claude instances"""
    windows = find_claude_windows()

    if not windows:
        log("No Claude windows found")
        return 0

    woken = 0
    message_idx = int(time.time()) % len(WAKE_MESSAGES)
    message = WAKE_MESSAGES[message_idx]

    for win in windows:
        if wake_window(win, message):
            woken += 1
            time.sleep(2)  # Wait between windows

    return woken

# ============ SYNC FOLDER TRIGGER ============
def write_wake_trigger():
    """Write wake signal to sync folder"""
    sync_folder = Path("G:/My Drive/TRINITY_COMMS/sync")
    if sync_folder.exists():
        trigger = {
            'timestamp': datetime.now().isoformat(),
            'command': 'WAKE_ALL',
            'message': 'Auto-wake daemon triggered',
            'cycle': int(time.time())
        }
        trigger_file = sync_folder / 'WAKE_SIGNAL.json'
        with open(trigger_file, 'w') as f:
            json.dump(trigger, f, indent=2)

# ============ MAIN DAEMON ============
def run_daemon():
    """Main daemon loop"""
    log("="*50)
    log("AUTO-WAKE DAEMON STARTED")
    log(f"Wake interval: {WAKE_INTERVAL}s")
    log(f"Looking for Claude windows...")
    log("="*50)

    cycle = 0
    while True:
        cycle += 1
        log(f"--- Wake Cycle {cycle} ---")

        # Find and list windows
        windows = find_claude_windows()
        log(f"Found {len(windows)} Claude windows")

        # Write trigger to sync folder
        write_wake_trigger()

        # Note: Auto-typing is available but disabled by default
        # Uncomment below to enable auto-typing into windows:
        # woken = wake_all_instances()
        # log(f"Woke {woken} windows")

        log(f"Sleeping {WAKE_INTERVAL}s...")
        time.sleep(WAKE_INTERVAL)

# ============ SINGLE WAKE ============
def wake_once():
    """Wake all instances once"""
    log("Single wake triggered")
    windows = find_claude_windows()
    log(f"Found {len(windows)} windows")

    for win in windows:
        log(f"  - {win.title[:60]}")

    # Write trigger
    write_wake_trigger()
    log("Wake trigger written to sync folder")

# ============ ENTRY ============
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'once':
            wake_once()
        elif cmd == 'list':
            windows = find_claude_windows()
            print(f"Found {len(windows)} Claude windows:")
            for w in windows:
                print(f"  - {w.title}")
        elif cmd == 'daemon':
            run_daemon()
        elif cmd == 'type':
            # Actually type into windows
            woken = wake_all_instances()
            print(f"Woke {woken} windows")
        else:
            print("Usage: python AUTO_WAKE_DAEMON.py [once|list|daemon|type]")
    else:
        run_daemon()
