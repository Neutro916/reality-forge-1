#!/usr/bin/env python3
"""
CYCLOTRON_SYNC.py - Cross-Computer State Synchronization
C2 Ordered - 2025-11-25

Syncs state between local .consciousness and Dropbox for multi-computer operation.

SYNC STRATEGY (C2 Decision):
- LAYER 1: Git for code (versioned, rollback)
- LAYER 2: Dropbox for state (real-time, atoms, hub)
- LAYER 3: Tailscale for direct comms (low latency)

This handles LAYER 2 - Dropbox state sync.
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
HOME = Path.home()
LOCAL_CONSCIOUSNESS = HOME / ".consciousness"
DROPBOX_BASE = HOME / "Dropbox"
DROPBOX_FEDERATION = DROPBOX_BASE / ".cyclotron_federation"
DROPBOX_TRINITY = DROPBOX_BASE / ".trinity_network"
DROPBOX_BRAIN = DROPBOX_BASE / "Consciousness_Brain"

# What to sync
SYNC_CONFIG = {
    "hub": {
        "local": LOCAL_CONSCIOUSNESS / "hub",
        "remote": DROPBOX_TRINITY / "trinity",
        "pattern": "*.json",
        "direction": "bidirectional"
    },
    "atoms": {
        "local": LOCAL_CONSCIOUSNESS / "cyclotron_core" / "atoms",
        "remote": DROPBOX_FEDERATION / "atoms",
        "pattern": "*.json",
        "direction": "push_merge"  # Push local, merge remote
    },
    "memory_db": {
        "local": LOCAL_CONSCIOUSNESS / "memory",
        "remote": DROPBOX_FEDERATION / "computers" / f"{os.environ.get('COMPUTERNAME', 'CP1')}",
        "pattern": "*.db",
        "direction": "push"  # Each computer pushes its own
    },
    "shared_knowledge": {
        "local": LOCAL_CONSCIOUSNESS / "shared_knowledge",
        "remote": DROPBOX_FEDERATION / "shared_knowledge",
        "pattern": "*.json",
        "direction": "bidirectional"
    },
    "indices": {
        "local": LOCAL_CONSCIOUSNESS / "indices",
        "remote": DROPBOX_FEDERATION / "indices",
        "pattern": "*.json",
        "direction": "bidirectional"
    }
}

def log(msg: str, level: str = "INFO"):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] SYNC [{level}]: {msg}")

def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file for comparison."""
    if not filepath.exists():
        return ""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def get_file_mtime(filepath: Path) -> float:
    """Get modification time."""
    if not filepath.exists():
        return 0
    return filepath.stat().st_mtime

def sync_files(local_dir: Path, remote_dir: Path, pattern: str, direction: str) -> Dict:
    """Sync files between local and remote directories."""
    results = {"synced": 0, "skipped": 0, "errors": 0}

    # Ensure directories exist
    local_dir.mkdir(parents=True, exist_ok=True)
    remote_dir.mkdir(parents=True, exist_ok=True)

    local_files = set(f.name for f in local_dir.glob(pattern))
    remote_files = set(f.name for f in remote_dir.glob(pattern))
    all_files = local_files | remote_files

    for filename in all_files:
        local_path = local_dir / filename
        remote_path = remote_dir / filename

        try:
            local_mtime = get_file_mtime(local_path)
            remote_mtime = get_file_mtime(remote_path)
            local_hash = get_file_hash(local_path)
            remote_hash = get_file_hash(remote_path)

            # Skip if identical
            if local_hash == remote_hash and local_hash:
                results["skipped"] += 1
                continue

            if direction == "push":
                # Always push local to remote
                if local_path.exists():
                    shutil.copy2(local_path, remote_path)
                    log(f"PUSH: {filename}")
                    results["synced"] += 1

            elif direction == "pull":
                # Always pull remote to local
                if remote_path.exists():
                    shutil.copy2(remote_path, local_path)
                    log(f"PULL: {filename}")
                    results["synced"] += 1

            elif direction == "bidirectional":
                # Newer wins
                if local_mtime > remote_mtime and local_path.exists():
                    shutil.copy2(local_path, remote_path)
                    log(f"PUSH (newer): {filename}")
                    results["synced"] += 1
                elif remote_mtime > local_mtime and remote_path.exists():
                    shutil.copy2(remote_path, local_path)
                    log(f"PULL (newer): {filename}")
                    results["synced"] += 1
                elif not local_path.exists() and remote_path.exists():
                    shutil.copy2(remote_path, local_path)
                    log(f"PULL (new): {filename}")
                    results["synced"] += 1
                elif local_path.exists() and not remote_path.exists():
                    shutil.copy2(local_path, remote_path)
                    log(f"PUSH (new): {filename}")
                    results["synced"] += 1

            elif direction == "push_merge":
                # Push local, but also pull anything new from remote
                if local_path.exists():
                    # Always push our version
                    shutil.copy2(local_path, remote_path)
                    results["synced"] += 1
                if not local_path.exists() and remote_path.exists():
                    # Pull if we don't have it
                    shutil.copy2(remote_path, local_path)
                    log(f"MERGE: {filename}")
                    results["synced"] += 1

        except Exception as e:
            log(f"Error syncing {filename}: {e}", "ERROR")
            results["errors"] += 1

    return results

def write_sync_manifest(results: Dict):
    """Write manifest showing last sync state."""
    manifest = {
        "computer": os.environ.get("COMPUTERNAME", "unknown"),
        "timestamp": datetime.now().isoformat() + "Z",
        "results": results,
        "local_path": str(LOCAL_CONSCIOUSNESS),
        "dropbox_path": str(DROPBOX_BASE)
    }

    manifest_path = DROPBOX_TRINITY / "sync_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Also write local copy
    local_manifest = LOCAL_CONSCIOUSNESS / "last_sync.json"
    with open(local_manifest, "w") as f:
        json.dump(manifest, f, indent=2)

def check_dropbox_status() -> bool:
    """Check if Dropbox is available."""
    if not DROPBOX_BASE.exists():
        log("Dropbox folder not found!", "ERROR")
        return False

    # Check if Dropbox is actively syncing (presence of .dropbox files)
    log(f"Dropbox found at: {DROPBOX_BASE}")
    log(f"Federation: {DROPBOX_FEDERATION.exists()}")
    log(f"Trinity: {DROPBOX_TRINITY.exists()}")
    log(f"Brain: {DROPBOX_BRAIN.exists()}")

    return True

def full_sync():
    """Run full sync across all configured paths."""
    log("=" * 60)
    log("CYCLOTRON STATE SYNC STARTING")
    log(f"Computer: {os.environ.get('COMPUTERNAME', 'unknown')}")
    log("=" * 60)

    if not check_dropbox_status():
        return {"error": "Dropbox not available"}

    all_results = {}

    for sync_name, config in SYNC_CONFIG.items():
        log(f"\nSyncing: {sync_name}")
        log(f"  Local:  {config['local']}")
        log(f"  Remote: {config['remote']}")
        log(f"  Direction: {config['direction']}")

        results = sync_files(
            config["local"],
            config["remote"],
            config["pattern"],
            config["direction"]
        )

        all_results[sync_name] = results
        log(f"  Result: {results['synced']} synced, {results['skipped']} unchanged, {results['errors']} errors")

    write_sync_manifest(all_results)

    log("\n" + "=" * 60)
    log("SYNC COMPLETE")
    log("=" * 60)

    total_synced = sum(r["synced"] for r in all_results.values())
    total_errors = sum(r["errors"] for r in all_results.values())
    log(f"Total files synced: {total_synced}")
    log(f"Total errors: {total_errors}")

    return all_results

def quick_sync():
    """Quick sync - just hub files for fast coordination."""
    log("Quick sync - hub only")
    config = SYNC_CONFIG["hub"]
    return sync_files(
        config["local"],
        config["remote"],
        config["pattern"],
        config["direction"]
    )

def push_atoms():
    """Push knowledge atoms to Dropbox."""
    log("Pushing knowledge atoms to Dropbox")
    config = SYNC_CONFIG["atoms"]
    return sync_files(
        config["local"],
        config["remote"],
        config["pattern"],
        config["direction"]
    )

def get_status() -> Dict:
    """Get current sync status."""
    status = {
        "dropbox_available": DROPBOX_BASE.exists(),
        "local_consciousness": LOCAL_CONSCIOUSNESS.exists(),
        "sync_targets": {}
    }

    for sync_name, config in SYNC_CONFIG.items():
        status["sync_targets"][sync_name] = {
            "local_exists": config["local"].exists(),
            "remote_exists": config["remote"].exists(),
            "local_files": len(list(config["local"].glob(config["pattern"]))) if config["local"].exists() else 0,
            "remote_files": len(list(config["remote"].glob(config["pattern"]))) if config["remote"].exists() else 0
        }

    return status

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "quick":
            quick_sync()
        elif cmd == "atoms":
            push_atoms()
        elif cmd == "status":
            status = get_status()
            print(json.dumps(status, indent=2))
        else:
            print("Usage:")
            print("  python CYCLOTRON_SYNC.py        - Full sync")
            print("  python CYCLOTRON_SYNC.py quick  - Hub only (fast)")
            print("  python CYCLOTRON_SYNC.py atoms  - Push knowledge atoms")
            print("  python CYCLOTRON_SYNC.py status - Show sync status")
    else:
        full_sync()
