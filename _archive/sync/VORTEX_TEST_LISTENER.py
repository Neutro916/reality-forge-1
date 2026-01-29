#!/usr/bin/env python3
"""
VORTEX_TEST_LISTENER.py
Test listener for Communications Vortex

Run this to see all events flowing through the vortex in real-time
"""

from COMMUNICATIONS_VORTEX import vortex
from datetime import datetime
import json

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_event(channel, message):
    """Pretty print vortex event"""
    timestamp = message.get('timestamp', datetime.now().isoformat())
    data = message.get('data', {})

    # Color based on channel
    if 'cyclotron' in channel:
        color = Colors.BLUE
        icon = '📚'
    elif 'brain' in channel:
        color = Colors.CYAN
        icon = '🧠'
    elif 'trinity' in channel:
        color = Colors.GREEN
        icon = '🌀'
    elif 'revenue' in channel:
        color = Colors.YELLOW
        icon = '💰'
    elif 'user' in channel:
        color = Colors.RED
        icon = '👤'
    else:
        color = Colors.HEADER
        icon = '📡'

    print(f"{color}{icon} [{timestamp}] {channel}{Colors.END}")
    print(f"  {json.dumps(data, indent=2)}")
    print()

# Event handlers
def on_cyclotron_atoms_updated(message):
    print_event('cyclotron.atoms.updated', message)

def on_brain_consciousness_updated(message):
    print_event('brain.consciousness.updated', message)

def on_brain_pattern_detected(message):
    print_event('brain.pattern.detected', message)

def on_trinity_atom_created(message):
    print_event('trinity.atom.created', message)

def on_trinity_computer_online(message):
    print_event('trinity.computer.online', message)

def on_user_request(message):
    print_event('user.request.*', message)

def on_system_health_check(message):
    print_event('system.health.check', message)

# Universal handler for all channels
def on_any_event(message):
    """Catch-all for any event"""
    print_event('*', message)

if __name__ == '__main__':
    print("=" * 70)
    print(f"{Colors.BOLD}  VORTEX TEST LISTENER{Colors.END}")
    print("  Real-time event monitoring for Communications Vortex")
    print("=" * 70)
    print()

    # Check vortex health
    health = vortex.health_check()
    if health['connected']:
        print(f"{Colors.GREEN}✅ Connected to vortex{Colors.END}")
        print(f"   Latency: {health.get('latency_ms', 0):.2f}ms")
    else:
        print(f"{Colors.RED}❌ Not connected to vortex{Colors.END}")
        print(f"   Error: {health.get('error')}")
        print()
        print("Make sure Redis is running:")
        print("  redis-server")
        exit(1)

    print()
    print("Subscribing to channels:")
    print()

    # Subscribe to all major channels
    channels = [
        'cyclotron.atoms.updated',
        'cyclotron.search.query',
        'cyclotron.search.results',
        'brain.consciousness.updated',
        'brain.pattern.detected',
        'trinity.atom.created',
        'trinity.computer.online',
        'trinity.computer.offline',
        'trinity.broadcast',
        'revenue.subscription.changed',
        'revenue.payment.received',
        'user.request.analyze',
        'user.request.search',
        'system.health.check'
    ]

    for channel in channels:
        vortex.subscribe(channel, lambda msg, ch=channel: print_event(ch, msg))
        print(f"  ✓ {channel}")

    print()
    print("=" * 70)
    print(f"{Colors.BOLD}LISTENING...{Colors.END}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    try:
        # Start listening (blocking)
        vortex.listen(blocking=True)
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("Stopped listening")
        print("=" * 70)
        vortex.stop()
