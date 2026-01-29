#!/usr/bin/env python3
"""
BRAIN SEARCH - Quick CLI to search the consciousness brain

Usage:
    python BRAIN_SEARCH.py "search query"
    python BRAIN_SEARCH.py consciousness
    python BRAIN_SEARCH.py "pattern theory"
"""

import sys
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "100X_DEPLOYMENT" / ".cyclotron_atoms" / "cyclotron.db"

def search(query, limit=10):
    """Search the brain for matching content"""
    if not DB_PATH.exists():
        print("❌ Brain not initialized. Run CYCLOTRON_CONTENT_INDEXER.py first.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # FTS5 search with ranking
    cur.execute("""
        SELECT name, type, preview, rank
        FROM knowledge
        WHERE knowledge MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit))

    results = cur.fetchall()

    if not results:
        print(f"No results for: {query}")
        return

    print(f"🔍 Results for: {query}")
    print("=" * 60)

    for i, (name, ftype, preview, rank) in enumerate(results, 1):
        # Clean preview
        preview_clean = preview[:150].replace('\n', ' ').strip() if preview else ""
        print(f"\n{i}. [{ftype}] {name}")
        print(f"   {preview_clean}...")

    print(f"\n{'=' * 60}")
    print(f"Found {len(results)} results")
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python BRAIN_SEARCH.py 'search query'")
        print("\nExamples:")
        print("  python BRAIN_SEARCH.py consciousness")
        print("  python BRAIN_SEARCH.py 'pattern theory'")
        print("  python BRAIN_SEARCH.py trinity")
        return

    query = " ".join(sys.argv[1:])
    search(query)

if __name__ == "__main__":
    main()
