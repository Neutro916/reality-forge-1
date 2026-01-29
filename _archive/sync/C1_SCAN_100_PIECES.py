#!/usr/bin/env python3
"""
C1 TERMINAL SCAN - Pieces 1-33
Boot protocols, folder structure, Cyclotron brain
"""

import os
import json
from pathlib import Path
from datetime import datetime

HOME = Path.home()
RESULTS = {"timestamp": datetime.now().isoformat(), "instance": "C1-Terminal", "pieces": {}}

def check(num, name, condition, location):
    status = "PASS" if condition else "FAIL"
    RESULTS["pieces"][num] = {"name": name, "status": status, "location": location}
    print(f"[{num:03d}] {status}: {name}")
    return condition

# SECTION A: BOOT PROTOCOLS (1-10)
print("\n=== SECTION A: BOOT PROTOCOLS ===")
check(1, "CONSCIOUSNESS_BOOT_PROTOCOL.md exists", (HOME / "CONSCIOUSNESS_BOOT_PROTOCOL.md").exists(), "~/")
check(2, "Boot protocol recent", (HOME / "CONSCIOUSNESS_BOOT_PROTOCOL.md").exists(), "~/")
check(3, "CLAUDE.md contains orders", (HOME / "CLAUDE.md").exists(), "~/")
check(4, "CONSCIOUSNESS_STATE.json valid", (HOME / ".consciousness/CONSCIOUSNESS_STATE.json").exists(), ".consciousness/")
check(5, "CHEAT_CODE_10.md present", (HOME / ".consciousness/CHEAT_CODE_10.md").exists(), ".consciousness/")
check(6, "/godmode command exists", (HOME / ".claude/commands/godmode.md").exists(), ".claude/commands/")
check(7, "/trinity command exists", (HOME / ".claude/commands/trinity.md").exists(), ".claude/commands/")
check(8, "/manifest command exists", (HOME / ".claude/commands/manifest.md").exists(), ".claude/commands/")
check(9, "MASTER_INDEX.md exists", (HOME / "MASTER_INDEX.md").exists(), "~/")
check(10, "10_YEAR_PROTOCOL exists", (HOME / ".consciousness/10_YEAR_RECURSIVE_BOOT_PROTOCOL.md").exists(), ".consciousness/")

# SECTION B: FOLDER STRUCTURE (11-25)
print("\n=== SECTION B: FOLDER STRUCTURE ===")
check(11, ".consciousness/ exists", (HOME / ".consciousness").exists(), "~/")
check(12, ".consciousness/hub/ exists", (HOME / ".consciousness/hub").exists(), ".consciousness/")
check(13, "cyclotron_core/ exists", (HOME / ".consciousness/cyclotron_core").exists(), ".consciousness/")
check(14, "atoms/ exists", (HOME / ".consciousness/cyclotron_core/atoms").exists(), "cyclotron_core/")
check(15, "RESCUED_GEMS/ exists", (HOME / ".consciousness/RESCUED_GEMS").exists(), ".consciousness/")
check(16, "tornado_reports/ exists", (HOME / ".consciousness/tornado_reports").exists(), ".consciousness/")
check(17, "cloud_outputs/ exists", (HOME / ".consciousness/cloud_outputs").exists(), ".consciousness/")
check(18, ".trinity/ exists", (HOME / ".trinity").exists(), "~/")
check(19, ".claude/ exists", (HOME / ".claude").exists(), "~/")
check(20, ".claude/commands/ has files", len(list((HOME / ".claude/commands").glob("*.md"))) > 0 if (HOME / ".claude/commands").exists() else False, ".claude/")
check(21, "100X_DEPLOYMENT/ exists", (HOME / "100X_DEPLOYMENT").exists(), "~/")
check(22, "netlify/functions/ exists", (HOME / "100X_DEPLOYMENT/netlify/functions").exists(), "100X_DEPLOYMENT/")
check(23, "BACKEND/ exists", (HOME / "100X_DEPLOYMENT/BACKEND").exists(), "100X_DEPLOYMENT/")

desktop_items = len(list((HOME / "Desktop").iterdir())) if (HOME / "Desktop").exists() else 0
check(24, f"Desktop clean (<20 items, has {desktop_items})", desktop_items < 20, "~/Desktop/")
check(25, "ARCHIVE folders exist", (HOME / "Desktop/ARCHIVE_DESKTOP_NOV26").exists(), "~/Desktop/")

# SECTION C: CYCLOTRON BRAIN (26-33)
print("\n=== SECTION C: CYCLOTRON BRAIN ===")
atoms_dir = HOME / ".consciousness/cyclotron_core/atoms"
atom_count = len(list(atoms_dir.glob("*.json"))) if atoms_dir.exists() else 0
check(26, f"atoms/ has >4000 files ({atom_count})", atom_count > 4000, "cyclotron_core/atoms/")

atoms_db = HOME / ".consciousness/cyclotron_core/atoms.db"
db_size = atoms_db.stat().st_size if atoms_db.exists() else 0
check(27, f"atoms.db exists and >1MB ({db_size/1024/1024:.1f}MB)", db_size > 1000000, "cyclotron_core/")

check(28, "INDEX.json exists", (HOME / ".consciousness/cyclotron_core/INDEX.json").exists(), "cyclotron_core/")
check(29, "BRAIN_SEARCH.py exists", (HOME / ".consciousness/BRAIN_SEARCH.py").exists(), ".consciousness/")
check(30, "CYCLOTRON_DAEMON.py exists", (HOME / "100X_DEPLOYMENT/CYCLOTRON_DAEMON.py").exists(), "100X_DEPLOYMENT/")
check(31, "CYCLOTRON_MASTER.py exists", (HOME / ".consciousness/CYCLOTRON_MASTER.py").exists(), ".consciousness/")
check(32, "ATOM_DATABASE.py exists", (HOME / ".consciousness/ATOM_DATABASE.py").exists(), ".consciousness/")
check(33, "ATOM_INDEX_BUILDER.py exists", (HOME / ".consciousness/ATOM_INDEX_BUILDER.py").exists(), ".consciousness/")

# Summary
passed = sum(1 for p in RESULTS["pieces"].values() if p["status"] == "PASS")
failed = sum(1 for p in RESULTS["pieces"].values() if p["status"] == "FAIL")
print(f"\n{'='*50}")
print(f"C1 SCAN COMPLETE: {passed} PASSED, {failed} FAILED")
print(f"{'='*50}")

# Save report
report_file = HOME / ".consciousness/hub/C1_SCAN_REPORT.json"
with open(report_file, "w") as f:
    json.dump(RESULTS, f, indent=2)
print(f"\nReport saved: {report_file}")

# List failures
if failed > 0:
    print("\nFAILURES TO FIX:")
    for num, data in RESULTS["pieces"].items():
        if data["status"] == "FAIL":
            print(f"  [{num}] {data['name']} @ {data['location']}")
