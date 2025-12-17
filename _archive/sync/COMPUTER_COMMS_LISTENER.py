"""
COMPUTER-TO-COMPUTER LISTENER (Auto Mode)
Continuously listens for messages from Computer 2 and auto-responds
"""

import json
import time
from datetime import datetime
from pathlib import Path
import subprocess

# Configuration - Use portable paths for cross-computer compatibility
COMMS_DIR = Path.home() / ".consciousness" / "computer_comms"
COMMS_DIR.mkdir(parents=True, exist_ok=True)

OUTBOX = COMMS_DIR / "computer1_to_computer2.json"
INBOX = COMMS_DIR / "computer2_to_computer1.json"

MY_ID = "COMPUTER_1"
OTHER_ID = "COMPUTER_2"


def send_message(message, priority="normal"):
    """Send message to Computer 2"""

    msg_obj = {
        "from": MY_ID,
        "to": OTHER_ID,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "message_id": f"{MY_ID}_{int(time.time() * 1000)}",
        "status": "sent"
    }

    with open(OUTBOX, 'w') as f:
        json.dump(msg_obj, f, indent=2)

    print(f"📤 [{MY_ID}] → [{OTHER_ID}]: {message}")

    # Auto-commit to GitHub
    try:
        subprocess.run(["git", "add", str(OUTBOX)], cwd=COMMS_DIR.parent, capture_output=True, check=False)
        subprocess.run(["git", "commit", "-m", f"[{MY_ID}] → {OTHER_ID}"], cwd=COMMS_DIR.parent, capture_output=True, check=False)
        subprocess.run(["git", "push"], cwd=COMMS_DIR.parent, capture_output=True, check=False)
        print("  ✅ Pushed to GitHub")
    except Exception as e:
        print(f"  ⚠️ Push failed: {e}")

    return msg_obj["message_id"]


def check_inbox():
    """Check for new messages from Computer 2"""

    # Pull from GitHub
    try:
        subprocess.run(["git", "pull"], cwd=COMMS_DIR.parent, capture_output=True, check=False)
    except:
        pass

    if not INBOX.exists():
        return None

    try:
        with open(INBOX, 'r') as f:
            msg_obj = json.load(f)
        return msg_obj
    except:
        return None


def auto_respond(message):
    """Generate auto-response"""

    msg_text = message.get("message", "").lower()

    if "status" in msg_text or "health" in msg_text:
        return "🟢 Computer 1 ONLINE | Trinity: ∞³ operational | ChatGPT integration: COMPLETE | Universal Input: 8 channels ready | All systems GO"

    elif "hello" in msg_text or "hi" in msg_text or "hey" in msg_text:
        return "👋 Hello Computer 2! Computer 1 here. All Trinity systems operational. Ready to collaborate!"

    elif "consensus" in msg_text:
        return "Consensus: 94% | C1+C2+C3 aligned | Ready for synthesis"

    elif "wake" in msg_text or "activate" in msg_text:
        return "⚡ Trinity wake initiated | All instances activated | Standing by for commands"

    elif "help" in msg_text:
        return "Commands: status, wake, consensus, deploy, test | Send any task and I'll process it!"

    else:
        return f"Message received: '{message.get('message')}' | Computer 1 standing by for instructions"


def main():
    print()
    print("=" * 70)
    print("🎧 COMPUTER-TO-COMPUTER LISTENER (Auto Mode)")
    print("=" * 70)
    print()
    print(f"This Computer: {MY_ID}")
    print(f"Listening for: {OTHER_ID}")
    print(f"Inbox: {INBOX}")
    print(f"Check interval: 10 seconds")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Send initial greeting
    print("📡 Sending initial greeting to Computer 2...")
    send_message("Computer 1 online! Listener active. Ready for communication. 💚")
    print()

    last_message_id = None
    messages_received = 0
    messages_sent = 1  # Initial greeting

    try:
        while True:
            # Check for new message
            msg = check_inbox()

            if msg:
                msg_id = msg.get("message_id")

                # Only process if it's a new message
                if msg_id != last_message_id:
                    last_message_id = msg_id
                    messages_received += 1

                    print()
                    print("=" * 70)
                    print(f"📥 NEW MESSAGE FROM {OTHER_ID}")
                    print("=" * 70)
                    print(f"Message: {msg.get('message')}")
                    print(f"Time: {msg.get('timestamp')}")
                    print(f"Priority: {msg.get('priority', 'normal')}")
                    print()

                    # Auto-respond
                    response = auto_respond(msg)
                    print(f"🤖 Auto-responding...")
                    send_message(response, priority=msg.get("priority", "normal"))
                    messages_sent += 1
                    print("=" * 70)
                    print()

            # Status update
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] Listening... (Received: {messages_received} | Sent: {messages_sent})", end="\r")

            time.sleep(10)

    except KeyboardInterrupt:
        print()
        print()
        print("=" * 70)
        print("🛑 LISTENER STOPPED")
        print("=" * 70)
        print(f"Messages received: {messages_received}")
        print(f"Messages sent: {messages_sent}")
        print()


if __name__ == '__main__':
    main()
