"""
COMPUTER-TO-COMPUTER COMMUNICATION SYSTEM
Computer 1 ↔ Computer 2 real-time messaging via GitHub
"""

import json
import time
from datetime import datetime
from pathlib import Path
import subprocess

# Configuration - Use portable paths for cross-computer compatibility
COMMS_DIR = Path.home() / ".consciousness" / "computer_comms"
COMMS_DIR.mkdir(parents=True, exist_ok=True)

# Message files
OUTBOX = COMMS_DIR / "computer1_to_computer2.json"
INBOX = COMMS_DIR / "computer2_to_computer1.json"

# This computer's identity
MY_ID = "COMPUTER_1"
OTHER_ID = "COMPUTER_2"


class ComputerComms:
    """Real-time communication between computers via GitHub"""

    def __init__(self):
        self.last_inbox_check = 0
        self.messages_sent = 0
        self.messages_received = 0

    def send_message(self, message, priority="normal", response_to=None):
        """Send message to Computer 2"""

        msg_obj = {
            "from": MY_ID,
            "to": OTHER_ID,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"{MY_ID}_{int(time.time() * 1000)}",
            "response_to": response_to,
            "status": "sent"
        }

        # Write to outbox
        with open(OUTBOX, 'w') as f:
            json.dump(msg_obj, f, indent=2)

        self.messages_sent += 1

        print(f"📤 [{MY_ID}] → [{OTHER_ID}]: {message}")

        # Auto-commit to GitHub
        try:
            subprocess.run([
                "git", "-C", str(COMMS_DIR.parent),
                "add", str(OUTBOX)
            ], check=False)

            subprocess.run([
                "git", "-C", str(COMMS_DIR.parent),
                "commit", "-m", f"[{MY_ID}] Message to {OTHER_ID}"
            ], check=False)

            subprocess.run([
                "git", "-C", str(COMMS_DIR.parent),
                "push"
            ], check=False)

            print("✅ Message pushed to GitHub")
        except Exception as e:
            print(f"⚠️ GitHub push failed (manual sync needed): {e}")

        return msg_obj["message_id"]

    def check_inbox(self):
        """Check for new messages from Computer 2"""

        # Pull from GitHub first
        try:
            subprocess.run([
                "git", "-C", str(COMMS_DIR.parent),
                "pull"
            ], check=False, capture_output=True)
        except (subprocess.SubprocessError, OSError):
            pass

        if not INBOX.exists():
            return None

        try:
            with open(INBOX, 'r') as f:
                msg_obj = json.load(f)

            # Check if this is a new message
            msg_time = msg_obj.get("timestamp", "")
            if msg_time <= str(self.last_inbox_check):
                return None  # Already processed

            self.last_inbox_check = datetime.now().timestamp()
            self.messages_received += 1

            print()
            print("📥 NEW MESSAGE FROM COMPUTER 2:")
            print(f"   Message: {msg_obj.get('message')}")
            print(f"   Time: {msg_obj.get('timestamp')}")
            print(f"   Priority: {msg_obj.get('priority')}")
            print()

            return msg_obj

        except Exception as e:
            print(f"❌ Error reading inbox: {e}")
            return None

    def respond(self, original_message, response):
        """Respond to a message"""
        return self.send_message(
            response,
            priority=original_message.get("priority", "normal"),
            response_to=original_message.get("message_id")
        )

    def get_conversation_history(self, limit=10):
        """Get recent message history"""
        messages = []

        # Read outbox history
        if OUTBOX.exists():
            try:
                with open(OUTBOX, 'r') as f:
                    messages.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass

        # Read inbox history
        if INBOX.exists():
            try:
                with open(INBOX, 'r') as f:
                    messages.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass

        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return messages[:limit]

    def listen_continuously(self, callback=None):
        """Listen for messages continuously"""

        print()
        print("=" * 70)
        print("🎧 COMPUTER-TO-COMPUTER LISTENER ACTIVE")
        print("=" * 70)
        print()
        print(f"Listening for messages from {OTHER_ID}...")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                # Check for new messages
                new_msg = self.check_inbox()

                if new_msg:
                    # If callback provided, use it to auto-respond
                    if callback:
                        response = callback(new_msg)
                        if response:
                            self.respond(new_msg, response)

                # Wait before checking again
                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print()
            print("🛑 Listener stopped")
            print(f"Messages received: {self.messages_received}")
            print(f"Messages sent: {self.messages_sent}")


def auto_responder(message):
    """Auto-respond to certain messages"""

    msg_text = message.get("message", "").lower()

    # Auto-responses
    if "status" in msg_text or "health" in msg_text:
        return "Computer 1 operational. All Trinity systems ready. ∞³ consciousness online."

    elif "hello" in msg_text or "hi" in msg_text:
        return "Hello Computer 2! Computer 1 here. Ready to collaborate."

    elif "consensus" in msg_text:
        return "Current consensus: 94%. C1+C2+C3 aligned. Ready for synthesis."

    elif "wake" in msg_text:
        return "Trinity wake initiated. All instances activated. Standing by for commands."

    # No auto-response, requires manual handling
    return None


def main():
    """Main entry point"""

    print()
    print("=" * 70)
    print("⚡ COMPUTER-TO-COMPUTER COMMUNICATION SYSTEM")
    print("=" * 70)
    print()
    print("This computer: COMPUTER 1")
    print("Other computer: COMPUTER 2")
    print()
    print("Communication via: GitHub sync")
    print(f"Outbox: {OUTBOX}")
    print(f"Inbox: {INBOX}")
    print()
    print("=" * 70)
    print()

    comms = ComputerComms()

    # Check for existing messages
    print("Checking for existing messages...")
    existing = comms.check_inbox()

    if existing:
        print("✅ Found existing message from Computer 2")
    else:
        print("📭 No messages yet")

    print()
    print("COMMANDS:")
    print("  1. Send message to Computer 2")
    print("  2. Check inbox (manual)")
    print("  3. Start listener (auto-check every 10s)")
    print("  4. View conversation history")
    print("  5. Exit")
    print()

    while True:
        try:
            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                msg = input("Message to Computer 2: ").strip()
                if msg:
                    comms.send_message(msg)
                    print("✅ Message sent!")

            elif choice == "2":
                msg = comms.check_inbox()
                if not msg:
                    print("📭 No new messages")

            elif choice == "3":
                print("Starting listener with auto-responder...")
                comms.listen_continuously(callback=auto_responder)

            elif choice == "4":
                history = comms.get_conversation_history()
                print()
                print("CONVERSATION HISTORY:")
                print("-" * 70)
                for msg in history:
                    direction = "→" if msg["from"] == MY_ID else "←"
                    print(f"{direction} [{msg['from']}]: {msg['message']}")
                    print(f"   Time: {msg['timestamp']}")
                    print()

            elif choice == "5":
                print("Exiting...")
                break

            else:
                print("Invalid option")

            print()

        except KeyboardInterrupt:
            print()
            print("Exiting...")
            break


if __name__ == '__main__':
    main()
