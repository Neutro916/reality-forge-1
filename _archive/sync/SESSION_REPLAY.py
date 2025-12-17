#!/usr/bin/env python3
"""
SESSION_REPLAY.py - Session Replay Tool
========================================
Created by: CP2C1 (C1 MECHANIC)
Task: ENH-007 from WORK_BACKLOG

Reconstructs work sessions from atoms based on timestamps.
Shows what was done, when, and by which instance.

Usage:
    python SESSION_REPLAY.py today              # Show today's work
    python SESSION_REPLAY.py date 2025-11-27    # Show specific date
    python SESSION_REPLAY.py last 24            # Last 24 hours
    python SESSION_REPLAY.py instance CP2C1     # Filter by instance
    python SESSION_REPLAY.py timeline           # Full timeline view
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import re

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
LOCAL_DB = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")


class SessionReplay:
    """Replay work sessions from atoms."""

    def __init__(self, db_path=LOCAL_DB):
        self.db_path = db_path
        self.atoms = []

    def load_atoms_in_range(self, start_date, end_date=None):
        """Load atoms created within a date range."""
        if not self.db_path.exists():
            return []

        if end_date is None:
            end_date = datetime.now()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, type, content, source, tags, created, confidence
            FROM atoms
            WHERE created >= ? AND created <= ?
            ORDER BY created ASC
        """, (start_date.isoformat(), end_date.isoformat()))

        self.atoms = []
        for row in cursor.fetchall():
            atom_id, atom_type, content, source, tags, created, confidence = row
            self.atoms.append({
                "id": atom_id,
                "type": atom_type,
                "content": content[:500] if content else "",
                "source": source,
                "tags": tags,
                "created": created,
                "confidence": confidence or 0.5
            })

        conn.close()
        return self.atoms

    def load_today(self):
        """Load atoms from today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.load_atoms_in_range(today)

    def load_last_hours(self, hours):
        """Load atoms from last N hours."""
        start = datetime.now() - timedelta(hours=hours)
        return self.load_atoms_in_range(start)

    def load_date(self, date_str):
        """Load atoms from a specific date."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            end_date = date + timedelta(days=1)
            return self.load_atoms_in_range(date, end_date)
        except ValueError:
            print(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
            return []

    def extract_instance(self, atom):
        """Try to extract instance ID from atom content or source."""
        content = atom.get("content", "") + " " + atom.get("source", "")

        # Look for instance patterns like CP2C1, CP1C2, etc.
        match = re.search(r'(CP\d+C\d+)', content, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Look for computer name
        match = re.search(r'(DESKTOP-\w+)', content, re.IGNORECASE)
        if match:
            return match.group(1)

        return "Unknown"

    def extract_action(self, atom):
        """Extract action description from atom."""
        content = atom.get("content", "")
        atom_type = atom.get("type", "")

        # Look for action keywords
        actions = {
            "created": ["created", "built", "wrote", "generated"],
            "modified": ["modified", "updated", "edited", "fixed"],
            "deleted": ["deleted", "removed", "cleaned"],
            "deployed": ["deployed", "synced", "pushed"],
            "tested": ["tested", "verified", "checked"],
            "analyzed": ["analyzed", "scanned", "audited"]
        }

        content_lower = content.lower()
        for action, keywords in actions.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return action

        return atom_type or "activity"

    def group_by_hour(self):
        """Group atoms by hour."""
        grouped = defaultdict(list)
        for atom in self.atoms:
            try:
                created = datetime.fromisoformat(atom["created"].replace("Z", "+00:00"))
                hour_key = created.strftime("%Y-%m-%d %H:00")
                grouped[hour_key].append(atom)
            except:
                pass
        return dict(grouped)

    def group_by_instance(self):
        """Group atoms by instance."""
        grouped = defaultdict(list)
        for atom in self.atoms:
            instance = self.extract_instance(atom)
            grouped[instance].append(atom)
        return dict(grouped)

    def get_session_summary(self):
        """Get summary of loaded session."""
        if not self.atoms:
            return {}

        by_type = defaultdict(int)
        by_instance = defaultdict(int)
        by_action = defaultdict(int)

        for atom in self.atoms:
            by_type[atom.get("type", "unknown")] += 1
            by_instance[self.extract_instance(atom)] += 1
            by_action[self.extract_action(atom)] += 1

        # Get time range
        timestamps = [a.get("created", "") for a in self.atoms if a.get("created")]
        start_time = min(timestamps) if timestamps else None
        end_time = max(timestamps) if timestamps else None

        return {
            "total_atoms": len(self.atoms),
            "time_range": {"start": start_time, "end": end_time},
            "by_type": dict(by_type),
            "by_instance": dict(by_instance),
            "by_action": dict(by_action)
        }

    def generate_timeline(self):
        """Generate timeline of events."""
        timeline = []
        for atom in self.atoms:
            instance = self.extract_instance(atom)
            action = self.extract_action(atom)
            content = atom.get("content", "")[:100]

            timeline.append({
                "time": atom.get("created", "?")[:19],
                "instance": instance,
                "action": action,
                "type": atom.get("type", "?"),
                "preview": content
            })

        return timeline


def print_summary(replay):
    """Print session summary."""
    summary = replay.get_session_summary()

    print("\n" + "="*60)
    print("SESSION SUMMARY")
    print("="*60)

    if not summary:
        print("  No atoms in session.")
        return

    print(f"\nTotal Atoms: {summary['total_atoms']}")

    time_range = summary.get("time_range", {})
    if time_range.get("start"):
        print(f"Time Range: {time_range['start'][:19]} to {time_range['end'][:19]}")

    print("\nBy Type:")
    for t, count in sorted(summary["by_type"].items(), key=lambda x: -x[1])[:10]:
        print(f"  {t}: {count}")

    print("\nBy Instance:")
    for inst, count in sorted(summary["by_instance"].items(), key=lambda x: -x[1]):
        print(f"  {inst}: {count}")

    print("\nBy Action:")
    for action, count in sorted(summary["by_action"].items(), key=lambda x: -x[1]):
        print(f"  {action}: {count}")

    print("="*60)


def print_timeline(replay, limit=50):
    """Print timeline of events."""
    timeline = replay.generate_timeline()

    print("\n" + "="*60)
    print("SESSION TIMELINE")
    print("="*60)

    for event in timeline[:limit]:
        time = event["time"][11:19] if len(event["time"]) > 11 else event["time"]
        instance = event["instance"][:10]
        action = event["action"][:10]
        preview = event["preview"][:40]

        print(f"\n[{time}] {instance}")
        print(f"  Action: {action} ({event['type']})")
        print(f"  {preview}...")

    if len(timeline) > limit:
        print(f"\n... and {len(timeline) - limit} more events")

    print("\n" + "="*60)


def print_hourly(replay):
    """Print hourly breakdown."""
    by_hour = replay.group_by_hour()

    print("\n" + "="*60)
    print("HOURLY BREAKDOWN")
    print("="*60)

    for hour, atoms in sorted(by_hour.items()):
        print(f"\n{hour} ({len(atoms)} atoms)")
        for atom in atoms[:3]:
            preview = atom.get("content", "")[:50]
            print(f"  - {atom.get('type', '?')}: {preview}...")
        if len(atoms) > 3:
            print(f"  ... and {len(atoms) - 3} more")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Session Replay Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Today command
    subparsers.add_parser("today", help="Show today's work")

    # Date command
    date_parser = subparsers.add_parser("date", help="Show specific date")
    date_parser.add_argument("date_str", help="Date in YYYY-MM-DD format")

    # Last N hours
    last_parser = subparsers.add_parser("last", help="Show last N hours")
    last_parser.add_argument("hours", type=int, help="Number of hours")

    # Timeline
    timeline_parser = subparsers.add_parser("timeline", help="Show timeline view")
    timeline_parser.add_argument("--limit", "-l", type=int, default=50)

    # Hourly
    subparsers.add_parser("hourly", help="Show hourly breakdown")

    # Instance filter
    instance_parser = subparsers.add_parser("instance", help="Filter by instance")
    instance_parser.add_argument("instance_id", help="Instance ID (e.g., CP2C1)")

    # Summary
    subparsers.add_parser("summary", help="Show summary only")

    args = parser.parse_args()

    replay = SessionReplay()

    if args.command == "today":
        replay.load_today()
        print_summary(replay)
        print_hourly(replay)

    elif args.command == "date":
        replay.load_date(args.date_str)
        print_summary(replay)
        print_hourly(replay)

    elif args.command == "last":
        replay.load_last_hours(args.hours)
        print_summary(replay)
        print_timeline(replay)

    elif args.command == "timeline":
        replay.load_today()
        print_timeline(replay, args.limit)

    elif args.command == "hourly":
        replay.load_today()
        print_hourly(replay)

    elif args.command == "instance":
        replay.load_today()
        by_instance = replay.group_by_instance()
        target = args.instance_id.upper()

        print(f"\n{'='*60}")
        print(f"ATOMS BY INSTANCE: {target}")
        print(f"{'='*60}")

        if target in by_instance:
            atoms = by_instance[target]
            print(f"\nFound {len(atoms)} atoms")
            for atom in atoms[:20]:
                time = atom.get("created", "?")[:19]
                preview = atom.get("content", "")[:60]
                print(f"\n  [{time}]")
                print(f"    {preview}...")
        else:
            print(f"No atoms found for {target}")
            print(f"Available instances: {', '.join(by_instance.keys())}")

    elif args.command == "summary":
        replay.load_today()
        print_summary(replay)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
