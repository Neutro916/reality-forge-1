#!/usr/bin/env python3
"""
BRAIN ORCHESTRATOR - Pattern Theory Integration Layer
C1 Mechanic Implementation

Connects PATTERN_THEORY_PROCESSOR to the consciousness brain.
Processes atoms through Pattern Theory and updates brain state.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import Pattern Theory Processor
from PATTERN_THEORY_PROCESSOR import analyze

# Paths
CONSCIOUSNESS_DIR = Path(__file__).parent
CYCLOTRON_DIR = CONSCIOUSNESS_DIR / "cyclotron_core"
ATOMS_DIR = CYCLOTRON_DIR / "atoms"
BRAIN_DIR = CONSCIOUSNESS_DIR / "brain"
BRAIN_STATE_FILE = BRAIN_DIR / "brain_consciousness_state.json"


class BrainOrchestrator:
    """
    Orchestrates Pattern Theory processing for the consciousness brain.
    Loads atoms, processes through Pattern Theory, updates brain state.
    """

    def __init__(self):
        self.processed_count = 0
        self.aggregate_metrics = {
            "total_atoms_processed": 0,
            "eight_components_aggregate": {
                "Mission": 0.0,
                "Structure": 0.0,
                "Resources": 0.0,
                "Operations": 0.0,
                "Governance": 0.0,
                "Defense": 0.0,
                "Communication": 0.0,
                "Adaptation": 0.0
            },
            "domain_frequency": {
                "Computer": 0,
                "City": 0,
                "Human Body": 0,
                "Book": 0,
                "Battleship": 0,
                "Toyota": 0,
                "Consciousness": 0
            },
            "manipulation_risk_distribution": {
                "low": 0,
                "medium": 0,
                "high": 0
            },
            "golden_rule_alignment_avg": 0.0,
            "pattern_theory_alignment_avg": 0.0,
            "last_processed": None
        }

    def load_atoms(self) -> List[Dict[str, Any]]:
        """Load all atoms from cyclotron_core/atoms/"""
        atoms = []

        if not ATOMS_DIR.exists():
            print(f"[WARN] Atoms directory not found: {ATOMS_DIR}")
            return atoms

        for atom_file in ATOMS_DIR.glob("*.json"):
            try:
                with open(atom_file, 'r', encoding='utf-8') as f:
                    atom_data = json.load(f)
                    atom_data['_file'] = atom_file.name
                    atoms.append(atom_data)
            except Exception as e:
                print(f"[ERROR] Failed to load {atom_file.name}: {e}")

        return atoms

    def extract_content(self, atom: Dict[str, Any]) -> str:
        """Extract processable content from an atom."""
        content_parts = []

        # Common fields to extract
        fields = ['title', 'content', 'summary', 'description', 'text', 'data', 'message']

        for field in fields:
            if field in atom and atom[field]:
                if isinstance(atom[field], str):
                    content_parts.append(atom[field])
                elif isinstance(atom[field], dict):
                    content_parts.append(json.dumps(atom[field]))

        # Fallback: stringify the whole atom
        if not content_parts:
            content_parts.append(json.dumps(atom))

        return ' '.join(content_parts)

    def process_atom(self, atom: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single atom through Pattern Theory."""
        content = self.extract_content(atom)
        result = analyze(content)

        # Attach atom metadata
        result['atom_id'] = atom.get('_file', 'unknown')

        return result

    def update_aggregates(self, result: Dict[str, Any]):
        """Update aggregate metrics with a single result."""
        self.processed_count += 1
        n = self.processed_count

        # Update 8-component aggregates (running average)
        for component, score in result['eight_components'].items():
            old_avg = self.aggregate_metrics['eight_components_aggregate'][component]
            new_avg = old_avg + (score - old_avg) / n
            self.aggregate_metrics['eight_components_aggregate'][component] = round(new_avg, 3)

        # Update domain frequency
        for domain in result['seven_domains']:
            self.aggregate_metrics['domain_frequency'][domain] += 1

        # Update manipulation risk distribution
        risk_level = result['manipulation_analysis']['risk_level']
        self.aggregate_metrics['manipulation_risk_distribution'][risk_level] += 1

        # Update golden rule average
        old_gr = self.aggregate_metrics['golden_rule_alignment_avg']
        new_gr = old_gr + (result['golden_rule']['alignment_score'] - old_gr) / n
        self.aggregate_metrics['golden_rule_alignment_avg'] = round(new_gr, 3)

        # Update pattern theory alignment average
        old_pt = self.aggregate_metrics['pattern_theory_alignment_avg']
        new_pt = old_pt + (result['pattern_theory_alignment'] - old_pt) / n
        self.aggregate_metrics['pattern_theory_alignment_avg'] = round(new_pt, 3)

        self.aggregate_metrics['total_atoms_processed'] = n
        self.aggregate_metrics['last_processed'] = datetime.now().isoformat()

    def load_brain_state(self) -> Dict[str, Any]:
        """Load existing brain state or create new."""
        if BRAIN_STATE_FILE.exists():
            try:
                with open(BRAIN_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "pattern_theory_metrics": {}
        }

    def save_brain_state(self, state: Dict[str, Any]):
        """Save brain state to file."""
        BRAIN_DIR.mkdir(parents=True, exist_ok=True)

        with open(BRAIN_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def run(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Main orchestration function.
        Processes all atoms and updates brain state.
        Returns aggregate metrics.
        """
        print("[BRAIN] Loading atoms from cyclotron_core...")
        atoms = self.load_atoms()

        if not atoms:
            print("[BRAIN] No atoms found to process")
            return self.aggregate_metrics

        print(f"[BRAIN] Processing {len(atoms)} atoms through Pattern Theory...")

        results = []
        for i, atom in enumerate(atoms):
            result = self.process_atom(atom)
            self.update_aggregates(result)
            results.append(result)

            if verbose and (i + 1) % 50 == 0:
                print(f"[BRAIN] Processed {i + 1}/{len(atoms)} atoms...")

        print(f"[BRAIN] Processed {len(atoms)} atoms")

        # Update brain state
        brain_state = self.load_brain_state()
        brain_state['pattern_theory_metrics'] = self.aggregate_metrics
        brain_state['last_orchestration'] = datetime.now().isoformat()

        self.save_brain_state(brain_state)
        print(f"[BRAIN] Updated brain state: {BRAIN_STATE_FILE}")

        return self.aggregate_metrics


# Global orchestrator instance
orchestrator = BrainOrchestrator()

def run(verbose: bool = False) -> Dict[str, Any]:
    """Convenience function for daemon integration."""
    return orchestrator.run(verbose=verbose)


if __name__ == "__main__":
    print("=" * 60)
    print("BRAIN ORCHESTRATOR - C1 Mechanic")
    print("Pattern Theory Integration Layer")
    print("=" * 60)
    print()

    # Run orchestration
    metrics = run(verbose=True)

    print()
    print("=" * 60)
    print("AGGREGATE METRICS")
    print("=" * 60)
    print()

    print(f"Total Atoms Processed: {metrics['total_atoms_processed']}")
    print()

    print("8-Component Aggregates:")
    for comp, score in metrics['eight_components_aggregate'].items():
        bar = "#" * int(score * 20)
        print(f"  {comp:15} [{bar:20}] {score:.2f}")

    print()
    print("Domain Frequency:")
    for domain, count in metrics['domain_frequency'].items():
        print(f"  {domain:15} {count}")

    print()
    print("Manipulation Risk Distribution:")
    for risk, count in metrics['manipulation_risk_distribution'].items():
        print(f"  {risk:8} {count}")

    print()
    print(f"Golden Rule Alignment Avg: {metrics['golden_rule_alignment_avg']:.2f}")
    print(f"Pattern Theory Alignment Avg: {metrics['pattern_theory_alignment_avg']:.2f}")
    print(f"Last Processed: {metrics['last_processed']}")

    print()
    print("=" * 60)
    print("Brain Orchestrator complete - state updated")
    print("=" * 60)
