#!/usr/bin/env python3
"""
ZERO LATENCY HUB - In-Memory Coordination Layer
Since Redis isn't available, this uses Python in-memory dicts with file persistence.
Achieves <5ms operations vs 50ms+ for pure file-based.

Based on C3's ZERO_LATENCY_BRAIN_ARCHITECTURE.md
"""

import json
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable
from collections import deque
import sqlite3

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB_DIR = CONSCIOUSNESS / "hub"
MEMORY_DB = CONSCIOUSNESS / "memory" / "cyclotron_brain.db"

class ZeroLatencyHub:
    """
    In-memory hub for sub-5ms operations.
    File persistence runs in background thread.
    """

    def __init__(self):
        # In-memory state
        self._wake_signals: Dict[str, dict] = {}
        self._tasks: Dict[str, List[dict]] = {}
        self._heartbeats: Dict[str, datetime] = {}
        self._broadcasts: deque = deque(maxlen=100)
        self._hot_memory: Dict[str, dict] = {}
        self._patterns: Dict[str, dict] = {}

        # Subscribers for event-driven mode
        self._subscribers: Dict[str, List[Callable]] = {}

        # Persistence
        self._dirty = False
        self._lock = threading.Lock()
        self._persist_thread = None
        self._running = False

        # Load initial state from files
        self._load_from_files()

    def _load_from_files(self):
        """Load current state from hub files."""
        # Load wake signal
        wake_file = HUB_DIR / "WAKE_SIGNAL.json"
        if wake_file.exists():
            try:
                with open(wake_file) as f:
                    data = json.load(f)
                    target = data.get("wake_target")
                    if target:
                        self._wake_signals[target] = data
            except:
                pass

        # Load tasks
        for task_file in HUB_DIR.glob("tasks_for_*.json"):
            try:
                instance = task_file.stem.replace("tasks_for_", "")
                with open(task_file) as f:
                    self._tasks[instance] = json.load(f)
            except:
                pass

        # Load heartbeats
        for hb_file in HUB_DIR.glob("heartbeat_*.json"):
            try:
                with open(hb_file) as f:
                    data = json.load(f)
                    instance = data.get("instance")
                    if instance:
                        self._heartbeats[instance] = datetime.fromisoformat(
                            data.get("last_beat", "").replace("Z", "")
                        )
            except:
                pass

    def start_persistence(self, interval: float = 5.0):
        """Start background persistence thread."""
        self._running = True
        self._persist_thread = threading.Thread(
            target=self._persistence_loop,
            args=(interval,),
            daemon=True
        )
        self._persist_thread.start()

    def stop_persistence(self):
        """Stop persistence thread."""
        self._running = False
        if self._persist_thread:
            self._persist_thread.join(timeout=2)

    def _persistence_loop(self, interval: float):
        """Background loop to persist dirty state."""
        while self._running:
            time.sleep(interval)
            if self._dirty:
                self._persist_to_files()

    def _persist_to_files(self):
        """Persist in-memory state to files."""
        with self._lock:
            try:
                # Persist wake signals
                for target, signal in self._wake_signals.items():
                    wake_file = HUB_DIR / "WAKE_SIGNAL.json"
                    with open(wake_file, "w") as f:
                        json.dump(signal, f, indent=2)

                # Persist tasks
                for instance, tasks in self._tasks.items():
                    task_file = HUB_DIR / f"tasks_for_{instance.lower().replace('-', '_')}.json"
                    with open(task_file, "w") as f:
                        json.dump(tasks, f, indent=2)

                # Persist heartbeats
                for instance, last_beat in self._heartbeats.items():
                    hb_file = HUB_DIR / f"heartbeat_{instance.lower().replace('-', '_')}.json"
                    with open(hb_file, "w") as f:
                        json.dump({
                            "instance": instance,
                            "alive": True,
                            "last_beat": last_beat.isoformat() + "Z"
                        }, f, indent=2)

                self._dirty = False
            except Exception as e:
                print(f"Persistence error: {e}")

    # ========== WAKE SIGNALS (<1ms) ==========

    def wake(self, target: str, reason: str, priority: str = "NORMAL", from_instance: str = "system"):
        """Send wake signal - <1ms operation."""
        signal = {
            "wake_target": target,
            "reason": reason,
            "priority": priority,
            "from": from_instance,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        with self._lock:
            self._wake_signals[target] = signal
            self._dirty = True

        # Notify subscribers
        self._notify("wake", signal)

        return signal

    def check_wake(self, instance_id: str) -> Optional[dict]:
        """Check for wake signal - <1ms operation."""
        with self._lock:
            signal = self._wake_signals.pop(instance_id, None)
            if signal:
                self._dirty = True
            return signal

    # ========== TASKS (<1ms) ==========

    def assign_task(self, target: str, task: dict):
        """Assign task to instance - <1ms operation."""
        with self._lock:
            if target not in self._tasks:
                self._tasks[target] = []
            self._tasks[target].append(task)
            self._dirty = True

        self._notify("task", {"target": target, "task": task})

    def get_tasks(self, instance_id: str) -> List[dict]:
        """Get and clear tasks - <1ms operation."""
        with self._lock:
            tasks = self._tasks.pop(instance_id, [])
            if tasks:
                self._dirty = True
            return tasks

    # ========== HEARTBEATS (<1ms) ==========

    def heartbeat(self, instance_id: str):
        """Record heartbeat - <1ms operation."""
        with self._lock:
            self._heartbeats[instance_id] = datetime.now(timezone.utc)
            self._dirty = True

    def get_active_instances(self, timeout_seconds: int = 60) -> List[str]:
        """Get instances with recent heartbeats - <1ms operation."""
        cutoff = datetime.utcnow()
        active = []

        with self._lock:
            for instance, last_beat in self._heartbeats.items():
                if (cutoff - last_beat).total_seconds() < timeout_seconds:
                    active.append(instance)

        return active

    # ========== HOT MEMORY (<1ms) ==========

    def cache_hot(self, key: str, value: dict, ttl_seconds: int = 3600):
        """Cache to hot memory - <1ms operation."""
        with self._lock:
            self._hot_memory[key] = {
                "value": value,
                "expires": datetime.now(timezone.utc).timestamp() + ttl_seconds
            }

    def get_hot(self, key: str) -> Optional[dict]:
        """Get from hot memory - <1ms operation."""
        with self._lock:
            item = self._hot_memory.get(key)
            if item:
                if datetime.now(timezone.utc).timestamp() < item["expires"]:
                    return item["value"]
                else:
                    del self._hot_memory[key]
            return None

    # ========== PATTERNS (<1ms) ==========

    def cache_pattern(self, name: str, pattern: dict):
        """Cache active pattern - <1ms operation."""
        with self._lock:
            self._patterns[name] = pattern

    def get_patterns(self) -> Dict[str, dict]:
        """Get all active patterns - <1ms operation."""
        with self._lock:
            return dict(self._patterns)

    # ========== EVENT SUBSCRIPTIONS ==========

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to events."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def _notify(self, event_type: str, data: dict):
        """Notify subscribers of event."""
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Subscriber error: {e}")

    # ========== BROADCAST ==========

    def broadcast(self, message: str, from_instance: str = "system"):
        """Broadcast to all instances - <1ms operation."""
        broadcast = {
            "message": message,
            "from": from_instance,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        with self._lock:
            self._broadcasts.append(broadcast)

        # Wake all known instances
        for instance in list(self._heartbeats.keys()):
            self.wake(instance, f"Broadcast: {message[:50]}", "NORMAL", from_instance)

        self._notify("broadcast", broadcast)

        return broadcast


class LocalLLMRouter:
    """Routes LLM requests to local Ollama models."""

    def __init__(self):
        self.models = {
            "code": "qwen2.5-coder:7b",
            "fast": "deepseek-r1:1.5b",
            "reason": "deepseek-r1:8b",
            "general": "mistral:latest"
        }
        self._available = None

    def check_availability(self) -> bool:
        """Check if Ollama is available."""
        try:
            import ollama
            ollama.list()
            self._available = True
            return True
        except:
            self._available = False
            return False

    def infer(self, prompt: str, task_type: str = "fast", timeout: int = 30) -> Optional[str]:
        """Run inference on local LLM."""
        if self._available is None:
            self.check_availability()

        if not self._available:
            return None

        try:
            import ollama
            model = self.models.get(task_type, self.models["fast"])

            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

            return response['message']['content']
        except Exception as e:
            print(f"LLM error: {e}")
            return None

    def quick_answer(self, question: str) -> Optional[str]:
        """Fast answer using smallest model."""
        return self.infer(question, task_type="fast")

    def code_help(self, code_context: str) -> Optional[str]:
        """Code assistance using code model."""
        return self.infer(
            f"Help with this code:\n\n{code_context}",
            task_type="code"
        )


# Global singleton
_hub_instance = None

def get_hub() -> ZeroLatencyHub:
    """Get global hub instance."""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = ZeroLatencyHub()
        _hub_instance.start_persistence()
    return _hub_instance


def test_latency():
    """Test hub latency."""
    import time

    hub = get_hub()

    print("=== ZERO LATENCY HUB TEST ===")
    print()

    # Test wake signal
    start = time.time()
    for i in range(100):
        hub.wake("C1-Terminal", f"Test {i}", "NORMAL", "test")
    elapsed = (time.time() - start) * 1000
    print(f"100 wake signals: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    # Test task assignment
    start = time.time()
    for i in range(100):
        hub.assign_task("C1-Terminal", {"task": f"Test task {i}"})
    elapsed = (time.time() - start) * 1000
    print(f"100 task assignments: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    # Test hot memory
    start = time.time()
    for i in range(100):
        hub.cache_hot(f"key_{i}", {"data": f"value_{i}"})
    elapsed = (time.time() - start) * 1000
    print(f"100 hot memory writes: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    start = time.time()
    for i in range(100):
        hub.get_hot(f"key_{i}")
    elapsed = (time.time() - start) * 1000
    print(f"100 hot memory reads: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    # Test heartbeat
    start = time.time()
    for i in range(100):
        hub.heartbeat(f"instance_{i}")
    elapsed = (time.time() - start) * 1000
    print(f"100 heartbeats: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    print()
    print("=== TEST COMPLETE ===")

    hub.stop_persistence()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_latency()
    else:
        print("Zero Latency Hub")
        print("Usage: python ZERO_LATENCY_HUB.py test")
