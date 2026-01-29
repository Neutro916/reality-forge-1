#!/usr/bin/env python3
"""
INGEST_JSON_KNOWLEDGE.py - Ingest JSON files with knowledge content
Created by CP3C1 - 2025-11-27

Task: CYC-003 from WORK_BACKLOG
Finds JSON files containing knowledge and adds them to Cyclotron brain
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
import re

# Paths
CYCLOTRON_DB = Path(r"C:\Users\Darrick\.consciousness\cyclotron_core\atoms.db")
ROOT_DIR = Path(r"C:\Users\Darrick")

# Skip these directories (node_modules, AppData, etc.)
SKIP_DIRS = {
    'node_modules', 'AppData', '.git', '__pycache__', 'venv',
    '.local', 'Cache', 'Temp', 'tmp', 'package-lock'
}

def get_existing_ids(conn):
    """Get all existing atom IDs"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM atoms")
    return set(row[0] for row in cursor.fetchall())

def generate_id(filepath):
    """Generate unique ID from filepath"""
    return hashlib.md5(str(filepath).encode()).hexdigest()[:12]

def is_knowledge_json(filepath, content):
    """Check if JSON file contains knowledge content"""
    name = filepath.name.lower()

    # Likely knowledge files based on name
    knowledge_patterns = [
        'knowledge', 'brain', 'pattern', 'atom', 'index', 'config',
        'manifest', 'metadata', 'schema', 'blueprint', 'framework',
        'protocol', 'audit', 'report', 'status', 'session', 'work'
    ]

    if any(p in name for p in knowledge_patterns):
        return True

    # Check content structure
    try:
        data = json.loads(content)

        # Has meaningful structure
        if isinstance(data, dict):
            # Has title or description
            if 'title' in data or 'description' in data or 'name' in data:
                return True
            # Has patterns or knowledge
            if 'patterns' in data or 'knowledge' in data or 'atoms' in data:
                return True
            # Has metadata
            if 'metadata' in data or 'created' in data or 'generated' in data:
                return True
            # Has significant string content
            str_values = sum(1 for v in data.values() if isinstance(v, str) and len(v) > 50)
            if str_values >= 2:
                return True

        # Array with meaningful items
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                return True

    except:
        pass

    return False

def extract_json_metadata(content, filepath):
    """Extract metadata from JSON content"""
    try:
        data = json.loads(content)
    except:
        return None

    title = filepath.stem
    preview = ""
    categories = ['json-knowledge']
    keywords = []

    if isinstance(data, dict):
        # Extract title
        for key in ['title', 'name', 'description', 'id']:
            if key in data and isinstance(data[key], str):
                title = data[key][:200]
                break

        # Extract preview
        for key in ['description', 'summary', 'content', 'preview']:
            if key in data and isinstance(data[key], str):
                preview = data[key][:1000]
                break

        # Build preview from all string values if no description
        if not preview:
            str_parts = []
            for k, v in data.items():
                if isinstance(v, str) and len(v) > 10:
                    str_parts.append(f"{k}: {v[:100]}")
            preview = " | ".join(str_parts)[:1000]

        # Extract keywords from keys
        keywords = [k for k in data.keys() if isinstance(k, str)][:10]

        # Categorize based on content
        data_str = json.dumps(data).lower()
        if 'trinity' in data_str:
            categories.append('trinity')
        if 'pattern' in data_str:
            categories.append('patterns')
        if 'cyclotron' in data_str or 'brain' in data_str:
            categories.append('cyclotron')
        if 'session' in data_str or 'audit' in data_str:
            categories.append('audit')

    elif isinstance(data, list):
        preview = f"Array with {len(data)} items"
        if len(data) > 0 and isinstance(data[0], dict):
            keywords = list(data[0].keys())[:10]

    return {
        'title': title,
        'preview': preview[:2000],
        'categories': ','.join(categories),
        'keywords': ','.join(keywords),
        'priority': 6  # Medium priority for JSON
    }

def should_skip(path):
    """Check if path should be skipped"""
    parts = path.parts
    return any(skip in parts for skip in SKIP_DIRS)

def main():
    print("="*60)
    print("JSON KNOWLEDGE INGEST")
    print("CP3C1 - Task CYC-003")
    print("="*60)

    if not CYCLOTRON_DB.exists():
        print(f"ERROR: Database not found at {CYCLOTRON_DB}")
        return

    conn = sqlite3.connect(str(CYCLOTRON_DB))
    existing_ids = get_existing_ids(conn)
    cursor = conn.cursor()

    print(f"\nExisting atoms: {len(existing_ids)}")
    print("Scanning for JSON knowledge files...")

    added = 0
    skipped = 0
    scanned = 0

    # Find JSON files
    for filepath in ROOT_DIR.rglob('*.json'):
        if should_skip(filepath):
            continue

        scanned += 1
        if scanned % 500 == 0:
            print(f"  Scanned {scanned} files...")

        # Skip large files (> 500KB)
        try:
            if filepath.stat().st_size > 500000:
                continue
            if filepath.stat().st_size < 100:  # Skip tiny files
                continue
        except:
            continue

        atom_id = generate_id(filepath)
        if atom_id in existing_ids:
            skipped += 1
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
        except:
            try:
                content = filepath.read_text(encoding='latin-1')
            except:
                continue

        # Check if it's knowledge content
        if not is_knowledge_json(filepath, content):
            continue

        # Extract metadata
        meta = extract_json_metadata(content, filepath)
        if not meta:
            continue

        # Insert into database
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO atoms
                (id, title, filepath, content_preview, categories, keywords,
                 priority, created_at, file_size, directory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                atom_id,
                meta['title'],
                str(filepath),
                meta['preview'],
                meta['categories'],
                meta['keywords'],
                meta['priority'],
                datetime.now().isoformat(),
                len(content),
                str(filepath.parent)
            ))

            # Add to FTS
            cursor.execute('''
                INSERT OR REPLACE INTO atoms_fts (rowid, title, content_preview, keywords, categories)
                SELECT rowid, title, content_preview, keywords, categories FROM atoms WHERE id = ?
            ''', (atom_id,))

            existing_ids.add(atom_id)
            added += 1

            if added % 50 == 0:
                print(f"  Added {added} JSON knowledge atoms...")
                conn.commit()

        except Exception as e:
            pass

    conn.commit()

    # Final count
    cursor.execute("SELECT COUNT(*) FROM atoms")
    final_count = cursor.fetchone()[0]
    conn.close()

    print("\n" + "="*60)
    print("JSON INGEST COMPLETE")
    print("="*60)
    print(f"Files scanned: {scanned}")
    print(f"JSON atoms added: {added}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"\nFinal atom count: {final_count}")

if __name__ == "__main__":
    main()
