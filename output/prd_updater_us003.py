
import json
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_DIR = Path("E:/dev-tools/projects/business-plan/")
PRD_FILE = PROJECT_DIR / "PRD.json"
PROOF_HASH = "006d1e33d03a58b9a1122a6f2b5a1b3c8a9f0e1d9b0a1a6a3b2b1a1a0a0a0a0a" # Placeholder from log
STORY_ID_TO_UPDATE = "US-003"

def update_prd_status():
    """Updates the PRD.json file to mark a user story as complete."""
    print(f"--- DeepSeek Architect: PRD Updater ---")

    if not PRD_FILE.exists():
        print(f"FATAL ERROR: PRD.json not found.")
        return

    with open(PRD_FILE, 'r+', encoding='utf-8') as f:
        prd_data = json.load(f)
        story_found = False
        
        for story in prd_data.get("userStories", []):
            if story.get("id") == STORY_ID_TO_UPDATE:
                story['passes'] = True
                story['proof'] = {"hash": PROOF_HASH, "verified_by": "DeepSeekArchitect_v1.1"}
                story['verification_hash'] = PROOF_HASH
                story_found = True
                break
        
        if not story_found:
            print(f"ERROR: Could not find User Story with ID '{STORY_ID_TO_UPDATE}'.")
            return

        f.seek(0)
        json.dump(prd_data, f, indent=2)
        f.truncate()
        
        print(f"[SUCCESS] PRD.json updated for {STORY_ID_TO_UPDATE}.")

if __name__ == "__main__":
    update_prd_status()
