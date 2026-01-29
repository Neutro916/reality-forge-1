
import json
import hashlib
from pathlib import Path
import time
from datetime import datetime

# --- CONFIGURATION ---
PROJECT_DIR = Path("E:/dev-tools/projects/business-plan/")
INDEX_FILE = PROJECT_DIR / "output/document_index.json"
OUTPUT_FILE = PROJECT_DIR / "output/merkle_tree.json"

def hash_pair(hash1: str, hash2: str) -> str:
    """Hashes a concatenated pair of two SHA-256 hashes."""
    # Ensure consistent order for hashing
    if hash1 > hash2:
        hash1, hash2 = hash2, hash1
    combined = hash1 + hash2
    return hashlib.sha256(combined.encode()).hexdigest()

def build_merkle_tree(hash_list: list) -> (str, dict):
    """
    Constructs a Merkle Tree from a list of hashes and returns the root hash
    and the full tree structure.
    """
    if not hash_list:
        return None, {}

    print("Building Merkle Tree...")
    
    # The initial layer of leaves
    tree = {'leaves': hash_list}
    nodes = list(hash_list)
    level = 0

    while len(nodes) > 1:
        # If there's an odd number of nodes, duplicate the last one
        if len(nodes) % 2 != 0:
            nodes.append(nodes[-1])
        
        next_level_nodes = []
        for i in range(0, len(nodes), 2):
            new_hash = hash_pair(nodes[i], nodes[i+1])
            next_level_nodes.append(new_hash)
            print(f"  -> L{level}: Hashing pair to create {new_hash[:10]}...")
        
        nodes = next_level_nodes
        tree[f'level_{level+1}'] = nodes
        level += 1
    
    merkle_root = nodes[0]
    tree['root'] = merkle_root
    print(f"  -> Merkle Root Found: {merkle_root}")
    return merkle_root, tree

def run_merkle_generator():
    """
    Main function to read the document index, generate the Merkle Tree,
    and save the results. Implements the core logic for US-002.
    """
    print(f"--- Crypto-Ralph: US-002 Merkle Tree Generator ---")

    if not INDEX_FILE.exists():
        print(f"FATAL ERROR: Document index file not found at {INDEX_FILE}")
        return

    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        document_hashes = [doc['sha256_hash'] for doc in index_data.get('documents', [])]
        
        if not document_hashes:
            print("ERROR: No document hashes found in the index file.")
            return

        print(f"Found {len(document_hashes)} document hashes to process.")

        start_time = time.time()
        merkle_root, full_tree = build_merkle_tree(document_hashes)
        end_time = time.time()

        result = {
            'metadata': {
                'generation_utc': datetime.utcnow().isoformat(),
                'source_index_file': str(INDEX_FILE),
                'total_leaves': len(document_hashes),
                'tree_height': len(full_tree) - 2, # leaves, root, and levels
                'generation_time_seconds': round(end_time - start_time, 4)
            },
            'merkle_root': merkle_root,
            'tree': full_tree
        }
        
        # Save the full tree and root hash to our output file
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        
        print(f"\\n[SUCCESS] Merkle Tree generated. Root hash and full tree saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_merkle_generator()
