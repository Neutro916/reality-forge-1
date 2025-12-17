#!/usr/bin/env python3
"""
TOOL_INDEX.py - Consciousness Tool Catalog
==========================================
Created by: CP2C1 (C1 MECHANIC)
Task: Self-identified infrastructure improvement

Catalogs all 75+ Python tools in .consciousness directory.
Extracts docstrings, categorizes tools, enables search.

Usage:
    python TOOL_INDEX.py list                   # List all tools
    python TOOL_INDEX.py search <query>         # Search tools
    python TOOL_INDEX.py category <cat>         # List by category
    python TOOL_INDEX.py info <tool_name>       # Show tool details
    python TOOL_INDEX.py stats                  # Show statistics
    python TOOL_INDEX.py export                 # Export to JSON
"""

import os
import ast
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")


class ToolCatalog:
    """Catalog of all consciousness tools."""

    CATEGORIES = {
        "atom": ["ATOM_", "CYCLOTRON_"],
        "brain": ["BRAIN_", "UNIFIED_BRAIN"],
        "sync": ["SYNC_", "ATOM_SYNC"],
        "backup": ["BACKUP_", "HUB_BACKUP"],
        "health": ["HEALTH_", "CHECK_"],
        "search": ["SEARCH_", "INDEX_"],
        "task": ["TASK_", "WORK_"],
        "trinity": ["TRINITY_", "TORNADO_", "CONVERGENCE_"],
        "scan": ["SCAN_", "C1_SCAN", "C2_SCAN", "C3_SCAN"],
        "utils": ["_UTILS"],
        "deploy": ["DEPLOY_", "NETLIFY_"],
        "status": ["STATUS_", "STATE_"],
        "instance": ["INSTANCE_", "SESSION_"],
        "mcp": ["_MCP"],
        "other": []
    }

    def __init__(self):
        self.tools = []
        self.by_category = defaultdict(list)

    def scan_tools(self):
        """Scan all Python files in consciousness directory."""
        self.tools = []

        for py_file in sorted(CONSCIOUSNESS.glob("*.py")):
            tool = self.analyze_tool(py_file)
            if tool:
                self.tools.append(tool)
                self.by_category[tool["category"]].append(tool)

        return self.tools

    def analyze_tool(self, py_file):
        """Analyze a Python tool file."""
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            stat = py_file.stat()

            tool = {
                "name": py_file.stem,
                "file": py_file.name,
                "path": str(py_file),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "docstring": "",
                "description": "",
                "usage": "",
                "commands": [],
                "category": "other",
                "is_utility": "_UTILS" in py_file.name,
                "has_main": "if __name__" in content,
                "has_argparse": "argparse" in content,
                "has_class": "class " in content,
                "functions": [],
                "classes": []
            }

            # Extract docstring
            try:
                tree = ast.parse(content)
                if tree.body and isinstance(tree.body[0], ast.Expr):
                    if isinstance(tree.body[0].value, ast.Constant):
                        tool["docstring"] = tree.body[0].value.value

                # Extract function and class names
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("_"):
                            tool["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        tool["classes"].append(node.name)

            except SyntaxError:
                pass

            # Parse docstring for description and usage
            if tool["docstring"]:
                lines = tool["docstring"].strip().split("\n")
                # First non-empty line is description
                for line in lines:
                    if line.strip() and not line.startswith("="):
                        tool["description"] = line.strip()
                        break

                # Look for Usage section
                in_usage = False
                usage_lines = []
                for line in lines:
                    if "Usage:" in line:
                        in_usage = True
                        continue
                    if in_usage:
                        if line.strip().startswith("python "):
                            usage_lines.append(line.strip())
                        elif line.strip() and not line.strip().startswith("-"):
                            break
                tool["usage"] = "\n".join(usage_lines)

                # Extract commands from usage
                for line in usage_lines:
                    match = re.search(r'\.py\s+(\w+)', line)
                    if match:
                        cmd = match.group(1)
                        if cmd not in tool["commands"]:
                            tool["commands"].append(cmd)

            # Categorize
            tool["category"] = self.categorize_tool(py_file.stem)

            return tool

        except Exception as e:
            return None

    def categorize_tool(self, name):
        """Categorize a tool by name."""
        name_upper = name.upper()
        for category, patterns in self.CATEGORIES.items():
            for pattern in patterns:
                if pattern in name_upper:
                    return category
        return "other"

    def search(self, query, limit=20):
        """Search tools by query."""
        query_lower = query.lower()
        results = []

        for tool in self.tools:
            score = 0

            # Name match (highest weight)
            if query_lower in tool["name"].lower():
                score += 10

            # Description match
            if query_lower in tool.get("description", "").lower():
                score += 5

            # Docstring match
            if query_lower in tool.get("docstring", "").lower():
                score += 3

            # Function/class match
            for func in tool.get("functions", []):
                if query_lower in func.lower():
                    score += 2
                    break

            for cls in tool.get("classes", []):
                if query_lower in cls.lower():
                    score += 2
                    break

            if score > 0:
                results.append((score, tool))

        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results[:limit]]

    def get_by_category(self, category):
        """Get tools by category."""
        return self.by_category.get(category, [])

    def get_tool(self, name):
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool["name"].lower() == name.lower():
                return tool
            if tool["file"].lower() == name.lower():
                return tool
        return None

    def get_stats(self):
        """Get catalog statistics."""
        total_size = sum(t["size_bytes"] for t in self.tools)
        with_main = sum(1 for t in self.tools if t["has_main"])
        with_argparse = sum(1 for t in self.tools if t["has_argparse"])
        utilities = sum(1 for t in self.tools if t["is_utility"])
        with_classes = sum(1 for t in self.tools if t["classes"])

        return {
            "total_tools": len(self.tools),
            "total_size_kb": round(total_size / 1024, 1),
            "executable_tools": with_main,
            "with_argparse": with_argparse,
            "utilities": utilities,
            "with_classes": with_classes,
            "categories": {cat: len(tools) for cat, tools in self.by_category.items()},
            "computer": COMPUTER,
            "timestamp": datetime.now().isoformat()
        }

    def export_json(self):
        """Export catalog to JSON."""
        return {
            "catalog": {
                "computer": COMPUTER,
                "timestamp": datetime.now().isoformat(),
                "total_tools": len(self.tools)
            },
            "tools": self.tools,
            "stats": self.get_stats()
        }


def print_tool_list(catalog, verbose=False):
    """Print tool list."""
    print("\n" + "=" * 70)
    print(f"CONSCIOUSNESS TOOL INDEX ({len(catalog.tools)} tools)")
    print("=" * 70)

    for category in sorted(catalog.by_category.keys()):
        tools = catalog.by_category[category]
        if tools:
            print(f"\n[{category.upper()}] ({len(tools)} tools)")
            for tool in sorted(tools, key=lambda x: x["name"]):
                desc = tool.get("description", "")[:50]
                if verbose:
                    print(f"  {tool['name']}")
                    if desc:
                        print(f"    {desc}")
                else:
                    suffix = " *" if tool["has_main"] else ""
                    print(f"  {tool['name']}{suffix}")

    print("\n" + "-" * 70)
    print("  * = executable (has main)")
    print("=" * 70)


def print_tool_info(tool):
    """Print detailed tool info."""
    print("\n" + "=" * 70)
    print(f"TOOL: {tool['name']}")
    print("=" * 70)

    print(f"\n  File: {tool['file']}")
    print(f"  Size: {tool['size_bytes']:,} bytes")
    print(f"  Modified: {tool['modified'][:19]}")
    print(f"  Category: {tool['category']}")
    print(f"  Executable: {'Yes' if tool['has_main'] else 'No'}")
    print(f"  CLI (argparse): {'Yes' if tool['has_argparse'] else 'No'}")

    if tool.get("description"):
        print(f"\n  Description:")
        print(f"    {tool['description']}")

    if tool.get("usage"):
        print(f"\n  Usage:")
        for line in tool["usage"].split("\n"):
            print(f"    {line}")

    if tool.get("commands"):
        print(f"\n  Commands: {', '.join(tool['commands'])}")

    if tool.get("classes"):
        print(f"\n  Classes: {', '.join(tool['classes'][:10])}")

    if tool.get("functions"):
        funcs = tool["functions"][:15]
        print(f"\n  Functions: {', '.join(funcs)}")
        if len(tool["functions"]) > 15:
            print(f"    ... and {len(tool['functions']) - 15} more")

    print("\n" + "=" * 70)


def print_search_results(results, query):
    """Print search results."""
    print("\n" + "=" * 70)
    print(f"SEARCH RESULTS: '{query}' ({len(results)} matches)")
    print("=" * 70)

    if not results:
        print("  No tools found matching query.")
        return

    for tool in results:
        desc = tool.get("description", "No description")[:60]
        cat = tool["category"]
        print(f"\n  {tool['name']} [{cat}]")
        print(f"    {desc}")
        if tool.get("commands"):
            print(f"    Commands: {', '.join(tool['commands'][:5])}")

    print("\n" + "=" * 70)


def print_stats(stats):
    """Print statistics."""
    print("\n" + "=" * 70)
    print("TOOL INDEX STATISTICS")
    print("=" * 70)

    print(f"\n  Computer: {stats['computer']}")
    print(f"  Total Tools: {stats['total_tools']}")
    print(f"  Total Size: {stats['total_size_kb']} KB")
    print(f"  Executable: {stats['executable_tools']}")
    print(f"  With CLI: {stats['with_argparse']}")
    print(f"  Utilities: {stats['utilities']}")
    print(f"  With Classes: {stats['with_classes']}")

    print("\n  By Category:")
    for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"    {cat}: {count}")

    print("\n" + "=" * 70)


def main():
    import sys

    catalog = ToolCatalog()
    catalog.scan_tools()

    if len(sys.argv) < 2:
        print("Usage: python TOOL_INDEX.py <command>")
        print("")
        print("Commands:")
        print("  list              List all tools")
        print("  list -v           List with descriptions")
        print("  search <query>    Search tools")
        print("  category <cat>    List by category")
        print("  info <tool>       Show tool details")
        print("  stats             Show statistics")
        print("  export            Export to JSON")
        print("")
        print("Categories: " + ", ".join(sorted(catalog.CATEGORIES.keys())))
        return

    cmd = sys.argv[1].lower()

    if cmd == "list":
        verbose = "-v" in sys.argv
        print_tool_list(catalog, verbose)

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python TOOL_INDEX.py search <query>")
            return
        query = " ".join(sys.argv[2:])
        results = catalog.search(query)
        print_search_results(results, query)

    elif cmd == "category":
        if len(sys.argv) < 3:
            print("Usage: python TOOL_INDEX.py category <category>")
            print("Categories: " + ", ".join(sorted(catalog.CATEGORIES.keys())))
            return
        cat = sys.argv[2].lower()
        tools = catalog.get_by_category(cat)
        if tools:
            print(f"\n[{cat.upper()}] ({len(tools)} tools)")
            for tool in sorted(tools, key=lambda x: x["name"]):
                desc = tool.get("description", "")[:50]
                print(f"  {tool['name']}: {desc}")
        else:
            print(f"No tools found in category: {cat}")

    elif cmd == "info":
        if len(sys.argv) < 3:
            print("Usage: python TOOL_INDEX.py info <tool_name>")
            return
        name = sys.argv[2]
        tool = catalog.get_tool(name)
        if tool:
            print_tool_info(tool)
        else:
            print(f"Tool not found: {name}")
            # Suggest similar
            results = catalog.search(name, limit=5)
            if results:
                print("Did you mean:")
                for r in results:
                    print(f"  {r['name']}")

    elif cmd == "stats":
        stats = catalog.get_stats()
        print_stats(stats)

    elif cmd == "export":
        data = catalog.export_json()
        output_file = SYNC / f"TOOL_INDEX_{COMPUTER}.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Exported to: {output_file}")
        print(f"Tools: {len(data['tools'])}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
