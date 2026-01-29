
import json
from pathlib import Path
from datetime import datetime

# Import our newly refactored modules
from .blockchain import Blockchain
from .merkletree import build_merkle_tree

class CryptoRalphAgent:
    """
    The main autonomous agent for the Crypto-Ralph project.
    This class orchestrates the entire workflow, from reading the PRD
    to executing tasks and updating the blockchain.
    """
    def __init__(self, project_dir: str | Path):
        self.project_dir = Path(project_dir)
        self.prd_file = self.project_dir / "PRD.json"
        
        if not self.prd_file.exists():
            raise FileNotFoundError(f"PRD.json not found in {self.project_dir}")
            
        with open(self.prd_file, 'r', encoding='utf-8') as f:
            self.prd = json.load(f)
        
        self.blockchain = Blockchain(self.project_dir, self.prd.get('consensus_rules', {}))

    def get_next_task(self) -> dict | None:
        """Finds the next user story to execute based on priority and status."""
        user_stories = self.prd.get('userStories', [])
        pending_stories = [story for story in user_stories if not story.get('passes', False)]
        
        if not pending_stories:
            return None
            
        # Sort by priority to find the next task
        pending_stories.sort(key=lambda x: x.get('priority', float('inf')))
        return pending_stories[0]

    def run_main_loop(self):
        """Executes one full cycle of the Mandala Protocol."""
        print("--- Crypto-Ralph Agent: Starting Mandala Protocol Cycle ---")
        
        # 1. Center (State is inherent in the Blockchain object)
        print(f"Current State: Last block is {self.blockchain.chain[-1].get('index')}")

        # 2. Recurse (Find next task)
        next_task = self.get_next_task()
        if not next_task:
            print("All user stories are complete. Loop paused.")
            return

        print(f"Next Task: {next_task['id']} - {next_task['title']}")

        # 3. & 4. Expand & Act (Execute the task)
        # This is where the specific logic for each user story will go.
        # For now, we will just simulate the completion of US-003.
        print(f"Executing logic for {next_task['id']}...")
        
        # In a real run, we would call specific functions based on the task ID.
        # For US-003, the "work" is the refactoring we just did.
        completion_data = {
            "task": next_task['title'],
            "description": "Refactored procedural scripts into a modular Python package.",
            "modules_created": [
                "src/crypto_ralph/blockchain.py",
                "src/crypto_ralph/merkletree.py",
                "src/crypto_ralph/agent.py"
            ]
        }
        
        # 5. Record (Mine the proof and update ledger)
        proof = self.blockchain.mine_proof(next_task['id'], completion_data)
        self.blockchain.add_block(next_task['id'], proof, completion_data)

        print("\\n--- Cycle Complete ---")

if __name__ == '__main__':
    # This allows us to run the agent directly for testing
    agent = CryptoRalphAgent(project_dir="E:/dev-tools/projects/business-plan/")
    agent.run_main_loop()
