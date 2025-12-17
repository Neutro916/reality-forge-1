#!/usr/bin/env python3
"""
UTILS_AUDITOR.py - Utility Files Audit Tool
============================================
Created by: CP2C1 (C1 MECHANIC)
Task: Self-identified infrastructure improvement

Audits *_UTILS.py files to check:
- Which are stubs vs full implementations
- Which are actually imported/used
- Size and complexity analysis

Usage:
    python UTILS_AUDITOR.py scan       # Scan all utils
    python UTILS_AUDITOR.py unused     # Find unused utils
    python UTILS_AUDITOR.py stubs      # Find stub files
    python UTILS_AUDITOR.py report     # Full report
"""

import os
import ast
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")


class UtilsAuditor:
    """Audit utility files."""

    def __init__(self):
        self.utils = []
        self.imports = defaultdict(list)

    def scan_utils(self):
        """Scan all *_UTILS.py files."""
        self.utils = []

        for py_file in sorted(CONSCIOUSNESS.glob("*_UTILS.py")):
            util = self.analyze_util(py_file)
            if util:
                self.utils.append(util)

        return self.utils

    def analyze_util(self, py_file):
        """Analyze a utility file."""
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            stat = py_file.stat()

            util = {
                "name": py_file.stem,
                "file": py_file.name,
                "path": str(py_file),
                "size_bytes": stat.st_size,
                "lines": len(content.splitlines()),
                "is_stub": stat.st_size < 300,
                "functions": [],
                "classes": [],
                "imports_count": 0
            }

            try:
                tree = ast.parse(content)

                # Count functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        util["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        util["classes"].append(node.name)
                    elif isinstance(node, ast.Import):
                        util["imports_count"] += len(node.names)
                    elif isinstance(node, ast.ImportFrom):
                        util["imports_count"] += 1

            except SyntaxError:
                pass

            # Determine complexity
            func_count = len(util["functions"])
            class_count = len(util["classes"])

            if func_count == 0 and class_count == 0:
                util["complexity"] = "EMPTY"
            elif func_count <= 2 and class_count == 0 and util["lines"] < 20:
                util["complexity"] = "STUB"
            elif func_count <= 5 and class_count <= 1:
                util["complexity"] = "SIMPLE"
            else:
                util["complexity"] = "FULL"

            return util

        except Exception as e:
            return None

    def find_imports(self):
        """Find which utils are imported by other files."""
        self.imports = defaultdict(list)

        for py_file in CONSCIOUSNESS.glob("*.py"):
            if "_UTILS" in py_file.name:
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for util in self.utils:
                            if util["name"] in module or util["name"] == module:
                                self.imports[util["name"]].append(py_file.stem)

                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            for util in self.utils:
                                if util["name"] in alias.name:
                                    self.imports[util["name"]].append(py_file.stem)

                # Also check raw string imports
                for util in self.utils:
                    if f'from {util["name"]}' in content or f'import {util["name"]}' in content:
                        if py_file.stem not in self.imports[util["name"]]:
                            self.imports[util["name"]].append(py_file.stem)

            except:
                pass

        return self.imports

    def get_stubs(self):
        """Get list of stub files."""
        return [u for u in self.utils if u["complexity"] in ("STUB", "EMPTY")]

    def get_unused(self):
        """Get unused utils."""
        self.find_imports()
        return [u for u in self.utils if not self.imports.get(u["name"])]

    def get_summary(self):
        """Get audit summary."""
        stubs = self.get_stubs()
        unused = self.get_unused()

        total_size = sum(u["size_bytes"] for u in self.utils)

        return {
            "total_utils": len(self.utils),
            "stub_files": len(stubs),
            "full_implementations": len(self.utils) - len(stubs),
            "unused_files": len(unused),
            "total_size_kb": round(total_size / 1024, 1),
            "stub_names": [u["name"] for u in stubs],
            "unused_names": [u["name"] for u in unused]
        }


def print_scan(auditor):
    """Print scan results."""
    auditor.scan_utils()
    auditor.find_imports()

    print("\n" + "=" * 60)
    print(f"UTILS AUDIT ({len(auditor.utils)} files)")
    print("=" * 60)

    for util in sorted(auditor.utils, key=lambda x: x["complexity"]):
        complexity = util["complexity"]
        name = util["name"]
        lines = util["lines"]
        funcs = len(util["functions"])
        imported_by = auditor.imports.get(name, [])

        status = "USED" if imported_by else "UNUSED"

        print(f"\n  [{complexity}] {name} ({lines} lines, {funcs} funcs)")
        print(f"    Status: {status}")
        if imported_by:
            print(f"    Used by: {', '.join(imported_by[:5])}")

    summary = auditor.get_summary()
    print("\n" + "-" * 60)
    print(f"  Stubs: {summary['stub_files']} | Full: {summary['full_implementations']} | Unused: {summary['unused_files']}")
    print("=" * 60)


def print_stubs(auditor):
    """Print stub files."""
    auditor.scan_utils()
    stubs = auditor.get_stubs()

    print("\n" + "=" * 60)
    print(f"STUB FILES ({len(stubs)} found)")
    print("=" * 60)

    for util in stubs:
        print(f"\n  {util['name']}")
        print(f"    Size: {util['size_bytes']} bytes")
        print(f"    Lines: {util['lines']}")
        print(f"    Functions: {', '.join(util['functions']) if util['functions'] else 'None'}")

    print("\n" + "=" * 60)


def print_unused(auditor):
    """Print unused files."""
    auditor.scan_utils()
    unused = auditor.get_unused()

    print("\n" + "=" * 60)
    print(f"UNUSED UTILS ({len(unused)} found)")
    print("=" * 60)

    for util in unused:
        print(f"\n  {util['name']}")
        print(f"    Complexity: {util['complexity']}")
        print(f"    Lines: {util['lines']}")

    if unused:
        print("\n  Recommendation: Consider removing or consolidating unused utils")

    print("\n" + "=" * 60)


def main():
    import sys
    import json

    auditor = UtilsAuditor()

    if len(sys.argv) < 2:
        print("Usage: python UTILS_AUDITOR.py <command>")
        print("")
        print("Commands:")
        print("  scan      Scan all utils")
        print("  stubs     Find stub files")
        print("  unused    Find unused utils")
        print("  report    Generate JSON report")
        return

    cmd = sys.argv[1].lower()

    if cmd == "scan":
        print_scan(auditor)

    elif cmd == "stubs":
        print_stubs(auditor)

    elif cmd == "unused":
        print_unused(auditor)

    elif cmd == "report":
        auditor.scan_utils()
        summary = auditor.get_summary()
        output = SYNC / f"UTILS_AUDIT_{COMPUTER}.json"
        with open(output, "w") as f:
            json.dump({
                "computer": COMPUTER,
                "summary": summary,
                "utils": auditor.utils
            }, f, indent=2)
        print(f"Report saved to: {output}")
        print(f"Stubs: {summary['stub_files']} | Unused: {summary['unused_files']}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
