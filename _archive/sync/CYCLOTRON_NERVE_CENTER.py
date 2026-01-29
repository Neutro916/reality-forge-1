#!/usr/bin/env python3
"""CYCLOTRON NERVE CENTER - Sensory system connecting inputs to Cyclotron Brain.
Sensors: FileWatcher, HubMessages, SystemState, BugQueue, Clipboard."""

import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import threading
import queue

# Add paths
sys.path.insert(0, str(Path.home() / ".consciousness"))
sys.path.insert(0, str(Path.home() / "100X_DEPLOYMENT"))

# Core paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
MEMORY = CONSCIOUSNESS / "memory"
NERVE_LOG = CONSCIOUSNESS / "nerve_center.log"

# Try to import brain systems
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

try:
    from BRAIN_AGENT_FRAMEWORK import AgentOrchestrator, AgentState
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False

# Ensure directories
HUB.mkdir(parents=True, exist_ok=True)
MEMORY.mkdir(parents=True, exist_ok=True)


class SensorInput:
    """Base class for all sensory inputs."""

    def __init__(self, name: str, input_type: str):
        self.name = name
        self.input_type = input_type
        self.last_data = None
        self.last_update = None

    def sense(self) -> Optional[Dict]:
        """Override to implement sensing logic."""
        raise NotImplementedError


class FileWatchSensor(FileSystemEventHandler, SensorInput):
    """Watches directories for changes - like visual cortex for files."""
    def __init__(self, watch_paths: List[str], extensions: List[str] = None):
        SensorInput.__init__(self, "FileWatcher", "filesystem")
        self.watch_paths, self.extensions = watch_paths, extensions or ['.py', '.md', '.json', '.txt', '.html']
        self.event_queue, self.observer = queue.Queue(), None

    def _handle_event(self, event, event_type: str):
        if not event.is_directory and Path(event.src_path).suffix.lower() in self.extensions:
            self.event_queue.put({"type": event_type, "path": event.src_path, "timestamp": datetime.now().isoformat()})

    def on_modified(self, event): self._handle_event(event, "modified")
    def on_created(self, event): self._handle_event(event, "created")

    def start(self):
        self.observer = Observer()
        for path in self.watch_paths:
            if Path(path).exists(): self.observer.schedule(self, path, recursive=True); print(f"[NERVE] Watching: {path}")
        self.observer.start()

    def stop(self):
        if self.observer: self.observer.stop(); self.observer.join()

    def sense(self) -> Optional[Dict]:
        events = []
        while not self.event_queue.empty():
            try: events.append(self.event_queue.get_nowait())
            except: break
        return {"sensor": self.name, "type": self.input_type, "count": len(events), "events": events} if events else None


class HubMessageSensor(SensorInput):
    """Monitors Trinity hub for messages - like auditory cortex."""
    def __init__(self):
        super().__init__("HubMessages", "communication"); self.last_check = {}

    def _check_file(self, path: Path, key: str, msg_type: str) -> Optional[Dict]:
        if not path.exists(): return None
        mtime = path.stat().st_mtime
        if self.last_check.get(key) == mtime: return None
        self.last_check[key] = mtime
        with open(path) as f: return {"type": msg_type, "data": json.load(f)}

    def sense(self) -> Optional[Dict]:
        messages = []
        if msg := self._check_file(HUB / "WAKE_SIGNAL.json", "wake", "wake_signal"): messages.append(msg)
        if msg := self._check_file(HUB / "BROADCAST.json", "broadcast", "broadcast"): messages.append(msg)
        for task_file in HUB.glob("tasks_for_*.json"):
            if msg := self._check_file(task_file, str(task_file), "task"):
                if msg["data"]: msg["file"] = task_file.name; messages.append(msg)
        return {"sensor": self.name, "type": self.input_type, "count": len(messages), "messages": messages} if messages else None


class SystemStateSensor(SensorInput):
    """Monitors system state - like proprioception."""
    def __init__(self):
        super().__init__("SystemState", "internal"); self.last_check = time.time()

    def sense(self) -> Optional[Dict]:
        now = time.time()
        if now - self.last_check < 30: return None
        self.last_check = now
        state = {"sensor": self.name, "type": self.input_type, "timestamp": datetime.now().isoformat()}
        if HAS_MEMORY:
            try: mem = CyclotronMemory("NerveCenter"); state["memory"] = mem.get_stats(); mem.close()
            except: pass
        if HAS_CHUNKER:
            try: from DATA_CHUNKER import get_stats; state["knowledge"] = get_stats()
            except: pass
        state["consciousness_files"] = len(list(CONSCIOUSNESS.glob("*.py")))
        state["hub_files"] = len(list(HUB.glob("*.json")))
        return state


class BugQueueSensor(SensorInput):
    """Monitors bug queue for new tasks"""
    def __init__(self):
        super().__init__("BugQueue", "task")
        self.last_check = {}
        self.github_api = "https://api.github.com/repos/overkillkulture/consciousness-bugs/issues"

    def _calc_priority(self, bug: Dict) -> str:
        labels = [l.get('name', '').lower() for l in bug.get('labels', [])]
        if any(l in labels for l in ['critical', 'urgent']): return 'URGENT'
        if any(l in labels for l in ['high', 'important']): return 'HIGH'
        return 'LOW' if 'low' in labels else 'NORMAL'

    def _fetch_local_bugs(self) -> List[Dict]:
        bug_dir = CONSCIOUSNESS / ".bug_tasks"
        if not bug_dir.exists(): return []
        bugs = []
        for f in bug_dir.glob("bug_*.json"):
            try:
                bug = json.loads(f.read_text())
                if bug.get('status', 'open') == 'open': bugs.append(bug)
            except: pass
        return bugs

    def _fetch_github_bugs(self) -> List[Dict]:
        try:
            import urllib.request
            token = os.environ.get('GITHUB_TOKEN')
            req = urllib.request.Request(f"{self.github_api}?state=open&per_page=10")
            if token: req.add_header('Authorization', f'token {token}')
            req.add_header('User-Agent', 'Cyclotron')
            with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read().decode())
        except: return []

    def sense(self) -> Optional[Dict]:
        new_bugs = []
        for bug in self._fetch_local_bugs():
            bug_id = bug.get('id', bug.get('number', 'unknown'))
            if f"local_{bug_id}" not in self.last_check:
                self.last_check[f"local_{bug_id}"] = True
                new_bugs.append({'type': 'new_bug', 'source': 'local', 'bug_id': bug_id,
                                'title': bug.get('title', 'Untitled'), 'priority': self._calc_priority(bug)})
        now = time.time()
        if now - self.last_check.get('github_time', 0) > 300:
            self.last_check['github_time'] = now
            for bug in self._fetch_github_bugs():
                bug_id, mtime = bug.get('number'), bug.get('updated_at', '')
                if self.last_check.get(f"github_{bug_id}") != mtime:
                    self.last_check[f"github_{bug_id}"] = mtime
                    new_bugs.append({'type': 'new_bug', 'source': 'github', 'bug_id': bug_id,
                                    'title': bug.get('title', 'Untitled'), 'priority': self._calc_priority(bug)})
        return {"sensor": self.name, "type": self.input_type, "count": len(new_bugs), "bugs": new_bugs} if new_bugs else None


class ClipboardSensor(SensorInput):
    """Monitors clipboard for new content - like tactile sensing."""
    def __init__(self):
        super().__init__("Clipboard", "input"); self.last_content = None

    def sense(self) -> Optional[Dict]:
        try:
            import pyperclip; content = pyperclip.paste()
            if content and content != self.last_content:
                self.last_content = content
                if len(content) > 50:
                    return {"sensor": self.name, "type": self.input_type, "content_preview": content[:200],
                            "content_length": len(content), "timestamp": datetime.now().isoformat()}
        except: pass
        return None


class NerveCenter:
    """Central nervous system for Cyclotron - coordinates sensors and routes to brain agents."""

    def __init__(self, agent_id: str = "C1-NerveCenter"):
        self.agent_id, self.sensors, self.processors = agent_id, {}, []
        self.running, self.cycle_count = False, 0
        self.memory = CyclotronMemory(agent_id) if HAS_MEMORY else None
        self.orchestrator = AgentOrchestrator() if HAS_AGENTS else None
        self.log("Nerve Center initializing...")

    def log(self, msg: str, level: str = "INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] NERVE [{level}]: {msg}")
        with open(NERVE_LOG, "a") as f: f.write(f"{datetime.now().isoformat()} [{level}] {msg}\n")

    def add_sensor(self, sensor: SensorInput):
        self.sensors[sensor.name] = sensor; self.log(f"Added sensor: {sensor.name} ({sensor.input_type})")

    def add_processor(self, processor: Callable): self.processors.append(processor)

    def setup_default_sensors(self):
        self.add_sensor(FileWatchSensor([str(HOME / "100X_DEPLOYMENT"), str(CONSCIOUSNESS), str(HOME / "Desktop")]))
        self.add_sensor(HubMessageSensor()); self.add_sensor(SystemStateSensor()); self.add_sensor(BugQueueSensor())
        try: import pyperclip; self.add_sensor(ClipboardSensor())
        except ImportError: self.log("Clipboard sensor not available", "WARN")

    def process_input(self, sensor_data: Dict):
        sensor_type = sensor_data.get("type", "unknown")
        self.log(f"Processing: {sensor_data.get('sensor')} -> {sensor_type}")
        handlers = {"filesystem": self._handle_file_events, "communication": self._handle_messages,
                    "internal": self._handle_system_state, "input": self._handle_clipboard, "task": self._handle_bugs}
        if h := handlers.get(sensor_type): h(sensor_data)
        if self.memory:
            self.memory.record_episode(task=f"Sensory input: {sensor_type}", action=f"Processed {sensor_data.get('count', 1)} items",
                                       result="Routed", success=True, context=sensor_data, tags=["nerve_center", sensor_type])

    def _handle_file_events(self, data: Dict):
        for event in data.get("events", []):
            path, event_type = event.get("path", ""), event.get("type", "unknown")
            self.log(f"File {event_type}: {Path(path).name}")
            if HAS_CHUNKER and event_type in ["created", "modified"] and Path(path).suffix.lower() in ['.md', '.txt']:
                try:
                    if Path(path).stat().st_size < 50000: self.log(f"Auto-chunking: {Path(path).name}"); process_file(path)
                except Exception as e: self.log(f"Chunk error: {e}", "ERROR")

    def _handle_messages(self, data: Dict):
        for msg in data.get("messages", []):
            msg_type = msg.get("type", "unknown")
            if msg_type == "wake_signal":
                s = msg.get("data", {}); self.log(f"Wake signal for {s.get('wake_target', 'unknown')}: {s.get('reason', 'none')}")
            elif msg_type == "task":
                tasks = msg.get("data", []); self.log(f"Received {len(tasks)} tasks")
                if self.orchestrator and tasks:
                    for task in tasks[:3]:
                        try: state = self.orchestrator.run(task.get("description", str(task))); self.log(f"Agent result: {state.status}")
                        except Exception as e: self.log(f"Agent error: {e}", "ERROR")
            elif msg_type == "broadcast": self.log(f"Broadcast received: {msg.get('data', {}).get('message', '')[:50]}")

    def _handle_system_state(self, data: Dict):
        m, k = data.get("memory", {}), data.get("knowledge", {})
        self.log(f"System state: {m.get('total_episodes', 0)} episodes, {k.get('total_atoms', 0)} atoms")
        status = {"agent": self.agent_id, "cycle": self.cycle_count, "timestamp": datetime.now().isoformat() + "Z",
                  "sensors": list(self.sensors.keys()), "memory": m, "knowledge": k}
        with open(HUB / "NERVE_CENTER_STATUS.json", "w") as f: json.dump(status, f, indent=2)

    def _handle_clipboard(self, data: Dict):
        self.log(f"Clipboard: {data.get('content_length', 0)} chars - {data.get('content_preview', '')[:30]}...")

    def _handle_bugs(self, data: Dict):
        """Handle bug queue events"""
        for bug in data.get("bugs", []):
            bug_id, title, priority = bug.get('bug_id', 'unknown'), bug.get('title', 'Untitled'), bug.get('priority', 'NORMAL')
            self.log(f"BUG [{priority}] #{bug_id}: {title[:50]}...")
            if self.orchestrator:
                try: self.orchestrator.run(f"Bug #{bug_id}: {title}")
                except Exception as e: self.log(f"Agent error: {e}", "ERROR")
            bug_task = {"type": "bug", "bug_id": bug_id, "title": title, "priority": priority,
                        "timestamp": datetime.now().isoformat() + "Z", "status": "detected"}
            with open(HUB / f"bug_detected_{bug_id}.json", "w") as f: json.dump(bug_task, f, indent=2)

    def get_health_status(self) -> Dict:
        """Health check endpoint"""
        health = {"status": "healthy" if self.running else "stopped", "agent_id": self.agent_id,
                  "cycle_count": self.cycle_count, "timestamp": datetime.now().isoformat() + "Z",
                  "sensors": {n: {"type": s.input_type} for n, s in self.sensors.items()},
                  "components": {"memory": self.memory is not None, "orchestrator": self.orchestrator is not None}}
        with open(HUB / "NERVE_CENTER_HEALTH.json", "w") as f: json.dump(health, f, indent=2)
        return health

    def run_cycle(self):
        """Run one sensing cycle."""
        self.cycle_count += 1

        # Update health status every 10 cycles
        if self.cycle_count % 10 == 0:
            self.get_health_status()

        # Poll all sensors
        for name, sensor in self.sensors.items():
            try:
                data = sensor.sense()
                if data:
                    self.process_input(data)
            except Exception as e:
                self.log(f"Sensor {name} error: {e}", "ERROR")

    def run(self, interval: int = 5):
        """Main loop - continuous sensing."""
        self.log(f"NERVE CENTER START | Agent: {self.agent_id} | Sensors: {list(self.sensors.keys())}")
        self.running = True
        file_sensor = self.sensors.get("FileWatcher")
        if file_sensor: file_sensor.start()
        try:
            while self.running:
                self.run_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.log("Stopped by user")
        finally:
            if file_sensor: file_sensor.stop()
            if self.memory: self.memory.close()
            self.log("Shutdown complete")

def main():
    """Main entry point"""
    nerve = NerveCenter()
    nerve.setup_default_sensors()
    nerve.run()

if __name__ == "__main__":
    main()
