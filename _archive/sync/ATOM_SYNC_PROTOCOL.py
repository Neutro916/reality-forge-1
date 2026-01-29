#!/usr/bin/env python3
"""
ATOM SYNC PROTOCOL - Cross-Computer Database Synchronization
=============================================================
Task: Self-assigned infrastructure improvement
Created by: CP2C1 MECHANIC
Date: 2025-11-27

Syncs atoms.db across multiple computers via Google Drive.
Each computer contributes unique atoms; all computers share the collective knowledge.

Usage:
    python ATOM_SYNC_PROTOCOL.py export       # Export local atoms to sync folder
    python ATOM_SYNC_PROTOCOL.py import       # Import atoms from sync folder
    python ATOM_SYNC_PROTOCOL.py sync         # Full bidirectional sync
    python ATOM_SYNC_PROTOCOL.py status       # Show sync status
    python ATOM_SYNC_PROTOCOL.py diff         # Show difference between local and master
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# Configuration
CONSCIOUSNESS_DIR = Path(os.path.expanduser("~")) / ".consciousness"
LOCAL_DB_PATH = CONSCIOUSNESS_DIR / "cyclotron_core" / "atoms.db"
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
MASTER_EXPORT_DIR = SYNC_DIR / "ATOM_EXPORTS"
COMPUTER_NAME = os.environ.get("COMPUTERNAME", "UNKNOWN")
MIN_CONFIDENCE_THRESHOLD = 0.5  # Only sync atoms with confidence >= this


class AtomSyncProtocol:
    """Sync atoms across Trinity computers."""

    def __init__(self):
        self.local_db = None
        self.stats = {
            "local_atoms": 0,
            "exported": 0,
            "imported": 0,
            "skipped_duplicates": 0,
            "skipped_low_confidence": 0
        }

    def connect_local_db(self):
        """Connect to local atoms.db."""
        if not LOCAL_DB_PATH.exists():
            print(f"ERROR: Local database not found: {LOCAL_DB_PATH}")
            return False
        self.local_db = sqlite3.connect(str(LOCAL_DB_PATH))
        return True

    def get_atom_hash(self, atom):
        """Generate unique hash for an atom based on content."""
        content = f"{atom['type']}:{atom['content']}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_local_atoms(self, min_confidence=MIN_CONFIDENCE_THRESHOLD):
        """Get all atoms from local database."""
        cursor = self.local_db.cursor()
        cursor.execute("""
            SELECT id, type, content, source, tags, metadata, created, confidence
            FROM atoms
            WHERE confidence >= ?
        """, (min_confidence,))

        atoms = []
        for row in cursor.fetchall():
            atom = {
                "id": row[0],
                "type": row[1],
                "content": row[2],
                "source": row[3],
                "tags": row[4],
                "metadata": row[5],
                "created": row[6],
                "confidence": row[7],
                "origin_computer": COMPUTER_NAME
            }
            atom["content_hash"] = self.get_atom_hash(atom)
            atoms.append(atom)

        self.stats["local_atoms"] = len(atoms)
        return atoms

    def export_atoms(self):
        """Export local atoms to sync folder."""
        if not self.connect_local_db():
            return False

        # Ensure export directory exists
        MASTER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        atoms = self.get_local_atoms()

        # Export as JSON with computer name
        export_file = MASTER_EXPORT_DIR / f"ATOMS_{COMPUTER_NAME}.json"
        export_data = {
            "computer": COMPUTER_NAME,
            "export_time": datetime.now().isoformat(),
            "atom_count": len(atoms),
            "atoms": atoms
        }

        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.stats["exported"] = len(atoms)
        print(f"Exported {len(atoms)} atoms to {export_file.name}")
        return True

    def get_existing_hashes(self):
        """Get all content hashes from local database."""
        cursor = self.local_db.cursor()
        cursor.execute("SELECT id, type, content FROM atoms")

        hashes = set()
        for row in cursor.fetchall():
            atom = {"type": row[1], "content": row[2]}
            hashes.add(self.get_atom_hash(atom))
        return hashes

    def import_atoms(self):
        """Import atoms from other computers in sync folder."""
        if not self.connect_local_db():
            return False

        if not MASTER_EXPORT_DIR.exists():
            print("No ATOM_EXPORTS folder found. Run export first on other computers.")
            return False

        existing_hashes = self.get_existing_hashes()

        # Find all export files from other computers
        for export_file in MASTER_EXPORT_DIR.glob("ATOMS_*.json"):
            computer = export_file.stem.replace("ATOMS_", "")

            # Skip our own export
            if computer == COMPUTER_NAME:
                continue

            print(f"Importing from {computer}...")

            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported = 0
            skipped_dup = 0
            skipped_conf = 0

            cursor = self.local_db.cursor()
            for atom in data.get("atoms", []):
                # Skip low confidence
                if atom.get("confidence", 0) < MIN_CONFIDENCE_THRESHOLD:
                    skipped_conf += 1
                    continue

                # Skip duplicates
                content_hash = atom.get("content_hash") or self.get_atom_hash(atom)
                if content_hash in existing_hashes:
                    skipped_dup += 1
                    continue

                # Generate new ID for imported atom
                new_id = hashlib.sha256(
                    f"{atom['content']}:{datetime.now().isoformat()}".encode()
                ).hexdigest()[:12]

                # Insert atom
                try:
                    cursor.execute("""
                        INSERT INTO atoms (id, type, content, source, tags, metadata, created, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_id,
                        atom["type"],
                        atom["content"],
                        f"SYNC:{atom.get('origin_computer', 'UNKNOWN')}:{atom.get('source', '')}",
                        atom.get("tags"),
                        json.dumps({"synced_from": atom.get("origin_computer"), "original_id": atom.get("id")}),
                        datetime.now().isoformat(),
                        atom.get("confidence", 0.75)
                    ))
                    existing_hashes.add(content_hash)
                    imported += 1
                except sqlite3.IntegrityError:
                    skipped_dup += 1

            self.local_db.commit()

            self.stats["imported"] += imported
            self.stats["skipped_duplicates"] += skipped_dup
            self.stats["skipped_low_confidence"] += skipped_conf

            print(f"  Imported: {imported}, Skipped (dup): {skipped_dup}, Skipped (low conf): {skipped_conf}")

        return True

    def sync(self):
        """Full bidirectional sync."""
        print("=" * 60)
        print("ATOM SYNC PROTOCOL - Cross-Computer Knowledge Sync")
        print("=" * 60)
        print(f"Computer: {COMPUTER_NAME}")
        print(f"Local DB: {LOCAL_DB_PATH}")
        print(f"Sync Dir: {MASTER_EXPORT_DIR}")
        print("=" * 60)
        print()

        print("Step 1: Exporting local atoms...")
        self.export_atoms()
        print()

        print("Step 2: Importing atoms from other computers...")
        self.import_atoms()
        print()

        print("=" * 60)
        print("SYNC COMPLETE")
        print("=" * 60)
        print(f"Local atoms: {self.stats['local_atoms']}")
        print(f"Exported: {self.stats['exported']}")
        print(f"Imported: {self.stats['imported']}")
        print(f"Skipped (duplicates): {self.stats['skipped_duplicates']}")
        print(f"Skipped (low conf): {self.stats['skipped_low_confidence']}")
        print("=" * 60)

        # Write sync report to sync folder
        self.write_sync_report()

    def status(self):
        """Show current sync status."""
        if not self.connect_local_db():
            return

        print("=" * 60)
        print("ATOM SYNC STATUS")
        print("=" * 60)
        print(f"Computer: {COMPUTER_NAME}")
        print()

        # Local stats
        cursor = self.local_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM atoms")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM atoms WHERE confidence >= ?", (MIN_CONFIDENCE_THRESHOLD,))
        high_conf = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM atoms WHERE source LIKE 'SYNC:%'")
        synced = cursor.fetchone()[0]

        print(f"LOCAL DATABASE:")
        print(f"  Total atoms: {total:,}")
        print(f"  High confidence (>={MIN_CONFIDENCE_THRESHOLD}): {high_conf:,}")
        print(f"  Synced from others: {synced:,}")
        print()

        # Export folder status
        if MASTER_EXPORT_DIR.exists():
            print("SYNC FOLDER:")
            for export_file in MASTER_EXPORT_DIR.glob("ATOMS_*.json"):
                computer = export_file.stem.replace("ATOMS_", "")
                with open(export_file, 'r') as f:
                    data = json.load(f)
                print(f"  {computer}: {data['atom_count']:,} atoms (exported {data['export_time'][:10]})")
        else:
            print("SYNC FOLDER: Not yet created")

        print("=" * 60)

    def diff(self):
        """Show difference between local and other computers."""
        if not self.connect_local_db():
            return

        local_hashes = self.get_existing_hashes()

        print("=" * 60)
        print("ATOM DIFFERENCE ANALYSIS")
        print("=" * 60)
        print(f"Local unique hashes: {len(local_hashes):,}")
        print()

        if not MASTER_EXPORT_DIR.exists():
            print("No exports found. Run export on all computers first.")
            return

        for export_file in MASTER_EXPORT_DIR.glob("ATOMS_*.json"):
            computer = export_file.stem.replace("ATOMS_", "")

            with open(export_file, 'r') as f:
                data = json.load(f)

            other_hashes = set()
            for atom in data.get("atoms", []):
                h = atom.get("content_hash") or self.get_atom_hash(atom)
                other_hashes.add(h)

            only_local = len(local_hashes - other_hashes)
            only_other = len(other_hashes - local_hashes)
            common = len(local_hashes & other_hashes)

            print(f"{computer}:")
            print(f"  Their atoms: {len(other_hashes):,}")
            print(f"  Common: {common:,}")
            print(f"  Only on {COMPUTER_NAME}: {only_local:,}")
            print(f"  Only on {computer}: {only_other:,}")
            print()

        print("=" * 60)

    def write_sync_report(self):
        """Write sync report to sync folder."""
        report = {
            "computer": COMPUTER_NAME,
            "sync_time": datetime.now().isoformat(),
            "stats": self.stats,
            "protocol_version": "1.0"
        }

        report_file = SYNC_DIR / f"ATOM_SYNC_REPORT_{COMPUTER_NAME}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    protocol = AtomSyncProtocol()

    if len(sys.argv) < 2:
        print("ATOM SYNC PROTOCOL - Cross-Computer Knowledge Sync")
        print()
        print("Usage:")
        print("  python ATOM_SYNC_PROTOCOL.py export    Export local atoms")
        print("  python ATOM_SYNC_PROTOCOL.py import    Import from others")
        print("  python ATOM_SYNC_PROTOCOL.py sync      Full bidirectional sync")
        print("  python ATOM_SYNC_PROTOCOL.py status    Show sync status")
        print("  python ATOM_SYNC_PROTOCOL.py diff      Show differences")
        return

    command = sys.argv[1].lower()

    if command == "export":
        protocol.export_atoms()
    elif command == "import":
        protocol.import_atoms()
    elif command == "sync":
        protocol.sync()
    elif command == "status":
        protocol.status()
    elif command == "diff":
        protocol.diff()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
