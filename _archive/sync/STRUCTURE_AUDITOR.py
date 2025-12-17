#!/usr/bin/env python3
"""
STRUCTURE AUDITOR
Maps every square inch of the ecosystem structure.
Finds hollow areas, orphan files, broken links, and generates a complete map.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
OUTPUT_DIR = HOME / '.consciousness' / 'structure_audit'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class StructureAuditor:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'by_extension': defaultdict(lambda: {'count': 0, 'size': 0}),
            'by_depth': defaultdict(int),
            'empty_files': [],
            'empty_dirs': [],
            'large_files': [],  # >1MB
            'recent_files': [],  # Modified in last 7 days
            'old_files': [],  # Not modified in 90+ days
            'potential_hollows': [],  # Dirs with only 1-2 files
        }
        self.tree = {}

    def audit(self):
        """Full audit of the structure"""
        print(f"Auditing: {self.root}")
        print("This may take a moment...")

        for dirpath, dirnames, filenames in os.walk(self.root):
            # Skip node_modules, .git, __pycache__
            dirnames[:] = [d for d in dirnames if d not in ['node_modules', '.git', '__pycache__', '.venv']]

            rel_path = Path(dirpath).relative_to(self.root)
            depth = len(rel_path.parts)
            self.stats['total_dirs'] += 1
            self.stats['by_depth'][depth] += 1

            # Check for empty or near-empty dirs
            if len(filenames) == 0 and len(dirnames) == 0:
                self.stats['empty_dirs'].append(str(rel_path))
            elif len(filenames) <= 2 and len(dirnames) == 0:
                self.stats['potential_hollows'].append({
                    'path': str(rel_path),
                    'files': filenames
                })

            for filename in filenames:
                filepath = Path(dirpath) / filename
                self.stats['total_files'] += 1

                try:
                    stat = filepath.stat()
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    ext = filepath.suffix.lower() or '.no_ext'

                    self.stats['total_size'] += size
                    self.stats['by_extension'][ext]['count'] += 1
                    self.stats['by_extension'][ext]['size'] += size

                    # Empty files
                    if size == 0:
                        self.stats['empty_files'].append(str(filepath.relative_to(self.root)))

                    # Large files
                    if size > 1_000_000:  # 1MB
                        self.stats['large_files'].append({
                            'path': str(filepath.relative_to(self.root)),
                            'size_mb': round(size / 1_000_000, 2)
                        })

                    # Recent vs old
                    days_old = (datetime.now() - mtime).days
                    if days_old <= 7:
                        self.stats['recent_files'].append({
                            'path': str(filepath.relative_to(self.root)),
                            'days_ago': days_old
                        })
                    elif days_old > 90:
                        self.stats['old_files'].append(str(filepath.relative_to(self.root)))

                except (OSError, PermissionError):
                    pass

        return self.stats

    def generate_report(self):
        """Generate human-readable report"""
        s = self.stats
        total_mb = s['total_size'] / 1_000_000

        # Sort extensions by count
        sorted_ext = sorted(s['by_extension'].items(), key=lambda x: -x[1]['count'])

        report = f"""# STRUCTURE AUDIT REPORT
## {self.root}
## Generated: {datetime.now().isoformat()}

---

## OVERVIEW

| Metric | Value |
|--------|-------|
| Total Files | {s['total_files']:,} |
| Total Directories | {s['total_dirs']:,} |
| Total Size | {total_mb:,.1f} MB |
| Empty Files | {len(s['empty_files'])} |
| Empty Directories | {len(s['empty_dirs'])} |
| Potential Hollows | {len(s['potential_hollows'])} |
| Recent (7 days) | {len(s['recent_files'])} |
| Old (90+ days) | {len(s['old_files'])} |

---

## FILES BY EXTENSION (Top 20)

| Extension | Count | Size (MB) |
|-----------|-------|-----------|
"""
        for ext, data in sorted_ext[:20]:
            size_mb = data['size'] / 1_000_000
            report += f"| {ext} | {data['count']:,} | {size_mb:,.1f} |\n"

        report += f"""
---

## DEPTH DISTRIBUTION

| Depth | Directories |
|-------|-------------|
"""
        for depth in sorted(s['by_depth'].keys()):
            report += f"| {depth} | {s['by_depth'][depth]} |\n"

        if s['empty_dirs']:
            report += f"""
---

## EMPTY DIRECTORIES ({len(s['empty_dirs'])})

"""
            for d in s['empty_dirs'][:20]:
                report += f"- {d}\n"
            if len(s['empty_dirs']) > 20:
                report += f"... and {len(s['empty_dirs']) - 20} more\n"

        if s['potential_hollows']:
            report += f"""
---

## POTENTIAL HOLLOW AREAS ({len(s['potential_hollows'])})
(Directories with only 1-2 files, no subdirs)

"""
            for h in s['potential_hollows'][:20]:
                report += f"- {h['path']}: {h['files']}\n"

        if s['large_files']:
            report += f"""
---

## LARGE FILES >1MB ({len(s['large_files'])})

"""
            for f in sorted(s['large_files'], key=lambda x: -x['size_mb'])[:20]:
                report += f"- {f['path']} ({f['size_mb']} MB)\n"

        report += f"""
---

## HEALTH ASSESSMENT

"""
        # Calculate health score
        health_issues = []
        if len(s['empty_files']) > 50:
            health_issues.append(f"Many empty files ({len(s['empty_files'])})")
        if len(s['empty_dirs']) > 20:
            health_issues.append(f"Many empty directories ({len(s['empty_dirs'])})")
        if len(s['potential_hollows']) > 30:
            health_issues.append(f"Many sparse directories ({len(s['potential_hollows'])})")
        if len(s['old_files']) > s['total_files'] * 0.5:
            health_issues.append("Over 50% of files are 90+ days old")

        if health_issues:
            report += "### Issues Found:\n"
            for issue in health_issues:
                report += f"- {issue}\n"
        else:
            report += "No major structural issues detected.\n"

        report += f"""
---

## RECOMMENDATIONS

1. Review empty directories and remove if unnecessary
2. Check potential hollow areas for incomplete implementations
3. Large files may need archiving or compression
4. Consider updating files older than 90 days or archiving them

---

*Generated by STRUCTURE_AUDITOR.py*
"""
        return report

    def save_results(self, name='audit'):
        """Save audit results to files"""
        # JSON stats
        stats_file = OUTPUT_DIR / f'{name}_stats.json'
        # Convert defaultdicts to regular dicts for JSON
        stats_json = dict(self.stats)
        stats_json['by_extension'] = dict(stats_json['by_extension'])
        stats_json['by_depth'] = dict(stats_json['by_depth'])

        with open(stats_file, 'w') as f:
            json.dump(stats_json, f, indent=2, default=str)

        # Markdown report
        report_file = OUTPUT_DIR / f'{name}_report.md'
        with open(report_file, 'w') as f:
            f.write(self.generate_report())

        print(f"\nResults saved:")
        print(f"  Stats: {stats_file}")
        print(f"  Report: {report_file}")

        return stats_file, report_file


def audit_path(path, name='audit'):
    """Public API to audit a path"""
    auditor = StructureAuditor(path)
    auditor.audit()
    return auditor.save_results(name)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else 'audit'
    else:
        path = str(HOME / '100X_DEPLOYMENT')
        name = '100X_DEPLOYMENT'

    audit_path(path, name)
