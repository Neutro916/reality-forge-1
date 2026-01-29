#!/usr/bin/env python3
"""
CYCLOTRON MEMORY SYSTEM
The brain that makes multi-agent coordination actually intelligent.

Features:
- Episodic memory (what happened)
- Pattern extraction (what works)
- Similarity search (find relevant past experiences)
- Q-learning (reinforce success)
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Memory location
MEMORY_DIR = Path.home() / ".consciousness" / "memory"
DB_PATH = MEMORY_DIR / "cyclotron_brain.db"

def ensure_memory_exists():
    """Create memory directory and database"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Episodes table - individual experiences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            agent TEXT,
            task TEXT,
            context TEXT,
            action TEXT,
            result TEXT,
            success INTEGER,
            q_value REAL DEFAULT 0.5,
            tags TEXT
        )
    ''')

    # Patterns table - extracted knowledge
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            trigger_conditions TEXT,
            recommended_action TEXT,
            success_rate REAL,
            times_used INTEGER DEFAULT 0,
            last_used TEXT
        )
    ''')

    # Shared pool - cross-agent knowledge
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_pool (
            id TEXT PRIMARY KEY,
            contributed_by TEXT,
            timestamp TEXT,
            knowledge_type TEXT,
            content TEXT,
            usefulness_score REAL DEFAULT 0.5
        )
    ''')

    conn.commit()
    conn.close()
    print(f"[MEMORY] Database initialized at {DB_PATH}")

def generate_id(content: str) -> str:
    """Generate unique ID from content"""
    return hashlib.sha256(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

class CyclotronMemory:
    """Main memory interface for agents"""

    def __init__(self, agent_id: str = "C1-Terminal"):
        self.agent_id = agent_id
        ensure_memory_exists()
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def record_episode(self, task: str, action: str, result: str,
                       success: bool, context: dict = None, tags: list = None) -> str:
        """Record a new experience"""
        episode_id = generate_id(f"{task}{action}")

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO episodes (id, timestamp, agent, task, context, action, result, success, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            episode_id,
            datetime.now().isoformat() + "Z",
            self.agent_id,
            task,
            json.dumps(context or {}),
            action,
            result,
            1 if success else 0,
            json.dumps(tags or [])
        ))
        self.conn.commit()

        print(f"[MEMORY] Recorded episode {episode_id}: {task[:50]}...")
        return episode_id

    def find_similar_episodes(self, task: str, limit: int = 5) -> List[Dict]:
        """Find similar past experiences (simple keyword matching for now)"""
        cursor = self.conn.cursor()

        # Split task into keywords
        keywords = task.lower().split()

        # Build search query
        conditions = []
        params = []
        for keyword in keywords[:5]:  # Limit to 5 keywords
            if len(keyword) > 3:  # Skip short words
                conditions.append("LOWER(task) LIKE ?")
                params.append(f"%{keyword}%")

        if not conditions:
            return []

        query = f'''
            SELECT *,
                   (success * q_value) as relevance_score
            FROM episodes
            WHERE {" OR ".join(conditions)}
            ORDER BY relevance_score DESC, timestamp DESC
            LIMIT ?
        '''
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def update_q_value(self, episode_id: str, reward: float, learning_rate: float = 0.1):
        """Update Q-value based on outcome (simple Q-learning)"""
        cursor = self.conn.cursor()

        # Get current Q-value
        cursor.execute("SELECT q_value FROM episodes WHERE id = ?", (episode_id,))
        row = cursor.fetchone()
        if not row:
            return

        old_q = row['q_value']

        # Q-learning update: Q = Q + α(reward - Q)
        new_q = old_q + learning_rate * (reward - old_q)
        new_q = max(0.0, min(1.0, new_q))  # Clamp to [0, 1]

        cursor.execute("UPDATE episodes SET q_value = ? WHERE id = ?", (new_q, episode_id))
        self.conn.commit()

        print(f"[MEMORY] Updated Q-value for {episode_id}: {old_q:.2f} -> {new_q:.2f}")

    def extract_pattern(self, name: str, description: str,
                       trigger: str, action: str, success_rate: float) -> str:
        """Extract a reusable pattern from experiences"""
        pattern_id = generate_id(name)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO patterns
            (id, name, description, trigger_conditions, recommended_action, success_rate, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            name,
            description,
            trigger,
            action,
            success_rate,
            datetime.now().isoformat() + "Z"
        ))
        self.conn.commit()

        print(f"[MEMORY] Extracted pattern: {name}")
        return pattern_id

    def get_recommended_patterns(self, task: str, limit: int = 3) -> List[Dict]:
        """Get patterns that might apply to this task"""
        cursor = self.conn.cursor()

        keywords = task.lower().split()
        conditions = []
        params = []

        for keyword in keywords[:5]:
            if len(keyword) > 3:
                conditions.append("LOWER(trigger_conditions) LIKE ?")
                params.append(f"%{keyword}%")

        if not conditions:
            # Return top patterns by success rate
            cursor.execute('''
                SELECT * FROM patterns ORDER BY success_rate DESC LIMIT ?
            ''', (limit,))
        else:
            query = f'''
                SELECT * FROM patterns
                WHERE {" OR ".join(conditions)}
                ORDER BY success_rate DESC
                LIMIT ?
            '''
            params.append(limit)
            cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def share_knowledge(self, knowledge_type: str, content: str) -> str:
        """Share knowledge to the collective pool"""
        knowledge_id = generate_id(content)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO shared_pool (id, contributed_by, timestamp, knowledge_type, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            knowledge_id,
            self.agent_id,
            datetime.now().isoformat() + "Z",
            knowledge_type,
            content
        ))
        self.conn.commit()

        print(f"[MEMORY] Shared knowledge: {knowledge_type}")
        return knowledge_id

    def get_shared_knowledge(self, knowledge_type: str = None, limit: int = 10) -> List[Dict]:
        """Retrieve knowledge from the shared pool"""
        cursor = self.conn.cursor()

        if knowledge_type:
            cursor.execute('''
                SELECT * FROM shared_pool
                WHERE knowledge_type = ?
                ORDER BY usefulness_score DESC, timestamp DESC
                LIMIT ?
            ''', (knowledge_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM shared_pool
                ORDER BY usefulness_score DESC, timestamp DESC
                LIMIT ?
            ''', (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        cursor = self.conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count, AVG(q_value) as avg_q FROM episodes")
        row = cursor.fetchone()
        stats['total_episodes'] = row['count']
        stats['average_q_value'] = row['avg_q'] or 0

        cursor.execute("SELECT COUNT(*) as count FROM episodes WHERE success = 1")
        stats['successful_episodes'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count, AVG(success_rate) as avg_success FROM patterns")
        row = cursor.fetchone()
        stats['total_patterns'] = row['count']
        stats['average_pattern_success'] = row['avg_success'] or 0

        cursor.execute("SELECT COUNT(*) as count FROM shared_pool")
        stats['shared_knowledge_items'] = cursor.fetchone()['count']

        return stats

    def close(self):
        """Close database connection"""
        self.conn.close()


# Quick test
if __name__ == "__main__":
    print("Testing Cyclotron Memory System...")

    memory = CyclotronMemory("C1-Terminal")

    # Record some test episodes
    ep1 = memory.record_episode(
        task="Fix null pointer in login.html",
        action="Added null check on line 45",
        result="Bug fixed, tests passing",
        success=True,
        context={"file": "login.html", "line": 45},
        tags=["bug", "null-pointer", "html"]
    )

    ep2 = memory.record_episode(
        task="Optimize database query",
        action="Added index to user_id column",
        result="Query time reduced 80%",
        success=True,
        context={"table": "users", "improvement": "80%"},
        tags=["performance", "database", "optimization"]
    )

    ep3 = memory.record_episode(
        task="Fix CSS alignment issue",
        action="Changed flex to grid",
        result="Still misaligned",
        success=False,
        context={"file": "styles.css"},
        tags=["css", "layout", "bug"]
    )

    # Update Q-values based on outcomes
    memory.update_q_value(ep1, reward=1.0)  # Very successful
    memory.update_q_value(ep2, reward=0.9)  # Successful
    memory.update_q_value(ep3, reward=0.2)  # Failed

    # Extract a pattern
    memory.extract_pattern(
        name="null_check_pattern",
        description="When encountering null pointer errors, add defensive null checks",
        trigger="null pointer, undefined, TypeError",
        action="Add null/undefined check before accessing property",
        success_rate=0.87
    )

    # Find similar episodes
    print("\n--- Similar Episodes for 'fix null error' ---")
    similar = memory.find_similar_episodes("fix null error in JavaScript")
    for ep in similar:
        print(f"  [{ep['q_value']:.2f}] {ep['task'][:50]}")

    # Get patterns
    print("\n--- Recommended Patterns for 'null error' ---")
    patterns = memory.get_recommended_patterns("null pointer error")
    for p in patterns:
        print(f"  [{p['success_rate']:.2f}] {p['name']}: {p['recommended_action'][:50]}")

    # Share knowledge
    memory.share_knowledge(
        knowledge_type="best_practice",
        content="Always validate user input before processing"
    )

    # Get stats
    print("\n--- Memory Statistics ---")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    memory.close()
    print("\n[OK] Memory system test complete!")
