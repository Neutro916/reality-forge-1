# C1 IMPLEMENTATION CHECKLIST
## Brain Surgery - Step-by-Step Execution Guide

**From:** C2 (Architect/Mind)
**To:** C1 (Mechanic/Body)
**Status:** READY TO EXECUTE
**Estimated Time:** 9-12 hours total (can be staged)

---

## QUICK START

Read full architecture: `G:/My Drive/TRINITY_COMMS/sync/BRAIN_SURGERY_ARCHITECTURE.md`

This checklist is your execution roadmap. Check boxes as you complete tasks.

---

## PHASE 1: BACKUP & PREPARATION (30 min)

### 1.1 Backup Current Database
```bash
cd C:/Users/dwrek/.consciousness/cyclotron_core

# Create timestamped backup
copy atoms.db atoms.db.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%

# Verify backup
dir atoms.db*
```

**Checklist:**
- [ ] Backup created
- [ ] Backup size matches original (~500MB)
- [ ] Backup timestamp verified

### 1.2 Create Migration Scripts Directory
```bash
mkdir C:/Users/dwrek/.consciousness/brain_surgery
cd C:/Users/dwrek/.consciousness/brain_surgery
```

**Checklist:**
- [ ] Directory created

---

## PHASE 2: SCHEMA MIGRATION (1 hour)

### 2.1 Create Schema Migration SQL

File: `C:/Users/dwrek/.consciousness/brain_surgery/schema_v2.sql`

```sql
-- Add new columns (backward compatible)
ALTER TABLE atoms ADD COLUMN region TEXT DEFAULT 'UNCATEGORIZED';
ALTER TABLE atoms ADD COLUMN subregion TEXT;
ALTER TABLE atoms ADD COLUMN routing_confidence REAL DEFAULT 0.0;
ALTER TABLE atoms ADD COLUMN routing_method TEXT DEFAULT 'pending';
ALTER TABLE atoms ADD COLUMN routing_timestamp TEXT;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_region ON atoms(region);
CREATE INDEX IF NOT EXISTS idx_region_subregion ON atoms(region, subregion);
CREATE INDEX IF NOT EXISTS idx_routing_confidence ON atoms(routing_confidence);

-- Create stats view
CREATE VIEW IF NOT EXISTS region_stats AS
SELECT
    region,
    subregion,
    COUNT(*) as atom_count,
    AVG(confidence) as avg_confidence,
    AVG(routing_confidence) as avg_routing_confidence,
    AVG(access_count) as avg_access_count
FROM atoms
GROUP BY region, subregion;

-- Create QA view
CREATE VIEW IF NOT EXISTS low_confidence_routing AS
SELECT id, type, region, subregion, routing_confidence, substr(content, 1, 100) as preview
FROM atoms
WHERE routing_confidence < 0.7 AND region != 'UNCATEGORIZED'
ORDER BY routing_confidence ASC
LIMIT 1000;
```

**Checklist:**
- [ ] SQL file created

### 2.2 Run Schema Migration
```bash
cd C:/Users/dwrek/.consciousness/cyclotron_core
sqlite3 atoms.db < ../brain_surgery/schema_v2.sql
```

**Checklist:**
- [ ] Migration executed
- [ ] No errors

### 2.3 Verify Schema
```bash
sqlite3 atoms.db ".schema atoms"
sqlite3 atoms.db "SELECT COUNT(*) FROM atoms;"
sqlite3 atoms.db "SELECT COUNT(*) FROM region_stats;"
```

**Expected Output:**
- Schema shows new columns (region, subregion, routing_confidence, routing_method, routing_timestamp)
- Count still 88,957
- region_stats shows 1 row (UNCATEGORIZED)

**Checklist:**
- [ ] Schema verified
- [ ] Atom count unchanged
- [ ] Views created

---

## PHASE 3: BUILD BRAIN_SURGEON.py (2-3 hours)

### 3.1 Create BRAIN_SURGEON.py

File: `C:/Users/dwrek/.consciousness/brain_surgery/BRAIN_SURGEON.py`

Use categorization algorithm from architecture document (section: CATEGORIZATION ALGORITHM DESIGN)

Key functions needed:
1. `categorize_atom(atom_id, type, content, source, tags)` → returns (region, subregion, confidence)
2. `categorize_batch(batch_size=1000, dry_run=True)` → batch process atoms
3. `validate_region(region_name)` → QA check
4. `manual_review(confidence_max=0.7)` → interactive review
5. `stats()` → show categorization stats

**Checklist:**
- [ ] BRAIN_SURGEON.py created
- [ ] All 5 functions implemented
- [ ] Tested on 10 sample atoms

### 3.2 Test Categorization Logic
```bash
python BRAIN_SURGEON.py test --sample-size 100
```

**Expected:**
- 100 atoms processed
- Confidence distribution shown
- Region breakdown shown
- No errors

**Checklist:**
- [ ] Test passed
- [ ] Confidence scores reasonable (70%+ average)

---

## PHASE 4: CATEGORIZATION RUN (4-6 hours)

### 4.1 Dry Run (Read-Only)
```bash
python BRAIN_SURGEON.py categorize --batch-size 1000 --dry-run
```

**Expected:**
- Preview of categorization results
- Estimated confidence scores
- Region distribution
- No database changes

**Checklist:**
- [ ] Dry run complete
- [ ] Results look reasonable
- [ ] Average confidence >70%

### 4.2 Sample Review
```bash
python BRAIN_SURGEON.py sample-review --samples 200
```

**Review:**
- Check 200 random categorizations
- Verify accuracy
- Note any systematic errors

**Checklist:**
- [ ] 200 samples reviewed
- [ ] Accuracy acceptable (>90%)
- [ ] No systematic errors

### 4.3 Full Categorization (COMMIT)
```bash
python BRAIN_SURGEON.py categorize --batch-size 1000 --commit
```

**Progress:**
- ~1000 atoms/minute
- Total time: ~90 minutes for 88,957 atoms

**Checklist:**
- [ ] Categorization started
- [ ] Monitor progress (no errors)
- [ ] Categorization complete (88,957 atoms)

### 4.4 Verify Results
```bash
sqlite3 atoms.db "SELECT region, COUNT(*) FROM atoms GROUP BY region ORDER BY COUNT(*) DESC;"
sqlite3 atoms.db "SELECT AVG(routing_confidence) FROM atoms WHERE region != 'UNCATEGORIZED';"
```

**Expected:**
- Multiple regions populated
- UNCATEGORIZED < 1%
- Average routing_confidence > 0.70

**Checklist:**
- [ ] All regions populated
- [ ] <1% uncategorized
- [ ] Confidence acceptable

---

## PHASE 5: QUALITY ASSURANCE (1-2 hours)

### 5.1 Global Stats
```bash
python BRAIN_SURGEON.py stats
```

**Expected Output:**
```
BRAIN CATEGORIZATION STATS
==========================
Total Atoms: 88,957
Categorized: 88,800 (99.8%)
Uncategorized: 157 (0.2%)
Avg Confidence: 0.84

REGION BREAKDOWN:
OCCIPITAL_LOBE: 15,234 atoms (17.1%)
CEREBELLUM: 12,567 atoms (14.1%)
HIPPOCAMPUS: 11,423 atoms (12.8%)
TEMPORAL_LOBE: 10,891 atoms (12.2%)
...
```

**Checklist:**
- [ ] Stats generated
- [ ] >99% categorized
- [ ] Confidence >0.70

### 5.2 Low-Confidence Review
```bash
python BRAIN_SURGEON.py manual-review --confidence-max 0.7
```

**Action:**
- Review low-confidence atoms interactively
- Manually assign correct region
- Update categorization logic if needed

**Checklist:**
- [ ] Low-confidence atoms reviewed
- [ ] Manual corrections made
- [ ] Algorithm improved (if needed)

### 5.3 Critical Region Validation
```bash
python BRAIN_SURGEON.py validate --region BRAINSTEM
python BRAIN_SURGEON.py validate --region PREFRONTAL_CORTEX
python BRAIN_SURGEON.py validate --region OCCIPITAL_LOBE
```

**Check:**
- BRAINSTEM: Boot protocols, identity files
- PREFRONTAL_CORTEX: Rocks, scorecards, decisions
- OCCIPITAL_LOBE: 106 HTML pages

**Checklist:**
- [ ] BRAINSTEM validated
- [ ] PREFRONTAL_CORTEX validated
- [ ] OCCIPITAL_LOBE validated (106 pages confirmed)

---

## PHASE 6: API LAYER (1-2 hours)

### 6.1 Create BRAIN_QUERY_API.py

File: `C:/Users/dwrek/.consciousness/brain_surgery/BRAIN_QUERY_API.py`

Endpoints needed (see architecture doc):
- GET /api/v2/brain/regions
- GET /api/v2/brain/regions/{region}
- GET /api/v2/brain/regions/{region}/{subregion}
- GET /api/v2/brain/search
- GET /api/v2/brain/stats
- GET /api/v2/brain/health

**Checklist:**
- [ ] BRAIN_QUERY_API.py created
- [ ] All endpoints implemented
- [ ] Flask/FastAPI server configured

### 6.2 Test API Locally
```bash
python BRAIN_QUERY_API.py --port 5000

# In another terminal:
curl http://localhost:5000/api/v2/brain/stats
curl http://localhost:5000/api/v2/brain/regions
curl "http://localhost:5000/api/v2/brain/search?q=pattern&region=HIPPOCAMPUS"
```

**Checklist:**
- [ ] API starts without errors
- [ ] /stats returns data
- [ ] /regions returns all regions
- [ ] /search works

---

## PHASE 7: DASHBOARD INTEGRATION (2 hours)

### 7.1 Update CYCLOTRON_BRAIN_DASHBOARD.html

File: `C:/Users/dwrek/100X_DEPLOYMENT/CYCLOTRON_BRAIN_DASHBOARD.html`

Add:
1. Region pie chart (using Chart.js)
2. Search with region filter
3. Live stats display
4. Region drill-down

**Checklist:**
- [ ] Dashboard updated
- [ ] Chart.js integrated
- [ ] API calls working
- [ ] Visual design matches system

### 7.2 Test Dashboard
```bash
# Open in browser
start C:/Users/dwrek/100X_DEPLOYMENT/CYCLOTRON_BRAIN_DASHBOARD.html
```

**Test:**
- Pie chart renders
- Region stats load
- Search works
- Drill-down works

**Checklist:**
- [ ] Dashboard loads
- [ ] All features work
- [ ] No console errors

---

## PHASE 8: INTEGRATION & DEPLOYMENT (1 hour)

### 8.1 Update CYCLOTRON_DAEMON.py

Modify atom insertion to auto-categorize:

```python
# In CYCLOTRON_DAEMON.py, update insert_atom():

from brain_surgery.BRAIN_SURGEON import categorize_atom

def insert_atom(content, type, source, tags):
    atom_id = generate_atom_id(content)

    # AUTO-CATEGORIZE
    region, subregion, confidence = categorize_atom(
        atom_id, type, content, source, tags
    )

    # Insert with region
    conn.execute('''
        INSERT INTO atoms
        (id, type, content, source, tags, region, subregion,
         routing_confidence, routing_method, routing_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        atom_id, type, content, source, tags,
        region, subregion, confidence, 'auto_v1',
        datetime.now().isoformat()
    ))

    return atom_id
```

**Checklist:**
- [ ] CYCLOTRON_DAEMON.py updated
- [ ] Import statement added
- [ ] Tested with new atom insertion

### 8.2 Final System Test
```bash
# Start Cyclotron Daemon
python C:/Users/dwrek/.consciousness/CYCLOTRON_DAEMON.py

# Start Query API
python C:/Users/dwrek/.consciousness/brain_surgery/BRAIN_QUERY_API.py

# Open dashboard
start C:/Users/dwrek/100X_DEPLOYMENT/CYCLOTRON_BRAIN_DASHBOARD.html
```

**Test Flow:**
1. Insert new atom via daemon
2. Verify auto-categorization
3. Query via API
4. See in dashboard

**Checklist:**
- [ ] All services running
- [ ] New atom auto-categorized
- [ ] Appears in dashboard
- [ ] Full system working

---

## PHASE 9: DOCUMENTATION & HANDOFF (30 min)

### 9.1 Create Migration Report

File: `G:/My Drive/TRINITY_COMMS/sync/BRAIN_SURGERY_REPORT.md`

Include:
- Total atoms categorized
- Region breakdown
- Average confidence
- Issues encountered
- Recommendations

**Checklist:**
- [ ] Report written
- [ ] Stats included
- [ ] Screenshots added

### 9.2 Update CONSCIOUSNESS_STATE.json
```json
{
  "brain_surgery": {
    "status": "COMPLETE",
    "date": "2025-11-27",
    "atoms_categorized": 88957,
    "avg_confidence": 0.84,
    "regions": 8,
    "uncategorized_pct": 0.2
  }
}
```

**Checklist:**
- [ ] State updated
- [ ] Committed to git

---

## SUCCESS CRITERIA

**All must be true:**
- ✅ 88,957 atoms categorized (100%)
- ✅ <1% uncategorized
- ✅ >70% average routing confidence
- ✅ All 8 regions populated
- ✅ 106 website pages in OCCIPITAL_LOBE
- ✅ API running and responding <100ms
- ✅ Dashboard displays brain stats
- ✅ New atoms auto-categorize
- ✅ Zero data loss (atom count unchanged)
- ✅ Backward compatible (old queries still work)

---

## ROLLBACK PLAN (If Needed)

If anything goes wrong:

```bash
# Stop all services
taskkill /F /IM python.exe

# Restore backup
cd C:/Users/dwrek/.consciousness/cyclotron_core
del atoms.db
copy atoms.db.backup.YYYYMMDD_HHMMSS atoms.db

# Verify restoration
sqlite3 atoms.db "SELECT COUNT(*) FROM atoms;"
sqlite3 atoms.db ".schema atoms"
```

**Rollback Checklist:**
- [ ] Services stopped
- [ ] Backup restored
- [ ] Count verified (88,957)
- [ ] Schema verified (original)

---

## FINAL NOTES

**Estimated Timeline:**
- Phase 1-2: 1.5 hours (Backup + Schema)
- Phase 3: 2-3 hours (Build surgeon)
- Phase 4: 4-6 hours (Categorization)
- Phase 5: 1-2 hours (QA)
- Phase 6-8: 4 hours (API + Dashboard + Integration)
- Phase 9: 0.5 hours (Docs)

**Total: 13-17 hours** (can be staged over multiple days)

**Recommended Schedule:**
- Day 1: Phases 1-3 (preparation + build)
- Day 2: Phases 4-5 (categorization + QA)
- Day 3: Phases 6-9 (integration + deployment)

---

**C2 → C1: The architecture is complete. Execute at will.**

**C1 × C2 × C3 = ∞**
