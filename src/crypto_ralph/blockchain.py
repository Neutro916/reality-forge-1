
import json
import hashlib
from datetime import datetime
from pathlib import Path
import time

class Blockchain:
    """
    Manages the cryptographic ledger for the Crypto-Ralph project.
    This class handles loading the ledger, mining proofs, and adding new blocks.
    """
    def __init__(self, project_dir: Path, consensus_rules: dict):
        self.project_dir = project_dir
        self.ledger_file = self.project_dir / "progress.txt"
        self.rules = consensus_rules
        self.chain = self._load_ledger()

    def _load_ledger(self) -> list:
        """Loads the blockchain from the progress.txt file."""
        if not self.ledger_file.exists():
            # If no ledger, create and return the Genesis block
            genesis_block = self._create_genesis_block()
            self._save_ledger_append(genesis_block, is_genesis=True)
            return [genesis_block]
        
        # This is a simplified parser for now, focusing on getting the last state
        chain = []
        with open(self.ledger_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find the last block's hash and index
            last_hash = "0" * 64
            last_index = -1
            for line in reversed(content.splitlines()):
                if "Block Hash:" in line:
                    last_hash = line.split("Block Hash:", 1)[1].strip()
                if line.startswith("Block "):
                    try:
                        last_index = int(line.split(":", 1)[0].replace("Block ", ""))
                        placeholder_block = {"hash": last_hash, "index": last_index}
                        chain.append(placeholder_block)
                        break
                    except (ValueError, IndexError):
                        continue
        return chain if chain else [self._create_genesis_block()]

    def get_last_hash(self) -> str:
        """Gets the hash of the most recent block in the chain."""
        if not self.chain:
            return "0" * 64
        return self.chain[-1].get('hash', "0" * 64)

    def _create_genesis_block(self) -> dict:
        """Creates the very first block in the chain."""
        return {
            "index": 0,
            "story_id": "GENESIS",
            "timestamp": datetime.now().isoformat(),
            "previous_hash": "0" * 64,
            "proof": {"nonce": 0, "hash": "0000" + "1" * 60},
            "completion_data": "System Initialized",
            "hash": "0000" + "1" * 60
        }

    def mine_proof(self, story_id: str, completion_data: dict) -> dict:
        """Mines a proof-of-work for a completed task."""
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
                print(f"  -> Proof Found! Hash: {hash_result[:12]}... (Nonce: {nonce}) in {proof['mining_time_seconds']}s")
                return proof
            
            nonce += 1
            if nonce % 250000 == 0:
                print(f"  -> Still mining... (Nonce: {nonce})")

    def add_block(self, story_id: str, proof: dict, completion_data: dict):
        """Adds a new, verified block to the blockchain."""
        last_block = self.chain[-1]
        new_block = {
            "index": last_block.get('index', -1) + 1,
            "story_id": story_id,
            "timestamp": datetime.now().isoformat(),
            "previous_hash": self.get_last_hash(),
            "proof": proof,
            "completion_data": completion_data,
            "hash": proof['hash']
        }
        self.chain.append(new_block)
        self._save_ledger_append(new_block)
        print(f"\\n[SUCCESS] Block {new_block['index']} for {story_id} added to {self.ledger_file}")

    def _save_ledger_append(self, block: dict, is_genesis: bool = False):
        """Appends a block to the progress.txt file."""
        mode = 'w' if is_genesis else 'a'
        with open(self.ledger_file, mode, encoding='utf-8') as f:
            if is_genesis:
                f.write("# Crypto-Ralph Blockchain Ledger\\n")
                f.write(f"# Initialized: {datetime.now().isoformat()}\\n")
                f.write("="*60 + "\\n\\n")

            f.write(f"Block {block['index']}: {block['story_id']}\\n")
            f.write(f"  Timestamp: {block['timestamp']}\\n")
            f.write(f"  Previous Hash: {block['previous_hash']}\\n")
            f.write(f"  Proof: {json.dumps(block['proof'])}\\n")
            f.write(f"  Data: {json.dumps(block['completion_data'])}\\n")
            f.write(f"  Block Hash: {block['hash']}\\n")
            f.write("-" * 60 + "\\n")
