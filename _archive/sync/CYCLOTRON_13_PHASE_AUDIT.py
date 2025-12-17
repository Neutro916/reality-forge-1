#!/usr/bin/env python3
"""CYCLOTRON 13-PHASE AUDIT SYSTEM - Complete Cyclotron knowledge base analysis."""

import os; import json; import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

class CyclotronAuditor:
    """13-Phase Cyclotron Audit System"""
    def __init__(self):
        self.home = Path.home(); self.deployment = self.home / '100X_DEPLOYMENT'
        self.atoms_dir = self.deployment / '.cyclotron_atoms'; self.dropbox = self.home / 'Dropbox'
        self.federation = self.dropbox / '.cyclotron_federation' if self.dropbox.exists() else None
        self.results = {'timestamp': datetime.now().isoformat(), 'phases': {}, 'overall_score': 0, 'critical_issues': [], 'recommendations': []}

    def run_full_audit(self):
        """Run all 13 phases"""
        print("=" * 70 + "\nCYCLOTRON 13-PHASE AUDIT SYSTEM\n" + "=" * 70 + "\n")
        phases = [("1. Structure", self.phase_1_structure), ("2. Integrity", self.phase_2_integrity),
                  ("3. Index", self.phase_3_index), ("4. Federation", self.phase_4_federation),
                  ("5. Performance", self.phase_5_performance), ("6. Coverage", self.phase_6_coverage),
                  ("7. Duplication", self.phase_7_duplication), ("8. Types", self.phase_8_types),
                  ("9. Growth", self.phase_9_growth), ("10. Errors", self.phase_10_errors),
                  ("11. API", self.phase_11_api), ("12. Security", self.phase_12_security),
                  ("13. Optimization", self.phase_13_optimization)]
        total_score = 0
        for name, func in phases:
            print(f"\n{'='*70}\nPHASE: {name}\n{'='*70}")
            try:
                result = func(); self.results['phases'][name] = result; score = result.get('score', 0); total_score += score
                status = "PASS" if score >= 70 else "WARN" if score >= 50 else "FAIL"
                icon = "" if score >= 70 else "⚠️" if score >= 50 else ""
                print(f"\n{icon} Phase Score: {score}/100 [{status}]")
                for issue in result.get('issues', []): self.results['critical_issues'].append(f"{name}: {issue}"); print(f"   Issue: {issue}")
            except Exception as e: print(f" Error: {e}"); self.results['phases'][name] = {'score': 0, 'error': str(e)}
        self.results['overall_score'] = round(total_score / len(phases))
        self.generate_recommendations(); self.print_summary(); self.save_results()
        return self.results

    def phase_1_structure(self):
        """Audit file and folder structure"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if self.atoms_dir.exists(): r['checks']['atoms_dir'] = True; r['score'] += 20
        else: r['checks']['atoms_dir'] = False; r['issues'].append("Atoms directory missing")
        atom_files = list(self.atoms_dir.glob('atoms_*.json')) if self.atoms_dir.exists() else []
        r['checks']['atom_files_count'] = len(atom_files)
        if len(atom_files) > 0: r['score'] += 20
        if len(atom_files) > 5: r['score'] += 10
        index_file = self.atoms_dir / 'index.json' if self.atoms_dir.exists() else None
        if index_file and index_file.exists(): r['checks']['index_exists'] = True; r['score'] += 20
        else: r['checks']['index_exists'] = False; r['issues'].append("Index file missing")
        if self.atoms_dir.exists() and (self.atoms_dir / 'mega_todos.json').exists(): r['checks']['mega_todos'] = True; r['score'] += 15
        scripts = ['CYCLOTRON_MASTER_RAKER.py', 'CYCLOTRON_INDEX_UPDATER.py', 'CYCLOTRON_ANALYTICS_ENGINE.py']
        existing = sum(1 for s in scripts if (self.deployment / s).exists()); r['checks']['scripts'] = f"{existing}/{len(scripts)}"
        r['score'] = min(100, int(r['score'] + (existing / len(scripts)) * 15))
        print(f"  Atoms dir: {'✓' if r['checks'].get('atoms_dir') else '✗'} | Files: {r['checks']['atom_files_count']} | Index: {'✓' if r['checks'].get('index_exists') else '✗'} | Scripts: {r['checks']['scripts']}")
        return r

    def phase_2_integrity(self):
        """Check data integrity of all JSON files"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if not self.atoms_dir.exists(): r['issues'].append("Atoms directory missing"); return r
        json_files = list(self.atoms_dir.glob('*.json')); valid, invalid = 0, []
        for jf in json_files:
            try: json.load(open(jf)); valid += 1
            except: invalid.append(jf.name)
        r['checks'] = {'total_json': len(json_files), 'valid_json': valid, 'invalid_json': invalid}
        r['score'] = int((valid / len(json_files)) * 100) if json_files else 0
        if not json_files: r['issues'].append("No JSON files found")
        if invalid: r['issues'].append(f"Invalid: {', '.join(invalid)}")
        print(f"  Total: {len(json_files)} | Valid: {valid} | Invalid: {len(invalid)}")
        return r

    def phase_3_index(self):
        """Check index health and staleness"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        index_file = self.atoms_dir / 'index.json' if self.atoms_dir.exists() else None
        if not index_file or not index_file.exists(): r['issues'].append("Index file not found"); return r
        try:
            index = json.load(open(index_file)); last_updated = index.get('last_updated', 0)
            age_minutes = (time.time() - last_updated) / 60
            r['checks']['last_updated'] = datetime.fromtimestamp(last_updated).isoformat(); r['checks']['age_minutes'] = round(age_minutes, 1)
            r['score'] += 40 if age_minutes < 10 else 25 if age_minutes < 60 else 0
            if age_minutes >= 60: r['issues'].append(f"Index stale ({round(age_minutes)}m old)")
            atom_count = index.get('total_atoms', 0); r['checks']['total_atoms'] = atom_count
            r['score'] += 30 if atom_count > 100 else 15 if atom_count > 0 else 0
            if atom_count == 0: r['issues'].append("No atoms in index")
            types = index.get('atoms_by_type', {}); r['checks']['atom_types'] = len(types)
            r['score'] += 30 if len(types) >= 5 else 15 if len(types) > 0 else 0
        except Exception as e: r['issues'].append(f"Failed to read index: {e}")
        r['score'] = min(100, r['score'])
        print(f"  Updated: {r['checks'].get('last_updated', 'N/A')} | Age: {r['checks'].get('age_minutes', 'N/A')}m | Atoms: {r['checks'].get('total_atoms', 0)} | Types: {r['checks'].get('atom_types', 0)}")
        return r

    def phase_4_federation(self):
        """Check federation (Dropbox sync) status"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if not self.dropbox or not self.dropbox.exists():
            r['checks']['dropbox'] = False; r['issues'].append("Dropbox not found"); print("  Dropbox: NOT FOUND"); return r
        r['checks']['dropbox'] = True; r['score'] += 25
        if self.federation and self.federation.exists(): r['checks']['federation_dir'] = True; r['score'] += 25
        else: r['checks']['federation_dir'] = False; r['issues'].append("Federation directory not created")
        if self.federation:
            atoms_sync = self.federation / 'atoms'
            if atoms_sync.exists(): synced = len(list(atoms_sync.glob('*.json'))); r['checks']['synced_atoms'] = synced; r['score'] += 25 if synced > 0 else 0
            if (self.federation / 'indices' / 'federation_index.json').exists(): r['checks']['federation_index'] = True; r['score'] += 25
        print(f"  Dropbox: {'✓' if r['checks'].get('dropbox') else '✗'} | Fed dir: {'✓' if r['checks'].get('federation_dir') else '✗'} | Synced: {r['checks'].get('synced_atoms', 0)}")
        return r

    def phase_5_performance(self):
        """Check performance metrics"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if not self.atoms_dir.exists(): return r
        index_file = self.atoms_dir / 'index.json'
        if index_file.exists():
            start = time.time(); json.load(open(index_file)); load_time = (time.time() - start) * 1000
            r['checks']['index_load_ms'] = round(load_time, 2)
            r['score'] += 50 if load_time < 100 else 30 if load_time < 500 else 0
            if load_time >= 500: r['issues'].append(f"Slow index load: {load_time}ms")
        total_size, file_count = 0, 0
        for f in self.atoms_dir.rglob('*'):
            if f.is_file(): total_size += f.stat().st_size; file_count += 1
        r['checks']['disk_mb'] = round(total_size / (1024*1024), 2); r['checks']['file_count'] = file_count
        r['score'] += 50 if total_size < 50*1024*1024 else 30 if total_size < 200*1024*1024 else 0
        if total_size >= 200*1024*1024: r['issues'].append(f"Large disk: {r['checks']['disk_mb']}MB")
        print(f"  Index load: {r['checks'].get('index_load_ms', 'N/A')}ms | Disk: {r['checks']['disk_mb']}MB | Files: {r['checks']['file_count']}")
        return r

    def phase_6_coverage(self):
        """Analyze what's being indexed and what's missed"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        expected_dirs = [self.home / '100X_DEPLOYMENT', self.home / '.consciousness', self.home / '.trinity']
        covered = sum(1 for d in expected_dirs if d.exists()); r['checks']['covered_dirs'] = f"{covered}/{len(expected_dirs)}"
        r['score'] += (covered / len(expected_dirs)) * 50
        expected_types = ['.md', '.txt', '.py', '.js', '.html', '.json']; r['checks']['indexed_types'] = expected_types; r['score'] += 30
        desktop = self.home / 'Desktop'
        if desktop.exists():
            desktop_files = len(list(desktop.glob('*.md'))) + len(list(desktop.glob('*.txt'))); r['checks']['desktop_files'] = desktop_files
            if desktop_files > 0: r['score'] += 20
        print(f"  Dirs: {r['checks']['covered_dirs']} | Types: {', '.join(expected_types)} | Desktop: {r['checks'].get('desktop_files', 0)}")
        return r

    def phase_7_duplication(self):
        """Check for duplicate data"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if not self.atoms_dir.exists(): return r
        atom_files = sorted(self.atoms_dir.glob('atoms_*.json'))
        if not atom_files: return r
        try:
            atoms = json.load(open(atom_files[-1])); paths = [a.get('path', '') for a in atoms]; unique_paths = set(paths)
            dup_count = len(paths) - len(unique_paths)
            r['checks'] = {'total_atoms': len(atoms), 'unique_paths': len(unique_paths), 'duplicates': dup_count}
            r['score'] = 100 if dup_count == 0 else 80 if dup_count < 10 else 60 if dup_count < 50 else 40
            if dup_count >= 10: r['issues'].append(f"{'High ' if dup_count >= 50 else ''}duplication: {dup_count} entries")
        except Exception as e: r['issues'].append(f"Failed to check duplicates: {e}")
        print(f"  Atoms: {r['checks'].get('total_atoms', 0)} | Unique: {r['checks'].get('unique_paths', 0)} | Dups: {r['checks'].get('duplicates', 0)}")
        return r

    def phase_8_types(self):
        """Check type distribution balance"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        index_file = self.atoms_dir / 'index.json' if self.atoms_dir.exists() else None
        if not index_file or not index_file.exists(): return r
        try:
            index = json.load(open(index_file)); types = index.get('atoms_by_type', {}); total = sum(types.values())
            r['checks'] = {'type_breakdown': types, 'total': total}
            r['score'] += 50 if len(types) >= 5 else 30 if len(types) >= 3 else 0
            if types:
                max_pct = max(types.values()) / total * 100
                r['score'] += 50 if max_pct < 50 else 30 if max_pct < 70 else 10
                if max_pct >= 70: r['issues'].append(f"Imbalanced: largest is {max_pct:.0f}%")
            print("  Types: " + " | ".join(f"{t}:{c}" for t, c in sorted(types.items(), key=lambda x: x[1], reverse=True)[:5]))
        except Exception as e: r['issues'].append(f"Failed to check types: {e}")
        return r

    def phase_9_growth(self):
        """Analyze growth velocity over time"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        if not self.atoms_dir.exists(): return r
        atom_files = sorted(self.atoms_dir.glob('atoms_*.json'))
        if len(atom_files) < 2:
            r['checks']['history_days'] = len(atom_files); r['score'] = 50 if atom_files else 0
            print(f"  History: {len(atom_files)} day(s)"); return r
        try:
            first, last = json.load(open(atom_files[0])), json.load(open(atom_files[-1]))
            growth, days = len(last) - len(first), len(atom_files); daily = growth / days if days > 0 else 0
            r['checks'] = {'first_count': len(first), 'last_count': len(last), 'total_growth': growth, 'daily_avg': round(daily, 1), 'history_days': days}
            r['score'] = 100 if daily > 10 else 70 if daily > 0 else 50 if daily == 0 else 30
            if daily <= 0: r['issues'].append("No growth" if daily == 0 else "Negative growth")
            print(f"  History: {days}d | First: {len(first)} | Latest: {len(last)} | Growth: {growth} ({daily:.1f}/day)")
        except Exception as e: r['issues'].append(f"Failed to analyze growth: {e}")
        return r

    def phase_10_errors(self):
        """Analyze historical errors"""
        r = {'score': 100, 'checks': {}, 'issues': []}
        error_files = []
        for pattern in ['error', 'failed', 'exception']:
            error_files.extend(self.deployment.glob(f'*{pattern}*.log')); error_files.extend(self.deployment.glob(f'*{pattern}*.txt'))
        r['checks']['error_files'] = len(error_files)
        rake_status = self.home / '.consciousness' / 'autonomous_rake_status.json'
        if rake_status.exists():
            try:
                status = json.load(open(rake_status)); r['checks']['daemon_cycles'] = status.get('cycles_completed', 0)
                errors = status.get('errors', 0); r['checks']['daemon_errors'] = errors
                if errors > 0: r['score'] -= min(50, errors * 5); r['issues'].append(f"Daemon has {errors} errors")
            except: pass
        r['score'] = max(0, r['score'])
        print(f"  Error files: {len(error_files)} | Daemon cycles: {r['checks'].get('daemon_cycles', 'N/A')} | Errors: {r['checks'].get('daemon_errors', 0)}")
        return r

    def phase_11_api(self):
        """Check API endpoints"""
        r = {'score': 0, 'checks': {}, 'issues': []}
        api_files = ['CYCLOTRON_SEARCH.py', 'CYCLOTRON_CLOUD_HOSTED_API.py']
        found = [api for api in api_files if (self.deployment / api).exists()]
        r['checks']['api_files'] = found; r['score'] = (len(found) / len(api_files)) * 100 if api_files else 50
        if (self.deployment / 'CYCLOTRON_SEARCH.html').exists(): r['checks']['search_ui'] = True; r['score'] = min(100, r['score'] + 20)
        print(f"  API: {', '.join(found) if found else 'None'} | Search UI: {'✓' if r['checks'].get('search_ui') else '✗'}")
        return r

    def phase_12_security(self):
        """Security audit"""
        r = {'score': 100, 'checks': {}, 'issues': []}
        if self.atoms_dir.exists():
            for af in list(self.atoms_dir.glob('*.json'))[:5]:
                try:
                    content = af.read_text()
                    if 'sk-ant-' in content or 'api_key' in content.lower():
                        r['score'] -= 30; r['issues'].append(f"Potential API key in {af.name}"); break
                except: pass
        r['checks']['atoms_readable'] = self.atoms_dir.exists() and os.access(self.atoms_dir, os.R_OK)
        r['score'] = max(0, r['score'])
        print(f"  Atoms readable: {'✓' if r['checks']['atoms_readable'] else '✗'}" + (f" | Issues: {len(r['issues'])}" if r['issues'] else ""))
        return r

    def phase_13_optimization(self):
        """Generate optimization recommendations"""
        result = {'score': 50, 'checks': {}, 'issues': [], 'recommendations': []}

        # Based on previous phases, generate recommendations

        # Check if federation is set up
        if not self.federation or not self.federation.exists():
            result['recommendations'].append("Set up Dropbox federation for multi-computer sync")

        # Check index freshness
        index_file = self.atoms_dir / 'index.json' if self.atoms_dir.exists() else None
        if index_file and index_file.exists():
            age = time.time() - index_file.stat().st_mtime
            if age > 600:  # 10 minutes
                result['recommendations'].append("Index is stale - verify daemon is running")

        # Check for search UI
        if not (self.deployment / 'CYCLOTRON_SEARCH.html').exists():
            result['recommendations'].append("Add search UI for easy querying")

        # Check analytics
        analytics_report = self.deployment / 'CYCLOTRON_ANALYTICS_REPORT.json'
        if not analytics_report.exists():
            result['recommendations'].append("Run analytics engine for detailed insights")

        result['checks']['recommendations'] = len(result['recommendations'])
        result['score'] = 100 - (len(result['recommendations']) * 10)
        result['score'] = max(50, result['score'])

        print("  Recommendations:")
        for rec in result['recommendations']:
            print(f"    → {rec}")
            self.results['recommendations'].append(rec)

        if not result['recommendations']:
            print("    All optimizations complete!")

        return result

    def generate_recommendations(self):
        """Generate final recommendations based on all phases"""
        scores = [(name, phase.get('score', 0)) for name, phase in self.results['phases'].items()]

        # Add recommendations for low-scoring phases
        for name, score in scores:
            if score < 50:
                self.results['recommendations'].append(f"Critical: Fix {name} (score: {score})")
            elif score < 70:
                self.results['recommendations'].append(f"Improve: {name} (score: {score})")

    def print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("AUDIT SUMMARY")
        print("=" * 70)

        overall = self.results['overall_score']

        if overall >= 80:
            status = "EXCELLENT"
            icon = ""
        elif overall >= 60:
            status = "GOOD"
            icon = ""
        elif overall >= 40:
            status = "NEEDS WORK"
            icon = "⚠️"
        else:
            status = "CRITICAL"
            icon = ""

        print(f"\n{icon} OVERALL SCORE: {overall}/100 [{status}]")

        print("\nPhase Scores:")
        for name, phase in self.results['phases'].items():
            score = int(phase.get('score', 0))
            bar = '█' * (score // 10) + '░' * (10 - score // 10)
            print(f"  {name:30} [{bar}] {score}")

        if self.results['critical_issues']:
            print(f"\nCritical Issues: {len(self.results['critical_issues'])}")
            for issue in self.results['critical_issues'][:5]:
                print(f"  - {issue}")

        if self.results['recommendations']:
            print(f"\nTop Recommendations:")
            for rec in self.results['recommendations'][:5]:
                print(f"  → {rec}")

    def save_results(self):
        """Save audit results to file"""
        output_file = self.deployment / 'CYCLOTRON_AUDIT_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {output_file}")

        # Also save readable summary
        summary_file = self.deployment / 'CYCLOTRON_AUDIT_SUMMARY.md'
        with open(summary_file, 'w') as f:
            f.write(f"# Cyclotron 13-Phase Audit Results\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Overall Score:** {self.results['overall_score']}/100\n\n")

            f.write("## Phase Scores\n\n")
            for name, phase in self.results['phases'].items():
                score = phase.get('score', 0)
                f.write(f"- {name}: {score}/100\n")

            if self.results['critical_issues']:
                f.write("\n## Critical Issues\n\n")
                for issue in self.results['critical_issues']:
                    f.write(f"- {issue}\n")

            if self.results['recommendations']:
                f.write("\n## Recommendations\n\n")
                for rec in self.results['recommendations']:
                    f.write(f"- {rec}\n")

        print(f"Summary saved to: {summary_file}")


def main():
    """Run the 13-phase audit"""
    auditor = CyclotronAuditor()
    auditor.run_full_audit()


if __name__ == '__main__':
    main()
