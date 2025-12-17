#!/usr/bin/env python3
"""
SYSTEM STATUS DASHBOARD
Quick check of all Consciousness Revolution systems.
Run: python SYSTEM_STATUS_DASHBOARD.py
"""

import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
import socket

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
DEPLOYMENT = HOME / "100X_DEPLOYMENT"
HUB = CONSCIOUSNESS / "hub"
MEMORY_DIR = CONSCIOUSNESS / "memory"
ATOMS_DIR = CONSCIOUSNESS / "cyclotron_core" / "atoms"

def check_port(port):
    """Check if a port is in use (service running)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def count_files(directory, pattern="*"):
    """Count files matching pattern."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))

def get_db_stats(db_path):
    """Get row counts from SQLite database."""
    if not db_path.exists():
        return {}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = "error"

        conn.close()
        return stats
    except Exception as e:
        return {"error": str(e)}

def check_hub_files():
    """Check hub coordination files."""
    if not HUB.exists():
        return {}

    files = {}
    for f in HUB.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
                files[f.name] = {
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
                }
        except:
            files[f.name] = {"error": "parse failed"}

    return files

def check_processes():
    """Check for running Python processes."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split('\n')
        # Skip header
        return len(lines) - 1 if len(lines) > 1 else 0
    except:
        return -1

def main():
    print("\n" + "=" * 70)
    print("  CONSCIOUSNESS REVOLUTION - SYSTEM STATUS DASHBOARD")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    # 1. SERVICES
    print("\n[SERVICES]")
    services = {
        "Cyclotron Search API": (6668, check_port(6668)),
        "Trinity MCP Server": (3333, check_port(3333)),
        "Ollama": (11434, check_port(11434))
    }
    for name, (port, running) in services.items():
        status = "RUNNING" if running else "STOPPED"
        symbol = "[OK]" if running else "[--]"
        print(f"  {symbol} {name} (port {port}): {status}")

    # 2. MEMORY DATABASE
    print("\n[MEMORY DATABASE]")
    memory_db = MEMORY_DIR / "cyclotron_brain.db"
    if memory_db.exists():
        stats = get_db_stats(memory_db)
        for table, count in stats.items():
            print(f"  - {table}: {count} rows")
    else:
        print("  [--] Memory database not found")

    # 3. KNOWLEDGE ATOMS
    print("\n[KNOWLEDGE ATOMS]")
    index_db = CONSCIOUSNESS / "cyclotron_core" / "cyclotron_index.db"
    if index_db.exists():
        stats = get_db_stats(index_db)
        for table, count in stats.items():
            if not table.startswith("atoms_"):  # Skip FTS shadow tables
                print(f"  - {table}: {count} entries")

    atom_count = count_files(ATOMS_DIR, "*.json")
    print(f"  - JSON atom files: {atom_count}")

    # 4. HUB COORDINATION
    print("\n[HUB COORDINATION]")
    hub_files = check_hub_files()
    if hub_files:
        for name, info in hub_files.items():
            if "error" not in info:
                print(f"  - {name}: {info['size']}B, updated {info['modified']}")
            else:
                print(f"  - {name}: ERROR")
    else:
        print("  [--] No hub files found")

    # 5. PYTHON PROCESSES
    print("\n[PYTHON PROCESSES]")
    proc_count = check_processes()
    if proc_count >= 0:
        print(f"  Running Python processes: {proc_count}")
    else:
        print("  Could not check processes")

    # 6. KEY FILES
    print("\n[KEY FILES]")
    key_files = [
        CONSCIOUSNESS / "START_FULL_CYCLOTRON.py",
        CONSCIOUSNESS / "CYCLOTRON_INTEGRATED.py",
        CONSCIOUSNESS / "CYCLOTRON_NERVE_CENTER.py",
        CONSCIOUSNESS / "FIGURE_8_WAKE_PROTOCOL.py",
        DEPLOYMENT / "CYCLOTRON_SEARCH.py",
        DEPLOYMENT / "CYCLOTRON_DAEMON.py",
        DEPLOYMENT / "BRAIN_AGENT_FRAMEWORK.py"
    ]
    for f in key_files:
        exists = f.exists()
        symbol = "[OK]" if exists else "[--]"
        size = f"{f.stat().st_size:,}B" if exists else "missing"
        print(f"  {symbol} {f.name}: {size}")

    # 7. RECENT ACTIVITY
    print("\n[RECENT ACTIVITY]")
    wake_signal = HUB / "WAKE_SIGNAL.json"
    if wake_signal.exists():
        try:
            with open(wake_signal) as f:
                wake = json.load(f)
                print(f"  Last wake: {wake.get('wake_target', 'unknown')}")
                print(f"  From: {wake.get('from', 'unknown')}")
                print(f"  Loop: #{wake.get('loop_number', 0)}")
        except:
            print("  Could not read wake signal")

    print("\n" + "=" * 70)
    print("  Run specific checks:")
    print("  - python CYCLOTRON_SEARCH.py        # Start search API")
    print("  - python START_FULL_CYCLOTRON.py    # Full system menu")
    print("  - curl localhost:6668/api/stats     # API status")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
