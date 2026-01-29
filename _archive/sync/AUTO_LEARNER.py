#!/usr/bin/env python3
"""AUTO LEARNER - Automatic Q-value updates based on outcome detection.
Q-Learning: Q(s,a) = Q(s,a) + α(reward - Q(s,a))"""

import json
import sqlite3
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re

# Paths
CONSCIOUSNESS = Path.home() / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
MEMORY_DB = CONSCIOUSNESS / "memory" / "cyclotron_brain.db"


class OutcomeType(Enum):
    """Types of task outcomes"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class OutcomeSignal:
    """Signal indicating task outcome"""
    episode_id: str
    outcome: OutcomeType
    reward: float
    reason: str
    timestamp: str
    source: str  # Where the signal came from

    def to_dict(self) -> dict:
        return {
            'episode_id': self.episode_id,
            'outcome': self.outcome.value,
            'reward': self.reward,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'source': self.source
        }


class OutcomeDetector:
    """Detects task outcomes from various signals"""

    def __init__(self):
        self.reward_map = {
            OutcomeType.SUCCESS: 1.0,
            OutcomeType.PARTIAL: 0.6,
            OutcomeType.FAILURE: 0.2,
            OutcomeType.ERROR: 0.1,
            OutcomeType.TIMEOUT: 0.3,
            OutcomeType.UNKNOWN: 0.5
        }

        # Patterns for detecting outcomes in text
        self.success_patterns = [
            r'complete[d]?',
            r'success(ful)?',
            r'fixed',
            r'resolved',
            r'working',
            r'passed',
            r'deployed',
            r'done'
        ]

        self.failure_patterns = [
            r'fail(ed|ure)?',
            r'error',
            r'broken',
            r'crash(ed)?',
            r'bug',
            r'issue',
            r'problem'
        ]

    def detect_from_text(self, text: str) -> OutcomeType:
        """Detect outcome from text content"""
        text_lower = text.lower()

        success_count = sum(1 for p in self.success_patterns if re.search(p, text_lower))
        failure_count = sum(1 for p in self.failure_patterns if re.search(p, text_lower))

        if success_count > failure_count + 1:
            return OutcomeType.SUCCESS
        elif failure_count > success_count + 1:
            return OutcomeType.FAILURE
        elif success_count > 0 and failure_count > 0:
            return OutcomeType.PARTIAL
        else:
            return OutcomeType.UNKNOWN

    def detect_from_hub_file(self, file_path: Path) -> Optional[OutcomeSignal]:
        """Detect outcome from hub file changes"""
        try:
            with open(file_path) as f:
                data = json.load(f)

            # Look for outcome indicators
            status = data.get('status', '').lower()
            result = data.get('result', '').lower()
            output = data.get('output', '').lower()

            combined_text = f"{status} {result} {output}"
            outcome = self.detect_from_text(combined_text)

            episode_id = data.get('episode_id', data.get('task_id', file_path.stem))

            return OutcomeSignal(
                episode_id=episode_id,
                outcome=outcome,
                reward=self.reward_map[outcome],
                reason=f"Detected from {file_path.name}: {combined_text[:50]}",
                timestamp=datetime.now().isoformat(),
                source=str(file_path)
            )

        except Exception as e:
            return None

    def detect_from_synthesis(self, synthesis: Dict) -> OutcomeType:
        """Detect outcome from synthesis results"""
        confidence = synthesis.get('confidence', 0.5)

        if confidence >= 0.8:
            return OutcomeType.SUCCESS
        elif confidence >= 0.6:
            return OutcomeType.PARTIAL
        elif confidence >= 0.4:
            return OutcomeType.UNKNOWN
        else:
            return OutcomeType.FAILURE


class AutoLearner:
    """
    Automatic learning system that updates Q-values based on outcomes.

    Features:
    - Monitor hub for completion signals
    - Detect outcomes from various sources
    - Update Q-values automatically
    - Extract patterns from successful episodes
    - Track learning statistics
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.detector = OutcomeDetector()
        self.pending_episodes: Dict[str, Dict] = {}  # Episodes awaiting outcomes
        self.learning_history: List[Dict] = []
        self.patterns_extracted = 0

        # Statistics
        self.updates_made = 0
        self.success_count = 0
        self.failure_count = 0

        # Callbacks
        self.on_learn_callbacks: List[Callable] = []

    def register_episode(self, episode_id: str, task: str, action: str,
                        context: Dict = None):
        """Register an episode for outcome tracking"""
        self.pending_episodes[episode_id] = {
            'episode_id': episode_id,
            'task': task,
            'action': action,
            'context': context or {},
            'registered_at': datetime.now().isoformat()
        }
        print(f"[AUTO_LEARNER] Registered episode {episode_id} for tracking")

    def process_outcome(self, signal: OutcomeSignal):
        """Process an outcome signal and update Q-value"""
        if not MEMORY_DB.exists():
            print("[AUTO_LEARNER] Memory DB not found")
            return

        try:
            conn = sqlite3.connect(MEMORY_DB)
            cursor = conn.cursor()

            # Get current Q-value
            cursor.execute(
                "SELECT q_value, success FROM episodes WHERE id = ?",
                (signal.episode_id,)
            )
            row = cursor.fetchone()

            if not row:
                print(f"[AUTO_LEARNER] Episode {signal.episode_id} not found in DB")
                conn.close()
                return

            old_q = row[0] or 0.5
            old_success = row[1]

            # Q-learning update
            new_q = old_q + self.learning_rate * (signal.reward - old_q)
            new_q = max(0.0, min(1.0, new_q))

            # Update success flag based on outcome
            new_success = 1 if signal.outcome == OutcomeType.SUCCESS else (
                old_success if signal.outcome == OutcomeType.PARTIAL else 0
            )

            # Apply update
            cursor.execute('''
                UPDATE episodes
                SET q_value = ?, success = ?
                WHERE id = ?
            ''', (new_q, new_success, signal.episode_id))

            conn.commit()
            conn.close()

            # Track statistics
            self.updates_made += 1
            if signal.outcome == OutcomeType.SUCCESS:
                self.success_count += 1
            elif signal.outcome in [OutcomeType.FAILURE, OutcomeType.ERROR]:
                self.failure_count += 1

            # Record in history
            self.learning_history.append({
                'episode_id': signal.episode_id,
                'old_q': old_q,
                'new_q': new_q,
                'reward': signal.reward,
                'outcome': signal.outcome.value,
                'timestamp': signal.timestamp
            })

            print(f"[AUTO_LEARNER] Updated {signal.episode_id}: Q {old_q:.2f} -> {new_q:.2f} ({signal.outcome.value})")

            # Check for pattern extraction
            if signal.outcome == OutcomeType.SUCCESS and new_q >= 0.7:
                self._maybe_extract_pattern(signal.episode_id)

            # Fire callbacks
            for callback in self.on_learn_callbacks:
                try:
                    callback(signal)
                except:
                    pass

            # Remove from pending
            if signal.episode_id in self.pending_episodes:
                del self.pending_episodes[signal.episode_id]

        except Exception as e:
            print(f"[AUTO_LEARNER] Error processing outcome: {e}")

    def _maybe_extract_pattern(self, episode_id: str):
        """Extract a pattern from a highly successful episode"""
        if not MEMORY_DB.exists():
            return

        try:
            conn = sqlite3.connect(MEMORY_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT task, action, result, q_value FROM episodes WHERE id = ?",
                (episode_id,)
            )
            row = cursor.fetchone()

            if not row:
                conn.close()
                return

            # Check if similar pattern already exists
            cursor.execute(
                "SELECT id FROM patterns WHERE name LIKE ?",
                (f"%{row['task'][:20]}%",)
            )

            if cursor.fetchone():
                conn.close()
                return

            # Extract keywords for trigger
            keywords = [w for w in row['task'].lower().split() if len(w) > 3][:5]
            trigger = ', '.join(keywords)

            # Create pattern
            import hashlib
            pattern_id = hashlib.sha256(f"{row['task']}{datetime.now()}".encode()).hexdigest()[:12]

            cursor.execute('''
                INSERT INTO patterns
                (id, name, description, trigger_conditions, recommended_action, success_rate, times_used, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id,
                f"auto_pattern_{pattern_id[:6]}",
                f"Auto-extracted from successful episode: {row['task'][:50]}",
                trigger,
                row['action'][:200] if row['action'] else 'Follow successful episode approach',
                row['q_value'],
                1,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            self.patterns_extracted += 1
            print(f"[AUTO_LEARNER] Extracted pattern from episode {episode_id}")

        except Exception as e:
            print(f"[AUTO_LEARNER] Error extracting pattern: {e}")

    def scan_hub_for_outcomes(self) -> List[OutcomeSignal]:
        """Scan hub for outcome signals"""
        signals = []

        if not HUB.exists():
            return signals

        # Check output files
        for output_file in HUB.glob("output_*.json"):
            signal = self.detector.detect_from_hub_file(output_file)
            if signal:
                signals.append(signal)

        # Check task completion files
        for task_file in HUB.glob("task_complete_*.json"):
            signal = self.detector.detect_from_hub_file(task_file)
            if signal:
                signals.append(signal)

        # Check status files
        for status_file in HUB.glob("*_status.json"):
            signal = self.detector.detect_from_hub_file(status_file)
            if signal:
                signals.append(signal)

        return signals

    def process_synthesis_outcome(self, episode_id: str, synthesis: Dict):
        """Process outcome from synthesis results"""
        outcome = self.detector.detect_from_synthesis(synthesis)
        reward = self.detector.reward_map[outcome]

        signal = OutcomeSignal(
            episode_id=episode_id,
            outcome=outcome,
            reward=reward,
            reason=f"Synthesis confidence: {synthesis.get('confidence', 0):.0%}",
            timestamp=datetime.now().isoformat(),
            source="synthesis"
        )

        self.process_outcome(signal)

    def learn_from_user_feedback(self, episode_id: str, feedback: str):
        """Learn from explicit user feedback"""
        feedback_lower = feedback.lower()

        if any(w in feedback_lower for w in ['good', 'great', 'perfect', 'works', 'thanks']):
            outcome = OutcomeType.SUCCESS
            reward = 1.0
        elif any(w in feedback_lower for w in ['ok', 'fine', 'acceptable']):
            outcome = OutcomeType.PARTIAL
            reward = 0.7
        elif any(w in feedback_lower for w in ['bad', 'wrong', 'broken', 'fail']):
            outcome = OutcomeType.FAILURE
            reward = 0.2
        else:
            outcome = OutcomeType.UNKNOWN
            reward = 0.5

        signal = OutcomeSignal(
            episode_id=episode_id,
            outcome=outcome,
            reward=reward,
            reason=f"User feedback: {feedback[:50]}",
            timestamp=datetime.now().isoformat(),
            source="user_feedback"
        )

        self.process_outcome(signal)

    def get_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            'updates_made': self.updates_made,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': f"{self.success_count / max(1, self.updates_made):.0%}",
            'patterns_extracted': self.patterns_extracted,
            'pending_episodes': len(self.pending_episodes),
            'history_length': len(self.learning_history)
        }

    def on_learn(self, callback: Callable):
        """Register callback for learning events"""
        self.on_learn_callbacks.append(callback)


class AutoLearnerDaemon:
    """Daemon that runs auto-learning continuously"""

    def __init__(self, learner: AutoLearner, interval: int = 30):
        self.learner = learner
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Start the daemon"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[AUTO_LEARNER] Daemon started (interval: {self.interval}s)")

    def stop(self):
        """Stop the daemon"""
        self.running = False
        print("[AUTO_LEARNER] Daemon stopped")

    def _run_loop(self):
        """Main daemon loop"""
        while self.running:
            try:
                # Scan for outcomes
                signals = self.learner.scan_hub_for_outcomes()

                for signal in signals:
                    self.learner.process_outcome(signal)

                # Check timeout on pending episodes (5 min)
                timeout = datetime.now() - timedelta(minutes=5)
                timed_out = []

                for ep_id, ep_data in self.learner.pending_episodes.items():
                    reg_time = datetime.fromisoformat(ep_data['registered_at'])
                    if reg_time < timeout:
                        timed_out.append(ep_id)

                for ep_id in timed_out:
                    signal = OutcomeSignal(
                        episode_id=ep_id,
                        outcome=OutcomeType.TIMEOUT,
                        reward=0.3,
                        reason="Episode timed out (5 min)",
                        timestamp=datetime.now().isoformat(),
                        source="timeout_check"
                    )
                    self.learner.process_outcome(signal)

            except Exception as e:
                print(f"[AUTO_LEARNER] Daemon error: {e}")

            time.sleep(self.interval)


def demo():
    """Quick demo of auto-learner"""
    learner = AutoLearner(learning_rate=0.15)
    print(f"AUTO_LEARNER ready. Stats: {learner.get_stats()}")

if __name__ == "__main__":
    demo()
