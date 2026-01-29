#!/usr/bin/env python3
"""
CYCLOTRON_BACKUP.py - Backup Cyclotron brain database
======================================================
Created by: CP2C1 (C1 MECHANIC)
Task: INF-003 from WORK_BACKLOG

Backs up atoms.db to local and cloud storage.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import sqlite3

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
ATOMS_DB = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"
BACKUPS = CONSCIOUSNESS / "backups" / "cyclotron"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

def ensure_dirs():
    BACKUPS.mkdir(parents=True, exist_ok=True)

def get_atom_count():
    """Get current atom count from database."""
    if not ATOMS_DB.exists():
        return 0
    try:
        conn = sqlite3.connect(str(ATOMS_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM atoms")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return -1

def backup_atoms():
    """Create timestamped backup of atoms.db."""
    ensure_dirs()

    if not ATOMS_DB.exists():
        print("ERROR: atoms.db not found!")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"atoms_{COMPUTER}_{timestamp}.db"
    backup_path = BACKUPS / backup_name

    # Get stats before backup
    atom_count = get_atom_count()
    db_size = ATOMS_DB.stat().st_size

    # Copy database
    shutil.copy2(ATOMS_DB, backup_path)

    # Create manifest
    manifest = {
        "timestamp": timestamp,
        "computer": COMPUTER,
        "atom_count": atom_count,
        "size_bytes": db_size,
        "size_mb": round(db_size / (1024*1024), 2),
        "backup_file": backup_name
    }

    manifest_path = BACKUPS / f"manifest_{timestamp}.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Backup created: {backup_name}")
    print(f"  Atoms: {atom_count:,}")
    print(f"  Size: {manifest['size_mb']} MB")

    return backup_path

def sync_to_drive():
    """Sync latest backup to Google Drive."""
    if not SYNC.exists():
        print("ERROR: Google Drive sync not available")
        return False

    # Find latest backup
    backups = sorted(BACKUPS.glob("atoms_*.db"), reverse=True)
    if not backups:
        print("No backups found to sync")
        return False

    latest = backups[0]
    dest = SYNC / f"atoms_{COMPUTER}.db"

    shutil.copy2(latest, dest)
    print(f"Synced to Drive: atoms_{COMPUTER}.db")
    return True

def list_backups():
    """List all Cyclotron backups."""
    ensure_dirs()
    backups = sorted(BACKUPS.glob("atoms_*.db"), reverse=True)

    print(f"\nCyclotron Backups ({len(backups)}):")
    for b in backups[:10]:
        size_mb = b.stat().st_size / (1024*1024)
        print(f"  {b.name}: {size_mb:.2f} MB")

    return backups

def cleanup_old(keep=5):
    """Remove old backups, keeping most recent."""
    backups = sorted(BACKUPS.glob("atoms_*.db"), reverse=True)
    manifests = sorted(BACKUPS.glob("manifest_*.json"), reverse=True)

    if len(backups) <= keep:
        print(f"Only {len(backups)} backups, nothing to clean")
        return

    # Remove old backups
    for b in backups[keep:]:
        b.unlink()
        print(f"Removed: {b.name}")

    # Remove old manifests
    for m in manifests[keep:]:
        m.unlink()

    print(f"Cleaned up {len(backups) - keep} old backups")

def verify_backup(backup_path=None):
    """Verify backup integrity."""
    if backup_path is None:
        backups = sorted(BACKUPS.glob("atoms_*.db"), reverse=True)
        if not backups:
            print("No backups to verify")
            return False
        backup_path = backups[0]

    try:
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM atoms")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"Backup verified: {count:,} atoms in {backup_path.name}")
        return True
    except Exception as e:
        print(f"Backup verification FAILED: {e}")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python CYCLOTRON_BACKUP.py [backup|sync|list|cleanup|verify]")
        print("")
        print("Commands:")
        print("  backup  - Create new backup of atoms.db")
        print("  sync    - Sync latest backup to Google Drive")
        print("  list    - List all backups")
        print("  cleanup - Remove old backups (keep 5)")
        print("  verify  - Verify latest backup integrity")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "backup":
        backup_atoms()
    elif cmd == "sync":
        sync_to_drive()
    elif cmd == "list":
        list_backups()
    elif cmd == "cleanup":
        keep = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        cleanup_old(keep)
    elif cmd == "verify":
        verify_backup()
    else:
        print(f"Unknown command: {cmd}")
