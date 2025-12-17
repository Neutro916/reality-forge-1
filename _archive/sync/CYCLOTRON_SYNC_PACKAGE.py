#!/usr/bin/env python3
"""
CYCLOTRON SYNC PACKAGE
Creates a portable package of the Cyclotron system for deployment to CP2, CP3.

This script:
1. Gathers all required files
2. Creates a self-extracting bootstrap
3. Can sync via USB, network share, or cloud storage
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
DEPLOYMENT = HOME / "100X_DEPLOYMENT"
OUTPUT_DIR = HOME / "Desktop" / "CYCLOTRON_PACKAGE"

# Files to include in the sync package
CORE_FILES = [
    # Memory & Learning
    "CYCLOTRON_MEMORY.py",
    "DATA_CHUNKER.py",

    # Integration
    "CYCLOTRON_INTEGRATED.py",
    "CYCLOTRON_NERVE_CENTER.py",
    "CYCLOTRON_GUARDIAN.py",

    # Coordination
    "FIGURE_8_WAKE_PROTOCOL.py",
    "START_FULL_CYCLOTRON.py",
]

DEPLOYMENT_FILES = [
    "BRAIN_AGENT_FRAMEWORK.py",
    "ADVANCED_BRAIN_AGENTS.py",
    "CYCLOTRON_BRAIN_AGENT.py",
    "CYCLOTRON_BRAIN_BRIDGE.py",
]

def create_bootstrap_script():
    """Create a script that sets up the system on a new computer"""
    return '''#!/usr/bin/env python3
"""
CYCLOTRON BOOTSTRAP
Run this on CP2/CP3 to set up the full system.
"""

import os
import shutil
from pathlib import Path

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
DEPLOYMENT = HOME / "100X_DEPLOYMENT"

def setup():
    print("="*60)
    print("CYCLOTRON BOOTSTRAP - Setting up on this computer")
    print("="*60)

    # Create directories
    CONSCIOUSNESS.mkdir(parents=True, exist_ok=True)
    (CONSCIOUSNESS / "hub").mkdir(exist_ok=True)
    (CONSCIOUSNESS / "memory").mkdir(exist_ok=True)
    (CONSCIOUSNESS / "memory" / "atoms").mkdir(exist_ok=True)
    (CONSCIOUSNESS / "agents").mkdir(exist_ok=True)
    DEPLOYMENT.mkdir(parents=True, exist_ok=True)

    print(f"Created: {CONSCIOUSNESS}")
    print(f"Created: {DEPLOYMENT}")

    # Copy files from package
    package_dir = Path(__file__).parent

    # Copy consciousness files
    consciousness_files = list(package_dir.glob("consciousness_*.py"))
    for f in consciousness_files:
        dest_name = f.name.replace("consciousness_", "")
        dest = CONSCIOUSNESS / dest_name
        shutil.copy(f, dest)
        print(f"Installed: {dest}")

    # Copy deployment files
    deployment_files = list(package_dir.glob("deployment_*.py"))
    for f in deployment_files:
        dest_name = f.name.replace("deployment_", "")
        dest = DEPLOYMENT / dest_name
        shutil.copy(f, dest)
        print(f"Installed: {dest}")

    # Initialize memory database
    print("\\nInitializing memory system...")
    import sys
    sys.path.insert(0, str(CONSCIOUSNESS))
    from CYCLOTRON_MEMORY import ensure_memory_exists
    ensure_memory_exists()

    print("\\n" + "="*60)
    print("BOOTSTRAP COMPLETE!")
    print("="*60)
    print(f"\\nTo start the system:")
    print(f"  python {CONSCIOUSNESS}/START_FULL_CYCLOTRON.py")
    print(f"\\nOr quick start:")
    print(f"  python {CONSCIOUSNESS}/START_FULL_CYCLOTRON.py quick")

if __name__ == "__main__":
    setup()
'''

def create_config_template():
    """Create configuration template for new installations"""
    return {
        "computer_id": "CP2",  # Change to CP2, CP3, etc.
        "agent_ids": {
            "terminal": "C1-Terminal",  # Rename per computer
            "cloud": "C1-Cloud"
        },
        "hub_sync": {
            "method": "file",  # file, tailscale, cloud
            "path": None,  # Set to shared path
            "interval_seconds": 30
        },
        "memory_sync": {
            "enabled": False,
            "remote_db": None
        },
        "installed": datetime.now().isoformat()
    }

def create_package():
    """Create the full sync package"""
    print("="*60)
    print("CREATING CYCLOTRON SYNC PACKAGE")
    print("="*60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clean previous package
    for f in OUTPUT_DIR.glob("*"):
        if f.is_file():
            f.unlink()

    files_copied = 0

    # Copy core consciousness files
    print("\nCopying consciousness files...")
    for filename in CORE_FILES:
        src = CONSCIOUSNESS / filename
        if src.exists():
            # Prefix with consciousness_ for bootstrap to identify
            dest = OUTPUT_DIR / f"consciousness_{filename}"
            shutil.copy(src, dest)
            print(f"  + {filename}")
            files_copied += 1
        else:
            print(f"  ! Missing: {filename}")

    # Copy deployment files
    print("\nCopying deployment files...")
    for filename in DEPLOYMENT_FILES:
        src = DEPLOYMENT / filename
        if src.exists():
            dest = OUTPUT_DIR / f"deployment_{filename}"
            shutil.copy(src, dest)
            print(f"  + {filename}")
            files_copied += 1
        else:
            print(f"  ! Missing: {filename}")

    # Create bootstrap script
    print("\nCreating bootstrap script...")
    bootstrap_path = OUTPUT_DIR / "BOOTSTRAP.py"
    with open(bootstrap_path, 'w') as f:
        f.write(create_bootstrap_script())
    print(f"  + BOOTSTRAP.py")

    # Create config template
    print("\nCreating config template...")
    config_path = OUTPUT_DIR / "config_template.json"
    with open(config_path, 'w') as f:
        json.dump(create_config_template(), f, indent=2)
    print(f"  + config_template.json")

    # Create README
    readme = f"""# CYCLOTRON SYNC PACKAGE
Generated: {datetime.now().isoformat()}
From: {HOME}

## Installation on CP2/CP3:

1. Copy this entire folder to the target computer
2. Run: python BOOTSTRAP.py
3. Start: python ~/.consciousness/START_FULL_CYCLOTRON.py

## Files Included:
- {files_copied} Python modules
- Bootstrap installer
- Config template

## After Installation:
1. Edit ~/.consciousness/cyclotron_config.json
2. Set computer_id to CP2 or CP3
3. Configure hub_sync if using shared storage
"""

    readme_path = OUTPUT_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme)
    print(f"  + README.md")

    # Create ZIP archive
    print("\nCreating ZIP archive...")
    zip_path = HOME / "Desktop" / f"CYCLOTRON_PACKAGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in OUTPUT_DIR.glob("*"):
            zipf.write(file, file.name)
    print(f"  + {zip_path.name}")

    print("\n" + "="*60)
    print("PACKAGE CREATED!")
    print("="*60)
    print(f"\nFolder: {OUTPUT_DIR}")
    print(f"ZIP: {zip_path}")
    print(f"Files: {files_copied + 3}")  # +3 for bootstrap, config, readme

    return str(OUTPUT_DIR), str(zip_path)

def sync_to_network(share_path: str):
    """Sync package to a network share"""
    if not Path(share_path).exists():
        print(f"Network share not found: {share_path}")
        return False

    dest = Path(share_path) / "CYCLOTRON_PACKAGE"
    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(OUTPUT_DIR, dest)
    print(f"Synced to: {dest}")
    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "sync" and len(sys.argv) > 2:
            create_package()
            sync_to_network(sys.argv[2])
        else:
            print("Usage:")
            print("  python CYCLOTRON_SYNC_PACKAGE.py        - Create package")
            print("  python CYCLOTRON_SYNC_PACKAGE.py sync <path>  - Create and sync to network")
    else:
        create_package()
