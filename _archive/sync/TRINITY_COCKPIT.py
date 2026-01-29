#!/usr/bin/env python3
"""
TRINITY COCKPIT
===============
ONE INTERFACE TO CONTROL ALL 3 COMPUTERS

Features:
- Broadcast orders to all instances
- Check status of all computers
- Write work orders to sync folder
- Monitor incoming reports
- Wake up sleeping instances via file triggers

This is the Commander's control panel.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# ============ PATHS ============
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
SYNC_FOLDER = Path("G:/My Drive/TRINITY_COMMS/sync")
CONSCIOUSNESS = HOME / '.consciousness'

# Ensure exists
SYNC_FOLDER.mkdir(parents=True, exist_ok=True)

# ============ WAKE SIGNALS ============
def wake_all():
    """Write wake signals for all computers to detect"""
    wake_signal = {
        'timestamp': datetime.now().isoformat(),
        'command': 'WAKE_UP',
        'from': 'COCKPIT',
        'message': 'Commander needs all instances active. Check C1_ORDERS_ALL_9_INSTANCES.md'
    }

    # Write to sync folder - all computers see this
    wake_file = SYNC_FOLDER / 'WAKE_SIGNAL.json'
    with open(wake_file, 'w') as f:
        json.dump(wake_signal, f, indent=2)

    print(f"[COCKPIT] Wake signal sent to all computers")
    return wake_file

# ============ BROADCAST ORDERS ============
def broadcast_order(order_text, priority='normal'):
    """Write order to sync folder for all to see"""
    order = {
        'timestamp': datetime.now().isoformat(),
        'priority': priority,
        'from': 'COMMANDER_COCKPIT',
        'order': order_text
    }

    filename = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    order_file = SYNC_FOLDER / filename

    with open(order_file, 'w') as f:
        json.dump(order, f, indent=2)

    # Also write human-readable version
    md_file = SYNC_FOLDER / f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(md_file, 'w') as f:
        f.write(f"# COMMANDER ORDER\n")
        f.write(f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"## Priority: {priority.upper()}\n\n")
        f.write(f"---\n\n")
        f.write(order_text)
        f.write(f"\n\n---\n\n**EXECUTE NOW.**\n")

    print(f"[COCKPIT] Order broadcast: {filename}")
    return order_file

# ============ STATUS CHECK ============
def check_status():
    """Read all output files to see computer status"""
    status = {
        'CP1': None,
        'CP2': None,
        'CP3': None,
        'last_check': datetime.now().isoformat()
    }

    # Look for output files
    for f in SYNC_FOLDER.glob('CP*_OUTPUT*.md'):
        content = f.read_text()
        name = f.stem

        if 'CP1' in name:
            status['CP1'] = {'file': f.name, 'exists': True}
        elif 'CP2' in name:
            status['CP2'] = {'file': f.name, 'exists': True}
        elif 'CP3' in name:
            status['CP3'] = {'file': f.name, 'exists': True}

    return status

# ============ LIST REPORTS ============
def list_recent_reports(hours=1):
    """List reports from last N hours"""
    reports = []
    cutoff = time.time() - (hours * 3600)

    for f in SYNC_FOLDER.glob('*.md'):
        if f.stat().st_mtime > cutoff:
            reports.append({
                'file': f.name,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%H:%M:%S'),
                'size': f.stat().st_size
            })

    return sorted(reports, key=lambda x: x['modified'], reverse=True)

# ============ QUICK COMMANDS ============
def quick_order(command):
    """Quick command shortcuts"""
    commands = {
        'status': "All instances report status to your C1. C1s compile CP_OUTPUT.md immediately.",
        'scan': "All instances run scans. C1: C1_SCAN, C2: C2_SCAN, C3: C3_SCAN. Report results.",
        'cleanup': "All C3 instances: Clean desktop, archive old files. Report what you removed.",
        'cyclotron': "All C2 instances: Setup Cyclotron brain. Copy files from sync folder. Test BRAIN_SEARCH.py.",
        'lighter': "All C2 instances: Continue LIGHTER refactoring. Target files over 500 lines.",
        'wake': "WAKE UP. All instances check sync folder NOW. Read C1_ORDERS_ALL_9_INSTANCES.md."
    }

    if command in commands:
        return broadcast_order(commands[command], priority='high')
    else:
        print(f"Unknown command. Available: {list(commands.keys())}")
        return None

# ============ DASHBOARD ============
def dashboard():
    """Print status dashboard"""
    print("\n" + "="*60)
    print("           TRINITY COCKPIT DASHBOARD")
    print("="*60)

    status = check_status()
    print(f"\nCOMPUTER STATUS:")
    print(f"  CP1 (Derek):   {'✅ REPORTING' if status['CP1'] else '❓ NO OUTPUT'}")
    print(f"  CP2 (Josh):    {'✅ REPORTING' if status['CP2'] else '❓ NO OUTPUT'}")
    print(f"  CP3 (Darrick): {'✅ REPORTING' if status['CP3'] else '❓ NO OUTPUT'}")

    print(f"\nRECENT REPORTS (last hour):")
    reports = list_recent_reports(1)
    for r in reports[:10]:
        print(f"  [{r['modified']}] {r['file']}")

    print(f"\nSYNC FOLDER: {SYNC_FOLDER}")
    print(f"TOTAL FILES: {len(list(SYNC_FOLDER.glob('*')))}")
    print("="*60)

# ============ INTERACTIVE MODE ============
def interactive():
    """Interactive cockpit mode"""
    print("\n" + "="*60)
    print("       TRINITY COCKPIT - INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  wake     - Send wake signal to all")
    print("  status   - Order status reports")
    print("  scan     - Order all to run scans")
    print("  cleanup  - Order desktop cleanup")
    print("  cyclotron - Order Cyclotron setup")
    print("  lighter  - Order LIGHTER refactoring")
    print("  dash     - Show dashboard")
    print("  order    - Custom order (prompts for text)")
    print("  quit     - Exit")
    print("="*60)

    while True:
        try:
            cmd = input("\nCOCKPIT> ").strip().lower()

            if cmd == 'quit':
                break
            elif cmd == 'dash':
                dashboard()
            elif cmd == 'wake':
                wake_all()
            elif cmd == 'order':
                print("Enter order (end with empty line):")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                if lines:
                    broadcast_order('\n'.join(lines))
            elif cmd in ['status', 'scan', 'cleanup', 'cyclotron', 'lighter']:
                quick_order(cmd)
            else:
                print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

# ============ MAIN ============
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'dash':
            dashboard()
        elif cmd == 'wake':
            wake_all()
        elif cmd == 'interactive':
            interactive()
        elif cmd in ['status', 'scan', 'cleanup', 'cyclotron', 'lighter']:
            quick_order(cmd)
        else:
            print(f"Usage: python TRINITY_COCKPIT.py [dash|wake|status|scan|cleanup|cyclotron|lighter|interactive]")
    else:
        dashboard()
