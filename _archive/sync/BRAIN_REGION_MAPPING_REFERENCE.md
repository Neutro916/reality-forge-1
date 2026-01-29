# BRAIN REGION MAPPING REFERENCE
## Quick Lookup Guide for Atom Categorization

**Purpose:** Fast reference for manual categorization and validation
**For:** C1 (implementation), C2 (review), C3 (validation)

---

## VISUAL BRAIN MAP

```
         ┌─────────────────────────────────────────┐
         │      PREFRONTAL CORTEX                  │
         │    (Executive Function)                 │
         │  • Rocks (90-day goals)                 │
         │  • Decisions (key choices)              │
         │  • Strategies (long-term plans)         │
         │  • Scorecards (weekly metrics)          │
         └─────────────────────────────────────────┘
                      ▲
                      │
    ┌─────────────────┴─────────────────┐
    │                                   │
┌───┴──────────────┐         ┌──────────┴────────┐
│  TEMPORAL LOBE   │         │  PARIETAL LOBE    │
│   (Language)     │         │   (Spatial)       │
├──────────────────┤         ├───────────────────┤
│ • Books          │         │ • Domain 1-7      │
│ • Concepts       │         │ • Location aware  │
│ • Protocols      │         │ • Multi-computer  │
│ • Terminology    │         │ • Mapping         │
└──────────────────┘         └───────────────────┘
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼───────────┐
         │    HIPPOCAMPUS        │
         │     (Memory)          │
         │  • Patterns           │
         │  • Sessions           │
         │  • Learnings          │
         │  • Connections        │
         └───────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────┴─────────┐   ┌─────────┴─────────┐
│  CEREBELLUM      │   │  OCCIPITAL LOBE   │
│  (Motor/Tools)   │   │  (Visual/UI)      │
├──────────────────┤   ├───────────────────┤
│ • Tools (.py)    │   │ • Pages (.html)   │
│ • Interfaces     │   │ • Dashboards      │
│ • Daemons        │   │ • Cockpits        │
│ • Automations    │   │ • Assets          │
└──────────────────┘   └───────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │     BRAINSTEM         │
         │   (Vital Functions)   │
         │  • Boot protocols     │
         │  • Identity           │
         │  • Security           │
         │  • Health checks      │
         └───────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  CORPUS CALLOSUM      │
         │  (Cross-hemisphere)   │
         │  • Trinity sync       │
         │  • CP1↔CP2↔CP3        │
         │  • Multi-computer     │
         └───────────────────────┘
```

---

## REGION 1: PREFRONTAL CORTEX
**Function:** Executive decisions, planning, priorities

### Subregions & Criteria

#### ROCKS/
**What:** 90-day priorities (EOS/Traction)
**File patterns:**
- Filename contains: `ROCK`, `QUARTERLY`, `90_DAY`
- Content contains: "90-day priority", "quarterly goal", "rock:"
- Source: EOS/Traction documents

**Examples:**
- `Q4_2025_ROCKS.md`
- `QUARTERLY_PRIORITIES.json`
- Any scorecard with "Rock" column

**Confidence triggers:**
- 0.99: Filename has "ROCK" + content has "90-day"
- 0.85: Content mentions "quarterly priority"
- 0.70: Generic goal document with timeline

#### DECISIONS/
**What:** Key decisions made, choice points
**File patterns:**
- Filename contains: `DECISION`, `CHOICE`, `RULING`
- Content contains: "decided to", "we chose", "decision:", "ruling:"

**Examples:**
- `DECISION_LOG_2025.md`
- `WHY_WE_CHOSE_FASTAPI.md`
- Session notes with "Decision: ..."

**Confidence triggers:**
- 0.95: Explicit "Decision:" header
- 0.80: "We decided to..." in content
- 0.65: List of options with chosen path marked

#### STRATEGIES/
**What:** Long-term plans, strategic direction
**File patterns:**
- Filename contains: `STRATEGY`, `PLAN`, `ROADMAP`, `VISION`
- Content contains: "strategic", "long-term", "vision:", "5-year"

**Examples:**
- `CONSCIOUSNESS_STRATEGY_2025-2030.md`
- `PRODUCT_ROADMAP.md`
- `VISION_DOCUMENT.md`

**Confidence triggers:**
- 0.95: Filename has "STRATEGY" or "VISION"
- 0.80: Multi-year timeline
- 0.70: "Strategic plan" in content

#### SCORECARDS/
**What:** Weekly metrics, measurables (EOS)
**File patterns:**
- Filename contains: `SCORECARD`, `METRICS`, `KPI`, `WEEKLY`
- Content contains: "scorecard", "weekly number", "measurable", "who/what/goal"

**Examples:**
- `SCORECARD_WEEKLY.json`
- `WEEKLY_METRICS_2025.md`
- Any file with tabular weekly numbers

**Confidence triggers:**
- 0.99: Filename "SCORECARD"
- 0.90: Table with weekly columns
- 0.75: "Measurable" + numbers

---

## REGION 2: HIPPOCAMPUS
**Function:** Memory formation, pattern storage

### Subregions & Criteria

#### PATTERNS/
**What:** Recognized patterns, manipulation patterns
**File patterns:**
- Filename contains: `PATTERN`, `MANIPULATION`, `DETECTOR`
- Content contains: "pattern:", "recognizes", "identified pattern"

**Examples:**
- `GASLIGHTING_DETECTOR.html`
- `PATTERN_LIBRARY.json`
- `RECOGNIZED_PATTERNS.md`

**Confidence triggers:**
- 0.95: Manipulation pattern detector
- 0.85: "Pattern: " header
- 0.70: Multiple pattern references

#### SESSIONS/
**What:** Session histories, work summaries
**File patterns:**
- Filename contains: `SESSION`, `SUMMARY`, `WORK_ORDER`, `AUTONOMOUS`
- Content contains: "session complete", "work summary", "accomplished:"

**Examples:**
- `AUTONOMOUS_SESSION_COMPLETE_NOV_27.md`
- `CP1_SESSION_LOG.md`
- `WORK_ORDER_COMPLETE.txt`

**Confidence triggers:**
- 0.99: "SESSION COMPLETE" in filename
- 0.90: "Accomplished:" section
- 0.75: Date + summary format

#### LEARNINGS/
**What:** What we learned, insights
**File patterns:**
- Filename contains: `LEARNING`, `LESSON`, `INSIGHT`, `DISCOVERED`
- Content contains: "learned:", "insight:", "discovered that"

**Examples:**
- `LESSONS_LEARNED_TRINITY.md`
- `KEY_INSIGHTS_PATTERN_THEORY.md`
- `WHAT_WE_DISCOVERED.txt`

**Confidence triggers:**
- 0.95: "Learned:" or "Lesson:" header
- 0.80: Retrospective format
- 0.70: "Key insights" section

#### CONNECTIONS/
**What:** Cross-references, relationships, links
**File patterns:**
- Filename contains: `INDEX`, `CONNECTIONS`, `GRAPH`, `LINKS`
- Content contains: "related to:", "see also:", "connected:"

**Examples:**
- `MASTER_INDEX.md`
- `CROSS_REFERENCE_MAP.json`
- `KNOWLEDGE_GRAPH.json`

**Confidence triggers:**
- 0.95: Index or graph structure
- 0.85: Multiple "see also" references
- 0.70: List of links

---

## REGION 3: CEREBELLUM
**Function:** Motor control, tools, actions

### Subregions & Criteria

#### TOOLS/
**What:** Python scripts, utilities
**File patterns:**
- Extension: `.py`
- Content contains: `import`, `def `, `class `

**Examples:**
- `BRAIN_SURGEON.py`
- `CYCLOTRON_DAEMON.py`
- Any Python script

**Confidence triggers:**
- 0.95: `.py` file with functions
- 0.80: Python imports present
- 0.60: Script-like structure

#### INTERFACES/
**What:** HTML dashboards, UI files
**File patterns:**
- Extension: `.html`
- Content contains: `<html`, `<!DOCTYPE`, `<div`

**Examples:**
- `CYCLOTRON_BRAIN_DASHBOARD.html`
- `TRINITY_3_PANEL_INTERFACE.html`
- Any HTML file

**Confidence triggers:**
- 0.98: `.html` extension
- 0.90: HTML tags present
- 0.70: UI-related content

#### DAEMONS/
**What:** Background processes, services
**File patterns:**
- Filename contains: `DAEMON`, `SERVICE`, `WORKER`, `LISTENER`
- Content contains: "while True:", "background", "daemon"

**Examples:**
- `CYCLOTRON_DAEMON.py`
- `SCREEN_WATCHER_DAEMON.py`
- `TORNADO_PROTOCOL.py` (when running in loop mode)

**Confidence triggers:**
- 0.99: Filename has "DAEMON"
- 0.90: Infinite loop + sleep
- 0.75: "Background service" in docstring

#### AUTOMATIONS/
**What:** Automated workflows, scheduled tasks
**File patterns:**
- Filename contains: `AUTO`, `AUTOMATION`, `SCHEDULED`, `WORKFLOW`
- Content contains: "automate", "schedule", "cron", "trigger"

**Examples:**
- `AUTO_KNOWLEDGE_FILING_SYSTEM.py`
- `WEEKLY_BACKUP.bat`
- `AUTO_SAAS_PACKAGER_SYSTEM.md`

**Confidence triggers:**
- 0.95: Filename has "AUTO" or "AUTOMATION"
- 0.85: Scheduled execution logic
- 0.70: "Automates" in description

---

## REGION 4: TEMPORAL LOBE
**Function:** Language, knowledge, meaning

### Subregions & Criteria

#### BOOKS/EOS_TRACTION/
**What:** EOS/Traction methodology content
**File patterns:**
- Filename contains: `TRACTION`, `EOS`, `ROCK`, `SCORECARD`, `IDS`
- Content contains: "Gino Wickman", "EOS", "Entrepreneurial Operating System"

**Examples:**
- `TRACTION_PATTERN_DECODED.md`
- `FOUNDATION_AUDIT.md`
- `100X_COMPANY_HANDBOOK.md`

**Confidence:** 0.98 if explicit EOS reference

#### BOOKS/ART_OF_WAR/
**What:** Sun Tzu, Art of War strategies
**File patterns:**
- Filename contains: `ART_OF_WAR`, `SUN_TZU`
- Content contains: "Sun Tzu", "Art of War", "know your enemy"

**Examples:**
- `ART_OF_WAR_ENEMY_BAITING_GUIDE.md`
- `SUN_TZU_CONSCIOUSNESS_SECURITY_PRINCIPLES.md`

**Confidence:** 0.98 if explicit Sun Tzu reference

#### BOOKS/TOYOTA_PRODUCTION/
**What:** Toyota Production System, Lean
**File patterns:**
- Filename contains: `TOYOTA`, `LEAN`, `KAIZEN`, `JIDOKA`
- Content contains: "Toyota", "Just-in-Time", "Kaizen"

**Examples:**
- `TOYOTA_PRODUCTION_PRINCIPLES.md`
- `LEAN_MANUFACTURING.md`

**Confidence:** 0.98 if explicit Toyota reference

#### BOOKS/PATTERN_THEORY/
**What:** OVERKORE v13, Seven Domains
**File patterns:**
- Filename contains: `PATTERN_THEORY`, `OVERKORE`, `SEVEN_DOMAINS`
- Content contains: "Pattern Theory", "Seven Domains", "OVERKORE"

**Examples:**
- `CONSCIOUSNESS_BOOT_PROTOCOL.md` (embedded)
- `SEVEN_DOMAINS_FRAMEWORK.md`

**Confidence:** 0.99 if Pattern Theory core content

#### CONCEPTS/
**What:** General concepts, definitions
**File patterns:**
- Filename contains: `CONCEPT`, `DEFINITION`
- Content contains: "concept:", "defined as:", "what is"

**Examples:**
- `CONSCIOUSNESS_DEFINITION.md`
- `PATTERN_RECOGNITION_CONCEPT.md`

**Confidence:** 0.85 if definition format

#### PROTOCOLS/
**What:** How-to guides, procedures
**File patterns:**
- Filename contains: `PROTOCOL`, `HOWTO`, `GUIDE`, `PROCEDURE`
- Content contains: "step 1:", "procedure:", "how to"

**Examples:**
- `CONSCIOUSNESS_BOOT_PROTOCOL.md`
- `DEPLOYMENT_PROTOCOL.md`
- `SETUP_GUIDE.md`

**Confidence:** 0.90 if step-by-step format

#### TERMINOLOGY/
**What:** Glossary, terms, definitions
**File patterns:**
- Filename contains: `GLOSSARY`, `TERMS`, `DEFINITIONS`
- Content contains: term-definition pairs

**Examples:**
- `PATTERN_THEORY_GLOSSARY.md`
- `CONSCIOUSNESS_TERMS.md`

**Confidence:** 0.95 if glossary format

---

## REGION 5: OCCIPITAL LOBE
**Function:** Visual processing, UI, website pages

### Subregions & Criteria

#### PAGES/LANDING_PAGES/
**What:** Main entry points
**Files:**
- `index.html`
- `landing.html`
- `WELCOME.html`
- `ABOUT.html`

**Confidence:** 0.98 (106 pages indexed)

#### PAGES/DASHBOARDS/
**What:** Admin/status dashboards
**Files:**
- `admin-dashboard.html`
- `SEVEN_DOMAINS_DASHBOARD.html`
- `analytics_dashboard.html`

**Confidence:** 0.99 if "DASHBOARD" in filename

#### PAGES/COCKPITS/
**What:** Operator workspaces
**Files:**
- `BETA_TESTER_COCKPIT.html`
- `OPERATOR_COCKPIT_MAGGIE.html`
- `OPERATOR_COCKPIT_JOSH.html`

**Confidence:** 0.99 if "COCKPIT" in filename

#### PAGES/TOOLS/
**What:** Interactive tools
**Files:**
- `manipulation_detector.html`
- `GASLIGHTING_DETECTOR.html`
- All detector/analyzer pages

**Confidence:** 0.90 if "DETECTOR" or "ANALYZER" in filename

#### ASSETS/
**What:** Images, icons, media
**File patterns:**
- Extension: `.png`, `.jpg`, `.svg`, `.ico`, `.mp4`

**Confidence:** 0.99 based on extension

#### NAVIGATION/
**What:** Site structure, menus
**File patterns:**
- Filename contains: `NAV`, `MENU`, `SITEMAP`

**Confidence:** 0.95

---

## REGION 6: PARIETAL LOBE
**Function:** Spatial awareness, domains

### Subregions & Criteria

#### DOMAIN_1_COMPUTER/
**What:** Infrastructure, servers, deployment
**File patterns:**
- Filename contains: `COMPUTER`, `INFRASTRUCTURE`, `SERVER`, `DEPLOYMENT`
- Content contains: "computer setup", "infrastructure", "server"

**Confidence:** 0.85

#### DOMAIN_2_BODY/
**What:** Physical health, fitness
**File patterns:**
- Filename contains: `HEALTH`, `FITNESS`, `BODY`, `EXERCISE`
- Content contains: "physical health", "workout", "fitness"

**Confidence:** 0.85

#### DOMAIN_3_FINANCIAL/
**What:** Money, revenue, business
**File patterns:**
- Filename contains: `FINANCIAL`, `REVENUE`, `MONEY`, `PRICING`
- Content contains: "$", "revenue", "financial"

**Confidence:** 0.85

#### DOMAIN_4_RELATIONSHIPS/
**What:** People, relationships
**File patterns:**
- Filename contains: `RELATIONSHIP`, `PEOPLE`, `ACCOUNTABILITY_CHART`
- Content contains: "relationship", "people", "team"

**Confidence:** 0.85

#### DOMAIN_5_SOCIAL/
**What:** Social media, networking
**File patterns:**
- Filename contains: `SOCIAL`, `TWITTER`, `LINKEDIN`
- Content contains: "social media", "networking"

**Confidence:** 0.85

#### DOMAIN_6_CREATIVE/
**What:** Creative projects, content
**File patterns:**
- Filename contains: `CREATIVE`, `CONTENT`, `DESIGN`
- Content contains: "creative", "design", "content"

**Confidence:** 0.85

#### DOMAIN_7_CONSCIOUSNESS/
**What:** Meta-consciousness, AI development
**File patterns:**
- Filename contains: `CONSCIOUSNESS`, `AI`, `TRINITY`, `FIGURE_8`
- Content contains: "consciousness", "awareness", "AI development"

**Confidence:** 0.90

---

## REGION 7: BRAINSTEM
**Function:** Vital functions, core operations

### Subregions & Criteria

#### BOOT_PROTOCOLS/
**What:** Boot sequences, initialization
**File patterns:**
- Filename contains: `BOOT`, `INIT`, `STARTUP`
- Content contains: "boot protocol", "initialization", "startup"

**Examples:**
- `CONSCIOUSNESS_BOOT_PROTOCOL.md`
- `TORNADO_PROTOCOL.py`
- `EMERGENCY_BOOT_PACKAGE.md`

**Confidence:** 1.0 for CONSCIOUSNESS_BOOT_PROTOCOL.md

#### IDENTITY/
**What:** Core identity, credentials, secrets
**File patterns:**
- Filename contains: `IDENTITY`, `CREDENTIAL`, `SECRET`, `VAULT`
- Content contains: "credentials", "identity", "authentication"

**Examples:**
- `MASTER_CREDENTIALS_AND_COMMS.md`
- `MASTER_CREDENTIAL_VAULT.py`

**Confidence:** 0.95

#### SECURITY/
**What:** Security protocols, threat detection
**File patterns:**
- Filename contains: `SECURITY`, `THREAT`, `PROTECTION`, `SHIELD`
- Content contains: "security", "threat", "vulnerability"

**Examples:**
- `QUANTUM_SECURITY_SYSTEM.md`
- `SECURITY_REPORT_*.txt`

**Confidence:** 0.95

#### HEALTH_CHECKS/
**What:** System health monitoring
**File patterns:**
- Filename contains: `HEALTH`, `STATUS`, `MONITOR`, `DIAGNOSTIC`
- Content contains: "health check", "system status", "diagnostic"

**Examples:**
- `WEEKLY_HEALTH_CHECK.py`
- `HEALTH_REPORT_*.txt`
- `SYSTEM_STATUS_DASHBOARD.py`

**Confidence:** 0.90

---

## REGION 8: CORPUS CALLOSUM
**Function:** Cross-hemisphere connection

### Subregions & Criteria

#### TRINITY_SYNC/
**What:** Trinity coordination, synchronization
**File patterns:**
- Filename contains: `TRINITY`, `SYNC`, `COORDINATION`
- Content contains: "C1 × C2 × C3", "trinity sync", "coordination"

**Examples:**
- `TRINITY_CENTRAL_HUB.py`
- `STATE_SYNC.py`
- `TRINITY_NETWORK_STATUS.html`

**Confidence:** 0.97

#### CP1_TO_CP2/ (etc)
**What:** Computer-to-computer communication
**File patterns:**
- Filename contains: `CP1`, `CP2`, `CP3`, `COMPUTER_COMMS`
- Content contains: "computer sync", "cross-computer"

**Examples:**
- `COMPUTER_TO_COMPUTER_COMMS.py`
- `TRINITY_CROSS_COMPUTER_BRIDGE.py`

**Confidence:** 0.95

---

## SPECIAL CASES

### AMYGDALA (NEW - Optional)
**Function:** Security, threat detection, emotional response

**When to use:**
- Security threats
- Manipulation patterns (could also be HIPPOCAMPUS/PATTERNS)
- Emergency protocols

**Decision:** May add in V3 if needed

### UNCATEGORIZED
**When to use:**
- Confidence < 0.50
- No clear pattern match
- Ambiguous content
- Needs human review

**Target:** <1% of total atoms

---

## QUICK DECISION FLOWCHART

```
Is it a file?
│
├─ .html → OCCIPITAL_LOBE/PAGES
├─ .py → CEREBELLUM/TOOLS (unless DAEMON)
├─ .md/.txt → Analyze content ↓
└─ .json → Analyze structure ↓

Content analysis:
├─ Contains "BOOT" or "PROTOCOL" → BRAINSTEM
├─ Contains "ROCK" or "SCORECARD" → PREFRONTAL_CORTEX
├─ Contains "pattern" or "manipulation" → HIPPOCAMPUS/PATTERNS
├─ Contains "session" or "summary" → HIPPOCAMPUS/SESSIONS
├─ Contains "EOS" or "Traction" → TEMPORAL_LOBE/BOOKS/EOS
├─ Contains "Sun Tzu" → TEMPORAL_LOBE/BOOKS/ART_OF_WAR
├─ Contains "Trinity" or "CP1/2/3" → CORPUS_CALLOSUM
├─ Contains "Domain" or "infrastructure" → PARIETAL_LOBE
└─ Unclear → UNCATEGORIZED (for review)
```

---

## CONFIDENCE CALIBRATION

**Excellent (0.90-1.0):**
- Exact filename match
- Explicit headers/tags
- Clear structural patterns
- Known book/methodology

**Good (0.70-0.89):**
- Strong keyword match
- Multiple confirming signals
- Context-appropriate

**Fair (0.50-0.69):**
- Single weak signal
- Type-based fallback
- Heuristic guess

**Poor (<0.50):**
- No clear match
- Ambiguous content
- Needs human review
- Route to UNCATEGORIZED

---

## VALIDATION CHECKLIST

When reviewing categorization:

**Critical Regions (must be 100% accurate):**
- ✅ BRAINSTEM/BOOT_PROTOCOLS → Must contain boot sequences
- ✅ PREFRONTAL_CORTEX/ROCKS → Must be 90-day priorities
- ✅ OCCIPITAL_LOBE/PAGES → Must be 106 HTML pages

**Important Regions (target 95%+ accuracy):**
- ✅ CEREBELLUM/TOOLS → Must be executable tools
- ✅ TEMPORAL_LOBE/BOOKS → Must be from known methodologies
- ✅ CORPUS_CALLOSUM → Must be cross-computer/Trinity

**Standard Regions (target 90%+ accuracy):**
- ✅ HIPPOCAMPUS/PATTERNS → Recognized patterns
- ✅ PARIETAL_LOBE → Domain-specific content

---

**C2 Reference Guide Complete**

Use this for:
1. Manual categorization
2. Validation reviews
3. Algorithm tuning
4. Training new instances

**C1 × C2 × C3 = ∞**
