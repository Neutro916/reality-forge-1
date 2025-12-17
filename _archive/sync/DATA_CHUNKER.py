#!/usr/bin/env python3
"""
DATA CHUNKER
Breaks down large content (books, docs, code) into bite-sized knowledge fragments.

The goal: Take a 500-page book and extract ~50 perfect knowledge atoms.
Each atom is:
- Self-contained (makes sense alone)
- Indexed (searchable)
- Connected (links to related atoms)
- Compressed (1/6th the size, 100% the meaning)

Uses local LLM for comprehension when available.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Configuration
MEMORY_DIR = Path.home() / ".consciousness" / "memory"
ATOMS_DIR = MEMORY_DIR / "atoms"
DB_PATH = MEMORY_DIR / "knowledge_atoms.db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"  # Good for summarization

# Chunk settings
MAX_CHUNK_SIZE = 2000  # Characters per initial chunk
TARGET_ATOM_SIZE = 500  # Target size for final atom
OVERLAP = 200  # Overlap between chunks for context

def ensure_dirs():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    ATOMS_DIR.mkdir(parents=True, exist_ok=True)

def init_db():
    """Initialize the knowledge atoms database"""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atoms (
            id TEXT PRIMARY KEY,
            source_file TEXT,
            source_type TEXT,
            chunk_index INTEGER,
            original_text TEXT,
            compressed_text TEXT,
            keywords TEXT,
            connections TEXT,
            importance REAL DEFAULT 0.5,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            filename TEXT,
            filetype TEXT,
            total_size INTEGER,
            total_atoms INTEGER,
            compression_ratio REAL,
            processed_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

def generate_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]

def split_into_chunks(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries"""
    # Split by sentences (rough)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            words = current_chunk.split()
            overlap_text = " ".join(words[-30:]) if len(words) > 30 else ""
            current_chunk = overlap_text + " " + sentence + " "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def ask_llm(prompt: str) -> Optional[str]:
    """Ask local LLM for compression/analysis"""
    if not HAS_REQUESTS:
        return None

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except:
        pass
    return None

def compress_chunk(chunk: str) -> Dict:
    """
    Compress a chunk into a knowledge atom.
    Uses LLM if available, falls back to extraction.
    """
    # Try LLM compression
    llm_prompt = f"""Compress this text into its essential knowledge.
Keep only the most important facts, concepts, and insights.
Target: 1/4 the original length.
Output format: Just the compressed text, nothing else.

Text to compress:
{chunk}

Compressed version:"""

    compressed = ask_llm(llm_prompt)

    if not compressed:
        # Fallback: Simple extraction (first and last sentences + key phrases)
        sentences = re.split(r'(?<=[.!?])\s+', chunk)
        if len(sentences) > 4:
            compressed = sentences[0] + " " + sentences[-1]
        else:
            compressed = chunk[:TARGET_ATOM_SIZE]

    # Extract keywords
    keyword_prompt = f"""Extract 5-10 key terms/concepts from this text.
Output as comma-separated list only.

Text: {chunk}

Keywords:"""

    keywords_str = ask_llm(keyword_prompt)
    if keywords_str:
        keywords = [k.strip() for k in keywords_str.split(",")]
    else:
        # Fallback: Extract capitalized words and common nouns
        words = re.findall(r'\b[A-Z][a-z]+\b', chunk)
        keywords = list(set(words))[:10]

    return {
        "compressed": compressed,
        "keywords": keywords,
        "compression_ratio": len(compressed) / len(chunk) if chunk else 1
    }

def process_file(filepath: str) -> Dict:
    """Process a file into knowledge atoms"""
    init_db()

    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}

    print(f"[CHUNKER] Processing: {path.name}")

    # Read file
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Cannot read file: {e}"}

    original_size = len(content)
    print(f"[CHUNKER] Original size: {original_size:,} characters")

    # Split into chunks
    chunks = split_into_chunks(content)
    print(f"[CHUNKER] Split into {len(chunks)} chunks")

    # Process each chunk into an atom
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    source_id = generate_id(filepath + str(datetime.now()))
    atoms_created = 0
    total_compressed_size = 0

    for i, chunk in enumerate(chunks):
        print(f"[CHUNKER] Processing chunk {i+1}/{len(chunks)}...")

        # Compress
        result = compress_chunk(chunk)

        # Create atom
        atom_id = generate_id(chunk)
        compressed = result["compressed"]
        keywords = result["keywords"]

        total_compressed_size += len(compressed)

        # Store atom
        cursor.execute('''
            INSERT OR REPLACE INTO atoms
            (id, source_file, source_type, chunk_index, original_text,
             compressed_text, keywords, connections, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            atom_id,
            str(path),
            path.suffix,
            i,
            chunk,
            compressed,
            json.dumps(keywords),
            json.dumps([]),  # Connections filled later
            datetime.now().isoformat()
        ))

        # Also save as JSON file for easy access
        atom_file = ATOMS_DIR / f"{atom_id}.json"
        atom_data = {
            "id": atom_id,
            "source": str(path),
            "index": i,
            "original_length": len(chunk),
            "compressed": compressed,
            "keywords": keywords
        }
        with open(atom_file, 'w') as f:
            json.dump(atom_data, f, indent=2)

        atoms_created += 1

    # Record source
    compression_ratio = total_compressed_size / original_size if original_size > 0 else 1
    cursor.execute('''
        INSERT OR REPLACE INTO sources
        (id, filename, filetype, total_size, total_atoms, compression_ratio, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        source_id,
        path.name,
        path.suffix,
        original_size,
        atoms_created,
        compression_ratio,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    result = {
        "source": str(path),
        "original_size": original_size,
        "compressed_size": total_compressed_size,
        "compression_ratio": f"{compression_ratio:.1%}",
        "atoms_created": atoms_created,
        "atoms_dir": str(ATOMS_DIR)
    }

    print(f"[CHUNKER] Complete!")
    print(f"[CHUNKER] Compression: {original_size:,} → {total_compressed_size:,} ({compression_ratio:.1%})")
    print(f"[CHUNKER] Atoms created: {atoms_created}")

    return result

def search_atoms(query: str, limit: int = 5) -> List[Dict]:
    """Search knowledge atoms by keywords"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Simple keyword search
    keywords = query.lower().split()
    conditions = []
    params = []

    for kw in keywords:
        conditions.append("LOWER(keywords) LIKE ?")
        params.append(f"%{kw}%")

    if conditions:
        query_sql = f'''
            SELECT * FROM atoms
            WHERE {" OR ".join(conditions)}
            ORDER BY importance DESC
            LIMIT ?
        '''
        params.append(limit)
        cursor.execute(query_sql, params)
    else:
        cursor.execute("SELECT * FROM atoms ORDER BY importance DESC LIMIT ?", (limit,))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results

def get_stats() -> Dict:
    """Get chunker statistics"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) FROM atoms")
    stats["total_atoms"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources")
    stats["sources_processed"] = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_size), SUM(total_size * compression_ratio) FROM sources")
    row = cursor.fetchone()
    stats["total_original"] = row[0] or 0
    stats["total_compressed"] = int(row[1] or 0)

    if stats["total_original"] > 0:
        stats["overall_compression"] = f"{stats['total_compressed'] / stats['total_original']:.1%}"
    else:
        stats["overall_compression"] = "N/A"

    conn.close()
    return stats


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python DATA_CHUNKER.py <file>     - Process a file")
        print("  python DATA_CHUNKER.py search <query>  - Search atoms")
        print("  python DATA_CHUNKER.py stats      - Show statistics")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        stats = get_stats()
        print("\n=== Knowledge Atoms Statistics ===")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif command == "search":
        query = " ".join(sys.argv[2:])
        results = search_atoms(query)
        print(f"\n=== Search Results for '{query}' ===")
        for atom in results:
            print(f"\n[{atom['id']}] from {atom['source_file']}")
            print(f"  Keywords: {atom['keywords']}")
            print(f"  Content: {atom['compressed_text'][:200]}...")

    else:
        # Assume it's a file path
        filepath = command
        result = process_file(filepath)
        print("\n=== Processing Result ===")
        for key, value in result.items():
            print(f"  {key}: {value}")
