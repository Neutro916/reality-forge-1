"""
CYCLOTRON ANALYTICS ENGINE
Comprehensive metrics and analytics for the knowledge dino

Tracks:
- Atom growth over time
- Source type distribution
- File type breakdown
- Growth velocity
- Disk usage
- Federation health
- Performance metrics
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

class CyclotronAnalytics:
    """Analytics engine for Cyclotron knowledge base"""

    def __init__(self):
        self.home = Path.home()
        self.dropbox = self.home / 'Dropbox'
        self.federation = self.dropbox / '.cyclotron_federation'
        self.deployment = self.home / '100X_DEPLOYMENT'

        print("📊 CYCLOTRON ANALYTICS ENGINE")
        print("=" * 60)
        print()

    def load_atoms(self):
        """Load all atoms from federation"""
        atoms_dir = self.federation / 'atoms'
        all_atoms = []

        if atoms_dir.exists():
            for atom_file in atoms_dir.glob('*_atoms.json'):
                try:
                    with open(atom_file) as f:
                        atoms = json.load(f)
                        all_atoms.extend(atoms)
                except:
                    pass

        return all_atoms

    def get_basic_stats(self, atoms):
        """Basic statistics"""
        return {
            'total_atoms': len(atoms),
            'total_size_bytes': sum(a.get('size', 0) for a in atoms),
            'avg_atom_size': sum(a.get('size', 0) for a in atoms) / len(atoms) if atoms else 0,
            'computers': list(set(a.get('computer_id', 'unknown') for a in atoms))
        }

    def get_source_breakdown(self, atoms):
        """Breakdown by source type"""
        sources = Counter(a.get('source_type', 'unknown') for a in atoms)
        return dict(sources.most_common())

    def get_file_type_breakdown(self, atoms):
        """Breakdown by file extension"""
        extensions = []
        for atom in atoms:
            filename = atom.get('file_name', '')
            if '.' in filename:
                ext = '.' + filename.split('.')[-1].lower()
                extensions.append(ext)
            else:
                extensions.append('(no ext)')

        return dict(Counter(extensions).most_common())

    def get_size_distribution(self, atoms):
        """Size distribution of atoms"""
        sizes = {
            'tiny (< 1KB)': 0,
            'small (1-10KB)': 0,
            'medium (10-50KB)': 0,
            'large (50-100KB)': 0,
            'huge (> 100KB)': 0
        }

        for atom in atoms:
            size = atom.get('size', 0)
            if size < 1000:
                sizes['tiny (< 1KB)'] += 1
            elif size < 10000:
                sizes['small (1-10KB)'] += 1
            elif size < 50000:
                sizes['medium (10-50KB)'] += 1
            elif size < 100000:
                sizes['large (50-100KB)'] += 1
            else:
                sizes['huge (> 100KB)'] += 1

        return sizes

    def get_recent_atoms(self, atoms, count=10):
        """Get most recently added atoms"""
        sorted_atoms = sorted(atoms,
            key=lambda x: x.get('timestamp', ''),
            reverse=True)

        return [{
            'file': a.get('file_name', 'unknown'),
            'type': a.get('source_type', 'unknown'),
            'size': a.get('size', 0),
            'time': a.get('timestamp', '')[:19]
        } for a in sorted_atoms[:count]]

    def get_largest_atoms(self, atoms, count=10):
        """Get largest atoms"""
        sorted_atoms = sorted(atoms,
            key=lambda x: x.get('size', 0),
            reverse=True)

        return [{
            'file': a.get('file_name', 'unknown'),
            'type': a.get('source_type', 'unknown'),
            'size': a.get('size', 0),
            'size_kb': round(a.get('size', 0) / 1024, 2)
        } for a in sorted_atoms[:count]]

    def get_federation_health(self):
        """Check federation health"""
        health = {
            'dropbox_exists': self.dropbox.exists(),
            'federation_exists': self.federation.exists(),
            'atoms_dir_exists': (self.federation / 'atoms').exists(),
            'indices_dir_exists': (self.federation / 'indices').exists(),
            'index_file_exists': (self.federation / 'indices' / 'federation_index.json').exists()
        }

        health['overall_score'] = sum(health.values()) / len(health) * 100

        return health

    def get_disk_usage(self):
        """Get disk usage for Cyclotron"""
        total_size = 0
        file_count = 0

        if self.federation.exists():
            for f in self.federation.rglob('*'):
                if f.is_file():
                    total_size += f.stat().st_size
                    file_count += 1

        return {
            'total_bytes': total_size,
            'total_kb': round(total_size / 1024, 2),
            'total_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count
        }

    def generate_full_report(self):
        """Generate comprehensive analytics report"""

        print("🔍 Loading atoms...")
        atoms = self.load_atoms()

        if not atoms:
            print("⚠️  No atoms found in federation!")
            return

        print(f"✅ Loaded {len(atoms)} atoms")
        print()

        # Basic stats
        basic = self.get_basic_stats(atoms)
        print("=" * 60)
        print("📊 BASIC STATISTICS")
        print("=" * 60)
        print(f"Total Atoms: {basic['total_atoms']}")
        print(f"Total Size: {basic['total_size_bytes']:,} bytes ({round(basic['total_size_bytes']/1024/1024, 2)} MB)")
        print(f"Average Atom: {round(basic['avg_atom_size'])} bytes")
        print(f"Computers: {', '.join(basic['computers'])}")
        print()

        # Source breakdown
        sources = self.get_source_breakdown(atoms)
        print("=" * 60)
        print("🗂️  SOURCE TYPE BREAKDOWN")
        print("=" * 60)
        for source, count in sources.items():
            pct = round(count / len(atoms) * 100, 1)
            bar = '█' * int(pct / 5)
            print(f"{source:20} {count:5} ({pct:5.1f}%) {bar}")
        print()

        # File type breakdown
        file_types = self.get_file_type_breakdown(atoms)
        print("=" * 60)
        print("📁 FILE TYPE BREAKDOWN")
        print("=" * 60)
        for ext, count in list(file_types.items())[:10]:
            pct = round(count / len(atoms) * 100, 1)
            bar = '█' * int(pct / 5)
            print(f"{ext:20} {count:5} ({pct:5.1f}%) {bar}")
        print()

        # Size distribution
        sizes = self.get_size_distribution(atoms)
        print("=" * 60)
        print("📏 SIZE DISTRIBUTION")
        print("=" * 60)
        for size_cat, count in sizes.items():
            pct = round(count / len(atoms) * 100, 1)
            bar = '█' * int(pct / 5)
            print(f"{size_cat:20} {count:5} ({pct:5.1f}%) {bar}")
        print()

        # Recent atoms
        recent = self.get_recent_atoms(atoms)
        print("=" * 60)
        print("🕐 MOST RECENT ATOMS")
        print("=" * 60)
        for i, atom in enumerate(recent, 1):
            print(f"{i}. {atom['file'][:40]:40} [{atom['type']:15}] {atom['size']:,} bytes")
        print()

        # Largest atoms
        largest = self.get_largest_atoms(atoms)
        print("=" * 60)
        print("🐘 LARGEST ATOMS")
        print("=" * 60)
        for i, atom in enumerate(largest, 1):
            print(f"{i}. {atom['file'][:40]:40} [{atom['type']:15}] {atom['size_kb']} KB")
        print()

        # Federation health
        health = self.get_federation_health()
        print("=" * 60)
        print("💚 FEDERATION HEALTH")
        print("=" * 60)
        for check, status in health.items():
            if check != 'overall_score':
                icon = '✅' if status else '❌'
                print(f"{icon} {check}")
        print(f"\n🏥 Overall Health: {health['overall_score']:.0f}%")
        print()

        # Disk usage
        disk = self.get_disk_usage()
        print("=" * 60)
        print("💾 DISK USAGE")
        print("=" * 60)
        print(f"Total Size: {disk['total_mb']} MB")
        print(f"File Count: {disk['file_count']}")
        print()

        # Save analytics to JSON
        analytics = {
            'generated_at': datetime.now().isoformat(),
            'basic_stats': basic,
            'source_breakdown': sources,
            'file_types': file_types,
            'size_distribution': sizes,
            'federation_health': health,
            'disk_usage': disk,
            'recent_atoms': recent,
            'largest_atoms': largest
        }

        analytics_file = self.deployment / 'CYCLOTRON_ANALYTICS_REPORT.json'
        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)

        print("=" * 60)
        print(f"📊 Full analytics saved to: {analytics_file}")
        print("=" * 60)
        print()

        return analytics


def main():
    """Run full analytics"""
    analytics = CyclotronAnalytics()
    analytics.generate_full_report()


if __name__ == '__main__':
    main()
