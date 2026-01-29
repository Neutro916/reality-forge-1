#!/usr/bin/env python3
"""
ATOM INDEX BUILDER - Zero Latency Supercharger
Creates SQLite FTS5 index for instant atom search across 4397+ atoms.

This eliminates the #1 bottleneck: sequential file reads.
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
ATOMS_DIR = CONSCIOUSNESS / "cyclotron_core" / "atoms"
INDEX_DB = CONSCIOUSNESS / "memory" / "atom_index.db"

def create_index_db():
    """Create the FTS5-enabled index database."""
    conn = sqlite3.connect(str(INDEX_DB))
    cur = conn.cursor()

    # Main atoms table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS atoms (
            id TEXT PRIMARY KEY,
            file_path TEXT,
            source TEXT,
            title TEXT,
            content TEXT,
            keywords TEXT,
            content_hash TEXT,
            created_at TEXT,
            indexed_at TEXT,
            access_count INTEGER DEFAULT 0,
            pattern_score REAL DEFAULT 0.0
        )
    ''')

    # FTS5 virtual table for full-text search
    cur.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS atoms_fts USING fts5(
            id,
            title,
            content,
            keywords,
            content='atoms',
            content_rowid='rowid'
        )
    ''')

    # Triggers to keep FTS in sync
    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS atoms_ai AFTER INSERT ON atoms BEGIN
            INSERT INTO atoms_fts(rowid, id, title, content, keywords)
            VALUES (new.rowid, new.id, new.title, new.content, new.keywords);
        END
    ''')

    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS atoms_ad AFTER DELETE ON atoms BEGIN
            INSERT INTO atoms_fts(atoms_fts, rowid, id, title, content, keywords)
            VALUES('delete', old.rowid, old.id, old.title, old.content, old.keywords);
        END
    ''')

    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS atoms_au AFTER UPDATE ON atoms BEGIN
            INSERT INTO atoms_fts(atoms_fts, rowid, id, title, content, keywords)
            VALUES('delete', old.rowid, old.id, old.title, old.content, old.keywords);
            INSERT INTO atoms_fts(rowid, id, title, content, keywords)
            VALUES (new.rowid, new.id, new.title, new.content, new.keywords);
        END
    ''')

    # Keyword index for fast lookup
    cur.execute('''
        CREATE TABLE IF NOT EXISTS keyword_index (
            keyword TEXT,
            atom_id TEXT,
            frequency INTEGER DEFAULT 1,
            PRIMARY KEY (keyword, atom_id)
        )
    ''')

    cur.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_index(keyword)')

    # Source index
    cur.execute('''
        CREATE TABLE IF NOT EXISTS source_index (
            source TEXT PRIMARY KEY,
            atom_count INTEGER DEFAULT 0,
            last_updated TEXT
        )
    ''')

    conn.commit()
    return conn

def extract_content(atom: Dict) -> str:
    """Extract searchable content from atom."""
    parts = []
    for key in ['title', 'content', 'summary', 'description', 'text', 'data']:
        if key in atom:
            val = atom[key]
            if isinstance(val, str):
                parts.append(val)
            elif isinstance(val, dict):
                parts.append(json.dumps(val))
    return ' '.join(parts)

def extract_keywords(content: str) -> List[str]:
    """Extract keywords from content."""
    import re
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    # Count frequency
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    # Return top keywords
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, c in sorted_words[:20]]

def index_atom(conn, atom_file: Path) -> bool:
    """Index a single atom file."""
    try:
        with open(atom_file, 'r', encoding='utf-8') as f:
            atom = json.load(f)

        atom_id = atom_file.stem
        content = extract_content(atom)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        keywords = extract_keywords(content)

        cur = conn.cursor()

        # Check if already indexed with same hash
        cur.execute('SELECT content_hash FROM atoms WHERE id = ?', (atom_id,))
        existing = cur.fetchone()
        if existing and existing[0] == content_hash:
            return False  # Already indexed, no change

        # Insert or replace
        cur.execute('''
            INSERT OR REPLACE INTO atoms
            (id, file_path, source, title, content, keywords, content_hash, created_at, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            atom_id,
            str(atom_file),
            atom.get('source', 'unknown'),
            atom.get('title', atom.get('source', 'untitled')),
            content[:10000],  # Limit content size
            ','.join(keywords),
            content_hash,
            atom.get('created', atom.get('timestamp', '')),
            datetime.now().isoformat()
        ))

        # Update keyword index
        for kw in keywords:
            cur.execute('''
                INSERT OR REPLACE INTO keyword_index (keyword, atom_id, frequency)
                VALUES (?, ?, COALESCE((SELECT frequency FROM keyword_index WHERE keyword=? AND atom_id=?), 0) + 1)
            ''', (kw, atom_id, kw, atom_id))

        # Update source index
        source = atom.get('source', 'unknown')
        cur.execute('''
            INSERT OR REPLACE INTO source_index (source, atom_count, last_updated)
            VALUES (?, COALESCE((SELECT atom_count FROM source_index WHERE source=?), 0) + 1, ?)
        ''', (source, source, datetime.now().isoformat()))

        return True

    except Exception as e:
        print(f"Error indexing {atom_file.name}: {e}")
        return False

def build_full_index():
    """Build index for all atoms."""
    print("=" * 60)
    print("ATOM INDEX BUILDER - Zero Latency Supercharger")
    print("=" * 60)

    if not ATOMS_DIR.exists():
        print(f"ERROR: Atoms directory not found: {ATOMS_DIR}")
        return

    conn = create_index_db()

    atom_files = list(ATOMS_DIR.glob("*.json"))
    total = len(atom_files)
    indexed = 0
    skipped = 0

    print(f"Found {total} atom files")
    print(f"Index DB: {INDEX_DB}")
    print()

    for i, atom_file in enumerate(atom_files):
        if index_atom(conn, atom_file):
            indexed += 1
        else:
            skipped += 1

        if (i + 1) % 500 == 0:
            conn.commit()
            print(f"Progress: {i+1}/{total} ({indexed} indexed, {skipped} unchanged)")

    conn.commit()

    # Get stats
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM atoms')
    atom_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(DISTINCT keyword) FROM keyword_index')
    keyword_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM source_index')
    source_count = cur.fetchone()[0]

    conn.close()

    print()
    print("=" * 60)
    print("INDEX BUILD COMPLETE")
    print("=" * 60)
    print(f"Atoms indexed: {atom_count}")
    print(f"Unique keywords: {keyword_count}")
    print(f"Sources: {source_count}")
    print(f"New/Updated: {indexed}")
    print(f"Unchanged: {skipped}")
    print()
    print(f"Index saved to: {INDEX_DB}")

def search_atoms(query: str, limit: int = 10) -> List[Dict]:
    """Fast FTS5 search across all atoms."""
    conn = sqlite3.connect(str(INDEX_DB))
    cur = conn.cursor()

    # FTS5 search
    cur.execute('''
        SELECT a.id, a.title, a.source, a.keywords,
               snippet(atoms_fts, 2, '<b>', '</b>', '...', 32) as snippet
        FROM atoms_fts
        JOIN atoms a ON atoms_fts.id = a.id
        WHERE atoms_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    ''', (query, limit))

    results = []
    for row in cur.fetchall():
        results.append({
            'id': row[0],
            'title': row[1],
            'source': row[2],
            'keywords': row[3],
            'snippet': row[4]
        })

    # Update access counts
    for r in results:
        cur.execute('UPDATE atoms SET access_count = access_count + 1 WHERE id = ?', (r['id'],))

    conn.commit()
    conn.close()

    return results

def search_by_keyword(keyword: str, limit: int = 20) -> List[str]:
    """Fast keyword lookup."""
    conn = sqlite3.connect(str(INDEX_DB))
    cur = conn.cursor()

    cur.execute('''
        SELECT atom_id FROM keyword_index
        WHERE keyword = ?
        ORDER BY frequency DESC
        LIMIT ?
    ''', (keyword.lower(), limit))

    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results

def get_stats() -> Dict:
    """Get index statistics."""
    conn = sqlite3.connect(str(INDEX_DB))
    cur = conn.cursor()

    stats = {}
    cur.execute('SELECT COUNT(*) FROM atoms')
    stats['total_atoms'] = cur.fetchone()[0]

    cur.execute('SELECT COUNT(DISTINCT keyword) FROM keyword_index')
    stats['unique_keywords'] = cur.fetchone()[0]

    cur.execute('SELECT SUM(access_count) FROM atoms')
    stats['total_accesses'] = cur.fetchone()[0] or 0

    cur.execute('SELECT id, title, access_count FROM atoms ORDER BY access_count DESC LIMIT 5')
    stats['hot_atoms'] = [{'id': r[0], 'title': r[1], 'accesses': r[2]} for r in cur.fetchall()]

    conn.close()
    return stats

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "search" and len(sys.argv) > 2:
            query = ' '.join(sys.argv[2:])
            results = search_atoms(query)
            print(f"Found {len(results)} results for '{query}':")
            for r in results:
                print(f"  [{r['id'][:8]}] {r['title'][:50]}")
        elif cmd == "stats":
            stats = get_stats()
            print(json.dumps(stats, indent=2))
        else:
            print("Usage:")
            print("  python ATOM_INDEX_BUILDER.py        - Build full index")
            print("  python ATOM_INDEX_BUILDER.py search <query>  - Search atoms")
            print("  python ATOM_INDEX_BUILDER.py stats  - Show statistics")
    else:
        build_full_index()
