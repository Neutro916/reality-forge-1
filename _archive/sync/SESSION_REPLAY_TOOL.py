#!/usr/bin/env python3
"""
SESSION_REPLAY_TOOL.py - Reconstruct Work Sessions from Atoms
=============================================================
Created by: CP1_C2 (C2 Architect)
Task: ENH-007 - Build session replay tool
Date: 2025-11-27

Features:
- Reconstructs work sessions from atom timestamps
- Groups atoms by session (time-based clustering)
- Shows session timeline with key activities
- Identifies session patterns and productivity metrics
- Exports session reports for review

Usage:
  python SESSION_REPLAY_TOOL.py list          # List recent sessions
  python SESSION_REPLAY_TOOL.py replay <date> # Replay specific date
  python SESSION_REPLAY_TOOL.py today         # Today's session
  python SESSION_REPLAY_TOOL.py stats         # Session statistics
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
DB_PATH = CONSCIOUSNESS / 'cyclotron_core' / 'atoms.db'
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Session gap threshold (minutes) - atoms more than this apart = new session
SESSION_GAP_MINUTES = 30


class SessionReplayTool:
    """Tool for reconstructing and analyzing work sessions from atoms."""

    def __init__(self):
        self.conn = None
        self.ensure_connection()

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

    def get_atoms_for_date(self, date_str):
        """Get all atoms created on a specific date."""
        cursor = self.conn.cursor()

        # Parse date
        if date_str.lower() == 'today':
            target_date = datetime.now().strftime('%Y-%m-%d')
        elif date_str.lower() == 'yesterday':
            target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            target_date = date_str

        cursor.execute("""
            SELECT id, type, content, source, tags, created, confidence
            FROM atoms
            WHERE DATE(created) = ?
            ORDER BY created ASC
        """, (target_date,))

        return cursor.fetchall()

    def get_atoms_in_range(self, start_date, end_date):
        """Get atoms in a date range."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, type, content, source, tags, created, confidence
            FROM atoms
            WHERE DATE(created) BETWEEN ? AND ?
            ORDER BY created ASC
        """, (start_date, end_date))
        return cursor.fetchall()

    def cluster_into_sessions(self, atoms):
        """Cluster atoms into sessions based on time gaps."""
        if not atoms:
            return []

        sessions = []
        current_session = {
            "start": None,
            "end": None,
            "atoms": [],
            "types": defaultdict(int),
            "sources": set()
        }

        for atom in atoms:
            created = datetime.fromisoformat(atom['created'].replace('Z', '+00:00').replace('+00:00', ''))

            if current_session["start"] is None:
                # First atom
                current_session["start"] = created
                current_session["end"] = created
                current_session["atoms"].append(atom)
                current_session["types"][atom['type']] += 1
                if atom['source']:
                    current_session["sources"].add(atom['source'][:50])
            else:
                # Check time gap
                gap = (created - current_session["end"]).total_seconds() / 60

                if gap > SESSION_GAP_MINUTES:
                    # New session
                    sessions.append(current_session)
                    current_session = {
                        "start": created,
                        "end": created,
                        "atoms": [atom],
                        "types": defaultdict(int, {atom['type']: 1}),
                        "sources": {atom['source'][:50]} if atom['source'] else set()
                    }
                else:
                    # Same session
                    current_session["end"] = created
                    current_session["atoms"].append(atom)
                    current_session["types"][atom['type']] += 1
                    if atom['source']:
                        current_session["sources"].add(atom['source'][:50])

        # Don't forget last session
        if current_session["atoms"]:
            sessions.append(current_session)

        return sessions

    def format_duration(self, start, end):
        """Format session duration."""
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def get_session_summary(self, session):
        """Generate summary for a session."""
        # Get first few atoms as preview
        preview_atoms = session["atoms"][:3]
        previews = []

        for atom in preview_atoms:
            content = atom['content']
            if len(content) > 80:
                content = content[:77] + "..."
            previews.append(f"  - [{atom['type']}] {content}")

        return "\n".join(previews)

    def replay_date(self, date_str):
        """Replay a day's work sessions."""
        atoms = self.get_atoms_for_date(date_str)

        if not atoms:
            print(f"\nNo atoms found for {date_str}")
            return

        sessions = self.cluster_into_sessions(atoms)

        print("\n" + "="*70)
        print(f"SESSION REPLAY: {date_str}")
        print(f"Computer: {COMPUTER}")
        print("="*70)
        print(f"\nTotal atoms: {len(atoms)}")
        print(f"Sessions identified: {len(sessions)}")

        for i, session in enumerate(sessions, 1):
            duration = self.format_duration(session["start"], session["end"])
            atom_count = len(session["atoms"])

            print(f"\n{'─'*70}")
            print(f"SESSION {i}: {session['start'].strftime('%H:%M')} - {session['end'].strftime('%H:%M')} ({duration})")
            print(f"{'─'*70}")
            print(f"  Atoms: {atom_count}")
            print(f"  Types: {dict(session['types'])}")

            if session["sources"]:
                print(f"  Sources: {', '.join(list(session['sources'])[:5])}")

            print(f"\n  Preview:")
            print(self.get_session_summary(session))

        # Session statistics
        print(f"\n{'='*70}")
        print("SESSION STATISTICS")
        print(f"{'='*70}")

        total_duration = sum(
            (s["end"] - s["start"]).seconds for s in sessions
        )
        avg_session_duration = total_duration / len(sessions) if sessions else 0
        atoms_per_hour = len(atoms) / (total_duration / 3600) if total_duration > 0 else 0

        print(f"  Total active time: {total_duration // 3600}h {(total_duration % 3600) // 60}m")
        print(f"  Avg session length: {avg_session_duration // 60:.0f}m")
        print(f"  Atoms per hour: {atoms_per_hour:.1f}")

        # Type breakdown
        all_types = defaultdict(int)
        for session in sessions:
            for t, count in session["types"].items():
                all_types[t] += count

        print(f"\n  Atom types:")
        for t, count in sorted(all_types.items(), key=lambda x: -x[1])[:10]:
            pct = count / len(atoms) * 100
            print(f"    {t}: {count} ({pct:.1f}%)")

    def list_recent_sessions(self, days=7):
        """List sessions from recent days."""
        print("\n" + "="*70)
        print(f"RECENT SESSIONS (Last {days} days)")
        print("="*70)

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            atoms = self.get_atoms_for_date(date)

            if not atoms:
                continue

            sessions = self.cluster_into_sessions(atoms)

            day_name = "Today" if i == 0 else "Yesterday" if i == 1 else date
            total_duration = sum((s["end"] - s["start"]).seconds for s in sessions)

            print(f"\n{day_name}:")
            print(f"  Sessions: {len(sessions)}")
            print(f"  Atoms: {len(atoms)}")
            print(f"  Active time: {total_duration // 3600}h {(total_duration % 3600) // 60}m")

            for j, session in enumerate(sessions, 1):
                duration = self.format_duration(session["start"], session["end"])
                print(f"    {j}. {session['start'].strftime('%H:%M')}-{session['end'].strftime('%H:%M')} ({duration}, {len(session['atoms'])} atoms)")

    def show_stats(self):
        """Show overall session statistics."""
        cursor = self.conn.cursor()

        # Get date range
        cursor.execute("SELECT MIN(DATE(created)), MAX(DATE(created)) FROM atoms")
        min_date, max_date = cursor.fetchone()

        # Get daily counts
        cursor.execute("""
            SELECT DATE(created) as day, COUNT(*) as count
            FROM atoms
            GROUP BY DATE(created)
            ORDER BY day DESC
            LIMIT 30
        """)
        daily_counts = cursor.fetchall()

        # Get type distribution
        cursor.execute("""
            SELECT type, COUNT(*) as count
            FROM atoms
            GROUP BY type
            ORDER BY count DESC
            LIMIT 15
        """)
        type_counts = cursor.fetchall()

        # Total count
        cursor.execute("SELECT COUNT(*) FROM atoms")
        total = cursor.fetchone()[0]

        print("\n" + "="*70)
        print("SESSION STATISTICS OVERVIEW")
        print("="*70)
        print(f"\nTotal atoms: {total:,}")
        print(f"Date range: {min_date} to {max_date}")
        print(f"Days with activity: {len(daily_counts)}")

        # Average per day
        if daily_counts:
            avg_per_day = sum(d['count'] for d in daily_counts) / len(daily_counts)
            max_day = max(daily_counts, key=lambda x: x['count'])
            print(f"Avg atoms/day: {avg_per_day:.1f}")
            print(f"Most productive day: {max_day['day']} ({max_day['count']} atoms)")

        print(f"\nTop atom types:")
        for t in type_counts:
            pct = t['count'] / total * 100
            bar = "#" * int(pct / 2)
            print(f"  {t['type'][:20]:20} {t['count']:6,} ({pct:5.1f}%) {bar}")

        print(f"\nRecent activity (last 7 days):")
        for d in daily_counts[:7]:
            bar = "#" * (d['count'] // 100)
            print(f"  {d['day']}: {d['count']:,} {bar}")

    def export_session(self, date_str, output_path=None):
        """Export session data to JSON."""
        atoms = self.get_atoms_for_date(date_str)
        sessions = self.cluster_into_sessions(atoms)

        export_data = {
            "date": date_str,
            "computer": COMPUTER,
            "exported_at": datetime.now().isoformat(),
            "total_atoms": len(atoms),
            "sessions": []
        }

        for i, session in enumerate(sessions):
            session_data = {
                "session_number": i + 1,
                "start": session["start"].isoformat(),
                "end": session["end"].isoformat(),
                "duration_minutes": (session["end"] - session["start"]).seconds // 60,
                "atom_count": len(session["atoms"]),
                "types": dict(session["types"]),
                "sources": list(session["sources"]),
                "atoms": [
                    {
                        "id": a['id'],
                        "type": a['type'],
                        "content": a['content'][:200],
                        "created": a['created']
                    }
                    for a in session["atoms"]
                ]
            }
            export_data["sessions"].append(session_data)

        if output_path is None:
            output_path = SYNC_DIR / f"SESSION_EXPORT_{date_str}_{COMPUTER}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\nSession exported to: {output_path}")
        return output_path


def main():
    tool = SessionReplayTool()

    if len(sys.argv) < 2:
        print("SESSION REPLAY TOOL")
        print("="*40)
        print("\nUsage:")
        print("  python SESSION_REPLAY_TOOL.py list           # List recent sessions")
        print("  python SESSION_REPLAY_TOOL.py today          # Today's session")
        print("  python SESSION_REPLAY_TOOL.py replay <date>  # Replay specific date")
        print("  python SESSION_REPLAY_TOOL.py stats          # Overall statistics")
        print("  python SESSION_REPLAY_TOOL.py export <date>  # Export session to JSON")
        print("\nExamples:")
        print("  python SESSION_REPLAY_TOOL.py replay 2025-11-27")
        print("  python SESSION_REPLAY_TOOL.py replay yesterday")
        tool.close()
        return

    cmd = sys.argv[1].lower()

    try:
        if cmd == "list":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            tool.list_recent_sessions(days)

        elif cmd == "today":
            tool.replay_date("today")

        elif cmd == "yesterday":
            tool.replay_date("yesterday")

        elif cmd == "replay":
            if len(sys.argv) < 3:
                print("Usage: python SESSION_REPLAY_TOOL.py replay <date>")
                print("  Date format: YYYY-MM-DD or 'today' or 'yesterday'")
            else:
                tool.replay_date(sys.argv[2])

        elif cmd == "stats":
            tool.show_stats()

        elif cmd == "export":
            date = sys.argv[2] if len(sys.argv) > 2 else "today"
            tool.export_session(date)

        else:
            print(f"Unknown command: {cmd}")

    finally:
        tool.close()


if __name__ == "__main__":
    main()
