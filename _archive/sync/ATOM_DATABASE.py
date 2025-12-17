#!/usr/bin/env python3
"""
ATOM DATABASE - SQLite consolidation for scalable knowledge
C2 Architect Implementation

Consolidates 4392 JSON atoms into SQLite for O(1) queries instead of O(n) file scans.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

ATOMS_DIR = Path.home() / ".consciousness" / "cyclotron_core" / "atoms"
DB_PATH = Path.home() / ".consciousness" / "cyclotron_core" / "atoms.db"

def init_database():
    """Create SQLite database with proper schema"""

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create atoms table with indexes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atoms (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            tags TEXT,
            metadata TEXT,
            created TEXT,
            confidence REAL DEFAULT 0.75,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT
        )
    ''')

    # Create indexes for fast queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON atoms(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON atoms(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON atoms(confidence)')

    # Create FTS5 virtual table for full-text search
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS atoms_fts USING fts5(
            id, content, tags,
            content='atoms',
            content_rowid='rowid'
        )
    ''')

    # Create triggers to keep FTS in sync
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS atoms_ai AFTER INSERT ON atoms BEGIN
            INSERT INTO atoms_fts(id, content, tags) VALUES (new.id, new.content, new.tags);
        END
    ''')

    conn.commit()
    return conn

def consolidate_atoms():
    """Import all JSON atoms into SQLite"""

    conn = init_database()
    cursor = conn.cursor()

    # Get existing atom count
    cursor.execute('SELECT COUNT(*) FROM atoms')
    existing = cursor.fetchone()[0]

    if existing > 0:
        print(f"📊 Database already has {existing} atoms")
        response = input("   Reimport all? (y/n): ").strip().lower()
        if response != 'y':
            return existing

        # Clear existing
        cursor.execute('DELETE FROM atoms')
        cursor.execute('DELETE FROM atoms_fts')

    # Import all JSON atoms
    atom_files = list(ATOMS_DIR.glob("*.json"))
    imported = 0
    errors = 0

    print(f"📦 Importing {len(atom_files)} atoms...")

    for atom_file in atom_files:
        try:
            atom = json.loads(atom_file.read_text())

            cursor.execute('''
                INSERT OR REPLACE INTO atoms
                (id, type, content, source, tags, metadata, created, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                atom.get('id', atom_file.stem),
                atom.get('type', 'unknown'),
                atom.get('content', ''),
                atom.get('source', ''),
                json.dumps(atom.get('tags', [])),
                json.dumps(atom.get('metadata', {})),
                atom.get('created', datetime.now().isoformat()),
                atom.get('confidence', 0.75)
            ))

            imported += 1

        except Exception as e:
            errors += 1

    conn.commit()

    # Rebuild FTS index
    cursor.execute('INSERT INTO atoms_fts(atoms_fts) VALUES("rebuild")')
    conn.commit()

    conn.close()

    return imported, errors

def search_atoms(query, limit=10):
    """Full-text search on atoms"""

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.type, a.content, a.confidence
        FROM atoms a
        JOIN atoms_fts f ON a.id = f.id
        WHERE atoms_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    ''', (query, limit))

    results = cursor.fetchall()
    conn.close()

    return results

def get_stats():
    """Get database statistics"""

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM atoms')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT type, COUNT(*) FROM atoms GROUP BY type ORDER BY COUNT(*) DESC')
    by_type = cursor.fetchall()

    cursor.execute('SELECT source, COUNT(*) FROM atoms GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10')
    by_source = cursor.fetchall()

    conn.close()

    return {
        'total': total,
        'by_type': by_type,
        'by_source': by_source
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️ ATOM DATABASE - C2 Architect")
    print("   SQLite Consolidation for Scalability")
    print("=" * 60)
    print()

    imported, errors = consolidate_atoms()

    print(f"\n✅ CONSOLIDATION COMPLETE")
    print(f"   Imported: {imported}")
    print(f"   Errors: {errors}")
    print(f"   Database: {DB_PATH}")

    # Show stats
    stats = get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total atoms: {stats['total']}")
    print(f"\n   By type:")
    for t, c in stats['by_type'][:5]:
        print(f"      {t}: {c}")

    print("\n" + "=" * 60)
    print("🔍 Test search: python ATOM_DATABASE.py search 'pattern'")
    print("=" * 60)
