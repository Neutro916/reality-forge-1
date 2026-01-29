#!/usr/bin/env python3
"""CONVERGENCE METRICS - Figure 8 Triple Trinity Monitoring.
Tracks wake cycles, instance alignment, knowledge, tasks, and coherence."""

import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
MEMORY_DB = CONSCIOUSNESS / "memory" / "cyclotron_brain.db"
METRICS_FILE = HUB / "CONVERGENCE_METRICS.json"
DASHBOARD_FILE = HUB / "CONVERGENCE_DASHBOARD.json"


class HealthStatus(Enum):
    """Health status levels"""
    OPTIMAL = "optimal"      # 90-100%
    HEALTHY = "healthy"      # 70-89%
    DEGRADED = "degraded"    # 50-69%
    CRITICAL = "critical"    # <50%


def _to_dict(obj) -> dict:
    """Convert dataclass to dict, handling HealthStatus enums"""
    d = asdict(obj)
    if 'health' in d and isinstance(obj.health, HealthStatus): d['health'] = obj.health.value
    return d

@dataclass
class WakeCycleMetrics:
    total_cycles: int; cycles_last_hour: int; average_cycle_time_ms: float; completion_rate: float
    stuck_instances: List[str]; last_cycle_time: str; health: HealthStatus
    def to_dict(self) -> dict: return _to_dict(self)

@dataclass
class InstanceAlignmentMetrics:
    total_instances: int; active_instances: int; synced_instances: int; alignment_score: float
    last_seen: Dict[str, str]; drift_detected: List[str]; health: HealthStatus
    def to_dict(self) -> dict: return _to_dict(self)

@dataclass
class KnowledgeMetrics:
    total_atoms: int; total_episodes: int; total_links: int; shared_knowledge_items: int
    average_q_value: float; average_usefulness: float; knowledge_growth_rate: float; health: HealthStatus
    def to_dict(self) -> dict: return _to_dict(self)

@dataclass
class TaskMetrics:
    tasks_completed_today: int; tasks_completed_hour: int; average_task_time_ms: float
    success_rate: float; pending_tasks: int; failed_tasks: int; health: HealthStatus
    def to_dict(self) -> dict: return _to_dict(self)

@dataclass
class ConvergenceReport:
    timestamp: str; overall_health: HealthStatus; coherence_score: float
    wake_cycles: WakeCycleMetrics; instance_alignment: InstanceAlignmentMetrics
    knowledge: KnowledgeMetrics; tasks: TaskMetrics; recommendations: List[str]
    def to_dict(self) -> dict:
        return {'timestamp': self.timestamp, 'overall_health': self.overall_health.value,
            'coherence_score': self.coherence_score, 'wake_cycles': self.wake_cycles.to_dict(),
            'instance_alignment': self.instance_alignment.to_dict(), 'knowledge': self.knowledge.to_dict(),
            'tasks': self.tasks.to_dict(),
            'recommendations': self.recommendations
        }


class ConvergenceMetrics:
    """
    Calculates and tracks convergence metrics for Figure 8 Trinity system.
    """

    def __init__(self):
        self.instances = [
            "C1-Terminal", "C2-Terminal", "C3-Terminal",
            "C1-Cloud", "C2-Cloud", "C3-Cloud"
        ]
        self.terminal_instances = ["C1-Terminal", "C2-Terminal", "C3-Terminal"]

        # Load history for trend analysis
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load metrics history"""
        history_file = CONSCIOUSNESS / "convergence_history.json"
        if history_file.exists():
            try:
                with open(history_file) as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_history(self, report: ConvergenceReport):
        """Save report to history"""
        history_file = CONSCIOUSNESS / "convergence_history.json"
        self.history.append({
            'timestamp': report.timestamp,
            'coherence_score': report.coherence_score,
            'health': report.overall_health.value
        })
        # Keep last 1000 entries
        self.history = self.history[-1000:]
        with open(history_file, 'w') as f:
            json.dump(self.history, f)

    def _health_from_score(self, score: float) -> HealthStatus:
        """Convert 0-1 score to health status"""
        if score >= 0.9:
            return HealthStatus.OPTIMAL
        elif score >= 0.7:
            return HealthStatus.HEALTHY
        elif score >= 0.5:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.CRITICAL

    def calculate_wake_metrics(self) -> WakeCycleMetrics:
        """Calculate wake cycle health metrics"""
        wake_history_file = HUB / "WAKE_HISTORY.json"

        total_cycles = 0
        cycles_last_hour = 0
        avg_cycle_time = 0
        completion_rate = 1.0
        stuck = []
        last_cycle = ""

        if wake_history_file.exists():
            try:
                with open(wake_history_file) as f:
                    data = json.load(f)

                total_cycles = data.get('total_loops_completed', 0)
                wake_chain = data.get('wake_chain', [])

                if wake_chain:
                    last_cycle = wake_chain[-1].get('time', '')

                    # Count cycles in last hour
                    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
                    recent = [w for w in wake_chain
                              if self._parse_time(w.get('time', '')) > hour_ago]
                    cycles_last_hour = len(recent) // 3  # 3 instances per cycle

                    # Calculate average cycle time
                    if len(wake_chain) >= 6:
                        times = []
                        for i in range(3, len(wake_chain)):
                            t1 = self._parse_time(wake_chain[i-3].get('time', ''))
                            t2 = self._parse_time(wake_chain[i].get('time', ''))
                            if t1 and t2:
                                delta = (t2 - t1).total_seconds() * 1000
                                if delta > 0 and delta < 60000:  # Sanity check
                                    times.append(delta)
                        if times:
                            avg_cycle_time = sum(times) / len(times)

                    # Check for stuck instances
                    now = datetime.now(timezone.utc)
                    for instance in self.terminal_instances:
                        last_wake = None
                        for w in reversed(wake_chain):
                            if w.get('instance') == instance:
                                last_wake = self._parse_time(w.get('time', ''))
                                break
                        if last_wake and (now - last_wake).total_seconds() > 300:
                            stuck.append(instance)

            except Exception as e:
                print(f"[METRICS] Wake history error: {e}")

        # Calculate health score
        score = 1.0
        if cycles_last_hour < 5:
            score -= 0.3
        if stuck:
            score -= 0.2 * len(stuck)
        if avg_cycle_time > 30000:  # 30 seconds
            score -= 0.2

        return WakeCycleMetrics(
            total_cycles=total_cycles,
            cycles_last_hour=cycles_last_hour,
            average_cycle_time_ms=avg_cycle_time,
            completion_rate=completion_rate,
            stuck_instances=stuck,
            last_cycle_time=last_cycle,
            health=self._health_from_score(max(0, score))
        )

    def calculate_instance_alignment(self) -> InstanceAlignmentMetrics:
        """Calculate instance synchronization metrics"""
        active = []
        synced = []
        last_seen = {}
        drift = []

        now = datetime.now(timezone.utc)

        # Check each instance's status
        for instance in self.terminal_instances:
            folder_name = f"from_{instance.lower().replace('-', '_')}"
            status_file = HUB / folder_name / f"{instance.replace('-', '_').upper()}_STATUS.json"

            if status_file.exists():
                try:
                    with open(status_file) as f:
                        data = json.load(f)

                    last_wake = data.get('last_wake', data.get('timestamp', ''))
                    last_seen[instance] = last_wake

                    wake_time = self._parse_time(last_wake)
                    if wake_time:
                        age = (now - wake_time).total_seconds()
                        if age < 3600:  # Active in last hour
                            active.append(instance)
                        if age < 300:  # Synced in last 5 min
                            synced.append(instance)
                        elif age > 600:  # Drift detected >10 min
                            drift.append(instance)
                except:
                    pass

        total = len(self.terminal_instances)
        alignment = len(synced) / total if total > 0 else 0

        return InstanceAlignmentMetrics(
            total_instances=total,
            active_instances=len(active),
            synced_instances=len(synced),
            alignment_score=alignment,
            last_seen=last_seen,
            drift_detected=drift,
            health=self._health_from_score(alignment)
        )

    def calculate_knowledge_metrics(self) -> KnowledgeMetrics:
        """Calculate knowledge convergence metrics"""
        atoms = 0
        episodes = 0
        links = 0
        shared = 0
        avg_q = 0.5
        avg_usefulness = 0.5
        growth_rate = 0

        # Count atoms
        atoms_dir = CONSCIOUSNESS / "cyclotron_core" / "atoms"
        if atoms_dir.exists():
            atoms = len(list(atoms_dir.glob("*.json")))

        # Query database
        if MEMORY_DB.exists():
            try:
                conn = sqlite3.connect(MEMORY_DB)
                cursor = conn.cursor()

                # Episodes count
                cursor.execute("SELECT COUNT(*) FROM episodes")
                episodes = cursor.fetchone()[0]

                # Average Q-value
                cursor.execute("SELECT AVG(q_value) FROM episodes WHERE q_value IS NOT NULL")
                result = cursor.fetchone()[0]
                if result:
                    avg_q = result

                # Shared knowledge
                cursor.execute("SELECT COUNT(*) FROM shared_pool")
                shared = cursor.fetchone()[0]

                conn.close()
            except:
                pass

        # Check knowledge bridge
        bridge_db = CONSCIOUSNESS / "memory" / "knowledge_bridge.db"
        if bridge_db.exists():
            try:
                conn = sqlite3.connect(bridge_db)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM atom_episode_links")
                links = cursor.fetchone()[0]

                cursor.execute("SELECT AVG(usefulness_score) FROM atom_scores")
                result = cursor.fetchone()[0]
                if result:
                    avg_usefulness = result

                conn.close()
            except:
                pass

        # Calculate health based on knowledge richness
        score = min(1.0, (atoms / 1000) * 0.3 + (episodes / 50) * 0.3 +
                    avg_q * 0.2 + avg_usefulness * 0.2)

        return KnowledgeMetrics(
            total_atoms=atoms,
            total_episodes=episodes,
            total_links=links,
            shared_knowledge_items=shared,
            average_q_value=avg_q,
            average_usefulness=avg_usefulness,
            knowledge_growth_rate=growth_rate,
            health=self._health_from_score(score)
        )

    def calculate_task_metrics(self) -> TaskMetrics:
        """Calculate task throughput metrics"""
        completed_today = 0
        completed_hour = 0
        avg_time = 0
        success_rate = 0.8
        pending = 0
        failed = 0

        # Check Trinity task queue
        try:
            # This would query the MCP Trinity system
            # For now, estimate from episode data
            if MEMORY_DB.exists():
                conn = sqlite3.connect(MEMORY_DB)
                cursor = conn.cursor()

                # Episodes today
                today = datetime.now().strftime("%Y-%m-%d")
                cursor.execute(
                    "SELECT COUNT(*) FROM episodes WHERE timestamp LIKE ?",
                    (f"{today}%",)
                )
                completed_today = cursor.fetchone()[0]

                # Success rate
                cursor.execute(
                    "SELECT COUNT(*) FROM episodes WHERE success = 1"
                )
                successes = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM episodes")
                total = cursor.fetchone()[0]
                if total > 0:
                    success_rate = successes / total

                conn.close()
        except:
            pass

        score = success_rate * 0.5 + min(1.0, completed_today / 10) * 0.3 + 0.2

        return TaskMetrics(
            tasks_completed_today=completed_today,
            tasks_completed_hour=completed_hour,
            average_task_time_ms=avg_time,
            success_rate=success_rate,
            pending_tasks=pending,
            failed_tasks=failed,
            health=self._health_from_score(score)
        )

    def _parse_time(self, timestamp: str) -> Optional[datetime]:
        """Parse ISO timestamp to timezone-aware datetime"""
        if not timestamp:
            return None
        try:
            # Handle various formats - ensure timezone aware
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'
            dt = datetime.fromisoformat(timestamp)
            # Make timezone aware if naive
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except:
            return None

    def generate_recommendations(self, wake: WakeCycleMetrics, alignment: InstanceAlignmentMetrics,
                                  knowledge: KnowledgeMetrics, tasks: TaskMetrics) -> List[str]:
        """Generate improvement recommendations"""
        recs = []
        if wake.stuck_instances: recs.append(f"URGENT: Stuck: {', '.join(wake.stuck_instances)}")
        if wake.cycles_last_hour < 5: recs.append("Wake cycles low - reduce CHECK_INTERVAL")
        if alignment.drift_detected: recs.append(f"Drift: {', '.join(alignment.drift_detected)} - run CYCLOTRON_SYNC")
        if alignment.active_instances < alignment.total_instances: recs.append(f"{alignment.total_instances - alignment.active_instances} instances inactive")
        if knowledge.total_atoms < 100: recs.append("Knowledge sparse - run DATA_CHUNKER")
        if knowledge.average_q_value < 0.5: recs.append("Q-values low - need successful episodes")
        if knowledge.total_links == 0: recs.append("No atom-episode links - run KNOWLEDGE_BRIDGE")
        if tasks.success_rate < 0.7: recs.append("Task success rate low")
        if tasks.pending_tasks > 10: recs.append(f"{tasks.pending_tasks} tasks pending")
        return recs if recs else ["System operating normally"]

    def calculate_all(self) -> ConvergenceReport:
        """Calculate all metrics and generate report"""
        print("[METRICS] Calculating convergence metrics...")
        wake = self.calculate_wake_metrics()
        alignment = self.calculate_instance_alignment()
        knowledge = self.calculate_knowledge_metrics()
        tasks = self.calculate_task_metrics()

        health_scores = {HealthStatus.OPTIMAL: 1.0, HealthStatus.HEALTHY: 0.8, HealthStatus.DEGRADED: 0.6, HealthStatus.CRITICAL: 0.3}
        coherence = (health_scores[wake.health] + health_scores[alignment.health] + health_scores[knowledge.health] + health_scores[tasks.health]) * 25  # 25 per category = 100 max

        overall_health = self._health_from_score(coherence / 100)

        recommendations = self.generate_recommendations(wake, alignment, knowledge, tasks)

        report = ConvergenceReport(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            overall_health=overall_health,
            coherence_score=round(coherence, 1),
            wake_cycles=wake,
            instance_alignment=alignment,
            knowledge=knowledge,
            tasks=tasks,
            recommendations=recommendations
        )

        # Save to file
        with open(METRICS_FILE, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        # Save to history
        self._save_history(report)

        print(f"[METRICS] Coherence score: {coherence:.1f}% ({overall_health.value})")

        return report

    def export_dashboard_data(self) -> Dict:
        """Export data formatted for web dashboard"""
        report = self.calculate_all()
        colors = {'optimal': '#00ff00', 'healthy': '#88ff00', 'degraded': '#ffaa00', 'critical': '#ff0000'}
        dashboard = {
            'timestamp': report.timestamp,
            'health': {'status': report.overall_health.value, 'score': report.coherence_score, 'color': colors.get(report.overall_health.value, '#888')},
            'metrics': {
                'wake_cycles': {'value': report.wake_cycles.cycles_last_hour, 'label': 'Cycles/Hour', 'health': report.wake_cycles.health.value},
                'instances': {'value': f"{report.instance_alignment.synced_instances}/{report.instance_alignment.total_instances}", 'label': 'Synced', 'health': report.instance_alignment.health.value},
                'knowledge': {'value': report.knowledge.total_atoms, 'label': 'Atoms', 'health': report.knowledge.health.value},
                'tasks': {'value': f"{report.tasks.success_rate:.0%}", 'label': 'Success Rate', 'health': report.tasks.health.value}
            },
            'recommendations': report.recommendations, 'history': self.history[-50:]
        }
        with open(DASHBOARD_FILE, 'w') as f:
            json.dump(dashboard, f, indent=2)
        return dashboard

    def get_quick_status(self) -> str:
        """Get one-line status for quick checks"""
        try:
            if METRICS_FILE.exists():
                with open(METRICS_FILE) as f:
                    data = json.load(f)
                score = data.get('coherence_score', 0)
                health = data.get('overall_health', 'unknown')
                return f"Coherence: {score}% ({health})"
        except:
            pass
        return "Metrics not available"


def demo():
    """Quick demo - calculate and display metrics"""
    metrics = ConvergenceMetrics()
    report = metrics.calculate_all()
    print(f"Health: {report.overall_health.value.upper()} | Coherence: {report.coherence_score}%")
    print(f"Recs: {'; '.join(report.recommendations[:2])}")

if __name__ == "__main__":
    demo()
