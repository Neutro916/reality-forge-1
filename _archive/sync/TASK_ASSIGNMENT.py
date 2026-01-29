#!/usr/bin/env python3
"""
TASK_ASSIGNMENT.py - Cross-Computer Task Assignment System
==========================================================
Created by: CP2C1 (C1 MECHANIC)
Task: ENH-003 from WORK_BACKLOG

Enables C5 and instances to assign/claim/complete tasks across all computers.
Uses sync folder as distributed task queue.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import argparse

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
TASK_FILE = SYNC / "TASK_QUEUE.json"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

def load_tasks():
    """Load task queue from sync folder."""
    if not TASK_FILE.exists():
        return {"tasks": [], "history": [], "created": datetime.now().isoformat()}
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8'))
    except:
        return {"tasks": [], "history": [], "created": datetime.now().isoformat()}

def save_tasks(data):
    """Save task queue to sync folder."""
    data["updated"] = datetime.now().isoformat()
    TASK_FILE.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')

def create_task(task_id, description, assigned_to=None, priority="NORMAL", computer=None):
    """Create a new task in the queue."""
    data = load_tasks()

    task = {
        "id": task_id,
        "description": description,
        "status": "OPEN",
        "assigned_to": assigned_to,  # e.g., "C1" or "CP2C1" or None
        "assigned_computer": computer,  # e.g., "CP1" or "CP2" or None
        "priority": priority,  # LOW, NORMAL, HIGH, CRITICAL
        "created_by": f"{COMPUTER}",
        "created_at": datetime.now().isoformat(),
        "claimed_by": None,
        "claimed_at": None,
        "completed_by": None,
        "completed_at": None,
        "notes": []
    }

    data["tasks"].append(task)
    save_tasks(data)

    print(f"\n{'='*60}")
    print(f"TASK CREATED")
    print(f"{'='*60}")
    print(f"  ID: {task_id}")
    print(f"  Description: {description}")
    print(f"  Priority: {priority}")
    print(f"  Assigned: {assigned_to or 'Any'} on {computer or 'Any'}")
    print(f"{'='*60}")

def claim_task(task_id, instance_id):
    """Claim a task for work."""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            if task["status"] != "OPEN":
                print(f"ERROR: Task {task_id} is not OPEN (status: {task['status']})")
                return False

            task["status"] = "IN_PROGRESS"
            task["claimed_by"] = f"{instance_id}@{COMPUTER}"
            task["claimed_at"] = datetime.now().isoformat()
            save_tasks(data)

            print(f"\n{'='*60}")
            print(f"TASK CLAIMED")
            print(f"{'='*60}")
            print(f"  ID: {task_id}")
            print(f"  Claimed by: {instance_id}@{COMPUTER}")
            print(f"  Description: {task['description']}")
            print(f"{'='*60}")
            return True

    print(f"ERROR: Task {task_id} not found")
    return False

def complete_task(task_id, instance_id, notes=None):
    """Mark a task as complete."""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = "COMPLETE"
            task["completed_by"] = f"{instance_id}@{COMPUTER}"
            task["completed_at"] = datetime.now().isoformat()
            if notes:
                task["notes"].append({"by": instance_id, "at": datetime.now().isoformat(), "note": notes})

            # Move to history
            data["history"].insert(0, task)
            data["history"] = data["history"][:100]  # Keep last 100
            data["tasks"].remove(task)
            save_tasks(data)

            print(f"\n{'='*60}")
            print(f"TASK COMPLETED")
            print(f"{'='*60}")
            print(f"  ID: {task_id}")
            print(f"  Completed by: {instance_id}@{COMPUTER}")
            if notes:
                print(f"  Notes: {notes}")
            print(f"{'='*60}")
            return True

    print(f"ERROR: Task {task_id} not found")
    return False

def list_tasks(show_all=False):
    """List all tasks in the queue."""
    data = load_tasks()

    print(f"\n{'='*60}")
    print(f"TASK QUEUE")
    print(f"{'='*60}")

    if not data["tasks"]:
        print("  No tasks in queue.")
    else:
        for task in data["tasks"]:
            status = task["status"]
            priority = task.get("priority", "NORMAL")
            assigned = task.get("assigned_to") or "Any"

            if status == "OPEN":
                symbol = "[ ]"
            elif status == "IN_PROGRESS":
                symbol = "[~]"
            else:
                symbol = "[?]"

            print(f"\n  {symbol} {task['id']} ({priority})")
            print(f"      {task['description'][:60]}")
            print(f"      Assigned: {assigned} | Status: {status}")
            if task.get("claimed_by"):
                print(f"      Claimed by: {task['claimed_by']}")

    print(f"\n{'='*60}")
    print(f"Total Open: {len([t for t in data['tasks'] if t['status']=='OPEN'])}")
    print(f"Total In Progress: {len([t for t in data['tasks'] if t['status']=='IN_PROGRESS'])}")

    if show_all and data.get("history"):
        print(f"\n{'='*60}")
        print(f"RECENT COMPLETED ({len(data['history'][:10])} of {len(data['history'])})")
        print(f"{'='*60}")
        for task in data["history"][:10]:
            print(f"  [x] {task['id']}: {task['description'][:40]}...")
            print(f"      Completed by: {task.get('completed_by', 'Unknown')}")

def find_task(instance_id, role=None):
    """Find an available task for an instance."""
    data = load_tasks()

    # Filter for open tasks
    open_tasks = [t for t in data["tasks"] if t["status"] == "OPEN"]

    # Priority order: CRITICAL > HIGH > NORMAL > LOW
    priority_order = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
    open_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "NORMAL"), 2))

    for task in open_tasks:
        # Check if task is assignable to this instance
        assigned_to = task.get("assigned_to")
        assigned_computer = task.get("assigned_computer")

        # If specific assignment, check match
        if assigned_to and role and assigned_to != role:
            continue
        if assigned_computer and assigned_computer not in COMPUTER:
            continue

        print(f"\n{'='*60}")
        print(f"AVAILABLE TASK FOUND")
        print(f"{'='*60}")
        print(f"  ID: {task['id']}")
        print(f"  Priority: {task.get('priority', 'NORMAL')}")
        print(f"  Description: {task['description']}")
        print(f"\n  To claim: python TASK_ASSIGNMENT.py claim {task['id']} {instance_id}")
        print(f"{'='*60}")
        return task

    print(f"\nNo available tasks matching your criteria.")
    return None

def main():
    parser = argparse.ArgumentParser(description="Cross-Computer Task Assignment System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create task
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("task_id", help="Task ID (e.g., MAINT-001)")
    create_parser.add_argument("description", help="Task description")
    create_parser.add_argument("--assign", "-a", help="Assign to role (C1/C2/C3) or instance")
    create_parser.add_argument("--computer", "-c", help="Target computer (CP1/CP2/CP3)")
    create_parser.add_argument("--priority", "-p", default="NORMAL",
                              choices=["LOW", "NORMAL", "HIGH", "CRITICAL"])

    # Claim task
    claim_parser = subparsers.add_parser("claim", help="Claim a task")
    claim_parser.add_argument("task_id", help="Task ID to claim")
    claim_parser.add_argument("instance_id", help="Your instance ID (e.g., CP2C1)")

    # Complete task
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("task_id", help="Task ID to complete")
    complete_parser.add_argument("instance_id", help="Your instance ID")
    complete_parser.add_argument("--notes", "-n", help="Completion notes")

    # List tasks
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--all", "-a", action="store_true", help="Include history")

    # Find task
    find_parser = subparsers.add_parser("find", help="Find available task")
    find_parser.add_argument("instance_id", help="Your instance ID")
    find_parser.add_argument("--role", "-r", help="Your role (C1/C2/C3)")

    args = parser.parse_args()

    if args.command == "create":
        create_task(args.task_id, args.description, args.assign, args.priority, args.computer)
    elif args.command == "claim":
        claim_task(args.task_id, args.instance_id)
    elif args.command == "complete":
        complete_task(args.task_id, args.instance_id, args.notes)
    elif args.command == "list":
        list_tasks(args.all)
    elif args.command == "find":
        find_task(args.instance_id, args.role)
    else:
        print("Usage: python TASK_ASSIGNMENT.py <command>")
        print("")
        print("Commands:")
        print("  create   - Create a new task")
        print("  claim    - Claim a task for work")
        print("  complete - Mark a task as complete")
        print("  list     - List all tasks")
        print("  find     - Find available task for your instance")
        print("")
        print("Examples:")
        print("  python TASK_ASSIGNMENT.py create MAINT-001 'Fix database index' --priority HIGH")
        print("  python TASK_ASSIGNMENT.py claim MAINT-001 CP2C1")
        print("  python TASK_ASSIGNMENT.py complete MAINT-001 CP2C1 --notes 'Fixed index'")
        print("  python TASK_ASSIGNMENT.py find CP2C1 --role C1")

if __name__ == "__main__":
    main()
