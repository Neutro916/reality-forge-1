#!/usr/bin/env python3
"""PATTERN TRAINING COLLECTOR - Collects labeled training data for pattern recognition.
Categories: task_success, task_failure, user_sequence, system_chain, error_recovery."""

import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
TRAINING_DIR = CONSCIOUSNESS / "training_data"
TRAINING_DB = TRAINING_DIR / "pattern_training.db"


class PatternCategory(Enum):
    """Categories of patterns to collect"""
    TASK_SUCCESS = "task_success"      # Successful task completions
    TASK_FAILURE = "task_failure"      # Failed tasks
    USER_SEQUENCE = "user_sequence"    # User interaction sequences
    SYSTEM_CHAIN = "system_chain"      # System task chains
    ERROR_RECOVERY = "error_recovery"  # Error and recovery patterns
    OPTIMIZATION = "optimization"      # Performance optimizations
    COMMUNICATION = "communication"    # Trinity communication patterns


@dataclass
class PatternObservation:
    """A single pattern observation"""
    observation_id: str
    timestamp: str
    category: str
    pattern_type: str
    input_context: Dict[str, Any]
    output_result: Dict[str, Any]
    label: str
    confidence: float
    source_instance: str
    metadata: Dict[str, Any]


class PatternTrainingCollector:
    """Collects and manages pattern recognition training data with SQLite persistence."""

    def __init__(self, db_path: Path = TRAINING_DB):
        self.db_path = db_path
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main observations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_observations (
                observation_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                input_context TEXT NOT NULL,
                output_result TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source_instance TEXT,
                metadata TEXT,
                content_hash TEXT UNIQUE
            )
        """)

        # Labels table for taxonomy
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                label TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                description TEXT,
                example_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Pattern sequences table (for sequential patterns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_sequences (
                sequence_id TEXT PRIMARY KEY,
                observation_ids TEXT NOT NULL,
                sequence_label TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON pattern_observations(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_label ON pattern_observations(label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON pattern_observations(timestamp)")

        conn.commit()
        conn.close()

    def _generate_id(self) -> str:
        """Generate unique observation ID"""
        import uuid
        return uuid.uuid4().hex[:12]

    def _compute_hash(self, input_context: Dict, output_result: Dict, pattern_type: str) -> str:
        """Compute content hash for deduplication"""
        content = json.dumps({
            'input': input_context,
            'output': output_result,
            'type': pattern_type
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_pattern(self, pattern_type: str, input_context: Dict[str, Any], output_result: Dict[str, Any],
                        label: str, category: PatternCategory = PatternCategory.TASK_SUCCESS, confidence: float = 1.0,
                        source_instance: str = "unknown", metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Record a pattern observation. Returns observation_id if recorded, None if duplicate."""
        content_hash = self._compute_hash(input_context, output_result, pattern_type)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            observation_id = self._generate_id()
            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO pattern_observations
                (observation_id, timestamp, category, pattern_type, input_context,
                 output_result, label, confidence, source_instance, metadata, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                observation_id,
                now,
                category.value if isinstance(category, PatternCategory) else category,
                pattern_type,
                json.dumps(input_context),
                json.dumps(output_result),
                label,
                confidence,
                source_instance,
                json.dumps(metadata or {}),
                content_hash
            ))

            # Update label count
            cursor.execute("""
                INSERT INTO labels (label, category, example_count, created_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(label) DO UPDATE SET
                example_count = example_count + 1
            """, (label, category.value if isinstance(category, PatternCategory) else category, now))

            conn.commit()
            print(f"[TRAINING] Recorded pattern: {pattern_type} -> {label}")
            return observation_id

        except sqlite3.IntegrityError:
            # Duplicate pattern
            print(f"[TRAINING] Duplicate pattern skipped: {pattern_type}")
            return None
        finally:
            conn.close()

    def record_sequence(
        self,
        observations: List[str],
        sequence_label: str
    ) -> str:
        """Record a sequence of patterns as a higher-order pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sequence_id = self._generate_id()
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO pattern_sequences (sequence_id, observation_ids, sequence_label, created_at)
            VALUES (?, ?, ?, ?)
        """, (sequence_id, json.dumps(observations), sequence_label, now))

        conn.commit()
        conn.close()

        return sequence_id

    def get_observations(
        self,
        category: Optional[PatternCategory] = None,
        label: Optional[str] = None,
        limit: int = 1000
    ) -> List[PatternObservation]:
        """Get observations with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM pattern_observations WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category.value if isinstance(category, PatternCategory) else category)

        if label:
            query += " AND label = ?"
            params.append(label)

        query += f" ORDER BY timestamp DESC LIMIT {limit}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        observations = []
        for row in rows:
            observations.append(PatternObservation(
                observation_id=row[0],
                timestamp=row[1],
                category=row[2],
                pattern_type=row[3],
                input_context=json.loads(row[4]),
                output_result=json.loads(row[5]),
                label=row[6],
                confidence=row[7],
                source_instance=row[8],
                metadata=json.loads(row[9])
            ))

        return observations

    def get_labels(self, category: Optional[PatternCategory] = None) -> List[Dict]:
        """Get all labels with counts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            cursor.execute(
                "SELECT * FROM labels WHERE category = ? ORDER BY example_count DESC",
                (category.value if isinstance(category, PatternCategory) else category,)
            )
        else:
            cursor.execute("SELECT * FROM labels ORDER BY example_count DESC")

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'label': row[0],
                'category': row[1],
                'description': row[2],
                'example_count': row[3],
                'created_at': row[4]
            }
            for row in rows
        ]

    def export_training_data(self, format: str = "jsonl", category: Optional[PatternCategory] = None,
                              output_path: Optional[Path] = None) -> Optional[str]:
        """Export training data in jsonl/json/csv format."""
        observations = self.get_observations(category=category, limit=100000)

        if not observations:
            print("[TRAINING] No observations to export")
            return None

        if format == "jsonl":
            lines = []
            for obs in observations:
                training_example = {
                    "input": obs.input_context,
                    "output": obs.output_result,
                    "label": obs.label,
                    "metadata": {
                        "category": obs.category,
                        "pattern_type": obs.pattern_type,
                        "confidence": obs.confidence,
                        "source": obs.source_instance
                    }
                }
                lines.append(json.dumps(training_example))

            data = "\n".join(lines)

        elif format == "json":
            data = json.dumps([asdict(obs) for obs in observations], indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['observation_id', 'timestamp', 'category', 'pattern_type',
                           'label', 'confidence', 'input_context', 'output_result'])

            for obs in observations:
                writer.writerow([
                    obs.observation_id,
                    obs.timestamp,
                    obs.category,
                    obs.pattern_type,
                    obs.label,
                    obs.confidence,
                    json.dumps(obs.input_context),
                    json.dumps(obs.output_result)
                ])

            data = output.getvalue()
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_path:
            output_path = Path(output_path)
            output_path.write_text(data)
            print(f"[TRAINING] Exported {len(observations)} observations to {output_path}")
            return str(output_path)

        return data

    def get_stats(self) -> Dict[str, Any]:
        """Get training data statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {
            'total_observations': 0,
            'by_category': {},
            'by_label': {},
            'unique_labels': 0,
            'sequences': 0,
            'date_range': {'first': None, 'last': None}
        }

        # Total observations
        cursor.execute("SELECT COUNT(*) FROM pattern_observations")
        stats['total_observations'] = cursor.fetchone()[0]

        # By category
        cursor.execute("SELECT category, COUNT(*) FROM pattern_observations GROUP BY category")
        stats['by_category'] = dict(cursor.fetchall())

        # By label (top 20)
        cursor.execute("""
            SELECT label, COUNT(*) as count FROM pattern_observations
            GROUP BY label ORDER BY count DESC LIMIT 20
        """)
        stats['by_label'] = dict(cursor.fetchall())

        # Unique labels
        cursor.execute("SELECT COUNT(*) FROM labels")
        stats['unique_labels'] = cursor.fetchone()[0]

        # Sequences
        cursor.execute("SELECT COUNT(*) FROM pattern_sequences")
        stats['sequences'] = cursor.fetchone()[0]

        # Date range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM pattern_observations")
        row = cursor.fetchone()
        if row[0]:
            stats['date_range'] = {'first': row[0], 'last': row[1]}

        conn.close()
        return stats

    def auto_collect_from_brain(self, brain_db_path: Path):
        """
        Automatically collect patterns from Cyclotron Brain database.

        Extracts:
        - Successful task patterns
        - Error patterns
        - Q-value changes (learning patterns)
        """
        if not brain_db_path.exists():
            print(f"[TRAINING] Brain database not found: {brain_db_path}")
            return 0

        conn = sqlite3.connect(brain_db_path)
        cursor = conn.cursor()

        collected = 0

        try:
            # Collect from episodes table (task executions)
            cursor.execute("""
                SELECT task_type, context, result, success, q_value_delta
                FROM episodes
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 500
            """)

            for row in cursor.fetchall():
                task_type, context_json, result_json, success, q_delta = row

                try:
                    context = json.loads(context_json) if context_json else {}
                    result = json.loads(result_json) if result_json else {}
                except:
                    context = {'raw': context_json}
                    result = {'raw': result_json}

                category = PatternCategory.TASK_SUCCESS if success else PatternCategory.TASK_FAILURE
                label = f"{task_type}_{'success' if success else 'failure'}"

                obs_id = self.record_pattern(
                    pattern_type=task_type or 'unknown',
                    input_context=context,
                    output_result=result,
                    label=label,
                    category=category,
                    confidence=min(1.0, abs(q_delta) + 0.5) if q_delta else 0.5,
                    source_instance="cyclotron_brain"
                )

                if obs_id:
                    collected += 1

        except sqlite3.OperationalError as e:
            print(f"[TRAINING] Error reading brain database: {e}")
        finally:
            conn.close()

        print(f"[TRAINING] Auto-collected {collected} patterns from brain")
        return collected

    def auto_collect_from_hub(self):
        """
        Collect patterns from hub status files.

        Extracts:
        - Wake chain patterns
        - Communication patterns
        - Instance behavior patterns
        """
        hub = CONSCIOUSNESS / "hub"
        if not hub.exists():
            return 0

        collected = 0

        # Collect from wake history
        wake_history = hub / "WAKE_HISTORY.json"
        if wake_history.exists():
            try:
                with open(wake_history) as f:
                    history = json.load(f)

                wake_chain = history.get('wake_chain', [])

                # Analyze wake sequences
                for i in range(len(wake_chain) - 2):
                    sequence = wake_chain[i:i+3]

                    pattern = {
                        'from': sequence[0].get('instance'),
                        'middle': sequence[1].get('instance'),
                        'to': sequence[2].get('instance')
                    }

                    obs_id = self.record_pattern(
                        pattern_type='wake_transition',
                        input_context={'from': pattern['from'], 'to': pattern['middle']},
                        output_result={'next': pattern['to']},
                        label=f"wake_chain_{pattern['from'][:2]}_{pattern['middle'][:2]}_{pattern['to'][:2]}",
                        category=PatternCategory.SYSTEM_CHAIN,
                        source_instance="hub"
                    )

                    if obs_id:
                        collected += 1

            except Exception as e:
                print(f"[TRAINING] Error reading wake history: {e}")

        print(f"[TRAINING] Auto-collected {collected} patterns from hub")
        return collected


def demo():
    """Quick demo - show stats"""
    collector = PatternTrainingCollector()
    stats = collector.get_stats()
    print(f"Training Collector: {stats['total_observations']} observations, {stats['unique_labels']} labels")

if __name__ == "__main__":
    demo()
