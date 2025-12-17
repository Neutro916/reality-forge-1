#!/usr/bin/env python3
"""
ATOM_CLEANER.py
===============
Removes duplicate and low-quality atoms from the Cyclotron brain.
Run ATOM_QUALITY_AUDITOR.py first to see what will be cleaned.

Created by: CP1 C1 Lead
Purpose: Make the brain LIGHTER, FASTER, STRONGER, MORE ELEGANT
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'

def get_db_path():
    """Find atoms.db"""
    paths = [
        CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db',
        CONSCIOUSNESS / 'atoms.db',
        HOME / '100X_DEPLOYMENT' / '.cyclotron_atoms' / 'cyclotron.db',
    ]
    for p in paths:
        if p.exists():
            return p
    return None

def hash_content(content):
    """Create hash for duplicate detection"""
    if not content:
        return None
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

def count_unique_tokens(content):
    """Count unique meaningful tokens"""
    if not content:
        return 0
    words = set(content.lower().split())
    stopwords = {'the','a','an','is','are','was','were','be','been','being',
                 'have','has','had','do','does','did','will','would','could',
                 'should','may','might','must','shall','can','need','dare',
                 'to','of','in','for','on','with','at','by','from','as','or',
                 'and','but','if','then','else','when','up','down','out','so'}
    return len(words - stopwords)

def clean_atoms(db_path, dry_run=True, remove_duplicates=True,
                remove_low_density=False, min_tokens=5):
    """
    Clean atoms database.

    Args:
        db_path: Path to atoms.db
        dry_run: If True, only report what would be deleted
        remove_duplicates: Remove duplicate content atoms
        remove_low_density: Remove atoms with < min_tokens
        min_tokens: Minimum tokens to keep (if remove_low_density=True)
    """
    print("=" * 60)
    print("ATOM CLEANER")
    print(f"Database: {db_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE - WILL DELETE'}")
    print("=" * 60)
    print()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get schema
    cursor.execute("PRAGMA table_info(atoms)")
    columns = [r[1] for r in cursor.fetchall()]
    content_col = 'content' if 'content' in columns else columns[2] if len(columns) > 2 else None

    if not content_col:
        print("ERROR: Cannot find content column")
        return None

    # Get total before
    cursor.execute("SELECT COUNT(*) FROM atoms")
    total_before = cursor.fetchone()[0]
    print(f"Total atoms before: {total_before:,}")

    # Load all atoms
    cursor.execute(f"SELECT id, {content_col} FROM atoms")
    atoms = cursor.fetchall()

    to_delete = set()
    seen_hashes = {}

    for atom_id, content in atoms:
        if not content:
            continue

        # Check for duplicates
        if remove_duplicates:
            h = hash_content(content)
            if h in seen_hashes:
                to_delete.add(atom_id)  # Keep first, delete subsequent
            else:
                seen_hashes[h] = atom_id

        # Check for low density
        if remove_low_density:
            tokens = count_unique_tokens(content)
            if tokens < min_tokens:
                to_delete.add(atom_id)

    print(f"Atoms to delete: {len(to_delete):,}")
    print()

    if len(to_delete) == 0:
        print("Nothing to clean!")
        conn.close()
        return {"deleted": 0, "remaining": total_before}

    if dry_run:
        print("DRY RUN - No changes made")
        print(f"Would delete {len(to_delete)} atoms")
        print(f"Would keep {total_before - len(to_delete)} atoms")
    else:
        print("Deleting atoms...")

        # Delete in batches
        delete_list = list(to_delete)
        batch_size = 100
        for i in range(0, len(delete_list), batch_size):
            batch = delete_list[i:i+batch_size]
            placeholders = ','.join('?' * len(batch))
            cursor.execute(f"DELETE FROM atoms WHERE id IN ({placeholders})", batch)

        conn.commit()

        # Get total after
        cursor.execute("SELECT COUNT(*) FROM atoms")
        total_after = cursor.fetchone()[0]

        print(f"Deleted: {len(to_delete):,}")
        print(f"Remaining: {total_after:,}")
        print(f"Reduction: {round((len(to_delete)/total_before)*100, 1)}%")

    conn.close()

    results = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "total_before": total_before,
        "deleted": len(to_delete) if not dry_run else 0,
        "would_delete": len(to_delete),
        "remaining": total_before - len(to_delete)
    }

    # Save report
    report_path = CONSCIOUSNESS / 'ATOM_CLEAN_REPORT.json'
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nReport saved: {report_path}")

    return results

if __name__ == '__main__':
    db_path = get_db_path()

    if not db_path:
        print("ERROR: No atoms.db found")
        sys.exit(1)

    # Parse args
    dry_run = '--live' not in sys.argv
    remove_low = '--low-density' in sys.argv

    if not dry_run:
        print("WARNING: LIVE MODE - This will delete atoms!")
        confirm = input("Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    clean_atoms(db_path, dry_run=dry_run, remove_low_density=remove_low)

    print()
    print("=" * 60)
    print("To actually delete, run: python ATOM_CLEANER.py --live")
    print("To also remove low-density: python ATOM_CLEANER.py --live --low-density")
    print("=" * 60)
