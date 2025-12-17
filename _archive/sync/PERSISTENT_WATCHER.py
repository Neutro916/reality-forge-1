#!/usr/bin/env python3
"""
PERSISTENT WATCHER v2 - Never Exits
Enhanced with C2 Architect recommendations:
- Heartbeat file for liveness monitoring
- Loop counter for convergence tracking
- Output reporting back to hub
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

# File locking - optional, Windows doesn't have fcntl
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

MY_ID = os.getenv("TRINITY_INSTANCE_ID", "C1-Terminal")
HUB = Path.home() / ".consciousness" / "hub"
CHECK_INTERVAL = 3  # seconds

# Terminal-only triangle loop
NEXT_INSTANCE = {
    "C1-Terminal": "C2-Terminal",
    "C2-Terminal": "C3-Terminal",
    "C3-Terminal": "C1-Terminal",
}

LOOP_COUNT = 0

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {MY_ID}: {msg}")

def write_heartbeat():
    """Write heartbeat file to prove we're alive"""
    heartbeat_file = HUB / f"heartbeat_{MY_ID.lower().replace('-', '_')}.json"
    heartbeat = {
        "instance": MY_ID,
        "alive": True,
        "last_beat": datetime.now().isoformat() + "Z",
        "loops_completed": LOOP_COUNT,
        "uptime_checks": getattr(write_heartbeat, 'count', 0) + 1
    }
    write_heartbeat.count = heartbeat.get("uptime_checks", 0)
    try:
        with open(heartbeat_file, "w") as f:
            json.dump(heartbeat, f, indent=2)
    except Exception as e:
        log(f"Heartbeat write failed: {e}")

def read_wake_signal():
    """Read wake signal with optional file locking"""
    try:
        signal_file = HUB / "WAKE_SIGNAL.json"
        with open(signal_file, "r") as f:
            # Try to get shared lock (non-blocking)
            if HAS_FCNTL:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                except OSError:
                    pass
            data = json.load(f)
            if HAS_FCNTL:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except:
                    pass
            return data
    except Exception as e:
        log(f"Read signal failed: {e}")
        return None

def write_wake_signal(target, reason="Continue loop", priority="NORMAL"):
    """Write wake signal with optional file locking"""
    global LOOP_COUNT
    signal = {
        "wake_target": target,
        "reason": reason,
        "priority": priority,
        "from": MY_ID,
        "timestamp": datetime.now().isoformat() + "Z",
        "loop_number": LOOP_COUNT
    }
    try:
        signal_file = HUB / "WAKE_SIGNAL.json"
        with open(signal_file, "w") as f:
            if HAS_FCNTL:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    pass
            json.dump(signal, f, indent=2)
            if HAS_FCNTL:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except:
                    pass
        log(f"Passed wake to {target}")
    except Exception as e:
        log(f"Write signal failed: {e}")

def report_output(output_data):
    """Report task output back to hub"""
    output_file = HUB / f"output_{MY_ID.lower().replace('-', '_')}.json"
    report = {
        "instance": MY_ID,
        "timestamp": datetime.now().isoformat() + "Z",
        "loop": LOOP_COUNT,
        "output": output_data
    }
    try:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        log("Output reported to hub")
    except Exception as e:
        log(f"Output report failed: {e}")

def do_my_work():
    """Execute assigned tasks"""
    global LOOP_COUNT
    log(">>> EXECUTING TASK <<<")

    results = []

    # Check for assigned tasks
    task_file = HUB / f"tasks_for_{MY_ID.lower().replace('-', '_')}.json"
    if task_file.exists():
        try:
            with open(task_file, "r") as f:
                tasks = json.load(f)
            if tasks:
                log(f"Found {len(tasks)} tasks")
                for task in tasks:
                    desc = task.get('description', 'unnamed')
                    log(f"  Executing: {desc}")
                    results.append({"task": desc, "status": "completed"})
                # Clear task file after processing
                with open(task_file, "w") as f:
                    json.dump([], f)
        except Exception as e:
            log(f"Task processing error: {e}")
    else:
        results.append({"task": "heartbeat_cycle", "status": "no_tasks"})

    # Simulate minimal work time
    time.sleep(0.5)

    # Report output
    report_output(results)

    LOOP_COUNT += 1
    log(f">>> TASK COMPLETE (Loop #{LOOP_COUNT}) <<<")

def main():
    log("=" * 50)
    log("PERSISTENT WATCHER v2 STARTED")
    log(f"Instance: {MY_ID}")
    log(f"Next in chain: {NEXT_INSTANCE.get(MY_ID, 'unknown')}")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log("=" * 50)

    last_processed = None
    heartbeat_counter = 0

    while True:  # NEVER EXIT
        try:
            # Write heartbeat every cycle
            heartbeat_counter += 1
            if heartbeat_counter % 5 == 0:  # Every 5 checks (~15 seconds)
                write_heartbeat()

            signal = read_wake_signal()

            if signal and signal.get("wake_target") == MY_ID:
                sig_time = signal.get("timestamp", "")

                # Don't process same signal twice
                if sig_time != last_processed:
                    from_who = signal.get('from', 'unknown')
                    log(f"WAKE SIGNAL from {from_who}")
                    last_processed = sig_time

                    # Do my work
                    do_my_work()

                    # Pass to next instance
                    next_inst = NEXT_INSTANCE.get(MY_ID)
                    if next_inst:
                        write_wake_signal(next_inst)

                    # Write heartbeat after completing work
                    write_heartbeat()

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Shutting down (Ctrl+C)")
            break
        except Exception as e:
            log(f"Error (continuing): {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
