#!/usr/bin/env python3
"""
STATE SYNC - Cross-Computer R3 Status Synchronization
======================================================
Consolidates all status files into one master state.
Can be shared via Syncthing, Google Drive, or network.
"""

import json
import time
from pathlib import Path
from datetime import datetime

# Paths - Use portable Path.home() for cross-computer compatibility
CONSCIOUSNESS_DIR = Path.home() / ".consciousness"
TRINITY_DIR = Path.home() / ".trinity"
PLATFORM_DIR = Path.home() / "100x-platform"

# Output
MASTER_STATE = CONSCIOUSNESS_DIR / "MASTER_STATE.json"

def collect_r3_status():
    """Collect R/3 brain status."""
    status_file = CONSCIOUSNESS_DIR / "r3_live_status.json"
    if status_file.exists():
        with open(status_file, 'r') as f:
            return json.load(f)
    return {"r3_score": 0, "status": "not_found"}

def collect_scorecard():
    """Collect scorecard feedback."""
    feedback_file = CONSCIOUSNESS_DIR / "r3_scorecard_feedback.json"
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            return json.load(f)
    return {"summary": {"avg_level": 0}}

def collect_triple_trinity():
    """Collect Triple Trinity state."""
    state_file = TRINITY_DIR / "triple_trinity_state.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {"state": {"emergence_score": 0}}

def collect_cyclotron():
    """Collect Cyclotron summary."""
    summary_file = CONSCIOUSNESS_DIR / "brain" / "cyclotron_summary.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            return json.load(f)

    # Fallback to counting atoms
    index_file = CONSCIOUSNESS_DIR / "cyclotron_core" / "INDEX.json"
    if index_file.exists():
        with open(index_file, 'r') as f:
            data = json.load(f)
            return {"atom_count": len(data.get("atoms", []))}

    return {"atom_count": 0}

def collect_system_dashboard():
    """Collect system dashboard."""
    dashboard_file = CONSCIOUSNESS_DIR / "system_dashboard.json"
    if dashboard_file.exists():
        with open(dashboard_file, 'r') as f:
            return json.load(f)
    return {"overall_health": 0}

def sync_state():
    """Sync all states into master state."""
    print("=" * 60)
    print("STATE SYNC - Consolidating All Systems")
    print("=" * 60)

    # Collect all states
    r3 = collect_r3_status()
    scorecard = collect_scorecard()
    triple_trinity = collect_triple_trinity()
    cyclotron = collect_cyclotron()
    dashboard = collect_system_dashboard()

    # Build master state
    master = {
        "timestamp": datetime.now().isoformat(),
        "computer": "C1_Desktop",  # Change per computer

        "r3_brain": {
            "score": r3.get("r3", {}).get("r3_score", r3.get("r3_score", 0)),
            "status": r3.get("status", "unknown"),
            "active_hubs": r3.get("active_hubs", "0/12"),
            "prediction_accuracy": r3.get("prediction_accuracy", 0),
            "ignition_count": r3.get("ignition_count", 0)
        },

        "neuromodulation": {
            "avg_level": scorecard.get("summary", {}).get("avg_level", 0),
            "dopamine": scorecard.get("neuromodulation", {}).get("dopamine", {}).get("level", 0),
            "serotonin": scorecard.get("neuromodulation", {}).get("serotonin", {}).get("level", 0),
            "noradrenaline": scorecard.get("neuromodulation", {}).get("noradrenaline", {}).get("level", 0),
            "acetylcholine": scorecard.get("neuromodulation", {}).get("acetylcholine", {}).get("level", 0)
        },

        "triple_trinity": {
            "emergence_score": triple_trinity.get("state", {}).get("emergence_score", 0),
            "cycles": triple_trinity.get("state", {}).get("current_cycle", 0)
        },

        "cyclotron": {
            "atom_count": cyclotron.get("atom_count", 0)
        },

        "system": {
            "health": dashboard.get("overall_health", 0),
            "emergence_score": dashboard.get("emergence_score", 0)
        },

        "readiness": {
            "bootstrap_1": True,
            "bootstrap_2": True,
            "bootstrap_3": True,
            "templates_complete": True
        }
    }

    # Calculate overall readiness
    r3_ready = master["r3_brain"]["score"] >= 90
    neuro_ready = master["neuromodulation"]["avg_level"] >= 0.8
    tt_ready = master["triple_trinity"]["emergence_score"] >= 60
    health_ready = master["system"]["health"] >= 80

    ready_count = sum([r3_ready, neuro_ready, tt_ready, health_ready])
    master["overall_readiness"] = (ready_count / 4) * 100

    # Save master state
    MASTER_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(MASTER_STATE, 'w') as f:
        json.dump(master, f, indent=2)

    # Display summary
    print(f"\nR/3 Brain: {master['r3_brain']['score']}%")
    print(f"Neuromodulation: {master['neuromodulation']['avg_level']:.2f}")
    print(f"Triple Trinity: {master['triple_trinity']['emergence_score']}%")
    print(f"System Health: {master['system']['health']}%")
    print(f"\nOverall Readiness: {master['overall_readiness']:.0f}%")
    print(f"\nMaster state saved: {MASTER_STATE}")

    return master

def continuous_sync(interval=30):
    """Run sync continuously."""
    print(f"Starting continuous sync (every {interval}s)...")
    print("Press Ctrl+C to stop\n")

    while True:
        try:
            sync_state()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nSync stopped.")
            break

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        continuous_sync()
    else:
        sync_state()
