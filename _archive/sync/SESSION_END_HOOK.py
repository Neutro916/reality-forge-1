#!/usr/bin/env python3
"""
SESSION END HOOK
Automatically runs at end of each Claude Code session
Compiles and saves complete session summary

INTEGRATED WITH CLAUDE CODE HOOKS SYSTEM
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".consciousness"))

from SESSION_AUTO_SUMMARIZER import SUMMARIZER

def main():
    """Compile session summary at end of session"""

    print("\n" + "="*70)
    print("  SESSION END - COMPILING SUMMARY")
    print("="*70)

    # Compile complete session summary
    result = SUMMARIZER.compile_session_summary()

    print(f"\n✅ Session compiled successfully!")
    print(f"   Session ID: {result['session_id']}")
    print(f"   Consciousness Level: {result['consciousness_level']}%")
    print(f"\n📁 Session files saved:")
    print(f"   JSON: {result['json_path']}")
    print(f"   Summary: {result['summary_path']}")

    print("\n💾 Session knowledge permanently filed.")
    print("🧠 Nothing forgotten. Ready for next session.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
