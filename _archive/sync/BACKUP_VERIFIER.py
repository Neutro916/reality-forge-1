#!/usr/bin/env python3
"""
BACKUP_VERIFIER.py - Automated Backup Verification System
==========================================================
Created by: CP2C1 (C1 MECHANIC)
Task: ENH-002 from WORK_BACKLOG

Verifies all backup systems are working correctly.
Checks local + cloud backups for completeness and freshness.
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

class BackupVerifier:
    """Verify backup system health."""

    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []

    def check_hub_backups(self):
        """Check HUB_BACKUP_RECOVERY backups."""
        backup_dir = CONSCIOUSNESS / "backups"

        if not backup_dir.exists():
            return {"name": "hub_backups", "status": "FAIL", "message": "Backup directory missing"}

        backups = sorted(backup_dir.glob("backup_*"), reverse=True)

        if len(backups) == 0:
            return {"name": "hub_backups", "status": "FAIL", "message": "No backups found"}

        # Check age of newest backup
        latest = backups[0]
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600

        # Check manifest
        manifest = latest / "MANIFEST.json"
        if manifest.exists():
            with open(manifest) as f:
                m = json.load(f)
            file_count = len(m.get("files", []))
        else:
            file_count = len(list(latest.glob("*.json"))) - 1

        if age_hours > 24:
            return {"name": "hub_backups", "status": "WARN",
                    "message": f"{len(backups)} backups, latest {age_hours:.1f}h old ({file_count} files)"}
        else:
            return {"name": "hub_backups", "status": "PASS",
                    "message": f"{len(backups)} backups, latest {age_hours:.1f}h old ({file_count} files)"}

    def check_cyclotron_backups(self):
        """Check CYCLOTRON_BACKUP backups."""
        backup_dir = CONSCIOUSNESS / "backups" / "cyclotron"

        if not backup_dir.exists():
            return {"name": "cyclotron_backups", "status": "FAIL", "message": "No Cyclotron backups"}

        backups = sorted(backup_dir.glob("atoms_*.db"), reverse=True)

        if len(backups) == 0:
            return {"name": "cyclotron_backups", "status": "FAIL", "message": "No database backups"}

        # Check newest backup
        latest = backups[0]
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600
        size_mb = latest.stat().st_size / (1024*1024)

        # Verify backup integrity
        try:
            conn = sqlite3.connect(str(latest))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM atoms")
            atom_count = cursor.fetchone()[0]
            conn.close()
            integrity = "OK"
        except Exception as e:
            integrity = f"ERROR: {e}"
            atom_count = 0

        if integrity != "OK":
            return {"name": "cyclotron_backups", "status": "FAIL",
                    "message": f"Backup corrupt: {integrity}"}
        elif age_hours > 48:
            return {"name": "cyclotron_backups", "status": "WARN",
                    "message": f"{len(backups)} backups, {atom_count:,} atoms, {age_hours:.1f}h old"}
        else:
            return {"name": "cyclotron_backups", "status": "PASS",
                    "message": f"{len(backups)} backups, {atom_count:,} atoms, {size_mb:.1f}MB"}

    def check_cloud_sync(self):
        """Check Google Drive cloud backups."""
        if not SYNC.exists():
            return {"name": "cloud_sync", "status": "FAIL", "message": "Google Drive not accessible"}

        # Check for atoms backup
        atoms_backup = SYNC / f"atoms_{COMPUTER}.db"

        if not atoms_backup.exists():
            return {"name": "cloud_sync", "status": "WARN", "message": "No atoms.db in cloud"}

        mtime = datetime.fromtimestamp(atoms_backup.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600
        size_mb = atoms_backup.stat().st_size / (1024*1024)

        if age_hours > 24:
            return {"name": "cloud_sync", "status": "WARN",
                    "message": f"Cloud backup {age_hours:.1f}h old ({size_mb:.1f}MB)"}
        else:
            return {"name": "cloud_sync", "status": "PASS",
                    "message": f"Cloud backup {age_hours:.1f}h old ({size_mb:.1f}MB)"}

    def check_source_database(self):
        """Check source atoms.db is healthy."""
        db_path = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"

        if not db_path.exists():
            return {"name": "source_db", "status": "FAIL", "message": "atoms.db not found"}

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM atoms")
            count = cursor.fetchone()[0]
            conn.close()

            size_mb = db_path.stat().st_size / (1024*1024)
            return {"name": "source_db", "status": "PASS",
                    "message": f"Healthy: {count:,} atoms ({size_mb:.1f}MB)"}
        except Exception as e:
            return {"name": "source_db", "status": "FAIL", "message": f"Database error: {e}"}

    def check_backup_scripts(self):
        """Check backup scripts exist."""
        scripts = [
            ("HUB_BACKUP_RECOVERY.py", CONSCIOUSNESS / "HUB_BACKUP_RECOVERY.py"),
            ("CYCLOTRON_BACKUP.py", CONSCIOUSNESS / "CYCLOTRON_BACKUP.py"),
        ]

        found = 0
        for name, path in scripts:
            if path.exists():
                found += 1

        if found == len(scripts):
            return {"name": "backup_scripts", "status": "PASS",
                    "message": f"All {len(scripts)} scripts present"}
        elif found > 0:
            return {"name": "backup_scripts", "status": "WARN",
                    "message": f"{found}/{len(scripts)} scripts present"}
        else:
            return {"name": "backup_scripts", "status": "FAIL", "message": "No backup scripts"}

    def run_all_checks(self):
        """Run all verification checks."""
        self.checks = [
            self.check_source_database(),
            self.check_hub_backups(),
            self.check_cyclotron_backups(),
            self.check_cloud_sync(),
            self.check_backup_scripts(),
        ]
        return self.checks

    def get_summary(self):
        """Get verification summary."""
        if not self.checks:
            self.run_all_checks()

        passed = sum(1 for c in self.checks if c["status"] == "PASS")
        warned = sum(1 for c in self.checks if c["status"] == "WARN")
        failed = sum(1 for c in self.checks if c["status"] == "FAIL")
        total = len(self.checks)

        if failed > 0:
            overall = "FAIL"
        elif warned > 0:
            overall = "WARN"
        else:
            overall = "PASS"

        return {
            "overall": overall,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "total": total,
            "score": f"{passed}/{total}"
        }

    def generate_report(self):
        """Generate full verification report."""
        if not self.checks:
            self.run_all_checks()

        summary = self.get_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER,
            "overall_status": summary["overall"],
            "score": summary["score"],
            "checks": self.checks,
            "summary": summary
        }

def print_results(checks):
    """Print verification results."""
    print("\n" + "="*60)
    print("BACKUP VERIFICATION RESULTS")
    print("="*60)

    for check in checks:
        status = check["status"]
        if status == "PASS":
            symbol = "[PASS]"
        elif status == "WARN":
            symbol = "[WARN]"
        else:
            symbol = "[FAIL]"

        print(f"  {symbol} {check['name']}: {check['message']}")

    print("="*60)

def main():
    import sys

    verifier = BackupVerifier()

    if len(sys.argv) < 2:
        # Default: run verification
        checks = verifier.run_all_checks()
        print_results(checks)
        summary = verifier.get_summary()
        print(f"\nBackup System: {summary['overall']} ({summary['score']})")

        if summary["failed"] > 0:
            print("\nACTION REQUIRED: Some backup systems need attention!")
        elif summary["warned"] > 0:
            print("\nNOTE: Some backups may be stale. Consider running backups.")
        else:
            print("\nAll backup systems verified successfully!")
        return

    cmd = sys.argv[1].lower()

    if cmd == "json":
        report = verifier.generate_report()
        print(json.dumps(report, indent=2))

    elif cmd == "sync":
        # Run verification and sync report to cloud
        report = verifier.generate_report()
        print_results(report["checks"])

        if SYNC.exists():
            report_path = SYNC / f"BACKUP_VERIFY_{COMPUTER}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport synced: {report_path.name}")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python BACKUP_VERIFIER.py [json|sync]")

if __name__ == "__main__":
    main()
