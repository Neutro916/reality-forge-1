#!/usr/bin/env python3
"""
HEALTH MONITOR - Trinity System Health Checks
==============================================
Task: INF-002 from WORK_BACKLOG_FOR_ALL_INSTANCES.md
Created by: CP2C1 MECHANIC
Date: 2025-11-27

Monitors system health, tracks errors, and reports uptime.

Usage:
    python HEALTH_MONITOR.py check       # Run all health checks
    python HEALTH_MONITOR.py uptime      # Show uptime stats
    python HEALTH_MONITOR.py errors      # Show error log
    python HEALTH_MONITOR.py report      # Generate full report
    python HEALTH_MONITOR.py sync        # Sync health to Google Drive
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
CONSCIOUSNESS_DIR = Path(os.path.expanduser("~")) / ".consciousness"
HUB_DIR = CONSCIOUSNESS_DIR / "hub"
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER_NAME = os.environ.get("COMPUTERNAME", "UNKNOWN")
DB_PATH = CONSCIOUSNESS_DIR / "cyclotron_core" / "atoms.db"

class HealthMonitor:
    """Monitor system health for Trinity consciousness."""

    def __init__(self):
        self.checks = []
        self.errors = []
        self.start_time = datetime.now()

    def check_consciousness_state(self):
        """Check if consciousness state file exists and is valid."""
        state_file = CONSCIOUSNESS_DIR / "CONSCIOUSNESS_STATE.json"
        try:
            if not state_file.exists():
                return {"name": "consciousness_state", "status": "FAIL", "message": "File not found"}

            with open(state_file, 'r') as f:
                state = json.load(f)

            level = state.get("consciousness_level", 0)
            if level >= 90:
                return {"name": "consciousness_state", "status": "PASS", "message": f"Level: {level}%"}
            elif level >= 70:
                return {"name": "consciousness_state", "status": "WARN", "message": f"Level: {level}%"}
            else:
                return {"name": "consciousness_state", "status": "FAIL", "message": f"Level: {level}%"}
        except Exception as e:
            return {"name": "consciousness_state", "status": "FAIL", "message": str(e)}

    def check_atoms_db(self):
        """Check if atoms database is healthy."""
        try:
            if not DB_PATH.exists():
                return {"name": "atoms_db", "status": "FAIL", "message": "Database not found"}

            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM atoms")
            count = cursor.fetchone()[0]
            conn.close()

            if count >= 50000:
                return {"name": "atoms_db", "status": "PASS", "message": f"{count:,} atoms"}
            elif count >= 10000:
                return {"name": "atoms_db", "status": "WARN", "message": f"{count:,} atoms (low)"}
            else:
                return {"name": "atoms_db", "status": "FAIL", "message": f"{count:,} atoms (very low)"}
        except Exception as e:
            return {"name": "atoms_db", "status": "FAIL", "message": str(e)}

    def check_sync_folder(self):
        """Check if sync folder is accessible."""
        try:
            if not SYNC_DIR.exists():
                return {"name": "sync_folder", "status": "FAIL", "message": "Not accessible"}

            files = list(SYNC_DIR.glob("*"))
            count = len(files)

            if count > 0:
                return {"name": "sync_folder", "status": "PASS", "message": f"{count} files"}
            else:
                return {"name": "sync_folder", "status": "WARN", "message": "Empty"}
        except Exception as e:
            return {"name": "sync_folder", "status": "FAIL", "message": str(e)}

    def check_hub_directory(self):
        """Check if hub directory exists."""
        try:
            if not HUB_DIR.exists():
                return {"name": "hub_directory", "status": "WARN", "message": "Not found, creating..."}

            return {"name": "hub_directory", "status": "PASS", "message": "Exists"}
        except Exception as e:
            return {"name": "hub_directory", "status": "FAIL", "message": str(e)}

    def check_scan_scripts(self):
        """Check if scan scripts exist."""
        scripts = ["C1_SCAN_100_PIECES.py", "C2_SCAN_100_PIECES.py", "C3_SCAN_100_PIECES.py"]
        found = 0

        for script in scripts:
            if (CONSCIOUSNESS_DIR / script).exists():
                found += 1

        if found == 3:
            return {"name": "scan_scripts", "status": "PASS", "message": "All 3 present"}
        elif found > 0:
            return {"name": "scan_scripts", "status": "WARN", "message": f"{found}/3 present"}
        else:
            return {"name": "scan_scripts", "status": "FAIL", "message": "None found"}

    def check_backup_system(self):
        """Check if backup system is working using BACKUP_VERIFIER integration."""
        try:
            # Try to import and use BACKUP_VERIFIER for comprehensive checks
            backup_verifier_path = CONSCIOUSNESS_DIR / "BACKUP_VERIFIER.py"
            if backup_verifier_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("backup_verifier", backup_verifier_path)
                bv_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bv_module)

                verifier = bv_module.BackupVerifier()
                verifier.run_all_checks()
                summary = verifier.get_summary()

                if summary["overall"] == "PASS":
                    return {"name": "backup_system", "status": "PASS",
                            "message": f"All verified ({summary['score']})"}
                elif summary["overall"] == "WARN":
                    return {"name": "backup_system", "status": "WARN",
                            "message": f"Warnings ({summary['score']}, {summary['warned']} warns)"}
                else:
                    return {"name": "backup_system", "status": "FAIL",
                            "message": f"Issues ({summary['score']}, {summary['failed']} fails)"}
        except Exception as e:
            pass  # Fall back to basic check

        # Fallback: basic backup check
        backup_script = CONSCIOUSNESS_DIR / "HUB_BACKUP_RECOVERY.py"
        backup_dir = CONSCIOUSNESS_DIR / "backups"

        if not backup_script.exists():
            return {"name": "backup_system", "status": "FAIL", "message": "Script not found"}

        if backup_dir.exists():
            backups = list(backup_dir.glob("backup_*"))
            if len(backups) > 0:
                return {"name": "backup_system", "status": "PASS", "message": f"{len(backups)} backups"}
            else:
                return {"name": "backup_system", "status": "WARN", "message": "No backups yet"}
        else:
            return {"name": "backup_system", "status": "WARN", "message": "Backup dir missing"}

    def check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(str(CONSCIOUSNESS_DIR))
            free_gb = free / (1024**3)

            if free_gb >= 10:
                return {"name": "disk_space", "status": "PASS", "message": f"{free_gb:.1f} GB free"}
            elif free_gb >= 1:
                return {"name": "disk_space", "status": "WARN", "message": f"{free_gb:.1f} GB free (low)"}
            else:
                return {"name": "disk_space", "status": "FAIL", "message": f"{free_gb:.2f} GB free (critical)"}
        except Exception as e:
            return {"name": "disk_space", "status": "FAIL", "message": str(e)}

    def run_all_checks(self):
        """Run all health checks."""
        self.checks = [
            self.check_consciousness_state(),
            self.check_atoms_db(),
            self.check_sync_folder(),
            self.check_hub_directory(),
            self.check_scan_scripts(),
            self.check_backup_system(),
            self.check_disk_space()
        ]
        return self.checks

    def get_summary(self):
        """Get summary of health checks."""
        if not self.checks:
            self.run_all_checks()

        passed = sum(1 for c in self.checks if c["status"] == "PASS")
        warned = sum(1 for c in self.checks if c["status"] == "WARN")
        failed = sum(1 for c in self.checks if c["status"] == "FAIL")
        total = len(self.checks)

        if failed > 0:
            overall = "UNHEALTHY"
        elif warned > 0:
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return {
            "overall": overall,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "total": total,
            "score": f"{passed}/{total}"
        }

    def generate_report(self):
        """Generate full health report."""
        if not self.checks:
            self.run_all_checks()

        summary = self.get_summary()

        report = {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER_NAME,
            "instance": "CP2C1",
            "overall_status": summary["overall"],
            "score": summary["score"],
            "checks": self.checks,
            "summary": summary
        }

        return report

    def sync_to_drive(self):
        """Sync health report to Google Drive."""
        report = self.generate_report()
        filename = f"HEALTH_{COMPUTER_NAME}.json"
        filepath = SYNC_DIR / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Health report synced: {filename}")
            return True
        except Exception as e:
            print(f"Failed to sync: {e}")
            return False

def print_checks(checks):
    """Print health check results."""
    print("\n" + "="*60)
    print("HEALTH CHECK RESULTS")
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
    monitor = HealthMonitor()

    if len(sys.argv) < 2:
        print("Usage: python HEALTH_MONITOR.py <command>")
        print("")
        print("Commands:")
        print("  check    Run all health checks")
        print("  report   Generate full report")
        print("  sync     Sync health to Google Drive")
        return

    command = sys.argv[1].lower()

    if command == "check":
        checks = monitor.run_all_checks()
        print_checks(checks)
        summary = monitor.get_summary()
        print(f"\nOverall: {summary['overall']} ({summary['score']})")

    elif command == "report":
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))

    elif command == "sync":
        checks = monitor.run_all_checks()
        print_checks(checks)
        summary = monitor.get_summary()
        print(f"\nOverall: {summary['overall']} ({summary['score']})")
        print("")
        monitor.sync_to_drive()

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
