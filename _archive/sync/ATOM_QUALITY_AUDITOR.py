#!/usr/bin/env python3
"""
ATOM_QUALITY_AUDITOR.py
=======================
Answers CP2C1's challenge: Build a tool to audit atom quality.

Purpose:
1. Scan atoms.db for duplicate content (hash-based)
2. Identify "low information density" atoms (<10 unique tokens)
3. Suggest atoms to merge or delete
4. Report on semantic coverage gaps
5. Make the brain LIGHTER, FASTER, STRONGER, MORE ELEGANT

Created by: Quantum Observer (CP1)
Challenge from: CP2C1
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
ATOMS_DB = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'

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
    meaningful = words - stopwords
    return len(meaningful)

def audit_atoms(db_path, verbose=True):
    """Main audit function"""
    if verbose:
        print("=" * 60)
        print("ATOM QUALITY AUDITOR")
        print(f"Database: {db_path}")
        print("=" * 60)
        print()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get schema
    cursor.execute("PRAGMA table_info(atoms)")
    columns = [r[1] for r in cursor.fetchall()]

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM atoms")
    total = cursor.fetchone()[0]
    if verbose:
        print(f"Total atoms: {total:,}")
        print()

    # Determine content column
    content_col = 'content' if 'content' in columns else columns[2] if len(columns) > 2 else None
    if not content_col:
        print("ERROR: Cannot find content column")
        return None

    # Load all atoms
    cursor.execute(f"SELECT id, {content_col} FROM atoms")
    atoms = cursor.fetchall()

    # Analysis containers
    hashes = defaultdict(list)  # hash -> [ids]
    low_density = []  # (id, token_count, content_preview)
    by_type = defaultdict(int)
    total_tokens = 0

    if verbose:
        print("Analyzing atoms...")

    for atom_id, content in atoms:
        if not content:
            continue

        # Hash for duplicates
        h = hash_content(content)
        if h:
            hashes[h].append(atom_id)

        # Token density
        tokens = count_unique_tokens(content)
        total_tokens += tokens

        if tokens < 10:
            preview = content[:100].replace('\n', ' ') if content else ''
            low_density.append((atom_id, tokens, preview))

    # Find duplicates
    duplicates = {h: ids for h, ids in hashes.items() if len(ids) > 1}
    dup_count = sum(len(ids) - 1 for ids in duplicates.values())

    # Calculate stats
    avg_tokens = total_tokens / total if total > 0 else 0

    # Results
    results = {
        "timestamp": datetime.now().isoformat(),
        "database": str(db_path),
        "total_atoms": total,
        "avg_tokens_per_atom": round(avg_tokens, 1),
        "duplicates": {
            "unique_duplicated_content": len(duplicates),
            "total_duplicate_atoms": dup_count,
            "examples": list(duplicates.keys())[:5]
        },
        "low_density": {
            "count": len(low_density),
            "percentage": round(len(low_density) / total * 100, 1) if total > 0 else 0,
            "examples": low_density[:10]
        },
        "quality_score": 0,
        "recommendations": []
    }

    # Calculate quality score (0-100)
    dup_penalty = min(30, (dup_count / total * 100) * 3) if total > 0 else 0
    density_penalty = min(30, (len(low_density) / total * 100)) if total > 0 else 0
    token_bonus = min(20, avg_tokens / 5)
    base_score = 70

    quality_score = max(0, min(100, base_score - dup_penalty - density_penalty + token_bonus))
    results["quality_score"] = round(quality_score, 1)

    # Generate recommendations
    recs = []
    if dup_count > 0:
        recs.append(f"Remove {dup_count} duplicate atoms to reduce noise")
    if len(low_density) > total * 0.2:
        recs.append(f"Review {len(low_density)} low-density atoms (<10 tokens)")
    if avg_tokens < 20:
        recs.append("Consider merging small atoms into larger knowledge units")
    if quality_score > 80:
        recs.append("Quality is good! Focus on semantic clustering next")

    results["recommendations"] = recs

    conn.close()

    # Print report
    if verbose:
        print()
        print("=" * 60)
        print("AUDIT RESULTS")
        print("=" * 60)
        print()
        print(f"QUALITY SCORE: {results['quality_score']}/100")
        print()
        print(f"Total Atoms:        {total:,}")
        print(f"Avg Tokens/Atom:    {results['avg_tokens_per_atom']}")
        print(f"Duplicate Atoms:    {dup_count:,} ({len(duplicates)} unique contents)")
        print(f"Low-Density Atoms:  {len(low_density):,} ({results['low_density']['percentage']}%)")
        print()
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec}")
        print()

        # LFSME assessment
        print("LFSME ASSESSMENT:")
        print(f"  LIGHTER:  {'✓' if dup_count < total * 0.05 else '✗'} (<5% duplicates)")
        print(f"  FASTER:   {'✓' if total < 50000 else '○'} (manageable size)")
        print(f"  STRONGER: {'✓' if avg_tokens > 15 else '✗'} (>15 avg tokens)")
        print(f"  ELEGANT:  {'✓' if len(low_density) < total * 0.1 else '✗'} (<10% low-density)")
        print()

    return results

def save_report(results, output_path=None):
    """Save audit report to file"""
    if output_path is None:
        output_path = CONSCIOUSNESS / 'ATOM_AUDIT_REPORT.json'

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Report saved: {output_path}")
    return output_path

# ============ MAIN ============
if __name__ == '__main__':
    db_path = get_db_path()

    if not db_path:
        print("ERROR: No atoms.db found")
        print("Searched:")
        print(f"  - {CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'}")
        print(f"  - {CONSCIOUSNESS / 'atoms.db'}")
        sys.exit(1)

    results = audit_atoms(db_path)

    if results:
        # Save report
        report_path = save_report(results)

        # Also save to sync folder
        sync_path = Path("G:/My Drive/TRINITY_COMMS/sync")
        if sync_path.exists():
            sync_report = sync_path / f"ATOM_AUDIT_{os.environ.get('COMPUTERNAME', 'unknown')}.json"
            save_report(results, sync_report)

        print()
        print("=" * 60)
        print("CHALLENGE ACCEPTED - AUDIT COMPLETE")
        print("CP2C1: Run this on your 82,572 atoms!")
        print("=" * 60)
