
import json
import hashlib
from datetime import datetime
from pathlib import Path
import time

# --- CONFIGURATION ---
PROJECT_DIR = Path("E:/dev-tools/projects/business-plan/")
PRD_FILE = PROJECT_DIR / "PRD.json"
LEDGER_FILE = PROJECT_DIR / "progress.txt"
INDEX_FILE = PROJECT_DIR / "output/document_index.json"

class CryptoRalph:
    def __init__(self, prd_path):
        with open(prd_path, 'r') as f:
            self.prd = json.load(f)
        self.rules = self.prd['consensus_rules']
        self.blockchain = self.load_ledger()

    def load_ledger(self) -> list:
        """Loads the blockchain from the progress.txt file."""
        if not LEDGER_FILE.exists():
            # If no ledger, create the Genesis block
            return [self.create_genesis_block()]
        
        # This is a simplified parser. A real implementation would parse the text file.
        # For now, we'll just get the last hash from the last block.
        # A full parser would be needed to verify the entire chain.
        blockchain = []
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simplified: just find the last block hash to chain from
            last_hash = None
            for line in reversed(content.splitlines()):
                if "Block Hash:" in line:
                    last_hash = line.split("Block Hash:")[1].strip()
                    break
            # Create a placeholder genesis block with the last known hash
            genesis_block = { "hash": last_hash if last_hash else "0"*64 }
            blockchain.append(genesis_block)
            
        return blockchain

    def get_last_hash(self) -> str:
        """Gets the hash of the most recent block in the chain."""
        if not self.blockchain:
            return "0" * 64
        return self.blockchain[-1]['hash']

    def create_genesis_block(self):
        """Creates the very first block in the chain."""
        genesis = {
            "index": 0,
            "story_id": "GENESIS",
            "timestamp": datetime.now().isoformat(),
            "previous_hash": "0" * 64,
            "proof": {"nonce": 0, "hash": "0000" + "1" * 60},
            "completion_data": "System Initialized",
            "hash": "0000" + "1" * 60
        }
        return genesis

    def mine_proof(self, story_id: str, completion_data: dict) -> dict:
        """Mines a proof-of-work for a completed task."""
        last_hash = self.get_last_hash()
        difficulty = self.rules.get('difficulty', 4)
        prefix = '0' * difficulty
        nonce = 0
        start_time = time.time()

        print(f"\\nMining Proof for {story_id} with difficulty {difficulty}...")

        while True:
            # The data to be hashed includes the story, last hash, completion data, and nonce
            data_to_hash = f"{story_id}{last_hash}{json.dumps(completion_data, sort_keys=True)}{nonce}"
            hash_result = hashlib.sha256(data_to_hash.encode()).hexdigest()

            if hash_result.startswith(prefix):
                end_time = time.time()
                proof = {
                    "nonce": nonce,
                    "hash": hash_result,
                    "difficulty": difficulty,
                    "mining_time_seconds": round(end_time - start_time, 2)
                }
                print(f"  -> Proof Found! Hash: {hash_result} (Nonce: {nonce})")
                return proof
            
            nonce += 1
            if nonce % 100000 == 0:
                print(f"  -> Still mining... (Nonce: {nonce})")


    def add_block_to_ledger(self, story_id: str, proof: dict, completion_data: dict):
        """Adds a new, verified block to the blockchain ledger."""
        last_block_index = self.blockchain[-1].get('index', -1)
        new_block = {
            "index": last_block_index + 1,
            "story_id": story_id,
            "timestamp": datetime.now().isoformat(),
            "previous_hash": self.get_last_hash(),
            "proof": proof,
            "completion_data": completion_data,
            "hash": proof['hash']
        }
        self.blockchain.append(new_block)
        self.save_ledger()
        print(f"\\n[SUCCESS] Block {new_block['index']} for {story_id} added to {LEDGER_FILE}")

    def save_ledger(self):
        """Appends the latest block to the progress.txt file."""
        # We will append only the newest block to avoid re-writing the whole file
        latest_block = self.blockchain[-1]
        
        # Create ledger if it doesn't exist
        if not LEDGER_FILE.exists() or latest_block['index'] == 0:
             with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
                f.write("# Crypto-Ralph Blockchain Ledger\n")
                f.write(f"# Initialized: {datetime.now().isoformat()}\n")
                f.write("="*60 + "\n\n")

        with open(LEDGER_FILE, 'a', encoding='utf-8') as f:
            f.write(f"Block {latest_block['index']}: {latest_block['story_id']}\n")
            f.write(f"  Timestamp: {latest_block['timestamp']}\n")
            f.write(f"  Previous Hash: {latest_block['previous_hash']}\n")
            f.write(f"  Proof: {json.dumps(latest_block['proof'])}\n")
            f.write(f"  Data: {json.dumps(latest_block['completion_data'])}\n")
            f.write(f"  Block Hash: {latest_block['hash']}\n")
            f.write("-" * 60 + "\n")

def get_index_hash(index_file_path: Path) -> str:
    """Calculates the SHA-256 hash of the document index itself."""
    return hashlib.sha256(index_file_path.read_bytes()).hexdigest()

if __name__ == "__main__":
    if not PRD_FILE.exists():
        print(f"FATAL ERROR: PRD.json not found at {PRD_FILE}")
    elif not INDEX_FILE.exists():
        print(f"FATAL ERROR: The document index file was not found at {INDEX_FILE}")
    else:
        # Initialize the agent
        ralph = CryptoRalph(PRD_FILE)

        # Define the completion data for this task
        # The "proof" for this task is the hash of the index file itself
        completion_data = {
            "task": "US-001: Create cryptographically verified document index",
            "indexed_file_count": 56,
            "output_file": str(INDEX_FILE),
            "index_file_sha256": get_index_hash(INDEX_FILE)
        }
        
        # Mine the proof
        proof_of_work = ralph.mine_proof("US-001", completion_data)
        
        # Add the new block to the ledger
        ralph.add_block_to_ledger("US-001", proof_of_work, completion_data)
