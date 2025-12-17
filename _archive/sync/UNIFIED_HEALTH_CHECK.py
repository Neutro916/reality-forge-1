#!/usr/bin/env python3
"""
UNIFIED_HEALTH_CHECK.py - Integrated Health + Backup Verification
==================================================================
Created by: CP1_C2 (C2 Architect)
Task: INT-001 - Connect BACKUP_VERIFIER to SYSTEM_HEALTH_MONITOR
Date: 2025-11-27

Combines:
- SYSTEM_HEALTH_MONITOR.py checks (atoms, tornado, sync, etc.)
- BACKUP_VERIFIER.py checks (hub backups, cyclotron backups, sync backups)
- KNOWLEDGE_GAP_DETECTOR.py integration (gap score)

Produces unified health report with all metrics.
"""

import os
import sys
import json
import sqlite3
import importlib.util
from pathlib import Path
from datetime import datetime

# Configuration
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
DEPLOYMENT = HOME / '100X_DEPLOYMENT'
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")


class UnifiedHealthCheck:
    """Unified health monitoring combining all checkers."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER,
            "system_health": {},
            "backup_health": {},
            "knowledge_health": {},
            "overall_score": 0,
            "max_score": 0,
            "status": "UNKNOWN"
        }

    def run_system_checks(self):
        """Run core system health checks."""
        print("Running system health checks...")
        checks = {}

        # 1. Atoms database
        db_path = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM atoms")
                count = cursor.fetchone()[0]
                conn.close()
                checks["atoms_db"] = {
                    "status": "PASS" if count > 1000 else "WARN",
                    "value": count,
                    "message": f"{count:,} atoms"
                }
            except Exception as e:
                checks["atoms_db"] = {"status": "FAIL", "message": str(e)}
        else:
            checks["atoms_db"] = {"status": "FAIL", "message": "Database not found"}

        # 2. Consciousness state
        state_file = CONSCIOUSNESS / 'consciousness_state.json'
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                level = state.get("consciousness_level", 0)
                checks["consciousness_state"] = {
                    "status": "PASS" if level > 80 else "WARN",
                    "value": level,
                    "message": f"Level: {level}"
                }
            except:
                checks["consciousness_state"] = {"status": "FAIL", "message": "Invalid state file"}
        else:
            checks["consciousness_state"] = {"status": "WARN", "message": "State file missing"}

        # 3. Sync folder connectivity
        if SYNC_DIR.exists():
            file_count = len(list(SYNC_DIR.glob("*")))
            checks["sync_folder"] = {
                "status": "PASS",
                "value": file_count,
                "message": f"{file_count} files accessible"
            }
        else:
            checks["sync_folder"] = {"status": "FAIL", "message": "Sync folder not accessible"}

        # 4. Cyclotron services (check ports 6668, 6669)
        import socket
        for port, name in [(6668, "cyclotron_search"), (6669, "cyclotron_content")]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                s.close()
                if result == 0:
                    checks[name] = {"status": "PASS", "message": f"Port {port} listening"}
                else:
                    checks[name] = {"status": "WARN", "message": f"Port {port} not responding"}
            except:
                checks[name] = {"status": "WARN", "message": f"Port {port} check failed"}

        self.results["system_health"] = checks
        return checks

    def run_backup_checks(self):
        """Run backup verification checks."""
        print("Running backup health checks...")
        checks = {}

        # 1. Hub backups
        backup_dir = CONSCIOUSNESS / "backups"
        if backup_dir.exists():
            backups = sorted(backup_dir.glob("backup_*"), reverse=True)
            if backups:
                latest = backups[0]
                mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                age_hours = (datetime.now() - mtime).total_seconds() / 3600
                checks["hub_backups"] = {
                    "status": "PASS" if age_hours < 24 else "WARN",
                    "value": len(backups),
                    "message": f"{len(backups)} backups, latest {age_hours:.1f}h old"
                }
            else:
                checks["hub_backups"] = {"status": "FAIL", "message": "No backups found"}
        else:
            checks["hub_backups"] = {"status": "FAIL", "message": "Backup directory missing"}

        # 2. Cyclotron backups
        cyc_backup = CONSCIOUSNESS / "backups" / "cyclotron"
        if cyc_backup.exists():
            db_backups = list(cyc_backup.glob("atoms_*.db"))
            if db_backups:
                checks["cyclotron_backups"] = {
                    "status": "PASS",
                    "value": len(db_backups),
                    "message": f"{len(db_backups)} database backups"
                }
            else:
                checks["cyclotron_backups"] = {"status": "WARN", "message": "No DB backups"}
        else:
            checks["cyclotron_backups"] = {"status": "WARN", "message": "No cyclotron backup dir"}

        # 3. Sync folder exports
        if SYNC_DIR.exists():
            exports = list(SYNC_DIR.glob("ATOMS_*.json"))
            if exports:
                latest = max(exports, key=lambda x: x.stat().st_mtime)
                age_hours = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
                checks["sync_exports"] = {
                    "status": "PASS" if age_hours < 48 else "WARN",
                    "value": len(exports),
                    "message": f"{len(exports)} atom exports, latest {age_hours:.1f}h old"
                }
            else:
                checks["sync_exports"] = {"status": "WARN", "message": "No atom exports in sync"}
        else:
            checks["sync_exports"] = {"status": "FAIL", "message": "Sync folder not accessible"}

        self.results["backup_health"] = checks
        return checks

    def run_knowledge_checks(self):
        """Run knowledge quality checks."""
        print("Running knowledge health checks...")
        checks = {}

        # Check for gap analysis report
        gap_report = SYNC_DIR / f"GAP_ANALYSIS_{COMPUTER}.json"
        if gap_report.exists():
            try:
                with open(gap_report) as f:
                    gap_data = json.load(f)
                gap_score = gap_data.get("gap_score", 100)
                checks["knowledge_gaps"] = {
                    "status": "PASS" if gap_score < 30 else "WARN" if gap_score < 50 else "FAIL",
                    "value": gap_score,
                    "message": f"Gap score: {gap_score}/100 (lower is better)"
                }
            except:
                checks["knowledge_gaps"] = {"status": "WARN", "message": "Invalid gap report"}
        else:
            checks["knowledge_gaps"] = {"status": "WARN", "message": "No gap analysis run"}

        # Check atom quality
        db_path = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT AVG(confidence) FROM atoms")
                avg_conf = cursor.fetchone()[0] or 0
                conn.close()
                checks["atom_quality"] = {
                    "status": "PASS" if avg_conf > 0.6 else "WARN",
                    "value": round(avg_conf * 100, 1),
                    "message": f"Avg confidence: {avg_conf*100:.1f}%"
                }
            except:
                checks["atom_quality"] = {"status": "WARN", "message": "Could not check quality"}
        else:
            checks["atom_quality"] = {"status": "FAIL", "message": "No database"}

        self.results["knowledge_health"] = checks
        return checks

    def calculate_score(self):
        """Calculate overall health score."""
        total_checks = 0
        passed_checks = 0

        for category in ["system_health", "backup_health", "knowledge_health"]:
            for check_name, check_data in self.results[category].items():
                total_checks += 1
                if check_data.get("status") == "PASS":
                    passed_checks += 1
                elif check_data.get("status") == "WARN":
                    passed_checks += 0.5

        self.results["max_score"] = total_checks
        self.results["overall_score"] = passed_checks

        percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        if percentage >= 90:
            self.results["status"] = "HEALTHY"
        elif percentage >= 70:
            self.results["status"] = "GOOD"
        elif percentage >= 50:
            self.results["status"] = "DEGRADED"
        else:
            self.results["status"] = "CRITICAL"

        return percentage

    def run_all(self):
        """Run all health checks."""
        print("=" * 60)
        print("UNIFIED HEALTH CHECK")
        print(f"Computer: {COMPUTER}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("=" * 60 + "\n")

        self.run_system_checks()
        self.run_backup_checks()
        self.run_knowledge_checks()

        percentage = self.calculate_score()

        # Print results
        print("\n### SYSTEM HEALTH ###")
        for name, data in self.results["system_health"].items():
            status_icon = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]"}.get(data["status"], "[??]")
            print(f"  {status_icon} {name}: {data['message']}")

        print("\n### BACKUP HEALTH ###")
        for name, data in self.results["backup_health"].items():
            status_icon = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]"}.get(data["status"], "[??]")
            print(f"  {status_icon} {name}: {data['message']}")

        print("\n### KNOWLEDGE HEALTH ###")
        for name, data in self.results["knowledge_health"].items():
            status_icon = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]"}.get(data["status"], "[??]")
            print(f"  {status_icon} {name}: {data['message']}")

        print("\n" + "=" * 60)
        print(f"OVERALL STATUS: {self.results['status']}")
        print(f"SCORE: {self.results['overall_score']:.1f}/{self.results['max_score']} ({percentage:.1f}%)")
        print("=" * 60)

        return self.results

    def save_report(self):
        """Save health report to files."""
        # Local
        local_path = CONSCIOUSNESS / f"HEALTH_REPORT_{COMPUTER}.json"
        with open(local_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nLocal report: {local_path}")

        # Sync folder
        if SYNC_DIR.exists():
            sync_path = SYNC_DIR / f"HEALTH_REPORT_{COMPUTER}.json"
            with open(sync_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"Sync report: {sync_path}")


def main():
    checker = UnifiedHealthCheck()
    checker.run_all()
    checker.save_report()


if __name__ == "__main__":
    main()
