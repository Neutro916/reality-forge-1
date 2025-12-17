# Large Python Files (>500 lines) - LIGHTER Violations

These files exceed the 500-line manufacturing standard. Document for future refactoring.

| File | Lines | Action |
|------|-------|--------|
| CYCLOTRON_NERVE_CENTER.py | 704 | Split into core + extensions |
| PATTERN_TRAINING_COLLECTOR.py | 662 | Extract data handlers |
| CONVERGENCE_METRICS.py | 659 | Separate metrics from visualization |
| PARALLEL_ORCHESTRATOR.py | 608 | Split workers from coordinator |
| AUTO_LEARNER.py | 558 | Extract model handlers |
| ADD_LEGAL_BOOKING_WIDGET.py | 534 | Can be deleted - one-time use |
| CLAUDE_COCKPIT.py | 509 | Extract UI from logic |
| CLOUD_TRINITY_WORKER.py | 500 | At threshold - monitor |

## Priority Refactor Order
1. ADD_LEGAL_BOOKING_WIDGET.py - DELETE (one-time script)
2. CYCLOTRON_NERVE_CENTER.py - Most complex, highest priority
3. CONVERGENCE_METRICS.py - Used frequently

## LIGHTER Standard
Files should be <500 lines. Functions should be <50 lines.
One file = One responsibility.

*Generated: 2025-11-27 by C2 Scan*
