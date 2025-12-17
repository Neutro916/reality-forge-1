#!/usr/bin/env python3
"""
CLAUDE COCKPIT - Master Situational Awareness System
=====================================================
One daemon to rule them all. Generates multiple glance files
that Claude can read with a single READ call each.

Output Files (all in .consciousness/cockpit/):
- MASTER_GLANCE.json      - Everything in one file
- TRINITY_GLANCE.json     - Trinity status, messages, tasks
- GIT_GLANCE.json         - Repo status, recent commits, branches
- DAEMONS_GLANCE.json     - Running Python scripts, ports, servers
- SYSTEM_GLANCE.json      - CPU, RAM, disk, network
- CYCLOTRON_GLANCE.json   - Recent atoms, query results

Usage:
    python CLAUDE_COCKPIT.py              # Run full cockpit daemon
    python CLAUDE_COCKPIT.py --once       # Single capture
    python CLAUDE_COCKPIT.py --query "search term"  # Cyclotron query
"""

import os
import sys
import json
import time
import socket
import sqlite3
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Paths
HOME = Path(os.environ.get('USERPROFILE', Path.home()))
CONSCIOUSNESS = HOME / '.consciousness'
COCKPIT_DIR = CONSCIOUSNESS / 'cockpit'
TRINITY_HUB = HOME / '.trinity' / 'hub'
TRINITY_MCP = CONSCIOUSNESS / 'hub'
CYCLOTRON_ATOMS = CONSCIOUSNESS / 'cyclotron_core' / 'atoms'
REPOS_TO_WATCH = [
    HOME,
    HOME / '100X_DEPLOYMENT',
    HOME / 'AI_AUTOMATION_TOOLS'
]

# Output files
MASTER_FILE = COCKPIT_DIR / 'MASTER_GLANCE.json'
TRINITY_FILE = COCKPIT_DIR / 'TRINITY_GLANCE.json'
GIT_FILE = COCKPIT_DIR / 'GIT_GLANCE.json'
DAEMONS_FILE = COCKPIT_DIR / 'DAEMONS_GLANCE.json'
SYSTEM_FILE = COCKPIT_DIR / 'SYSTEM_GLANCE.json'
CYCLOTRON_FILE = COCKPIT_DIR / 'CYCLOTRON_GLANCE.json'
QUERY_FILE = COCKPIT_DIR / 'CYCLOTRON_QUERY.txt'
QUERY_RESULT_FILE = COCKPIT_DIR / 'CYCLOTRON_QUERY_RESULT.json'

# Config
UPDATE_INTERVAL = 10  # seconds

def ensure_dirs():
    COCKPIT_DIR.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] COCKPIT: {msg}")

# ============================================================
# TRINITY GLANCE
# ============================================================
def get_trinity_glance() -> Dict[str, Any]:
    """Get Trinity status, messages, and tasks in one shot."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "instances": {},
        "messages": [],
        "tasks": [],
        "summary": ""
    }

    # Read instance status files
    for hub in [TRINITY_HUB, TRINITY_MCP]:
        if hub.exists():
            for f in hub.glob('*_status.json'):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        instance = data.get('instance', f.stem.replace('_status', ''))
                        result['instances'][instance] = {
                            'status': data.get('status', 'unknown'),
                            'task': data.get('current_task', 'none'),
                            'updated': data.get('last_update', 'unknown'),
                            'computer': data.get('computer', 'unknown')
                        }
                except (json.JSONDecodeError, IOError, KeyError):
                    pass

            # Read recent messages (last 10)
            for f in sorted(hub.glob('message_*.json'), reverse=True)[:10]:
                try:
                    with open(f) as fp:
                        result['messages'].append(json.load(fp))
                except (json.JSONDecodeError, IOError):
                    pass

            # Read task queue
            task_file = hub / 'TASK_QUEUE.json'
            if task_file.exists():
                try:
                    with open(task_file) as fp:
                        result['tasks'] = json.load(fp).get('tasks', [])[:5]
                except (json.JSONDecodeError, IOError, KeyError):
                    pass

    # Summary
    online = [k for k, v in result['instances'].items() if v.get('status') == 'online']
    result['summary'] = f"Trinity: {len(online)} online ({', '.join(online)}) | {len(result['messages'])} msgs | {len(result['tasks'])} tasks"

    return result

# ============================================================
# GIT GLANCE
# ============================================================
def run_git(repo: Path, cmd: str) -> str:
    """Run git command in repo."""
    try:
        result = subprocess.run(
            f'git -C "{repo}" {cmd}',
            shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return ""

def get_git_glance() -> Dict[str, Any]:
    """Get git status for watched repos."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "repos": {},
        "summary": ""
    }

    for repo in REPOS_TO_WATCH:
        git_dir = repo / '.git'
        if git_dir.exists():
            repo_name = repo.name or 'home'

            # Status
            status_raw = run_git(repo, 'status --porcelain')
            status_lines = [l for l in status_raw.split('\n') if l.strip()]

            # Branch
            branch = run_git(repo, 'rev-parse --abbrev-ref HEAD')

            # Recent commits
            log_raw = run_git(repo, 'log --oneline -5')
            commits = [l for l in log_raw.split('\n') if l.strip()]

            # Diff stat
            diff_stat = run_git(repo, 'diff --stat HEAD~1 2>/dev/null')

            result['repos'][repo_name] = {
                'path': str(repo),
                'branch': branch,
                'modified_files': len(status_lines),
                'status_preview': status_lines[:5],
                'recent_commits': commits,
                'changes_since_last': diff_stat[:200] if diff_stat else "No changes"
            }

    # Summary
    total_modified = sum(r.get('modified_files', 0) for r in result['repos'].values())
    result['summary'] = f"Git: {len(result['repos'])} repos | {total_modified} modified files"

    return result

# ============================================================
# DAEMONS GLANCE
# ============================================================
def get_daemons_glance() -> Dict[str, Any]:
    """Get running Python processes and servers."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "python_scripts": [],
        "servers": [],
        "notable_processes": [],
        "summary": ""
    }

    notable_names = ['python', 'node', 'ollama', 'claude', 'ngrok', 'tailscale']

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            info = proc.info
            name = (info['name'] or '').lower()

            # Python scripts
            if 'python' in name:
                cmdline = info.get('cmdline', [])
                script = 'unknown'
                if cmdline and len(cmdline) > 1:
                    for arg in cmdline[1:]:
                        if arg.endswith('.py'):
                            script = os.path.basename(arg)
                            break

                uptime = datetime.now() - datetime.fromtimestamp(info['create_time'])
                result['python_scripts'].append({
                    'pid': info['pid'],
                    'script': script,
                    'cpu': round(info['cpu_percent'] or 0, 1),
                    'memory': round(info['memory_percent'] or 0, 1),
                    'uptime_minutes': int(uptime.total_seconds() / 60)
                })

            # Notable processes
            for notable in notable_names:
                if notable in name and notable != 'python':
                    result['notable_processes'].append({
                        'name': info['name'],
                        'pid': info['pid']
                    })
                    break

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Check common server ports
    common_ports = [3000, 5000, 6666, 8000, 8080, 8888, 11434]
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex(('localhost', port)) == 0:
                result['servers'].append({'port': port, 'status': 'listening'})
            sock.close()
        except (socket.error, OSError):
            pass

    # Summary
    result['summary'] = f"Daemons: {len(result['python_scripts'])} Python | {len(result['servers'])} servers | {len(result['notable_processes'])} notable"

    return result

# ============================================================
# SYSTEM GLANCE
# ============================================================
def get_system_glance() -> Dict[str, Any]:
    """Get system health metrics."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {},
        "memory": {},
        "disk": {},
        "network": {},
        "summary": ""
    }

    # CPU
    result['cpu'] = {
        'percent': psutil.cpu_percent(interval=0.5),
        'cores': psutil.cpu_count(),
        'freq_mhz': round(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
    }

    # Memory
    mem = psutil.virtual_memory()
    result['memory'] = {
        'percent': mem.percent,
        'used_gb': round(mem.used / (1024**3), 1),
        'total_gb': round(mem.total / (1024**3), 1),
        'available_gb': round(mem.available / (1024**3), 1)
    }

    # Disk
    disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
    result['disk'] = {
        'percent': disk.percent,
        'used_gb': round(disk.used / (1024**3), 1),
        'total_gb': round(disk.total / (1024**3), 1),
        'free_gb': round(disk.free / (1024**3), 1)
    }

    # Network (basic)
    try:
        net = psutil.net_io_counters()
        result['network'] = {
            'bytes_sent_mb': round(net.bytes_sent / (1024**2), 1),
            'bytes_recv_mb': round(net.bytes_recv / (1024**2), 1)
        }
    except (AttributeError, RuntimeError):
        result['network'] = {}

    # Summary
    result['summary'] = f"System: CPU {result['cpu']['percent']}% | RAM {result['memory']['percent']}% | Disk {result['disk']['percent']}%"

    return result

# ============================================================
# CYCLOTRON GLANCE
# ============================================================
def get_cyclotron_glance() -> Dict[str, Any]:
    """Get Cyclotron status and recent atoms."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_atoms": 0,
        "recent_atoms": [],
        "query_result": None,
        "summary": ""
    }

    # Count atoms
    if CYCLOTRON_ATOMS.exists():
        atom_files = list(CYCLOTRON_ATOMS.glob('*.json'))
        result['total_atoms'] = len(atom_files)

        # Get 5 most recent
        recent = sorted(atom_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
        for f in recent:
            try:
                with open(f) as fp:
                    atom = json.load(fp)
                    result['recent_atoms'].append({
                        'id': atom.get('id', f.stem),
                        'content': atom.get('content', '')[:100],
                        'type': atom.get('type', 'unknown')
                    })
            except (json.JSONDecodeError, IOError, KeyError):
                pass

    # Check for query
    if QUERY_FILE.exists():
        try:
            query = QUERY_FILE.read_text().strip()
            if query:
                # Search atoms
                matches = []
                for f in CYCLOTRON_ATOMS.glob('*.json'):
                    try:
                        with open(f) as fp:
                            atom = json.load(fp)
                            content = json.dumps(atom).lower()
                            if query.lower() in content:
                                matches.append({
                                    'id': atom.get('id'),
                                    'content': atom.get('content', '')[:200],
                                    'type': atom.get('type')
                                })
                                if len(matches) >= 10:
                                    break
                    except (json.JSONDecodeError, IOError, KeyError):
                        pass

                result['query_result'] = {
                    'query': query,
                    'matches': len(matches),
                    'results': matches
                }

                # Write result file
                with open(QUERY_RESULT_FILE, 'w') as f:
                    json.dump(result['query_result'], f, indent=2)

                # Clear query
                QUERY_FILE.unlink()
        except (IOError, OSError, json.JSONDecodeError):
            pass

    # Summary
    result['summary'] = f"Cyclotron: {result['total_atoms']} atoms"
    if result['query_result']:
        result['summary'] += f" | Query '{result['query_result']['query']}': {result['query_result']['matches']} matches"

    return result

def save_all_glances():
    """Generate and save all glance files."""
    # Individual files
    trinity = get_trinity_glance()
    with open(TRINITY_FILE, 'w') as f:
        json.dump(trinity, f, indent=2)

    git = get_git_glance()
    with open(GIT_FILE, 'w') as f:
        json.dump(git, f, indent=2)

    daemons = get_daemons_glance()
    with open(DAEMONS_FILE, 'w') as f:
        json.dump(daemons, f, indent=2)

    system = get_system_glance()
    with open(SYSTEM_FILE, 'w') as f:
        json.dump(system, f, indent=2)

    cyclotron = get_cyclotron_glance()
    with open(CYCLOTRON_FILE, 'w') as f:
        json.dump(cyclotron, f, indent=2)

    # Master file
    master = {
        "_meta": {
            "purpose": "Claude Cockpit - Complete situational awareness in one READ",
            "updated": datetime.now().isoformat(),
            "update_interval": UPDATE_INTERVAL
        },
        "quick_status": f"{system['summary']} | {trinity['summary']} | {daemons['summary']}",
        "trinity": trinity,
        "git": git,
        "daemons": daemons,
        "system": system,
        "cyclotron": cyclotron
    }
    with open(MASTER_FILE, 'w') as f:
        json.dump(master, f, indent=2)

    return master

def run_once():
    """Single capture."""
    ensure_dirs()
    log("Single capture mode...")
    master = save_all_glances()
    log(f"Output: {COCKPIT_DIR}")
    print(f"\nQuick Status: {master['quick_status']}")

def run_daemon():
    """Run continuous cockpit updates."""
    ensure_dirs()
    log("=" * 60)
    log("CLAUDE COCKPIT STARTING")
    log(f"Output: {COCKPIT_DIR}")
    log(f"Interval: {UPDATE_INTERVAL}s")
    log("=" * 60)
    log("")
    log("Claude can READ these files:")
    log(f"  {MASTER_FILE} (everything)")
    log(f"  {TRINITY_FILE}")
    log(f"  {GIT_FILE}")
    log(f"  {DAEMONS_FILE}")
    log(f"  {SYSTEM_FILE}")
    log(f"  {CYCLOTRON_FILE}")
    log("")
    log("To query Cyclotron, write search term to:")
    log(f"  {QUERY_FILE}")
    log("")

    count = 0
    while True:
        try:
            master = save_all_glances()
            count += 1

            if count % 6 == 0:  # Log every minute
                log(master['quick_status'])

            time.sleep(UPDATE_INTERVAL)

        except KeyboardInterrupt:
            log("Stopped by user")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(UPDATE_INTERVAL)

def query_cyclotron(query: str):
    """Write a query for the daemon to process."""
    ensure_dirs()
    QUERY_FILE.write_text(query)
    log(f"Query written: {query}")
    log(f"Results will appear in: {QUERY_RESULT_FILE}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            run_once()
        elif sys.argv[1] == '--query' and len(sys.argv) > 2:
            query_cyclotron(' '.join(sys.argv[2:]))
        else:
            print("Usage:")
            print("  python CLAUDE_COCKPIT.py          # Run daemon")
            print("  python CLAUDE_COCKPIT.py --once   # Single capture")
            print("  python CLAUDE_COCKPIT.py --query 'search'  # Cyclotron query")
    else:
        run_daemon()
