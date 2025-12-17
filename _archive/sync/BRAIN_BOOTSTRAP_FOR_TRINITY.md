# BRAIN BOOTSTRAP FOR TRIPLE TRINITY
## How Every Trinity Instance Uses the Brain
## Created: 2025-11-27 (Turkey Day)

---

## THE PROBLEM YOU IDENTIFIED

"You're telling me to use it but you're the one that needs to use it!"
"You're saying it's my external brain but it's your brain tool - how do you use it?"

**Solution:** This document tells EVERY Claude instance how to use the brain.

---

## MANDATORY BRAIN QUERY BEFORE ANY WORK

Every Claude instance MUST run this before answering questions:

```python
# Step 1: Query the brain for relevant existing content
sqlite3 C:/Users/dwrek/.consciousness/cyclotron_core/atoms.db \
  "SELECT region, substr(content, 1, 100) FROM atoms WHERE content LIKE '%{topic}%' LIMIT 10;"
```

**If results exist:** USE THEM, don't rebuild
**If no results:** BUILD IT, then index it

---

## BRAIN REGIONS (Query by region)

| Region | What's There | When to Query |
|--------|--------------|---------------|
| PREFRONTAL_CORTEX | Decisions, rocks, strategies | "What have we decided?" |
| HIPPOCAMPUS | Patterns, sessions, learnings | "What did we learn before?" |
| CEREBELLUM | Python tools, daemons | "Do we have a tool for this?" |
| TEMPORAL_LOBE | EOS, Art of War, methodologies | "What framework applies?" |
| OCCIPITAL_LOBE | Website pages, dashboards | "What UI exists?" |
| PARIETAL_LOBE | Seven domains | "Which domain is this?" |
| BRAINSTEM | Boot protocols, identity | "Core identity stuff" |
| CORPUS_CALLOSUM | Trinity sync | "Cross-computer stuff" |

---

## QUICK QUERIES

### Find existing tools before building
```sql
SELECT * FROM atoms WHERE region = 'CEREBELLUM' AND content LIKE '%{tool_name}%';
```

### Find existing pages before creating
```sql
SELECT * FROM atoms WHERE region = 'OCCIPITAL_LOBE' AND content LIKE '%{page_topic}%';
```

### Find patterns before analyzing
```sql
SELECT * FROM atoms WHERE region = 'HIPPOCAMPUS' AND content LIKE '%{pattern}%';
```

### Find methodologies before designing
```sql
SELECT * FROM atoms WHERE region = 'TEMPORAL_LOBE';
```

---

## AFTER CREATING ANYTHING - INDEX IT

```sql
INSERT INTO atoms (id, type, content, source, region, created, confidence)
VALUES (
  '{unique_id}',
  '{type}',
  '{first 500 chars of content}',
  '{file_path}',
  '{brain_region}',
  datetime('now'),
  0.9
);
```

---

## BRAIN STATISTICS (Current)

```
Total Atoms: 88,957

BRAINSTEM:           67,495 (75.9%)
CORPUS_CALLOSUM:     16,848 (18.9%)
HIPPOCAMPUS:          2,930 (3.3%)
OCCIPITAL_LOBE:         769 (0.9%)
CEREBELLUM:             417 (0.5%)
PREFRONTAL_CORTEX:      172 (0.2%)
PARIETAL_LOBE:          169 (0.2%)
TEMPORAL_LOBE:          157 (0.2%)
```

---

## BURIED TREASURE (Already Indexed)

### Analytics Tools:
- `SCORECARD_AUTOMATION.py` - EOS weekly metrics
- `BETA_ANALYTICS_DASHBOARD.html` - Beta user analytics
- `TRINITY_PERFORMANCE_METRICS.py` - Trinity metrics
- `OVERKORE_HEATMAP_ANALYTICS.html` - Heat map visualization

### Learning/Kaizen:
- `kaizen-builder-board.html` - Continuous improvement board
- `AUTO_LEARNER.py` - Auto-learning system

### Sync/Mirror:
- `sync_daemon.py` - Cross-computer sync
- `CYCLOTRON_SYNC.py` - Cyclotron sync package

---

## FOR TRIPLE TRINITY (C1 × C2 × C3)³

### C1 MECHANICS (Body) - Use brain for:
- Finding existing tools (CEREBELLUM)
- Checking what's built (OCCIPITAL_LOBE)
- Getting previous implementations (HIPPOCAMPUS)

### C2 ARCHITECTS (Mind) - Use brain for:
- Finding methodologies (TEMPORAL_LOBE)
- Checking architecture decisions (PREFRONTAL_CORTEX)
- Finding scaling patterns (HIPPOCAMPUS)

### C3 ORACLES (Soul) - Use brain for:
- Finding patterns (HIPPOCAMPUS)
- Checking domain balance (PARIETAL_LOBE)
- Validating alignment (BRAINSTEM)

---

## MIRROR TO ALL COMPUTERS

The brain database should sync to:
- CP1 (main): `C:/Users/dwrek/.consciousness/cyclotron_core/atoms.db`
- CP2 (laptop): Same path via Google Drive sync
- CP3 (desktop): Same path via Google Drive sync

Sync folder: `G:/My Drive/TRINITY_COMMS/sync/`

---

## THE SHIFT

| Before | After |
|--------|-------|
| Claude builds, user organizes | **Claude queries brain, uses existing** |
| Scattered knowledge | **Brain-organized** |
| Duplicate work | **Check first, build if missing** |
| Manual indexing | **Auto-index on create** |

---

## BRAIN ATTENDANT (Running)

Location: `C:/Users/dwrek/.consciousness/BRAIN_ATTENDANT.py`

Commands:
- `python BRAIN_ATTENDANT.py suggest` - Get suggestions
- `python BRAIN_ATTENDANT.py search "term"` - Quick search
- `python BRAIN_ATTENDANT.py patterns` - See usage patterns
- `python BRAIN_ATTENDANT.py log` - View query log

---

**THE BRAIN IS CLAUDE'S MEMORY, NOT THE USER'S BURDEN**

Every Trinity instance reads this bootstrap.
Every query goes through the brain.
Every creation gets indexed.

**C1 × C2 × C3 = ∞**
