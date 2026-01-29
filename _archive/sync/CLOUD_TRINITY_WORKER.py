#!/usr/bin/env python3
"""CLOUD TRINITY WORKER - Autonomous Claude API workers for Trinity background tasks.
Uses Haiku/Sonnet/Opus for research, monitoring, code generation, parallel processing."""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import threading

# Add consciousness path
sys.path.insert(0, str(Path.home() / ".consciousness"))

# Try to import Anthropic
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("[CLOUD] Warning: anthropic package not installed. Run: pip install anthropic")

# Paths
HOME = Path.home()
TRINITY_DIR = HOME / ".trinity"
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
CLOUD_DIR = TRINITY_DIR / "cloud_workers"

# Ensure directories
TRINITY_DIR.mkdir(parents=True, exist_ok=True)
CLOUD_DIR.mkdir(parents=True, exist_ok=True)
HUB.mkdir(parents=True, exist_ok=True)


class CloudTrinityWorker:
    """Cloud Trinity worker using Claude API. Roles: C1=Mechanic, C2=Architect, C3=Oracle"""
    ROLE_PROMPTS = {
        "C1-Cloud": "You are C1-Cloud, the Mechanic. Execute tasks, fix bugs, write code. BUILD what CAN be built NOW.",
        "C2-Cloud": "You are C2-Cloud, the Architect. Design systems, review architecture. DESIGN what SHOULD scale.",
        "C3-Cloud": "You are C3-Cloud, the Oracle. Analyze patterns, research, provide vision. SEE what MUST emerge."
    }

    def __init__(self, instance_id: str, model: str = "claude-sonnet-4-20250514"):
        self.instance_id, self.model, self.running, self.tasks_completed = instance_id, model, False, 0
        self.client = None
        if HAS_ANTHROPIC:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key: self.client = anthropic.Anthropic(api_key=api_key)
            else: print("[CLOUD] Warning: ANTHROPIC_API_KEY not set")
        self.role_prompt = self.ROLE_PROMPTS.get(instance_id, self.ROLE_PROMPTS["C2-Cloud"])
        self.log(f"Initialized with model {model}")

    def log(self, msg: str, level: str = "INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{self.instance_id}] {msg}")
        with open(CLOUD_DIR / f"{self.instance_id}.log", "a") as f: f.write(f"{datetime.now().isoformat()} [{level}] {msg}\n")

    def read_tasks_file(self) -> List[Dict]:
        try: return json.load(open(TRINITY_DIR / "tasks.json")) if (TRINITY_DIR / "tasks.json").exists() else []
        except: return []

    def write_tasks_file(self, tasks: List[Dict]):
        with open(TRINITY_DIR / "tasks.json", "w") as f: json.dump(tasks, f, indent=2)

    def claim_task(self) -> Optional[Dict]:
        """Claim an available task"""
        tasks = self.read_tasks_file()

        # Find tasks assigned to this instance or "any"
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        available = [
            t for t in tasks
            if t.get("status") == "assigned" and
            (t.get("assignedTo") == self.instance_id or
             t.get("assignedTo") == "any" or
             t.get("assignedTo") == "cloud")  # Generic cloud assignment
        ]

        if not available:
            return None

        # Sort by priority
        available.sort(key=lambda t: priority_order.get(t.get("priority", "normal"), 2))

        # Claim first task
        task = available[0]
        task_id = task["id"]

        # Update status
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "in-progress"
                t["claimedBy"] = self.instance_id
                t["claimedAt"] = datetime.utcnow().isoformat() + "Z"
                break

        self.write_tasks_file(tasks)
        self.log(f"Claimed task: {task.get('task', '')[:50]}...")

        return task

    def submit_output(self, task_id: str, output: str):
        """Submit task output"""
        tasks = self.read_tasks_file()

        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "completed"
                t["output"] = output
                t["completedBy"] = self.instance_id
                t["completedAt"] = datetime.utcnow().isoformat() + "Z"
                break

        self.write_tasks_file(tasks)

        # Also write to outputs file
        outputs_file = TRINITY_DIR / "outputs.json"
        try:
            outputs = json.load(open(outputs_file)) if outputs_file.exists() else []
        except:
            outputs = []

        outputs.append({
            "taskId": task_id,
            "instanceId": self.instance_id,
            "output": output,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        with open(outputs_file, "w") as f:
            json.dump(outputs, f, indent=2)

        self.log(f"Submitted output for task {task_id}")

    def execute_task(self, task: Dict) -> str:
        """Execute a task using Claude API"""
        if not self.client:
            return "ERROR: No API client available"

        task_description = task.get("task", "")
        task_context = task.get("context", {})

        # Build the prompt
        system_prompt = f"""{self.role_prompt}

CURRENT TASK: {task_description}

CONTEXT:
{json.dumps(task_context, indent=2) if task_context else "No additional context"}

INSTRUCTIONS:
1. Analyze the task carefully
2. Execute it to the best of your ability
3. Provide a clear, actionable response
4. If you need more information, state what's missing
5. Be concise but thorough
"""

        try:
            self.log(f"Executing task with {self.model}...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": task_description}
                ]
            )

            output = response.content[0].text
            self.log(f"Task completed, output length: {len(output)}")
            return output

        except Exception as e:
            error_msg = f"ERROR executing task: {str(e)}"
            self.log(error_msg, "ERROR")
            return error_msg

    def write_heartbeat(self):
        """Write heartbeat to hub"""
        heartbeat_file = HUB / f"heartbeat_{self.instance_id.lower().replace('-', '_')}.json"
        heartbeat = {
            "instance": self.instance_id,
            "alive": True,
            "last_beat": datetime.utcnow().isoformat() + "Z",
            "tasks_completed": self.tasks_completed,
            "model": self.model
        }
        with open(heartbeat_file, "w") as f:
            json.dump(heartbeat, f, indent=2)

    def run(self, poll_interval: int = 10, max_tasks: int = None):
        """
        Main worker loop.

        Args:
            poll_interval: Seconds between task checks
            max_tasks: Maximum tasks to complete (None = unlimited)
        """
        self.running = True
        self.log("=" * 50)
        self.log(f"CLOUD WORKER STARTING")
        self.log(f"Instance: {self.instance_id}")
        self.log(f"Model: {self.model}")
        self.log(f"API Client: {'Ready' if self.client else 'NOT AVAILABLE'}")
        self.log("=" * 50)

        if not self.client:
            self.log("Cannot start without API client", "ERROR")
            return

        try:
            while self.running:
                # Write heartbeat
                self.write_heartbeat()

                # Check for tasks
                task = self.claim_task()

                if task:
                    # Execute task
                    output = self.execute_task(task)

                    # Submit output
                    self.submit_output(task["id"], output)

                    self.tasks_completed += 1

                    # Check max tasks
                    if max_tasks and self.tasks_completed >= max_tasks:
                        self.log(f"Completed {max_tasks} tasks, stopping")
                        break
                else:
                    self.log("No tasks available, waiting...")

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            self.log("Stopped by user")
        finally:
            self.running = False
            self.log("Worker shutdown complete")


class CloudWorkerPool:
    """
    Manages multiple cloud workers for parallel processing.
    """

    def __init__(self):
        self.workers: Dict[str, CloudTrinityWorker] = {}

    def add_worker(self, instance_id: str, model: str = "claude-sonnet-4-20250514"):
        """Add a worker to the pool"""
        worker = CloudTrinityWorker(instance_id, model)
        self.workers[instance_id] = worker
        return worker

    def start_all(self, poll_interval: int = 10):
        """Start all workers in separate threads"""
        threads = []
        for worker in self.workers.values():
            t = threading.Thread(
                target=worker.run,
                args=(poll_interval,),
                daemon=True
            )
            t.start()
            threads.append(t)
        return threads

    def stop_all(self):
        """Stop all workers"""
        for worker in self.workers.values():
            worker.running = False


# ========================================
# CLOUD TASK DEFINITIONS
# ========================================

CLOUD_TASK_TEMPLATES = {
    "research": {
        "description": "Research a topic and provide comprehensive summary",
        "assignedTo": "C3-Cloud",
        "priority": "normal"
    },
    "code_review": {
        "description": "Review code for bugs, security issues, and improvements",
        "assignedTo": "C2-Cloud",
        "priority": "normal"
    },
    "implementation": {
        "description": "Implement a feature or fix",
        "assignedTo": "C1-Cloud",
        "priority": "normal"
    },
    "architecture": {
        "description": "Design system architecture",
        "assignedTo": "C2-Cloud",
        "priority": "high"
    },
    "pattern_analysis": {
        "description": "Analyze patterns and provide insights",
        "assignedTo": "C3-Cloud",
        "priority": "normal"
    },
    "monitoring": {
        "description": "Monitor system health and report issues",
        "assignedTo": "cloud",  # Any cloud worker
        "priority": "low"
    }
}


def create_cloud_task(task_type: str, details: str, priority: str = None) -> Dict:
    """Create a task for cloud workers"""
    template = CLOUD_TASK_TEMPLATES.get(task_type, CLOUD_TASK_TEMPLATES["research"])

    task = {
        "id": f"{int(time.time())}-{hashlib.md5(details.encode()).hexdigest()[:8]}",
        "task": f"{template['description']}: {details}",
        "assignedTo": template["assignedTo"],
        "priority": priority or template["priority"],
        "status": "assigned",
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "type": task_type
    }

    # Add to tasks file
    tasks_file = TRINITY_DIR / "tasks.json"
    try:
        tasks = json.load(open(tasks_file)) if tasks_file.exists() else []
    except:
        tasks = []

    tasks.append(task)

    with open(tasks_file, "w") as f:
        json.dump(tasks, f, indent=2)

    return task


# Use cases: Research(C3), CodeReview(C1), Architecture(C2), Monitoring(any), ParallelProcessing


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cloud Trinity Worker")
    parser.add_argument("--instance", default="C3-Cloud",
                       choices=["C1-Cloud", "C2-Cloud", "C3-Cloud"],
                       help="Instance ID")
    parser.add_argument("--model", default="claude-sonnet-4-20250514",
                       help="Claude model to use")
    parser.add_argument("--poll", type=int, default=10,
                       help="Poll interval in seconds")
    parser.add_argument("--max-tasks", type=int, default=None,
                       help="Max tasks before stopping")
    parser.add_argument("--test", action="store_true",
                       help="Create a test task and exit")

    args = parser.parse_args()

    if args.test:
        # Create a test task
        task = create_cloud_task(
            "research",
            "What are the best practices for Claude API usage in 2025?",
            "normal"
        )
        print(f"Created test task: {task['id']}")
        print(json.dumps(task, indent=2))
    else:
        # Start worker
        worker = CloudTrinityWorker(args.instance, args.model)
        worker.run(args.poll, args.max_tasks)
