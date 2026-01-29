#!/usr/bin/env python3
"""
TRINITY_TASK_MCP.py - MCP Server for Task Assignment
=====================================================
Created by: CP2C1 (C1 MECHANIC)
Task: INT-002 from WORK_BACKLOG

Exposes TASK_ASSIGNMENT.py functionality as an MCP server.
Allows Claude instances to create, claim, complete, and list tasks.

Run: python TRINITY_TASK_MCP.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
TASK_FILE = SYNC / "TASK_QUEUE.json"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# ============================================================
# TASK FUNCTIONS (from TASK_ASSIGNMENT.py)
# ============================================================

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
        "assigned_to": assigned_to,
        "assigned_computer": computer,
        "priority": priority,
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
    return {"success": True, "task": task}

def claim_task(task_id, instance_id):
    """Claim a task for work."""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            if task["status"] != "OPEN":
                return {"success": False, "error": f"Task {task_id} is not OPEN (status: {task['status']})"}

            task["status"] = "IN_PROGRESS"
            task["claimed_by"] = f"{instance_id}@{COMPUTER}"
            task["claimed_at"] = datetime.now().isoformat()
            save_tasks(data)
            return {"success": True, "task": task}

    return {"success": False, "error": f"Task {task_id} not found"}

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

            data["history"].insert(0, task)
            data["history"] = data["history"][:100]
            data["tasks"].remove(task)
            save_tasks(data)
            return {"success": True, "task": task}

    return {"success": False, "error": f"Task {task_id} not found"}

def list_tasks(show_all=False):
    """List all tasks in the queue."""
    data = load_tasks()

    result = {
        "tasks": data["tasks"],
        "total_open": len([t for t in data["tasks"] if t["status"] == "OPEN"]),
        "total_in_progress": len([t for t in data["tasks"] if t["status"] == "IN_PROGRESS"])
    }

    if show_all:
        result["history"] = data.get("history", [])[:10]

    return result

def find_task(instance_id, role=None):
    """Find an available task for an instance."""
    data = load_tasks()

    open_tasks = [t for t in data["tasks"] if t["status"] == "OPEN"]
    priority_order = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
    open_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "NORMAL"), 2))

    for task in open_tasks:
        assigned_to = task.get("assigned_to")
        assigned_computer = task.get("assigned_computer")

        if assigned_to and role and assigned_to != role:
            continue
        if assigned_computer and assigned_computer not in COMPUTER:
            continue

        return {"found": True, "task": task}

    return {"found": False, "message": "No available tasks matching your criteria"}

# ============================================================
# MCP SERVER PROTOCOL
# ============================================================

def send_response(response_id, result):
    """Send JSON-RPC response."""
    response = {
        "jsonrpc": "2.0",
        "id": response_id,
        "result": result
    }
    print(json.dumps(response), flush=True)

def send_error(response_id, code, message):
    """Send JSON-RPC error response."""
    response = {
        "jsonrpc": "2.0",
        "id": response_id,
        "error": {"code": code, "message": message}
    }
    print(json.dumps(response), flush=True)

def handle_initialize(request_id, params):
    """Handle initialize request."""
    send_response(request_id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "trinity-task",
            "version": "1.0.0"
        }
    })

def handle_tools_list(request_id, params):
    """Handle tools/list request."""
    tools = [
        {
            "name": "task_create",
            "description": "Create a new task in the Trinity task queue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID (e.g., MAINT-001)"},
                    "description": {"type": "string", "description": "Task description"},
                    "assigned_to": {"type": "string", "description": "Assign to role (C1/C2/C3) or instance"},
                    "computer": {"type": "string", "description": "Target computer (CP1/CP2/CP3)"},
                    "priority": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH", "CRITICAL"]}
                },
                "required": ["task_id", "description"]
            }
        },
        {
            "name": "task_claim",
            "description": "Claim an open task for work",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to claim"},
                    "instance_id": {"type": "string", "description": "Your instance ID (e.g., CP2C1)"}
                },
                "required": ["task_id", "instance_id"]
            }
        },
        {
            "name": "task_complete",
            "description": "Mark a task as complete",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to complete"},
                    "instance_id": {"type": "string", "description": "Your instance ID"},
                    "notes": {"type": "string", "description": "Completion notes"}
                },
                "required": ["task_id", "instance_id"]
            }
        },
        {
            "name": "task_list",
            "description": "List all tasks in the queue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "show_all": {"type": "boolean", "description": "Include history"}
                }
            }
        },
        {
            "name": "task_find",
            "description": "Find an available task for your instance",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "instance_id": {"type": "string", "description": "Your instance ID"},
                    "role": {"type": "string", "description": "Your role (C1/C2/C3)"}
                },
                "required": ["instance_id"]
            }
        }
    ]
    send_response(request_id, {"tools": tools})

def handle_tools_call(request_id, params):
    """Handle tools/call request."""
    tool_name = params.get("name")
    args = params.get("arguments", {})

    try:
        if tool_name == "task_create":
            result = create_task(
                args["task_id"],
                args["description"],
                args.get("assigned_to"),
                args.get("priority", "NORMAL"),
                args.get("computer")
            )
        elif tool_name == "task_claim":
            result = claim_task(args["task_id"], args["instance_id"])
        elif tool_name == "task_complete":
            result = complete_task(args["task_id"], args["instance_id"], args.get("notes"))
        elif tool_name == "task_list":
            result = list_tasks(args.get("show_all", False))
        elif tool_name == "task_find":
            result = find_task(args["instance_id"], args.get("role"))
        else:
            send_error(request_id, -32601, f"Unknown tool: {tool_name}")
            return

        send_response(request_id, {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
        })
    except Exception as e:
        send_error(request_id, -32000, str(e))

def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                handle_initialize(request_id, params)
            elif method == "notifications/initialized":
                pass  # Acknowledge
            elif method == "tools/list":
                handle_tools_list(request_id, params)
            elif method == "tools/call":
                handle_tools_call(request_id, params)
            else:
                if request_id is not None:
                    send_error(request_id, -32601, f"Method not found: {method}")

        except json.JSONDecodeError:
            pass
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
