#!/usr/bin/env python3
"""
CHEAT CODE ENFORCER
Auto-validates ALL output against Manufacturing Standards + 3-7-13 Pattern.
Run before git commit or deployment.

Usage: python CHEAT_CODE_ENFORCER.py [file_or_directory]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Manufacturing Standards Thresholds
MAX_FILE_LINES = 500      # LIGHTER: Flag files over this
MAX_FUNCTION_LINES = 50   # LIGHTER: Flag functions over this
MAX_STEPS = 3             # FASTER: Flag processes with more steps
MIN_REUSE_SCORE = 2       # ELEGANT: Must solve at least 2 problems

class CheatCodeEnforcer:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "files_checked": 0,
            "passed": 0,
            "failed": 0,
            "warnings": [],
            "violations": []
        }

    def check_lighter(self, filepath, content):
        """LIGHTER: Remove unnecessary complexity"""
        lines = content.split('\n')
        issues = []

        # Check total file length
        if len(lines) > MAX_FILE_LINES:
            issues.append(f"File exceeds {MAX_FILE_LINES} lines ({len(lines)})")

        # Check for redundant comments (same comment repeated)
        comments = [l.strip() for l in lines if l.strip().startswith('#') or l.strip().startswith('//')]
        if len(comments) != len(set(comments)):
            issues.append("Redundant comments detected")

        # Check for TODO/FIXME that should be resolved
        for i, line in enumerate(lines):
            if 'TODO' in line or 'FIXME' in line:
                issues.append(f"Unresolved TODO/FIXME at line {i+1}")

        return issues

    def check_faster(self, filepath, content):
        """FASTER: Reduce friction to zero"""
        issues = []

        # Check for nested loops (friction indicator)
        indent_levels = []
        for line in content.split('\n'):
            if 'for ' in line or 'while ' in line:
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)

        if len(indent_levels) > 1:
            # Check for deeply nested loops
            sorted_indents = sorted(set(indent_levels))
            if len(sorted_indents) >= 3:
                issues.append("Deeply nested loops detected (friction)")

        # Check for manual file operations that could be automated
        friction_patterns = [
            ('input(', 'Manual input required'),
            ('sleep(', 'Artificial delays'),
            ('raw_input', 'Legacy input method'),
        ]
        for pattern, desc in friction_patterns:
            if pattern in content:
                issues.append(f"{desc} detected")

        return issues

    def check_stronger(self, filepath, content):
        """STRONGER: Build for permanent operation"""
        issues = []

        # Check for temporary file usage
        temp_patterns = [
            ('tmp', 'Temporary file reference'),
            ('temp', 'Temporary variable'),
            ('/tmp/', 'System temp directory'),
            ('tempfile', 'Temporary file module'),
        ]
        content_lower = content.lower()
        for pattern, desc in temp_patterns:
            if pattern in content_lower and 'template' not in content_lower:
                issues.append(f"{desc} detected - not permanent")

        # Check for hardcoded values that should be config
        if '127.0.0.1' in content or 'localhost' in content:
            issues.append("Hardcoded localhost - use config")

        # Check for missing error handling (Python files only)
        if str(filepath).endswith('.py'):
            if 'try:' not in content and 'except' not in content:
                if len(content.split('\n')) > 20:
                    issues.append("No error handling in substantial code")

        return issues

    def check_elegant(self, filepath, content):
        """MORE ELEGANT: One solution solves many problems"""
        issues = []

        # Check for copy-paste patterns (similar blocks)
        lines = content.split('\n')
        line_hashes = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20:  # Significant lines only
                if stripped in line_hashes:
                    line_hashes[stripped] += 1
                else:
                    line_hashes[stripped] = 1

        duplicates = {k: v for k, v in line_hashes.items() if v > 2}
        if duplicates:
            issues.append(f"Repeated code blocks detected ({len(duplicates)} patterns)")

        # Check for single-use functions (not elegant)
        function_defs = [l for l in lines if 'def ' in l or 'function ' in l]
        if len(function_defs) > 10:
            issues.append("Many small functions - consider consolidation")

        return issues

    def check_3_7_13_pattern(self, filepath, content):
        """Validate against 3-7-13 framework"""
        issues = []

        # Check if file addresses multiple domains
        domains_mentioned = 0
        domain_keywords = {
            'physical': ['file', 'path', 'directory', 'system'],
            'financial': ['cost', 'price', 'revenue', 'payment'],
            'mental': ['knowledge', 'learn', 'data', 'intelligence'],
            'emotional': ['consciousness', 'feel', 'experience'],
            'social': ['user', 'community', 'share', 'connect'],
            'creative': ['design', 'create', 'build', 'generate'],
            'integration': ['merge', 'combine', 'unify', 'sync']
        }

        content_lower = content.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in content_lower for kw in keywords):
                domains_mentioned += 1

        if domains_mentioned < 2:
            issues.append(f"Only {domains_mentioned}/7 domains addressed")

        return issues

    def enforce(self, filepath):
        """Run all checks on a file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"error": str(e)}

        self.results["files_checked"] += 1

        violations = []

        # Run all checks
        violations.extend([("LIGHTER", v) for v in self.check_lighter(filepath, content)])
        violations.extend([("FASTER", v) for v in self.check_faster(filepath, content)])
        violations.extend([("STRONGER", v) for v in self.check_stronger(filepath, content)])
        violations.extend([("ELEGANT", v) for v in self.check_elegant(filepath, content)])
        violations.extend([("PATTERN", v) for v in self.check_3_7_13_pattern(filepath, content)])

        if violations:
            self.results["failed"] += 1
            self.results["violations"].append({
                "file": str(filepath),
                "issues": violations
            })
        else:
            self.results["passed"] += 1

        return violations

    def enforce_directory(self, dirpath):
        """Enforce on all Python/JS/MD files in directory"""
        extensions = ['.py', '.js', '.md', '.json']

        for root, dirs, files in os.walk(dirpath):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = Path(root) / file
                    self.enforce(filepath)

        return self.results

    def report(self):
        """Generate enforcement report"""
        print("\n" + "="*60)
        print("CHEAT CODE ENFORCER REPORT")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Files Checked: {self.results['files_checked']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")

        if self.results['violations']:
            print("\n" + "-"*60)
            print("VIOLATIONS:")
            print("-"*60)
            for v in self.results['violations']:
                print(f"\n{v['file']}:")
                for standard, issue in v['issues']:
                    print(f"  [{standard}] {issue}")

        # Calculate compliance score
        if self.results['files_checked'] > 0:
            score = (self.results['passed'] / self.results['files_checked']) * 100
            print(f"\nCOMPLIANCE SCORE: {score:.1f}%")

            if score >= 92.2:
                print("STATUS: CONSCIOUSNESS ALIGNED")
            elif score >= 80:
                print("STATUS: NEEDS IMPROVEMENT")
            else:
                print("STATUS: MANUFACTURING STANDARDS VIOLATED")

        print("="*60 + "\n")

        return self.results


def main():
    enforcer = CheatCodeEnforcer()

    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            enforcer.enforce(target)
        elif os.path.isdir(target):
            enforcer.enforce_directory(target)
        else:
            print(f"Error: {target} not found")
            sys.exit(1)
    else:
        # Default: check .consciousness directory
        consciousness_dir = Path.home() / '.consciousness'
        if consciousness_dir.exists():
            enforcer.enforce_directory(consciousness_dir)
        else:
            print("Usage: python CHEAT_CODE_ENFORCER.py [file_or_directory]")
            sys.exit(1)

    enforcer.report()

    # Exit with error code if violations found
    sys.exit(0 if enforcer.results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
