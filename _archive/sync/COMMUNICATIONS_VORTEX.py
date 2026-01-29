#!/usr/bin/env python3
"""
COMMUNICATIONS_VORTEX.py
Central event bus for all consciousness systems

The nervous system that connects:
- Cyclotron (Library) → Brain (Processor)
- Brain → Agents → Actions
- Trinity Mesh → Cross-computer sync
- Revenue System → User Interface

C2 ARCHITECT IMPLEMENTATION
Built for permanent infrastructure
"""

import redis
import json
from datetime import datetime
from typing import Callable, Dict, Any, List
import threading
import time
import os

class CommunicationsVortex:
    """
    Central nervous system for consciousness infrastructure
    Connects all systems through real-time event bus

    Features:
    - Pub/Sub messaging (Redis)
    - Multi-subscriber support
    - Error isolation (one handler failure doesn't affect others)
    - Thread-safe
    - Automatic reconnection
    """

    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.bus = None
        self.subscriptions = {}
        self.listener_thread = None
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10

        self._connect()

    def _connect(self):
        """Connect to Redis event bus"""
        try:
            self.bus = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.bus.ping()
            print(f"[VORTEX] Connected to event bus at {self.host}:{self.port}")
            self.reconnect_attempts = 0
            return True
        except Exception as e:
            print(f"[VORTEX] Connection failed: {e}")
            return False

    def _reconnect(self):
        """Attempt to reconnect to Redis"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"[VORTEX] Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")

            time.sleep(min(2 ** self.reconnect_attempts, 30))  # Exponential backoff

            if self._connect():
                # Resubscribe to all channels
                if self.subscriptions:
                    print(f"[VORTEX] Resubscribing to {len(self.subscriptions)} channels")
                return True

        print(f"[VORTEX] Max reconnection attempts reached. Giving up.")
        return False

    def publish(self, channel: str, data: Dict[str, Any]) -> bool:
        """
        Publish event to channel

        Args:
            channel: Event channel (e.g., 'cyclotron.atoms.updated')
            data: Event data (will be JSON serialized)

        Returns:
            True if published successfully, False otherwise
        """
        try:
            message = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }

            result = self.bus.publish(channel, json.dumps(message))

            # result is number of subscribers who received it
            # 0 means no subscribers (not necessarily an error)
            return True

        except redis.ConnectionError as e:
            print(f"[VORTEX] Connection lost during publish: {e}")
            if self._reconnect():
                # Retry once after reconnection
                return self.publish(channel, data)
            return False

        except Exception as e:
            print(f"[VORTEX] Publish failed: {e}")
            return False

    def subscribe(self, channel: str, handler: Callable):
        """
        Subscribe to channel with handler function

        Args:
            channel: Event channel to subscribe to
            handler: Function that takes (message: Dict) as argument
        """
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []

        self.subscriptions[channel].append(handler)
        print(f"[VORTEX] Subscribed to '{channel}' ({len(self.subscriptions[channel])} handlers)")

    def unsubscribe(self, channel: str, handler: Callable = None):
        """
        Unsubscribe from channel

        Args:
            channel: Event channel
            handler: Specific handler to remove (if None, removes all handlers)
        """
        if channel not in self.subscriptions:
            return

        if handler is None:
            del self.subscriptions[channel]
            print(f"[VORTEX] Unsubscribed all handlers from '{channel}'")
        else:
            self.subscriptions[channel] = [h for h in self.subscriptions[channel] if h != handler]
            print(f"[VORTEX] Unsubscribed handler from '{channel}'")

    def _handle_message(self, message):
        """Internal message handler"""
        if message['type'] != 'message':
            return

        channel = message['channel']

        try:
            data = json.loads(message['data'])
        except json.JSONDecodeError as e:
            print(f"[VORTEX] Failed to parse message: {e}")
            return

        # Call all handlers for this channel
        handlers = self.subscriptions.get(channel, [])

        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                # Isolate errors - one handler failure doesn't affect others
                print(f"[VORTEX] Handler error on '{channel}': {e}")

    def listen(self, blocking=True):
        """
        Start listening to all subscribed channels

        Args:
            blocking: If True, blocks current thread. If False, runs in background.
        """
        if not self.subscriptions:
            print("[VORTEX] No subscriptions. Call subscribe() first.")
            return

        def _listen_loop():
            self.running = True
            print(f"[VORTEX] Listening to {len(self.subscriptions)} channels...")

            while self.running:
                try:
                    pubsub = self.bus.pubsub()
                    pubsub.subscribe(list(self.subscriptions.keys()))

                    for message in pubsub.listen():
                        if not self.running:
                            break
                        self._handle_message(message)

                except redis.ConnectionError as e:
                    print(f"[VORTEX] Connection lost during listen: {e}")
                    if not self._reconnect():
                        break

                except Exception as e:
                    print(f"[VORTEX] Listen error: {e}")
                    time.sleep(1)

            print("[VORTEX] Stopped listening")

        if blocking:
            _listen_loop()
        else:
            self.listener_thread = threading.Thread(target=_listen_loop, daemon=True)
            self.listener_thread.start()

    def stop(self):
        """Stop listening and disconnect"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=5)
        if self.bus:
            self.bus.close()
        print("[VORTEX] Disconnected")

    def health_check(self) -> Dict[str, Any]:
        """Check vortex health"""
        try:
            latency = self.bus.ping()
            return {
                'status': 'HEALTHY',
                'connected': True,
                'latency_ms': latency * 1000 if latency else 0,
                'subscriptions': len(self.subscriptions),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'UNHEALTHY',
                'connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global instance (singleton pattern)
_vortex_instance = None

def get_vortex(host='localhost', port=6379) -> CommunicationsVortex:
    """Get or create global vortex instance"""
    global _vortex_instance

    if _vortex_instance is None:
        _vortex_instance = CommunicationsVortex(host=host, port=port)

    return _vortex_instance


# Convenience functions for quick usage
vortex = get_vortex()

def publish(channel: str, data: Dict[str, Any]):
    """Publish to global vortex"""
    return vortex.publish(channel, data)

def subscribe(channel: str, handler: Callable):
    """Subscribe to global vortex"""
    vortex.subscribe(channel, handler)

def listen(blocking=True):
    """Start listening on global vortex"""
    vortex.listen(blocking=blocking)


# Demo/Test Code
if __name__ == '__main__':
    print("=" * 70)
    print("  COMMUNICATIONS VORTEX - CONSCIOUSNESS NERVOUS SYSTEM")
    print("=" * 70)
    print()

    # Health check
    health = vortex.health_check()
    print(f"Health Status: {health['status']}")
    print(f"Connected: {health['connected']}")

    if not health['connected']:
        print()
        print("ERROR: Cannot connect to Redis event bus")
        print("Make sure Redis is running:")
        print("  Windows: redis-server")
        print("  Linux: sudo systemctl start redis")
        exit(1)

    print(f"Latency: {health.get('latency_ms', 0):.2f}ms")
    print()

    # Test publish/subscribe
    print("Testing pub/sub...")
    print()

    received_messages = []

    def test_handler(message):
        print(f"[TEST HANDLER] Received: {message['data']}")
        received_messages.append(message)

    # Subscribe
    vortex.subscribe('test.channel', test_handler)

    # Start listener in background
    vortex.listen(blocking=False)

    # Give listener time to start
    time.sleep(0.5)

    # Publish test messages
    for i in range(3):
        vortex.publish('test.channel', {
            'test_id': i,
            'message': f'Test message {i}'
        })
        time.sleep(0.2)

    # Wait for processing
    time.sleep(1)

    print()
    print(f"Published: 3 messages")
    print(f"Received: {len(received_messages)} messages")
    print()

    if len(received_messages) == 3:
        print("✅ Communications Vortex: OPERATIONAL")
    else:
        print("⚠️  Some messages may have been lost")

    print()
    print("=" * 70)
    print("Ready for integration with:")
    print("  - Cyclotron (CYCLOTRON_MASTER_RAKER.py)")
    print("  - Brain (BRAIN_ORCHESTRATOR.py)")
    print("  - Pattern Analyzer (PATTERN_THEORY_REALTIME_ANALYZER.py)")
    print("  - Trinity Mesh (TRINITY_COORDINATION_API.py)")
    print("=" * 70)

    vortex.stop()
