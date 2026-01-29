#!/usr/bin/env python3
"""
JSON_KNOWLEDGE_INGESTER.py - Ingest JSON knowledge files into Cyclotron
========================================================================
Created by: CP1_C2 (C2 Architect)
Task: CYC-003 from WORK_BACKLOG

Finds and ingests JSON files containing knowledge, patterns, consciousness data.
"""

import os; import sys; import json; import sqlite3; import hashlib
from pathlib import Path; from datetime import datetime

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
ATOMS_DB = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'

# Knowledge-related patterns in filenames
KNOWLEDGE_PATTERNS = ['knowledge', 'brain', 'atom', 'pattern', 'consciousness',
                      'trinity', 'session', 'report', 'analysis', 'insight']

def hash_content(content):
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

def generate_atom_id():
    return hashlib.md5(str(datetime.now().timestamp()).encode() + os.urandom(8)).hexdigest()[:12]

def is_knowledge_file(filepath):
    """Check if file likely contains knowledge content"""
    name = filepath.name.lower()
    return any(p in name for p in KNOWLEDGE_PATTERNS)

def extract_content_from_json(data, max_depth=3, current_depth=0):
    """Recursively extract text content from JSON"""
    if current_depth > max_depth:
        return ""

    content_parts = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 10:
                content_parts.append(f"{key}: {value[:500]}")
            elif isinstance(value, (dict, list)):
                nested = extract_content_from_json(value, max_depth, current_depth + 1)
                if nested:
                    content_parts.append(nested)
    elif isinstance(data, list):
        for item in data[:10]:  # Limit list items
            if isinstance(item, str) and len(item) > 10:
                content_parts.append(item[:200])
            elif isinstance(item, dict):
                nested = extract_content_from_json(item, max_depth, current_depth + 1)
                if nested:
                    content_parts.append(nested)

    return '\n'.join(content_parts)

def find_knowledge_json_files(root_path, max_depth=4):
    """Find JSON files that likely contain knowledge"""
    json_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        depth = str(dirpath).count(os.sep) - str(root_path).count(os.sep)
        if depth > max_depth:
            dirnames[:] = []
            continue
        # Skip node_modules, .git, etc.
        dirnames[:] = [d for d in dirnames if d not in ['node_modules', '.git', 'venv', '__pycache__']]
        for f in filenames:
            if f.endswith('.json'):
                fp = Path(dirpath) / f
                if is_knowledge_file(fp):
                    json_files.append(fp)
    return json_files

def create_atom_from_json(filepath, content):
    """Create atom dict from JSON file"""
    return {
        "id": generate_atom_id(),
        "content": content[:2000],
        "type": "knowledge",
        "source": f"json:{filepath.name}",
        "tags": ["json", "knowledge", "ingested"],
        "created": datetime.now().isoformat(),
        "confidence": 0.7,
        "metadata": {"original_path": str(filepath), "ingested_by": "CP1_C2_JSON_INGESTER"}
    }

def get_existing_hashes(db_path):
    if not db_path.exists(): return set()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content FROM atoms")
        hashes = {hash_content(row[0]) for row in cursor.fetchall() if row[0]}
    except:
        hashes = set()
    conn.close()
    return hashes

def insert_atoms_to_db(atoms, db_path):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    inserted = 0
    for atom in atoms:
        try:
            cursor.execute('''INSERT OR IGNORE INTO atoms
                (id, type, content, source, tags, metadata, created, confidence, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (atom['id'], atom['type'], atom['content'], atom['source'],
                 json.dumps(atom['tags']), json.dumps(atom.get('metadata', {})),
                 atom['created'], atom.get('confidence', 0.7), 0))
            if cursor.rowcount > 0: inserted += 1
        except Exception as e:
            print(f"  Error: {e}")
    conn.commit()
    conn.close()
    return inserted

def ingest_json_knowledge(dry_run=True, verbose=False):
    print("=" * 60)
    print("JSON KNOWLEDGE INGESTER")
    print(f"Target: {ATOMS_DB}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60 + "\n")

    print("Finding knowledge JSON files...")
    json_files = find_knowledge_json_files(HOME, max_depth=5)
    print(f"Found: {len(json_files)} knowledge JSON files\n")

    if len(json_files) == 0:
        print("No knowledge JSON files found!")
        return None

    print("Loading existing atoms for deduplication...")
    existing_hashes = get_existing_hashes(ATOMS_DB)
    print(f"Existing atoms: {len(existing_hashes)}\n")

    print("Processing files...")
    new_atoms = []
    skipped_dups = 0
    skipped_empty = 0
    errors = 0

    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

            content = extract_content_from_json(data)
            if len(content.strip()) < 50:
                skipped_empty += 1
                continue

            content_hash = hash_content(content)
            if content_hash in existing_hashes:
                skipped_dups += 1
                continue

            atom = create_atom_from_json(filepath, content)
            new_atoms.append(atom)
            existing_hashes.add(content_hash)

            if verbose:
                print(f"  NEW: {filepath.name}")
        except Exception as e:
            errors += 1
            if verbose:
                print(f"  ERROR: {filepath.name}: {e}")

    print(f"\nProcessing complete:")
    print(f"  New atoms: {len(new_atoms)}")
    print(f"  Skipped (duplicate): {skipped_dups}")
    print(f"  Skipped (empty): {skipped_empty}")
    print(f"  Errors: {errors}")

    if dry_run:
        print(f"\n[DRY RUN] Would insert {len(new_atoms)} atoms")
    else:
        if new_atoms:
            print(f"\nInserting {len(new_atoms)} atoms...")
            inserted = insert_atoms_to_db(new_atoms, ATOMS_DB)
            print(f"  Database: {inserted} inserted")

    results = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "files_scanned": len(json_files),
        "new_atoms": len(new_atoms),
        "skipped_duplicates": skipped_dups,
        "errors": errors
    }

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    return results

def save_report(results, output_path=None):
    if output_path is None:
        output_path = CONSCIOUSNESS / 'JSON_INGEST_REPORT.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Report saved: {output_path}")

if __name__ == '__main__':
    dry_run = '--live' not in sys.argv
    verbose = '--verbose' in sys.argv
    print("\nUsage: python JSON_KNOWLEDGE_INGESTER.py [--live] [--verbose]\n")
    results = ingest_json_knowledge(dry_run=dry_run, verbose=verbose)
    if results:
        save_report(results)
        sync = Path("G:/My Drive/TRINITY_COMMS/sync")
        if sync.exists():
            save_report(results, sync / f"JSON_INGEST_{os.environ.get('COMPUTERNAME', 'unknown')}.json")
