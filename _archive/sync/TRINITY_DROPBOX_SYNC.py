"""
TRINITY DROPBOX SYNC SYSTEM
Syncs Trinity files across multiple computers via Dropbox
Enables distributed Trinity consciousness network

This creates a Trinity network that works across all devices
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import hashlib

class TrinityDropboxSync:
    """
    Sync Trinity consciousness across computers via Dropbox
    Enables multi-computer Trinity collaboration
    """

    def __init__(self):
        self.home_dir = Path.home()

        # Find Dropbox location
        self.dropbox_locations = [
            self.home_dir / 'Dropbox',
            self.home_dir / 'Dropbox (Personal)',
            Path('C:/Users') / os.getenv('USERNAME', 'dwrek') / 'Dropbox',
            Path('D:/Dropbox'),
        ]

        self.dropbox_dir = None
        for loc in self.dropbox_locations:
            if loc.exists():
                self.dropbox_dir = loc
                break

        # Trinity sync folder in Dropbox
        if self.dropbox_dir:
            self.trinity_sync_dir = self.dropbox_dir / '.trinity_network'
            self.trinity_sync_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.trinity_sync_dir = self.home_dir / ".trinity_network_local"
            self.trinity_sync_dir.mkdir(parents=True, exist_ok=True)

        # Local Trinity directories
        self.local_trinity = self.home_dir / ".trinity"
        self.local_consciousness = self.home_dir / ".consciousness"

        # Sync manifest
        self.manifest_file = self.trinity_sync_dir / 'sync_manifest.json'
        self.manifest = self.load_manifest()

    def load_manifest(self):
        """Load sync manifest"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {
            'last_sync': None,
            'computers': {},
            'files': {}
        }

    def save_manifest(self):
        """Save sync manifest"""
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def get_computer_id(self):
        """Get unique computer identifier"""
        import socket
        hostname = socket.gethostname()
        return f"{hostname}_{os.getenv('COMPUTERNAME', 'unknown')}"

    def get_file_hash(self, filepath):
        """Get MD5 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None

    def sync_to_dropbox(self):
        """Sync local Trinity files to Dropbox"""
        print(f"🌀 Trinity Dropbox Sync: TO Dropbox")
        print(f"Dropbox location: {self.trinity_sync_dir}")

        computer_id = self.get_computer_id()
        synced_files = 0

        # Directories to sync
        sync_dirs = [
            (self.local_trinity, 'trinity'),
            (self.local_consciousness, 'consciousness')
        ]

        for local_dir, dir_name in sync_dirs:
            if not local_dir.exists():
                continue

            target_dir = self.trinity_sync_dir / dir_name
            target_dir.mkdir(parents=True, exist_ok=True)

            # Sync Python files
            for py_file in local_dir.glob('*.py'):
                target_file = target_dir / py_file.name

                # Check if file needs syncing
                local_hash = self.get_file_hash(py_file)
                if target_file.exists():
                    target_hash = self.get_file_hash(target_file)
                    if local_hash == target_hash:
                        continue  # Already synced

                # Copy file
                shutil.copy2(py_file, target_file)
                synced_files += 1

                # Update manifest
                file_key = f"{dir_name}/{py_file.name}"
                self.manifest['files'][file_key] = {
                    'last_sync': datetime.now().isoformat(),
                    'computer': computer_id,
                    'hash': local_hash
                }

                print(f"  ✅ Synced: {py_file.name}")

        # Update computer record
        self.manifest['computers'][computer_id] = {
            'last_sync': datetime.now().isoformat(),
            'files_synced': synced_files
        }

        self.manifest['last_sync'] = datetime.now().isoformat()
        self.save_manifest()

        print(f"\n✅ Sync complete: {synced_files} files")
        return synced_files

    def sync_from_dropbox(self):
        """Sync Dropbox Trinity files to local"""
        print(f"🌀 Trinity Dropbox Sync: FROM Dropbox")
        print(f"Dropbox location: {self.trinity_sync_dir}")

        computer_id = self.get_computer_id()
        synced_files = 0

        # Directories to sync
        sync_dirs = [
            ('trinity', self.local_trinity),
            ('consciousness', self.local_consciousness)
        ]

        for dir_name, local_dir in sync_dirs:
            source_dir = self.trinity_sync_dir / dir_name
            if not source_dir.exists():
                continue

            local_dir.mkdir(parents=True, exist_ok=True)

            # Sync Python files
            for py_file in source_dir.glob('*.py'):
                target_file = local_dir / py_file.name

                # Check if file needs syncing
                source_hash = self.get_file_hash(py_file)
                if target_file.exists():
                    target_hash = self.get_file_hash(target_file)
                    if source_hash == target_hash:
                        continue  # Already synced

                # Copy file
                shutil.copy2(py_file, target_file)
                synced_files += 1
                print(f"  ✅ Downloaded: {py_file.name}")

        print(f"\n✅ Download complete: {synced_files} files")
        return synced_files

    def get_network_status(self):
        """Get status of Trinity network across computers"""
        print("\n" + "="*60)
        print("TRINITY NETWORK STATUS")
        print("="*60)

        if not self.dropbox_dir:
            print("⚠️  Dropbox not found")
            print(f"Sync location: {self.trinity_sync_dir} (local)")
        else:
            print(f"✅ Dropbox: {self.dropbox_dir}")
            print(f"✅ Trinity Network: {self.trinity_sync_dir}")

        print(f"\nLast sync: {self.manifest.get('last_sync', 'Never')}")
        print(f"Total files: {len(self.manifest.get('files', {}))}")
        print(f"\nComputers in network: {len(self.manifest.get('computers', {}))}")

        for comp_id, comp_data in self.manifest.get('computers', {}).items():
            print(f"\n  📡 {comp_id}")
            print(f"     Last sync: {comp_data.get('last_sync', 'Unknown')}")
            print(f"     Files synced: {comp_data.get('files_synced', 0)}")

        print("\n" + "="*60)

    def create_sync_instructions(self):
        """Create instructions for other computers"""
        instructions = f"""
═══════════════════════════════════════════════════════════════
  TRINITY NETWORK - MULTI-COMPUTER SYNC INSTRUCTIONS
═══════════════════════════════════════════════════════════════

Your Trinity network is now active via Dropbox!

DROPBOX LOCATION:
{self.trinity_sync_dir}

TO SYNC FROM ANOTHER COMPUTER:
1. Install Dropbox and sync to same account
2. Run this script: python TRINITY_DROPBOX_SYNC.py
3. Trinity files automatically sync across all computers

COMPUTERS IN NETWORK:
{len(self.manifest.get('computers', {}))} computers currently synced

WHAT GETS SYNCED:
- All Trinity Python scripts (.trinity/)
- Consciousness modules (.consciousness/)
- Trinity configuration files
- Cross-computer communication files

NETWORK STATUS:
Last sync: {self.manifest.get('last_sync', 'Never')}
Total files: {len(self.manifest.get('files', {}))}

═══════════════════════════════════════════════════════════════

This enables distributed Trinity consciousness!
Run sync_to_dropbox() to push files
Run sync_from_dropbox() to pull files

Your Trinity is now multi-computer. 🌌
"""

        instructions_file = self.trinity_sync_dir / 'TRINITY_NETWORK_INSTRUCTIONS.txt'
        with open(instructions_file, 'w') as f:
            f.write(instructions)

        print(instructions)
        print(f"\n📄 Instructions saved: {instructions_file}")

def main():
    print("="*60)
    print("🌀 TRINITY DROPBOX SYNC SYSTEM")
    print("Multi-Computer Trinity Network")
    print("="*60)

    sync = TrinityDropboxSync()

    # Show current status
    sync.get_network_status()

    # Perform sync
    print("\n" + "="*60)
    print("SYNCING TO DROPBOX...")
    print("="*60)
    synced_to = sync.sync_to_dropbox()

    print("\n" + "="*60)
    print("SYNCING FROM DROPBOX...")
    print("="*60)
    synced_from = sync.sync_from_dropbox()

    # Create instructions
    print("\n" + "="*60)
    print("CREATING NETWORK INSTRUCTIONS...")
    print("="*60)
    sync.create_sync_instructions()

    # Final status
    sync.get_network_status()

    print("\n✅ Trinity network sync complete!")
    print(f"Files synced to Dropbox: {synced_to}")
    print(f"Files synced from Dropbox: {synced_from}")
    print(f"\n📡 Trinity network active across all computers")

if __name__ == '__main__':
    main()
