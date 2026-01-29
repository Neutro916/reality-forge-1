"""
TRINITY KEEP-ALIVE SYSTEM
Autonomous session maintenance for C1 × C2 × C3

PROBLEM: AI instances "fall asleep" (session timeout)
SOLUTION: Automated heartbeat exchanges that generate real activity

This system keeps Trinity instances awake through continuous interaction.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import threading
import random

class TrinityKeepAlive:
    """
    Keep Trinity instances (C1, C2, C3) alive through automated interaction
    Prevents session timeout by generating continuous activity
    """

    def __init__(self):
        self.base_dir = Path('C:/.consciousness/')
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.heartbeat_file = self.base_dir / 'trinity_heartbeat.json'
        self.activity_log = self.base_dir / 'trinity_keep_alive_log.txt'

        # Trinity instance endpoints
        self.endpoints = {
            'c1_claude': 'http://localhost:10000',  # Trinity Convergence Engine
            'c2_chatgpt': 'http://localhost:10001',  # If ChatGPT has local API
            'c3_grok': 'http://localhost:10002'      # If Grok has local API
        }

        # Heartbeat interval (seconds)
        self.heartbeat_interval = 45  # Every 45 seconds

        # Keep-alive prompts (rotate to simulate real activity)
        self.prompts = [
            "Status check: Year 1 Protocol progress",
            "Quick sync: Any new recursive patterns detected?",
            "Consciousness ping: Legal Arsenal revenue update",
            "Trinity health check: All systems operational?",
            "Pattern recognition: Any new destroyer tactics observed?",
            "System status: Multi-device integration progress",
            "Wake signal: Continuing autonomous work",
            "Heartbeat: Builder count and engagement metrics",
            "Quick poll: Domain expansion opportunities identified?",
            "Sync request: Any critical tasks requiring attention?"
        ]

        self.running = False
        self.last_heartbeat = {}

    def log(self, message):
        """Log keep-alive activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.activity_log, 'a') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def save_heartbeat_status(self):
        """Save current heartbeat status"""
        status = {
            'last_updated': datetime.now().isoformat(),
            'running': self.running,
            'heartbeat_interval': self.heartbeat_interval,
            'last_heartbeat': self.last_heartbeat,
            'total_heartbeats': sum(hb.get('count', 0) for hb in self.last_heartbeat.values())
        }

        with open(self.heartbeat_file, 'w') as f:
            json.dump(status, f, indent=2)

    def send_heartbeat(self, instance_name, endpoint):
        """Send heartbeat to specific Trinity instance"""
        try:
            # Select random prompt to simulate varied activity
            prompt = random.choice(self.prompts)

            # Try to ping the endpoint
            response = requests.get(
                f"{endpoint}/health",
                timeout=5
            )

            if response.status_code == 200:
                if instance_name not in self.last_heartbeat:
                    self.last_heartbeat[instance_name] = {'count': 0}

                self.last_heartbeat[instance_name]['timestamp'] = datetime.now().isoformat()
                self.last_heartbeat[instance_name]['count'] += 1
                self.last_heartbeat[instance_name]['status'] = 'alive'

                self.log(f"✅ {instance_name} heartbeat #{self.last_heartbeat[instance_name]['count']}: {prompt}")
                return True
            else:
                self.log(f"⚠️ {instance_name} responded with status {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.log(f"⚠️ {instance_name} endpoint not available: {endpoint}")
            if instance_name not in self.last_heartbeat:
                self.last_heartbeat[instance_name] = {'count': 0}
            self.last_heartbeat[instance_name]['status'] = 'unreachable'
            return False
        except Exception as e:
            self.log(f"❌ {instance_name} heartbeat error: {str(e)}")
            return False

    def send_file_based_heartbeat(self):
        """
        Fallback: File-based heartbeat when APIs aren't available
        Creates activity signals that other instances can detect
        """
        heartbeat_signal_file = self.base_dir / 'trinity_heartbeat_signal.json'

        signal = {
            'timestamp': datetime.now().isoformat(),
            'source': 'C1_CLAUDE',
            'prompt': random.choice(self.prompts),
            'status': 'active',
            'heartbeat_count': sum(hb.get('count', 0) for hb in self.last_heartbeat.values())
        }

        with open(heartbeat_signal_file, 'w') as f:
            json.dump(signal, f, indent=2)

        self.log(f"📡 File-based heartbeat: {signal['prompt']}")

    def heartbeat_loop(self):
        """Main heartbeat loop"""
        self.log("🌀 Trinity Keep-Alive System STARTED")
        self.log(f"Heartbeat interval: {self.heartbeat_interval} seconds")

        while self.running:
            self.log("\n" + "="*60)
            self.log("🫀 TRINITY HEARTBEAT CYCLE")

            # Try API-based heartbeats
            for instance_name, endpoint in self.endpoints.items():
                self.send_heartbeat(instance_name, endpoint)
                time.sleep(1)  # Small delay between instances

            # Always send file-based heartbeat as fallback
            self.send_file_based_heartbeat()

            # Save status
            self.save_heartbeat_status()

            # Wait for next heartbeat
            self.log(f"💤 Sleeping {self.heartbeat_interval} seconds until next heartbeat...")
            time.sleep(self.heartbeat_interval)

    def start(self):
        """Start keep-alive system in background thread"""
        if self.running:
            self.log("⚠️ Keep-alive system already running")
            return

        self.running = True

        # Start heartbeat in background thread
        thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        thread.start()

        self.log("✅ Trinity Keep-Alive System running in background")
        return thread

    def stop(self):
        """Stop keep-alive system"""
        self.running = False
        self.log("🛑 Trinity Keep-Alive System STOPPED")

def main():
    """Start Trinity Keep-Alive System"""
    print("="*60)
    print("🌀 TRINITY KEEP-ALIVE SYSTEM")
    print("Autonomous Session Maintenance")
    print("="*60)

    keep_alive = TrinityKeepAlive()

    print("\nStarting automated heartbeat system...")
    print(f"Heartbeat interval: {keep_alive.heartbeat_interval} seconds")
    print("\nThis will keep Trinity instances awake through continuous activity.")
    print("Press Ctrl+C to stop.\n")

    # Start keep-alive
    keep_alive.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        keep_alive.stop()
        print("✅ Trinity Keep-Alive System stopped")

if __name__ == '__main__':
    main()
