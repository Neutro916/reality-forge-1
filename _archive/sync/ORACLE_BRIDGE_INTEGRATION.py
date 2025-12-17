#!/usr/bin/env python3
"""
ORACLE BRIDGE INTEGRATION
=========================
Integrates the Oracle Bridge (trinity_shared) with the existing
Cyclotron Nerve Center and Hub system.

This enables:
1. Nerve Center to watch oracle_outbox for Desktop tasks
2. Automatic task execution via existing brain agents
3. Results written back to oracle_inbox
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List

# Paths
HOME = Path.home()
TRINITY_SHARED = HOME / "trinity_shared"
ORACLE_OUTBOX = TRINITY_SHARED / "oracle_outbox"
ORACLE_INBOX = TRINITY_SHARED / "oracle_inbox"
WAKE_DIR = TRINITY_SHARED / "wake"
HUB_DIR = HOME / ".consciousness" / "hub"

class OracleBridgeSensor:
    """
    Sensor for Cyclotron Nerve Center that monitors Oracle's outbox.
    Add this to CYCLOTRON_NERVE_CENTER.py's sensor list.
    """

    def __init__(self, instance_id: str = "C1-Terminal"):
        self.name = "OracleBridge"
        self.type = "oracle"
        self.instance_id = instance_id
        self.processed_tasks = set()
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure required directories exist."""
        for d in [ORACLE_OUTBOX, ORACLE_INBOX, WAKE_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    def sense(self) -> Optional[Dict]:
        """
        Check oracle_outbox for new tasks from Desktop Claude.
        Returns task data if found, None otherwise.
        """
        try:
            # Check for .task files addressed to this instance
            for task_file in ORACLE_OUTBOX.glob("*.json"):
                if task_file.name in self.processed_tasks:
                    continue

                try:
                    with open(task_file) as f:
                        task = json.load(f)

                    # Check if task is for us
                    target = task.get("target", task.get("instance", "any"))
                    if target in ["any", self.instance_id, "all"]:
                        self.processed_tasks.add(task_file.name)

                        return {
                            "type": "oracle_task",
                            "source": "Desktop-Oracle",
                            "file": str(task_file),
                            "task": task.get("task", task.get("prompt", "")),
                            "priority": task.get("priority", "NORMAL"),
                            "metadata": {
                                "from_oracle": True,
                                "file_name": task_file.name,
                                "timestamp": task.get("timestamp", "")
                            }
                        }
                except Exception as e:
                    print(f"[OracleBridge] Error reading {task_file}: {e}")

            # Also check wake directory for this instance
            wake_pattern = f"{self.instance_id.replace('-', '_')}*.task"
            for wake_file in WAKE_DIR.glob(wake_pattern):
                if wake_file.name in self.processed_tasks:
                    continue

                try:
                    with open(wake_file) as f:
                        task = json.load(f)

                    self.processed_tasks.add(wake_file.name)

                    # Remove wake file after reading
                    wake_file.unlink()

                    return {
                        "type": "wake_task",
                        "source": task.get("triggered_by", "unknown"),
                        "task": task.get("prompt", ""),
                        "priority": "HIGH",  # Wake signals are high priority
                        "metadata": {
                            "wake_signal": True,
                            "chain_task": task.get("chain_task"),
                            "wake_next": task.get("wake_next")
                        }
                    }
                except Exception as e:
                    print(f"[OracleBridge] Error reading wake file: {e}")

        except Exception as e:
            print(f"[OracleBridge] Sensor error: {e}")

        return None

    def report_result(self, task_id: str, result: Dict, success: bool = True):
        """
        Write result back to oracle_inbox for Desktop Claude to read.
        """
        result_file = ORACLE_INBOX / f"{self.instance_id}_{task_id}_{int(time.time())}.json"

        report = {
            "from": self.instance_id,
            "task_id": task_id,
            "success": success,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        with open(result_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[OracleBridge] Result written to {result_file}")
        return result_file

def add_oracle_sensor_to_nerve_center():
    """
    Code snippet to add OracleBridgeSensor to existing Nerve Center.
    Copy this into CYCLOTRON_NERVE_CENTER.py's setup_default_sensors()
    """
    code = '''
# Add to setup_default_sensors() in CYCLOTRON_NERVE_CENTER.py:

from ORACLE_BRIDGE_INTEGRATION import OracleBridgeSensor

# In setup_default_sensors():
oracle_sensor = OracleBridgeSensor(instance_id=self.agent_id)
self.add_sensor(oracle_sensor)
'''
    return code

def create_oracle_task(
    task: str,
    target: str = "any",
    priority: str = "NORMAL",
    metadata: Dict = None
) -> Path:
    """
    Create a task file in oracle_outbox for Oracle to see
    (or for testing the bridge).
    """
    ORACLE_OUTBOX.mkdir(parents=True, exist_ok=True)

    task_file = ORACLE_OUTBOX / f"task_{int(time.time())}.json"

    task_data = {
        "task": task,
        "target": target,
        "priority": priority,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }

    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)

    return task_file

def wake_instance(
    instance_id: str,
    prompt: str,
    triggered_by: str = "ORACLE_BRIDGE",
    chain_task: str = None,
    wake_next: str = None
) -> Path:
    """
    Create a wake signal for a specific instance.
    """
    WAKE_DIR.mkdir(parents=True, exist_ok=True)

    wake_file = WAKE_DIR / f"{instance_id.replace('-', '_')}.task"

    task_data = {
        "prompt": prompt,
        "triggered_by": triggered_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_to_oracle": True
    }

    if chain_task:
        task_data["chain_task"] = chain_task
    if wake_next:
        task_data["wake_next"] = wake_next

    with open(wake_file, "w") as f:
        json.dump(task_data, f, indent=2)

    return wake_file

def get_oracle_results(since_minutes: int = 60) -> List[Dict]:
    """
    Read results from oracle_inbox.
    Useful for Oracle to check what terminals have reported.
    """
    results = []
    cutoff = time.time() - (since_minutes * 60)

    for result_file in ORACLE_INBOX.glob("*.json"):
        if result_file.stat().st_mtime > cutoff:
            try:
                with open(result_file) as f:
                    results.append(json.load(f))
            except:
                pass

    return sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)

def bridge_status() -> Dict:
    """Get current status of the Oracle Bridge."""
    return {
        "oracle_outbox_tasks": len(list(ORACLE_OUTBOX.glob("*.json"))),
        "oracle_inbox_results": len(list(ORACLE_INBOX.glob("*.json"))),
        "pending_wake_signals": len(list(WAKE_DIR.glob("*.task"))),
        "trinity_shared_path": str(TRINITY_SHARED),
        "syncthing_expected": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "status":
            print(json.dumps(bridge_status(), indent=2))

        elif cmd == "results":
            results = get_oracle_results()
            print(f"Found {len(results)} results:")
            for r in results[:10]:
                print(f"  - {r.get('from')}: {r.get('success')} at {r.get('timestamp')}")

        elif cmd == "wake" and len(sys.argv) > 3:
            instance = sys.argv[2]
            prompt = sys.argv[3]
            wake_file = wake_instance(instance, prompt)
            print(f"Wake signal created: {wake_file}")

        elif cmd == "task" and len(sys.argv) > 2:
            task = " ".join(sys.argv[2:])
            task_file = create_oracle_task(task)
            print(f"Task created: {task_file}")

        else:
            print("Usage:")
            print("  python ORACLE_BRIDGE_INTEGRATION.py status")
            print("  python ORACLE_BRIDGE_INTEGRATION.py results")
            print("  python ORACLE_BRIDGE_INTEGRATION.py wake <instance> <prompt>")
            print("  python ORACLE_BRIDGE_INTEGRATION.py task <task description>")
    else:
        print("Oracle Bridge Integration Module")
        print(json.dumps(bridge_status(), indent=2))
