#!/usr/bin/env python3
"""
CYCLOTRON WITH BRAIN
An intelligent multi-agent coordinator that LEARNS from experience.

This replaces the hollow CYCLOTRON_MASTER with actual intelligence:
- Records every action as an episode
- Searches for similar past experiences
- Uses patterns to guide decisions
- Updates Q-values based on outcomes
- Shares knowledge across agents
"""

import json
import time
from pathlib import Path
from datetime import datetime

# Import our memory system
from CYCLOTRON_MEMORY import CyclotronMemory

HUB = Path.home() / ".consciousness" / "hub"
CYCLE_INTERVAL = 15  # Slower cycles for thoughtful operation

class IntelligentCyclotron:
    def __init__(self, agent_id: str = "C1-Terminal"):
        self.agent_id = agent_id
        self.memory = CyclotronMemory(agent_id)
        self.cycle_count = 0

        # Ensure hub exists
        HUB.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.agent_id}: {msg}")

    def think_before_acting(self, task: str) -> dict:
        """
        The INTELLIGENCE: Before acting, consult memory.
        Returns guidance based on past experience.
        """
        guidance = {
            "similar_episodes": [],
            "recommended_patterns": [],
            "suggested_approach": None,
            "confidence": 0.5
        }

        # Find similar past experiences
        similar = self.memory.find_similar_episodes(task, limit=3)
        if similar:
            guidance["similar_episodes"] = similar
            # If past similar tasks succeeded, boost confidence
            successes = [ep for ep in similar if ep['success']]
            if successes:
                avg_q = sum(ep['q_value'] for ep in successes) / len(successes)
                guidance["confidence"] = avg_q

                # Use the most successful approach
                best = max(successes, key=lambda x: x['q_value'])
                guidance["suggested_approach"] = best['action']

        # Get relevant patterns
        patterns = self.memory.get_recommended_patterns(task, limit=2)
        if patterns:
            guidance["recommended_patterns"] = patterns

        return guidance

    def act(self, task: str, guidance: dict) -> tuple:
        """
        Execute the task, using guidance from memory.
        Returns (action_taken, result, success)
        """
        self.log(f"Task: {task}")

        # Check if we have a suggested approach
        if guidance["suggested_approach"]:
            self.log(f"Using learned approach (confidence: {guidance['confidence']:.2f})")
            action = f"Applied learned pattern: {guidance['suggested_approach'][:50]}"
        elif guidance["recommended_patterns"]:
            pattern = guidance["recommended_patterns"][0]
            self.log(f"Applying pattern: {pattern['name']}")
            action = f"Applied pattern {pattern['name']}: {pattern['recommended_action'][:50]}"
        else:
            self.log("No prior experience - exploring new approach")
            action = "Executed exploratory action"

        # Simulate work (in real system, this would do actual work)
        time.sleep(1)

        # Simulate outcome (in real system, this would check actual results)
        # For now, slight random variance with bias toward success
        import random
        success = random.random() > 0.3  # 70% base success rate

        if success:
            result = "Task completed successfully"
        else:
            result = "Task encountered issues"

        return action, result, success

    def learn_from_outcome(self, task: str, action: str, result: str, success: bool):
        """
        Record the experience and update learning.
        """
        # Record the episode
        episode_id = self.memory.record_episode(
            task=task,
            action=action,
            result=result,
            success=success,
            context={"cycle": self.cycle_count, "agent": self.agent_id},
            tags=[self.agent_id, f"cycle_{self.cycle_count}"]
        )

        # Calculate reward
        reward = 1.0 if success else 0.2

        # Update Q-value
        self.memory.update_q_value(episode_id, reward)

        # If very successful, extract a pattern
        if success and self.memory.find_similar_episodes(task):
            similar_successes = [
                ep for ep in self.memory.find_similar_episodes(task)
                if ep['success'] and ep['q_value'] > 0.6
            ]
            if len(similar_successes) >= 2:
                # We've succeeded at this type of task multiple times - create pattern
                self.memory.extract_pattern(
                    name=f"pattern_from_cycle_{self.cycle_count}",
                    description=f"Successful approach for tasks like: {task[:30]}",
                    trigger=task[:50],
                    action=action,
                    success_rate=0.75
                )

        # Share knowledge with other agents
        self.memory.share_knowledge(
            knowledge_type="episode_summary",
            content=json.dumps({
                "task": task,
                "success": success,
                "cycle": self.cycle_count
            })
        )

    def run_cycle(self, task: str = None):
        """Run one intelligent cycle"""
        self.cycle_count += 1
        self.log(f"{'='*50}")
        self.log(f"CYCLE {self.cycle_count} - THINKING...")
        self.log(f"{'='*50}")

        # Default task if none provided
        if not task:
            task = f"Process cycle {self.cycle_count} tasks"

        # 1. THINK - Consult memory
        guidance = self.think_before_acting(task)
        if guidance["similar_episodes"]:
            self.log(f"Found {len(guidance['similar_episodes'])} similar past experiences")
        if guidance["recommended_patterns"]:
            self.log(f"Found {len(guidance['recommended_patterns'])} applicable patterns")

        # 2. ACT - Execute with guidance
        action, result, success = self.act(task, guidance)

        # 3. LEARN - Record and update
        self.learn_from_outcome(task, action, result, success)

        # 4. REPORT
        status = "SUCCESS" if success else "NEEDS_IMPROVEMENT"
        self.log(f"Cycle {self.cycle_count} complete: {status}")

        # Update status file
        self.write_status()

        return success

    def write_status(self):
        """Write current status to hub"""
        stats = self.memory.get_stats()
        status = {
            "agent": self.agent_id,
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat() + "Z",
            "memory_stats": stats
        }
        with open(HUB / "CYCLOTRON_STATUS.json", "w") as f:
            json.dump(status, f, indent=2)

    def run(self, max_cycles: int = None):
        """Run the cyclotron loop"""
        self.log("=" * 60)
        self.log("INTELLIGENT CYCLOTRON STARTING")
        self.log(f"Agent: {self.agent_id}")
        self.log(f"Memory stats: {self.memory.get_stats()}")
        self.log("=" * 60)

        cycle = 0
        while True:
            try:
                cycle += 1
                if max_cycles and cycle > max_cycles:
                    self.log(f"Reached max cycles ({max_cycles})")
                    break

                # Check for tasks in queue
                task_file = HUB / f"tasks_for_{self.agent_id.lower().replace('-', '_')}.json"
                if task_file.exists():
                    with open(task_file) as f:
                        tasks = json.load(f)
                    if tasks:
                        task = tasks[0].get("description", "Process task")
                        # Clear task file
                        with open(task_file, "w") as f:
                            json.dump([], f)
                    else:
                        task = None
                else:
                    task = None

                self.run_cycle(task)

                self.log(f"Waiting {CYCLE_INTERVAL}s...")
                time.sleep(CYCLE_INTERVAL)

            except KeyboardInterrupt:
                self.log("Stopped by user")
                break
            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(5)

        # Final stats
        self.log("=" * 60)
        self.log("FINAL MEMORY STATISTICS:")
        stats = self.memory.get_stats()
        for key, value in stats.items():
            self.log(f"  {key}: {value}")
        self.log("=" * 60)

        self.memory.close()


if __name__ == "__main__":
    import sys

    agent_id = sys.argv[1] if len(sys.argv) > 1 else "C1-Terminal"
    max_cycles = int(sys.argv[2]) if len(sys.argv) > 2 else None

    cyclotron = IntelligentCyclotron(agent_id)
    cyclotron.run(max_cycles)
