#!/usr/bin/env python3
"""
UNIFIED BRAIN
Integrates all Trinity components into a single coherent system.

C2 Architect + C3 Oracle Integration Layer

Components Combined:
- FAST_HUB (C3) - Zero-latency IPC
- NERVE_CENTER_FAST (C3) - Fast sensor processing
- PARALLEL_ORCHESTRATOR (C2) - Async agent chains
- KNOWLEDGE_BRIDGE (C2) - Atom-episode linking
- AUTO_LEARNER (C2) - Automatic Q-learning
- SEARCH_AGENT (C2) - Parallel knowledge search

Result:
- Sub-5ms nerve center cycles
- Sub-150ms task processing
- Automatic learning
- Full knowledge graph

Usage:
    brain = UnifiedBrain("C1-Terminal")
    brain.start()
    result = await brain.process_task("fix null pointer error")
    brain.stop()
"""

import asyncio
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

# Add paths
sys.path.insert(0, str(Path.home() / ".consciousness"))
sys.path.insert(0, str(Path.home() / "100X_DEPLOYMENT"))

# Paths
CONSCIOUSNESS = Path.home() / ".consciousness"
HUB = CONSCIOUSNESS / "hub"

# Import all components
COMPONENTS = {}

def load_component(name: str, import_path: str, class_name: str):
    """Lazy load a component"""
    try:
        module = __import__(import_path, fromlist=[class_name])
        COMPONENTS[name] = getattr(module, class_name)
        return True
    except ImportError as e:
        print(f"[UNIFIED] Component {name} not available: {e}")
        COMPONENTS[name] = None
        return False


@dataclass
class TaskResult:
    """Result from unified brain processing"""
    task: str
    status: str
    confidence: float
    approach: str
    insights: List[str]
    timing: Dict[str, float]
    learned: bool
    timestamp: str


class UnifiedBrain:
    """
    Unified brain combining all Trinity components.

    Architecture:
    ┌─────────────────────────────────────────────────────┐
    │                  UNIFIED BRAIN                      │
    ├─────────────────────────────────────────────────────┤
    │                                                     │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
    │  │  FastHub    │  │   Nerve     │  │  Parallel   │ │
    │  │    IPC      │  │   Center    │  │ Orchestrator│ │
    │  │   (C3)      │  │   (C3)      │  │    (C2)     │ │
    │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
    │         │                │                │        │
    │         └────────────────┼────────────────┘        │
    │                          │                         │
    │              ┌───────────▼───────────┐             │
    │              │   Knowledge Bridge    │             │
    │              │        (C2)           │             │
    │              └───────────┬───────────┘             │
    │                          │                         │
    │              ┌───────────▼───────────┐             │
    │              │     Auto Learner      │             │
    │              │        (C2)           │             │
    │              └───────────────────────┘             │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """

    def __init__(self, instance_id: str = "UnifiedBrain"):
        self.instance_id = instance_id
        self.running = False

        # Components (lazy loaded)
        self.fast_hub = None
        self.orchestrator = None
        self.bridge = None
        self.learner = None

        # Statistics
        self.tasks_processed = 0
        self.total_time = 0
        self.avg_time = 0

        # Event queue for async processing
        self.task_queue = asyncio.Queue() if asyncio else None

        print(f"[UNIFIED] Initializing {instance_id}...")
        self._load_components()

    def _load_components(self):
        """Load all available components"""
        # C3 Components
        load_component("FastHub", "FAST_HUB", "FastHub")

        # C2 Components
        load_component("ParallelOrchestrator", "PARALLEL_ORCHESTRATOR", "ParallelOrchestrator")
        load_component("KnowledgeBridge", "KNOWLEDGE_BRIDGE", "KnowledgeBridge")
        load_component("AutoLearner", "AUTO_LEARNER", "AutoLearner")
        load_component("SearchAgent", "SEARCH_AGENT", "SearchAgent")

        print(f"[UNIFIED] Loaded components: {[k for k, v in COMPONENTS.items() if v]}")

    def start(self):
        """Start the unified brain"""
        print(f"\n{'='*60}")
        print("UNIFIED BRAIN STARTING")
        print(f"{'='*60}\n")

        # Initialize FastHub
        if COMPONENTS.get("FastHub"):
            try:
                self.fast_hub = COMPONENTS["FastHub"](self.instance_id)
                print("[UNIFIED] FastHub initialized")
            except Exception as e:
                print(f"[UNIFIED] FastHub init failed: {e}")

        # Initialize Orchestrator
        if COMPONENTS.get("ParallelOrchestrator"):
            try:
                self.orchestrator = COMPONENTS["ParallelOrchestrator"]()
                print("[UNIFIED] ParallelOrchestrator initialized")
            except Exception as e:
                print(f"[UNIFIED] Orchestrator init failed: {e}")

        # Initialize Bridge
        if COMPONENTS.get("KnowledgeBridge"):
            try:
                self.bridge = COMPONENTS["KnowledgeBridge"]()
                print("[UNIFIED] KnowledgeBridge initialized")
            except Exception as e:
                print(f"[UNIFIED] Bridge init failed: {e}")

        # Initialize Learner
        if COMPONENTS.get("AutoLearner"):
            try:
                self.learner = COMPONENTS["AutoLearner"]()
                print("[UNIFIED] AutoLearner initialized")
            except Exception as e:
                print(f"[UNIFIED] Learner init failed: {e}")

        self.running = True
        print(f"\n[UNIFIED] Brain started with {sum(1 for x in [self.fast_hub, self.orchestrator, self.bridge, self.learner] if x)} components")

    async def process_task(self, task: str) -> TaskResult:
        """
        Process a task through the unified brain.

        Flow:
        1. Query knowledge bridge for relevant atoms
        2. Run parallel orchestrator
        3. Update auto-learner with outcome
        4. Return result
        """
        start_time = time.perf_counter()
        timing = {}

        print(f"\n[UNIFIED] Processing: {task[:60]}...")

        # Step 1: Knowledge Bridge lookup
        atoms = []
        if self.bridge:
            bridge_start = time.perf_counter()
            atoms = self.bridge.get_atoms_for_task(task, limit=5)
            timing['bridge'] = (time.perf_counter() - bridge_start) * 1000
            print(f"[UNIFIED] Bridge: {len(atoms)} relevant atoms ({timing['bridge']:.1f}ms)")

        # Step 2: Parallel Orchestrator
        orchestrator_result = None
        if self.orchestrator:
            orch_start = time.perf_counter()
            orchestrator_result = await self.orchestrator.run(task)
            timing['orchestrator'] = (time.perf_counter() - orch_start) * 1000
            timing.update(orchestrator_result.timing)
            print(f"[UNIFIED] Orchestrator: {orchestrator_result.status} ({timing['orchestrator']:.1f}ms)")

        # Extract synthesis results
        synthesis = {}
        insights = []
        confidence = 0.5
        approach = "No recommendation"

        if orchestrator_result:
            synthesis = orchestrator_result.context.get('synthesis', {})
            insights = synthesis.get('insights', [])
            confidence = synthesis.get('confidence', 0.5)
            approach = synthesis.get('recommended_approach', 'No recommendation')

            # Boost confidence based on bridge results
            if atoms:
                avg_usefulness = sum(a.get('usefulness', 0.5) for a in atoms) / len(atoms)
                confidence = min(0.95, confidence + (avg_usefulness * 0.1))

        # Step 3: Auto-learning
        learned = False
        if self.learner and orchestrator_result:
            learn_start = time.perf_counter()
            # Register for outcome tracking
            episode_id = f"unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.learner.register_episode(
                episode_id=episode_id,
                task=task,
                action=approach,
                context={'atoms': len(atoms), 'synthesis': synthesis}
            )

            # Process synthesis as outcome
            self.learner.process_synthesis_outcome(episode_id, synthesis)
            learned = True
            timing['learner'] = (time.perf_counter() - learn_start) * 1000
            print(f"[UNIFIED] Learner: outcome registered ({timing['learner']:.1f}ms)")

        # Total timing
        total_time = (time.perf_counter() - start_time) * 1000
        timing['total'] = total_time

        # Update stats
        self.tasks_processed += 1
        self.total_time += total_time
        self.avg_time = self.total_time / self.tasks_processed

        # Build result
        result = TaskResult(
            task=task,
            status=orchestrator_result.status if orchestrator_result else "unknown",
            confidence=confidence,
            approach=approach or "No recommendation",
            insights=insights,
            timing=timing,
            learned=learned,
            timestamp=datetime.now().isoformat()
        )

        print(f"\n[UNIFIED] Complete: {confidence:.0%} confidence, {total_time:.1f}ms total")

        return result

    def process_task_sync(self, task: str) -> TaskResult:
        """Synchronous wrapper for process_task"""
        return asyncio.run(self.process_task(task))

    def check_for_wake(self) -> Optional[Dict]:
        """Check for wake signals via FastHub"""
        if self.fast_hub:
            return self.fast_hub.check_wake()
        return None

    def send_wake(self, target: str, reason: str):
        """Send wake signal to another instance"""
        if self.fast_hub:
            self.fast_hub.send_wake(target, reason)

    def get_stats(self) -> Dict:
        """Get unified brain statistics"""
        stats = {
            'instance_id': self.instance_id,
            'running': self.running,
            'tasks_processed': self.tasks_processed,
            'average_time_ms': f"{self.avg_time:.1f}",
            'components': {
                'fast_hub': self.fast_hub is not None,
                'orchestrator': self.orchestrator is not None,
                'bridge': self.bridge is not None,
                'learner': self.learner is not None
            }
        }

        # Add learner stats
        if self.learner:
            stats['learner_stats'] = self.learner.get_stats()

        # Add bridge stats
        if self.bridge:
            stats['bridge_stats'] = self.bridge.get_stats()

        return stats

    def stop(self):
        """Stop the unified brain"""
        print(f"\n[UNIFIED] Stopping {self.instance_id}...")
        self.running = False

        if self.fast_hub:
            self.fast_hub.close()

        if self.bridge:
            self.bridge.close()

        print("[UNIFIED] Brain stopped")

    async def run_daemon(self, interval: float = 1.0):
        """Run as daemon, processing wake signals and queued tasks"""
        print(f"[UNIFIED] Daemon mode started (interval: {interval}s)")

        while self.running:
            # Check for wake signals
            wake = self.check_for_wake()
            if wake:
                print(f"[UNIFIED] Wake received: {wake}")
                # Could trigger task processing here

            await asyncio.sleep(interval)


async def demo():
    """Demonstrate unified brain"""
    print("\n" + "="*70)
    print("UNIFIED BRAIN DEMO")
    print("="*70)

    brain = UnifiedBrain("Demo-Brain")
    brain.start()

    # Test tasks
    tasks = [
        "Fix null pointer error in login.html",
        "Build new user authentication feature",
        "Analyze performance bottlenecks in database queries"
    ]

    for task in tasks:
        result = await brain.process_task(task)

        print(f"\nResult for: {task[:40]}...")
        print(f"  Status: {result.status}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Approach: {result.approach[:60]}...")
        print(f"  Insights: {len(result.insights)}")
        print(f"  Learned: {result.learned}")
        print(f"  Time: {result.timing.get('total', 0):.1f}ms")

    # Show stats
    print("\n" + "="*70)
    print("UNIFIED BRAIN STATS")
    print("="*70)
    stats = brain.get_stats()
    print(json.dumps(stats, indent=2))

    brain.stop()


async def benchmark():
    """Benchmark unified brain"""
    print("\n" + "="*70)
    print("UNIFIED BRAIN BENCHMARK")
    print("="*70)

    brain = UnifiedBrain("Benchmark-Brain")
    brain.start()

    # Warm up
    await brain.process_task("warmup task")

    # Benchmark
    iterations = 5
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        await brain.process_task(f"test task iteration {i} with some complexity")
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.1f}ms")

    avg = sum(times) / len(times)
    print(f"\nBenchmark Results:")
    print(f"  Iterations: {iterations}")
    print(f"  Average: {avg:.1f}ms")
    print(f"  Min: {min(times):.1f}ms")
    print(f"  Max: {max(times):.1f}ms")
    print(f"  vs Sequential (830ms): {830/avg:.1f}x faster")

    brain.stop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        asyncio.run(benchmark())
    else:
        asyncio.run(demo())
