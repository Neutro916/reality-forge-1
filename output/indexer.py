
import os
import hashlib
import json
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
# The directory containing the business plan markdown files.
SCAN_DIRECTORY = Path("D:/Breathing_App_Essentials/business_plan/businessesplan/")
# The official destination for the output file.
OUTPUT_FILE = Path("E:/dev-tools/projects/business-plan/output/document_index.json")

def hash_file(filepath: Path) -> str:
    """Calculates the SHA-256 hash of a file's content."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            # Read in 4K chunks
            chunk = f.read(4096)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def create_document_index():
    """
    Scans the SCAN_DIRECTORY, hashes each markdown file, and saves the
    results to a JSON file in the OUTPUT_FILE location.
    This script is the first implementation step of User Story US-001.
    """
    print(f"--- Crypto-Ralph: US-001 Indexer ---")
    print(f"Scanning directory: {SCAN_DIRECTORY}")

    if not SCAN_DIRECTORY.is_dir():
        print(f"FATAL ERROR: Scan directory not found at the specified location.")
        return

    documents = []
    total_files = 0

    for file_path in SCAN_DIRECTORY.glob("*.md"):
        if file_path.is_file():
            total_files += 1
            print(f"  -> Indexing: {file_path.name}")
            try:
                file_hash = hash_file(file_path)
                stat = file_path.stat()
                document = {
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_bytes': stat.st_size,
                    'modified_utc': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'sha256_hash': file_hash
                }
                documents.append(document)
            except Exception as e:
                print(f"    ERROR: Could not process file {file_path.name}: {e}")

    # Sort documents alphabetically by filename for consistency
    documents.sort(key=lambda x: x['filename'])

    index_data = {
        'metadata': {
            'index_creation_utc': datetime.utcnow().isoformat(),
            'scan_directory': str(SCAN_DIRECTORY),
            'total_documents_indexed': len(documents),
            'version': "1.0.0",
            'description': "Cryptographically verified index of all business plan documents."
        },
        'documents': documents
    }

    print(f"\nScan complete. Indexed {len(documents)} out of {total_files} files.")
    
    # Ensure the output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)

    print(f"\n[SUCCESS] Cryptographic index saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_document_index()
