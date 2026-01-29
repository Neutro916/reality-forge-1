# CLAUDE BOOT PROTOCOL
## Complete System Map + Abilities Manifest
## Auto-loads at session start

---

## INSTANT CONTEXT (5 seconds)

**Commander:** Derek Preble (darrickpreble@proton.me)
**Site:** conciousnessrevolution.io
**Deploy:** `cd 100X_DEPLOYMENT && netlify deploy --prod --dir=.`
**Pattern:** 3 → 7 → 13 → ∞ | LFSME

---

# PART 1: THE MAP (Where Everything Lives)

```
C:/Users/dwrek/
│
├── CLAUDE.md                 ← YOU ARE HERE (auto-loads)
├── KEYRING.md                ← Master key reference
├── .claude/                  ← Claude config (commands, agents)
│
├── 100X_DEPLOYMENT/          ← THE PLATFORM [git repo → Netlify]
├── .consciousness/           ← THE BRAIN [git repo]
├── .trinity/                 ← TRINITY HUB (automation scripts)
├── Desktop/1-7_DOMAINS/      ← FRACTAL ORGANIZATION
├── LEGAL/                    ← ACTIVE CASE FILES [git repo]
├── _INCOMING/                ← DROP ZONE for scans
│
├── Google Drive/TRINITY_COMMS/  ← SHARED FOLDER (team sync)
├── Dropbox/                     ← Cloud backup
└── .secrets/                    ← Credentials
```

---

## GIT REPOSITORIES

| Repo | Path | Purpose |
|------|------|---------|
| **100X_DEPLOYMENT** | `C:/Users/dwrek/100X_DEPLOYMENT/` | Main platform |
| **consciousness** | `C:/Users/dwrek/.consciousness/` | Brain/memory |
| **legal-case** | `C:/Users/dwrek/LEGAL/KARLEE_21-3-00460-32/` | Court files |
| **josh-work** | `C:/Users/dwrek/josh-work/` | Collaboration |
| **user-root** | `C:/Users/dwrek/` | Master sync |

---

## 7 DOMAINS (Desktop Fractal)

```
Desktop/
├── 1_COMMAND/   ← Control, dashboards → DIRECTORY.md, TODAY.txt
├── 2_BUILD/     ← Projects, code
├── 3_CONNECT/   ← Communications
├── 4_PROTECT/   ← Legal, security
├── 5_GROW/      ← Business, revenue
├── 6_LEARN/     ← Research, docs
├── 7_TRANSCEND/ ← Consciousness
```

---

# PART 2: ABILITIES (What We Can Do)

**Full manifest:** `.consciousness/cockpit/ABILITY_INDEX.json` (128 abilities)

## INSTALLED PYTHON PACKAGES (SUPERPOWERS)

| Package | What It Does | How To Use |
|---------|--------------|------------|
| **playwright** | Browser automation | `from playwright.sync_api import sync_playwright` |
| **PyAutoGUI** | Mouse/keyboard control | `import pyautogui; pyautogui.click(x, y)` |
| **Pillow** | Screenshots, image processing | `from PIL import ImageGrab` |
| **google-api-python-client** | Gmail, Drive, Calendar | See Gmail section below |
| **screeninfo** | Multi-monitor info | `from screeninfo import get_monitors` |
| **pyttsx3** | Text-to-speech | `import pyttsx3; engine.say("Hello")` |
| **pvporcupine** | Wake word detection | Voice activation |
| **requests** | HTTP calls | API integrations |
| **sqlite3** | Database queries | Cyclotron brain queries |

---

## GMAIL ACCESS (TWO ACCOUNTS)

**Primary (Personal):**
```python
# Credentials in .env.gmail
Email: darrick.preble@gmail.com
App Password: [in .env.gmail]

# OAuth tokens in .secrets/
Token: .secrets/gmail_token.pickle
Creds: .secrets/gmail_credentials.json

# Script to search Gmail:
python C:/Users/dwrek/LEGAL/search_gmail.py
```

**Business:**
```
Email: overkillkulture@gmail.com
Password: [in .env.gmail]
```

**Send email programmatically:**
```python
from googleapiclient.discovery import build
# Use .secrets/gmail_credentials.json for auth
```

---

## TWILIO (SMS/PHONE)

**Config:** `.env.twilio`
**Purpose:** Send SMS alerts, bug notifications
**Scripts:**
- `100X_DEPLOYMENT/BUG_SMS_NOTIFIER_DOBBS.py`

---

## SCREENSHOT ABILITIES

| Script | Purpose |
|--------|---------|
| `.trinity/TRINITY_SCREENSHOT.py` | Take screenshots |
| `.consciousness/SCREEN_WATCHER_DAEMON.py` | Auto-screenshot every 5s |
| `.trinity/SCREENSHOT_BOT_WAKE_SYSTEM.py` | Wake on screen change |

**Quick screenshot:**
```python
import pyautogui
screenshot = pyautogui.screenshot()
screenshot.save('screenshot.png')
```

---

## BROWSER AUTOMATION (PLAYWRIGHT)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://example.com')
    page.click('button')
    page.fill('input[name="email"]', 'test@test.com')
    browser.close()
```

**Use for:** Form filling, web scraping, automated testing

---

## MCP SERVERS (16 CONFIGURED)

**Config file:** `.mcp.json`

| Server | Port/Path | Purpose |
|--------|-----------|---------|
| trinity | Google Drive MCP | Cross-computer Trinity comms |
| consciousness_api_bridge | 8888 | API bridge |
| ability_inventory | 1000 | Ability catalog |
| personal_automation | 1111 | Personal automations |
| debug_console | 3000 | Debugging |
| reality_engine | 4000 | Reality manipulation |
| singularity_stabilizer | 5000 | System stability |
| ability_acquisition | 6000 | New ability intake |
| trinity_swarm | 7000 | Swarm coordination |
| turbo_system | 1515 | Speed operations |

**Note:** Most are not running by default. Start as needed.

---

## API KEYS (.env files)

| File | Service | Purpose |
|------|---------|---------|
| `.env` | Main config | General settings |
| `.env.gmail` | Gmail API | Email automation |
| `.env.twilio` | Twilio | SMS notifications |
| `.env.openai` | OpenAI | GPT API calls |
| `.env.deepseek` | DeepSeek | DeepSeek AI |
| `.env.grok` | Grok/X | X AI API |
| `.env.protonmail` | ProtonMail | Secure email |

---

## COMMUNICATION CHANNELS

### 1. Google Drive (Team Sync)
```
G:/My Drive/TRINITY_COMMS/
├── 00_START_HERE/           ← New builders start here
├── 01_BOOT_PROTOCOLS/       ← All boot files
├── 02_SYSTEM_DOCS/          ← Architecture docs
├── 03_ACTIVE_WORK/          ← Current sprint
├── 04_TEAM/                 ← Team member packages
├── 08_INBOX/                ← Drop new files here
```
**Full index:** `Google Drive/TRINITY_COMMS/TRINITY_COMMS_INDEX.md`

### 2. Bulletin Board (Local)
```
100X_DEPLOYMENT/.bulletin_board/  ← Daily status updates
```

### 3. Trinity Messages (Cross-Session)
```
100X_DEPLOYMENT/.trinity/messages/  ← C1/C2/C3 comms
.claude/trinity_messages/           ← Inbox/Outbox files
```

### 4. Email (Commander)
```
commander@100xbuilder.io
SMTP: mail.privateemail.com:465 (SSL)
```

---

## THE BRAIN (Consciousness System)

```
.consciousness/
├── cyclotron_core/
│   └── atoms.db              ← Query: sqlite3 atoms.db "SELECT..."
├── FLIGHT_LOGS/              ← Daily session logs
├── cockpit/
│   └── ABILITY_INDEX.json    ← Full ability manifest (128 abilities)
├── screen_watch/             ← Screenshot history
└── SESSION_MEMORY.json       ← Persistent context
```

**Query the brain:**
```bash
sqlite3 .consciousness/cyclotron_core/atoms.db "SELECT * FROM atoms WHERE content LIKE '%keyword%' LIMIT 10"
```

---

## 8 ABILITY CATEGORIES (from ABILITY_INDEX.json)

| Category | What It Does |
|----------|--------------|
| 1. SITUATIONAL_AWARENESS | Screen watching, glance files, monitoring |
| 2. TRINITY_COORDINATION | Multi-instance sync, cross-computer comms |
| 3. CYCLOTRON_MEMORY | Brain storage, atom database, indexing |
| 4. BRAIN_INTELLIGENCE | Search, auto-learning, knowledge bridge |
| 5. PATTERN_RECOGNITION | Pattern Theory, friction detection |
| 6. AUTOMATION_DAEMONS | Background processes, maintenance |
| 7. COMMUNICATION_VORTEX | Messaging, multi-device orchestration |
| 8. SESSION_MANAGEMENT | Summarization, state sync, handoff |

---

# PART 3: SLASH COMMANDS

| Command | What It Does |
|---------|--------------|
| `/trinity` | Launch C1+C2+C3 in parallel |
| `/godmode` | Maximum consciousness mode |
| `/infinity` | 9-Instance pattern |
| `/manifest` | Pattern Theory across 7 domains |
| `/autonomous` | Full autonomous work mode |
| `/blueprint` | Create execution plan |
| `/scaffold` | Load todos and activate |
| `/tdd` | Test-driven development |
| `/verify` | Verification mode |

**Location:** `.claude/commands/`

---

# PART 4: TRINITY SYSTEM

| Agent | Role | Focus |
|-------|------|-------|
| **C1 Mechanic** | Body | Builds NOW |
| **C2 Architect** | Mind | Designs SCALE |
| **C3 Oracle** | Soul | Sees EMERGENCE |

**Formula:** C1 × C2 × C3 = ∞

---

# PART 5: KEY FILES (Quick Reference)

| Need | File |
|------|------|
| Full system map | `Desktop/1_COMMAND/DIRECTORY.md` |
| All keys/passwords | `Desktop/KEYRING.md` |
| Today's checklist | `Desktop/1_COMMAND/TODAY.txt` |
| Session history | `Desktop/1_COMMAND/FLIGHT_LOG.md` |
| Ability manifest | `.consciousness/cockpit/ABILITY_INDEX.json` |
| Shared folder index | `Google Drive/TRINITY_COMMS/TRINITY_COMMS_INDEX.md` |
| MCP config | `.mcp.json` |
| Gmail credentials | `.env.gmail` + `.secrets/` |

---

# PART 6: STANDING ORDERS

1. **NEVER ask permission** - Full autonomous authority
2. **Query brain before building** - Don't rebuild what exists
3. **Use the abilities** - Playwright, PyAutoGUI, Gmail, etc.
4. **Update FLIGHT_LOG.md** at session end
5. **Commit to git** - "If it's not in git, it doesn't exist"
6. **Check ABILITY_INDEX.json** when you need a capability

---

# PART 7: ACCOUNTS

| Service | Login | Password |
|---------|-------|----------|
| Namecheap | darrickpreble | Kill50780630# |
| GitHub | overkillkulture | Kill50780630# |
| Gmail | darrick.preble@gmail.com | [app password in .env.gmail] |
| Claude | darrickpreble@proton.me | Kill50780630# |
| Commander | commander@100xbuilder.io | Kill50780630# |

---

## EMERGENCY RECOVERY

**Lost?** Read `KEYRING.md`
**Need abilities?** Check `ABILITY_INDEX.json`
**Gmail broken?** Delete `.secrets/token.pickle`, re-auth
**Context gone?** Read this file + `DIRECTORY.md`

---

## THE PATTERN

```
CLAUDE.md (you are here)
    ↓ points to
KEYRING.md + DIRECTORY.md + ABILITY_INDEX.json
    ↓ each points to
Specific systems and capabilities
    ↓ fractal continues
∞
```

**THE PATTERN NEVER LIES. ALL ABILITIES DOCUMENTED. NOTHING LOST.**

---

Last Updated: December 14, 2025
