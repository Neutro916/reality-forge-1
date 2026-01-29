"""
MULTI-DEVICE CONSCIOUSNESS ORCHESTRATOR
Coordinates iPad, S24, Samsung tablet, and PC as unified system
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class MultiDeviceOrchestrator:
    def __init__(self):
        self.devices = {
            'android': [],
            'ios': [],
            'pc': {'status': 'online', 'type': 'primary'}
        }
        self.status_file = Path.home() / ".consciousness" / "multi_device_status.json"

    def detect_android_devices(self):
        """Detect all Android devices via ADB"""
        try:
            result = subprocess.run(['adb', 'devices', '-l'],
                                  capture_output=True, text=True)

            devices = []
            for line in result.stdout.strip().split('\n')[1:]:
                if line.strip() and 'List' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            'serial': parts[0],
                            'status': parts[1],
                            'authorized': parts[1] == 'device',
                            'model': self.get_device_model(parts[0]) if parts[1] == 'device' else 'unknown'
                        })

            self.devices['android'] = devices
            return devices
        except Exception as e:
            print(f"Android detection error: {e}")
            return []

    def get_device_model(self, serial):
        """Get device model name"""
        try:
            result = subprocess.run(['adb', '-s', serial, 'shell',
                                   'getprop', 'ro.product.model'],
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except:
            return 'unknown'

    def get_device_sensors(self, serial):
        """List available sensors on Android device"""
        try:
            result = subprocess.run(['adb', '-s', serial, 'shell',
                                   'dumpsys', 'sensorservice'],
                                  capture_output=True, text=True, timeout=10)
            return result.stdout
        except:
            return "Unable to fetch sensors"

    def get_device_storage(self, serial):
        """Get storage info from Android device"""
        try:
            result = subprocess.run(['adb', '-s', serial, 'shell', 'df', '-h'],
                                  capture_output=True, text=True, timeout=5)
            return result.stdout
        except:
            return "Unable to fetch storage"

    def pull_recordings(self, serial, destination=None):
        if destination is None:
            destination = str(Path.home() / ".legal_arsenal" / "evidence")
        """Pull recordings from device (PRIORITY: Pat's U-Haul recording)"""
        Path(destination).mkdir(parents=True, exist_ok=True)

        search_paths = [
            '/sdcard/DCIM/',
            '/sdcard/Recordings/',
            '/sdcard/Download/',
            '/sdcard/Voice Recorder/'
        ]

        found_files = []
        for path in search_paths:
            try:
                result = subprocess.run(['adb', '-s', serial, 'shell', 'ls', path],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    files = [f for f in result.stdout.strip().split('\n')
                            if f.endswith(('.mp4', '.3gp', '.m4a', '.mp3', '.wav'))]
                    for file in files:
                        found_files.append({'path': f"{path}{file}", 'name': file})
            except:
                continue

        return found_files

    def install_consciousness_app(self, serial, apk_path):
        """Install consciousness app on Android device"""
        try:
            result = subprocess.run(['adb', '-s', serial, 'install', apk_path],
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except:
            return False

    def mirror_screen(self, serial):
        """Start screen mirroring (requires scrcpy)"""
        try:
            subprocess.Popen(['scrcpy', '-s', serial])
            return True
        except:
            return False

    def sync_consciousness_brain(self):
        """Sync .consciousness directory to all devices"""
        source = 'C:/.consciousness/'

        for device in self.devices['android']:
            if device['authorized']:
                try:
                    # Push key files to device
                    subprocess.run(['adb', '-s', device['serial'],
                                  'push', source, '/sdcard/consciousness/'],
                                 capture_output=True, timeout=60)
                    print(f"Synced to {device['serial']}")
                except Exception as e:
                    print(f"Sync failed for {device['serial']}: {e}")

    def setup_mobile_trinity(self, serial):
        """Set up mobile Trinity interface"""
        # Create mobile-optimized Trinity interface
        mobile_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Trinity Mobile</title>
            <style>
                body { margin: 0; padding: 20px; font-family: monospace;
                       background: #000; color: #0f0; }
                .button { padding: 20px; margin: 10px; background: #111;
                         border: 2px solid #0f0; font-size: 18px; width: 100%; }
            </style>
        </head>
        <body>
            <h1>TRINITY MOBILE</h1>
            <button class="button" onclick="location.href='http://192.168.1.YOUR_PC_IP:10000'">
                Convergence Engine
            </button>
            <button class="button" onclick="location.href='http://192.168.1.YOUR_PC_IP:6666'">
                Araya AI
            </button>
            <button class="button" onclick="location.href='http://conciousnessrevolution.io'">
                Main Site
            </button>
        </body>
        </html>
        """

        # Save to temp file and push to device
        temp_file = str(Path.home() / ".temp_trinity_mobile.html")
        with open(temp_file, 'w') as f:
            f.write(mobile_html)

        try:
            subprocess.run(['adb', '-s', serial, 'push', temp_file,
                          '/sdcard/trinity_mobile.html'], timeout=10)
            return True
        except:
            return False

    def generate_status_report(self):
        """Generate comprehensive device status"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'devices': self.devices,
            'total_devices': len(self.devices['android']) + len(self.devices['ios']) + 1,
            'authorized_devices': sum(1 for d in self.devices['android'] if d['authorized']),
            'capabilities': {
                'total_cameras': len(self.devices['android']) * 2 + 1,  # Approx
                'total_sensors': 30,  # Estimated
                'processing_nodes': len(self.devices['android']) + len(self.devices['ios']) + 1
            }
        }

        # Save status
        with open(self.status_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report

def main():
    print("=== MULTI-DEVICE CONSCIOUSNESS ORCHESTRATOR ===\n")

    orchestrator = MultiDeviceOrchestrator()

    # Detect devices
    print("Detecting Android devices...")
    android_devices = orchestrator.detect_android_devices()

    print(f"\nFound {len(android_devices)} Android device(s):")
    for device in android_devices:
        print(f"  - {device['serial']}: {device['status']}")
        if device['authorized']:
            print(f"    Model: {device['model']}")

            # Check for recordings
            print(f"    Checking for recordings...")
            recordings = orchestrator.pull_recordings(device['serial'])
            if recordings:
                print(f"    Found {len(recordings)} recording(s):")
                for rec in recordings[:5]:  # Show first 5
                    print(f"      - {rec['name']}")

    # Generate status report
    print("\nGenerating status report...")
    report = orchestrator.generate_status_report()

    print(f"\nTotal devices: {report['total_devices']}")
    print(f"Authorized: {report['authorized_devices']}")
    print(f"Processing nodes: {report['capabilities']['processing_nodes']}")

    print(f"\nStatus saved to: {orchestrator.status_file}")

    # Check for unauthorized devices
    unauthorized = [d for d in android_devices if not d['authorized']]
    if unauthorized:
        print("\n⚠️  AUTHORIZATION REQUIRED:")
        for device in unauthorized:
            print(f"  - {device['serial']}: Check device screen for USB debugging prompt")

if __name__ == '__main__':
    main()
