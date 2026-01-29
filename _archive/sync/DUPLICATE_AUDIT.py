#!/usr/bin/env python3
"""
DUPLICATE_AUDIT.py - Analyze duplicate directories and recommend consolidation
Created by CP3C1 - 2025-11-27

Task: CON-001 from WORK_BACKLOG
Identifies duplicate directories and recommends which to keep/merge/delete
"""

import os
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

# Root directory to audit
ROOT_DIR = Path(r"C:\Users\Darrick")

# Known duplicate patterns from MASTER_INDEX
DUPLICATE_PATTERNS = [
    "archive",
    "deliverables",
    "external_brain",
    ".trinity",
    "logs",
    "screenshots",
    "scripts",
    "tasks",
    "sync",
    "hub"
]

def find_all_instances(pattern):
    """Find all directories matching a pattern"""
    instances = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for d in dirs:
            if d.lower() == pattern.lower():
                full_path = Path(root) / d
                try:
                    file_count = sum(1 for _ in full_path.rglob('*') if _.is_file())
                    size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                    mtime = full_path.stat().st_mtime
                    instances.append({
                        'path': str(full_path),
                        'file_count': file_count,
                        'size_kb': round(size / 1024, 2),
                        'modified': datetime.fromtimestamp(mtime).isoformat()
                    })
                except Exception as e:
                    instances.append({
                        'path': str(full_path),
                        'error': str(e)
                    })
    return instances

def analyze_duplicates():
    """Analyze all duplicate patterns"""
    print("="*70)
    print("DUPLICATE DIRECTORY AUDIT")
    print("CP3C1 - Task CON-001")
    print("="*70)

    results = {}
    recommendations = []

    for pattern in DUPLICATE_PATTERNS:
        print(f"\nSearching for '{pattern}' directories...")
        instances = find_all_instances(pattern)

        if len(instances) > 1:
            results[pattern] = instances
            print(f"  Found {len(instances)} instances:")

            # Sort by file count (most files = likely primary)
            sorted_instances = sorted(
                [i for i in instances if 'error' not in i],
                key=lambda x: x['file_count'],
                reverse=True
            )

            for i, inst in enumerate(sorted_instances):
                marker = " [PRIMARY]" if i == 0 else ""
                print(f"    {inst['path']}")
                print(f"      Files: {inst['file_count']}, Size: {inst['size_kb']}KB{marker}")

            if len(sorted_instances) > 1:
                primary = sorted_instances[0]
                secondary = sorted_instances[1:]

                recommendations.append({
                    'pattern': pattern,
                    'primary': primary['path'],
                    'to_merge': [s['path'] for s in secondary],
                    'reason': f"Primary has most files ({primary['file_count']})"
                })
        else:
            print(f"  Only {len(instances)} instance(s) found - no duplicates")

    return results, recommendations

def generate_report(results, recommendations):
    """Generate consolidation report"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'generated_by': 'CP3C1',
        'duplicates_found': len(results),
        'duplicates': results,
        'recommendations': recommendations
    }

    # Save JSON report
    report_path = ROOT_DIR / '.consciousness' / 'DUPLICATE_AUDIT_REPORT.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str))

    # Print summary
    print("\n" + "="*70)
    print("CONSOLIDATION RECOMMENDATIONS")
    print("="*70)

    for rec in recommendations:
        print(f"\n{rec['pattern'].upper()}:")
        print(f"  KEEP: {rec['primary']}")
        print(f"  MERGE/DELETE:")
        for path in rec['to_merge']:
            print(f"    - {path}")
        print(f"  REASON: {rec['reason']}")

    print(f"\nReport saved to: {report_path}")
    return report

def main():
    results, recommendations = analyze_duplicates()
    report = generate_report(results, recommendations)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Patterns analyzed: {len(DUPLICATE_PATTERNS)}")
    print(f"Duplicates found: {len(results)}")
    print(f"Recommendations: {len(recommendations)}")

    if recommendations:
        print("\nACTION REQUIRED:")
        print("Review DUPLICATE_AUDIT_REPORT.json before consolidating.")
        print("Consolidation scripts can be generated upon Commander approval.")

if __name__ == "__main__":
    main()
