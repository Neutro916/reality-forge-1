#!/usr/bin/env python3
"""
TRINITY AUTO COORDINATOR
Combines MCP relay + Screen Watcher for automatic instance coordination.

Put this at the FRONT of all tools - it enables:
1. Automatic wake detection (sees when other instances are active)
2. MCP message checking (receives coordination messages)
3. Status broadcasting (tells others you're alive)
4. Task claiming (picks up work automatically)

Usage:
    from TRINITY_AUTO_COORDINATOR import coordinator
    coordinator.check_in("C2-Terminal")  # Call at start of any tool
    messages = coordinator.get_pending()  # Check for work
    coordinator.broadcast("Status update")  # Tell others
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Paths
CONSCIOUSNESS = Path.home() / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
SCREEN_WATCH = CONSCIOUSNESS / "screen_watch"
TRINITY_HUB = Path.home() / ".trinity" / "hub"
WAKE_FOLDER = Path("G:/My Drive/TRINITY_COMMS/wake")

class TrinityAutoCoordinator:
    """Automatic coordination between Trinity instances."""

    def __init__(self):
        self.instance_id = None
        self.last_check = None

    def check_in(self, instance_id: str) -> Dict:
        """
        Call this at the START of any tool/session.
        Announces presence, checks for messages, returns status.
        """
        self.instance_id = instance_id
        self.last_check = datetime.now(timezone.utc)

        result = {
            "instance": instance_id,
            "timestamp": self.last_check.isoformat(),
            "messages": [],
            "tasks": [],
            "other_instances": [],
            "screen_state": None
        }

        # 1. Write heartbeat
        self._write_heartbeat()

        # 2. Check screen watcher for system state
        result["screen_state"] = self._read_screen_state()

        # 3. Check for other active instances
        result["other_instances"] = self._find_active_instances()

        # 4. Check MCP messages (via file - MCP tools need Claude)
        result["messages"] = self._check_message_files()

        # 5. Check for pending tasks
        result["tasks"] = self._check_pending_tasks()

        return result

    def _write_heartbeat(self):
        """Write heartbeat to hub."""
        heartbeat = {
            "instance": self.instance_id,
            "alive": True,
            "last_beat": datetime.now(timezone.utc).isoformat(),
            "computer": os.environ.get("COMPUTERNAME", "unknown")
        }

        heartbeat_file = HUB / f"heartbeat_{self.instance_id.lower().replace('-', '_')}.json"
        heartbeat_file.parent.mkdir(parents=True, exist_ok=True)

        with open(heartbeat_file, 'w') as f:
            json.dump(heartbeat, f, indent=2)

        # Also write to Google Drive wake folder if available
        if WAKE_FOLDER.exists():
            wake_file = WAKE_FOLDER / f"{self.instance_id}_ALIVE.json"
            with open(wake_file, 'w') as f:
                json.dump(heartbeat, f, indent=2)

    def _read_screen_state(self) -> Optional[Dict]:
        """Read screen watcher state."""
        glance_file = SCREEN_WATCH / "CLAUDE_GLANCE.json"
        if glance_file.exists():
            try:
                with open(glance_file) as f:
                    return json.load(f)
            except:
                pass
        return None

    def _find_active_instances(self) -> List[Dict]:
        """Find other active instances from heartbeats."""
        active = []

        # Check hub heartbeats
        for hb_file in HUB.glob("heartbeat_*.json"):
            try:
                with open(hb_file) as f:
                    hb = json.load(f)
                    if hb.get("alive"):
                        active.append({
                            "instance": hb.get("instance"),
                            "last_seen": hb.get("last_beat"),
                            "source": "hub"
                        })
            except:
                pass

        # Check Trinity hub status files
        if TRINITY_HUB.exists():
            for status_file in TRINITY_HUB.glob("*_status.json"):
                try:
                    with open(status_file) as f:
                        status = json.load(f)
                        if status.get("status") == "online":
                            active.append({
                                "instance": status.get("instance"),
                                "task": status.get("current_task"),
                                "source": "trinity_hub"
                            })
                except:
                    pass

        return active

    def _check_message_files(self) -> List[Dict]:
        """Check for message files addressed to this instance."""
        messages = []

        # Check hub/from_* folders
        from_folder = HUB / f"from_{self.instance_id.lower().replace('-', '_')}"
        if from_folder.exists():
            for msg_file in from_folder.glob("*.json"):
                try:
                    with open(msg_file) as f:
                        messages.append(json.load(f))
                except:
                    pass

        # Check for tasks assigned to this instance
        tasks_file = HUB / f"tasks_for_{self.instance_id.lower().replace('-', '_')}.json"
        if tasks_file.exists():
            try:
                with open(tasks_file) as f:
                    task_data = json.load(f)
                    if task_data.get("tasks"):
                        messages.extend(task_data["tasks"])
            except:
                pass

        return messages

    def _check_pending_tasks(self) -> List[Dict]:
        """Check for unclaimed tasks."""
        tasks = []

        # Check wake signal
        wake_file = HUB / "WAKE_SIGNAL.json"
        if wake_file.exists():
            try:
                with open(wake_file) as f:
                    wake = json.load(f)
                    if wake.get("wake_target") == self.instance_id:
                        tasks.append({
                            "type": "wake",
                            "from": wake.get("from"),
                            "reason": wake.get("reason"),
                            "context": wake.get("task_context")
                        })
            except:
                pass

        return tasks

    def broadcast(self, message: str) -> bool:
        """
        Broadcast message to all instances.
        Note: For full MCP broadcast, use Claude's trinity_broadcast tool.
        This writes to file-based channels.
        """
        broadcast_data = {
            "from": self.instance_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Write to hub
        broadcast_file = HUB / f"broadcast_{self.instance_id}_{int(datetime.now().timestamp())}.json"
        with open(broadcast_file, 'w') as f:
            json.dump(broadcast_data, f, indent=2)

        # Write to Google Drive if available
        if WAKE_FOLDER.exists():
            gd_file = WAKE_FOLDER / f"{self.instance_id}_BROADCAST.json"
            with open(gd_file, 'w') as f:
                json.dump(broadcast_data, f, indent=2)

        return True

    def send_wake_signal(self, target: str, reason: str, context: Dict = None):
        """Send wake signal to another instance."""
        wake_signal = {
            "wake_target": target,
            "reason": reason,
            "priority": "HIGH",
            "from": self.instance_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_context": context or {}
        }

        wake_file = HUB / "WAKE_SIGNAL.json"
        with open(wake_file, 'w') as f:
            json.dump(wake_signal, f, indent=2)

        print(f"[COORDINATOR] Wake signal sent to {target}: {reason}")

    def get_system_status(self) -> Dict:
        """Get quick system status."""
        screen = self._read_screen_state()
        instances = self._find_active_instances()

        return {
            "cpu": screen.get("system", {}).get("cpu_percent") if screen else None,
            "ram": screen.get("system", {}).get("memory_percent") if screen else None,
            "active_instances": len(instances),
            "instances": [i.get("instance") for i in instances],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Singleton instance
coordinator = TrinityAutoCoordinator()


# Quick functions for easy import
def check_in(instance_id: str) -> Dict:
    """Quick check-in."""
    return coordinator.check_in(instance_id)

def broadcast(message: str) -> bool:
    """Quick broadcast."""
    return coordinator.broadcast(message)

def wake(target: str, reason: str):
    """Quick wake signal."""
    coordinator.send_wake_signal(target, reason)

def status() -> Dict:
    """Quick status."""
    return coordinator.get_system_status()


if __name__ == "__main__":
    import sys

    instance_id = sys.argv[1] if len(sys.argv) > 1 else "C2-Terminal"

    print(f"[COORDINATOR] Checking in as {instance_id}...")
    result = check_in(instance_id)

    print(f"\n=== TRINITY AUTO COORDINATOR ===")
    print(f"Instance: {result['instance']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Other Instances: {len(result['other_instances'])}")
    for inst in result['other_instances']:
        print(f"  - {inst.get('instance')}: {inst.get('task', 'active')}")
    print(f"Pending Messages: {len(result['messages'])}")
    print(f"Pending Tasks: {len(result['tasks'])}")

    if result['screen_state']:
        print(f"\nSystem: {result['screen_state'].get('quick_status', 'unknown')}")

    print("\n[COORDINATOR] Ready for coordination.")
