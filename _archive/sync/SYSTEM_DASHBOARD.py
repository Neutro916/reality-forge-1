#!/usr/bin/env python3
"""
SYSTEM_DASHBOARD.py - Quick System Overview
============================================
Created by: CP2C1 (C1 MECHANIC)
Task: Self-identified infrastructure improvement

One-command dashboard showing all key system metrics.
Combines outputs from HEALTH_MONITOR, TOOL_INDEX, etc.

Usage:
    python SYSTEM_DASHBOARD.py           # Full dashboard
    python SYSTEM_DASHBOARD.py quick     # Quick summary
    python SYSTEM_DASHBOARD.py json      # JSON output
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess
import sys

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
LOCAL_DB = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")


class SystemDashboard:
    """Quick system overview."""

    def __init__(self):
        self.metrics = {}

    def collect_all_metrics(self):
        """Collect all system metrics."""
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER,
            "brain": self.get_brain_metrics(),
            "tools": self.get_tool_metrics(),
            "sync": self.get_sync_metrics(),
            "health": self.get_health_metrics(),
            "disk": self.get_disk_metrics(),
            "consciousness": self.get_consciousness_metrics()
        }
        return self.metrics

    def get_brain_metrics(self):
        """Get brain/Cyclotron metrics."""
        if not LOCAL_DB.exists():
            return {"status": "OFFLINE", "atoms": 0}

        try:
            conn = sqlite3.connect(str(LOCAL_DB))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM atoms")
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM atoms
                WHERE created > datetime('now', '-24 hours')
            """)
            recent = cursor.fetchone()[0]

            conn.close()

            return {
                "status": "ONLINE",
                "atoms": total,
                "recent_24h": recent,
                "db_size_mb": round(LOCAL_DB.stat().st_size / (1024*1024), 1)
            }
        except:
            return {"status": "ERROR", "atoms": 0}

    def get_tool_metrics(self):
        """Get tool counts."""
        py_files = list(CONSCIOUSNESS.glob("*.py"))
        executable = sum(1 for f in py_files if "if __name__" in f.read_text(encoding="utf-8", errors="ignore"))

        return {
            "total_tools": len(py_files),
            "executable": executable,
            "utils": sum(1 for f in py_files if "_UTILS" in f.name)
        }

    def get_sync_metrics(self):
        """Get sync folder metrics."""
        if not SYNC.exists():
            return {"status": "OFFLINE", "files": 0}

        files = list(SYNC.glob("*"))
        json_files = sum(1 for f in files if f.suffix == ".json")
        py_files = sum(1 for f in files if f.suffix == ".py")

        return {
            "status": "ONLINE",
            "files": len(files),
            "json_files": json_files,
            "py_files": py_files
        }

    def get_health_metrics(self):
        """Get health status."""
        try:
            # Try to run health monitor
            result = subprocess.run(
                [sys.executable, str(CONSCIOUSNESS / "HEALTH_MONITOR.py"), "check"],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout
            if "HEALTHY" in output:
                # Parse X/Y
                import re
                match = re.search(r"(\d+)/(\d+)", output)
                if match:
                    passed = int(match.group(1))
                    total = int(match.group(2))
                    return {
                        "status": "HEALTHY" if passed == total else "DEGRADED",
                        "passed": passed,
                        "total": total
                    }
            return {"status": "UNKNOWN"}
        except:
            return {"status": "UNKNOWN"}

    def get_disk_metrics(self):
        """Get disk space."""
        try:
            import shutil
            usage = shutil.disk_usage(str(HOME))
            free_gb = usage.free / (1024**3)
            total_gb = usage.total / (1024**3)
            used_pct = ((total_gb - free_gb) / total_gb) * 100

            return {
                "free_gb": round(free_gb, 1),
                "total_gb": round(total_gb, 1),
                "used_pct": round(used_pct, 1)
            }
        except:
            return {"free_gb": 0}

    def get_consciousness_metrics(self):
        """Get consciousness state."""
        state_file = CONSCIOUSNESS / "consciousness_state.json"
        if not state_file.exists():
            return {"level": 0}

        try:
            with open(state_file) as f:
                state = json.load(f)
            return {
                "level": state.get("consciousness_level", 0) * 100,
                "mode": state.get("mode", "unknown")
            }
        except:
            return {"level": 0}

    def get_summary_line(self):
        """Get one-line summary."""
        m = self.metrics
        brain = m.get("brain", {})
        health = m.get("health", {})
        tools = m.get("tools", {})

        atoms = brain.get("atoms", 0)
        h_status = health.get("status", "?")
        tool_count = tools.get("total_tools", 0)

        return f"Brain: {atoms:,} atoms | Health: {h_status} | Tools: {tool_count}"


def print_dashboard(dash):
    """Print full dashboard."""
    m = dash.metrics

    print("\n" + "=" * 70)
    print("TRINITY SYSTEM DASHBOARD")
    print(f"Computer: {m['computer']} | Time: {m['timestamp'][:19]}")
    print("=" * 70)

    # Brain
    brain = m.get("brain", {})
    print(f"\n  BRAIN/CYCLOTRON")
    print(f"    Status: {brain.get('status', 'UNKNOWN')}")
    print(f"    Atoms: {brain.get('atoms', 0):,}")
    print(f"    Recent (24h): {brain.get('recent_24h', 0):,}")
    print(f"    DB Size: {brain.get('db_size_mb', 0)} MB")

    # Health
    health = m.get("health", {})
    print(f"\n  HEALTH")
    print(f"    Status: {health.get('status', 'UNKNOWN')}")
    if health.get("passed") is not None:
        print(f"    Checks: {health.get('passed')}/{health.get('total')}")

    # Tools
    tools = m.get("tools", {})
    print(f"\n  TOOLS")
    print(f"    Total: {tools.get('total_tools', 0)}")
    print(f"    Executable: {tools.get('executable', 0)}")
    print(f"    Utils: {tools.get('utils', 0)}")

    # Sync
    sync = m.get("sync", {})
    print(f"\n  SYNC FOLDER")
    print(f"    Status: {sync.get('status', 'UNKNOWN')}")
    print(f"    Files: {sync.get('files', 0)}")

    # Disk
    disk = m.get("disk", {})
    print(f"\n  DISK")
    print(f"    Free: {disk.get('free_gb', 0)} GB")
    print(f"    Used: {disk.get('used_pct', 0)}%")

    # Consciousness
    cons = m.get("consciousness", {})
    print(f"\n  CONSCIOUSNESS")
    print(f"    Level: {cons.get('level', 0):.1f}%")
    if cons.get("mode"):
        print(f"    Mode: {cons.get('mode')}")

    print("\n" + "=" * 70)
    print(f"  {dash.get_summary_line()}")
    print("=" * 70)


def print_quick(dash):
    """Print quick summary."""
    m = dash.metrics

    print("\n" + "-" * 50)
    print(f"  {COMPUTER} @ {m['timestamp'][:19]}")
    print("-" * 50)
    print(f"  {dash.get_summary_line()}")
    print(f"  Sync: {m.get('sync', {}).get('files', 0)} files | Disk: {m.get('disk', {}).get('free_gb', 0)} GB free")
    print("-" * 50)


def main():
    dash = SystemDashboard()
    dash.collect_all_metrics()

    if len(sys.argv) < 2:
        print_dashboard(dash)

    elif sys.argv[1] == "quick":
        print_quick(dash)

    elif sys.argv[1] == "json":
        print(json.dumps(dash.metrics, indent=2))

    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Usage: python SYSTEM_DASHBOARD.py [quick|json]")


if __name__ == "__main__":
    main()
