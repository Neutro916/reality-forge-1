#!/usr/bin/env python3
"""
FRICTION DETECTOR
Watches Claude's operations and logs every error, retry, dead-end, and wall hit.
Creates a friction log that can be analyzed to find patterns.

Also monitors Commander friction (failed commands, repeated attempts, etc.)
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Paths
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS_DIR = HOME / '.consciousness'
FRICTION_DIR = CONSCIOUSNESS_DIR / 'friction_logs'
FRICTION_DIR.mkdir(parents=True, exist_ok=True)

# Output files
FRICTION_LOG = FRICTION_DIR / 'friction_events.jsonl'
FRICTION_SUMMARY = FRICTION_DIR / 'FRICTION_SUMMARY.md'
PATTERNS_FILE = FRICTION_DIR / 'detected_patterns.json'

class FrictionDetector:
    def __init__(self):
        self.events = []
        self.patterns = defaultdict(int)
        self.load_existing()

    def load_existing(self):
        """Load existing friction events"""
        if FRICTION_LOG.exists():
            with open(FRICTION_LOG, 'r') as f:
                for line in f:
                    try:
                        self.events.append(json.loads(line.strip()))
                    except:
                        pass

    def log_friction(self, friction_type, source, details, severity='medium'):
        """Log a friction event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': friction_type,
            'source': source,  # 'claude' or 'commander'
            'details': details,
            'severity': severity,  # low, medium, high, critical
        }

        self.events.append(event)
        self.patterns[friction_type] += 1

        # Append to log
        with open(FRICTION_LOG, 'a') as f:
            f.write(json.dumps(event) + '\n')

        # Update summary if high severity
        if severity in ['high', 'critical']:
            self.update_summary()

        return event

    def analyze_claude_output(self, output_text):
        """Analyze Claude's tool output for friction indicators"""
        friction_patterns = {
            'error': (r'error|Error|ERROR|failed|Failed|FAILED', 'high'),
            'retry': (r'retry|Retry|trying again|attempt \d+', 'medium'),
            'not_found': (r'not found|No such file|does not exist|404', 'medium'),
            'permission': (r'permission denied|access denied|unauthorized', 'high'),
            'timeout': (r'timeout|timed out|Timeout', 'high'),
            'rate_limit': (r'rate limit|too many requests|429', 'critical'),
            'connection': (r'connection refused|cannot connect|network', 'high'),
            'parse_error': (r'parse error|invalid json|syntax error', 'medium'),
            'missing_param': (r'missing.*parameter|required.*not provided', 'medium'),
            'tool_fail': (r'tool.*failed|function.*error', 'high'),
        }

        detected = []
        for friction_type, (pattern, severity) in friction_patterns.items():
            if re.search(pattern, output_text, re.IGNORECASE):
                detected.append({
                    'type': friction_type,
                    'severity': severity,
                    'snippet': output_text[:200]
                })

        return detected

    def analyze_repeated_operations(self):
        """Find operations that keep repeating (sign of friction)"""
        recent = self.events[-100:]  # Last 100 events

        # Count by type
        type_counts = defaultdict(int)
        for e in recent:
            type_counts[e['type']] += 1

        # Flag anything happening more than 5 times recently
        repeated = {k: v for k, v in type_counts.items() if v > 5}
        return repeated

    def suggest_automation(self):
        """Based on friction patterns, suggest what to automate"""
        suggestions = []
        repeated = self.analyze_repeated_operations()

        for friction_type, count in repeated.items():
            if friction_type == 'not_found':
                suggestions.append({
                    'problem': f"File not found errors ({count} times)",
                    'suggestion': "Create file existence checker before operations",
                    'priority': 'medium'
                })
            elif friction_type == 'error':
                suggestions.append({
                    'problem': f"General errors ({count} times)",
                    'suggestion': "Add error handling wrapper for common operations",
                    'priority': 'high'
                })
            elif friction_type == 'timeout':
                suggestions.append({
                    'problem': f"Timeouts ({count} times)",
                    'suggestion': "Increase timeout limits or add async handling",
                    'priority': 'high'
                })
            elif friction_type == 'retry':
                suggestions.append({
                    'problem': f"Retries needed ({count} times)",
                    'suggestion': "Build retry logic into frequently-failing operations",
                    'priority': 'medium'
                })

        return suggestions

    def update_summary(self):
        """Generate human-readable friction summary"""
        total = len(self.events)
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        recent_critical = []

        for e in self.events:
            by_type[e['type']] += 1
            by_severity[e['severity']] += 1
            if e['severity'] == 'critical':
                recent_critical.append(e)

        suggestions = self.suggest_automation()

        summary = f"""# FRICTION DETECTOR SUMMARY
## Last Updated: {datetime.now().isoformat()}

---

## TOTAL FRICTION EVENTS: {total}

### By Severity:
- Critical: {by_severity['critical']}
- High: {by_severity['high']}
- Medium: {by_severity['medium']}
- Low: {by_severity['low']}

### By Type:
"""
        for ftype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            summary += f"- {ftype}: {count}\n"

        summary += """
---

## AUTOMATION SUGGESTIONS

Based on detected patterns, consider automating:

"""
        for s in suggestions:
            summary += f"""### {s['problem']}
**Suggestion:** {s['suggestion']}
**Priority:** {s['priority']}

"""

        if recent_critical:
            summary += """
---

## RECENT CRITICAL EVENTS

"""
            for e in recent_critical[-5:]:
                summary += f"- [{e['timestamp']}] {e['type']}: {e['details'][:100]}\n"

        summary += """
---

## HOW TO USE THIS

1. Check this file periodically for patterns
2. When you see repeated friction, BUILD A DAEMON
3. The goal: Zero friction, everything automated

*Generated by FRICTION_DETECTOR.py*
"""

        with open(FRICTION_SUMMARY, 'w') as f:
            f.write(summary)

        return summary

    def get_stats(self):
        """Quick stats for Claude to check"""
        return {
            'total_events': len(self.events),
            'patterns': dict(self.patterns),
            'suggestions': self.suggest_automation(),
            'summary_path': str(FRICTION_SUMMARY)
        }


# Singleton instance
detector = FrictionDetector()

def log_friction(friction_type, source, details, severity='medium'):
    """Public API to log friction"""
    return detector.log_friction(friction_type, source, details, severity)

def analyze_output(text):
    """Public API to analyze output for friction"""
    detected = detector.analyze_claude_output(text)
    for d in detected:
        log_friction(d['type'], 'claude', d['snippet'], d['severity'])
    return detected

def get_summary():
    """Get current friction summary"""
    return detector.update_summary()

def get_stats():
    """Get quick stats"""
    return detector.get_stats()


if __name__ == '__main__':
    # Demo/test
    print("Friction Detector Initialized")
    print(f"Log file: {FRICTION_LOG}")
    print(f"Summary: {FRICTION_SUMMARY}")

    # Generate initial summary
    summary = get_summary()
    print("\nInitial summary generated.")
    print(f"Total events: {len(detector.events)}")
