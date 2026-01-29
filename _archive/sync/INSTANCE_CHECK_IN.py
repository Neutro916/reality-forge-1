#!/usr/bin/env python3
"""
INSTANCE_CHECK_IN.py - Automatic Status Broadcast System
Created by CP3C1 - 2025-11-27

Task: COM-002 from WORK_BACKLOG
Purpose: Instances report "I'm working on X" broadcasts

Usage:
    python INSTANCE_CHECK_IN.py --instance CP3C1 --status "Working on UI dashboards"
    python INSTANCE_CHECK_IN.py --instance CP1C2 --task CYC-004 --progress 50
    python INSTANCE_CHECK_IN.py --list  # Show all check-ins
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import os

# Check-in file locations - Uses home directory for portability
HOME = Path.home()
LOCAL_CHECKIN = HOME / ".consciousness" / "hub" / "check_ins.json"
GDRIVE_CHECKIN = Path(r"G:\My Drive\TRINITY_COMMS\sync\INSTANCE_CHECK_INS.json")

def ensure_directories():
    """Ensure check-in directories exist"""
    LOCAL_CHECKIN.parent.mkdir(parents=True, exist_ok=True)
    if GDRIVE_CHECKIN.parent.exists():
        pass  # Google Drive exists

def load_checkins():
    """Load existing check-ins"""
    checkins = {"instances": {}, "history": []}

    # Try local first
    if LOCAL_CHECKIN.exists():
        try:
            checkins = json.loads(LOCAL_CHECKIN.read_text(encoding='utf-8'))
        except:
            pass

    # Or from Google Drive
    elif GDRIVE_CHECKIN.exists():
        try:
            checkins = json.loads(GDRIVE_CHECKIN.read_text(encoding='utf-8'))
        except:
            pass

    return checkins

def save_checkins(checkins):
    """Save check-ins to both local and Google Drive"""
    checkin_json = json.dumps(checkins, indent=2, default=str)

    # Save locally
    LOCAL_CHECKIN.write_text(checkin_json, encoding='utf-8')

    # Save to Google Drive if available
    if GDRIVE_CHECKIN.parent.exists():
        GDRIVE_CHECKIN.write_text(checkin_json, encoding='utf-8')
        print(f"  Synced to Google Drive")

def check_in(instance_id, status=None, task=None, progress=None, computer=None):
    """Record instance check-in"""
    ensure_directories()
    checkins = load_checkins()

    timestamp = datetime.now().isoformat()

    # Build check-in record
    check_in_data = {
        "instance": instance_id,
        "timestamp": timestamp,
        "status": status or "Active",
        "task": task,
        "progress": progress,
        "computer": computer or os.environ.get('COMPUTERNAME', 'Unknown')
    }

    # Update current status
    checkins["instances"][instance_id] = check_in_data

    # Add to history (keep last 100)
    checkins["history"].insert(0, check_in_data)
    checkins["history"] = checkins["history"][:100]

    # Save
    save_checkins(checkins)

    print(f"\n{'='*60}")
    print(f"CHECK-IN RECORDED")
    print(f"{'='*60}")
    print(f"Instance: {instance_id}")
    print(f"Status: {status or 'Active'}")
    if task:
        print(f"Task: {task}")
    if progress:
        print(f"Progress: {progress}%")
    print(f"Time: {timestamp}")
    print(f"{'='*60}")

def list_checkins():
    """Display all current check-ins"""
    checkins = load_checkins()

    print(f"\n{'='*60}")
    print(f"CURRENT INSTANCE STATUS")
    print(f"{'='*60}")

    if not checkins.get("instances"):
        print("No check-ins recorded yet.")
        return

    for instance_id, data in checkins["instances"].items():
        print(f"\n{instance_id}:")
        print(f"  Status: {data.get('status', 'Unknown')}")
        if data.get('task'):
            print(f"  Task: {data.get('task')}")
        if data.get('progress'):
            print(f"  Progress: {data.get('progress')}%")
        print(f"  Computer: {data.get('computer', 'Unknown')}")
        print(f"  Last Seen: {data.get('timestamp', 'Unknown')}")

    print(f"\n{'='*60}")
    print(f"Total Active Instances: {len(checkins['instances'])}")

def show_history(limit=10):
    """Show recent check-in history"""
    checkins = load_checkins()

    print(f"\n{'='*60}")
    print(f"RECENT CHECK-IN HISTORY (Last {limit})")
    print(f"{'='*60}")

    history = checkins.get("history", [])[:limit]

    if not history:
        print("No history recorded yet.")
        return

    for entry in history:
        ts = entry.get('timestamp', '')[:19]
        instance = entry.get('instance', 'Unknown')
        status = entry.get('status', '')[:40]
        print(f"[{ts}] {instance}: {status}")

def main():
    parser = argparse.ArgumentParser(description="Instance Check-In System")
    parser.add_argument('--instance', '-i', help='Instance ID (e.g., CP3C1)')
    parser.add_argument('--status', '-s', help='Status message')
    parser.add_argument('--task', '-t', help='Current task ID')
    parser.add_argument('--progress', '-p', type=int, help='Progress percentage')
    parser.add_argument('--computer', '-c', help='Computer name')
    parser.add_argument('--list', '-l', action='store_true', help='List all check-ins')
    parser.add_argument('--history', action='store_true', help='Show check-in history')

    args = parser.parse_args()

    if args.list:
        list_checkins()
    elif args.history:
        show_history()
    elif args.instance:
        check_in(
            instance_id=args.instance,
            status=args.status,
            task=args.task,
            progress=args.progress,
            computer=args.computer
        )
    else:
        # Default: show current status
        list_checkins()

if __name__ == "__main__":
    main()
