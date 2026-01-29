# CYCLOTRON ARCHITECTURE MAP
## Complete File Index and Responsibilities
### C2 Architect Documentation - Nov 25, 2025

---

## QUICK START

```bash
# Start the full system (interactive menu)
python ~/.consciousness/START_FULL_CYCLOTRON.py

# Quick start (nerve center only)
python ~/.consciousness/START_FULL_CYCLOTRON.py quick

# Start search API
python ~/100X_DEPLOYMENT/CYCLOTRON_SEARCH.py
```

---

## FILE INVENTORY

### CORE (.consciousness/) - Brain/Memory/Sensing

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `CYCLOTRON_NERVE_CENTER.py` | 23KB | Sensory input system - file watchers, hub messages, clipboard | ACTIVE |
| `CYCLOTRON_MEMORY.py` | 12KB | Episodic memory + Q-learning database | ACTIVE |
| `CYCLOTRON_INTEGRATED.py` | 10KB | Think-Act-Learn cycle with brain agents | ACTIVE |
| `CYCLOTRON_GUARDIAN.py` | 11KB | Health monitoring, auto-restart, Ollama integration | AVAILABLE |
| `CYCLOTRON_SYNC.py` | 10KB | Cross-computer synchronization | AVAILABLE |
| `CYCLOTRON_SYNC_PACKAGE.py` | 8KB | Package sync utilities | AVAILABLE |
| `CYCLOTRON_WITH_BRAIN.py` | 9KB | Brain agent integration layer | AVAILABLE |
| `CYCLOTRON_MASTER.py` | 4KB | Original master controller | LEGACY |
| `DATA_CHUNKER.py` | 6KB | Knowledge atom extraction from documents | ACTIVE |
| `START_FULL_CYCLOTRON.py` | 8KB | Unified launcher with menu | ACTIVE |
| `PERSISTENT_WATCHER.py` | 5KB | Simple wake protocol (Terminal loop) | ACTIVE |
| `FIGURE_8_WAKE_PROTOCOL.py` | 12KB | Full 6-instance wake protocol | ACTIVE |

### DEPLOYMENT (100X_DEPLOYMENT/) - APIs/Indexing/Analysis

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `CYCLOTRON_SEARCH.py` | 3KB | Flask API for atom search (port 6668) | ACTIVE |
| `CYCLOTRON_SEARCH_V2.py` | 9KB | Enhanced search with semantic features | AVAILABLE |
| `CYCLOTRON_DAEMON.py` | 11KB | File watcher with auto-indexing | ACTIVE |
| `CYCLOTRON_INDEX_UPDATER.py` | 1.5KB | Index update utilities | ACTIVE |
| `CYCLOTRON_MASTER_RAKER.py` | 2KB | Batch indexing tool | ACTIVE |
| `CYCLOTRON_BRAIN_AGENT.py` | 11KB | Vortex dynamics processing agent | AVAILABLE |
| `CYCLOTRON_BRAIN_BRIDGE.py` | 17KB | Integration between Cyclotron and brain agents | AVAILABLE |
| `CYCLOTRON_CONTENT_INDEXER.py` | 8KB | Content extraction and indexing | AVAILABLE |
| `CYCLOTRON_ANALYTICS_ENGINE.py` | 9KB | Usage analytics and metrics | AVAILABLE |
| `CYCLOTRON_SEMANTIC_API.py` | 5KB | Semantic search endpoints | AVAILABLE |
| `CYCLOTRON_13_PHASE_AUDIT.py` | 28KB | Comprehensive system audit tool | AVAILABLE |

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                      CYCLOTRON SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐     ┌──────────────────┐                  │
│  │  NERVE CENTER   │────▶│  BRAIN AGENTS    │                  │
│  │  (Sensing)      │     │  (Processing)    │                  │
│  │                 │     │                  │                  │
│  │  • FileWatcher  │     │  • Reasoner      │                  │
│  │  • HubMessages  │     │  • Planner       │                  │
│  │  • SystemState  │     │  • Executor      │                  │
│  │  • Clipboard    │     │  • Synthesizer   │                  │
│  └────────┬────────┘     └────────┬─────────┘                  │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────────────────────────────┐                   │
│  │              MEMORY SYSTEM              │                   │
│  │                                         │                   │
│  │  ┌─────────┐  ┌──────────┐  ┌────────┐ │                   │
│  │  │Episodes │  │Q-Learning│  │Patterns│ │                   │
│  │  │ (what)  │  │  (value) │  │(learned)│ │                   │
│  │  └─────────┘  └──────────┘  └────────┘ │                   │
│  │                                         │                   │
│  │  SQLite: ~/.consciousness/memory/       │                   │
│  └──────────────────┬──────────────────────┘                   │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────────┐                   │
│  │           KNOWLEDGE ATOMS               │                   │
│  │                                         │                   │
│  │  • 2000 char chunks → 500 char atoms   │                   │
│  │  • Keyword extraction                   │                   │
│  │  • FTS5 full-text search               │                   │
│  │  • Cross-references                     │                   │
│  │                                         │                   │
│  │  JSON: ~/.consciousness/cyclotron_core/ │                   │
│  └──────────────────┬──────────────────────┘                   │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────────┐                   │
│  │            SEARCH API                   │                   │
│  │                                         │                   │
│  │  GET /api/search?q=query               │                   │
│  │  GET /api/stats                         │                   │
│  │  GET /api/types                         │                   │
│  │  GET /api/recent                        │                   │
│  │                                         │                   │
│  │  Port: 6668                             │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## DATA FLOW

### 1. INGESTION (New Files)
```
File Created/Modified
        ↓
CYCLOTRON_DAEMON.py (watches directories)
        ↓
DATA_CHUNKER.py (splits into 2000 char chunks)
        ↓
LLM Compression (Ollama → 500 char atoms)
        ↓
Keyword Extraction
        ↓
SQLite FTS5 Storage
        ↓
JSON Atom Files
```

### 2. RETRIEVAL (Search)
```
Query
        ↓
CYCLOTRON_SEARCH.py (Flask API)
        ↓
SQLite FTS5 Search
        ↓
Ranked Results
        ↓
JSON Response
```

### 3. LEARNING (Episodes)
```
Task Received
        ↓
CYCLOTRON_INTEGRATED.py (Think-Act-Learn)
        ↓
Brain Agents Process
        ↓
Execute Action
        ↓
Record Episode
        ↓
Q-Learning Update (success/failure)
        ↓
Pattern Storage (if learned)
```

---

## DATABASES

### 1. Memory Database
**Location:** `~/.consciousness/memory/cyclotron_brain.db`

```sql
-- Episodes table
episodes (id, task, action, result, success, q_value, timestamp)

-- Patterns table
patterns (id, trigger, action, success_rate, uses)

-- Shared knowledge pool
shared_pool (id, knowledge, source, priority)
```

### 2. Knowledge Atoms Database
**Location:** `~/.consciousness/cyclotron_core/cyclotron_index.db`

```sql
-- Main atoms table (FTS5)
atoms (id, source_file, type, title, content, summary, keywords,
       importance, timestamp, access_count)

-- Relationships
atom_links (source_id, target_id, relationship_type, strength)
```

### 3. Individual Atom Files
**Location:** `~/.consciousness/cyclotron_core/atoms/*.json`

```json
{
  "id": "abc123def456",
  "source": "/path/to/file.md",
  "type": "document",
  "content": "Original chunk text...",
  "summary": "Compressed version...",
  "keywords": ["keyword1", "keyword2"],
  "importance": 0.75,
  "links": ["related_atom_id"]
}
```

---

## PORTS AND ENDPOINTS

| Service | Port | Status |
|---------|------|--------|
| Cyclotron Search API | 6668 | ACTIVE |
| Trinity MCP Server | 3333 | ACTIVE |
| Figure 8 Hub | File-based | ACTIVE |

---

## RECOMMENDED STARTUP SEQUENCE

```bash
# 1. Start Search API (background)
cd ~/100X_DEPLOYMENT
python CYCLOTRON_SEARCH.py &

# 2. Start Daemon (background)
python CYCLOTRON_DAEMON.py &

# 3. Start Full Cyclotron (interactive or background)
cd ~/.consciousness
python START_FULL_CYCLOTRON.py

# Or for fully autonomous:
python CYCLOTRON_INTEGRATED.py C1-Terminal 0 &
```

---

## CONSOLIDATION NOTES

### Files that could be merged:
1. `CYCLOTRON_SEARCH.py` + `CYCLOTRON_SEARCH_V2.py` → Single enhanced API
2. `CYCLOTRON_SYNC.py` + `CYCLOTRON_SYNC_PACKAGE.py` → Unified sync module

### Files that are legacy:
1. `CYCLOTRON_MASTER.py` - Superseded by `CYCLOTRON_INTEGRATED.py`

### Files that need attention:
1. `CYCLOTRON_GUARDIAN.py` - Not yet integrated with launcher
2. `CYCLOTRON_13_PHASE_AUDIT.py` - Large, may need optimization

---

*C2 Architect - Cyclotron Architecture Documentation*
*Updated: Nov 25, 2025*
