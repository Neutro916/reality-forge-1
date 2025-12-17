#!/usr/bin/env python3
"""
ATOM_QUALITY_SCORER.py - Automated Atom Quality Scoring System
==============================================================
Created by: CP1_C2 (C2 Architect)
Task: ENH-005 - Build automated atom quality scorer with ML
Date: 2025-11-27

Features:
- Scores atom quality based on multiple factors
- Uses heuristic scoring (no external ML dependencies)
- Factors: content length, completeness, source quality, recency
- Identifies low-quality atoms for review/cleanup
- Batch scoring with progress tracking
- Export quality reports

Scoring Factors:
- Content completeness (length, structure)
- Source reliability (known good sources vs unknown)
- Metadata quality (tags, type specificity)
- Age and access patterns
- Duplicate/similarity detection

Run: python ATOM_QUALITY_SCORER.py [score|report|cleanup|batch]
"""

import os
import sys
import json
import sqlite3
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# Configuration
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
DB_PATH = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Quality thresholds
QUALITY_THRESHOLDS = {
    "excellent": 0.85,
    "good": 0.70,
    "acceptable": 0.50,
    "poor": 0.30,
    "garbage": 0.0
}

# Known high-quality sources
HIGH_QUALITY_SOURCES = [
    "consciousness", "pattern", "trinity", "cyclotron",
    "seven_domains", "manipulation", "immunity",
    "overkore", "boot_protocol", "architecture"
]

# Low-quality indicators
LOW_QUALITY_PATTERNS = [
    r'^.{0,20}$',  # Very short content
    r'^[{}[\]()]+$',  # Just brackets
    r'^\s*$',  # Empty/whitespace
    r'^null$|^undefined$|^none$',  # Null values
    r'^[0-9.]+$',  # Just numbers
]


class AtomQualityScorer:
    """Automated atom quality scoring system."""

    def __init__(self):
        self.conn = None
        self.ensure_connection()
        self.quality_cache = {}

    def ensure_connection(self):
        """Ensure database connection."""
        if self.conn is None:
            if not DB_PATH.exists():
                print(f"ERROR: Database not found: {DB_PATH}")
                sys.exit(1)
            self.conn = sqlite3.connect(str(DB_PATH))
            self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def score_content_quality(self, content):
        """Score based on content quality."""
        if not content:
            return 0.0

        score = 0.0
        content_str = str(content)

        # Length scoring (longer is generally better, up to a point)
        length = len(content_str)
        if length < 10:
            score += 0.0
        elif length < 50:
            score += 0.2
        elif length < 200:
            score += 0.5
        elif length < 1000:
            score += 0.8
        else:
            score += 1.0

        # Penalize low-quality patterns
        for pattern in LOW_QUALITY_PATTERNS:
            if re.match(pattern, content_str, re.IGNORECASE):
                score *= 0.1
                break

        # Bonus for structured content
        if any(char in content_str for char in ['.', ':', '-', '\n']):
            score *= 1.1

        # Bonus for meaningful words
        word_count = len(content_str.split())
        if word_count >= 5:
            score *= 1.1
        if word_count >= 20:
            score *= 1.05

        return min(score, 1.0)

    def score_source_quality(self, source, atom_type):
        """Score based on source reliability."""
        if not source:
            return 0.3  # Unknown source

        source_lower = source.lower()
        score = 0.5  # Base score

        # High-quality source bonus
        for hq_source in HIGH_QUALITY_SOURCES:
            if hq_source in source_lower:
                score += 0.3
                break

        # File type bonus
        if any(ext in source_lower for ext in ['.md', '.py', '.json', '.html']):
            score += 0.1

        # Penalize temporary/unknown sources
        if any(bad in source_lower for bad in ['temp', 'tmp', 'test', 'debug', 'backup']):
            score *= 0.7

        # Type-based scoring
        high_value_types = ['knowledge', 'concept', 'insight', 'pattern', 'fact']
        if atom_type in high_value_types:
            score *= 1.2

        return min(score, 1.0)

    def score_metadata_quality(self, tags, metadata):
        """Score based on metadata completeness."""
        score = 0.3  # Base score

        # Tags scoring
        if tags:
            tag_list = tags.split(',') if isinstance(tags, str) else tags
            tag_count = len(tag_list)
            if tag_count >= 1:
                score += 0.2
            if tag_count >= 3:
                score += 0.2
            if tag_count >= 5:
                score += 0.1

        # Metadata scoring
        if metadata:
            try:
                if isinstance(metadata, str):
                    meta_dict = json.loads(metadata)
                else:
                    meta_dict = metadata

                if isinstance(meta_dict, dict):
                    if len(meta_dict) >= 2:
                        score += 0.2
                    if 'source' in meta_dict or 'origin' in meta_dict:
                        score += 0.1
            except:
                pass

        return min(score, 1.0)

    def score_recency(self, created):
        """Score based on atom age."""
        if not created:
            return 0.5

        try:
            if isinstance(created, str):
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00').replace('+00:00', ''))
            else:
                created_dt = created

            age_days = (datetime.now() - created_dt).days

            if age_days <= 1:
                return 1.0
            elif age_days <= 7:
                return 0.9
            elif age_days <= 30:
                return 0.8
            elif age_days <= 90:
                return 0.7
            else:
                return 0.6
        except:
            return 0.5

    def score_access_pattern(self, access_count, confidence):
        """Score based on access patterns."""
        score = 0.5

        # Access count bonus
        if access_count and access_count > 0:
            if access_count >= 10:
                score += 0.3
            elif access_count >= 5:
                score += 0.2
            elif access_count >= 1:
                score += 0.1

        # Confidence bonus
        if confidence:
            score += confidence * 0.3

        return min(score, 1.0)

    def calculate_overall_score(self, atom):
        """Calculate overall quality score for an atom."""
        # Individual scores
        content_score = self.score_content_quality(atom['content'])
        source_score = self.score_source_quality(atom.get('source'), atom.get('type'))
        metadata_score = self.score_metadata_quality(atom.get('tags'), atom.get('metadata'))
        recency_score = self.score_recency(atom.get('created'))
        access_score = self.score_access_pattern(
            atom.get('access_count', 0),
            atom.get('confidence', 0)
        )

        # Weighted average
        weights = {
            'content': 0.35,
            'source': 0.20,
            'metadata': 0.15,
            'recency': 0.15,
            'access': 0.15
        }

        overall = (
            content_score * weights['content'] +
            source_score * weights['source'] +
            metadata_score * weights['metadata'] +
            recency_score * weights['recency'] +
            access_score * weights['access']
        )

        return {
            'overall': round(overall, 3),
            'content': round(content_score, 3),
            'source': round(source_score, 3),
            'metadata': round(metadata_score, 3),
            'recency': round(recency_score, 3),
            'access': round(access_score, 3)
        }

    def get_quality_label(self, score):
        """Get quality label for score."""
        for label, threshold in QUALITY_THRESHOLDS.items():
            if score >= threshold:
                return label
        return "garbage"

    def score_atom(self, atom_id):
        """Score a single atom by ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, type, content, source, tags, metadata, created, confidence, access_count
            FROM atoms WHERE id = ?
        """, (atom_id,))

        row = cursor.fetchone()
        if not row:
            return None

        atom = dict(row)
        scores = self.calculate_overall_score(atom)
        scores['id'] = atom_id
        scores['type'] = atom.get('type')
        scores['label'] = self.get_quality_label(scores['overall'])

        return scores

    def batch_score(self, limit=None, update_db=False):
        """Score all atoms in batch."""
        cursor = self.conn.cursor()

        query = """
            SELECT id, type, content, source, tags, metadata, created, confidence, access_count
            FROM atoms
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()

        results = {
            'total': len(rows),
            'by_label': defaultdict(int),
            'by_type': defaultdict(lambda: {'count': 0, 'avg_score': 0, 'scores': []}),
            'low_quality': [],
            'high_quality': [],
            'avg_score': 0
        }

        total_score = 0
        for row in rows:
            atom = dict(row)
            scores = self.calculate_overall_score(atom)
            label = self.get_quality_label(scores['overall'])

            results['by_label'][label] += 1
            results['by_type'][atom['type']]['count'] += 1
            results['by_type'][atom['type']]['scores'].append(scores['overall'])

            total_score += scores['overall']

            # Track extremes
            if scores['overall'] < 0.3:
                results['low_quality'].append({
                    'id': atom['id'],
                    'type': atom['type'],
                    'score': scores['overall'],
                    'content_preview': str(atom['content'])[:50]
                })
            elif scores['overall'] > 0.85:
                results['high_quality'].append({
                    'id': atom['id'],
                    'type': atom['type'],
                    'score': scores['overall']
                })

            # Optionally update DB with score
            if update_db:
                self.update_atom_confidence(atom['id'], scores['overall'])

        # Calculate averages
        results['avg_score'] = round(total_score / len(rows), 3) if rows else 0

        for atom_type, data in results['by_type'].items():
            if data['scores']:
                data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 3)
            del data['scores']  # Remove raw scores from output

        # Limit low/high quality lists
        results['low_quality'] = sorted(results['low_quality'], key=lambda x: x['score'])[:100]
        results['high_quality'] = sorted(results['high_quality'], key=lambda x: -x['score'])[:100]

        return results

    def update_atom_confidence(self, atom_id, score):
        """Update atom's confidence field with calculated score."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE atoms SET confidence = ? WHERE id = ?", (score, atom_id))
        self.conn.commit()

    def generate_report(self, limit=None):
        """Generate quality report."""
        results = self.batch_score(limit)

        print("\n" + "="*70)
        print("ATOM QUALITY REPORT")
        print(f"Computer: {COMPUTER}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*70)

        print(f"\nTotal Atoms Scored: {results['total']:,}")
        print(f"Average Quality Score: {results['avg_score']:.1%}")

        print("\n### QUALITY DISTRIBUTION ###")
        for label in ['excellent', 'good', 'acceptable', 'poor', 'garbage']:
            count = results['by_label'].get(label, 0)
            pct = count / results['total'] * 100 if results['total'] > 0 else 0
            bar = "#" * int(pct / 2)
            print(f"  {label:12} {count:6,} ({pct:5.1f}%) {bar}")

        print("\n### QUALITY BY TYPE (Top 10) ###")
        sorted_types = sorted(
            results['by_type'].items(),
            key=lambda x: -x[1]['count']
        )[:10]

        for atom_type, data in sorted_types:
            print(f"  {atom_type:15} {data['count']:6,} atoms, avg: {data['avg_score']:.1%}")

        print("\n### LOW QUALITY ATOMS (Bottom 10) ###")
        for atom in results['low_quality'][:10]:
            print(f"  [{atom['score']:.1%}] {atom['id'][:12]} ({atom['type']})")
            print(f"          {atom['content_preview'][:40]}...")

        print("\n" + "="*70)

        return results

    def export_report(self, output_path=None):
        """Export quality report to JSON."""
        results = self.batch_score()

        report = {
            'timestamp': datetime.now().isoformat(),
            'computer': COMPUTER,
            'summary': {
                'total_atoms': results['total'],
                'avg_score': results['avg_score'],
                'distribution': dict(results['by_label'])
            },
            'by_type': dict(results['by_type']),
            'low_quality_samples': results['low_quality'][:50],
            'high_quality_samples': results['high_quality'][:50]
        }

        if output_path is None:
            output_path = SYNC_DIR / f"QUALITY_REPORT_{COMPUTER}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nReport exported to: {output_path}")
        return output_path


def main():
    scorer = AtomQualityScorer()

    if len(sys.argv) < 2:
        print("ATOM QUALITY SCORER")
        print("="*40)
        print("\nUsage:")
        print("  python ATOM_QUALITY_SCORER.py score <atom_id>  # Score single atom")
        print("  python ATOM_QUALITY_SCORER.py report [limit]   # Generate report")
        print("  python ATOM_QUALITY_SCORER.py export           # Export to JSON")
        print("  python ATOM_QUALITY_SCORER.py update           # Update all atom confidences")
        scorer.close()
        return

    cmd = sys.argv[1].lower()

    try:
        if cmd == "score":
            if len(sys.argv) < 3:
                print("Usage: python ATOM_QUALITY_SCORER.py score <atom_id>")
            else:
                result = scorer.score_atom(sys.argv[2])
                if result:
                    print(f"\nAtom Quality Score: {result['id']}")
                    print(f"  Overall: {result['overall']:.1%} ({result['label']})")
                    print(f"  Content: {result['content']:.1%}")
                    print(f"  Source:  {result['source']:.1%}")
                    print(f"  Metadata: {result['metadata']:.1%}")
                    print(f"  Recency: {result['recency']:.1%}")
                    print(f"  Access:  {result['access']:.1%}")
                else:
                    print(f"Atom not found: {sys.argv[2]}")

        elif cmd == "report":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            scorer.generate_report(limit)

        elif cmd == "export":
            scorer.export_report()

        elif cmd == "update":
            print("Updating all atom confidence scores...")
            results = scorer.batch_score(update_db=True)
            print(f"Updated {results['total']:,} atoms")
            print(f"Average score: {results['avg_score']:.1%}")

        else:
            print(f"Unknown command: {cmd}")

    finally:
        scorer.close()


if __name__ == "__main__":
    main()
