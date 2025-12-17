#!/usr/bin/env python3
"""
CYCLOTRON GUARDIAN
A persistent, intelligent watcher powered by local LLM (Ollama).

This is the "smart watcher" that:
- Runs 24/7 in the background
- Monitors the Cyclotron health
- Makes intelligent decisions about interventions
- Can escalate to Claude when needed
- Learns from its own observations

Uses: Ollama with qwen2.5-coder or mistral for local intelligence
"""

import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

# Configuration
HUB = Path.home() / ".consciousness" / "hub"
MEMORY_DIR = Path.home() / ".consciousness" / "memory"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"  # Fast and smart for coding tasks
CHECK_INTERVAL = 30  # Check every 30 seconds
ESCALATION_THRESHOLD = 3  # Escalate after 3 consecutive issues

class CyclotronGuardian:
    def __init__(self):
        self.issues_count = 0
        self.last_healthy = datetime.now()
        self.observations = []
        self.log_file = MEMORY_DIR / "guardian_log.jsonl"

        # Ensure directories exist
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        HUB.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] GUARDIAN [{level}]: {msg}")

        # Also write to log file
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": msg
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def check_ollama(self) -> bool:
        """Verify Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.RequestException, OSError):
            return False

    def ask_llm(self, prompt: str, context: str = "") -> Optional[str]:
        """Ask the local LLM for intelligent analysis"""
        full_prompt = f"""You are the Cyclotron Guardian, monitoring an AI coordination system.

Context: {context}

Question: {prompt}

Respond concisely (1-3 sentences). Focus on actionable insights."""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            self.log(f"LLM query failed: {e}", "WARN")
        return None

    def get_cyclotron_status(self) -> Dict:
        """Read current Cyclotron status"""
        status_file = HUB / "CYCLOTRON_STATUS.json"
        if status_file.exists():
            try:
                with open(status_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def get_memory_stats(self) -> Dict:
        """Get memory database stats"""
        db_path = MEMORY_DIR / "cyclotron_brain.db"
        if not db_path.exists():
            return {"exists": False}

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM episodes")
            episodes = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(q_value) FROM episodes")
            avg_q = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM episodes WHERE success = 1")
            successes = cursor.fetchone()[0]

            conn.close()

            return {
                "exists": True,
                "episodes": episodes,
                "avg_q_value": round(avg_q, 3),
                "successes": successes,
                "success_rate": round(successes / episodes, 2) if episodes > 0 else 0
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}

    def check_health(self) -> tuple:
        """
        Check overall system health.
        Returns (is_healthy, issues_list)
        """
        issues = []

        # Check Cyclotron status
        status = self.get_cyclotron_status()
        if not status:
            issues.append("No Cyclotron status file found")
        else:
            # Check if status is stale (older than 2 minutes)
            try:
                last_update = datetime.fromisoformat(status.get("timestamp", "").replace("Z", ""))
                age = datetime.now() - last_update
                if age > timedelta(minutes=2):
                    issues.append(f"Cyclotron status is stale ({age.seconds}s old)")
            except (ValueError, TypeError):
                issues.append("Cannot parse Cyclotron timestamp")

        # Check memory stats
        mem_stats = self.get_memory_stats()
        if not mem_stats.get("exists"):
            issues.append("Memory database not found")
        elif mem_stats.get("error"):
            issues.append(f"Memory database error: {mem_stats['error']}")
        elif mem_stats.get("success_rate", 1) < 0.3:
            issues.append(f"Low success rate: {mem_stats['success_rate']}")

        # Check hub files
        wake_signal = HUB / "WAKE_SIGNAL.json"
        if not wake_signal.exists():
            issues.append("No wake signal file")

        return len(issues) == 0, issues

    def analyze_situation(self, issues: list) -> str:
        """Use LLM to analyze the situation"""
        context = f"""
Current issues detected: {issues}
Memory stats: {self.get_memory_stats()}
Cyclotron status: {self.get_cyclotron_status()}
Time since last healthy: {datetime.now() - self.last_healthy}
"""

        analysis = self.ask_llm(
            "What's wrong and what should we do about it?",
            context
        )
        return analysis or "Unable to analyze (LLM unavailable)"

    def attempt_recovery(self, issues: list) -> bool:
        """Attempt automatic recovery actions"""
        self.log("Attempting automatic recovery...", "WARN")

        for issue in issues:
            if "stale" in issue.lower():
                # Cyclotron might have stopped - check if process exists
                self.log("Checking if Cyclotron process is running...")
                # Could add process restart logic here

            if "memory database not found" in issue.lower():
                # Initialize memory
                self.log("Initializing memory database...")
                try:
                    from CYCLOTRON_MEMORY import ensure_memory_exists
                    ensure_memory_exists()
                    self.log("Memory database initialized", "INFO")
                except Exception as e:
                    self.log(f"Failed to init memory: {e}", "ERROR")

            if "wake signal" in issue.lower():
                # Create default wake signal with all required fields
                self.log("Creating default wake signal...")
                signal = {
                    "wake_target": "C1-Terminal",
                    "reason": "Guardian recovery",
                    "priority": "NORMAL",
                    "from": "Guardian",
                    "timestamp": datetime.now().isoformat() + "Z",
                    "loop_number": 0,
                    "convergence_level": 0,
                    "task_context": {
                        "previous_instance": "Guardian",
                        "last_action": "Recovery signal",
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
                }
                with open(HUB / "WAKE_SIGNAL.json", "w") as f:
                    json.dump(signal, f, indent=2)

        # Check if recovery helped
        time.sleep(5)
        is_healthy, remaining_issues = self.check_health()
        return is_healthy

    def escalate(self, issues: list, analysis: str):
        """Escalate to human/Claude when Guardian can't fix it"""
        self.log("ESCALATING - Issues beyond automatic recovery", "ERROR")

        escalation = {
            "timestamp": datetime.now().isoformat() + "Z",
            "issues": issues,
            "analysis": analysis,
            "guardian_attempts": self.issues_count,
            "requires_human": True
        }

        escalation_file = HUB / "ESCALATION_NEEDED.json"
        with open(escalation_file, "w") as f:
            json.dump(escalation, f, indent=2)

        self.log(f"Escalation written to {escalation_file}", "ERROR")

        # Could also send notification here (email, webhook, etc.)

    def run(self):
        """Main guardian loop"""
        self.log("=" * 60)
        self.log("CYCLOTRON GUARDIAN STARTING")
        self.log(f"Model: {MODEL}")
        self.log(f"Check interval: {CHECK_INTERVAL}s")
        self.log("=" * 60)

        # Check Ollama
        if not self.check_ollama():
            self.log("WARNING: Ollama not available - running in limited mode", "WARN")
        else:
            self.log("Ollama connected - full intelligence available")

        while True:
            try:
                # Check health
                is_healthy, issues = self.check_health()

                if is_healthy:
                    if self.issues_count > 0:
                        self.log("System recovered - back to healthy state")
                    self.issues_count = 0
                    self.last_healthy = datetime.now()

                    # Periodic status report
                    mem_stats = self.get_memory_stats()
                    self.log(f"Healthy | Episodes: {mem_stats.get('episodes', '?')} | Success rate: {mem_stats.get('success_rate', '?')}")

                else:
                    self.issues_count += 1
                    self.log(f"Issues detected ({self.issues_count}/{ESCALATION_THRESHOLD}): {issues}", "WARN")

                    # Get LLM analysis
                    analysis = self.analyze_situation(issues)
                    self.log(f"Analysis: {analysis}", "WARN")

                    # Attempt recovery
                    if self.attempt_recovery(issues):
                        self.log("Recovery successful!")
                        self.issues_count = 0
                    elif self.issues_count >= ESCALATION_THRESHOLD:
                        self.escalate(issues, analysis)
                        self.issues_count = 0  # Reset after escalation

                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                self.log("Guardian stopped by user")
                break
            except Exception as e:
                self.log(f"Guardian error: {e}", "ERROR")
                time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    guardian = CyclotronGuardian()
    guardian.run()
