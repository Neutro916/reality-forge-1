#!/usr/bin/env python3
"""
SEARCH AGENT - Parallel Knowledge Chain
Part of the Fractal Supercharging Architecture

C2 Architect Implementation - Phase 2 Component

This agent runs IN PARALLEL with ReasoningAgent and PlanningAgent.
While they analyze the task structure, SearchAgent queries:
1. Knowledge atoms (4,394 from DATA_CHUNKER)
2. Episode history (from CYCLOTRON_MEMORY)
3. Pattern database (successful approaches)

Result: Synthesizer receives search results BEFORE reasoning completes,
allowing richer context for decision making.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

# Add paths for imports
sys.path.insert(0, str(Path.home() / ".consciousness"))
sys.path.insert(0, str(Path.home() / "100X_DEPLOYMENT"))

# Configuration
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
ATOMS_DIR = CONSCIOUSNESS / "cyclotron_core" / "atoms"
MEMORY_DB = CONSCIOUSNESS / "memory" / "cyclotron_brain.db"
KNOWLEDGE_DB = CONSCIOUSNESS / "memory" / "knowledge_atoms.db"


class SearchAgent:
    """
    Agent that searches knowledge bases in parallel with reasoning.

    Capabilities:
    - Search 4,394 knowledge atoms by keyword
    - Find similar episodes from memory
    - Match against successful patterns
    - Rank results by relevance

    Integration:
    - Runs as part of parallel agent chain
    - Results merged at synthesis phase
    - Provides context that reasoner/planner don't have
    """

    def __init__(self, name: str = "Searcher"):
        self.name = name
        self.description = "Searches knowledge atoms and episode history"
        self.capabilities = ["search_atoms", "search_episodes", "search_patterns"]

        # Track search stats
        self.searches_performed = 0
        self.total_results = 0

    def process(self, state: dict) -> dict:
        """
        Main processing method - matches BrainAgent interface.

        Args:
            state: AgentState dict with 'task', 'context', 'memory', 'outputs'

        Returns:
            Updated state with search results
        """
        task = state.get('task', '')

        if not task:
            return state

        # Initialize context if needed
        if 'context' not in state:
            state['context'] = {}

        # Run all searches
        search_results = {
            'atoms': self.search_atoms(task),
            'episodes': self.search_episodes(task),
            'patterns': self.search_patterns(task),
            'timestamp': datetime.now().isoformat()
        }

        # Store in context for synthesis
        state['context']['search_results'] = search_results

        # Add summary to outputs
        total_found = (
            len(search_results['atoms']) +
            len(search_results['episodes']) +
            len(search_results['patterns'])
        )

        if 'outputs' not in state:
            state['outputs'] = []

        state['outputs'].append({
            'agent': self.name,
            'output': f"Search complete: {total_found} relevant items found",
            'timestamp': datetime.now().isoformat()
        })

        # Add to memory log
        if 'memory' not in state:
            state['memory'] = []

        state['memory'].append({
            'content': f"Found {len(search_results['atoms'])} atoms, "
                      f"{len(search_results['episodes'])} episodes, "
                      f"{len(search_results['patterns'])} patterns",
            'category': 'search',
            'timestamp': datetime.now().isoformat()
        })

        self.searches_performed += 1
        self.total_results += total_found

        return state

    def search_atoms(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search knowledge atoms by keyword.

        Searches both:
        - cyclotron_core/atoms/*.json files
        - knowledge_atoms.db if available
        """
        results = []
        keywords = query.lower().split()[:5]

        # Method 1: Search JSON atom files directly
        if ATOMS_DIR.exists():
            for atom_file in list(ATOMS_DIR.glob("*.json"))[:500]:  # Limit scan
                try:
                    with open(atom_file) as f:
                        atom = json.load(f)

                    # Check if keywords match
                    atom_text = json.dumps(atom).lower()
                    matches = sum(1 for kw in keywords if kw in atom_text)

                    if matches >= 2:  # At least 2 keyword matches
                        results.append({
                            'id': atom.get('id', atom_file.stem),
                            'source': str(atom.get('source', atom_file.name)),
                            'relevance': matches,
                            'content_preview': str(atom.get('compressed', atom.get('content', '')))[:200]
                        })
                except:
                    continue

        # Method 2: Search knowledge_atoms.db if exists
        if KNOWLEDGE_DB.exists():
            try:
                conn = sqlite3.connect(KNOWLEDGE_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                conditions = []
                params = []
                for kw in keywords:
                    if len(kw) > 3:
                        conditions.append("(LOWER(keywords) LIKE ? OR LOWER(compressed_text) LIKE ?)")
                        params.extend([f"%{kw}%", f"%{kw}%"])

                if conditions:
                    query_sql = f'''
                        SELECT id, source_file, compressed_text, keywords
                        FROM atoms
                        WHERE {" OR ".join(conditions)}
                        ORDER BY importance DESC
                        LIMIT ?
                    '''
                    params.append(limit)
                    cursor.execute(query_sql, params)

                    for row in cursor.fetchall():
                        results.append({
                            'id': row['id'],
                            'source': row['source_file'],
                            'relevance': 3,  # DB matches are higher quality
                            'content_preview': row['compressed_text'][:200] if row['compressed_text'] else ''
                        })

                conn.close()
            except Exception as e:
                pass  # Silent fail - use file results only

        # Sort by relevance and dedupe
        results.sort(key=lambda x: x['relevance'], reverse=True)

        # Dedupe by ID
        seen = set()
        unique_results = []
        for r in results:
            if r['id'] not in seen:
                seen.add(r['id'])
                unique_results.append(r)

        return unique_results[:limit]

    def search_episodes(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search episode history for similar past experiences.
        """
        if not MEMORY_DB.exists():
            return []

        results = []
        keywords = query.lower().split()

        try:
            conn = sqlite3.connect(MEMORY_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            conditions = []
            params = []
            for kw in keywords[:5]:
                if len(kw) > 3:
                    conditions.append("LOWER(task) LIKE ?")
                    params.append(f"%{kw}%")

            if not conditions:
                return []

            query_sql = f'''
                SELECT id, task, action, result, success, q_value,
                       (success * q_value) as relevance_score
                FROM episodes
                WHERE {" OR ".join(conditions)}
                ORDER BY relevance_score DESC, timestamp DESC
                LIMIT ?
            '''
            params.append(limit)

            cursor.execute(query_sql, params)

            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'task': row['task'][:100],
                    'action': row['action'][:100],
                    'success': bool(row['success']),
                    'q_value': row['q_value'],
                    'relevance': row['relevance_score']
                })

            conn.close()
        except Exception as e:
            pass

        return results

    def search_patterns(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search pattern database for successful approaches.
        """
        if not MEMORY_DB.exists():
            return []

        results = []
        keywords = query.lower().split()

        try:
            conn = sqlite3.connect(MEMORY_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            conditions = []
            params = []
            for kw in keywords[:5]:
                if len(kw) > 3:
                    conditions.append("LOWER(trigger_conditions) LIKE ?")
                    params.append(f"%{kw}%")

            if conditions:
                query_sql = f'''
                    SELECT id, name, description, trigger_conditions,
                           recommended_action, success_rate
                    FROM patterns
                    WHERE {" OR ".join(conditions)}
                    ORDER BY success_rate DESC
                    LIMIT ?
                '''
                params.append(limit)
            else:
                query_sql = '''
                    SELECT id, name, description, trigger_conditions,
                           recommended_action, success_rate
                    FROM patterns
                    ORDER BY success_rate DESC
                    LIMIT ?
                '''
                params = [limit]

            cursor.execute(query_sql, params)

            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'][:100] if row['description'] else '',
                    'trigger': row['trigger_conditions'][:100] if row['trigger_conditions'] else '',
                    'action': row['recommended_action'][:100] if row['recommended_action'] else '',
                    'success_rate': row['success_rate']
                })

            conn.close()
        except Exception as e:
            pass

        return results

    def get_stats(self) -> Dict:
        """Get search agent statistics"""
        atom_count = len(list(ATOMS_DIR.glob("*.json"))) if ATOMS_DIR.exists() else 0

        return {
            'name': self.name,
            'searches_performed': self.searches_performed,
            'total_results_returned': self.total_results,
            'atoms_available': atom_count,
            'memory_db_exists': MEMORY_DB.exists(),
            'knowledge_db_exists': KNOWLEDGE_DB.exists()
        }


# Async version for parallel processing
class AsyncSearchAgent(SearchAgent):
    """
    Async version of SearchAgent for parallel chains.

    Usage:
        agent = AsyncSearchAgent()
        result = await agent.process_async(state)
    """

    async def process_async(self, state: dict) -> dict:
        """
        Async processing - wraps sync method for now.
        Future: True async DB queries with aiosqlite.
        """
        import asyncio
        # Run sync method in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, state)


# Integration example
def integrate_with_orchestrator():
    """
    Shows how to add SearchAgent to BRAIN_AGENT_FRAMEWORK.py

    Add to AgentOrchestrator.__init__():
        from SEARCH_AGENT import SearchAgent
        self.agents['searcher'] = SearchAgent()

    Then modify run() to include 'searcher' in sequence,
    or run in parallel with asyncio.
    """
    pass


# CLI test
if __name__ == "__main__":
    print("Testing Search Agent...")
    print("=" * 60)

    agent = SearchAgent()

    # Test search
    test_task = "fix null pointer error in login.html"

    state = {
        'task': test_task,
        'context': {},
        'memory': [],
        'outputs': []
    }

    print(f"\nSearching for: {test_task}")
    print("-" * 40)

    result = agent.process(state)

    search_results = result['context'].get('search_results', {})

    print(f"\nAtoms found: {len(search_results.get('atoms', []))}")
    for atom in search_results.get('atoms', [])[:3]:
        print(f"  - [{atom['relevance']}] {atom['source'][:50]}")

    print(f"\nEpisodes found: {len(search_results.get('episodes', []))}")
    for ep in search_results.get('episodes', [])[:3]:
        print(f"  - [Q:{ep['q_value']:.2f}] {ep['task'][:50]}")

    print(f"\nPatterns found: {len(search_results.get('patterns', []))}")
    for pat in search_results.get('patterns', [])[:3]:
        print(f"  - [{pat['success_rate']:.0%}] {pat['name']}")

    print("\n" + "=" * 60)
    print("Stats:", agent.get_stats())
    print("[OK] Search Agent test complete!")
