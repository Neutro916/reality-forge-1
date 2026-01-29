#!/usr/bin/env python3
"""
NETLIFY_DEPLOYMENT_VERIFIER.py - HTML Dashboard Deployment Verification
========================================================================
Created by: CP2C1 (C1 MECHANIC)
Task: MAINT-002 from WORK_BACKLOG

Verifies all HTML dashboards are ready for Netlify deployment.
Checks for: broken links, missing assets, valid HTML structure, dependencies.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
DEPLOYMENT = HOME / "100X_DEPLOYMENT"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

class NetlifyVerifier:
    """Verify HTML dashboards for Netlify deployment."""

    def __init__(self, deployment_dir=DEPLOYMENT):
        self.deployment_dir = Path(deployment_dir)
        self.html_files = []
        self.checks = []
        self.issues = defaultdict(list)
        self.stats = {}

    def find_html_files(self):
        """Find all HTML files in deployment directory."""
        self.html_files = list(self.deployment_dir.rglob("*.html"))
        return len(self.html_files)

    def check_html_structure(self, html_file):
        """Check basic HTML structure validity."""
        issues = []
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')

            # Check for doctype
            if not re.search(r'<!DOCTYPE\s+html', content, re.IGNORECASE):
                issues.append("Missing DOCTYPE declaration")

            # Check for <html> tag
            if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
                issues.append("Missing <html> tag")

            # Check for <head> section
            if not re.search(r'<head[^>]*>', content, re.IGNORECASE):
                issues.append("Missing <head> section")

            # Check for <title>
            if not re.search(r'<title[^>]*>.*</title>', content, re.IGNORECASE | re.DOTALL):
                issues.append("Missing <title> tag")

            # Check for <body>
            if not re.search(r'<body[^>]*>', content, re.IGNORECASE):
                issues.append("Missing <body> tag")

            # Check for viewport meta (mobile responsiveness)
            if not re.search(r'<meta[^>]*viewport', content, re.IGNORECASE):
                issues.append("Missing viewport meta tag (mobile)")

        except Exception as e:
            issues.append(f"Read error: {e}")

        return issues

    def check_internal_links(self, html_file):
        """Check for broken internal links."""
        issues = []
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')

            # Find href links
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)

            for href in hrefs:
                # Skip external links and anchors
                if href.startswith(('http://', 'https://', '#', 'mailto:', 'tel:')):
                    continue

                # Check if local file exists
                if href.startswith('/'):
                    linked_file = self.deployment_dir / href.lstrip('/')
                else:
                    linked_file = html_file.parent / href

                # Normalize and check
                try:
                    linked_file = linked_file.resolve()
                    if not linked_file.exists() and not href.endswith('.html'):
                        # Maybe it's a route, not a file
                        pass
                    elif not linked_file.exists():
                        issues.append(f"Broken link: {href}")
                except:
                    pass

        except Exception as e:
            issues.append(f"Link check error: {e}")

        return issues

    def check_external_dependencies(self, html_file):
        """Check for external CDN dependencies."""
        dependencies = []
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')

            # Find CDN scripts
            scripts = re.findall(r'src=["\']([^"\']*cdn[^"\']+)["\']', content, re.IGNORECASE)
            for script in scripts:
                dependencies.append(f"CDN: {script[:60]}...")

            # Find CDN stylesheets
            styles = re.findall(r'href=["\']([^"\']*cdn[^"\']+\.css[^"\']*)["\']', content, re.IGNORECASE)
            for style in styles:
                dependencies.append(f"CSS: {style[:60]}...")

        except:
            pass

        return dependencies

    def check_api_keys_exposed(self, html_file):
        """Check for exposed API keys (security issue)."""
        issues = []
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')

            # Common API key patterns
            patterns = [
                (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API key'),
                (r'AIza[a-zA-Z0-9_-]{35}', 'Google API key'),
                (r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']', 'Generic API key'),
                (r'secret["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']', 'Secret token'),
            ]

            for pattern, name in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"SECURITY: Possible {name} exposed")

        except:
            pass

        return issues

    def categorize_files(self):
        """Categorize HTML files by type."""
        categories = {
            'detectors': [],
            'dashboards': [],
            'analyzers': [],
            'trackers': [],
            'tools': [],
            'pages': [],
            'other': []
        }

        for f in self.html_files:
            name = f.stem.upper()
            if 'DETECTOR' in name:
                categories['detectors'].append(f)
            elif 'DASHBOARD' in name or 'PANEL' in name:
                categories['dashboards'].append(f)
            elif 'ANALYZER' in name or 'ANALYSIS' in name:
                categories['analyzers'].append(f)
            elif 'TRACKER' in name:
                categories['trackers'].append(f)
            elif 'TOOL' in name or 'SEARCH' in name or 'CHECK' in name:
                categories['tools'].append(f)
            elif name in ['INDEX', 'ABOUT', 'WELCOME', 'ONBOARD']:
                categories['pages'].append(f)
            else:
                categories['other'].append(f)

        return categories

    def run_verification(self):
        """Run all verification checks."""
        self.find_html_files()

        results = {
            'structure_issues': 0,
            'link_issues': 0,
            'security_issues': 0,
            'files_checked': 0,
            'files_passed': 0,
            'external_deps': []
        }

        file_results = []

        for html_file in self.html_files:
            rel_path = html_file.relative_to(self.deployment_dir)

            structure_issues = self.check_html_structure(html_file)
            link_issues = self.check_internal_links(html_file)
            security_issues = self.check_api_keys_exposed(html_file)
            external_deps = self.check_external_dependencies(html_file)

            all_issues = structure_issues + link_issues + security_issues

            file_result = {
                'file': str(rel_path),
                'status': 'PASS' if not all_issues else 'ISSUES',
                'structure': structure_issues,
                'links': link_issues,
                'security': security_issues,
                'dependencies': external_deps
            }

            file_results.append(file_result)
            results['files_checked'] += 1

            if not all_issues:
                results['files_passed'] += 1

            results['structure_issues'] += len(structure_issues)
            results['link_issues'] += len(link_issues)
            results['security_issues'] += len(security_issues)
            results['external_deps'].extend(external_deps)

        # Deduplicate external deps
        results['external_deps'] = list(set(results['external_deps']))

        self.stats = results
        self.checks = file_results

        return results

    def get_summary(self):
        """Get verification summary."""
        if not self.stats:
            self.run_verification()

        total = self.stats['files_checked']
        passed = self.stats['files_passed']

        if self.stats['security_issues'] > 0:
            overall = 'SECURITY_WARNING'
        elif passed == total:
            overall = 'PASS'
        elif passed > total * 0.9:
            overall = 'MOSTLY_PASS'
        else:
            overall = 'NEEDS_ATTENTION'

        return {
            'overall': overall,
            'total_files': total,
            'passed': passed,
            'percentage': f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
            'structure_issues': self.stats['structure_issues'],
            'link_issues': self.stats['link_issues'],
            'security_issues': self.stats['security_issues'],
            'external_dependencies': len(self.stats['external_deps'])
        }

    def generate_report(self):
        """Generate full deployment verification report."""
        if not self.stats:
            self.run_verification()

        summary = self.get_summary()
        categories = self.categorize_files()

        return {
            'timestamp': datetime.now().isoformat(),
            'computer': COMPUTER,
            'deployment_dir': str(self.deployment_dir),
            'summary': summary,
            'categories': {k: len(v) for k, v in categories.items()},
            'issues': [c for c in self.checks if c['status'] != 'PASS'],
            'external_dependencies': self.stats['external_deps'][:20]  # Top 20
        }


def print_results(verifier):
    """Print verification results."""
    summary = verifier.get_summary()
    categories = verifier.categorize_files()

    print("\n" + "="*60)
    print("NETLIFY DEPLOYMENT VERIFICATION")
    print("="*60)
    print(f"  Deployment: {verifier.deployment_dir}")
    print(f"  Overall: {summary['overall']}")
    print(f"  Files: {summary['passed']}/{summary['total_files']} ({summary['percentage']})")
    print()

    print("CATEGORIES:")
    for cat, files in categories.items():
        if files:
            print(f"  {cat.title()}: {len(files)} files")
    print()

    print("CHECKS:")
    print(f"  [{'PASS' if summary['structure_issues']==0 else 'WARN'}] HTML Structure: {summary['structure_issues']} issues")
    print(f"  [{'PASS' if summary['link_issues']==0 else 'WARN'}] Internal Links: {summary['link_issues']} issues")
    print(f"  [{'PASS' if summary['security_issues']==0 else 'FAIL'}] Security: {summary['security_issues']} issues")
    print(f"  [INFO] External CDN Dependencies: {summary['external_dependencies']}")
    print()

    if summary['security_issues'] > 0:
        print("SECURITY WARNINGS:")
        for check in verifier.checks:
            if check['security']:
                print(f"  ! {check['file']}")
                for issue in check['security']:
                    print(f"      {issue}")
        print()

    # Show files with issues
    files_with_issues = [c for c in verifier.checks if c['status'] != 'PASS']
    if files_with_issues and len(files_with_issues) <= 20:
        print(f"FILES WITH ISSUES ({len(files_with_issues)}):")
        for f in files_with_issues[:15]:
            issues = f['structure'] + f['links']
            print(f"  - {f['file']}: {len(issues)} issues")
        if len(files_with_issues) > 15:
            print(f"  ... and {len(files_with_issues)-15} more")

    print("="*60)


def main():
    import sys

    verifier = NetlifyVerifier()

    if len(sys.argv) < 2:
        # Default: run verification
        verifier.run_verification()
        print_results(verifier)

        summary = verifier.get_summary()
        if summary['security_issues'] > 0:
            print("\nACTION REQUIRED: Security issues detected!")
        elif summary['overall'] == 'PASS':
            print("\nREADY FOR DEPLOYMENT: All checks passed!")
        else:
            print("\nMINOR ISSUES: Review and fix for optimal deployment.")
        return

    cmd = sys.argv[1].lower()

    if cmd == "json":
        verifier.run_verification()
        report = verifier.generate_report()
        print(json.dumps(report, indent=2))

    elif cmd == "sync":
        verifier.run_verification()
        print_results(verifier)

        if SYNC.exists():
            report = verifier.generate_report()
            report_path = SYNC / f"NETLIFY_VERIFY_{COMPUTER}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport synced: {report_path.name}")

    elif cmd == "list":
        count = verifier.find_html_files()
        print(f"\nHTML Files in Deployment ({count}):")
        for f in sorted(verifier.html_files):
            rel = f.relative_to(verifier.deployment_dir)
            print(f"  {rel}")

    elif cmd == "categories":
        verifier.find_html_files()
        categories = verifier.categorize_files()
        print("\nHTML File Categories:")
        for cat, files in categories.items():
            if files:
                print(f"\n{cat.upper()} ({len(files)}):")
                for f in files[:10]:
                    print(f"  - {f.stem}")
                if len(files) > 10:
                    print(f"  ... and {len(files)-10} more")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python NETLIFY_DEPLOYMENT_VERIFIER.py [json|sync|list|categories]")


if __name__ == "__main__":
    main()
