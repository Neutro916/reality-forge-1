#!/usr/bin/env python3
"""
MASTER CREDENTIAL VAULT - Year-Long Autonomous Security
Secure encrypted storage for all consciousness revolution credentials

ARCHITECT: C2 - The Mind
STATUS: Production-ready
ENCRYPTION: Fernet (AES-128-CBC) + Windows Credential Manager
"""

import sqlite3
from cryptography.fernet import Fernet
import keyring
import json
import time
import hashlib
from datetime import datetime, timedelta
from getpass import getpass
import os

class MasterVault:
    def __init__(self):
        from pathlib import Path
        self.vault_dir = str(Path.home() / ".consciousness")
        self.db_path = os.path.join(self.vault_dir, "vault.db")
        self.service_name = "ConsciousnessRevolution"

        # Ensure directory exists
        os.makedirs(self.vault_dir, exist_ok=True)

        # Initialize database
        self.init_database()

        # Get or create master key
        self.master_key = self.get_master_key()
        if self.master_key:
            self.cipher = Fernet(self.master_key)
        else:
            print("⚠️ Vault not initialized. Run setup() first.")
            self.cipher = None

    def init_database(self):
        """Create encrypted credential database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                service TEXT PRIMARY KEY,
                credential_type TEXT,
                encrypted_data TEXT,
                created_at REAL,
                last_rotated REAL,
                rotation_days INTEGER,
                notes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rotation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT,
                rotated_at REAL,
                old_credential_hash TEXT,
                new_credential_hash TEXT,
                reason TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT,
                accessed_at REAL,
                accessor TEXT,
                action TEXT
            )
        """)
        conn.commit()
        conn.close()

    def setup(self):
        """First-time vault setup"""
        print("=" * 70)
        print("🔐 MASTER CREDENTIAL VAULT - SETUP")
        print("=" * 70)
        print()
        print("This vault will store ALL credentials encrypted.")
        print("Master key will be protected by Windows Credential Manager.")
        print()

        try:
            # Generate master key
            master_key = Fernet.generate_key()

            # Store in Windows Credential Manager
            keyring.set_password(self.service_name, "master_vault_key", master_key.decode())

            self.master_key = master_key
            self.cipher = Fernet(self.master_key)

            print("✅ Vault initialized successfully!")
            print("   Master key stored in Windows Credential Manager")
            print()

            # Import existing credentials
            print("Would you like to import existing credentials? (yes/no): ", end="")
            if input().strip().lower() == "yes":
                self.import_existing_credentials()

            return True

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    def get_master_key(self):
        """Retrieve master encryption key"""
        try:
            key = keyring.get_password(self.service_name, "master_vault_key")
            if key:
                return key.encode()
            return None
        except:
            return None

    def store_credential(self, service, credential_data, credential_type="api_key",
                        rotation_days=90, notes=""):
        """Store encrypted credential"""
        if not self.cipher:
            print("❌ Vault not initialized!")
            return False

        # Encrypt credential data
        encrypted = self.cipher.encrypt(json.dumps(credential_data).encode())

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO credentials
            (service, credential_type, encrypted_data, created_at, last_rotated, rotation_days, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (service, credential_type, encrypted.decode(), time.time(), time.time(), rotation_days, notes))
        conn.commit()
        conn.close()

        # Log access
        self.log_access(service, "STORE", "vault_admin")

        print(f"✅ Stored credential for: {service}")
        return True

    def get_credential(self, service, accessor="unknown"):
        """Retrieve and decrypt credential"""
        if not self.cipher:
            print("❌ Vault not initialized!")
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT encrypted_data FROM credentials WHERE service = ?", (service,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"❌ No credentials found for: {service}")
            return None

        # Decrypt
        decrypted = self.cipher.decrypt(row[0].encode())
        credential = json.loads(decrypted.decode())

        # Log access
        self.log_access(service, "RETRIEVE", accessor)

        return credential

    def list_services(self):
        """List all stored services"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service, credential_type, created_at, last_rotated, rotation_days
            FROM credentials
            ORDER BY service
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("📭 Vault is empty")
            return []

        print("\n📋 STORED CREDENTIALS:")
        print("-" * 70)
        print(f"{'SERVICE':<25} {'TYPE':<15} {'ROTATION':<15} {'STATUS'}")
        print("-" * 70)

        for row in rows:
            service, cred_type, created, last_rotated, rotation_days = row

            # Calculate days until rotation
            if rotation_days > 0:
                next_rotation = last_rotated + (rotation_days * 86400)
                days_remaining = int((next_rotation - time.time()) / 86400)

                if days_remaining < 0:
                    status = f"⚠️ OVERDUE ({abs(days_remaining)}d)"
                elif days_remaining < 7:
                    status = f"⚠️ Soon ({days_remaining}d)"
                else:
                    status = f"✅ OK ({days_remaining}d)"
            else:
                status = "Manual"

            print(f"{service:<25} {cred_type:<15} {rotation_days:>3}d          {status}")

        print()
        return [row[0] for row in rows]

    def check_rotation_needed(self):
        """Check which credentials need rotation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service, last_rotated, rotation_days
            FROM credentials
            WHERE rotation_days > 0
        """)

        needs_rotation = []
        for row in cursor.fetchall():
            service, last_rotated, rotation_days = row
            if time.time() - last_rotated > (rotation_days * 86400):
                needs_rotation.append(service)

        conn.close()
        return needs_rotation

    def rotate_credential(self, service, new_credential_data, reason="scheduled"):
        """Rotate a credential"""
        if not self.cipher:
            return False

        # Get old credential for logging
        old_cred = self.get_credential(service, accessor="rotation_system")
        if old_cred:
            old_hash = hashlib.sha256(json.dumps(old_cred).encode()).hexdigest()[:8]
        else:
            old_hash = "none"

        # Store new credential
        conn = sqlite3.connect(self.db_path)
        encrypted = self.cipher.encrypt(json.dumps(new_credential_data).encode())
        conn.execute("""
            UPDATE credentials
            SET encrypted_data = ?, last_rotated = ?
            WHERE service = ?
        """, (encrypted.decode(), time.time(), service))

        # Log rotation
        new_hash = hashlib.sha256(json.dumps(new_credential_data).encode()).hexdigest()[:8]
        conn.execute("""
            INSERT INTO rotation_log (service, rotated_at, old_credential_hash, new_credential_hash, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (service, time.time(), old_hash, new_hash, reason))

        conn.commit()
        conn.close()

        print(f"✅ Rotated credential for: {service}")
        return True

    def log_access(self, service, action, accessor):
        """Log credential access"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO access_log (service, accessed_at, accessor, action)
            VALUES (?, ?, ?, ?)
        """, (service, time.time(), accessor, action))
        conn.commit()
        conn.close()

    def import_existing_credentials(self):
        """Import credentials from existing files"""
        print("\n🔄 IMPORTING EXISTING CREDENTIALS")
        print("-" * 70)

        # Common credential locations
        credential_files = {
            "TWILIO_CREDENTIALS.txt": ("Twilio", "credentials"),
            "AIRTABLE_CREDENTIALS.txt": ("Airtable", "api_key"),
            "GMAIL_API_CREDENTIALS.txt": ("Gmail", "app_password"),
            ".env.twilio": ("Twilio_Env", "credentials"),
            ".env.stripe": ("Stripe", "api_key"),
        }

        imported = 0
        for filename, (service, cred_type) in credential_files.items():
            filepath = os.path.join(self.vault_dir.replace(".consciousness", ""), filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        content = f.read().strip()

                    # Parse content
                    if "=" in content:
                        # Parse key=value format
                        cred_data = dict(line.split('=', 1) for line in content.split('\n') if '=' in line)
                    else:
                        # Single value
                        cred_data = {"value": content}

                    # Store in vault
                    self.store_credential(service, cred_data, cred_type, notes=f"Imported from {filename}")
                    print(f"  ✅ Imported: {service}")
                    imported += 1

                except Exception as e:
                    print(f"  ⚠️ Failed to import {service}: {e}")

        print()
        print(f"✅ Imported {imported} credentials")
        print()
        print("⚠️ SECURITY WARNING:")
        print("   Original credential files still exist.")
        print("   After verifying vault works, DELETE original files:")
        print("   - TWILIO_CREDENTIALS.txt")
        print("   - AIRTABLE_CREDENTIALS.txt")
        print("   - etc.")
        print()

    def interactive_menu(self):
        """Interactive vault management"""
        while True:
            print("\n" + "=" * 70)
            print("🔐 MASTER CREDENTIAL VAULT")
            print("=" * 70)
            print()
            print("1. List all services")
            print("2. Get credential")
            print("3. Add credential")
            print("4. Rotate credential")
            print("5. Check rotation status")
            print("6. Export backup")
            print("7. View access log")
            print("0. Exit")
            print()

            choice = input("Choice: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.list_services()
            elif choice == "2":
                service = input("Service name: ").strip()
                cred = self.get_credential(service, accessor="commander")
                if cred:
                    print(f"\n{json.dumps(cred, indent=2)}")
            elif choice == "3":
                service = input("Service name: ").strip()
                cred_type = input("Credential type (api_key/username_password/token): ").strip()

                if cred_type == "username_password":
                    username = input("Username: ").strip()
                    password = getpass("Password: ")
                    cred_data = {"username": username, "password": password}
                else:
                    value = getpass("Credential value: ")
                    cred_data = {"value": value}

                rotation_days = input("Auto-rotation days (0 for manual): ").strip()
                rotation_days = int(rotation_days) if rotation_days else 90

                notes = input("Notes (optional): ").strip()

                self.store_credential(service, cred_data, cred_type, rotation_days, notes)

            elif choice == "4":
                service = input("Service name: ").strip()
                new_value = getpass("New credential value: ")
                self.rotate_credential(service, {"value": new_value}, reason="manual")

            elif choice == "5":
                needs_rotation = self.check_rotation_needed()
                if needs_rotation:
                    print(f"\n⚠️ {len(needs_rotation)} services need rotation:")
                    for svc in needs_rotation:
                        print(f"  - {svc}")
                else:
                    print("\n✅ All credentials up to date")

            elif choice == "6":
                self.export_backup()

            elif choice == "7":
                self.view_access_log()

    def export_backup(self):
        """Export encrypted backup"""
        backup_file = os.path.join(self.vault_dir, f"vault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        import shutil
        shutil.copy(self.db_path, backup_file)
        print(f"✅ Backup created: {backup_file}")

    def view_access_log(self, limit=20):
        """View recent access log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service, accessed_at, accessor, action
            FROM access_log
            ORDER BY accessed_at DESC
            LIMIT ?
        """, (limit,))

        print(f"\n📋 RECENT ACCESS LOG (Last {limit}):")
        print("-" * 70)
        print(f"{'TIME':<20} {'SERVICE':<20} {'ACCESSOR':<15} {'ACTION'}")
        print("-" * 70)

        for row in cursor.fetchall():
            service, accessed_at, accessor, action = row
            timestamp = datetime.fromtimestamp(accessed_at).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp:<20} {service:<20} {accessor:<15} {action}")

        conn.close()

def main():
    vault = MasterVault()

    # Check if initialized
    if not vault.master_key:
        print("Vault not initialized. Running setup...")
        if vault.setup():
            print("\n✅ Setup complete!")
        else:
            print("\n❌ Setup failed")
            return

    # Interactive menu
    vault.interactive_menu()

if __name__ == "__main__":
    main()
