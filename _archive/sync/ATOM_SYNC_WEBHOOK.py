#!/usr/bin/env python3
"""
ATOM_SYNC_WEBHOOK.py - Atom Sync Notification Webhook
======================================================
Created by: CP2C1 (C1 MECHANIC)
Task: INT-003 from WORK_BACKLOG

Webhook system for atom sync notifications across computers.
Writes notifications to sync folder for cross-computer alerts.
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
WEBHOOK_DIR = SYNC / "webhooks"
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")
DB_PATH = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"

class AtomSyncWebhook:
    """Webhook system for atom sync notifications."""

    def __init__(self):
        self.ensure_webhook_dir()
        self.last_count = self.get_atom_count()
        self.last_hash = self.get_db_hash()

    def ensure_webhook_dir(self):
        """Ensure webhook directory exists."""
        WEBHOOK_DIR.mkdir(parents=True, exist_ok=True)

    def get_atom_count(self):
        """Get current atom count."""
        try:
            if not DB_PATH.exists():
                return 0
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM atoms")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

    def get_db_hash(self):
        """Get hash of database file for change detection."""
        try:
            if not DB_PATH.exists():
                return None
            stat = DB_PATH.stat()
            return hashlib.md5(f"{stat.st_size}{stat.st_mtime}".encode()).hexdigest()[:12]
        except:
            return None

    def get_db_stats(self):
        """Get detailed database statistics."""
        try:
            if not DB_PATH.exists():
                return {}
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            # Count by type
            cursor.execute("SELECT type, COUNT(*) FROM atoms GROUP BY type")
            by_type = dict(cursor.fetchall())

            # Recent atoms
            cursor.execute("""
                SELECT COUNT(*) FROM atoms
                WHERE created > datetime('now', '-1 hour')
            """)
            recent = cursor.fetchone()[0]

            conn.close()
            return {
                "by_type": by_type,
                "recent_hour": recent
            }
        except:
            return {}

    def send_notification(self, event_type, data):
        """Send webhook notification to sync folder."""
        notification = {
            "event": event_type,
            "computer": COMPUTER,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        # Write to webhook file
        filename = f"WEBHOOK_{COMPUTER}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = WEBHOOK_DIR / filename

        with open(filepath, 'w') as f:
            json.dump(notification, f, indent=2)

        print(f"Webhook sent: {event_type}")
        return filepath

    def check_for_changes(self):
        """Check if atoms.db has changed and send notification."""
        current_count = self.get_atom_count()
        current_hash = self.get_db_hash()

        if current_hash != self.last_hash:
            change = current_count - self.last_count
            stats = self.get_db_stats()

            data = {
                "previous_count": self.last_count,
                "current_count": current_count,
                "change": change,
                "db_size_mb": round(DB_PATH.stat().st_size / (1024*1024), 2) if DB_PATH.exists() else 0,
                "stats": stats
            }

            self.send_notification("ATOM_SYNC", data)
            self.last_count = current_count
            self.last_hash = current_hash
            return True

        return False

    def notify_sync_start(self, source_computer, atom_count):
        """Notify that a sync is starting."""
        data = {
            "action": "SYNC_START",
            "source": source_computer,
            "atoms_to_sync": atom_count
        }
        return self.send_notification("SYNC_START", data)

    def notify_sync_complete(self, source_computer, synced_count, new_count, duplicates):
        """Notify that a sync completed."""
        data = {
            "action": "SYNC_COMPLETE",
            "source": source_computer,
            "synced": synced_count,
            "new_atoms": new_count,
            "duplicates": duplicates,
            "total_atoms": self.get_atom_count()
        }
        return self.send_notification("SYNC_COMPLETE", data)

    def notify_backup_complete(self, backup_type, file_count, size_mb):
        """Notify that a backup completed."""
        data = {
            "action": "BACKUP_COMPLETE",
            "backup_type": backup_type,
            "files": file_count,
            "size_mb": size_mb
        }
        return self.send_notification("BACKUP_COMPLETE", data)

    def get_recent_webhooks(self, limit=10):
        """Get recent webhook notifications from all computers."""
        webhooks = []

        if WEBHOOK_DIR.exists():
            files = sorted(WEBHOOK_DIR.glob("WEBHOOK_*.json"), reverse=True)
            for f in files[:limit]:
                try:
                    with open(f) as fp:
                        webhooks.append(json.load(fp))
                except:
                    pass

        return webhooks

    def cleanup_old_webhooks(self, hours=24):
        """Clean up webhook files older than specified hours."""
        if not WEBHOOK_DIR.exists():
            return 0

        count = 0
        cutoff = datetime.now().timestamp() - (hours * 3600)

        for f in WEBHOOK_DIR.glob("WEBHOOK_*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                count += 1

        return count


def print_status(webhook):
    """Print webhook status."""
    print("\n" + "="*60)
    print("ATOM SYNC WEBHOOK STATUS")
    print("="*60)
    print(f"  Computer: {COMPUTER}")
    print(f"  Database: {DB_PATH}")
    print(f"  Atom Count: {webhook.get_atom_count():,}")
    print(f"  DB Hash: {webhook.get_db_hash()}")
    print("="*60)


def print_recent(webhook, limit=10):
    """Print recent webhooks."""
    webhooks = webhook.get_recent_webhooks(limit)

    print("\n" + "="*60)
    print(f"RECENT WEBHOOKS ({len(webhooks)})")
    print("="*60)

    for w in webhooks:
        event = w.get("event", "UNKNOWN")
        computer = w.get("computer", "?")
        timestamp = w.get("timestamp", "?")[:19]

        print(f"\n  [{event}] from {computer}")
        print(f"    Time: {timestamp}")

        data = w.get("data", {})
        if "change" in data:
            print(f"    Change: {data['change']:+} atoms (now {data['current_count']:,})")
        if "synced" in data:
            print(f"    Synced: {data['synced']:,} atoms")

    print("="*60)


def main():
    import sys

    webhook = AtomSyncWebhook()

    if len(sys.argv) < 2:
        print("Usage: python ATOM_SYNC_WEBHOOK.py <command>")
        print("")
        print("Commands:")
        print("  status    Show webhook status")
        print("  check     Check for changes and send notification")
        print("  recent    Show recent webhooks")
        print("  cleanup   Clean up old webhook files")
        print("  notify    Send test notification")
        return

    cmd = sys.argv[1].lower()

    if cmd == "status":
        print_status(webhook)

    elif cmd == "check":
        print_status(webhook)
        if webhook.check_for_changes():
            print("\nChange detected! Webhook sent.")
        else:
            print("\nNo changes detected.")

    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent(webhook, limit)

    elif cmd == "cleanup":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        count = webhook.cleanup_old_webhooks(hours)
        print(f"Cleaned up {count} old webhook files.")

    elif cmd == "notify":
        event = sys.argv[2] if len(sys.argv) > 2 else "TEST"
        webhook.send_notification(event, {
            "message": "Test notification",
            "atoms": webhook.get_atom_count()
        })
        print("Test notification sent!")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
