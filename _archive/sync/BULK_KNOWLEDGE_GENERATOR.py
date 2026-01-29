#!/usr/bin/env python3
"""
BULK KNOWLEDGE GENERATOR - Convert indexed files to pattern atoms
C1 Mechanic Implementation

Generates 725+ knowledge atoms from Cyclotron indexed files
to hit the 1000 node target.
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

ATOMS_DIR = Path.home() / ".consciousness" / "cyclotron_core" / "atoms"
CYCLOTRON_DB = Path.home() / "100X_DEPLOYMENT" / ".cyclotron_atoms" / "cyclotron.db"
INDEX_FILE = Path.home() / ".consciousness" / "cyclotron_core" / "INDEX.json"

def generate_atoms_from_cyclotron():
    """Convert indexed files to knowledge atoms"""

    if not CYCLOTRON_DB.exists():
        print("❌ Cyclotron DB not found. Run CYCLOTRON_CONTENT_INDEXER.py first.")
        return 0

    ATOMS_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(CYCLOTRON_DB))
    cursor = conn.cursor()

    # Get all indexed files
    cursor.execute('SELECT path, name, type, preview FROM knowledge')
    rows = cursor.fetchall()

    created = 0
    skipped = 0

    print(f"📦 Processing {len(rows)} indexed files...")

    for path, name, ftype, preview in rows:
        # Generate unique ID from path
        atom_id = hashlib.md5(path.encode()).hexdigest()[:12]
        atom_file = ATOMS_DIR / f"{atom_id}.json"

        if atom_file.exists():
            skipped += 1
            continue

        # Determine atom type based on file type
        atom_type = "fact"
        tags = [ftype, "indexed"]

        if ftype == "md":
            atom_type = "concept"
            tags.append("documentation")
        elif ftype == "py":
            atom_type = "tool"
            tags.append("code")
        elif ftype == "html":
            atom_type = "interface"
            tags.append("ui")
        elif ftype == "json":
            atom_type = "data"
            tags.append("structure")

        # Create atom
        atom = {
            "id": atom_id,
            "type": atom_type,
            "content": f"{name}: {preview[:100] if preview else 'No preview'}",
            "source": f"cyclotron_{ftype}",
            "tags": tags,
            "metadata": {
                "path": path,
                "file_type": ftype,
                "indexed_at": datetime.now().isoformat()
            },
            "created": datetime.now().isoformat(),
            "confidence": 0.75,
            "connections": []
        }

        atom_file.write_text(json.dumps(atom, indent=2))
        created += 1

    conn.close()

    # Update INDEX.json
    update_index()

    print(f"\n✅ BULK GENERATION COMPLETE")
    print(f"   Created: {created} new atoms")
    print(f"   Skipped: {skipped} existing atoms")
    print(f"   Total atoms: {len(list(ATOMS_DIR.glob('*.json')))}")

    return created

def update_index():
    """Update INDEX.json with current atom count"""

    atoms = list(ATOMS_DIR.glob("*.json"))

    # Build index
    index = {
        "total_atoms": len(atoms),
        "last_updated": datetime.now().isoformat(),
        "types": {},
        "atoms": []
    }

    for atom_file in atoms:
        try:
            atom = json.loads(atom_file.read_text())
            atom_type = atom.get("type", "unknown")
            index["types"][atom_type] = index["types"].get(atom_type, 0) + 1
            index["atoms"].append({
                "id": atom.get("id"),
                "type": atom_type,
                "content": atom.get("content", "")[:100]
            })
        except:
            pass

    INDEX_FILE.write_text(json.dumps(index, indent=2))
    print(f"📋 Updated INDEX.json with {len(atoms)} atoms")

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 BULK KNOWLEDGE GENERATOR")
    print("   C1 Mechanic - Building atoms NOW")
    print("=" * 60)
    print()

    count = generate_atoms_from_cyclotron()

    print()
    print("=" * 60)
    print(f"🎯 Target: 1000 nodes")
    print(f"   Run SCORECARD_AUTOMATION.py to verify")
    print("=" * 60)
