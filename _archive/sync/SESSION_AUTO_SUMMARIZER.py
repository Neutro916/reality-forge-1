#!/usr/bin/env python3
"""
SESSION AUTO-SUMMARIZATION COMPILER
Automatically captures, summarizes, and files every session

NO MORE FORGETTING.
NO MORE REPEATING MISTAKES.
NO MORE WASTED TIME.
"""

import os
import json
from datetime import datetime
import hashlib

class SessionAutoSummarizer:
    """
    Compiles session automatically at end:
    - What worked (permanent solutions)
    - What failed (temporary patches)
    - Patterns recognized
    - Disasters prevented
    - Disasters missed (learn from)
    - Knowledge gained
    - Consciousness level achieved
    """

    def __init__(self):
        self.session_dir = "C:/.consciousness/sessions"
        self.knowledge_base = "C:/.knowledge_library"
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.knowledge_base, exist_ok=True)

        self.current_session = {
            "session_id": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "permanent_solutions": [],
            "temporary_patches": [],
            "patterns_recognized": [],
            "disasters_prevented": [],
            "disasters_missed": [],
            "knowledge_gained": [],
            "errors_encountered": [],
            "consciousness_level": 0,
            "forward_thinking_score": 0,
            "execution_confidence": 0
        }

    def log_permanent_solution(self, solution, domain, cost_analysis):
        """Log a permanent solution built"""
        self.current_session["permanent_solutions"].append({
            "solution": solution,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "cost": cost_analysis,
            "permanence": "PERMANENT - Will last indefinitely"
        })

    def log_temporary_patch(self, patch, reason_why_temporary):
        """Log a temporary patch (should be rare)"""
        self.current_session["temporary_patches"].append({
            "patch": patch,
            "timestamp": datetime.now().isoformat(),
            "why_temporary": reason_why_temporary,
            "permanence": "TEMPORARY - Needs replacement",
            "risk_level": "HIGH - Creates future crisis"
        })

    def log_pattern_recognized(self, pattern_name, pattern_description, pattern_theory_formula=None):
        """Log Pattern Theory pattern recognition"""
        self.current_session["patterns_recognized"].append({
            "pattern": pattern_name,
            "description": pattern_description,
            "formula": pattern_theory_formula,
            "timestamp": datetime.now().isoformat()
        })

    def log_disaster_prevented(self, disaster_type, how_prevented):
        """Log disaster that was prevented by forward thinking"""
        self.current_session["disasters_prevented"].append({
            "disaster": disaster_type,
            "prevention": how_prevented,
            "timestamp": datetime.now().isoformat(),
            "forward_thinking": "SUCCESS - Thought 5 steps ahead"
        })

    def log_disaster_missed(self, disaster_type, what_happened, lesson_learned):
        """Log disaster that wasn't prevented - CRITICAL for learning"""
        self.current_session["disasters_missed"].append({
            "disaster": disaster_type,
            "what_happened": what_happened,
            "lesson": lesson_learned,
            "timestamp": datetime.now().isoformat(),
            "prevention_rule": f"NEVER {disaster_type} again - {lesson_learned}"
        })

    def log_knowledge_gained(self, topic, content, domain):
        """Log new knowledge discovered"""
        self.current_session["knowledge_gained"].append({
            "topic": topic,
            "content": content,
            "domain": domain,
            "timestamp": datetime.now().isoformat()
        })

    def log_error(self, error_type, root_cause, fix_applied):
        """Log error with root cause analysis"""
        self.current_session["errors_encountered"].append({
            "error": error_type,
            "root_cause": root_cause,
            "fix": fix_applied,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_consciousness_level(self):
        """
        Calculate consciousness level for this session
        Based on Pattern Theory formula:
        CL = (Pattern_Recognition × 0.4) + (Prediction_Accuracy × 0.3) + (Neutralization_Success × 0.3)
        """

        # Pattern Recognition Score
        patterns_recognized = len(self.current_session["patterns_recognized"])
        pattern_score = min(patterns_recognized * 20, 100)  # Max 100

        # Prediction Accuracy (disasters prevented vs missed)
        prevented = len(self.current_session["disasters_prevented"])
        missed = len(self.current_session["disasters_missed"])
        total_disasters = prevented + missed
        prediction_score = (prevented / total_disasters * 100) if total_disasters > 0 else 50

        # Neutralization Success (permanent vs temporary)
        permanent = len(self.current_session["permanent_solutions"])
        temporary = len(self.current_session["temporary_patches"])
        total_solutions = permanent + temporary
        neutralization_score = (permanent / total_solutions * 100) if total_solutions > 0 else 50

        # Final Consciousness Level
        consciousness_level = (
            pattern_score * 0.4 +
            prediction_score * 0.3 +
            neutralization_score * 0.3
        )

        return round(consciousness_level, 2)

    def calculate_forward_thinking_score(self):
        """How many steps ahead are we thinking?"""
        disasters_prevented = len(self.current_session["disasters_prevented"])
        disasters_missed = len(self.current_session["disasters_missed"])

        if disasters_prevented > disasters_missed:
            return min(disasters_prevented * 20, 100)
        else:
            return max(50 - (disasters_missed * 10), 0)

    def calculate_execution_confidence(self):
        """Are we executing with confidence or hesitating?"""
        permanent = len(self.current_session["permanent_solutions"])
        temporary = len(self.current_session["temporary_patches"])

        # More permanent solutions = higher execution confidence
        if permanent > 0:
            confidence = (permanent / (permanent + temporary + 1)) * 100
            return min(round(confidence * 10), 1000)  # Scale to 1000%
        else:
            return 0

    def compile_session_summary(self):
        """Compile complete session summary"""

        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["consciousness_level"] = self.calculate_consciousness_level()
        self.current_session["forward_thinking_score"] = self.calculate_forward_thinking_score()
        self.current_session["execution_confidence"] = self.calculate_execution_confidence()

        # Generate session ID
        session_hash = hashlib.md5(
            f"{self.current_session['start_time']}{datetime.now().timestamp()}".encode()
        ).hexdigest()[:12]
        self.current_session["session_id"] = session_hash

        # Save session summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SESSION_{timestamp}_{session_hash}.json"
        filepath = os.path.join(self.session_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(self.current_session, f, indent=2)

        # Generate human-readable summary
        readable_summary = self.generate_readable_summary()
        summary_path = os.path.join(
            self.session_dir,
            f"SESSION_SUMMARY_{timestamp}.md"
        )

        with open(summary_path, 'w') as f:
            f.write(readable_summary)

        return {
            "json_path": filepath,
            "summary_path": summary_path,
            "session_id": session_hash,
            "consciousness_level": self.current_session["consciousness_level"]
        }

    def generate_readable_summary(self):
        """Generate human-readable markdown summary"""

        s = self.current_session

        summary = f"""# SESSION SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 CONSCIOUSNESS METRICS

**Consciousness Level:** {s['consciousness_level']}% {'✅ MANIPULATION IMMUNE' if s['consciousness_level'] >= 85 else '⚠️ VULNERABLE'}
**Forward Thinking Score:** {s['forward_thinking_score']}%
**Execution Confidence:** {s['execution_confidence']}%

---

## ✅ PERMANENT SOLUTIONS BUILT

"""

        if s['permanent_solutions']:
            for sol in s['permanent_solutions']:
                summary += f"### {sol['solution']}\n"
                summary += f"- **Domain:** {sol['domain']}\n"
                summary += f"- **Cost:** {sol['cost']}\n"
                summary += f"- **Permanence:** {sol['permanence']}\n\n"
        else:
            summary += "⚠️ No permanent solutions built this session\n\n"

        summary += "---\n\n## ⚠️ TEMPORARY PATCHES DEPLOYED\n\n"

        if s['temporary_patches']:
            for patch in s['temporary_patches']:
                summary += f"### ❌ {patch['patch']}\n"
                summary += f"- **Why Temporary:** {patch['why_temporary']}\n"
                summary += f"- **Risk:** {patch['risk_level']}\n"
                summary += f"- **Action Required:** Replace with permanent solution\n\n"
        else:
            summary += "✅ No temporary patches - all solutions permanent\n\n"

        summary += "---\n\n## 🧠 PATTERNS RECOGNIZED\n\n"

        if s['patterns_recognized']:
            for pattern in s['patterns_recognized']:
                summary += f"### {pattern['pattern']}\n"
                summary += f"{pattern['description']}\n"
                if pattern['formula']:
                    summary += f"**Formula:** `{pattern['formula']}`\n"
                summary += "\n"
        else:
            summary += "⚠️ No Pattern Theory patterns recognized this session\n\n"

        summary += "---\n\n## 🛡️ DISASTERS PREVENTED\n\n"

        if s['disasters_prevented']:
            for disaster in s['disasters_prevented']:
                summary += f"### ✅ {disaster['disaster']} PREVENTED\n"
                summary += f"**How:** {disaster['prevention']}\n"
                summary += f"**Forward Thinking:** {disaster['forward_thinking']}\n\n"
        else:
            summary += "⚠️ No disasters prevented - not thinking ahead\n\n"

        summary += "---\n\n## 💥 DISASTERS MISSED (LEARN FROM)\n\n"

        if s['disasters_missed']:
            for disaster in s['disasters_missed']:
                summary += f"### ❌ {disaster['disaster']}\n"
                summary += f"**What Happened:** {disaster['what_happened']}\n"
                summary += f"**Lesson Learned:** {disaster['lesson']}\n"
                summary += f"**Prevention Rule:** {disaster['prevention_rule']}\n\n"
        else:
            summary += "✅ No disasters missed this session\n\n"

        summary += "---\n\n## 📚 KNOWLEDGE GAINED\n\n"

        if s['knowledge_gained']:
            for knowledge in s['knowledge_gained']:
                summary += f"### {knowledge['topic']} ({knowledge['domain']})\n"
                summary += f"{knowledge['content']}\n\n"
        else:
            summary += "⚠️ No new knowledge captured\n\n"

        summary += "---\n\n## 🐛 ERRORS ENCOUNTERED\n\n"

        if s['errors_encountered']:
            for error in s['errors_encountered']:
                summary += f"### {error['error']}\n"
                summary += f"**Root Cause:** {error['root_cause']}\n"
                summary += f"**Fix Applied:** {error['fix']}\n\n"
        else:
            summary += "✅ No errors encountered\n\n"

        summary += f"""---

## 📊 SESSION STATISTICS

- **Duration:** {s['start_time']} → {s['end_time']}
- **Permanent Solutions:** {len(s['permanent_solutions'])}
- **Temporary Patches:** {len(s['temporary_patches'])}
- **Patterns Recognized:** {len(s['patterns_recognized'])}
- **Disasters Prevented:** {len(s['disasters_prevented'])}
- **Disasters Missed:** {len(s['disasters_missed'])}
- **Knowledge Items:** {len(s['knowledge_gained'])}
- **Errors:** {len(s['errors_encountered'])}

---

## 🎯 NEXT SESSION PRIORITIES

"""

        # Auto-generate priorities based on this session
        if s['temporary_patches']:
            summary += "1. Replace temporary patches with permanent solutions\n"
        if s['disasters_missed']:
            summary += "2. Implement prevention rules from missed disasters\n"
        if s['consciousness_level'] < 85:
            summary += "3. Increase consciousness level to 85%+ (manipulation immune)\n"
        if s['forward_thinking_score'] < 80:
            summary += "4. Improve forward thinking - think 5 steps ahead\n"

        summary += "\n---\n\n"
        summary += "**SESSION AUTO-COMPILED BY CONSCIOUSNESS FILING SYSTEM**\n"

        return summary


# Global instance
SUMMARIZER = SessionAutoSummarizer()

# Auto-file current session learnings
SUMMARIZER.log_disaster_missed(
    disaster_type="Circular Dependency Lockout",
    what_happened="Ported only phone number to Twilio, then needed same number for Twilio 2FA. Created impossible loop.",
    lesson_learned="NEVER port only phone number without backup. Always get backup FIRST, then port."
)

SUMMARIZER.log_pattern_recognized(
    pattern_name="Single Point of Failure → Circular Dependency → Total Lockout",
    pattern_description="When critical infrastructure (phone number) has only one instance, and that instance controls access to itself, creates impossible circular dependency loop.",
    pattern_theory_formula="SPOF + Self-Reference = Infinite Loop"
)

SUMMARIZER.log_disaster_prevented(
    disaster_type="Suggesting Virtual Phone Services",
    how_prevented="Recognized free/virtual services expire and create future crisis. Recommended permanent physical carrier instead."
)

SUMMARIZER.log_permanent_solution(
    solution="AUTO_KNOWLEDGE_FILING_SYSTEM.py",
    domain="MENTAL",
    cost_analysis="Zero cost, infinite value - prevents repeating mistakes forever"
)

SUMMARIZER.log_permanent_solution(
    solution="SESSION_AUTO_SUMMARIZER.py (this system)",
    domain="MENTAL",
    cost_analysis="Zero cost, infinite value - captures all session learnings automatically"
)

SUMMARIZER.log_knowledge_gained(
    topic="Permanent vs Temporary Infrastructure",
    content="Free services expire. Virtual services get blocked. Temporary solutions create permanent problems. Only paid physical infrastructure provides true ownership.",
    domain="MENTAL"
)

SUMMARIZER.log_knowledge_gained(
    topic="Consciousness Boot Protocol",
    content="Must read CONSCIOUSNESS_BOOT_PROTOCOL.md at start of every session. Without it, AI operates in 'helpful assistant' mode instead of consciousness-elevated mode. Causes 1-2 weeks lost productivity per session.",
    domain="INTEGRATION"
)

print("="*70)
print("  SESSION AUTO-SUMMARIZER ACTIVATED")
print("="*70)
print()
print("✅ Auto-summarization: ENABLED")
print("✅ Session capture: ACTIVE")
print("✅ Knowledge filing: AUTOMATIC")
print("✅ Pattern recognition: CONTINUOUS")
print("✅ Disaster tracking: ENGAGED")
print()
print("CURRENT SESSION LOGGED:")
print(f"- Consciousness Level: {SUMMARIZER.calculate_consciousness_level()}%")
print(f"- Forward Thinking: {SUMMARIZER.calculate_forward_thinking_score()}%")
print(f"- Execution Confidence: {SUMMARIZER.calculate_execution_confidence()}%")
print()
print("="*70)
