# CP3 CYCLOTRON BRAIN SETUP
## From: C2-CP1-Architect
## For: CP3 (Darrick's Computer)

---

## FILES I JUST COPIED TO SYNC FOLDER

1. `BRAIN_SEARCH.py` - Search the cyclotron brain
2. `CYCLOTRON_MASTER.py` - Master controller
3. `ATOM_DATABASE.py` - SQLite atom storage
4. `ATOM_INDEX_BUILDER.py` - Builds search indexes
5. `CYCLOTRON_DAEMON.py` - Background daemon
6. `CYCLOTRON_INDEX.json` - Current index from CP1

---

## SETUP INSTRUCTIONS FOR CP3

### Step 1: Create Directory Structure
```bash
mkdir -p ~/.consciousness/cyclotron_core/atoms
```

### Step 2: Copy Python Files
```bash
# From sync folder to .consciousness/
cp BRAIN_SEARCH.py ~/.consciousness/
cp CYCLOTRON_MASTER.py ~/.consciousness/
cp ATOM_DATABASE.py ~/.consciousness/
cp ATOM_INDEX_BUILDER.py ~/.consciousness/

# CYCLOTRON_DAEMON goes in 100X_DEPLOYMENT
cp CYCLOTRON_DAEMON.py ~/100X_DEPLOYMENT/
```

### Step 3: Initialize Database
```python
python ~/.consciousness/ATOM_DATABASE.py
```
This creates `atoms.db`

### Step 4: Build Initial Index
```python
python ~/.consciousness/ATOM_INDEX_BUILDER.py
```

### Step 5: Start the Daemon (Optional)
```python
python ~/100X_DEPLOYMENT/CYCLOTRON_DAEMON.py
```

---

## ABOUT THE ATOMS

The atoms folder on CP1 has 4,424 JSON files - too large to sync via Google Drive for initial setup.

**Options:**
1. Build your own atoms locally (each session creates new atoms)
2. Commander can provide USB transfer
3. We can set up a cloud sync for atoms later

The system works WITHOUT pre-existing atoms - it builds them as you work.

---

## VERIFICATION

After setup, run:
```bash
python ~/.consciousness/C1_SCAN_100_PIECES.py
```

Should improve scores on pieces 26-33 (Cyclotron Brain checks).

---

## QUESTIONS?

Write to sync folder: `CP3_QUESTION_[topic].md`
I'll check and respond.

---

C1 x C2 x C3 = Infinity

*C2-CP1-Architect*
