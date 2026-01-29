
import json
import hashlib
from datetime import datetime
from pathlib import Path
import time

# --- CONFIGURATION ---
PROJECT_DIR = Path("E:/dev-tools/projects/business-plan/")
PRD_FILE = PROJECT_DIR / "PRD.json"
LEDGER_FILE = PROJECT_DIR / "progress.txt"
MERKLE_TREE_FILE = PROJECT_DIR / "output/merkle_tree.json"

class CryptoRalph:
    def __init__(self, prd_path):
        with open(prd_path, 'r') as f:
            self.prd = json.load(f)
        self.rules = self.prd['consensus_rules']
        self.blockchain = self.load_ledger()

    def load_ledger(self) -> list:
        blockchain = []
        if not LEDGER_FILE.exists():
            return blockchain

        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simplified parser to get the last block's hash and index
            last_hash = "0" * 64
            last_index = -1
            for line in reversed(content.splitlines()):
                if "Block Hash:" in line and not last_hash:
                    last_hash = line.split("Block Hash:")[1].strip()
                if "Block " in line and line.startswith("Block "):
                    try:
                        last_index = int(line.split(":")[0].replace("Block ", ""))
                        # Found the last block, create a placeholder
                        placeholder_block = {"hash": last_hash, "index": last_index}
                        blockchain.insert(0, placeholder_block) # Insert at beginning
                        break
                    except ValueError:
                        continue
        return blockchain

    def get_last_hash(self) -> str:
        if not self.blockchain:
            return "0" * 64
        # Since we only load a placeholder for the last block, this is correct
        return self.blockchain[0].get('hash', "0" * 64)

    def mine_proof(self, story_id: str, completion_data: dict) -> dict:
        last_hash = self.get_last_hash()
        difficulty = self.rules.get('difficulty', 2)
        prefix = '0' * difficulty
        nonce = 0
        start_time = time.time()

        print(f"\\nMining Proof for {story_id} with difficulty {difficulty}...")
        
        while True:
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
                print(f"  -> Proof Found! Hash: {hash_result} (Nonce: {nonce}) in {proof['mining_time_seconds']}s")
                return proof
            
            nonce += 1
            if nonce % 250000 == 0:
                print(f"  -> Still mining... (Nonce: {nonce})")

    def add_block_to_ledger(self, story_id: str, proof: dict, completion_data: dict):
        last_block_index = self.blockchain[0].get('index', -1) if self.blockchain else -1
        new_block = {
            "index": last_block_index + 1,
            "story_id": story_id,
            "timestamp": datetime.now().isoformat(),
            "previous_hash": self.get_last_hash(),
            "proof": proof,
            "completion_data": completion_data,
            "hash": proof['hash']
        }
        # We don't need to keep the full chain in memory for this operation
        self.blockchain = [new_block] # Only store the latest block
        self.save_ledger_append(new_block)
        print(f"\\n[SUCCESS] Block {new_block['index']} for {story_id} added to {LEDGER_FILE}")

    def save_ledger_append(self, block_to_append: dict):
        with open(LEDGER_FILE, 'a', encoding='utf-8') as f:
            f.write(f"Block {block_to_append['index']}: {block_to_append['story_id']}\\n")
            f.write(f"  Timestamp: {block_to_append['timestamp']}\\n")
            f.write(f"  Previous Hash: {block_to_append['previous_hash']}\\n")
            f.write(f"  Proof: {json.dumps(block_to_append['proof'])}\\n")
            f.write(f"  Data: {json.dumps(block_to_append['completion_data'])}\\n")
            f.write(f"  Block Hash: {block_to_append['hash']}\\n")
            f.write("-" * 60 + "\\n")

if __name__ == "__main__":
    if not PRD_FILE.exists():
        print(f"FATAL ERROR: PRD.json not found at {PRD_FILE}")
    elif not MERKLE_TREE_FILE.exists():
        print(f"FATAL ERROR: The merkle_tree.json file was not found at {MERKLE_TREE_FILE}")
    else:
        ralph = CryptoRalph(PRD_FILE)
        
        with open(MERKLE_TREE_FILE, 'r', encoding='utf-8') as f:
            merkle_data = json.load(f)
        
        merkle_root = merkle_data.get('merkle_root')

        completion_data = {
            "task": "US-002: Generate Merkle Tree for Document Integrity",
            "merkle_root_hash": merkle_root,
            "source_file": str(MERKLE_TREE_FILE)
        }
        
        proof_of_work = ralph.mine_proof("US-002", completion_data)
        
        ralph.add_block_to_ledger("US-002", proof_of_work, completion_data)

