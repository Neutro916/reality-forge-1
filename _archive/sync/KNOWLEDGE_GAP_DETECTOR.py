#!/usr/bin/env python3
"""
KNOWLEDGE_GAP_DETECTOR.py - Knowledge Gap Analysis
===================================================
Created by: CP2C1 (C1 MECHANIC)
Task: ENH-006 from WORK_BACKLOG

Analyzes the Cyclotron brain to detect knowledge gaps.
Identifies missing topics, weak areas, and suggests improvements.

Usage:
    python KNOWLEDGE_GAP_DETECTOR.py scan               # Full gap analysis
    python KNOWLEDGE_GAP_DETECTOR.py domains            # Check Seven Domains coverage
    python KNOWLEDGE_GAP_DETECTOR.py types              # Analyze atom type distribution
    python KNOWLEDGE_GAP_DETECTOR.py recent             # Check recent vs historical balance
    python KNOWLEDGE_GAP_DETECTOR.py report             # Generate full report
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
LOCAL_DB = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Seven Domains of Mastery
SEVEN_DOMAINS = {
    "creative": ["art", "design", "creative", "visual", "aesthetic", "music", "writing"],
    "technical": ["code", "programming", "software", "technical", "engineering", "algorithm"],
    "strategic": ["strategy", "planning", "roadmap", "architecture", "system"],
    "relational": ["communication", "team", "collaboration", "network", "social"],
    "operational": ["process", "workflow", "automation", "operations", "deploy"],
    "financial": ["business", "revenue", "pricing", "monetization", "market"],
    "spiritual": ["consciousness", "awareness", "pattern", "theory", "philosophy", "wisdom"]
}

# Expected atom types
EXPECTED_TYPES = [
    "concept", "pattern", "technique", "tool", "framework",
    "insight", "connection", "principle", "example", "reference"
]


class KnowledgeGapDetector:
    """Detects gaps in the knowledge base."""

    def __init__(self, db_path=LOCAL_DB):
        self.db_path = db_path
        self.stats = {}
        self.gaps = []

    def get_atom_stats(self):
        """Get basic atom statistics."""
        if not self.db_path.exists():
            return {}

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) FROM atoms")
        total = cursor.fetchone()[0]

        # By type
        cursor.execute("""
            SELECT type, COUNT(*) as cnt
            FROM atoms
            GROUP BY type
            ORDER BY cnt DESC
        """)
        by_type = dict(cursor.fetchall())

        # By confidence
        cursor.execute("""
            SELECT
                CASE
                    WHEN confidence >= 0.8 THEN 'high'
                    WHEN confidence >= 0.5 THEN 'medium'
                    ELSE 'low'
                END as level,
                COUNT(*) as cnt
            FROM atoms
            GROUP BY level
        """)
        by_confidence = dict(cursor.fetchall())

        # Recent vs old
        cursor.execute("""
            SELECT COUNT(*) FROM atoms
            WHERE created > datetime('now', '-7 days')
        """)
        recent_week = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM atoms
            WHERE created > datetime('now', '-30 days')
        """)
        recent_month = cursor.fetchone()[0]

        conn.close()

        self.stats = {
            "total": total,
            "by_type": by_type,
            "by_confidence": by_confidence,
            "recent_week": recent_week,
            "recent_month": recent_month
        }

        return self.stats

    def analyze_domain_coverage(self):
        """Analyze coverage of Seven Domains."""
        if not self.db_path.exists():
            return {}

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        domain_coverage = {}

        for domain, keywords in SEVEN_DOMAINS.items():
            # Build search pattern
            patterns = [f"%{kw}%" for kw in keywords]

            # Count atoms matching any keyword
            placeholders = " OR ".join(["content LIKE ? OR tags LIKE ?" for _ in patterns])
            params = []
            for p in patterns:
                params.extend([p, p])

            query = f"SELECT COUNT(*) FROM atoms WHERE {placeholders}"
            cursor.execute(query, params)
            count = cursor.fetchone()[0]

            domain_coverage[domain] = count

        conn.close()

        # Calculate percentages
        total = sum(domain_coverage.values())
        if total > 0:
            for domain in domain_coverage:
                pct = (domain_coverage[domain] / total) * 100
                domain_coverage[domain] = {
                    "count": domain_coverage[domain],
                    "percentage": round(pct, 1)
                }

        return domain_coverage

    def analyze_type_gaps(self):
        """Analyze missing or underrepresented atom types."""
        if not self.stats:
            self.get_atom_stats()

        type_gaps = []
        existing_types = self.stats.get("by_type", {})
        total = self.stats.get("total", 0)

        if total == 0:
            return type_gaps

        for expected in EXPECTED_TYPES:
            count = existing_types.get(expected, 0)
            pct = (count / total) * 100

            if count == 0:
                type_gaps.append({
                    "type": expected,
                    "status": "MISSING",
                    "count": 0,
                    "recommendation": f"Create atoms of type '{expected}'"
                })
            elif pct < 1:
                type_gaps.append({
                    "type": expected,
                    "status": "LOW",
                    "count": count,
                    "percentage": round(pct, 2),
                    "recommendation": f"Increase '{expected}' atoms (currently {count})"
                })

        return type_gaps

    def analyze_recency_balance(self):
        """Analyze balance between recent and historical knowledge."""
        if not self.stats:
            self.get_atom_stats()

        total = self.stats.get("total", 0)
        recent_week = self.stats.get("recent_week", 0)
        recent_month = self.stats.get("recent_month", 0)

        if total == 0:
            return {}

        week_pct = (recent_week / total) * 100
        month_pct = (recent_month / total) * 100

        status = "BALANCED"
        issues = []

        # Too much recent (brain is mostly new, lacks historical depth)
        if month_pct > 80:
            status = "TOO_RECENT"
            issues.append("Brain lacks historical depth - most knowledge is recent")

        # Too little recent (brain isn't learning)
        elif recent_week == 0:
            status = "STAGNANT"
            issues.append("No new atoms in last week - brain isn't actively learning")

        return {
            "status": status,
            "recent_week_pct": round(week_pct, 1),
            "recent_month_pct": round(month_pct, 1),
            "issues": issues
        }

    def find_gaps(self):
        """Find all knowledge gaps."""
        self.gaps = []

        # Domain gaps
        domains = self.analyze_domain_coverage()
        if domains:
            avg_coverage = sum(d["count"] for d in domains.values()) / len(domains)
            for domain, data in domains.items():
                if data["count"] < avg_coverage * 0.3:  # Less than 30% of average
                    self.gaps.append({
                        "category": "domain",
                        "area": domain,
                        "severity": "HIGH" if data["count"] < avg_coverage * 0.1 else "MEDIUM",
                        "count": data["count"],
                        "recommendation": f"Add more knowledge about {domain.upper()} domain"
                    })

        # Type gaps
        type_gaps = self.analyze_type_gaps()
        for gap in type_gaps:
            self.gaps.append({
                "category": "type",
                "area": gap["type"],
                "severity": "HIGH" if gap["status"] == "MISSING" else "LOW",
                "count": gap["count"],
                "recommendation": gap["recommendation"]
            })

        # Confidence gaps
        if self.stats:
            by_conf = self.stats.get("by_confidence", {})
            low_conf = by_conf.get("low", 0)
            total = self.stats.get("total", 1)
            low_pct = (low_conf / total) * 100

            if low_pct > 30:
                self.gaps.append({
                    "category": "quality",
                    "area": "confidence",
                    "severity": "MEDIUM",
                    "count": low_conf,
                    "recommendation": f"Improve atom quality - {low_pct:.1f}% have low confidence"
                })

        return self.gaps

    def generate_report(self):
        """Generate full gap analysis report."""
        self.get_atom_stats()
        domains = self.analyze_domain_coverage()
        recency = self.analyze_recency_balance()
        gaps = self.find_gaps()

        return {
            "timestamp": datetime.now().isoformat(),
            "computer": COMPUTER,
            "summary": {
                "total_atoms": self.stats.get("total", 0),
                "gaps_found": len(gaps),
                "high_severity": sum(1 for g in gaps if g["severity"] == "HIGH"),
                "overall_health": "GOOD" if len(gaps) < 3 else ("FAIR" if len(gaps) < 6 else "NEEDS_ATTENTION")
            },
            "stats": self.stats,
            "domain_coverage": domains,
            "recency_balance": recency,
            "gaps": gaps,
            "recommendations": [g["recommendation"] for g in gaps[:5]]
        }


def print_scan_results(detector):
    """Print scan results."""
    gaps = detector.find_gaps()

    print("\n" + "=" * 60)
    print("KNOWLEDGE GAP SCAN")
    print("=" * 60)

    print(f"\nTotal Atoms: {detector.stats.get('total', 0):,}")
    print(f"Gaps Found: {len(gaps)}")

    if gaps:
        print("\nGaps Detected:")
        for gap in sorted(gaps, key=lambda x: (0 if x["severity"] == "HIGH" else 1)):
            sev = gap["severity"]
            area = gap["area"]
            rec = gap["recommendation"]
            print(f"\n  [{sev}] {area}")
            print(f"    {rec}")
    else:
        print("\n  No significant gaps detected!")

    print("\n" + "=" * 60)


def print_domain_coverage(detector):
    """Print domain coverage."""
    domains = detector.analyze_domain_coverage()

    print("\n" + "=" * 60)
    print("SEVEN DOMAINS COVERAGE")
    print("=" * 60)

    for domain, data in sorted(domains.items(), key=lambda x: -x[1]["count"]):
        count = data["count"]
        pct = data["percentage"]
        bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
        print(f"\n  {domain.upper()}: {count:,} atoms ({pct}%)")
        print(f"    [{bar}]")

    print("\n" + "=" * 60)


def print_type_distribution(detector):
    """Print type distribution."""
    detector.get_atom_stats()
    by_type = detector.stats.get("by_type", {})

    print("\n" + "=" * 60)
    print("ATOM TYPE DISTRIBUTION")
    print("=" * 60)

    total = detector.stats.get("total", 1)
    for atype, count in sorted(by_type.items(), key=lambda x: -x[1])[:15]:
        pct = (count / total) * 100
        bar = "#" * int(pct / 3) + "-" * max(0, (20 - int(pct / 3)))
        print(f"\n  {atype}: {count:,} ({pct:.1f}%)")
        print(f"    [{bar}]")

    # Show missing expected types
    missing = [t for t in EXPECTED_TYPES if t not in by_type]
    if missing:
        print(f"\n  Missing types: {', '.join(missing)}")

    print("\n" + "=" * 60)


def print_recency(detector):
    """Print recency analysis."""
    recency = detector.analyze_recency_balance()

    print("\n" + "=" * 60)
    print("RECENCY BALANCE")
    print("=" * 60)

    print(f"\n  Status: {recency.get('status', 'UNKNOWN')}")
    print(f"  Last 7 days: {recency.get('recent_week_pct', 0)}%")
    print(f"  Last 30 days: {recency.get('recent_month_pct', 0)}%")

    issues = recency.get("issues", [])
    if issues:
        print("\n  Issues:")
        for issue in issues:
            print(f"    - {issue}")

    print("\n" + "=" * 60)


def main():
    import sys

    detector = KnowledgeGapDetector()

    if len(sys.argv) < 2:
        print("Usage: python KNOWLEDGE_GAP_DETECTOR.py <command>")
        print("")
        print("Commands:")
        print("  scan      Full gap analysis")
        print("  domains   Check Seven Domains coverage")
        print("  types     Analyze atom type distribution")
        print("  recent    Check recency balance")
        print("  report    Generate full JSON report")
        return

    cmd = sys.argv[1].lower()

    if cmd == "scan":
        print_scan_results(detector)

    elif cmd == "domains":
        print_domain_coverage(detector)

    elif cmd == "types":
        print_type_distribution(detector)

    elif cmd == "recent":
        print_recency(detector)

    elif cmd == "report":
        report = detector.generate_report()
        output = SYNC / f"KNOWLEDGE_GAP_REPORT_{COMPUTER}.json"
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {output}")
        print(f"Gaps found: {report['summary']['gaps_found']}")
        print(f"Overall health: {report['summary']['overall_health']}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
