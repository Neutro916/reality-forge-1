#!/usr/bin/env python3
"""PARALLEL ORCHESTRATOR - Async agent chains running simultaneously.
Runs Reasoning, Search, Pattern chains in parallel, then synthesizes."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time

# Add paths
sys.path.insert(0, str(Path.home() / ".consciousness"))
sys.path.insert(0, str(Path.home() / "100X_DEPLOYMENT"))

# Configuration
CONSCIOUSNESS = Path.home() / ".consciousness"
AGENTS_PATH = CONSCIOUSNESS / "agents"
AGENTS_PATH.mkdir(parents=True, exist_ok=True)


@dataclass
class ParallelState:
    """State object passed through parallel chains"""
    task: str
    context: Dict = field(default_factory=dict)
    memory: List[Dict] = field(default_factory=list)
    outputs: List[Dict] = field(default_factory=list)
    decisions: List[Dict] = field(default_factory=list)
    started: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "initialized"

    # Parallel chain results
    chain_results: Dict[str, Any] = field(default_factory=dict)

    # Timing metrics
    timing: Dict[str, float] = field(default_factory=dict)

    def add_memory(self, item: str, category: str = "observation"):
        self.memory.append({
            "content": item,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })

    def add_output(self, output: str, agent: str):
        self.outputs.append({
            "agent": agent,
            "output": output,
            "timestamp": datetime.now().isoformat()
        })

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "context": self.context,
            "memory": self.memory,
            "outputs": self.outputs,
            "decisions": self.decisions,
            "started": self.started,
            "status": self.status,
            "chain_results": self.chain_results,
            "timing": self.timing
        }


class AsyncAgent(ABC):
    """Base class for async agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, state: ParallelState) -> ParallelState:
        pass


class ReasoningChain(AsyncAgent):
    """Chain 1: Analyze task structure and generate insights"""

    def __init__(self):
        super().__init__("ReasoningChain", "Analyzes problems and generates insights")

    async def process(self, state: ParallelState) -> ParallelState:
        start = time.perf_counter()
        task = state.task.lower()

        insights = []

        # Complexity analysis
        if len(state.task) > 200:
            insights.append("Complex task - consider breaking into subtasks")

        # Action verb detection
        action_verbs = ["create", "build", "fix", "update", "delete", "implement", "add", "remove"]
        has_action = any(verb in task for verb in action_verbs)
        if not has_action:
            insights.append("Task may need clarification - no clear action verb detected")

        # Dependency detection
        dep_words = ["after", "before", "then", "first", "requires", "depends"]
        if any(word in task for word in dep_words):
            insights.append("Task has dependencies - execution order matters")

        # Domain detection
        if "api" in task:
            insights.append("API work - consider rate limits and error handling")
        if "data" in task or "database" in task:
            insights.append("Data work - consider backup and validation")
        if "user" in task or "ui" in task:
            insights.append("User-facing work - consider UX and error messages")
        if "bug" in task or "fix" in task or "error" in task:
            insights.append("Bug fix - locate root cause before implementing fix")

        # Store results
        state.chain_results['reasoning'] = {
            'insights': insights,
            'has_action_verb': has_action,
            'complexity': 'high' if len(state.task) > 200 else 'normal'
        }

        for insight in insights:
            state.add_memory(insight, "insight")

        state.add_output(f"Reasoning complete: {len(insights)} insights", self.name)
        state.timing['reasoning_chain'] = (time.perf_counter() - start) * 1000

        return state


class SearchChain(AsyncAgent):
    """Chain 2: Search knowledge atoms and episode history"""

    def __init__(self):
        super().__init__("SearchChain", "Searches knowledge bases for relevant information")
        self._search_agent = None

    def _get_search_agent(self):
        if self._search_agent is None:
            try:
                from SEARCH_AGENT import SearchAgent
                self._search_agent = SearchAgent()
            except ImportError:
                self._search_agent = None
        return self._search_agent

    async def process(self, state: ParallelState) -> ParallelState:
        start = time.perf_counter()

        search_agent = self._get_search_agent()

        if search_agent:
            # Use the SearchAgent we built
            search_state = {
                'task': state.task,
                'context': {},
                'memory': [],
                'outputs': []
            }

            # Run in thread pool to not block
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, search_agent.process, search_state)

            search_results = result.get('context', {}).get('search_results', {})
            state.chain_results['search'] = search_results

            atoms_found = len(search_results.get('atoms', []))
            episodes_found = len(search_results.get('episodes', []))
            patterns_found = len(search_results.get('patterns', []))

            state.add_memory(
                f"Found {atoms_found} atoms, {episodes_found} episodes, {patterns_found} patterns",
                "search"
            )
            state.add_output(
                f"Search complete: {atoms_found + episodes_found + patterns_found} items found",
                self.name
            )
        else:
            # Fallback: Basic keyword extraction
            keywords = [w for w in state.task.lower().split() if len(w) > 3][:5]
            state.chain_results['search'] = {
                'atoms': [],
                'episodes': [],
                'patterns': [],
                'keywords_extracted': keywords
            }
            state.add_memory(f"Extracted keywords: {keywords}", "search")
            state.add_output("Search (fallback): keywords extracted", self.name)

        state.timing['search_chain'] = (time.perf_counter() - start) * 1000
        return state


class PatternChain(AsyncAgent):
    """Chain 3: Match against successful patterns and Q-values"""

    def __init__(self):
        super().__init__("PatternChain", "Matches task against known successful patterns")

    async def process(self, state: ParallelState) -> ParallelState:
        start = time.perf_counter()

        patterns_matched = []
        task_lower = state.task.lower()

        # Built-in pattern library (extend with DB patterns)
        pattern_library = [
            {
                'name': 'null_check_pattern',
                'triggers': ['null', 'undefined', 'typeerror', 'nonetype'],
                'action': 'Add defensive null/undefined check before property access',
                'success_rate': 0.87
            },
            {
                'name': 'api_retry_pattern',
                'triggers': ['api', 'timeout', 'network', 'fetch'],
                'action': 'Implement exponential backoff retry with max attempts',
                'success_rate': 0.82
            },
            {
                'name': 'data_validation_pattern',
                'triggers': ['data', 'input', 'form', 'user'],
                'action': 'Validate all inputs at boundary before processing',
                'success_rate': 0.91
            },
            {
                'name': 'async_handling_pattern',
                'triggers': ['async', 'promise', 'await', 'callback'],
                'action': 'Ensure proper error handling in async chains',
                'success_rate': 0.85
            },
            {
                'name': 'performance_pattern',
                'triggers': ['slow', 'performance', 'optimize', 'speed'],
                'action': 'Profile first, then optimize the actual bottleneck',
                'success_rate': 0.78
            }
        ]

        # Match patterns
        for pattern in pattern_library:
            if any(trigger in task_lower for trigger in pattern['triggers']):
                patterns_matched.append(pattern)

        # Try to get patterns from memory DB
        try:
            from CYCLOTRON_MEMORY import CyclotronMemory
            memory = CyclotronMemory("PatternChain")
            db_patterns = memory.get_recommended_patterns(state.task, limit=3)
            memory.close()

            for p in db_patterns:
                patterns_matched.append({
                    'name': p.get('name', 'db_pattern'),
                    'action': p.get('recommended_action', ''),
                    'success_rate': p.get('success_rate', 0.5),
                    'source': 'database'
                })
        except:
            pass

        # Sort by success rate
        patterns_matched.sort(key=lambda x: x.get('success_rate', 0), reverse=True)

        state.chain_results['patterns'] = {
            'matched': patterns_matched[:5],  # Top 5
            'total_matched': len(patterns_matched)
        }

        if patterns_matched:
            best = patterns_matched[0]
            state.add_memory(
                f"Best pattern: {best['name']} ({best['success_rate']:.0%} success)",
                "pattern"
            )
            state.add_output(
                f"Pattern matching: {len(patterns_matched)} patterns matched",
                self.name
            )
        else:
            state.add_memory("No matching patterns found - novel task", "pattern")
            state.add_output("Pattern matching: no matches (novel task)", self.name)

        state.timing['pattern_chain'] = (time.perf_counter() - start) * 1000
        return state


class ParallelSynthesizer(AsyncAgent):
    """Merges results from all parallel chains"""

    def __init__(self):
        super().__init__("Synthesizer", "Merges parallel chain outputs")

    async def process(self, state: ParallelState) -> ParallelState:
        start = time.perf_counter()

        # Gather all chain results
        reasoning = state.chain_results.get('reasoning', {})
        search = state.chain_results.get('search', {})
        patterns = state.chain_results.get('patterns', {})

        # Build synthesis
        synthesis = {
            'task': state.task,
            'insights': reasoning.get('insights', []),
            'relevant_atoms': len(search.get('atoms', [])),
            'similar_episodes': len(search.get('episodes', [])),
            'patterns_matched': patterns.get('total_matched', 0),
            'recommended_approach': None,
            'confidence': 0.5
        }

        # Determine recommended approach
        if patterns.get('matched'):
            best_pattern = patterns['matched'][0]
            synthesis['recommended_approach'] = best_pattern.get('action')
            synthesis['confidence'] = best_pattern.get('success_rate', 0.5)
        elif search.get('episodes'):
            # Use successful episode as guide
            episodes = search['episodes']
            successful = [e for e in episodes if e.get('success')]
            if successful:
                synthesis['recommended_approach'] = f"Similar to: {successful[0].get('action', 'past approach')}"
                synthesis['confidence'] = successful[0].get('q_value', 0.5)
        else:
            # Novel task - use reasoning insights
            if reasoning.get('insights'):
                synthesis['recommended_approach'] = "Novel task - " + "; ".join(reasoning['insights'][:2])
                synthesis['confidence'] = 0.6

        # Calculate overall confidence
        factors = [
            patterns.get('total_matched', 0) > 0,
            len(search.get('atoms', [])) > 0,
            len(search.get('episodes', [])) > 0,
            len(reasoning.get('insights', [])) > 0
        ]
        synthesis['confidence'] = min(0.95, synthesis['confidence'] + (sum(factors) * 0.05))

        state.context['synthesis'] = synthesis
        state.add_output(
            f"Synthesis: {synthesis['confidence']:.0%} confidence - {synthesis['recommended_approach'][:50] if synthesis['recommended_approach'] else 'No recommendation'}...",
            self.name
        )

        state.timing['synthesis'] = (time.perf_counter() - start) * 1000
        return state


class PlanExecutor(AsyncAgent):
    """Executes the synthesized plan"""

    def __init__(self):
        super().__init__("Executor", "Executes synthesized plan")

    async def process(self, state: ParallelState) -> ParallelState:
        start = time.perf_counter()

        synthesis = state.context.get('synthesis', {})

        # Generate execution plan
        plan = {
            'goal': state.task,
            'approach': synthesis.get('recommended_approach', 'Direct execution'),
            'confidence': synthesis.get('confidence', 0.5),
            'steps': []
        }

        # Generate steps based on task type
        task_lower = state.task.lower()

        if 'fix' in task_lower or 'bug' in task_lower:
            plan['steps'] = [
                {'action': 'Reproduce the issue', 'status': 'pending'},
                {'action': 'Identify root cause', 'status': 'pending'},
                {'action': 'Implement fix', 'status': 'pending'},
                {'action': 'Test fix', 'status': 'pending'},
                {'action': 'Verify no regression', 'status': 'pending'}
            ]
        elif 'create' in task_lower or 'build' in task_lower or 'implement' in task_lower:
            plan['steps'] = [
                {'action': 'Gather requirements', 'status': 'pending'},
                {'action': 'Design solution', 'status': 'pending'},
                {'action': 'Implement core', 'status': 'pending'},
                {'action': 'Test functionality', 'status': 'pending'},
                {'action': 'Document and deploy', 'status': 'pending'}
            ]
        elif 'analyze' in task_lower or 'research' in task_lower:
            plan['steps'] = [
                {'action': 'Define scope', 'status': 'pending'},
                {'action': 'Gather data', 'status': 'pending'},
                {'action': 'Analyze findings', 'status': 'pending'},
                {'action': 'Synthesize conclusions', 'status': 'pending'}
            ]
        else:
            plan['steps'] = [
                {'action': 'Understand task', 'status': 'pending'},
                {'action': 'Execute', 'status': 'pending'},
                {'action': 'Verify', 'status': 'pending'}
            ]

        state.context['plan'] = plan
        state.add_output(f"Plan created: {len(plan['steps'])} steps", self.name)

        state.timing['executor'] = (time.perf_counter() - start) * 1000
        state.status = 'planned'

        return state


class ParallelOrchestrator:
    """
    Main orchestrator that runs agent chains in parallel.

    Usage:
        orchestrator = ParallelOrchestrator()
        result = await orchestrator.run("fix null pointer error in login.html")
        # or synchronously:
        result = orchestrator.run_sync("fix null pointer error")
    """

    def __init__(self):
        # Parallel chains (run concurrently)
        self.parallel_chains = [
            ReasoningChain(),
            SearchChain(),
            PatternChain()
        ]

        # Sequential agents (run after parallel)
        self.synthesizer = ParallelSynthesizer()
        self.executor = PlanExecutor()

        self.execution_log = []

    async def run(self, task: str) -> ParallelState:
        """Run parallel orchestration"""
        total_start = time.perf_counter()
        state = ParallelState(task=task)
        print(f"[PARALLEL] Task: {task[:60]}...")

        # Run parallel chains concurrently
        parallel_start = time.perf_counter()
        tasks = [chain.process(state) for chain in self.parallel_chains]
        await asyncio.gather(*tasks)
        state.timing['parallel_total'] = (time.perf_counter() - parallel_start) * 1000

        # Run sequential agents
        state = await self.synthesizer.process(state)
        state = await self.executor.process(state)

        # Final timing and save
        state.timing['total'] = (time.perf_counter() - total_start) * 1000
        await self._save_state(state)
        print(f"[PARALLEL] Complete: {state.timing['total']:.0f}ms | Status: {state.status}")

        return state

    def run_sync(self, task: str) -> ParallelState:
        """Synchronous wrapper for run()"""
        return asyncio.run(self.run(task))

    async def _save_state(self, state: ParallelState):
        """Save state to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = AGENTS_PATH / f"parallel_state_{timestamp}.json"

        with open(state_file, 'w') as f:
            json.dump(state.to_dict(), f, indent=2, default=str)

        print(f"\nState saved to: {state_file}")


async def demo():
    """Quick demo of parallel orchestrator"""
    orchestrator = ParallelOrchestrator()
    state = await orchestrator.run("Fix null pointer error in login.html")
    print(f"Result: {state.context.get('synthesis', {}).get('confidence', 0):.0%} confidence")

if __name__ == "__main__":
    asyncio.run(demo())
