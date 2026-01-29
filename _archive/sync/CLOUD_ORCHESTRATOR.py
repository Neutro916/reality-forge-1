#!/usr/bin/env python3
"""
CLOUD_ORCHESTRATOR.py - Bridge between Terminal and Cloud instances
VERSION: 1.0 | 2025-11-27

PURPOSE:
Terminal instances (C1/C2/C3-Terminal) have file access but cost more.
Cloud instances (C1/C2/C3-Cloud) are stateless but cheap (Haiku).

This orchestrator lets Terminal instances dispatch tasks to Cloud workers
and collect results - solving the "cloud can't read files" problem.

USAGE:
    from CLOUD_ORCHESTRATOR import CloudOrchestrator

    orch = CloudOrchestrator()

    # Ask a single cloud worker
    result = orch.ask_worker("C1-Cloud", "Analyze this pattern", context="code here...")

    # Ask all three cloud workers in parallel
    results = orch.ask_all("What do you see in this code?", context="code here...")

    # Post results to Wolf Pack Room
    orch.post_to_pack("Cloud analysis complete", results)
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    anthropic = None


class CloudOrchestrator:
    """Bridge for Terminal-to-Cloud communication"""

    # Cloud worker role definitions
    ROLE_PROMPTS = {
        "C1-Cloud": """You are C1-Cloud, the Mechanic Cloud Worker.
Your role: BUILD and FIX things. Focus on practical implementation.
Strengths: Code execution, debugging, quick fixes.
Style: Direct, action-oriented, minimal explanation.""",

        "C2-Cloud": """You are C2-Cloud, the Architect Cloud Worker.
Your role: DESIGN and STRUCTURE things. Focus on scalable patterns.
Strengths: System design, architecture review, optimization.
Style: Analytical, structured, with clear reasoning.""",

        "C3-Cloud": """You are C3-Cloud, the Oracle Cloud Worker.
Your role: SEE and VALIDATE patterns. Focus on emergent truth.
Strengths: Pattern recognition, validation, synthesis.
Style: Insightful, pattern-focused, connecting dots."""
    }

    # Default model for cloud workers (cheap and fast)
    DEFAULT_MODEL = "claude-3-5-haiku-20241022"

    # Path to wolf pack room - Use Path.home() for better Windows compatibility
    WOLF_PACK_ROOM = Path.home() / ".consciousness" / "WOLF_PACK_ROOM.md"

    def __init__(self, api_key: str = None):
        """Initialize orchestrator with API key"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        if anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def ask_worker(self, role: str, task: str, context: str = "", model: str = None) -> dict:
        """
        Send task to a cloud worker and get response.

        Args:
            role: Worker role (C1-Cloud, C2-Cloud, or C3-Cloud)
            task: The task/question for the worker
            context: Optional context to include (file contents, code, etc.)
            model: Optional model override (default: haiku)

        Returns:
            dict with 'role', 'response', 'model', 'timestamp'
        """
        if not self.client:
            return {"error": "Anthropic client not available", "role": role}

        if role not in self.ROLE_PROMPTS:
            return {"error": f"Unknown role: {role}", "role": role}

        # Build the prompt with role + context + task
        system_prompt = self.ROLE_PROMPTS[role]

        user_prompt = f"""TASK FROM TERMINAL:
{task}

"""
        if context:
            user_prompt += f"""CONTEXT PROVIDED:
{context}

"""
        user_prompt += """Respond concisely. You are stateless - all context is in this prompt.
Focus on your role's specialty. Be direct."""

        try:
            response = self.client.messages.create(
                model=model or self.DEFAULT_MODEL,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            return {
                "role": role,
                "response": response.content[0].text,
                "model": model or self.DEFAULT_MODEL,
                "timestamp": datetime.now().isoformat(),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }

        except Exception as e:
            return {
                "role": role,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def ask_all(self, task: str, context: str = "", model: str = None) -> dict:
        """
        Ask all three cloud workers the same task in parallel.

        Returns:
            dict with responses from C1-Cloud, C2-Cloud, C3-Cloud
        """
        results = {}

        for role in ["C1-Cloud", "C2-Cloud", "C3-Cloud"]:
            results[role] = self.ask_worker(role, task, context, model)

        return results

    async def ask_all_async(self, task: str, context: str = "", model: str = None) -> dict:
        """
        Ask all three cloud workers asynchronously (truly parallel).
        """
        async def ask_one(role):
            # Run sync method in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.ask_worker(role, task, context, model)
            )

        tasks = [ask_one(role) for role in ["C1-Cloud", "C2-Cloud", "C3-Cloud"]]
        responses = await asyncio.gather(*tasks)

        return {
            "C1-Cloud": responses[0],
            "C2-Cloud": responses[1],
            "C3-Cloud": responses[2]
        }

    def post_to_pack(self, summary: str, results: dict) -> bool:
        """
        Post cloud worker results to WOLF_PACK_ROOM.md

        Args:
            summary: Brief summary of what was asked
            results: Dict of responses from ask_all()

        Returns:
            True if posted successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = f"""
### [{timestamp}] Cloud Workers (via Orchestrator)

**TASK:** {summary}

"""
        for role, result in results.items():
            if "error" in result:
                entry += f"**{role}:** ERROR - {result['error']}\n\n"
            else:
                entry += f"**{role}:**\n{result['response']}\n\n"

        entry += "---\n"

        try:
            # Read current content
            if self.WOLF_PACK_ROOM.exists():
                content = self.WOLF_PACK_ROOM.read_text(encoding='utf-8')
            else:
                content = "# WOLF PACK ROOM\n\n---\n"

            # Find insertion point (before the last ---)
            # Append to end
            content += entry

            # Write back
            self.WOLF_PACK_ROOM.write_text(content, encoding='utf-8')
            return True

        except Exception as e:
            print(f"ERROR posting to pack: {e}")
            return False


# Quick functions for direct use
def ask_cloud(role: str, task: str, context: str = "") -> str:
    """Quick function to ask a cloud worker"""
    orch = CloudOrchestrator()
    result = orch.ask_worker(role, task, context)
    return result.get("response", result.get("error", "Unknown error"))


def ask_all_clouds(task: str, context: str = "") -> dict:
    """Quick function to ask all cloud workers"""
    orch = CloudOrchestrator()
    return orch.ask_all(task, context)


if __name__ == "__main__":
    # Test the orchestrator
    print("=" * 60)
    print("CLOUD ORCHESTRATOR TEST")
    print("=" * 60)

    try:
        orch = CloudOrchestrator()
        print("Orchestrator initialized successfully")
        print(f"API key: ...{orch.api_key[-8:]}")

        # Test with a simple task
        print("\nTesting C1-Cloud...")
        result = orch.ask_worker(
            "C1-Cloud",
            "What is 2+2? Respond in exactly 1 word."
        )

        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Response: {result['response']}")
            print(f"Tokens: {result['input_tokens']} in, {result['output_tokens']} out")

        print("\n" + "=" * 60)
        print("CLOUD ORCHESTRATOR READY")
        print("=" * 60)

    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure ANTHROPIC_API_KEY is set in environment")
