#!/usr/bin/env python3
"""
AUTO INDEX GENERATOR
Creates basic INDEX.md files for folders that are missing them
"""

import os
from pathlib import Path
from datetime import datetime

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"

# Descriptions for known folders
FOLDER_DESCRIPTIONS = {
    "agents": "AI agent configurations and spawned worker outputs",
    "backups": "System backup files and recovery points",
    "brain": "Core brain processing components",
    "cloud_outputs": "Outputs from cloud-spawned Trinity workers",
    "cockpit": "Claude Cockpit interface files",
    "computer_comms": "Cross-computer communication files",
    "computer_indexes": "Index files for multi-computer sync",
    "cyclotron_core": "Cyclotron knowledge system core with atoms database",
    "daily_reports": "Daily system status reports",
    "dimensions": "Seven Domains dimension mapping files",
    "exports": "Exported data and artifacts",
    "graphrag": "Graph-based retrieval augmented generation data",
    "health_logs": "System health monitoring logs",
    "hub": "Trinity coordination hub - messages, signals, work orders",
    "indices": "Search indices for fast retrieval",
    "input_queue": "Queued inputs waiting for processing",
    "memory": "Persistent memory storage",
    "monitoring": "System monitoring and metrics",
    "prompts": "Prompt templates and configurations",
    "r3_live": "R3 live processing outputs",
    "RESCUED_GEMS": "Recovered valuable content and documents",
    "tornado_reports": "Tornado protocol scan reports",
}

def generate_index(folder_path: Path) -> str:
    """Generate INDEX.md content for a folder"""
    folder_name = folder_path.name
    description = FOLDER_DESCRIPTIONS.get(folder_name, f"Contains {folder_name} related files")

    # Count files by type
    files = list(folder_path.glob("*"))
    py_files = [f for f in files if f.suffix == ".py"]
    md_files = [f for f in files if f.suffix == ".md"]
    json_files = [f for f in files if f.suffix == ".json"]
    other_files = [f for f in files if f.is_file() and f.suffix not in [".py", ".md", ".json"]]
    subdirs = [f for f in files if f.is_dir()]

    content = f"""# {folder_name.upper()}

{description}

## Contents

| Type | Count |
|------|-------|
| Python files | {len(py_files)} |
| Markdown files | {len(md_files)} |
| JSON files | {len(json_files)} |
| Other files | {len(other_files)} |
| Subdirectories | {len(subdirs)} |

## Key Files

"""

    # List important files (up to 10)
    important = py_files[:5] + md_files[:3] + json_files[:2]
    for f in important[:10]:
        content += f"- `{f.name}`\n"

    if subdirs:
        content += "\n## Subdirectories\n\n"
        for d in subdirs[:10]:
            content += f"- `{d.name}/`\n"

    content += f"""
---
*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Part of the Consciousness Revolution system*
"""
    return content

def create_indexes():
    """Create INDEX.md for all folders missing them"""
    created = 0
    skipped = 0

    for folder in CONSCIOUSNESS.iterdir():
        if not folder.is_dir():
            continue
        if folder.name.startswith('.') or folder.name == '__pycache__':
            continue

        index_path = folder / "INDEX.md"
        readme_path = folder / "README.md"

        if index_path.exists() or readme_path.exists():
            skipped += 1
            continue

        content = generate_index(folder)
        index_path.write_text(content, encoding='utf-8')
        print(f"Created: {folder.name}/INDEX.md")
        created += 1

    print(f"\nSummary: {created} created, {skipped} already had INDEX")
    return created

if __name__ == "__main__":
    create_indexes()
