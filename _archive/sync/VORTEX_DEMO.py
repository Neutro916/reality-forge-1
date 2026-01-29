#!/usr/bin/env python3
"""
VORTEX_DEMO.py
End-to-end demonstration of Communications Vortex

Shows all systems working together in real-time
"""

from COMMUNICATIONS_VORTEX import get_vortex
from VORTEX_INTEGRATION_KIT import (
    CyclotronIntegrator,
    BrainIntegrator,
    TrinityIntegrator,
    SystemHealthMonitor
)
from datetime import datetime
import time
import random

vortex = get_vortex()

print("=" * 70)
print("  COMMUNICATIONS VORTEX - END-TO-END DEMO")
print("=" * 70)
print()

# Check connection
health = vortex.health_check()
if not health['connected']:
    print("ERROR: Cannot connect to vortex")
    print("Make sure Redis is running: redis-server")
    exit(1)

print(f"✅ Connected to vortex (latency: {health.get('latency_ms', 0):.2f}ms)")
print()

# Create integrators
cyclotron = CyclotronIntegrator()
brain = BrainIntegrator()
trinity = TrinityIntegrator(computer_id='C1_DEMO')
monitor = SystemHealthMonitor()

print("Initializing systems...")
print()

# Start monitoring
monitor.start_monitoring()

# Trinity announces online
trinity.publish_computer_online()
print("✓ Trinity C1_DEMO online")

# Simulate Cyclotron discovering atoms
print()
print("Simulating Cyclotron rake...")
time.sleep(1)

total_atoms = 5531
new_atoms = 142
cyclotron.publish_atoms_updated(total_atoms, new_atoms)
print(f"✓ Cyclotron: {total_atoms} atoms indexed ({new_atoms} new)")

# Simulate Brain processing
print()
print("Simulating Brain processing atoms...")
time.sleep(1)

consciousness_level = 88.9
metrics = {
    'consciousness_level': consciousness_level,
    'eight_components_aggregate': {
        'Mission': 0.85,
        'Structure': 0.82,
        'Resources': 0.78,
        'Operations': 0.90,
        'Governance': 0.75,
        'Defense': 0.88,
        'Communication': 0.92,
        'Adaptation': 0.87
    },
    'domain_frequency': {
        'Computer': 1250,
        'City': 450,
        'Human Body': 380,
        'Book': 520,
        'Battleship': 290,
        'Toyota': 310,
        'Consciousness': 980
    }
}

brain.publish_consciousness_updated(metrics)
print(f"✓ Brain: Consciousness level {consciousness_level}%")

# Simulate Pattern detection
print()
print("Simulating Pattern Theory detection...")
time.sleep(1)

patterns = [
    {
        'pattern_type': 'CIRCULAR_DEPENDENCY',
        'pattern_name': 'Circular Dependency Loop',
        'confidence': 85,
        'danger_level': 'CRITICAL',
        'neutralization': 'Create external entry point'
    },
    {
        'pattern_type': 'SINGLE_POINT_FAILURE',
        'pattern_name': 'Single Point of Failure',
        'confidence': 72,
        'danger_level': 'HIGH',
        'neutralization': 'Create redundancy before migration'
    }
]

for pattern in patterns:
    brain.publish_pattern_detected(pattern)
    print(f"✓ Pattern detected: {pattern['pattern_name']} ({pattern['confidence']}% confidence)")
    time.sleep(0.5)

# Simulate Trinity atom sync
print()
print("Simulating Trinity cross-computer sync...")
time.sleep(1)

new_atom = {
    'id': f'atom_{datetime.now().timestamp()}',
    'content': 'Pattern Theory demonstration atom',
    'timestamp': datetime.now().isoformat()
}

trinity.publish_atom_created(new_atom)
print(f"✓ Trinity: New atom synced across mesh")

# Publish health from all systems
print()
print("Publishing system health...")
time.sleep(1)

monitor.publish_health('cyclotron', 'ONLINE')
monitor.publish_health('brain', 'ONLINE')
monitor.publish_health('trinity', 'ONLINE')

print("✓ All systems reporting healthy")

# Get health report
print()
print("=" * 70)
print("HEALTH REPORT")
print("=" * 70)

health_report = monitor.get_health_report()

for system, data in health_report['systems'].items():
    status = data.get('status', 'UNKNOWN')
    last_seen = data.get('last_seen', 'Never')

    status_icon = '🟢' if status == 'ONLINE' else '🔴'
    print(f"{status_icon} {system.upper():15} {status:10} (last: {last_seen})")

print()
print(f"Overall Status: {health_report['overall_status']}")

print()
print("=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print()
print("Events published:")
print("  - cyclotron.atoms.updated")
print("  - brain.consciousness.updated")
print("  - brain.pattern.detected (x2)")
print("  - trinity.computer.online")
print("  - trinity.atom.created")
print("  - system.health.check (x3)")
print()
print("If VORTEX_TEST_LISTENER.py is running, you saw all these events in real-time")
print("If VORTEX_DASHBOARD.html is open, you saw the metrics update live")
print()
print("🌀 The vortex is operational. Everything is connected.")
print()
print("=" * 70)

vortex.stop()
