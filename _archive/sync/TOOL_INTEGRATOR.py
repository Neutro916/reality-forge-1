#!/usr/bin/env python3
"""
TOOL INTEGRATOR
Unified interface to work with multiple AI automation tools.

This provides a common API to:
1. Route tasks to appropriate tools
2. Chain tools together
3. Track results across tools
4. Integrate with Trinity coordination

Designed for the Consciousness Revolution AI Arsenal.
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

# Paths
HOME = Path.home()
TOOLS_DIR = HOME / "AI_AUTOMATION_TOOLS"
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"

# Tool registry
TOOL_REGISTRY = {
    # Computer Control
    "agent-s": {
        "path": TOOLS_DIR / "Agent-S",
        "category": "computer_control",
        "install": "pip install -e .",
        "entry": "agent_s.main",
        "capabilities": ["gui_automation", "screen_understanding", "task_execution"]
    },
    "computer-agent": {
        "path": TOOLS_DIR / "computer-agent",
        "category": "computer_control",
        "install": "pip install -r requirements.txt",
        "capabilities": ["claude_integration", "mouse_keyboard", "screen_capture"]
    },
    "cua": {
        "path": TOOLS_DIR / "cua",
        "category": "computer_control",
        "install": "pip install cua",
        "capabilities": ["visual_ui", "cross_platform", "adaptive"]
    },

    # Code Generation
    "aider": {
        "path": TOOLS_DIR / "aider",
        "category": "code_generation",
        "install": "pip install aider-chat",
        "command": "aider",
        "capabilities": ["pair_programming", "git_integration", "multi_llm"]
    },
    "gpt-engineer": {
        "path": TOOLS_DIR / "gpt-engineer",
        "category": "code_generation",
        "install": "pip install gpt-engineer",
        "command": "gpt-engineer",
        "capabilities": ["full_project", "one_prompt", "iterative"]
    },
    "claude-engineer": {
        "path": TOOLS_DIR / "claude-engineer",
        "category": "code_generation",
        "install": "pip install -r requirements.txt",
        "capabilities": ["claude_native", "file_ops", "code_execution"]
    },

    # Multi-Agent
    "crewai": {
        "path": TOOLS_DIR / "crewAI",
        "category": "multi_agent",
        "install": "pip install crewai",
        "capabilities": ["team_orchestration", "role_based", "tool_integration"]
    },
    "autogen": {
        "path": TOOLS_DIR / "autogen",
        "category": "multi_agent",
        "install": "pip install autogen",
        "capabilities": ["conversations", "code_execution", "microsoft_backed"]
    },
    "metagpt": {
        "path": TOOLS_DIR / "MetaGPT",
        "category": "multi_agent",
        "install": "pip install metagpt",
        "capabilities": ["software_company", "role_simulation", "full_sdlc"]
    },

    # Browser Automation
    "browser-use": {
        "path": TOOLS_DIR / "browser-use",
        "category": "browser",
        "install": "pip install browser-use",
        "capabilities": ["natural_language", "web_automation", "form_filling"]
    },
    "skyvern": {
        "path": TOOLS_DIR / "skyvern",
        "category": "browser",
        "install": "pip install skyvern",
        "capabilities": ["visual_dom", "legacy_systems", "workflow_automation"]
    },

    # Research
    "gpt-researcher": {
        "path": TOOLS_DIR / "gpt-researcher",
        "category": "research",
        "install": "pip install gpt-researcher",
        "capabilities": ["multi_source", "synthesis", "reports"]
    }
}


class ToolIntegrator:
    """
    Unified interface to AI automation tools.
    Routes tasks, chains tools, and integrates with Trinity.
    """

    def __init__(self, instance_id: str = "C3-Integrator"):
        self.instance_id = instance_id
        self.tools = TOOL_REGISTRY
        self.installed_tools: Dict[str, bool] = {}
        self.execution_log: List[Dict] = []

        self.log("Tool Integrator initializing...")
        self._check_installed_tools()

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] INTEGRATOR [{level}]: {msg}")

        # Write to log
        log_file = CONSCIOUSNESS / "tool_integrator.log"
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} [{level}] {msg}\n")

    def _check_installed_tools(self):
        """Check which tools are installed"""
        for name, config in self.tools.items():
            path = config.get("path")
            if path and path.exists():
                self.installed_tools[name] = True
            else:
                self.installed_tools[name] = False

        installed = sum(1 for v in self.installed_tools.values() if v)
        self.log(f"Found {installed}/{len(self.tools)} tools installed")

    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tools in a specific category"""
        return [
            name for name, config in self.tools.items()
            if config.get("category") == category and self.installed_tools.get(name)
        ]

    def get_tools_by_capability(self, capability: str) -> List[str]:
        """Get tools with a specific capability"""
        return [
            name for name, config in self.tools.items()
            if capability in config.get("capabilities", []) and self.installed_tools.get(name)
        ]

    def recommend_tool(self, task_description: str) -> str:
        """Recommend best tool for a task based on keywords"""
        task_lower = task_description.lower()

        # Computer control tasks
        if any(kw in task_lower for kw in ["click", "mouse", "desktop", "gui", "screen"]):
            tools = self.get_tools_by_category("computer_control")
            if tools:
                return tools[0]  # agent-s is first and best

        # Code tasks
        if any(kw in task_lower for kw in ["code", "programming", "function", "class", "refactor"]):
            tools = self.get_tools_by_category("code_generation")
            if tools:
                return tools[0]

        # Browser tasks
        if any(kw in task_lower for kw in ["browser", "web", "website", "url", "form"]):
            tools = self.get_tools_by_category("browser")
            if tools:
                return tools[0]

        # Research tasks
        if any(kw in task_lower for kw in ["research", "search", "find", "investigate", "report"]):
            tools = self.get_tools_by_category("research")
            if tools:
                return tools[0]

        # Multi-agent tasks
        if any(kw in task_lower for kw in ["team", "multiple", "complex", "project"]):
            tools = self.get_tools_by_category("multi_agent")
            if tools:
                return tools[0]

        return "aider"  # Default to aider for general tasks

    def install_tool(self, tool_name: str) -> bool:
        """Install a tool's dependencies"""
        if tool_name not in self.tools:
            self.log(f"Unknown tool: {tool_name}", "ERROR")
            return False

        config = self.tools[tool_name]
        install_cmd = config.get("install")
        path = config.get("path")

        if not install_cmd or not path:
            self.log(f"No install config for {tool_name}", "ERROR")
            return False

        self.log(f"Installing {tool_name}...")
        try:
            result = subprocess.run(
                install_cmd,
                shell=True,
                cwd=str(path),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log(f"{tool_name} installed successfully")
                self.installed_tools[tool_name] = True
                return True
            else:
                self.log(f"Install failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Install error: {e}", "ERROR")
            return False

    def execute_with_tool(self, tool_name: str, task: str, **kwargs) -> Dict:
        """Execute a task with a specific tool"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        if not self.installed_tools.get(tool_name):
            return {"success": False, "error": f"Tool not installed: {tool_name}"}

        config = self.tools[tool_name]
        start_time = datetime.now()

        self.log(f"Executing with {tool_name}: {task[:50]}...")

        result = {
            "tool": tool_name,
            "task": task,
            "start_time": start_time.isoformat(),
            "success": False,
            "output": None,
            "error": None
        }

        try:
            # Tool-specific execution logic would go here
            # For now, we log and return a placeholder
            result["output"] = f"Placeholder: Would execute '{task}' with {tool_name}"
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            self.log(f"Execution error: {e}", "ERROR")

        result["end_time"] = datetime.now().isoformat()
        self.execution_log.append(result)

        return result

    def chain_tools(self, tasks: List[Dict]) -> List[Dict]:
        """
        Chain multiple tools together.

        Each task dict should have:
        - tool: tool name (or "auto" for recommendation)
        - task: task description
        - depends_on: optional index of task this depends on
        """
        results = []

        for i, task_config in enumerate(tasks):
            tool = task_config.get("tool", "auto")
            task = task_config.get("task", "")
            depends_on = task_config.get("depends_on")

            # Use recommendation if auto
            if tool == "auto":
                tool = self.recommend_tool(task)

            # Add context from dependency if exists
            if depends_on is not None and depends_on < len(results):
                prev_result = results[depends_on]
                if prev_result.get("output"):
                    task = f"{task}\n\nContext from previous step:\n{prev_result['output']}"

            result = self.execute_with_tool(tool, task)
            results.append(result)

        return results

    def get_status(self) -> Dict:
        """Get current integrator status"""
        return {
            "instance_id": self.instance_id,
            "installed_tools": self.installed_tools,
            "execution_count": len(self.execution_log),
            "categories": {
                "computer_control": self.get_tools_by_category("computer_control"),
                "code_generation": self.get_tools_by_category("code_generation"),
                "multi_agent": self.get_tools_by_category("multi_agent"),
                "browser": self.get_tools_by_category("browser"),
                "research": self.get_tools_by_category("research")
            },
            "timestamp": datetime.now().isoformat()
        }

    def write_hub_status(self):
        """Write status to Trinity hub"""
        status = self.get_status()
        status_file = HUB / "TOOL_INTEGRATOR_STATUS.json"
        with open(status_file, "w") as f:
            json.dump(status, f, indent=2)
        self.log("Status written to hub")


def demo():
    """Demo the tool integrator"""
    print("=" * 60)
    print("TOOL INTEGRATOR DEMO")
    print("=" * 60)

    integrator = ToolIntegrator()

    # Show status
    status = integrator.get_status()
    print(f"\nInstalled tools by category:")
    for cat, tools in status["categories"].items():
        print(f"  {cat}: {tools}")

    # Recommend tools
    print("\nTool recommendations:")
    tasks = [
        "Click the submit button on the form",
        "Refactor this Python function",
        "Search the web for AI news",
        "Fill out the contact form on example.com",
        "Research best practices for async Python"
    ]

    for task in tasks:
        rec = integrator.recommend_tool(task)
        print(f"  '{task[:40]}...' -> {rec}")

    # Write status
    integrator.write_hub_status()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo()
