#!/usr/bin/env python3
"""
ONEDRIVE_MD_INGESTER.py - Ingest OneDrive MD files into Cyclotron
=================================================================
Created by: CP1_C2 (C2 Architect)
Task: CYC-002 from WORK_BACKLOG

Reuses GOOGLE_DRIVE_MD_INGESTER logic for OneDrive.
"""

import os; import sys; import json; import sqlite3; import hashlib
from pathlib import Path; from datetime import datetime

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
ONEDRIVE = HOME / 'OneDrive'
CONSCIOUSNESS = HOME / '.consciousness'
ATOMS_DB = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
ATOMS_DIR = CONSCIOUSNESS / 'cyclotron_core' / 'atoms'

def hash_content(content):
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

def generate_atom_id():
    return hashlib.md5(str(datetime.now().timestamp()).encode() + os.urandom(8)).hexdigest()[:12]

def extract_title(content, filepath):
    lines = content.split('\n')
    for line in lines[:5]:
        if line.startswith('# '):
            return line[2:].strip()
    return filepath.stem.replace('_', ' ').replace('-', ' ')

def extract_tags(content, filepath):
    tags = ['onedrive', 'markdown']
    path_parts = str(filepath).lower()
    if 'trinity' in path_parts: tags.append('trinity')
    if 'consciousness' in path_parts: tags.append('consciousness')
    if 'pattern' in path_parts: tags.append('pattern_theory')
    content_lower = content.lower()
    if 'overkore' in content_lower: tags.append('overkore')
    return list(set(tags))

def find_md_files(root_path, max_depth=4):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        depth = str(dirpath).count(os.sep) - str(root_path).count(os.sep)
        if depth > max_depth:
            dirnames[:] = []
            continue
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(Path(dirpath) / f)
    return md_files

def create_atom_from_md(filepath, content):
    return {
        "id": generate_atom_id(),
        "content": content[:2000],
        "type": "knowledge",
        "source": f"onedrive:{filepath.name}",
        "title": extract_title(content, filepath),
        "tags": extract_tags(content, filepath),
        "created": datetime.now().isoformat(),
        "confidence": 0.8,
        "metadata": {"original_path": str(filepath), "file_size": len(content), "ingested_by": "CP1_C2_INGESTER"}
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
                 atom['created'], atom.get('confidence', 0.8), 0))
            if cursor.rowcount > 0: inserted += 1
        except Exception as e:
            print(f"  Error: {e}")
    conn.commit()
    conn.close()
    return inserted

def save_atom_files(atoms, atoms_dir):
    atoms_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for atom in atoms:
        atom_file = atoms_dir / f"{atom['id']}.json"
        if not atom_file.exists():
            with open(atom_file, 'w') as f:
                json.dump(atom, f, indent=2)
            saved += 1
    return saved

def ingest_onedrive(dry_run=True, verbose=False):
    print("=" * 60)
    print("ONEDRIVE MD INGESTER")
    print(f"Source: {ONEDRIVE}")
    print(f"Target: {ATOMS_DB}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60 + "\n")

    if not ONEDRIVE.exists():
        print(f"ERROR: OneDrive not found at {ONEDRIVE}")
        return None

    print("Finding MD files...")
    md_files = find_md_files(ONEDRIVE, max_depth=4)
    print(f"Found: {len(md_files)} MD files\n")

    if len(md_files) == 0:
        print("No MD files found!")
        return None

    print("Loading existing atoms for deduplication...")
    existing_hashes = get_existing_hashes(ATOMS_DB)
    print(f"Existing atoms: {len(existing_hashes)}\n")

    print("Processing files...")
    new_atoms = []
    skipped_dups = 0
    skipped_empty = 0

    for filepath in md_files:
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            if len(content.strip()) < 20:
                skipped_empty += 1
                continue
            content_hash = hash_content(content)
            if content_hash in existing_hashes:
                skipped_dups += 1
                continue
            atom = create_atom_from_md(filepath, content)
            new_atoms.append(atom)
            existing_hashes.add(content_hash)
        except Exception as e:
            if verbose: print(f"  ERROR: {filepath.name}: {e}")

    print(f"\nProcessing complete:")
    print(f"  New atoms: {len(new_atoms)}")
    print(f"  Skipped (duplicate): {skipped_dups}")
    print(f"  Skipped (empty): {skipped_empty}")

    if dry_run:
        print(f"\n[DRY RUN] Would insert {len(new_atoms)} atoms")
    else:
        if new_atoms:
            print(f"\nInserting {len(new_atoms)} atoms...")
            inserted_db = insert_atoms_to_db(new_atoms, ATOMS_DB)
            print(f"  Database: {inserted_db} inserted")
            saved_files = save_atom_files(new_atoms, ATOMS_DIR)
            print(f"  Files: {saved_files} saved")

    results = {
        "timestamp": datetime.now().isoformat(),
        "source": str(ONEDRIVE),
        "dry_run": dry_run,
        "files_scanned": len(md_files),
        "new_atoms": len(new_atoms),
        "skipped_duplicates": skipped_dups
    }

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    return results

def save_report(results, output_path=None):
    if output_path is None:
        output_path = CONSCIOUSNESS / 'ONEDRIVE_INGEST_REPORT.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Report saved: {output_path}")

if __name__ == '__main__':
    dry_run = '--live' not in sys.argv
    verbose = '--verbose' in sys.argv
    print("\nUsage: python ONEDRIVE_MD_INGESTER.py [--live] [--verbose]\n")
    results = ingest_onedrive(dry_run=dry_run, verbose=verbose)
    if results:
        save_report(results)
        sync = Path("G:/My Drive/TRINITY_COMMS/sync")
        if sync.exists():
            save_report(results, sync / f"ONEDRIVE_INGEST_{os.environ.get('COMPUTERNAME', 'unknown')}.json")
