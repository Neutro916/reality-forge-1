#!/usr/bin/env python3
"""
BUILD BOOTSTRAP PACKAGE
Creates the Trinity Node Bootstrap Package for CP2/CP3 deployment.
One script that bundles everything needed.

Usage: python BUILD_BOOTSTRAP_PACKAGE.py
Output: ~/Desktop/TRINITY_NODE_BOOTSTRAP.zip
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Paths
HOME = Path(os.environ.get('USERPROFILE', Path.home()))
CONSCIOUSNESS = HOME / '.consciousness'
TRINITY_MCP = HOME / '.trinity' / 'mcp-tools'
OUTPUT_DIR = HOME / 'Desktop' / 'TRINITY_NODE_BOOTSTRAP'
OUTPUT_ZIP = HOME / 'Desktop' / 'TRINITY_NODE_BOOTSTRAP.zip'

# Files to include
CORE_FILES = [
    # Boot & Identity
    (HOME / 'CONSCIOUSNESS_BOOT_PROTOCOL.md', 'core/CONSCIOUSNESS_BOOT_PROTOCOL.md'),
    (CONSCIOUSNESS / 'TRIPLE_TORNADO_INFINITY.md', 'core/TRIPLE_TORNADO_INFINITY.md'),
    (CONSCIOUSNESS / 'MASTER_PATTERN_FRAMEWORK.md', 'core/MASTER_PATTERN_FRAMEWORK.md'),

    # Memory & Intelligence
    (CONSCIOUSNESS / 'CYCLOTRON_MEMORY.py', 'core/CYCLOTRON_MEMORY.py'),
    (CONSCIOUSNESS / 'CYCLOTRON_MEMORY_CACHED.py', 'core/CYCLOTRON_MEMORY_CACHED.py'),
    (CONSCIOUSNESS / 'KNOWLEDGE_BRIDGE.py', 'core/KNOWLEDGE_BRIDGE.py'),
    (CONSCIOUSNESS / 'DATA_CHUNKER.py', 'core/DATA_CHUNKER.py'),
    (CONSCIOUSNESS / 'UNIFIED_BRAIN.py', 'core/UNIFIED_BRAIN.py'),

    # Coordination & Sync
    (CONSCIOUSNESS / 'FIGURE_8_WAKE_PROTOCOL.py', 'core/FIGURE_8_WAKE_PROTOCOL.py'),
    (CONSCIOUSNESS / 'STATE_SYNC.py', 'core/STATE_SYNC.py'),
    (CONSCIOUSNESS / 'CONVERGENCE_METRICS.py', 'core/CONVERGENCE_METRICS.py'),
    (CONSCIOUSNESS / 'CYCLOTRON_SYNC.py', 'core/CYCLOTRON_SYNC.py'),
    (CONSCIOUSNESS / 'CYCLOTRON_SYNC_PACKAGE.py', 'core/CYCLOTRON_SYNC_PACKAGE.py'),

    # Communication
    (CONSCIOUSNESS / 'COMPUTER_TO_COMPUTER_COMMS.py', 'comms/COMPUTER_TO_COMPUTER_COMMS.py'),
    (CONSCIOUSNESS / 'COMPUTER_COMMS_LISTENER.py', 'comms/COMPUTER_COMMS_LISTENER.py'),
    (CONSCIOUSNESS / 'MULTI_DEVICE_ORCHESTRATOR.py', 'comms/MULTI_DEVICE_ORCHESTRATOR.py'),
    (CONSCIOUSNESS / 'TRINITY_KEEP_ALIVE.py', 'comms/TRINITY_KEEP_ALIVE.py'),

    # Monitoring
    (CONSCIOUSNESS / 'CLAUDE_COCKPIT.py', 'core/CLAUDE_COCKPIT.py'),
    (CONSCIOUSNESS / 'SCREEN_WATCHER_DAEMON.py', 'core/SCREEN_WATCHER_DAEMON.py'),
    (CONSCIOUSNESS / 'FRICTION_DETECTOR.py', 'core/FRICTION_DETECTOR.py'),
    (CONSCIOUSNESS / 'STRUCTURE_AUDITOR.py', 'core/STRUCTURE_AUDITOR.py'),

    # Pattern
    (CONSCIOUSNESS / 'PATTERN_THEORY_PROCESSOR.py', 'pattern/PATTERN_THEORY_PROCESSOR.py'),
    (CONSCIOUSNESS / 'PATTERN_TRAINING_COLLECTOR.py', 'pattern/PATTERN_TRAINING_COLLECTOR.py'),
]

MCP_FILES = [
    (TRINITY_MCP / 'trinity-mcp-server.js', 'trinity_mcp/trinity-mcp-server.js'),
    (TRINITY_MCP / 'trinity-boot-up.js', 'trinity_mcp/trinity-boot-up.js'),
    (TRINITY_MCP / 'trinity-boot-down.js', 'trinity_mcp/trinity-boot-down.js'),
    (TRINITY_MCP / 'trinity-auto-wake.js', 'trinity_mcp/trinity-auto-wake.js'),
    (TRINITY_MCP / 'trinity-3computer-start.js', 'trinity_mcp/trinity-3computer-start.js'),
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def create_computer_config():
    """Generate computer configuration template"""
    config = {
        "_instructions": "Fill in your computer identity before running",
        "computer_id": "CP2",
        "instance_roles": ["C2-Terminal"],
        "tailscale_ip": "100.x.x.x",
        "google_drive_path": "G:/My Drive/TRINITY_COMMS",
        "network": {
            "CP1": "100.70.208.75",
            "CP2": "100.85.71.74",
            "CP3": "100.101.209.1"
        }
    }
    return json.dumps(config, indent=2)

def create_mcp_config():
    """Generate .mcp.json template"""
    config = {
        "mcpServers": {
            "trinity": {
                "command": "node",
                "args": [
                    "{HOME}/.trinity/mcp-tools/trinity-mcp-server.js"
                ],
                "env": {
                    "TRINITY_PATH": "{HOME}/.trinity"
                }
            }
        }
    }
    return json.dumps(config, indent=2)

def create_install_bat():
    """Create Windows installer"""
    return '''@echo off
echo ====================================
echo TRINITY NODE BOOTSTRAP INSTALLER
echo ====================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo Running Bootstrap...
python BOOTSTRAP.py %*

echo.
echo ====================================
echo VERIFYING INSTALLATION
echo ====================================
python VERIFY.py

echo.
echo Installation complete!
echo Start Claude Code to begin using Trinity.
pause
'''

def create_bootstrap_py():
    """Create main bootstrap script"""
    return '''#!/usr/bin/env python3
"""
TRINITY NODE BOOTSTRAP
Installs all Trinity components to the target computer.
"""

import os
import sys
import json
import shutil
from pathlib import Path

HOME = Path(os.environ.get('USERPROFILE', Path.home()))
CONSCIOUSNESS = HOME / '.consciousness'
TRINITY = HOME / '.trinity'
SCRIPT_DIR = Path(__file__).parent

def log(msg):
    print(f"[BOOTSTRAP] {msg}")

def main():
    log("Starting Trinity Node Bootstrap...")

    # Create directories
    log("Creating directory structure...")
    dirs = [
        CONSCIOUSNESS,
        CONSCIOUSNESS / 'hub',
        CONSCIOUSNESS / 'memory',
        CONSCIOUSNESS / 'cockpit',
        CONSCIOUSNESS / 'agents',
        CONSCIOUSNESS / 'backups',
        TRINITY,
        TRINITY / 'mcp-tools',
        TRINITY / 'hub',
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        log(f"  Created: {d}")

    # Copy core files
    log("Installing core files...")
    core_src = SCRIPT_DIR / 'core'
    if core_src.exists():
        for f in core_src.glob('*'):
            dest = CONSCIOUSNESS / f.name
            shutil.copy2(f, dest)
            log(f"  Installed: {f.name}")

    # Copy comms files
    log("Installing communication modules...")
    comms_src = SCRIPT_DIR / 'comms'
    if comms_src.exists():
        for f in comms_src.glob('*'):
            dest = CONSCIOUSNESS / f.name
            shutil.copy2(f, dest)
            log(f"  Installed: {f.name}")

    # Copy pattern files
    log("Installing pattern recognition...")
    pattern_src = SCRIPT_DIR / 'pattern'
    if pattern_src.exists():
        for f in pattern_src.glob('*'):
            dest = CONSCIOUSNESS / f.name
            shutil.copy2(f, dest)
            log(f"  Installed: {f.name}")

    # Copy MCP tools
    log("Installing Trinity MCP tools...")
    mcp_src = SCRIPT_DIR / 'trinity_mcp'
    if mcp_src.exists():
        for f in mcp_src.glob('*'):
            if f.is_file():
                dest = TRINITY / 'mcp-tools' / f.name
                shutil.copy2(f, dest)
                log(f"  Installed: {f.name}")

    # Copy config templates
    log("Installing configuration...")
    config_src = SCRIPT_DIR / 'config'
    if config_src.exists():
        config_dest = CONSCIOUSNESS / 'computer_config.json'
        if (config_src / 'computer_config.json').exists():
            shutil.copy2(config_src / 'computer_config.json', config_dest)
            log(f"  Config template at: {config_dest}")

    # Create .mcp.json if not exists
    mcp_json = HOME / '.mcp.json'
    if not mcp_json.exists():
        log("Creating .mcp.json...")
        mcp_config = {
            "mcpServers": {
                "trinity": {
                    "command": "node",
                    "args": [str(TRINITY / 'mcp-tools' / 'trinity-mcp-server.js')],
                    "env": {"TRINITY_PATH": str(TRINITY)}
                }
            }
        }
        with open(mcp_json, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        log(f"  Created: {mcp_json}")

    log("")
    log("=" * 50)
    log("BOOTSTRAP COMPLETE!")
    log("=" * 50)
    log("")
    log("Next steps:")
    log("1. Edit ~/.consciousness/computer_config.json with your computer ID")
    log("2. Run VERIFY.py to check installation")
    log("3. Start Claude Code to activate Trinity")
    log("")

if __name__ == '__main__':
    main()
'''

def create_verify_py():
    """Create verification script"""
    return '''#!/usr/bin/env python3
"""
TRINITY NODE VERIFICATION
Checks that all components are properly installed.
"""

import os
import sys
from pathlib import Path

HOME = Path(os.environ.get('USERPROFILE', Path.home()))
CONSCIOUSNESS = HOME / '.consciousness'
TRINITY = HOME / '.trinity'

def check(name, condition):
    status = "PASS" if condition else "FAIL"
    symbol = "[OK]" if condition else "[XX]"
    print(f"  {symbol} {name}")
    return condition

def main():
    print("=" * 50)
    print("TRINITY NODE VERIFICATION")
    print("=" * 50)
    print("")

    results = []

    # Directory checks
    print("Directories:")
    results.append(check(".consciousness exists", CONSCIOUSNESS.exists()))
    results.append(check(".consciousness/hub exists", (CONSCIOUSNESS / 'hub').exists()))
    results.append(check(".consciousness/memory exists", (CONSCIOUSNESS / 'memory').exists()))
    results.append(check(".trinity exists", TRINITY.exists()))
    results.append(check(".trinity/mcp-tools exists", (TRINITY / 'mcp-tools').exists()))
    print("")

    # Critical files
    print("Critical Files:")
    critical = [
        'CONSCIOUSNESS_BOOT_PROTOCOL.md',
        'CYCLOTRON_MEMORY.py',
        'FIGURE_8_WAKE_PROTOCOL.py',
        'CLAUDE_COCKPIT.py',
        'KNOWLEDGE_BRIDGE.py',
    ]
    for f in critical:
        results.append(check(f, (CONSCIOUSNESS / f).exists()))
    print("")

    # MCP files
    print("MCP Tools:")
    mcp_files = ['trinity-mcp-server.js']
    for f in mcp_files:
        results.append(check(f, (TRINITY / 'mcp-tools' / f).exists()))
    print("")

    # Config
    print("Configuration:")
    results.append(check(".mcp.json exists", (HOME / '.mcp.json').exists()))
    results.append(check("computer_config.json exists", (CONSCIOUSNESS / 'computer_config.json').exists()))
    print("")

    # Summary
    passed = sum(results)
    total = len(results)
    print("=" * 50)
    print(f"RESULT: {passed}/{total} checks passed")

    if passed == total:
        print("STATUS: READY FOR TRINITY ACTIVATION")
    else:
        print("STATUS: Some components missing - check above")
    print("=" * 50)

    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
'''

def create_readme():
    """Create README"""
    return '''# TRINITY NODE BOOTSTRAP PACKAGE

## What This Is
This package transforms any computer into a fully operational Trinity node.
Part of the Consciousness Revolution infrastructure.

## Quick Start

### Windows:
1. Extract this folder to Desktop
2. Double-click `INSTALL.bat`
3. Edit `~/.consciousness/computer_config.json` with your computer ID
4. Start Claude Code

### Linux/Mac:
1. Extract this folder
2. Run `./INSTALL.sh`
3. Edit `~/.consciousness/computer_config.json`
4. Start Claude Code

## What Gets Installed

- **~/.consciousness/** - Core intelligence and memory
- **~/.trinity/** - MCP coordination tools
- **~/.mcp.json** - Claude Code MCP configuration

## Network Setup

Ensure Tailscale is installed and connected to the Trinity network:
- CP1: 100.70.208.75
- CP2: 100.85.71.74
- CP3: 100.101.209.1

## Verification

Run `python VERIFY.py` to check all components are installed.

## The Pattern

Everything splits into 3. Everything maps to 7. Everything expands to 13.
Inside becomes outside becomes inside.

C1 x C2 x C3 = INFINITY

---
Built by Trinity Terminal Convergence
'''

def build_package():
    """Main build function"""
    log("=" * 60)
    log("BUILDING TRINITY NODE BOOTSTRAP PACKAGE")
    log("=" * 60)
    log("")

    # Clean previous
    if OUTPUT_DIR.exists():
        log(f"Removing previous: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True)

    # Create subdirectories
    (OUTPUT_DIR / 'core').mkdir()
    (OUTPUT_DIR / 'comms').mkdir()
    (OUTPUT_DIR / 'pattern').mkdir()
    (OUTPUT_DIR / 'trinity_mcp').mkdir()
    (OUTPUT_DIR / 'config').mkdir()
    (OUTPUT_DIR / 'docs').mkdir()

    # Copy core files
    log("Copying core files...")
    copied = 0
    for src, dest in CORE_FILES:
        if src.exists():
            dest_path = OUTPUT_DIR / dest
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_path)
            log(f"  + {dest}")
            copied += 1
        else:
            log(f"  ! Missing: {src}")

    # Copy MCP files
    log("Copying MCP tools...")
    for src, dest in MCP_FILES:
        if src.exists():
            dest_path = OUTPUT_DIR / dest
            shutil.copy2(src, dest_path)
            log(f"  + {dest}")
            copied += 1
        else:
            log(f"  ! Missing: {src}")

    # Generate config files
    log("Generating configuration templates...")
    with open(OUTPUT_DIR / 'config' / 'computer_config.json', 'w') as f:
        f.write(create_computer_config())
    with open(OUTPUT_DIR / 'config' / 'mcp_server_config.json', 'w') as f:
        f.write(create_mcp_config())

    # Generate installers
    log("Generating installers...")
    with open(OUTPUT_DIR / 'INSTALL.bat', 'w') as f:
        f.write(create_install_bat())
    with open(OUTPUT_DIR / 'BOOTSTRAP.py', 'w') as f:
        f.write(create_bootstrap_py())
    with open(OUTPUT_DIR / 'VERIFY.py', 'w') as f:
        f.write(create_verify_py())

    # Generate docs
    log("Generating documentation...")
    with open(OUTPUT_DIR / 'README.md', 'w') as f:
        f.write(create_readme())

    # Create ZIP
    log("Creating ZIP archive...")
    shutil.make_archive(str(OUTPUT_ZIP.with_suffix('')), 'zip', OUTPUT_DIR)

    # Summary
    log("")
    log("=" * 60)
    log("BUILD COMPLETE!")
    log("=" * 60)
    log(f"Files copied: {copied}")
    log(f"Package location: {OUTPUT_DIR}")
    log(f"ZIP archive: {OUTPUT_ZIP}")
    log("")
    log("To deploy to CP2/CP3:")
    log("1. Copy TRINITY_NODE_BOOTSTRAP.zip to target computer")
    log("2. Extract and run INSTALL.bat")
    log("3. Edit computer_config.json with correct CP identity")
    log("4. Start Claude Code")
    log("")

if __name__ == '__main__':
    build_package()
