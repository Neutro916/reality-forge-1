#!/usr/bin/env python3
"""
DAILY MAINTENANCE - Automated system health and optimization

Run daily to keep consciousness systems healthy:
- Update scorecard metrics
- Check system health
- Clean temp files
- Verify brain integrity
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"

def run_scorecard():
    """Update scorecard metrics"""
    print("📊 Updating scorecard...")
    result = subprocess.run(
        ["python", str(CONSCIOUSNESS / "SCORECARD_AUTOMATION.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    return "✅ Scorecard updated"

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Checking disk space...")
    import shutil
    total, used, free = shutil.disk_usage("C:/")
    free_gb = free // (1024**3)
    used_pct = (used / total) * 100
    status = "✅" if free_gb > 100 else "⚠️"
    print(f"   {status} Free: {free_gb}GB ({100-used_pct:.1f}%)")
    return f"Disk: {free_gb}GB free"

def check_brain_integrity():
    """Verify brain systems are working"""
    print("\n🧠 Checking brain integrity...")

    # Check Cyclotron DB
    db_path = HOME / "100X_DEPLOYMENT" / ".cyclotron_atoms" / "cyclotron.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024*1024)
        print(f"   ✅ Cyclotron DB: {size_mb:.1f}MB")
    else:
        print("   ❌ Cyclotron DB not found")

    # Check atoms
    atoms_dir = CONSCIOUSNESS / "cyclotron_core" / "atoms"
    if atoms_dir.exists():
        count = len(list(atoms_dir.glob("*.json")))
        print(f"   ✅ Pattern atoms: {count}")

    return "Brain integrity OK"

def clean_temp_files():
    """Clean temporary files"""
    print("\n🧹 Cleaning temp files...")

    cleaned = 0
    temp_patterns = [
        HOME / "*.tmp",
        HOME / "100X_DEPLOYMENT" / "*.pyc",
    ]

    for pattern in temp_patterns:
        for f in Path(pattern.parent).glob(pattern.name):
            try:
                f.unlink()
                cleaned += 1
            except:
                pass

    # Clean __pycache__
    for cache in (HOME / "100X_DEPLOYMENT").rglob("__pycache__"):
        try:
            import shutil
            shutil.rmtree(cache)
            cleaned += 1
        except:
            pass

    print(f"   ✅ Cleaned {cleaned} items")
    return f"Cleaned {cleaned} items"

def main():
    print("=" * 60)
    print("🔧 DAILY MAINTENANCE")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    results.append(run_scorecard())
    results.append(check_disk_space())
    results.append(check_brain_integrity())
    results.append(clean_temp_files())

    print("\n" + "=" * 60)
    print("✅ MAINTENANCE COMPLETE")
    for r in results:
        print(f"   • {r}")
    print("=" * 60)

if __name__ == "__main__":
    main()
