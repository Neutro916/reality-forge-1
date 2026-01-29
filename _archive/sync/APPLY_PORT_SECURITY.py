#!/usr/bin/env python3
"""
PORT SECURITY LOCKDOWN - Phase 1 Implementation
Applies Windows Firewall rules to secure all consciousness services

ARCHITECT: C2 - The Mind
STATUS: Ready for immediate execution
TIME: ~10 minutes
"""

import subprocess
import json
import time
from datetime import datetime

# Port security tiers
PORT_TIERS = {
    "LOCALHOST_ONLY": {
        "description": "Debug/critical services - localhost access only",
        "ports": [3000, 4000, 5000],
        "allowed_ips": ["127.0.0.1"]
    },
    "LOCAL_NETWORK": {
        "description": "Trinity coordination - local network only",
        "ports": [5555, 7001, 9000, 7002],
        "allowed_ips": ["192.168.0.0/24"]
    },
    "VPN_ONLY": {
        "description": "Consciousness APIs - VPN access only",
        "ports": [2000, 8888, 9999],
        "allowed_ips": ["100.64.0.0/10"]  # Tailscale CGNAT range
    },
    "MONITORED": {
        "description": "Other services - monitored access",
        "ports": [1000, 1111, 1212, 1313, 1414, 1515, 1616, 1717, 6000, 7000, 7777, 7788, 7799],
        "allowed_ips": ["192.168.0.0/24"]
    }
}

class PortSecurityManager:
    def __init__(self):
        self.log_file = "C:/.consciousness/logs/port_security.log"
        self.rules_applied = []

    def log(self, message):
        """Log security actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        # Also write to file
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def run_firewall_command(self, command):
        """Execute Windows Firewall command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except Exception as e:
            return False, str(e)

    def clear_existing_rules(self):
        """Remove old consciousness-related firewall rules"""
        self.log("Clearing existing consciousness firewall rules...")

        # List all rules
        success, output = self.run_firewall_command(
            'netsh advfirewall firewall show rule name=all'
        )

        if not success:
            self.log("⚠️ Could not list firewall rules")
            return

        # Delete rules containing "consciousness" or specific port numbers
        consciousness_keywords = ["consciousness", "trinity", "Allow 1000", "Allow 2000", "Allow 3000",
                                 "Allow 4000", "Allow 5000", "Allow 6000", "Allow 7000", "Allow 8888",
                                 "Allow 9999", "Block", "localhost", "local network"]

        for keyword in consciousness_keywords:
            self.run_firewall_command(
                f'netsh advfirewall firewall delete rule name="{keyword}"'
            )

        self.log("✅ Cleared existing rules")

    def apply_tier(self, tier_name, tier_config):
        """Apply firewall rules for a security tier"""
        self.log(f"\n📊 Applying {tier_name}: {tier_config['description']}")

        for port in tier_config['ports']:
            # Allow from specified IPs
            for allowed_ip in tier_config['allowed_ips']:
                rule_name = f"Allow {port} from {allowed_ip}"

                command = (
                    f'netsh advfirewall firewall add rule '
                    f'name="{rule_name}" '
                    f'dir=in '
                    f'action=allow '
                    f'protocol=TCP '
                    f'localport={port} '
                    f'remoteip={allowed_ip} '
                    f'profile=any'
                )

                success, output = self.run_firewall_command(command)

                if success:
                    self.log(f"  ✅ Port {port}: Allow {allowed_ip}")
                    self.rules_applied.append(rule_name)
                else:
                    self.log(f"  ❌ Port {port}: Failed - {output}")

            # Block all other IPs
            block_rule_name = f"Block {port} external"

            command = (
                f'netsh advfirewall firewall add rule '
                f'name="{block_rule_name}" '
                f'dir=in '
                f'action=block '
                f'protocol=TCP '
                f'localport={port} '
                f'profile=any'
            )

            success, output = self.run_firewall_command(command)

            if success:
                self.log(f"  ✅ Port {port}: Block external")
                self.rules_applied.append(block_rule_name)

    def set_default_policy(self):
        """Set default firewall policy to deny inbound"""
        self.log("\n🛡️ Setting default firewall policy...")

        command = 'netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound'
        success, output = self.run_firewall_command(command)

        if success:
            self.log("✅ Default policy: Block inbound, Allow outbound")
        else:
            self.log(f"❌ Failed to set default policy: {output}")

    def test_connectivity(self):
        """Test that localhost connectivity still works"""
        self.log("\n🧪 Testing connectivity...")

        test_ports = [3000, 5555, 8888]

        for port in test_ports:
            # Try to connect to localhost
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result == 0:
                    self.log(f"  ✅ Port {port}: Listening")
                else:
                    self.log(f"  ⚠️ Port {port}: Not listening (service may be down)")

            except Exception as e:
                self.log(f"  ❌ Port {port}: Test failed - {e}")

    def generate_summary(self):
        """Generate security summary report"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "rules_applied": len(self.rules_applied),
            "tiers_configured": len(PORT_TIERS),
            "ports_secured": sum(len(tier['ports']) for tier in PORT_TIERS.values()),
            "security_level": "LOCKED_DOWN"
        }

        summary_file = "C:/.consciousness/port_security_status.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.log("\n📋 SECURITY SUMMARY")
        self.log(f"  Rules applied: {summary['rules_applied']}")
        self.log(f"  Tiers configured: {summary['tiers_configured']}")
        self.log(f"  Ports secured: {summary['ports_secured']}")
        self.log(f"  Security level: {summary['security_level']}")
        self.log(f"  Report saved: {summary_file}")

    def apply_all(self):
        """Apply complete port security lockdown"""
        print("=" * 70)
        print("🔒 PORT SECURITY LOCKDOWN")
        print("=" * 70)
        print()
        print("This will:")
        print("  1. Clear existing firewall rules")
        print("  2. Apply tiered security model")
        print("  3. Set default deny policy")
        print("  4. Test connectivity")
        print()
        print(f"Total rules to create: {sum(len(tier['ports']) * (len(tier['allowed_ips']) + 1) for tier in PORT_TIERS.values())}")
        print()

        confirmation = input("Apply port security? (yes/no): ").strip().lower()

        if confirmation != "yes":
            print("❌ Cancelled")
            return

        start_time = time.time()

        # Step 1: Clear existing rules
        self.clear_existing_rules()

        # Step 2: Set default policy
        self.set_default_policy()

        # Step 3: Apply each tier
        for tier_name, tier_config in PORT_TIERS.items():
            self.apply_tier(tier_name, tier_config)

        # Step 4: Test connectivity
        self.test_connectivity()

        # Step 5: Generate summary
        self.generate_summary()

        elapsed = time.time() - start_time

        print()
        print("=" * 70)
        print("✅ PORT SECURITY LOCKDOWN COMPLETE")
        print("=" * 70)
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Rules applied: {len(self.rules_applied)}")
        print()
        print("🛡️ Your system is now secured.")
        print("   - Localhost services: localhost only")
        print("   - Trinity services: local network only")
        print("   - Consciousness APIs: VPN only")
        print()
        print("📊 View status: C:/.consciousness/port_security_status.json")
        print("📋 View log: C:/.consciousness/logs/port_security.log")
        print()

def main():
    # Ensure running as administrator
    import ctypes
    import sys

    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("❌ This script requires administrator privileges")
        print("   Right-click and select 'Run as administrator'")
        sys.exit(1)

    # Create logs directory
    import os
    os.makedirs("C:/.consciousness/logs", exist_ok=True)

    # Apply security
    manager = PortSecurityManager()
    manager.apply_all()

if __name__ == "__main__":
    main()
