#!/usr/bin/env python3
"""
GOOGLE_DRIVE_MD_INGESTER.py - Ingest Google Drive MD files into Cyclotron
=========================================================================
Created by: CP1_C2 (C2 Architect)
Task: CYC-001 from WORK_BACKLOG

Purpose:
1. Find all .md files in Google Drive
2. Convert to atom format (JSON)
3. Add to Cyclotron database (atoms.db)
4. Deduplicate using content hash

Usage:
  python GOOGLE_DRIVE_MD_INGESTER.py [--dry-run] [--verbose]
"""

import os; import sys; import json; import sqlite3; import hashlib
from pathlib import Path; from datetime import datetime

# Paths
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
GDRIVE = Path("G:/My Drive")
CONSCIOUSNESS = HOME / '.consciousness'
ATOMS_DB = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
ATOMS_DIR = CONSCIOUSNESS / 'cyclotron_core' / 'atoms'

def hash_content(content):
    """Create MD5 hash for deduplication"""
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

def generate_atom_id():
    """Generate unique 12-char hex atom ID"""
    return hashlib.md5(str(datetime.now().timestamp()).encode() + os.urandom(8)).hexdigest()[:12]

def extract_title(content, filepath):
    """Extract title from MD content or filename"""
    lines = content.split('\n')
    for line in lines[:5]:
        if line.startswith('# '):
            return line[2:].strip()
    return filepath.stem.replace('_', ' ').replace('-', ' ')

def extract_tags(content, filepath):
    """Extract relevant tags from content and path"""
    tags = []
    path_parts = str(filepath).lower()

    # Add source tag
    if 'trinity' in path_parts: tags.append('trinity')
    if 'sync' in path_parts: tags.append('sync')
    if 'consciousness' in path_parts: tags.append('consciousness')
    if 'pattern' in path_parts: tags.append('pattern_theory')
    if 'domain' in path_parts: tags.append('seven_domains')

    # Add content-based tags
    content_lower = content.lower()
    if 'c1' in content_lower or 'c2' in content_lower or 'c3' in content_lower:
        tags.append('trinity_instance')
    if 'overkore' in content_lower: tags.append('overkore')
    if 'fibonacci' in content_lower: tags.append('fibonacci')
    if 'manipulation' in content_lower: tags.append('manipulation')

    tags.append('google_drive')
    tags.append('markdown')
    return list(set(tags))

def find_md_files(root_path, max_depth=4):
    """Find all MD files up to max_depth"""
    md_files = []
    for i, (dirpath, dirnames, filenames) in enumerate(os.walk(root_path)):
        depth = str(dirpath).count(os.sep) - str(root_path).count(os.sep)
        if depth > max_depth:
            dirnames[:] = []  # Don't recurse deeper
            continue
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(Path(dirpath) / f)
    return md_files

def create_atom_from_md(filepath, content):
    """Create atom dict from MD file"""
    return {
        "id": generate_atom_id(),
        "content": content[:2000],  # Truncate long content
        "type": "knowledge",
        "source": f"gdrive:{filepath.name}",
        "title": extract_title(content, filepath),
        "tags": extract_tags(content, filepath),
        "links": [],
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "confidence": 0.8,
        "usage_count": 0,
        "metadata": {
            "original_path": str(filepath),
            "file_size": len(content),
            "ingested_by": "CP1_C2_INGESTER"
        }
    }

def get_existing_hashes(db_path):
    """Get all existing content hashes from database"""
    if not db_path.exists():
        return set()
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
    """Insert atoms into SQLite database - matches existing schema"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Use existing schema: id, type, content, source, tags, metadata, created, confidence, access_count, last_accessed
    inserted = 0
    for atom in atoms:
        try:
            cursor.execute('''INSERT OR IGNORE INTO atoms
                (id, type, content, source, tags, metadata, created, confidence, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (atom['id'], atom['type'], atom['content'], atom['source'],
                 json.dumps(atom['tags']), json.dumps(atom.get('metadata', {})),
                 atom['created'], atom.get('confidence', 0.8), 0))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"  Error inserting {atom['id']}: {e}")

    conn.commit()
    conn.close()
    return inserted

def save_atom_files(atoms, atoms_dir):
    """Save atoms as individual JSON files"""
    atoms_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for atom in atoms:
        atom_file = atoms_dir / f"{atom['id']}.json"
        if not atom_file.exists():
            with open(atom_file, 'w') as f:
                json.dump(atom, f, indent=2)
            saved += 1
    return saved

def ingest_google_drive(dry_run=True, verbose=False):
    """Main ingestion function"""
    print("=" * 60)
    print("GOOGLE DRIVE MD INGESTER")
    print(f"Source: {GDRIVE}")
    print(f"Target: {ATOMS_DB}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60 + "\n")

    # Find MD files
    print("Finding MD files...")
    md_files = find_md_files(GDRIVE, max_depth=4)
    print(f"Found: {len(md_files)} MD files\n")

    if len(md_files) == 0:
        print("No MD files found!")
        return None

    # Get existing hashes for deduplication
    print("Loading existing atoms for deduplication...")
    existing_hashes = get_existing_hashes(ATOMS_DB)
    print(f"Existing atoms: {len(existing_hashes)}\n")

    # Process files
    print("Processing files...")
    new_atoms = []
    skipped_dups = 0
    skipped_empty = 0
    errors = 0

    for filepath in md_files:
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            if len(content.strip()) < 20:
                skipped_empty += 1
                continue

            content_hash = hash_content(content)
            if content_hash in existing_hashes:
                skipped_dups += 1
                if verbose:
                    print(f"  SKIP (dup): {filepath.name}")
                continue

            atom = create_atom_from_md(filepath, content)
            new_atoms.append(atom)
            existing_hashes.add(content_hash)  # Prevent intra-batch dups

            if verbose:
                print(f"  NEW: {filepath.name} -> {atom['id']}")
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
        # Show sample
        if new_atoms:
            print("\nSample new atoms:")
            for atom in new_atoms[:5]:
                print(f"  - {atom['title'][:50]}... ({atom['source']})")
    else:
        if new_atoms:
            # Insert to database
            print(f"\nInserting {len(new_atoms)} atoms to database...")
            inserted_db = insert_atoms_to_db(new_atoms, ATOMS_DB)
            print(f"  Database: {inserted_db} inserted")

            # Save atom files
            saved_files = save_atom_files(new_atoms, ATOMS_DIR)
            print(f"  Files: {saved_files} saved")
        else:
            print("\nNo new atoms to insert.")

    # Results
    results = {
        "timestamp": datetime.now().isoformat(),
        "source": str(GDRIVE),
        "dry_run": dry_run,
        "files_scanned": len(md_files),
        "new_atoms": len(new_atoms),
        "skipped_duplicates": skipped_dups,
        "skipped_empty": skipped_empty,
        "errors": errors
    }

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)

    return results

def save_report(results, output_path=None):
    """Save ingestion report"""
    if output_path is None:
        output_path = CONSCIOUSNESS / 'GDRIVE_INGEST_REPORT.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Report saved: {output_path}")
    return output_path

if __name__ == '__main__':
    dry_run = '--live' not in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    print("\nUsage: python GOOGLE_DRIVE_MD_INGESTER.py [--live] [--verbose]")
    print("  --live: Actually insert atoms (default is dry run)")
    print("  --verbose: Show each file being processed\n")

    results = ingest_google_drive(dry_run=dry_run, verbose=verbose)

    if results:
        save_report(results)
        sync = Path("G:/My Drive/TRINITY_COMMS/sync")
        if sync.exists():
            save_report(results, sync / f"GDRIVE_INGEST_{os.environ.get('COMPUTERNAME', 'unknown')}.json")
