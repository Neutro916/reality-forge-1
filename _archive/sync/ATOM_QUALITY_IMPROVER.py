#!/usr/bin/env python3
"""
ATOM_QUALITY_IMPROVER.py - Fix issues found by ATOM_QUALITY_AUDITOR
===================================================================
C2 Architect Response to Quality Audit Challenge

Actions:
1. Remove duplicate atoms (keep first occurrence)
2. Remove or flag low-density atoms (<5 tokens)
3. Compact database after cleanup
4. Report improvements

SAFETY: Creates backup before modifications!

Created by: C2 Architect (CP1)
"""

import os; import sys; import json; import sqlite3; import hashlib; import shutil
from pathlib import Path; from datetime import datetime; from collections import defaultdict

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'

def get_db_path():
    for p in [CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db', CONSCIOUSNESS / 'atoms.db', HOME / '100X_DEPLOYMENT' / '.cyclotron_atoms' / 'cyclotron.db']:
        if p.exists(): return p
    return None

def hash_content(content):
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest() if content else None

def count_tokens(content):
    if not content: return 0
    words = set(content.lower().split())
    stopwords = {'the','a','an','is','are','was','were','be','been','being','have','has','had','do','does','did','will','would','could','should','may','might','must','shall','can','need','dare','to','of','in','for','on','with','at','by','from','as','or','and','but','if','then','else','when','up','down','out','so'}
    return len(words - stopwords)

def backup_database(db_path):
    backup = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(db_path, backup)
    print(f"Backup created: {backup}")
    return backup

def improve_quality(db_path, dry_run=True, min_tokens=5):
    print("=" * 60)
    print("ATOM QUALITY IMPROVER")
    print(f"Database: {db_path}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will modify)'}")
    print("=" * 60 + "\n")

    if not dry_run:
        backup_database(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(atoms)")
    columns = [r[1] for r in cursor.fetchall()]
    content_col = 'content' if 'content' in columns else columns[2] if len(columns) > 2 else None
    if not content_col:
        print("ERROR: Cannot find content column"); return None

    cursor.execute(f"SELECT id, {content_col} FROM atoms")
    atoms = cursor.fetchall()
    total_before = len(atoms)
    print(f"Total atoms before: {total_before:,}\n")

    # Find duplicates and low-density
    hashes = defaultdict(list)
    to_delete = set()
    low_density_ids = []

    for atom_id, content in atoms:
        if not content: to_delete.add(atom_id); continue
        h = hash_content(content)
        if h:
            if hashes[h]: to_delete.add(atom_id)  # Keep first, delete rest
            hashes[h].append(atom_id)
        tokens = count_tokens(content)
        if tokens < min_tokens: low_density_ids.append(atom_id)

    dup_count = len([ids for ids in hashes.values() if len(ids) > 1])
    print(f"Duplicate content found: {len(to_delete)} atoms (from {dup_count} unique duplicates)")
    print(f"Low-density atoms (<{min_tokens} tokens): {len(low_density_ids)}")

    # Decide what to delete
    delete_ids = to_delete  # Always delete exact duplicates
    # For low-density, only delete if also a duplicate OR if very low (<3 tokens)
    for lid in low_density_ids:
        content = next((c for i, c in atoms if i == lid), None)
        if content and count_tokens(content) < 3: delete_ids.add(lid)

    print(f"\nAtoms to delete: {len(delete_ids)}")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        print(f"Would delete: {len(delete_ids)} atoms")
        print(f"Would keep: {total_before - len(delete_ids)} atoms")
    else:
        if delete_ids:
            placeholders = ','.join(['?' for _ in delete_ids])
            cursor.execute(f"DELETE FROM atoms WHERE id IN ({placeholders})", list(delete_ids))
            conn.commit()
            print(f"\nDeleted {len(delete_ids)} atoms")

        # Compact database
        cursor.execute("VACUUM")
        conn.commit()
        print("Database compacted")

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM atoms")
    total_after = cursor.fetchone()[0]
    conn.close()

    results = {
        "timestamp": datetime.now().isoformat(),
        "database": str(db_path),
        "dry_run": dry_run,
        "before": total_before,
        "after": total_after,
        "deleted": total_before - total_after,
        "duplicates_removed": len(to_delete),
        "low_density_flagged": len(low_density_ids)
    }

    print("\n" + "=" * 60)
    print("IMPROVEMENT RESULTS")
    print("=" * 60)
    print(f"Before: {total_before:,} atoms")
    print(f"After:  {total_after:,} atoms")
    print(f"Removed: {total_before - total_after:,} atoms ({(total_before - total_after) / total_before * 100:.1f}%)" if total_before > 0 else "")
    print("=" * 60)

    return results

def save_report(results, output_path=None):
    if output_path is None: output_path = CONSCIOUSNESS / 'ATOM_IMPROVEMENT_REPORT.json'
    json.dump(results, open(output_path, 'w'), indent=2, default=str)
    print(f"Report saved: {output_path}")
    return output_path

if __name__ == '__main__':
    db_path = get_db_path()
    if not db_path:
        print("ERROR: No atoms.db found"); sys.exit(1)

    # Parse args
    dry_run = '--live' not in sys.argv
    min_tokens = 5
    for arg in sys.argv:
        if arg.startswith('--min-tokens='): min_tokens = int(arg.split('=')[1])

    print(f"\nUsage: python {sys.argv[0]} [--live] [--min-tokens=N]")
    print("  --live: Actually delete atoms (default is dry run)")
    print("  --min-tokens=N: Minimum tokens to keep (default 5)\n")

    results = improve_quality(db_path, dry_run=dry_run, min_tokens=min_tokens)
    if results:
        save_report(results)
        sync = Path("G:/My Drive/TRINITY_COMMS/sync")
        if sync.exists(): save_report(results, sync / f"ATOM_IMPROVEMENT_{os.environ.get('COMPUTERNAME', 'unknown')}.json")
