#!/usr/bin/env python3
"""
KNOWLEDGE BRIDGE
Links the 4,394 knowledge atoms to the 48 episodes in memory.

C2 Architect Implementation - Phase 3 Component

Problem:
- Knowledge atoms (from DATA_CHUNKER) are isolated chunks
- Episodes (from CYCLOTRON_MEMORY) are task experiences
- No connection between them

Solution:
- Extract keywords from both
- Build bidirectional links via shared keywords
- Enable queries like "what atoms were useful in successful episodes?"

Result:
- Atoms that appeared in successful episodes get boosted
- Episodes that used valuable atoms are highlighted
- Synthesis can draw from both sources coherently
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional
from collections import defaultdict
import re

# Paths
CONSCIOUSNESS = Path.home() / ".consciousness"
ATOMS_DIR = CONSCIOUSNESS / "cyclotron_core" / "atoms"
MEMORY_DB = CONSCIOUSNESS / "memory" / "cyclotron_brain.db"
KNOWLEDGE_DB = CONSCIOUSNESS / "memory" / "knowledge_atoms.db"
BRIDGE_DB = CONSCIOUSNESS / "memory" / "knowledge_bridge.db"


def init_bridge_db():
    """Initialize the bridge database"""
    BRIDGE_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()

    # Atom-Episode links
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atom_episode_links (
            id TEXT PRIMARY KEY,
            atom_id TEXT,
            episode_id TEXT,
            link_type TEXT,
            strength REAL DEFAULT 0.5,
            created_at TEXT
        )
    ''')

    # Keyword index for atoms
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atom_keywords (
            atom_id TEXT,
            keyword TEXT,
            frequency INTEGER DEFAULT 1,
            PRIMARY KEY (atom_id, keyword)
        )
    ''')

    # Keyword index for episodes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episode_keywords (
            episode_id TEXT,
            keyword TEXT,
            frequency INTEGER DEFAULT 1,
            PRIMARY KEY (episode_id, keyword)
        )
    ''')

    # Atom usefulness scores (based on episode success)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atom_scores (
            atom_id TEXT PRIMARY KEY,
            usefulness_score REAL DEFAULT 0.5,
            times_linked INTEGER DEFAULT 0,
            successful_links INTEGER DEFAULT 0,
            last_updated TEXT
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_atom_keywords ON atom_keywords(keyword)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_episode_keywords ON episode_keywords(keyword)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_atom ON atom_episode_links(atom_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_episode ON atom_episode_links(episode_id)')

    conn.commit()
    conn.close()


def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text"""
    # Clean text
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Split and filter
    words = text.split()
    keywords = []

    # Stop words to skip
    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'been',
        'were', 'they', 'their', 'what', 'when', 'where', 'which', 'would',
        'could', 'should', 'there', 'these', 'those', 'then', 'than', 'them',
        'also', 'into', 'over', 'such', 'about', 'some', 'only', 'very',
        'just', 'more', 'most', 'other', 'after', 'before', 'being', 'does'
    }

    for word in words:
        if len(word) >= min_length and word not in stop_words:
            keywords.append(word)

    return keywords


class KnowledgeBridge:
    """Main bridge connecting atoms and episodes"""

    def __init__(self):
        init_bridge_db()
        self.conn = sqlite3.connect(BRIDGE_DB)
        self.conn.row_factory = sqlite3.Row

    def index_atoms(self, limit: int = None) -> int:
        """Index keywords from all atoms"""
        print("[BRIDGE] Indexing atoms...")
        indexed = 0

        # Index from JSON files
        if ATOMS_DIR.exists():
            files = list(ATOMS_DIR.glob("*.json"))
            if limit:
                files = files[:limit]

            for atom_file in files:
                try:
                    with open(atom_file) as f:
                        atom = json.load(f)

                    atom_id = atom.get('id', atom_file.stem)

                    # Get text to extract keywords from
                    text_parts = [
                        atom.get('compressed', ''),
                        atom.get('content', ''),
                        str(atom.get('keywords', '')),
                        atom.get('source', '')
                    ]
                    full_text = ' '.join(str(p) for p in text_parts)

                    keywords = extract_keywords(full_text)

                    # Store keywords
                    cursor = self.conn.cursor()
                    for kw in set(keywords):
                        cursor.execute('''
                            INSERT OR REPLACE INTO atom_keywords (atom_id, keyword, frequency)
                            VALUES (?, ?, ?)
                        ''', (atom_id, kw, keywords.count(kw)))

                    indexed += 1

                except Exception as e:
                    continue

            self.conn.commit()

        print(f"[BRIDGE] Indexed {indexed} atoms")
        return indexed

    def index_episodes(self) -> int:
        """Index keywords from all episodes"""
        print("[BRIDGE] Indexing episodes...")

        if not MEMORY_DB.exists():
            print("[BRIDGE] Memory DB not found")
            return 0

        indexed = 0

        try:
            mem_conn = sqlite3.connect(MEMORY_DB)
            mem_conn.row_factory = sqlite3.Row
            cursor = mem_conn.cursor()

            cursor.execute('SELECT id, task, action, result, context FROM episodes')

            bridge_cursor = self.conn.cursor()

            for row in cursor.fetchall():
                episode_id = row['id']

                # Combine text fields
                text_parts = [
                    row['task'] or '',
                    row['action'] or '',
                    row['result'] or '',
                    row['context'] or ''
                ]
                full_text = ' '.join(text_parts)

                keywords = extract_keywords(full_text)

                # Store keywords
                for kw in set(keywords):
                    bridge_cursor.execute('''
                        INSERT OR REPLACE INTO episode_keywords (episode_id, keyword, frequency)
                        VALUES (?, ?, ?)
                    ''', (episode_id, kw, keywords.count(kw)))

                indexed += 1

            self.conn.commit()
            mem_conn.close()

        except Exception as e:
            print(f"[BRIDGE] Error indexing episodes: {e}")

        print(f"[BRIDGE] Indexed {indexed} episodes")
        return indexed

    def build_links(self) -> int:
        """Build links between atoms and episodes based on shared keywords"""
        print("[BRIDGE] Building atom-episode links...")

        cursor = self.conn.cursor()

        # Find shared keywords between atoms and episodes
        cursor.execute('''
            SELECT DISTINCT
                ak.atom_id,
                ek.episode_id,
                COUNT(DISTINCT ak.keyword) as shared_keywords
            FROM atom_keywords ak
            INNER JOIN episode_keywords ek ON ak.keyword = ek.keyword
            GROUP BY ak.atom_id, ek.episode_id
            HAVING shared_keywords >= 2
        ''')

        links_created = 0
        for row in cursor.fetchall():
            atom_id = row['atom_id']
            episode_id = row['episode_id']
            shared = row['shared_keywords']

            # Calculate link strength based on shared keywords
            strength = min(1.0, shared / 10.0)

            link_id = hashlib.sha256(f"{atom_id}:{episode_id}".encode()).hexdigest()[:12]

            cursor.execute('''
                INSERT OR REPLACE INTO atom_episode_links
                (id, atom_id, episode_id, link_type, strength, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                link_id,
                atom_id,
                episode_id,
                'keyword_overlap',
                strength,
                datetime.now().isoformat()
            ))

            links_created += 1

        self.conn.commit()
        print(f"[BRIDGE] Created {links_created} links")
        return links_created

    def update_atom_scores(self) -> int:
        """Update atom usefulness scores based on linked episode success"""
        print("[BRIDGE] Updating atom scores...")

        if not MEMORY_DB.exists():
            return 0

        cursor = self.conn.cursor()

        # Get episode success info
        mem_conn = sqlite3.connect(MEMORY_DB)
        mem_cursor = mem_conn.cursor()
        mem_cursor.execute('SELECT id, success, q_value FROM episodes')
        episode_success = {row[0]: (row[1], row[2]) for row in mem_cursor.fetchall()}
        mem_conn.close()

        # Calculate scores for each atom
        cursor.execute('''
            SELECT atom_id, episode_id, strength
            FROM atom_episode_links
        ''')

        atom_stats = defaultdict(lambda: {'total': 0, 'successful': 0, 'q_sum': 0})

        for row in cursor.fetchall():
            atom_id = row['atom_id']
            episode_id = row['episode_id']
            strength = row['strength']

            if episode_id in episode_success:
                success, q_value = episode_success[episode_id]
                atom_stats[atom_id]['total'] += 1
                if success:
                    atom_stats[atom_id]['successful'] += 1
                atom_stats[atom_id]['q_sum'] += (q_value or 0.5) * strength

        # Update scores
        updated = 0
        for atom_id, stats in atom_stats.items():
            if stats['total'] > 0:
                usefulness = (
                    (stats['successful'] / stats['total']) * 0.5 +
                    (stats['q_sum'] / stats['total']) * 0.5
                )

                cursor.execute('''
                    INSERT OR REPLACE INTO atom_scores
                    (atom_id, usefulness_score, times_linked, successful_links, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    atom_id,
                    usefulness,
                    stats['total'],
                    stats['successful'],
                    datetime.now().isoformat()
                ))
                updated += 1

        self.conn.commit()
        print(f"[BRIDGE] Updated {updated} atom scores")
        return updated

    def get_atoms_for_task(self, task: str, limit: int = 10) -> List[Dict]:
        """Get most relevant atoms for a task, ranked by usefulness"""
        keywords = extract_keywords(task)

        if not keywords:
            return []

        cursor = self.conn.cursor()

        # Find atoms with matching keywords, ranked by usefulness
        placeholders = ','.join('?' for _ in keywords)
        cursor.execute(f'''
            SELECT DISTINCT
                ak.atom_id,
                COUNT(DISTINCT ak.keyword) as keyword_matches,
                COALESCE(scores.usefulness_score, 0.5) as usefulness
            FROM atom_keywords ak
            LEFT JOIN atom_scores scores ON ak.atom_id = scores.atom_id
            WHERE ak.keyword IN ({placeholders})
            GROUP BY ak.atom_id
            ORDER BY usefulness DESC, keyword_matches DESC
            LIMIT ?
        ''', keywords + [limit])

        results = []
        for row in cursor.fetchall():
            results.append({
                'atom_id': row['atom_id'],
                'keyword_matches': row['keyword_matches'],
                'usefulness': row['usefulness']
            })

        return results

    def get_successful_episodes_for_atom(self, atom_id: str) -> List[Dict]:
        """Get successful episodes that used this atom"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT episode_id, strength
            FROM atom_episode_links
            WHERE atom_id = ?
            ORDER BY strength DESC
        ''', (atom_id,))

        links = cursor.fetchall()

        if not links or not MEMORY_DB.exists():
            return []

        # Get episode details
        mem_conn = sqlite3.connect(MEMORY_DB)
        mem_conn.row_factory = sqlite3.Row
        mem_cursor = mem_conn.cursor()

        results = []
        for link in links:
            mem_cursor.execute('''
                SELECT id, task, action, result, success, q_value
                FROM episodes WHERE id = ? AND success = 1
            ''', (link['episode_id'],))

            row = mem_cursor.fetchone()
            if row:
                results.append({
                    'episode_id': row['id'],
                    'task': row['task'],
                    'action': row['action'],
                    'result': row['result'],
                    'q_value': row['q_value'],
                    'link_strength': link['strength']
                })

        mem_conn.close()
        return results

    def get_stats(self) -> Dict:
        """Get bridge statistics"""
        cursor = self.conn.cursor()

        stats = {}

        cursor.execute('SELECT COUNT(DISTINCT atom_id) FROM atom_keywords')
        stats['atoms_indexed'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT episode_id) FROM episode_keywords')
        stats['episodes_indexed'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM atom_episode_links')
        stats['total_links'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM atom_scores')
        stats['atoms_scored'] = cursor.fetchone()[0]

        cursor.execute('SELECT AVG(usefulness_score) FROM atom_scores')
        avg = cursor.fetchone()[0]
        stats['average_usefulness'] = f"{avg:.2f}" if avg else "N/A"

        return stats

    def full_rebuild(self) -> Dict:
        """Full rebuild of the bridge"""
        print("\n" + "="*60)
        print("KNOWLEDGE BRIDGE - FULL REBUILD")
        print("="*60 + "\n")

        results = {
            'atoms_indexed': self.index_atoms(),
            'episodes_indexed': self.index_episodes(),
            'links_created': self.build_links(),
            'scores_updated': self.update_atom_scores()
        }

        print("\n" + "="*60)
        print("REBUILD COMPLETE")
        print("="*60)
        for key, value in results.items():
            print(f"  {key}: {value}")

        return results

    def close(self):
        self.conn.close()


def demo():
    """Demonstrate knowledge bridge"""
    bridge = KnowledgeBridge()

    # Rebuild bridge
    bridge.full_rebuild()

    # Show stats
    print("\n--- Bridge Statistics ---")
    stats = bridge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test query
    print("\n--- Query: 'fix null pointer error' ---")
    atoms = bridge.get_atoms_for_task("fix null pointer error in login page")
    for atom in atoms[:5]:
        print(f"  [{atom['usefulness']:.2f}] {atom['atom_id']} (matches: {atom['keyword_matches']})")

    bridge.close()


if __name__ == "__main__":
    demo()
