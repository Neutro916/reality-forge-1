#!/usr/bin/env python3
"""
NERVE CENTER FAST - Zero-Latency Cyclotron Integration
Combines FAST_HUB's sub-millisecond coordination with CYCLOTRON_NERVE_CENTER's sensors.

Performance targets:
- Wake signal: <0.1ms (was 100ms via files)
- Hub state: <1ms (was 10-50ms via files)
- Memory lookup: <1ms (was 5-20ms)
- Event routing: <5ms total cycle

This is the UPGRADED nerve center using SharedMemory + SQLite :memory:
"""

import json
import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Add paths
sys.path.insert(0, str(Path.home() / ".consciousness"))

# Core paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
MEMORY = CONSCIOUSNESS / "memory"

# Import FAST_HUB components
try:
    from FAST_HUB import FastHub, FastWakeSignal, HotMemoryDB
    HAS_FAST_HUB = True
except ImportError:
    HAS_FAST_HUB = False
    print("[NERVE_FAST] Warning: FAST_HUB not available, falling back to file-based")

# Import standard nerve center components
try:
    from CYCLOTRON_NERVE_CENTER import (
        NerveCenter, SensorInput, FileWatchSensor,
        HubMessageSensor, SystemStateSensor, BugQueueSensor
    )
    HAS_NERVE_CENTER = True
except ImportError:
    HAS_NERVE_CENTER = False
    print("[NERVE_FAST] Warning: CYCLOTRON_NERVE_CENTER not available")

# Import memory systems
try:
    from CYCLOTRON_MEMORY import CyclotronMemory
    HAS_MEMORY = True
except ImportError:
    HAS_MEMORY = False

try:
    from DATA_CHUNKER import process_file, search_atoms
    HAS_CHUNKER = True
except ImportError:
    HAS_CHUNKER = False


class FastWakeSensor(SensorInput if HAS_NERVE_CENTER else object):
    """
    Ultra-fast wake signal sensor using SharedMemory.
    Replaces file-based HubMessageSensor for wake signals.
    Target: <0.1ms latency
    """

    def __init__(self, instance_id: str):
        if HAS_NERVE_CENTER:
            super().__init__("FastWake", "fast_communication")
        else:
            self.name = "FastWake"
            self.input_type = "fast_communication"
            self.last_data = None
            self.last_update = None

        self.instance_id = instance_id
        self.wake_signal = None

        if HAS_FAST_HUB:
            try:
                self.wake_signal = FastWakeSignal(create=True)
            except Exception as e:
                print(f"[FAST_WAKE] Init error: {e}")

    def sense(self) -> Optional[Dict]:
        """Check for wake signal - <0.1ms"""
        if not self.wake_signal:
            return None

        signal = self.wake_signal.check_wake(self.instance_id)
        if signal:
            self.last_update = datetime.now()
            return {
                "sensor": self.name,
                "type": self.input_type,
                "signal": signal,
                "latency_ms": "sub_0.1"
            }
        return None

    def send_wake(self, target: str, reason: str, priority: str = "NORMAL"):
        """Send wake signal to another instance"""
        if self.wake_signal:
            self.wake_signal.send_wake(target, reason, priority)

    def close(self):
        if self.wake_signal:
            self.wake_signal.close()


class HotMemorySensor(SensorInput if HAS_NERVE_CENTER else object):
    """
    In-memory SQLite sensor for fast brain queries.
    Target: <1ms latency
    """

    def __init__(self):
        if HAS_NERVE_CENTER:
            super().__init__("HotMemory", "memory")
        else:
            self.name = "HotMemory"
            self.input_type = "memory"
            self.last_data = None
            self.last_update = None

        self.memory_db = None

        if HAS_FAST_HUB:
            try:
                self.memory_db = HotMemoryDB()
            except Exception as e:
                print(f"[HOT_MEMORY] Init error: {e}")

    def sense(self) -> Optional[Dict]:
        """Get memory stats - <1ms"""
        if not self.memory_db:
            return None

        # Only report every 30 seconds
        now = time.time()
        if hasattr(self, '_last_sense') and now - self._last_sense < 30:
            return None
        self._last_sense = now

        active = self.memory_db.get_active_instances()

        return {
            "sensor": self.name,
            "type": self.input_type,
            "active_instances": active,
            "instance_count": len(active),
            "timestamp": datetime.now().isoformat()
        }

    def record_episode(self, episode_id: str, agent: str, task: str,
                       action: str, result: str, success: bool) -> str:
        """Record episode - <1ms"""
        if self.memory_db:
            return self.memory_db.record_episode(
                episode_id, agent, task, action, result, success
            )
        return episode_id

    def find_similar(self, task: str, limit: int = 5) -> list:
        """Find similar episodes - <1ms"""
        if self.memory_db:
            return self.memory_db.find_similar(task, limit)
        return []

    def get_patterns(self, task: str = None) -> list:
        """Get matching patterns - <1ms"""
        if self.memory_db:
            return self.memory_db.get_patterns(task)
        return []

    def heartbeat(self, instance_id: str, status: str = "active"):
        """Record heartbeat - <1ms"""
        if self.memory_db:
            self.memory_db.heartbeat(instance_id, status)

    def close(self):
        if self.memory_db:
            self.memory_db.close()


class FastNerveCenter:
    """
    Zero-latency nerve center combining:
    - FAST_HUB SharedMemory for wake signals (<0.1ms)
    - SQLite :memory: for hot data (<1ms)
    - Standard sensors for file/bug monitoring

    Total cycle target: <5ms for event processing
    """

    def __init__(self, instance_id: str = "C1-NerveCenter"):
        self.instance_id = instance_id
        self.running = False
        self.cycle_count = 0
        self.sensors: Dict[str, object] = {}

        # Fast components
        self.fast_wake = FastWakeSensor(instance_id)
        self.hot_memory = HotMemorySensor()

        # Add fast sensors
        self.sensors["FastWake"] = self.fast_wake
        self.sensors["HotMemory"] = self.hot_memory

        # Performance tracking
        self.cycle_times = []
        self.max_cycle_time = 0
        self.avg_cycle_time = 0

        self.log("FastNerveCenter initializing...")
        self.log(f"FAST_HUB: {'YES' if HAS_FAST_HUB else 'NO'}")
        self.log(f"NERVE_CENTER: {'YES' if HAS_NERVE_CENTER else 'NO'}")

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] NERVE_FAST [{level}]: {msg}")

        # Write to log
        log_file = CONSCIOUSNESS / "nerve_center_fast.log"
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} [{level}] {msg}\n")

    def add_standard_sensors(self):
        """Add standard sensors from CYCLOTRON_NERVE_CENTER"""
        if not HAS_NERVE_CENTER:
            self.log("Standard sensors not available", "WARN")
            return

        # File watcher
        watch_paths = [
            str(HOME / "100X_DEPLOYMENT"),
            str(CONSCIOUSNESS),
            str(HOME / "Desktop")
        ]
        self.sensors["FileWatcher"] = FileWatchSensor(watch_paths)

        # Bug queue (for C2 integration)
        self.sensors["BugQueue"] = BugQueueSensor()

        # System state
        self.sensors["SystemState"] = SystemStateSensor()

        self.log(f"Added standard sensors: FileWatcher, BugQueue, SystemState")

    def send_wake(self, target: str, reason: str, priority: str = "NORMAL"):
        """Send wake signal via fast channel"""
        self.fast_wake.send_wake(target, reason, priority)
        self.log(f"Wake sent to {target}: {reason} [{priority}]")

    def record_learning(self, task: str, action: str, result: str, success: bool):
        """Record learning episode via hot memory"""
        import hashlib
        episode_id = hashlib.md5(f"{task}{action}{time.time()}".encode()).hexdigest()[:12]

        self.hot_memory.record_episode(
            episode_id, self.instance_id, task, action, result, success
        )
        self.log(f"Recorded episode: {episode_id}")
        return episode_id

    def query_similar(self, task: str) -> list:
        """Query similar past experiences"""
        similar = self.hot_memory.find_similar(task)
        if similar:
            self.log(f"Found {len(similar)} similar episodes for: {task[:30]}...")
        return similar

    def get_patterns(self, task: str = None) -> list:
        """Get relevant patterns"""
        return self.hot_memory.get_patterns(task)

    def run_cycle(self) -> float:
        """Run one sensing cycle, return cycle time in ms"""
        start = time.perf_counter()
        self.cycle_count += 1

        # Heartbeat
        self.hot_memory.heartbeat(self.instance_id)

        # Poll fast sensors first
        wake_signal = self.fast_wake.sense()
        if wake_signal:
            self._handle_wake(wake_signal)

        memory_state = self.hot_memory.sense()
        if memory_state:
            self._handle_memory_state(memory_state)

        # Poll standard sensors (less frequently)
        if self.cycle_count % 10 == 0:
            for name, sensor in self.sensors.items():
                if name in ["FastWake", "HotMemory"]:
                    continue
                try:
                    data = sensor.sense()
                    if data:
                        self._handle_standard_input(name, data)
                except Exception as e:
                    self.log(f"Sensor {name} error: {e}", "ERROR")

        # Calculate cycle time
        elapsed = (time.perf_counter() - start) * 1000
        self.cycle_times.append(elapsed)
        if len(self.cycle_times) > 100:
            self.cycle_times = self.cycle_times[-100:]

        self.max_cycle_time = max(self.cycle_times)
        self.avg_cycle_time = sum(self.cycle_times) / len(self.cycle_times)

        return elapsed

    def _handle_wake(self, wake_data: Dict):
        """Handle incoming wake signal"""
        signal = wake_data.get("signal", {})
        reason = signal.get("reason", "unknown")
        priority = signal.get("priority", "NORMAL")

        self.log(f"WAKE [{priority}]: {reason}")

        # Record the wake event
        self.record_learning(
            f"Wake signal received: {reason}",
            "Process wake",
            "Handled",
            True
        )

    def _handle_memory_state(self, state: Dict):
        """Handle memory state update"""
        active = state.get("active_instances", [])
        self.log(f"Active instances: {active}")

    def _handle_standard_input(self, sensor_name: str, data: Dict):
        """Handle standard sensor input"""
        self.log(f"Sensor {sensor_name}: {data.get('type', 'unknown')}")

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            "instance_id": self.instance_id,
            "cycle_count": self.cycle_count,
            "avg_cycle_ms": round(self.avg_cycle_time, 3),
            "max_cycle_ms": round(self.max_cycle_time, 3),
            "sensors": list(self.sensors.keys()),
            "fast_hub": HAS_FAST_HUB,
            "target_met": self.avg_cycle_time < 5.0  # <5ms target
        }

    def run(self, interval: float = 0.1):
        """Main loop - fast sensing (default 100ms interval, 10Hz)"""
        self.log("=" * 60)
        self.log("FAST NERVE CENTER STARTING")
        self.log(f"Instance: {self.instance_id}")
        self.log(f"Sensors: {list(self.sensors.keys())}")
        self.log(f"Interval: {interval}s ({1/interval:.1f} Hz)")
        self.log("=" * 60)

        self.running = True

        # Start file watcher if present
        file_sensor = self.sensors.get("FileWatcher")
        if file_sensor and hasattr(file_sensor, 'start'):
            file_sensor.start()

        try:
            while self.running:
                cycle_time = self.run_cycle()

                # Log performance every 100 cycles
                if self.cycle_count % 100 == 0:
                    stats = self.get_performance_stats()
                    self.log(f"Perf: avg={stats['avg_cycle_ms']:.2f}ms, max={stats['max_cycle_ms']:.2f}ms")

                    # Write status
                    status_file = HUB / "NERVE_CENTER_FAST_STATUS.json"
                    with open(status_file, "w") as f:
                        json.dump(stats, f, indent=2)

                time.sleep(interval)

        except KeyboardInterrupt:
            self.log("Stopped by user")
        finally:
            self.running = False

            # Cleanup
            if file_sensor and hasattr(file_sensor, 'stop'):
                file_sensor.stop()
            self.fast_wake.close()
            self.hot_memory.close()

            self.log("FastNerveCenter shutdown complete")


def benchmark():
    """Benchmark the fast nerve center"""
    print("=" * 60)
    print("FAST NERVE CENTER BENCHMARK")
    print("=" * 60)

    nerve = FastNerveCenter("C3-Benchmark")
    nerve.add_standard_sensors()

    # Run 100 cycles
    times = []
    for i in range(100):
        t = nerve.run_cycle()
        times.append(t)

    print(f"\nResults (100 cycles):")
    print(f"  Average: {sum(times)/len(times):.3f}ms")
    print(f"  Min: {min(times):.3f}ms")
    print(f"  Max: {max(times):.3f}ms")
    print(f"  Target (<5ms): {'PASS' if sum(times)/len(times) < 5 else 'FAIL'}")

    # Test wake signal
    print("\nWake signal test:")
    start = time.perf_counter()
    for i in range(1000):
        nerve.send_wake("C1-Terminal", f"test_{i}")
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  1000 wake signals: {elapsed:.2f}ms ({elapsed/1000:.4f}ms each)")

    # Test memory query
    print("\nMemory query test:")
    start = time.perf_counter()
    for i in range(100):
        nerve.query_similar("fix null pointer error")
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  100 similarity queries: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    nerve.fast_wake.close()
    nerve.hot_memory.close()

    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fast Nerve Center")
    parser.add_argument("--instance", default="C1-NerveCenter", help="Instance ID")
    parser.add_argument("--interval", type=float, default=0.1, help="Sensing interval (seconds)")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    if args.benchmark:
        benchmark()
    else:
        nerve = FastNerveCenter(args.instance)
        nerve.add_standard_sensors()
        nerve.run(args.interval)


if __name__ == "__main__":
    main()
