
import json
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_DIR = Path("E:/dev-tools/projects/business-plan/")
PRD_FILE = PROJECT_DIR / "PRD.json"
PROOF_HASH = "00eb6869e69eb0fde853d61e1cbc75dba0dba8da7d2549755c154276ca8394d7"
STORY_ID_TO_UPDATE = "US-001"

def update_prd_status():
    """
    Updates the PRD.json file to mark a user story as complete and records the proof hash.
    This is the final step in the Crypto-Ralph loop for a given task.
    """
    print(f"--- Crypto-Ralph: PRD Updater ---")

    if not PRD_FILE.exists():
        print(f"FATAL ERROR: PRD.json not found at {PRD_FILE}")
        return

    with open(PRD_FILE, 'r+', encoding='utf-8') as f:
        try:
            prd_data = json.load(f)
            story_found = False
            
            for story in prd_data.get("userStories", []):
                if story.get("id") == STORY_ID_TO_UPDATE:
                    story['passes'] = True
                    story['proof'] = {
                        "hash": PROOF_HASH,
                        "verified_by": "CryptoRalph_v1.0"
                    }
                    story['verification_hash'] = PROOF_HASH # Legacy or simplified field
                    story_found = True
                    print(f"  -> Found User Story '{STORY_ID_TO_UPDATE}'. Updating status to 'passes: true'.")
                    break
            
            if not story_found:
                print(f"ERROR: Could not find User Story with ID '{STORY_ID_TO_UPDATE}' in the PRD.")
                return

            # Go back to the beginning of the file to overwrite it
            f.seek(0)
            json.dump(prd_data, f, indent=2)
            f.truncate()
            
            print(f"\\n[SUCCESS] PRD.json has been updated for {STORY_ID_TO_UPDATE}.")

        except json.JSONDecodeError as e:
            print(f"FATAL ERROR: Could not parse PRD.json. It may be corrupted. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    update_prd_status()
