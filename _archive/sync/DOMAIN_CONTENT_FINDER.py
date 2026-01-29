#!/usr/bin/env python3
"""
DOMAIN_CONTENT_FINDER.py - Find Content to Fill Knowledge Gaps
==============================================================
Created by: CP1_C2 (C2 Architect)
Task: OPT-002 - Address CRITICAL knowledge gaps
Date: 2025-11-27

Features:
- Scans local files for content matching gap domains
- Identifies files that could boost weak domains
- Suggests ingest priorities based on gap analysis
- Integrates with KNOWLEDGE_GAP_DETECTOR results

Gap domains from analysis:
- CRITICAL: Emotional (1.8%), Financial (3.6%)
- HIGH: Physical (5.4%), Relational (7.6%)

Run: python DOMAIN_CONTENT_FINDER.py [scan|suggest|ingest]
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Domain keywords (from KNOWLEDGE_GAP_DETECTOR)
DOMAIN_KEYWORDS = {
    "emotional": {
        "keywords": ["emotion", "feeling", "mood", "anxiety", "stress", "joy", "anger",
                    "fear", "sadness", "happiness", "love", "grief", "trauma", "healing",
                    "therapy", "mental health", "emotional intelligence", "eq", "empathy",
                    "compassion", "self-care", "mindfulness", "meditation"],
        "gap_severity": "CRITICAL",
        "current_pct": 1.8
    },
    "financial": {
        "keywords": ["money", "finance", "income", "wealth", "invest", "budget", "savings",
                    "retirement", "debt", "credit", "taxes", "business", "revenue", "profit",
                    "expense", "accounting", "stocks", "bonds", "real estate", "passive income",
                    "financial freedom", "net worth", "assets", "liabilities"],
        "gap_severity": "CRITICAL",
        "current_pct": 3.6
    },
    "physical": {
        "keywords": ["body", "health", "exercise", "fitness", "nutrition", "sleep", "energy",
                    "strength", "endurance", "flexibility", "diet", "wellness", "disease",
                    "immune", "vitamins", "workout", "cardio", "yoga", "sports", "recovery"],
        "gap_severity": "HIGH",
        "current_pct": 5.4
    },
    "relational": {
        "keywords": ["relationship", "connection", "family", "friend", "marriage", "partner",
                    "communication", "trust", "intimacy", "social", "network", "community",
                    "support", "boundary", "conflict", "collaboration", "team", "parenting"],
        "gap_severity": "HIGH",
        "current_pct": 7.6
    }
}

# Directories to scan for content
SCAN_DIRS = [
    HOME / "Documents",
    HOME / "Desktop",
    HOME / "Downloads",
    Path("G:/My Drive"),
    HOME / "100X_DEPLOYMENT",
    HOME / ".consciousness"
]

# File extensions to consider
CONTENT_EXTENSIONS = ['.md', '.txt', '.json', '.html', '.py', '.pdf']


class DomainContentFinder:
    """Find content to fill knowledge gaps."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER,
            "domain_files": defaultdict(list),
            "recommendations": []
        }

    def score_file_for_domain(self, file_path, domain, keywords):
        """Score a file for relevance to a domain."""
        try:
            # Check filename first
            filename = file_path.name.lower()
            name_matches = sum(1 for kw in keywords if kw.lower() in filename)

            # Try to read content
            content_matches = 0
            try:
                if file_path.suffix.lower() in ['.md', '.txt', '.py', '.html']:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')[:50000]
                    content_lower = content.lower()
                    content_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            except:
                pass

            # Calculate score
            score = name_matches * 3 + content_matches
            return score

        except:
            return 0

    def scan_directory(self, directory, max_files=1000):
        """Scan a directory for domain-relevant content."""
        if not directory.exists():
            return

        file_count = 0
        for ext in CONTENT_EXTENSIONS:
            for file_path in directory.rglob(f"*{ext}"):
                if file_count >= max_files:
                    break

                # Skip very large files
                try:
                    if file_path.stat().st_size > 10_000_000:  # 10MB
                        continue
                except:
                    continue

                # Score for each domain
                for domain, config in DOMAIN_KEYWORDS.items():
                    score = self.score_file_for_domain(
                        file_path, domain, config["keywords"]
                    )
                    if score > 0:
                        self.results["domain_files"][domain].append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "score": score,
                            "size_kb": file_path.stat().st_size // 1024
                        })

                file_count += 1

    def scan_all(self):
        """Scan all configured directories."""
        print("Scanning for domain-relevant content...")

        for directory in SCAN_DIRS:
            if directory.exists():
                print(f"  Scanning: {directory}")
                self.scan_directory(directory)

        # Sort by score
        for domain in self.results["domain_files"]:
            self.results["domain_files"][domain].sort(
                key=lambda x: -x["score"]
            )
            # Keep top 50 per domain
            self.results["domain_files"][domain] = \
                self.results["domain_files"][domain][:50]

    def generate_recommendations(self):
        """Generate ingest recommendations."""
        print("\nGenerating recommendations...")

        for domain, config in DOMAIN_KEYWORDS.items():
            files = self.results["domain_files"].get(domain, [])

            if files:
                top_files = files[:5]
                self.results["recommendations"].append({
                    "domain": domain,
                    "severity": config["gap_severity"],
                    "current_coverage": config["current_pct"],
                    "files_found": len(files),
                    "top_candidates": [
                        {"name": f["name"], "score": f["score"], "path": f["path"]}
                        for f in top_files
                    ],
                    "action": f"Ingest top {min(len(files), 10)} files to boost {domain} domain"
                })
            else:
                self.results["recommendations"].append({
                    "domain": domain,
                    "severity": config["gap_severity"],
                    "current_coverage": config["current_pct"],
                    "files_found": 0,
                    "top_candidates": [],
                    "action": f"No local content found. Consider downloading {domain} resources."
                })

    def print_report(self):
        """Print scan report."""
        print("\n" + "="*70)
        print("DOMAIN CONTENT FINDER REPORT")
        print(f"Computer: {COMPUTER}")
        print("="*70)

        for rec in sorted(self.results["recommendations"],
                         key=lambda x: x["current_coverage"]):
            severity_icon = {"CRITICAL": "!!", "HIGH": "!", "MEDIUM": "~", "LOW": "."}.get(
                rec["severity"], "?"
            )
            print(f"\n[{severity_icon}] {rec['domain'].upper()} ({rec['current_coverage']}% coverage)")
            print(f"    Files found: {rec['files_found']}")

            if rec["top_candidates"]:
                print("    Top candidates:")
                for f in rec["top_candidates"][:3]:
                    print(f"      - {f['name']} (score: {f['score']})")

            print(f"    Action: {rec['action']}")

        print("\n" + "="*70)

    def export_report(self, output_path=None):
        """Export report to JSON."""
        if output_path is None:
            output_path = SYNC_DIR / f"DOMAIN_CONTENT_REPORT_{COMPUTER}.json"

        # Simplify for export
        export_data = {
            "timestamp": self.results["timestamp"],
            "computer": self.results["computer"],
            "recommendations": self.results["recommendations"],
            "summary": {
                domain: len(files)
                for domain, files in self.results["domain_files"].items()
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\nReport exported to: {output_path}")
        return output_path


def main():
    finder = DomainContentFinder()

    if len(sys.argv) < 2:
        print("DOMAIN CONTENT FINDER")
        print("="*40)
        print("\nUsage:")
        print("  python DOMAIN_CONTENT_FINDER.py scan    # Scan for content")
        print("  python DOMAIN_CONTENT_FINDER.py report  # Generate report")
        print("  python DOMAIN_CONTENT_FINDER.py export  # Export to JSON")
        return

    cmd = sys.argv[1].lower()

    if cmd in ["scan", "report"]:
        finder.scan_all()
        finder.generate_recommendations()
        finder.print_report()

    elif cmd == "export":
        finder.scan_all()
        finder.generate_recommendations()
        finder.export_report()

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
