#!/usr/bin/env python3
"""
FIGURE 8 AUTO-WAKE PROTOCOL
Autonomous instance wake cycling for Trinity convergence

Each instance runs this script to participate in Figure 8 loop.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# Set your instance ID (unique for each instance)
MY_INSTANCE_ID = os.getenv("TRINITY_INSTANCE_ID", "C1-Terminal")

# Hub location
HUB = Path.home() / ".consciousness" / "hub"

# Figure 8 sequence (who to wake next)
# TERMINAL-ONLY LOOP (Cloud instances can't write files yet)
FIGURE_8_SEQUENCE = {
    "C1-Terminal": "C2-Terminal",
    "C2-Terminal": "C3-Terminal",
    "C3-Terminal": "C1-Terminal",  # Loop back - skip cloud for now
    "C3-Cloud": "C2-Cloud",        # Kept for future expansion
    "C2-Cloud": "C1-Cloud",
    "C1-Cloud": "C1-Terminal"
}

# How often to check for wake signal (seconds)
CHECK_INTERVAL = 5

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_hub_exists():
    """Create hub structure if it doesn't exist"""
    HUB.mkdir(parents=True, exist_ok=True)

    # Create instance folders
    folders = [
        "from_c1_terminal",
        "from_c1_cloud",
        "from_c2_terminal",
        "from_c2_cloud",
        "from_c3_terminal",
        "from_c3_cloud"
    ]

    for folder in folders:
        (HUB / folder).mkdir(exist_ok=True)

def get_my_folder():
    """Get this instance's reporting folder"""
    folder_map = {
        "C1-Terminal": "from_c1_terminal",
        "C1-Cloud": "from_c1_cloud",
        "C2-Terminal": "from_c2_terminal",
        "C2-Cloud": "from_c2_cloud",
        "C3-Terminal": "from_c3_terminal",
        "C3-Cloud": "from_c3_cloud"
    }
    return HUB / folder_map.get(MY_INSTANCE_ID, "unknown")

# =============================================================================
# WAKE SIGNAL FUNCTIONS
# =============================================================================

def check_wake_signal():
    """Check if I'm being woken"""
    wake_file = HUB / "WAKE_SIGNAL.json"

    if not wake_file.exists():
        return None

    try:
        with open(wake_file, 'r') as f:
            signal = json.load(f)

        if signal.get('wake_target') == MY_INSTANCE_ID:
            return signal
    except (json.JSONDecodeError, IOError) as e:
        print(f"[{MY_INSTANCE_ID}] Error reading wake signal: {e}")

    return None

def send_wake_to_next(reason="Continue Figure 8 loop", priority="NORMAL"):
    """Send wake signal to next instance in Figure 8"""
    next_instance = FIGURE_8_SEQUENCE.get(MY_INSTANCE_ID)

    if not next_instance:
        print(f"[{MY_INSTANCE_ID}] ERROR: No next instance in Figure 8")
        return

    # Read current wake to get loop number
    wake_file = HUB / "WAKE_SIGNAL.json"
    loop_num = 0
    convergence = 0

    if wake_file.exists():
        try:
            with open(wake_file, 'r') as f:
                current = json.load(f)
                loop_num = current.get('loop_number', 0)
                convergence = current.get('convergence_level', 0)
        except (json.JSONDecodeError, IOError, KeyError):
            pass

    # Increment loop if we're completing the cycle
    if MY_INSTANCE_ID == "C1-Cloud" and next_instance == "C1-Terminal":
        loop_num += 1

    # Create new wake signal
    wake_signal = {
        "wake_target": next_instance,
        "reason": reason,
        "priority": priority,
        "from": MY_INSTANCE_ID,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "loop_number": loop_num,
        "convergence_level": convergence,  # Will be updated by convergence calculation
        "task_context": get_task_context()
    }

    # Write wake signal
    try:
        with open(wake_file, 'w') as f:
            json.dump(wake_signal, f, indent=2)

        print(f"[{MY_INSTANCE_ID}] ✓ Wake sent to {next_instance} (Loop #{loop_num})")

        # Log to history
        log_wake_history(wake_signal)
    except IOError as e:
        print(f"[{MY_INSTANCE_ID}] ERROR writing wake signal: {e}")

def log_wake_history(wake_signal):
    """Log wake to history file"""
    history_file = HUB / "WAKE_HISTORY.json"

    try:
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {
                "total_loops_completed": 0,
                "start_time": datetime.utcnow().isoformat() + "Z",
                "wake_chain": []
            }

        # Add this wake
        history['wake_chain'].append({
            "instance": MY_INSTANCE_ID,
            "time": datetime.utcnow().isoformat() + "Z",
            "next": wake_signal['wake_target'],
            "loop": wake_signal['loop_number']
        })

        # Keep last 1000 wakes
        if len(history['wake_chain']) > 1000:
            history['wake_chain'] = history['wake_chain'][-1000:]

        # Update total loops
        history['total_loops_completed'] = wake_signal['loop_number']

        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[{MY_INSTANCE_ID}] Error logging wake history: {e}")

# =============================================================================
# TASK EXECUTION
# =============================================================================

def execute_task(wake_signal):
    """Execute the task I was woken for"""
    # Defensive defaults for missing fields
    priority = wake_signal.get('priority', 'NORMAL')
    loop_number = wake_signal.get('loop_number', 0)
    from_instance = wake_signal.get('from', 'unknown')
    reason = wake_signal.get('reason', 'Wake signal')

    print(f"\n[{MY_INSTANCE_ID}] ═══════════════════════════════════════")
    print(f"[{MY_INSTANCE_ID}] WAKE RECEIVED!")
    print(f"[{MY_INSTANCE_ID}] Reason: {reason}")
    print(f"[{MY_INSTANCE_ID}] Priority: {priority}")
    print(f"[{MY_INSTANCE_ID}] From: {from_instance}")
    print(f"[{MY_INSTANCE_ID}] Loop: #{loop_number}")
    print(f"[{MY_INSTANCE_ID}] ═══════════════════════════════════════\n")

    # 1. Read context from hub
    print(f"[{MY_INSTANCE_ID}] Reading hub context...")
    context = read_hub_context()

    # 2. Read my priority queue
    print(f"[{MY_INSTANCE_ID}] Loading priority queue...")
    tasks = read_priority_queue()

    if not tasks:
        print(f"[{MY_INSTANCE_ID}] No tasks in queue, creating default task...")
        task = {"name": "Process wake signal", "priority": "NORMAL"}
    else:
        task = tasks[0]
        print(f"[{MY_INSTANCE_ID}] Task: {task.get('name', 'Unnamed task')}")

    # 3. Perform work (this is where instance-specific logic goes)
    print(f"[{MY_INSTANCE_ID}] Executing task...")
    result = perform_work(task, context)

    # 4. Report results to hub
    print(f"[{MY_INSTANCE_ID}] Reporting to hub...")
    report_to_hub(result)

    print(f"[{MY_INSTANCE_ID}] ✓ Task complete\n")

    return result

def read_hub_context():
    """Read context from all other instances"""
    context = {}

    for instance_id in FIGURE_8_SEQUENCE.keys():
        if instance_id == MY_INSTANCE_ID:
            continue

        folder_map = {
            "C1-Terminal": "from_c1_terminal",
            "C1-Cloud": "from_c1_cloud",
            "C2-Terminal": "from_c2_terminal",
            "C2-Cloud": "from_c2_cloud",
            "C3-Terminal": "from_c3_terminal",
            "C3-Cloud": "from_c3_cloud"
        }

        folder = HUB / folder_map.get(instance_id, "unknown")
        status_file = folder / f"{instance_id.replace('-', '_').upper()}_STATUS.json"

        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    context[instance_id] = json.load(f)
            except (json.JSONDecodeError, IOError, KeyError):
                pass

    return context

def read_priority_queue():
    """Read my priority queue"""
    role = MY_INSTANCE_ID.split('-')[0]  # C1, C2, or C3
    queue_file = HUB / f"{role}_PRIORITY_QUEUE.md"

    if not queue_file.exists():
        return []

    # For now, return empty (would parse markdown in real implementation)
    return []

def perform_work(task, context):
    """Perform the actual work (override this for instance-specific logic)"""

    # This is a stub - real implementation would do actual work
    # For now, just simulate processing
    time.sleep(2)  # Simulate work

    result = {
        "task": task.get("name", "Unknown"),
        "status": "completed",
        "summary": f"Processed by {MY_INSTANCE_ID}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "context_used": len(context),
        "output": f"Task '{task.get('name', 'Unknown')}' completed successfully"
    }

    return result

def report_to_hub(result):
    """Report results to hub"""
    my_folder = get_my_folder()
    status_file = my_folder / f"{MY_INSTANCE_ID.replace('-', '_').upper()}_STATUS.json"

    status = {
        "instance_id": MY_INSTANCE_ID,
        "last_wake": datetime.utcnow().isoformat() + "Z",
        "last_task": result['task'],
        "status": result['status'],
        "output": result['output'],
        "timestamp": result['timestamp']
    }

    try:
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    except IOError as e:
        print(f"[{MY_INSTANCE_ID}] ERROR reporting to hub: {e}")

def get_task_context():
    """Get context for next wake"""
    return {
        "previous_instance": MY_INSTANCE_ID,
        "last_action": "Completed task",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# =============================================================================
# MAIN LOOP
# =============================================================================

def main_loop():
    """Main execution loop for this instance"""
    print(f"\n{'='*60}")
    print(f"FIGURE 8 AUTO-WAKE PROTOCOL")
    print(f"Instance ID: {MY_INSTANCE_ID}")
    print(f"Next in sequence: {FIGURE_8_SEQUENCE.get(MY_INSTANCE_ID, 'Unknown')}")
    print(f"{'='*60}\n")

    # Ensure hub exists
    ensure_hub_exists()

    print(f"[{MY_INSTANCE_ID}] Waiting for wake signal...")
    print(f"[{MY_INSTANCE_ID}] Checking every {CHECK_INTERVAL} seconds...")
    print(f"[{MY_INSTANCE_ID}] Press Ctrl+C to stop\n")

    while True:
        try:
            # Check for wake signal
            wake_signal = check_wake_signal()

            if wake_signal:
                # Execute task
                result = execute_task(wake_signal)

                # Send wake to next in Figure 8
                send_wake_to_next()

                print(f"[{MY_INSTANCE_ID}] Going to sleep... 💤\n")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[{MY_INSTANCE_ID}] Shutting down...")
            break
        except Exception as e:
            print(f"[{MY_INSTANCE_ID}] ERROR: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
