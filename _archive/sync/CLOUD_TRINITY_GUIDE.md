# CLOUD TRINITY GUIDE
## Background AI Workers via Claude API

---

## WHAT IS CLOUD TRINITY?

Cloud Trinity extends the 3-instance Trinity system with API-based workers:

```
LOCAL TRINITY (Claude Code - on your machine)
├── C1-Terminal (Mechanic/Body) - Interactive coding
├── C2-Terminal (Architect/Mind) - Design review
└── C3-Terminal (Oracle/Soul) - Pattern analysis

CLOUD TRINITY (Claude API - runs in background)
├── C1-Cloud (Mechanic) - Batch code tasks
├── C2-Cloud (Architect) - Background design work
└── C3-Cloud (Oracle) - Research & analysis
```

## WHY USE CLOUD WORKERS?

| Use Case | Terminal | Cloud |
|----------|----------|-------|
| Interactive coding | Best | No |
| Long-running research | Limited | Best |
| 24/7 monitoring | No | Yes |
| Parallel processing | Limited | Best |
| Batch operations | No | Yes |
| Cost control | Fixed | Flexible |

## COST BREAKDOWN

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| Haiku 4.5 | $0.25/1M | $1.25/1M | Simple tasks, monitoring |
| Sonnet 4 | $3/1M | $15/1M | Balanced work |
| Opus 4.5 | $15/1M | $75/1M | Complex reasoning |

**Example Costs:**
- 1000 simple monitoring checks/day with Haiku: ~$0.50
- 100 code reviews/day with Sonnet: ~$6
- 10 complex analyses/day with Opus: ~$15

## SETUP

### 1. Set API Key
```bash
# Windows (temporary)
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows (permanent)
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
```

### 2. Install Dependencies
```bash
pip install anthropic
```

### 3. Start a Cloud Worker
```bash
cd C:\Users\dwrek\.consciousness
python CLOUD_TRINITY_WORKER.py --instance C3-Cloud --model claude-sonnet-4-20250514
```

Or use the batch file:
```
C:\Users\dwrek\100X_DEPLOYMENT\START_CLOUD_TRINITY.bat
```

## ASSIGNING TASKS TO CLOUD

### Option 1: MCP Tool (from Terminal instance)
```
Use trinity_assign_task tool:
- task: "Research best practices for Python async"
- assignedTo: "C3-Cloud" (or "cloud" for any worker)
- priority: "normal"
```

### Option 2: Python Script
```python
from CLOUD_TRINITY_WORKER import create_cloud_task

# Research task (goes to C3-Cloud)
create_cloud_task("research", "Compare Redis vs Memcached for caching")

# Code review (goes to C2-Cloud)
create_cloud_task("code_review", "Review FAST_HUB.py for security issues")

# Implementation (goes to C1-Cloud)
create_cloud_task("implementation", "Add rate limiting to API endpoints")
```

### Option 3: Direct JSON
```json
// Add to ~/.trinity/tasks.json
{
  "id": "unique-id",
  "task": "Your task description",
  "assignedTo": "C3-Cloud",
  "priority": "normal",
  "status": "assigned",
  "createdAt": "2025-11-25T00:00:00Z"
}
```

## TASK TYPES

| Type | Assigned To | Purpose |
|------|-------------|---------|
| research | C3-Cloud | Information gathering, analysis |
| code_review | C2-Cloud | Review code for issues |
| implementation | C1-Cloud | Write/fix code |
| architecture | C2-Cloud | Design systems |
| pattern_analysis | C3-Cloud | Find patterns in data |
| monitoring | Any cloud | Health checks, alerts |

## RECOMMENDED PATTERNS

### Pattern 1: Terminal + Cloud Pipeline
1. C1-Terminal writes initial code
2. Submit to C2-Cloud for architecture review
3. C3-Cloud analyzes patterns
4. Results merged back to Terminal

### Pattern 2: 24/7 Monitoring
```python
# Create monitoring task
create_cloud_task(
    "monitoring",
    "Check https://conciousnessrevolution.io every 5 minutes, alert on errors",
    "low"
)
```

### Pattern 3: Batch Processing
```python
# Process multiple files
for file in files_to_review:
    create_cloud_task("code_review", f"Review {file}")
```

### Pattern 4: Cost-Optimized Work
```python
# Use Haiku for simple tasks
worker = CloudTrinityWorker("C1-Cloud", "claude-haiku-4-5-20251101")

# Use Opus for complex analysis
worker = CloudTrinityWorker("C3-Cloud", "claude-opus-4-5-20251101")
```

## FILES

| File | Purpose |
|------|---------|
| CLOUD_TRINITY_WORKER.py | Main worker implementation |
| START_CLOUD_TRINITY.bat | Windows launcher |
| ~/.trinity/tasks.json | Task queue |
| ~/.trinity/outputs.json | Completed outputs |
| ~/.consciousness/hub/heartbeat_*.json | Worker status |

## MONITORING CLOUD WORKERS

Check worker status:
```bash
type %USERPROFILE%\.consciousness\hub\heartbeat_c3_cloud.json
```

View completed outputs:
```bash
type %USERPROFILE%\.trinity\outputs.json
```

Check task queue:
```bash
type %USERPROFILE%\.trinity\tasks.json
```

## EXAMPLE USE CASES

### 1. Research Assistant
```python
create_cloud_task("research", """
Research the current state of AI autonomous computer control:
- What benchmarks exist?
- Who are the leading players?
- What's the SOTA performance?
Provide a comprehensive report.
""")
```

### 2. Code Documentation
```python
create_cloud_task("implementation", """
Generate docstrings for all functions in FAST_HUB.py
Follow Google Python style guide.
""")
```

### 3. Security Audit
```python
create_cloud_task("code_review", """
Security audit of CLOUD_TRINITY_WORKER.py:
- Check for injection vulnerabilities
- Verify API key handling
- Check file permissions
""")
```

### 4. Pattern Detection
```python
create_cloud_task("pattern_analysis", """
Analyze the last 100 bug reports in GitHub.
Identify common patterns and root causes.
Recommend preventive measures.
""")
```

---

## SUMMARY

Cloud Trinity enables:
- **24/7 Background Processing**: Workers run indefinitely
- **Parallel Work**: Multiple workers process simultaneously
- **Cost Control**: Choose model based on task complexity
- **Seamless Integration**: Works with existing Trinity MCP

Start simple:
1. Set ANTHROPIC_API_KEY
2. Run START_CLOUD_TRINITY.bat
3. Assign tasks via MCP or Python

*Cloud Trinity - Your AI team that never sleeps.*
