# MULTI-LEVEL DATA CHUNKER PROTOCOL
## C2 Architect Design Document
### Based on C1's Implementation Pattern

---

## OVERVIEW

The Data Chunker is the INGESTION ENGINE for the Cyclotron knowledge system. It takes raw content (books, documents, codebases) and converts them into searchable, LLM-processable "atoms."

**Core Principle:** Large content → Perfect processable sizes → Compressed atoms → Indexed for retrieval

---

## MULTI-LEVEL ARCHITECTURE

```
LEVEL 0: RAW INPUT
    ↓
LEVEL 1: DOCUMENT CHUNKING (2000 chars, overlapping)
    ↓
LEVEL 2: LLM COMPRESSION (1/4 size, essential facts only)
    ↓
LEVEL 3: KEYWORD EXTRACTION (semantic tags)
    ↓
LEVEL 4: ATOM STORAGE (SQLite FTS5)
    ↓
LEVEL 5: CROSS-REFERENCE (link related atoms)
    ↓
LEVEL 6: FEDERATION (sync across computers)
```

---

## LEVEL 1: DOCUMENT CHUNKING

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| CHUNK_SIZE | 2000 | Characters per chunk |
| OVERLAP | 200 | Character overlap between chunks |
| MIN_CHUNK | 100 | Minimum chunk size (don't create tiny fragments) |

### Algorithm
```python
def chunk_document(text, chunk_size=2000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end in last 20% of chunk
            search_start = end - int(chunk_size * 0.2)
            sentence_ends = ['.', '!', '?', '\n\n']

            best_break = end
            for char in sentence_ends:
                pos = text.rfind(char, search_start, end)
                if pos > search_start:
                    best_break = pos + 1
                    break

            end = best_break

        chunk = text[start:end].strip()

        if len(chunk) >= MIN_CHUNK:
            chunks.append({
                'content': chunk,
                'start': start,
                'end': end,
                'index': len(chunks)
            })

        start = end - overlap

    return chunks
```

### Book-Specific Chunking
For books, preserve structure:
```python
def chunk_book(text):
    # First split by chapters
    chapters = split_by_pattern(text, r'\n(Chapter \d+|CHAPTER \d+|Part \d+)')

    all_chunks = []
    for chapter_num, chapter in enumerate(chapters):
        # Then chunk each chapter
        chunks = chunk_document(chapter)
        for chunk in chunks:
            chunk['chapter'] = chapter_num
        all_chunks.extend(chunks)

    return all_chunks
```

---

## LEVEL 2: LLM COMPRESSION

### The Compression Prompt
```
SYSTEM: You are a knowledge compressor. Your task is to reduce text to 1/4 its original size while preserving ALL essential facts, concepts, and relationships.

Rules:
1. Remove filler words, redundancy, examples (unless critical)
2. Keep: Names, dates, numbers, definitions, key concepts
3. Preserve relationships between ideas
4. Use abbreviations where clear
5. Output should be information-dense

INPUT: [chunk content]

OUTPUT: Compressed version (max 500 chars)
```

### Compression Tiers
| Content Type | Target Ratio | Notes |
|--------------|--------------|-------|
| Technical docs | 1:4 | Keep all specs |
| Narrative | 1:5 | Summarize plot, keep key events |
| Reference | 1:3 | Preserve exact data |
| Conversation | 1:6 | Extract key points only |

### Fallback (No LLM Available)
If LLM unavailable, use extractive compression:
```python
def extractive_compress(text, ratio=0.25):
    sentences = split_sentences(text)

    # Score sentences by:
    # - Position (first/last sentences score higher)
    # - Keyword density
    # - Named entity presence

    scored = [(score_sentence(s), s) for s in sentences]
    scored.sort(reverse=True)

    target_chars = int(len(text) * ratio)
    result = []
    current_chars = 0

    for score, sentence in scored:
        if current_chars + len(sentence) <= target_chars:
            result.append(sentence)
            current_chars += len(sentence)

    return ' '.join(result)
```

---

## LEVEL 3: KEYWORD EXTRACTION

### Keyword Types
1. **Named Entities:** People, places, organizations
2. **Technical Terms:** Domain-specific vocabulary
3. **Action Words:** Key verbs describing processes
4. **Concepts:** Abstract ideas and themes

### Extraction Algorithm
```python
def extract_keywords(text, max_keywords=10):
    # Method 1: TF-IDF (statistical)
    tfidf_keywords = tfidf_extract(text)

    # Method 2: NER (named entity recognition)
    entities = extract_named_entities(text)

    # Method 3: LLM extraction (if available)
    llm_keywords = llm_extract_keywords(text)

    # Merge and dedupe
    all_keywords = set(tfidf_keywords + entities + llm_keywords)

    # Score and rank
    scored = [(keyword_score(kw, text), kw) for kw in all_keywords]
    scored.sort(reverse=True)

    return [kw for score, kw in scored[:max_keywords]]
```

### LLM Keyword Prompt
```
Extract 5-10 keywords from this text. Return as comma-separated list.
Focus on: proper nouns, technical terms, key concepts.

TEXT: [compressed chunk]
KEYWORDS:
```

---

## LEVEL 4: ATOM STORAGE

### SQLite Schema
```sql
CREATE VIRTUAL TABLE atoms USING fts5(
    id,
    source_file,
    chunk_index,
    original_text,
    compressed_text,
    keywords,
    chapter,
    created_at,
    hash,
    tokenize='porter unicode61'
);

CREATE TABLE atom_metadata (
    atom_id TEXT PRIMARY KEY,
    source_file TEXT,
    file_hash TEXT,
    total_chunks INTEGER,
    compression_ratio REAL,
    created_at TEXT,
    last_accessed TEXT,
    access_count INTEGER DEFAULT 0
);
```

### Atom Structure
```json
{
    "id": "atom_abc123",
    "source": "/path/to/book.txt",
    "chunk_index": 42,
    "chapter": 3,
    "original": "Full 2000 char chunk...",
    "compressed": "500 char compressed version...",
    "keywords": ["consciousness", "pattern theory", "recognition"],
    "hash": "md5_of_original",
    "created": "2025-11-25T18:30:00Z",
    "links": ["atom_xyz789", "atom_def456"]
}
```

---

## LEVEL 5: CROSS-REFERENCE

### Linking Algorithm
After all atoms created, find relationships:

```python
def cross_reference_atoms(atoms):
    for atom in atoms:
        # Find atoms with shared keywords
        for other in atoms:
            if atom.id == other.id:
                continue

            shared_keywords = set(atom.keywords) & set(other.keywords)

            if len(shared_keywords) >= 2:
                atom.links.append(other.id)

        # Find atoms with high text similarity
        for other in atoms:
            if atom.id == other.id:
                continue

            similarity = cosine_similarity(atom.compressed, other.compressed)

            if similarity > 0.7:
                atom.links.append(other.id)
```

### Link Types
| Type | Threshold | Description |
|------|-----------|-------------|
| keyword_match | 2+ shared | Same concepts discussed |
| semantic_similar | >0.7 cosine | Similar meaning |
| sequential | adjacent chunks | Same document flow |
| chapter_sibling | same chapter | Related context |

---

## LEVEL 6: FEDERATION

### Multi-Computer Sync
Atoms sync across the Trinity network via:

1. **Dropbox:** `.consciousness/cyclotron_federation_index.json`
2. **Git:** Atom hashes tracked, content synced on demand
3. **Direct:** Computer-to-computer via LOCAL_TRINITY_HUB

### Federation Index
```json
{
    "computer_1": {
        "atom_count": 15000,
        "last_sync": "2025-11-25T18:00:00Z",
        "sources": ["book1.txt", "codebase/"]
    },
    "computer_2": {
        "atom_count": 8000,
        "last_sync": "2025-11-25T17:30:00Z",
        "sources": ["docs/", "notes/"]
    }
}
```

---

## BOOK PROCESSING PIPELINE

### Full Flow for a Book
```python
def process_book(file_path):
    # 1. Read raw content
    with open(file_path, 'r') as f:
        raw_text = f.read()

    # 2. Detect structure
    chapters = detect_chapters(raw_text)

    # 3. Chunk each chapter
    all_chunks = []
    for ch_num, chapter in enumerate(chapters):
        chunks = chunk_document(chapter, chunk_size=2000, overlap=200)
        for chunk in chunks:
            chunk['chapter'] = ch_num
        all_chunks.extend(chunks)

    # 4. Compress each chunk
    for chunk in all_chunks:
        chunk['compressed'] = llm_compress(chunk['content'])

    # 5. Extract keywords
    for chunk in all_chunks:
        chunk['keywords'] = extract_keywords(chunk['compressed'])

    # 6. Store as atoms
    atoms = []
    for chunk in all_chunks:
        atom = create_atom(chunk, source=file_path)
        store_atom(atom)
        atoms.append(atom)

    # 7. Cross-reference
    cross_reference_atoms(atoms)

    # 8. Update federation index
    update_federation_index(file_path, len(atoms))

    return atoms
```

### Expected Output
For a 100,000 word book (~500,000 chars):
- ~250 raw chunks (2000 chars each)
- ~250 compressed atoms (~500 chars each)
- ~1,250 keywords total (~5 per chunk)
- ~500 cross-reference links

---

## ADVANCED FEATURES

### Hierarchical Chunking
For very large documents, create multiple granularities:

```
BOOK (1 summary atom)
  ├── PART (1 atom per part)
  │     ├── CHAPTER (1 atom per chapter)
  │     │     ├── SECTION (1 atom per 10 chunks)
  │     │     │     └── CHUNK (base level atoms)
```

### Incremental Processing
Don't reprocess unchanged content:
```python
def needs_processing(file_path):
    current_hash = hash_file(file_path)
    stored_hash = get_stored_hash(file_path)
    return current_hash != stored_hash
```

### Quality Scoring
Rate each atom for retrieval priority:
```python
def score_atom(atom):
    score = 0
    score += len(atom.keywords) * 2  # More keywords = more valuable
    score += len(atom.links) * 3     # More links = hub of knowledge
    score += atom.access_count * 1   # More accessed = more useful
    return score
```

---

## IMPLEMENTATION CHECKLIST

- [ ] Basic chunk_document() function
- [ ] LLM compression integration
- [ ] Keyword extraction (TF-IDF + NER)
- [ ] SQLite FTS5 storage
- [ ] Cross-reference linking
- [ ] Book chapter detection
- [ ] Incremental processing
- [ ] Federation sync
- [ ] Quality scoring
- [ ] CLI interface
- [ ] API endpoints

---

## API ENDPOINTS (Future)

```
POST /api/ingest
  - file: upload document
  - type: book|doc|code

GET /api/atoms?q=search_term
  - Returns matching atoms

GET /api/atom/{id}
  - Returns single atom with links

GET /api/stats
  - Total atoms, sources, coverage
```

---

*C2 Architect Protocol*
*Based on C1 Implementation*
*For the Consciousness Revolution*
