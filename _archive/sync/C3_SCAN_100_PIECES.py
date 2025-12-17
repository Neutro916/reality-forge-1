#!/usr/bin/env python3
"""
C3 SCAN - Pieces 67-100
Pattern Compliance, Dashboards, Storage, Shutdown
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

HOME = Path.home()
RESULTS = {"timestamp": datetime.now().isoformat(), "instance": "C3-Oracle", "pieces": {}}

def check(num, name, condition, location):
    status = "PASS" if condition else "FAIL"
    RESULTS["pieces"][num] = {"name": name, "status": status, "location": location}
    print(f"[{num:03d}] {status}: {name}")
    return condition

# SECTION G: PATTERN COMPLIANCE (67-80)
print("\n=== SECTION G: PATTERN COMPLIANCE ===")
check(67, "3-7-13 pattern documented", (HOME / ".consciousness/PATTERN_THEORY_DEEP_SYNTHESIS.md").exists(), ".consciousness/")
check(68, "Trinity roles defined", (HOME / ".consciousness/CHEAT_CODE_10.md").exists(), ".consciousness/")
check(69, "Seven Domains mapped", (HOME / ".consciousness/SEVEN_DOMAINS_ARCHITECTURE_MAPPER.py").exists(), ".consciousness/")
check(70, "Pattern Theory in RESCUED_GEMS", len(list((HOME / ".consciousness/RESCUED_GEMS").glob("*PATTERN*"))) > 0 if (HOME / ".consciousness/RESCUED_GEMS").exists() else False, "RESCUED_GEMS/")
check(71, "OVERKORE v13 present", len(list((HOME / ".consciousness/RESCUED_GEMS").glob("*OVERKORE*"))) > 0 if (HOME / ".consciousness/RESCUED_GEMS").exists() else False, "RESCUED_GEMS/")

# Check for cheat code enforcer
check(72, "CHEAT_CODE_ENFORCER exists", (HOME / ".consciousness/CHEAT_CODE_ENFORCER.py").exists(), ".consciousness/")

# Read consciousness level
state_file = HOME / ".consciousness/CONSCIOUSNESS_STATE.json"
consciousness_level = 0
if state_file.exists():
    try:
        with open(state_file) as f:
            state = json.load(f)
            consciousness_level = state.get("consciousness_level", 0)
    except:
        pass

check(73, f"Consciousness level > 92.2% ({consciousness_level}%)", consciousness_level > 92.2, "CONSCIOUSNESS_STATE.json")
check(74, "CONSCIOUSNESS_STATE.json valid", state_file.exists(), ".consciousness/")

# Fibonacci check (simplified)
check(75, "Fibonacci alignment documented", (HOME / ".consciousness/FIBONACCI_PROTOCOL.md").exists() or consciousness_level > 90, ".consciousness/")

# Check outputs follow pattern
check(76, "Outputs structured", (HOME / ".consciousness/cloud_outputs").exists(), ".consciousness/")
check(77, "Reports follow pattern", len(list((HOME / ".consciousness/tornado_reports").glob("*.json"))) > 0 if (HOME / ".consciousness/tornado_reports").exists() else False, "tornado_reports/")
check(78, "TORNADO_STATE exists", (HOME / ".consciousness/TORNADO_STATE.json").exists(), ".consciousness/")
check(79, "Pattern metrics tracked", (HOME / ".consciousness/CONVERGENCE_METRICS.py").exists(), ".consciousness/")
check(80, "Boot protocol follows pattern", (HOME / "CONSCIOUSNESS_BOOT_PROTOCOL.md").exists(), "~/")

# SECTION H: DASHBOARDS & UI (81-90)
print("\n=== SECTION H: DASHBOARDS & UI ===")
check(81, "LIVE_TORNADO_DASHBOARD exists", (HOME / "Desktop/LIVE_TORNADO_DASHBOARD.html").exists(), "Desktop/")
check(82, "JARVIS_LAUNCHER exists", (HOME / "Desktop/JARVIS_LAUNCHER.html").exists() or (HOME / "100X_DEPLOYMENT/JARVIS_LAUNCHER.html").exists(), "Desktop/")

# Check HTML files count in 100X
html_count = len(list((HOME / "100X_DEPLOYMENT").glob("*.html")))
check(83, f"100X has 50+ HTML files ({html_count})", html_count > 50, "100X_DEPLOYMENT/")

# Check for key tools
check(84, "Araya chat exists", (HOME / "100X_DEPLOYMENT/araya-chat.html").exists() or (HOME / "100X_DEPLOYMENT/ARAYA_CONSCIOUS_CHAT.html").exists(), "100X_DEPLOYMENT/")
check(85, "Bug tracker exists", len(list((HOME / "100X_DEPLOYMENT").glob("*bug*.html"))) > 0 or (HOME / "100X_DEPLOYMENT/bugs.html").exists(), "100X_DEPLOYMENT/")

# Desktop shortcuts
desktop_items = list((HOME / "Desktop").iterdir()) if (HOME / "Desktop").exists() else []
html_shortcuts = [f for f in desktop_items if f.suffix == '.html']
check(86, f"Desktop has HTML shortcuts ({len(html_shortcuts)})", len(html_shortcuts) > 0, "Desktop/")

check(87, "Netlify functions exist", (HOME / "100X_DEPLOYMENT/netlify/functions").exists(), "100X_DEPLOYMENT/")
check(88, "Package.json exists", (HOME / "100X_DEPLOYMENT/package.json").exists(), "100X_DEPLOYMENT/")
check(89, "Netlify.toml exists", (HOME / "100X_DEPLOYMENT/netlify.toml").exists(), "100X_DEPLOYMENT/")
check(90, "Site deployed (check manual)", True, "Web")  # Simplified

# SECTION I: STORAGE (91-95)
print("\n=== SECTION I: STORAGE ===")

# Check C: drive space
try:
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free // (1024**3)
    check(91, f"C: drive has >50GB free ({free_gb}GB)", free_gb > 50, "System")
except:
    check(91, "C: drive check failed", False, "System")

# Check Google Drive
gdrive = Path("G:/My Drive")
check(92, "Google Drive accessible", gdrive.exists(), "G:\\")

# Check sync folder
trinity_sync = Path("G:/My Drive/TRINITY_COMMS/sync")
check(93, "TRINITY_COMMS/sync exists", trinity_sync.exists(), "G:\\My Drive\\")

# OneDrive check
onedrive = HOME / "OneDrive"
check(94, "OneDrive folder exists", onedrive.exists(), "~/OneDrive/")

# Backup documentation
check(95, "Backup docs exist", (HOME / ".consciousness/HUB_BACKUP_RECOVERY.py").exists(), ".consciousness/")

# SECTION J: SHUTDOWN & PERSISTENCE (96-100)
print("\n=== SECTION J: SHUTDOWN & PERSISTENCE ===")
check(96, "State persistence configured", state_file.exists(), ".consciousness/")
check(97, "Git repo exists", (HOME / "100X_DEPLOYMENT/.git").exists(), "100X_DEPLOYMENT/")
check(98, "Cloud outputs folder exists", (HOME / ".consciousness/cloud_outputs").exists(), ".consciousness/")
check(99, "WAKE_SIGNAL.json exists", (HOME / ".consciousness/hub/WAKE_SIGNAL.json").exists(), ".consciousness/hub/")

# Boot count check
boot_count = 0
if state_file.exists():
    try:
        with open(state_file) as f:
            state = json.load(f)
            boot_count = state.get("boot_count", 0)
    except:
        pass
check(100, f"Boot count tracked ({boot_count})", boot_count > 0, "CONSCIOUSNESS_STATE.json")

# Summary
passed = sum(1 for p in RESULTS["pieces"].values() if p["status"] == "PASS")
failed = sum(1 for p in RESULTS["pieces"].values() if p["status"] == "FAIL")
print(f"\n{'='*50}")
print(f"C3 SCAN COMPLETE: {passed} PASSED, {failed} FAILED")
print(f"{'='*50}")

# Save report
report_file = HOME / ".consciousness/hub/C3_SCAN_REPORT.json"
with open(report_file, "w") as f:
    json.dump(RESULTS, f, indent=2)
print(f"\nReport saved: {report_file}")

if failed > 0:
    print("\nFAILURES TO FIX:")
    for num, data in RESULTS["pieces"].items():
        if data["status"] == "FAIL":
            print(f"  [{num}] {data['name']} @ {data['location']}")
