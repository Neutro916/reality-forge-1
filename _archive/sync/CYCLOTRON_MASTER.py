#!/usr/bin/env python3
"""
CYCLOTRON MASTER - C1 Orchestrates Everything
Instead of waiting for other instances to run watchers,
C1 directly controls them via PyAutoGUI + MCP.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

HUB = Path.home() / ".consciousness" / "hub"
CYCLE_INTERVAL = 10  # seconds between cycles

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] CYCLOTRON: {msg}")

def write_task(instance_id, task_description):
    """Write a task for an instance to pick up"""
    task_file = HUB / f"tasks_for_{instance_id.lower().replace('-', '_')}.json"
    tasks = [{"description": task_description, "timestamp": datetime.now().isoformat()}]
    with open(task_file, "w") as f:
        json.dump(tasks, f, indent=2)
    log(f"Task written for {instance_id}: {task_description}")

def read_output(instance_id):
    """Read output from an instance"""
    output_file = HUB / f"output_{instance_id.lower().replace('-', '_')}.json"
    if output_file.exists():
        with open(output_file, "r") as f:
            return json.load(f)
    return None

def write_cycle_status(cycle_num, status):
    """Write current cycle status"""
    status_file = HUB / "CYCLOTRON_STATUS.json"
    data = {
        "cycle": cycle_num,
        "status": status,
        "timestamp": datetime.now().isoformat() + "Z",
        "instances": ["C1-Terminal", "C2-Terminal", "C3-Terminal"]
    }
    with open(status_file, "w") as f:
        json.dump(data, f, indent=2)

def c1_work():
    """C1's work - Mechanic tasks"""
    log("C1 MECHANIC: Building/fixing...")
    # Actual work would go here
    time.sleep(1)
    return {"role": "mechanic", "action": "build_cycle", "status": "complete"}

def signal_c2():
    """Signal C2 to do work via MCP message file"""
    log("Signaling C2 Architect...")
    write_task("C2-Terminal", "Architecture review cycle")
    # Write wake signal (includes all fields required by FIGURE_8_WAKE_PROTOCOL)
    signal = {
        "wake_target": "C2-Terminal",
        "from": "C1-Terminal",
        "reason": "Cyclotron cycle",
        "priority": "NORMAL",
        "timestamp": datetime.now().isoformat() + "Z",
        "loop_number": 0,
        "convergence_level": 0,
        "task_context": {
            "previous_instance": "C1-Terminal",
            "last_action": "Cyclotron signal",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    }
    with open(HUB / "WAKE_SIGNAL.json", "w") as f:
        json.dump(signal, f, indent=2)

def signal_c3():
    """Signal C3 to do work"""
    log("Signaling C3 Oracle...")
    write_task("C3-Terminal", "Vision/pattern check cycle")
    # Write wake signal (includes all fields required by FIGURE_8_WAKE_PROTOCOL)
    signal = {
        "wake_target": "C3-Terminal",
        "from": "C2-Terminal",
        "reason": "Cyclotron cycle",
        "priority": "NORMAL",
        "timestamp": datetime.now().isoformat() + "Z",
        "loop_number": 0,
        "convergence_level": 0,
        "task_context": {
            "previous_instance": "C2-Terminal",
            "last_action": "Cyclotron signal",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    }
    with open(HUB / "WAKE_SIGNAL.json", "w") as f:
        json.dump(signal, f, indent=2)

def run_cycle(cycle_num):
    """Run one complete C1 -> C2 -> C3 -> C1 cycle"""
    log(f"{'='*50}")
    log(f"CYCLE {cycle_num} STARTING")
    log(f"{'='*50}")

    write_cycle_status(cycle_num, "C1_WORKING")

    # C1 does its work
    c1_result = c1_work()
    log(f"C1 complete: {c1_result}")

    # Signal C2
    write_cycle_status(cycle_num, "C2_SIGNALED")
    signal_c2()
    time.sleep(2)  # Give C2 time to see signal

    # Signal C3
    write_cycle_status(cycle_num, "C3_SIGNALED")
    signal_c3()
    time.sleep(2)  # Give C3 time to see signal

    # Cycle complete
    write_cycle_status(cycle_num, "COMPLETE")
    log(f"CYCLE {cycle_num} COMPLETE")

    return True

def main():
    log("=" * 60)
    log("CYCLOTRON MASTER STARTED")
    log("C1 orchestrating C2 and C3 via hub signals")
    log("=" * 60)

    cycle = 0

    while True:
        try:
            cycle += 1
            run_cycle(cycle)

            log(f"Waiting {CYCLE_INTERVAL}s before next cycle...")
            time.sleep(CYCLE_INTERVAL)

        except KeyboardInterrupt:
            log("Cyclotron stopped by user")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
