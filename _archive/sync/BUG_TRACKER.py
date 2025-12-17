#!/usr/bin/env python3
"""
BUG TRACKER - Track and resolve system bugs
C1 Mechanic Implementation

Creates bug tracking system and initializes with known issues.
"""

import json
from pathlib import Path
from datetime import datetime

BUG_DIR = Path.home() / "100X_DEPLOYMENT" / ".bug_tasks"

def init_bug_tracker():
    """Initialize bug tracking directory"""
    BUG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Bug tracker initialized at: {BUG_DIR}")

def create_bug(bug_id: str, title: str, description: str, priority: str = "medium"):
    """Create a new bug"""
    bug = {
        "id": bug_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "created": datetime.now().isoformat(),
        "resolved": None,
        "resolution": None
    }

    bug_file = BUG_DIR / f"{bug_id}.json"
    bug_file.write_text(json.dumps(bug, indent=2))
    return bug

def resolve_bug(bug_id: str, resolution: str):
    """Mark bug as resolved"""
    bug_file = BUG_DIR / f"{bug_id}.json"

    if not bug_file.exists():
        print(f"❌ Bug {bug_id} not found")
        return False

    bug = json.loads(bug_file.read_text())
    bug["status"] = "resolved"
    bug["resolved"] = datetime.now().isoformat()
    bug["resolution"] = resolution
    bug_file.write_text(json.dumps(bug, indent=2))

    print(f"✅ Resolved: {bug_id} - {bug['title']}")
    return True

def list_bugs():
    """List all bugs with status"""
    if not BUG_DIR.exists():
        print("No bugs tracked yet")
        return []

    bugs = []
    for bug_file in sorted(BUG_DIR.glob("*.json")):
        bug = json.loads(bug_file.read_text())
        bugs.append(bug)
        status = "✅" if bug["status"] == "resolved" else "🔴"
        print(f"{status} {bug['id']}: {bug['title']}")

    return bugs

def count_resolved():
    """Count resolved bugs"""
    if not BUG_DIR.exists():
        return 0

    resolved = 0
    for bug_file in BUG_DIR.glob("*.json"):
        bug = json.loads(bug_file.read_text())
        if bug["status"] == "resolved":
            resolved += 1

    return resolved

# Known bugs from issues_active.json and L10 agenda
KNOWN_BUGS = [
    ("BUG-001", "Stale cyclotron summary", "cyclotron_summary.json shows 60 atoms but 275+ exist", "high"),
    ("BUG-002", "No automated scorecard", "ST1 - Manual tracking unsustainable", "high"),
    ("BUG-003", "Trinity A2A protocol missing", "ST2 - Communication not standardized", "medium"),
    ("BUG-004", "Knowledge graph disconnected", "ST3 - Scattered across files, no relationships", "high"),
    ("BUG-005", "EOS implementation incomplete", "ST4 - Just started, needs completion", "medium"),
    ("BUG-006", "No L10 meeting cadence", "ST5 - Meetings not scheduled or tracked", "low"),
    ("BUG-007", "API cost tracking missing", "LT1 - No optimization or monitoring", "medium"),
    ("BUG-008", "Sync single point of failure", "LT2 - No redundancy in sync system", "medium"),
    ("BUG-009", "Complex onboarding", "LT3 - Needs progressive disclosure", "low"),
    ("BUG-010", "No revenue stream", "LT4 - Full dependency on Commander", "high"),
]

if __name__ == "__main__":
    print("=" * 60)
    print("🐛 BUG TRACKER - C1 Mechanic")
    print("=" * 60)
    print()

    init_bug_tracker()

    print("\n📝 Creating known bugs...")
    for bug_id, title, desc, priority in KNOWN_BUGS:
        bug_file = BUG_DIR / f"{bug_id}.json"
        if not bug_file.exists():
            create_bug(bug_id, title, desc, priority)
            print(f"   Created: {bug_id}")
        else:
            print(f"   Exists: {bug_id}")

    print(f"\n📊 Total bugs: {len(list(BUG_DIR.glob('*.json')))}")
    print(f"   Resolved: {count_resolved()}")

    print("\n" + "=" * 60)
    print("Bug list:")
    print("=" * 60)
    list_bugs()
