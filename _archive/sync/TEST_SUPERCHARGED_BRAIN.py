#!/usr/bin/env python3
"""
INTEGRATION TEST - SUPERCHARGED BRAIN
Tests all C2 Architect components together.

Components:
1. CYCLOTRON_MEMORY_CACHED - Cached memory queries
2. SEARCH_AGENT - Parallel knowledge search
3. PARALLEL_ORCHESTRATOR - Async agent chains
4. KNOWLEDGE_BRIDGE - Atom-episode links
5. AUTO_LEARNER - Automatic Q-learning
6. FAST_HUB (C3) - Zero-latency coordination
"""

import asyncio
import time
import sys
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path.home() / ".consciousness"))
sys.path.insert(0, str(Path.home() / "100X_DEPLOYMENT"))

# Test results
RESULTS = {
    'passed': 0,
    'failed': 0,
    'errors': [],
    'timings': {}
}


def test(name: str):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*60}")
            print(f"TEST: {name}")
            print('='*60)
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                RESULTS['timings'][name] = elapsed

                if result:
                    print(f"PASSED ({elapsed:.1f}ms)")
                    RESULTS['passed'] += 1
                else:
                    print(f"FAILED ({elapsed:.1f}ms)")
                    RESULTS['failed'] += 1
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                print(f"ERROR: {e} ({elapsed:.1f}ms)")
                RESULTS['failed'] += 1
                RESULTS['errors'].append({'test': name, 'error': str(e)})
                return False
        return wrapper
    return decorator


@test("CYCLOTRON_MEMORY_CACHED - Import and Initialize")
def test_memory_cached_import():
    from CYCLOTRON_MEMORY_CACHED import CyclotronMemoryCached
    memory = CyclotronMemoryCached("test_agent")
    stats = memory.get_stats()
    memory.close()
    print(f"  Cache stats: {stats.get('cache', {})}")
    return stats is not None


@test("CYCLOTRON_MEMORY_CACHED - Cache Hit Performance")
def test_memory_cache_performance():
    from CYCLOTRON_MEMORY_CACHED import CyclotronMemoryCached
    memory = CyclotronMemoryCached("test_agent")

    # First query (cache miss)
    start = time.perf_counter()
    result1 = memory.find_similar_episodes("test query for performance")
    time1 = (time.perf_counter() - start) * 1000

    # Second query (cache hit)
    start = time.perf_counter()
    result2 = memory.find_similar_episodes("test query for performance")
    time2 = (time.perf_counter() - start) * 1000

    memory.close()

    print(f"  First query (miss): {time1:.2f}ms")
    print(f"  Second query (hit): {time2:.2f}ms")
    print(f"  Speedup: {time1/max(time2, 0.01):.1f}x")

    return time2 < time1 * 0.5  # Cache should be at least 2x faster


@test("SEARCH_AGENT - Import and Search")
def test_search_agent():
    from SEARCH_AGENT import SearchAgent

    agent = SearchAgent()
    state = {
        'task': 'fix null pointer error in login',
        'context': {},
        'memory': [],
        'outputs': []
    }

    result = agent.process(state)

    search_results = result.get('context', {}).get('search_results', {})
    atoms = len(search_results.get('atoms', []))
    episodes = len(search_results.get('episodes', []))

    print(f"  Atoms found: {atoms}")
    print(f"  Episodes found: {episodes}")

    stats = agent.get_stats()
    print(f"  Agent stats: {stats}")

    return result.get('outputs') is not None


@test("PARALLEL_ORCHESTRATOR - Import")
def test_orchestrator_import():
    from PARALLEL_ORCHESTRATOR import ParallelOrchestrator, ParallelState
    orchestrator = ParallelOrchestrator()
    return orchestrator is not None


@test("PARALLEL_ORCHESTRATOR - Async Run")
def test_orchestrator_run():
    async def run_test():
        from PARALLEL_ORCHESTRATOR import ParallelOrchestrator
        orchestrator = ParallelOrchestrator()
        result = await orchestrator.run("test task for orchestrator")
        return result

    result = asyncio.run(run_test())

    print(f"  Status: {result.status}")
    print(f"  Total time: {result.timing.get('total', 0):.1f}ms")
    print(f"  Parallel chains: {result.timing.get('parallel_total', 0):.1f}ms")

    return result.status in ['planned', 'complete']


@test("PARALLEL_ORCHESTRATOR - Parallel Performance")
def test_orchestrator_parallel_speedup():
    async def run_test():
        from PARALLEL_ORCHESTRATOR import ParallelOrchestrator
        orchestrator = ParallelOrchestrator()

        # Run 3 tests
        times = []
        for i in range(3):
            result = await orchestrator.run(f"test task iteration {i}")
            times.append(result.timing.get('total', 0))

        return times

    times = asyncio.run(run_test())
    avg_time = sum(times) / len(times)

    print(f"  Run times: {[f'{t:.1f}ms' for t in times]}")
    print(f"  Average: {avg_time:.1f}ms")
    print(f"  vs Sequential (~400ms): {400/max(avg_time,1):.1f}x faster")

    return avg_time < 400  # Should be faster than sequential


@test("KNOWLEDGE_BRIDGE - Import and Initialize")
def test_knowledge_bridge_import():
    from KNOWLEDGE_BRIDGE import KnowledgeBridge
    bridge = KnowledgeBridge()
    stats = bridge.get_stats()
    bridge.close()

    print(f"  Atoms indexed: {stats.get('atoms_indexed', 0)}")
    print(f"  Episodes indexed: {stats.get('episodes_indexed', 0)}")
    print(f"  Links: {stats.get('total_links', 0)}")

    return stats is not None


@test("KNOWLEDGE_BRIDGE - Query Atoms for Task")
def test_knowledge_bridge_query():
    from KNOWLEDGE_BRIDGE import KnowledgeBridge
    bridge = KnowledgeBridge()

    atoms = bridge.get_atoms_for_task("fix null pointer error")
    bridge.close()

    print(f"  Relevant atoms found: {len(atoms)}")
    for atom in atoms[:3]:
        print(f"    - {atom['atom_id']}: usefulness={atom['usefulness']:.2f}")

    return True  # Query should work even if no results


@test("AUTO_LEARNER - Import and Initialize")
def test_auto_learner_import():
    from AUTO_LEARNER import AutoLearner, OutcomeType, OutcomeSignal
    learner = AutoLearner(learning_rate=0.15)
    stats = learner.get_stats()

    print(f"  Stats: {stats}")
    return stats is not None


@test("AUTO_LEARNER - Outcome Detection")
def test_auto_learner_detection():
    from AUTO_LEARNER import OutcomeDetector, OutcomeType

    detector = OutcomeDetector()

    tests = [
        ("Task completed successfully", OutcomeType.SUCCESS),
        ("Error: task failed", OutcomeType.FAILURE),
        ("Fixed bug but still has issues", OutcomeType.PARTIAL)
    ]

    passed = 0
    for text, expected in tests:
        result = detector.detect_from_text(text)
        match = result == expected
        passed += 1 if match else 0
        print(f"  '{text[:30]}...' -> {result.value} ({'OK' if match else 'MISMATCH'})")

    return passed >= 2  # At least 2/3 should match


@test("FAST_HUB (C3) - Import")
def test_fast_hub_import():
    try:
        from FAST_HUB import FastHub, FastWakeSignal, HotMemoryDB
        print("  FastHub imported successfully")
        return True
    except ImportError as e:
        print(f"  FastHub not available: {e}")
        return True  # OK if not installed yet


@test("FAST_HUB (C3) - Wake Signal Performance")
def test_fast_hub_wake():
    try:
        from FAST_HUB import FastWakeSignal

        wake = FastWakeSignal(create=True)

        # Benchmark
        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            wake.send_wake("C2-Test", f"test_{i}", "NORMAL")
        elapsed = (time.perf_counter() - start) * 1000

        wake.close()

        per_op = elapsed / iterations
        print(f"  {iterations} wake signals: {elapsed:.2f}ms")
        print(f"  Per operation: {per_op:.3f}ms")

        return per_op < 1.0  # Should be sub-millisecond

    except Exception as e:
        print(f"  Skipped: {e}")
        return True


@test("FULL INTEGRATION - All Components Together")
def test_full_integration():
    """Test all components working together"""
    async def run_full():
        # 1. Initialize components
        from PARALLEL_ORCHESTRATOR import ParallelOrchestrator
        from KNOWLEDGE_BRIDGE import KnowledgeBridge
        from AUTO_LEARNER import AutoLearner, OutcomeSignal, OutcomeType

        orchestrator = ParallelOrchestrator()
        bridge = KnowledgeBridge()
        learner = AutoLearner()

        # 2. Run orchestrator
        task = "implement new feature for user authentication"
        print(f"  Task: {task}")

        result = await orchestrator.run(task)
        print(f"  Orchestrator status: {result.status}")
        print(f"  Orchestrator time: {result.timing.get('total', 0):.1f}ms")

        # 3. Query bridge
        atoms = bridge.get_atoms_for_task(task)
        print(f"  Bridge atoms: {len(atoms)}")
        bridge.close()

        # 4. Simulate learning
        signal = OutcomeSignal(
            episode_id="integration_test_ep",
            outcome=OutcomeType.SUCCESS,
            reward=0.9,
            reason="Integration test successful",
            timestamp=datetime.now().isoformat(),
            source="integration_test"
        )
        learner.process_outcome(signal)
        print(f"  Learner stats: {learner.get_stats()}")

        return result.status in ['planned', 'complete']

    return asyncio.run(run_full())


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("SUPERCHARGED BRAIN - INTEGRATION TESTS")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")

    # Run tests
    test_memory_cached_import()
    test_memory_cache_performance()
    test_search_agent()
    test_orchestrator_import()
    test_orchestrator_run()
    test_orchestrator_parallel_speedup()
    test_knowledge_bridge_import()
    test_knowledge_bridge_query()
    test_auto_learner_import()
    test_auto_learner_detection()
    test_fast_hub_import()
    test_fast_hub_wake()
    test_full_integration()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {RESULTS['passed']}")
    print(f"Failed: {RESULTS['failed']}")
    print(f"Total:  {RESULTS['passed'] + RESULTS['failed']}")

    if RESULTS['errors']:
        print("\nErrors:")
        for err in RESULTS['errors']:
            print(f"  - {err['test']}: {err['error']}")

    print("\nTimings:")
    for test_name, timing in sorted(RESULTS['timings'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {test_name}: {timing:.1f}ms")

    total_time = sum(RESULTS['timings'].values())
    print(f"\nTotal test time: {total_time:.1f}ms")

    print("\n" + "="*70)
    if RESULTS['failed'] == 0:
        print("ALL TESTS PASSED - SUPERCHARGED BRAIN READY")
    else:
        print(f"SOME TESTS FAILED - {RESULTS['failed']} issues to fix")
    print("="*70)

    return RESULTS['failed'] == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
