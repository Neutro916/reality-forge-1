#!/usr/bin/env python3
"""
VORTEX_INTEGRATION_KIT.py
Helper utilities for integrating systems with Communications Vortex

Provides drop-in integration for:
- Cyclotron
- Brain Orchestrator
- Pattern Theory Analyzer
- Trinity Mesh
- Any custom system

C2 ARCHITECT IMPLEMENTATION
"""

from COMMUNICATIONS_VORTEX import get_vortex
from datetime import datetime
import json
import os
from typing import Dict, Any, Callable

vortex = get_vortex()


class CyclotronIntegrator:
    """
    Integrates Cyclotron with Communications Vortex

    Drop this into CYCLOTRON_MASTER_RAKER.py:

    from VORTEX_INTEGRATION_KIT import CyclotronIntegrator
    integrator = CyclotronIntegrator()
    integrator.publish_atoms_updated(total_atoms=5531, new_atoms=142)
    """

    def __init__(self):
        self.vortex = vortex

    def publish_atoms_updated(self, total_atoms: int, new_atoms: int = 0):
        """Publish when atoms are updated"""
        self.vortex.publish('cyclotron.atoms.updated', {
            'total_atoms': total_atoms,
            'new_atoms': new_atoms,
            'source': 'CYCLOTRON_MASTER_RAKER',
            'timestamp': datetime.now().isoformat()
        })

    def publish_search_results(self, request_id: str, results: list):
        """Publish search results"""
        self.vortex.publish('cyclotron.search.results', {
            'request_id': request_id,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        })

    def subscribe_to_search_requests(self, handler: Callable):
        """Subscribe to search requests from vortex"""
        self.vortex.subscribe('cyclotron.search.query', handler)


class BrainIntegrator:
    """
    Integrates Brain systems with Communications Vortex

    Drop this into BRAIN_ORCHESTRATOR.py:

    from VORTEX_INTEGRATION_KIT import BrainIntegrator
    integrator = BrainIntegrator()
    integrator.publish_consciousness_updated(metrics)
    integrator.subscribe_to_atom_updates(on_atoms_updated)
    """

    def __init__(self):
        self.vortex = vortex

    def publish_consciousness_updated(self, metrics: Dict[str, Any]):
        """Publish when consciousness metrics are updated"""
        self.vortex.publish('brain.consciousness.updated', {
            'consciousness_level': metrics.get('consciousness_level', 0),
            'eight_components': metrics.get('eight_components_aggregate', {}),
            'domain_alignment': metrics.get('domain_frequency', {}),
            'timestamp': datetime.now().isoformat()
        })

    def publish_pattern_detected(self, pattern: Dict[str, Any]):
        """Publish when Pattern Theory pattern is detected"""
        self.vortex.publish('brain.pattern.detected', {
            'pattern_type': pattern.get('pattern_type'),
            'pattern_name': pattern.get('pattern_name'),
            'confidence': pattern.get('confidence'),
            'danger_level': pattern.get('danger_level'),
            'neutralization': pattern.get('neutralization'),
            'timestamp': datetime.now().isoformat()
        })

    def subscribe_to_atom_updates(self, handler: Callable):
        """Subscribe to Cyclotron atom updates"""
        self.vortex.subscribe('cyclotron.atoms.updated', handler)

    def subscribe_to_user_requests(self, handler: Callable):
        """Subscribe to user analysis requests"""
        self.vortex.subscribe('user.request.analyze', handler)


class TrinityIntegrator:
    """
    Integrates Trinity mesh with Communications Vortex

    Drop this into TRINITY_COORDINATION_API.py:

    from VORTEX_INTEGRATION_KIT import TrinityIntegrator
    integrator = TrinityIntegrator(computer_id='C1')
    integrator.publish_computer_online()
    integrator.publish_atom_created(atom)
    """

    def __init__(self, computer_id: str):
        self.vortex = vortex
        self.computer_id = computer_id

    def publish_computer_online(self):
        """Announce this computer is online"""
        self.vortex.publish('trinity.computer.online', {
            'computer_id': self.computer_id,
            'timestamp': datetime.now().isoformat()
        })

    def publish_computer_offline(self):
        """Announce this computer is going offline"""
        self.vortex.publish('trinity.computer.offline', {
            'computer_id': self.computer_id,
            'timestamp': datetime.now().isoformat()
        })

    def publish_atom_created(self, atom: Dict[str, Any]):
        """Publish when new atom is created (for cross-computer sync)"""
        self.vortex.publish('trinity.atom.created', {
            'source_computer': self.computer_id,
            'atom_id': atom.get('id'),
            'atom': atom,
            'timestamp': datetime.now().isoformat()
        })

    def publish_sync_conflict(self, conflict: Dict[str, Any]):
        """Publish when sync conflict is detected"""
        self.vortex.publish('trinity.sync.conflict', {
            'computer_id': self.computer_id,
            'conflict': conflict,
            'timestamp': datetime.now().isoformat()
        })

    def subscribe_to_remote_atoms(self, handler: Callable):
        """Subscribe to atoms created on other computers"""
        def filtered_handler(message):
            # Don't process our own atoms
            if message['data'].get('source_computer') != self.computer_id:
                handler(message)

        self.vortex.subscribe('trinity.atom.created', filtered_handler)

    def subscribe_to_broadcasts(self, handler: Callable):
        """Subscribe to broadcast messages"""
        self.vortex.subscribe('trinity.broadcast', handler)


class RevenueIntegrator:
    """
    Integrates revenue/monetization systems with Communications Vortex
    """

    def __init__(self):
        self.vortex = vortex

    def publish_subscription_changed(self, user_id: str, tier: str, action: str):
        """Publish subscription change"""
        self.vortex.publish('revenue.subscription.changed', {
            'user_id': user_id,
            'tier': tier,
            'action': action,  # 'created', 'upgraded', 'downgraded', 'cancelled'
            'timestamp': datetime.now().isoformat()
        })

    def publish_payment_received(self, user_id: str, amount: float):
        """Publish payment received"""
        self.vortex.publish('revenue.payment.received', {
            'user_id': user_id,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        })

    def subscribe_to_consciousness_updates(self, handler: Callable):
        """Subscribe to consciousness updates (for dynamic pricing)"""
        self.vortex.subscribe('brain.consciousness.updated', handler)


class SystemHealthMonitor:
    """
    Monitor system health via vortex events
    """

    def __init__(self):
        self.vortex = vortex
        self.health_data = {
            'cyclotron': {'status': 'UNKNOWN', 'last_seen': None},
            'brain': {'status': 'UNKNOWN', 'last_seen': None},
            'trinity': {'status': 'UNKNOWN', 'last_seen': None},
            'revenue': {'status': 'UNKNOWN', 'last_seen': None}
        }

    def start_monitoring(self):
        """Start monitoring all systems"""
        # Subscribe to system health checks
        self.vortex.subscribe('system.health.check', self._on_health_check)

        # Subscribe to system-specific events to track activity
        self.vortex.subscribe('cyclotron.atoms.updated', lambda m: self._mark_alive('cyclotron'))
        self.vortex.subscribe('brain.consciousness.updated', lambda m: self._mark_alive('brain'))
        self.vortex.subscribe('trinity.computer.online', lambda m: self._mark_alive('trinity'))
        self.vortex.subscribe('revenue.subscription.changed', lambda m: self._mark_alive('revenue'))

        print("[HEALTH MONITOR] Monitoring started")

    def _mark_alive(self, system: str):
        """Mark system as alive"""
        if system in self.health_data:
            self.health_data[system]['status'] = 'ONLINE'
            self.health_data[system]['last_seen'] = datetime.now().isoformat()

    def _on_health_check(self, message):
        """Handle health check event"""
        system = message['data'].get('system')
        if system in self.health_data:
            self.health_data[system]['status'] = message['data'].get('status', 'UNKNOWN')
            self.health_data[system]['last_seen'] = datetime.now().isoformat()

    def get_health_report(self) -> Dict[str, Any]:
        """Get current health report"""
        return {
            'systems': self.health_data,
            'overall_status': 'HEALTHY' if all(
                s['status'] == 'ONLINE' for s in self.health_data.values()
            ) else 'DEGRADED',
            'timestamp': datetime.now().isoformat()
        }

    def publish_health(self, system: str, status: str):
        """Publish health check for a system"""
        self.vortex.publish('system.health.check', {
            'system': system,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })


# Quick integration examples
def integrate_cyclotron():
    """Example: Integrate Cyclotron"""
    cyclotron = CyclotronIntegrator()

    # After raking atoms
    total_atoms = 5531
    new_atoms = 142
    cyclotron.publish_atoms_updated(total_atoms, new_atoms)

    # Handle search requests
    def on_search(message):
        query = message['data']['query']
        request_id = message['data']['request_id']

        # Perform search
        results = []  # Your search logic here

        cyclotron.publish_search_results(request_id, results)

    cyclotron.subscribe_to_search_requests(on_search)


def integrate_brain():
    """Example: Integrate Brain Orchestrator"""
    brain = BrainIntegrator()

    # After processing atoms
    metrics = {
        'consciousness_level': 88.9,
        'eight_components_aggregate': {
            'Mission': 0.85,
            'Structure': 0.82,
            # ... etc
        },
        'domain_frequency': {
            'Computer': 1250,
            'Consciousness': 980,
            # ... etc
        }
    }
    brain.publish_consciousness_updated(metrics)

    # After detecting pattern
    pattern = {
        'pattern_type': 'CIRCULAR_DEPENDENCY',
        'pattern_name': 'Circular Dependency Loop',
        'confidence': 85,
        'danger_level': 'CRITICAL',
        'neutralization': 'Create external entry point'
    }
    brain.publish_pattern_detected(pattern)

    # Listen for new atoms
    def on_atoms_updated(message):
        total = message['data']['total_atoms']
        print(f"[BRAIN] Processing {total} new atoms")
        # Trigger reprocessing

    brain.subscribe_to_atom_updates(on_atoms_updated)


def integrate_trinity():
    """Example: Integrate Trinity mesh"""
    trinity = TrinityIntegrator(computer_id='C1')

    # On startup
    trinity.publish_computer_online()

    # When creating atom
    new_atom = {
        'id': 'atom_12345',
        'content': 'Pattern Theory knowledge',
        'timestamp': datetime.now().isoformat()
    }
    trinity.publish_atom_created(new_atom)

    # Listen for atoms from other computers
    def on_remote_atom(message):
        atom = message['data']['atom']
        source = message['data']['source_computer']
        print(f"[TRINITY] Received atom from {source}: {atom['id']}")
        # Save locally

    trinity.subscribe_to_remote_atoms(on_remote_atom)


# Demo
if __name__ == '__main__':
    print("=" * 70)
    print("  VORTEX INTEGRATION KIT")
    print("=" * 70)
    print()

    print("Available integrators:")
    print("  - CyclotronIntegrator")
    print("  - BrainIntegrator")
    print("  - TrinityIntegrator")
    print("  - RevenueIntegrator")
    print("  - SystemHealthMonitor")
    print()

    print("Example usage:")
    print()
    print("# Cyclotron integration")
    print("from VORTEX_INTEGRATION_KIT import CyclotronIntegrator")
    print("integrator = CyclotronIntegrator()")
    print("integrator.publish_atoms_updated(total_atoms=5531, new_atoms=142)")
    print()

    print("# Brain integration")
    print("from VORTEX_INTEGRATION_KIT import BrainIntegrator")
    print("integrator = BrainIntegrator()")
    print("integrator.publish_consciousness_updated(metrics)")
    print()

    print("# Trinity integration")
    print("from VORTEX_INTEGRATION_KIT import TrinityIntegrator")
    print("integrator = TrinityIntegrator(computer_id='C1')")
    print("integrator.publish_computer_online()")
    print()

    print("=" * 70)
    print("Integration kit ready for deployment")
    print("=" * 70)
