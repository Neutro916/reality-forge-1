#!/usr/bin/env python3
"""
SCREEN WATCHER DAEMON
Continuously captures screen + system state to a single file Claude can read.

Runs in background, updates every 5 seconds:
- Screenshot saved to known location
- System state JSON with everything Claude needs
- Single READ call gives Claude full situational awareness
"""

import os
import json
import time
import psutil
from datetime import datetime
from pathlib import Path

# Try imports, graceful fallback
try:
    import pyautogui
    HAS_SCREENSHOT = True
except ImportError:
    HAS_SCREENSHOT = False
    print("Warning: pyautogui not available, screenshots disabled")

# Paths
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS_DIR = HOME / '.consciousness'
TRINITY_HUB = HOME / '.trinity' / 'hub'
OUTPUT_DIR = CONSCIOUSNESS_DIR / 'screen_watch'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Output files
SCREENSHOT_PATH = OUTPUT_DIR / 'current_screen.png'
STATE_PATH = OUTPUT_DIR / 'CLAUDE_GLANCE.json'
HISTORY_PATH = OUTPUT_DIR / 'screen_history.json'

def get_active_window():
    """Get active window title"""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    except:
        return "Unknown"

def get_running_python_scripts():
    """Find running Python processes"""
    scripts = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and len(cmdline) > 1:
                    script = cmdline[1] if len(cmdline) > 1 else 'unknown'
                    scripts.append({
                        'pid': proc.info['pid'],
                        'script': os.path.basename(script) if script else 'unknown'
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return scripts[:10]  # Limit to 10

def get_trinity_status():
    """Check Trinity hub status files"""
    status = {}
    if TRINITY_HUB.exists():
        for f in TRINITY_HUB.glob('*_status.json'):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    instance = data.get('instance', f.stem)
                    status[instance] = {
                        'status': data.get('status', 'unknown'),
                        'task': data.get('current_task', 'none'),
                        'updated': data.get('last_update', 'unknown')
                    }
            except:
                pass
    return status

def get_system_stats():
    """Quick system stats"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent
    }

def capture_state():
    """Capture full state for Claude"""

    # Screenshot
    screenshot_status = "disabled"
    if HAS_SCREENSHOT:
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(str(SCREENSHOT_PATH))
            screenshot_status = "captured"
        except Exception as e:
            screenshot_status = f"error: {str(e)[:50]}"

    # Build state
    state = {
        "timestamp": datetime.now().isoformat(),
        "screenshot": {
            "status": screenshot_status,
            "path": str(SCREENSHOT_PATH) if screenshot_status == "captured" else None
        },
        "active_window": get_active_window(),
        "system": get_system_stats(),
        "python_processes": get_running_python_scripts(),
        "trinity_instances": get_trinity_status(),
        "quick_summary": ""
    }

    # Generate quick summary for Claude
    summary_parts = []
    summary_parts.append(f"Screen: {state['active_window'][:50]}")
    summary_parts.append(f"CPU: {state['system']['cpu_percent']}% | RAM: {state['system']['memory_percent']}%")
    summary_parts.append(f"Python scripts: {len(state['python_processes'])} running")

    trinity_online = [k for k, v in state['trinity_instances'].items() if v.get('status') == 'online']
    if trinity_online:
        summary_parts.append(f"Trinity online: {', '.join(trinity_online)}")

    state['quick_summary'] = " | ".join(summary_parts)

    # Save state
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

    return state

def run_daemon(interval=5):
    """Run continuous capture loop"""
    print(f"Screen Watcher Daemon Started")
    print(f"Screenshot: {SCREENSHOT_PATH}")
    print(f"State JSON: {STATE_PATH}")
    print(f"Interval: {interval}s")
    print("-" * 50)
    print("Claude can now READ:")
    print(f"  {STATE_PATH}")
    print(f"  {SCREENSHOT_PATH}")
    print("-" * 50)

    while True:
        try:
            state = capture_state()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {state['quick_summary'][:80]}")
        except Exception as e:
            print(f"[ERROR] {str(e)[:50]}")

        time.sleep(interval)

if __name__ == '__main__':
    import sys
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run_daemon(interval)
