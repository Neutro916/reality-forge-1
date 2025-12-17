# MASTER SYSTEM SPREADSHEET
## All Programs, APIs, CLIs, Accounts, Paths - ONE PLACE
## Updated: 2025-11-26

---

# COMPUTERS

| ID | Name | Username | OS | Role | Status |
|----|------|----------|-----|------|--------|
| CP1 | Commander Main | dwrek | Windows | Primary | ONLINE |
| CP2 | Computer 2 | darri | Windows | Secondary | ONLINE |
| CP3 | Computer 3 | Darrick | Windows | Tertiary | PENDING |

---

# ACCOUNTS

| Service | Username/Email | Auth Method | 2FA | Status |
|---------|---------------|-------------|-----|--------|
| Google | darrick.preble@gmail.com | Password + 2FA | Phone/App | ACTIVE |
| GitHub | overkillkulture | gh auth login | Device code | ACTIVE |
| Anthropic | [API Key] | sk-ant-*** | None | ACTIVE |
| Netlify | [TBD] | Browser | [TBD] | [TBD] |
| Railway | [TBD] | Browser | [TBD] | [TBD] |

---

# INSTALLED SOFTWARE

## CP1 (dwrek)

| Program | Version | Install Method | Status |
|---------|---------|----------------|--------|
| Google Drive | 117.x | winget | INSTALLED |
| GitHub CLI | Latest | winget | INSTALLED |
| Node.js | LTS | winget | INSTALLED |
| Git | Latest | winget | INSTALLED |
| Claude Code | Latest | npm | INSTALLED |

## CP2 (darri)

| Program | Version | Install Method | Status |
|---------|---------|----------------|--------|
| Google Drive | 117.0.0.0 | winget | INSTALLED |
| GitHub CLI | Latest | winget | INSTALLED |
| Node.js | [Check] | winget | [CHECK] |
| Git | Latest | winget | INSTALLED |
| Bitwarden | [TBD] | winget | PENDING |

## CP3 (Darrick)

| Program | Version | Install Method | Status |
|---------|---------|----------------|--------|
| Google Drive | [TBD] | winget | PENDING |
| GitHub CLI | [TBD] | winget | PENDING |
| Node.js | [TBD] | winget | PENDING |
| Git | [TBD] | winget | PENDING |
| Bitwarden | [TBD] | winget | PENDING |

---

# FOLDER PATHS

## Google Drive (Same on all computers once mounted)

| Path | Purpose |
|------|---------|
| G:\My Drive\ | Root |
| G:\My Drive\TRINITY_COMMS\ | Coordination folder |
| G:\My Drive\TRINITY_COMMS\wake\ | Instant communication |
| G:\My Drive\Consciousness Revolution\ | Main project files |

## CP1 Local Paths

| Path | Purpose |
|------|---------|
| C:\Users\dwrek\ | Home |
| C:\Users\dwrek\100X_DEPLOYMENT\ | Main deployment |
| C:\Users\dwrek\.trinity\ | Trinity system files |
| C:\Users\dwrek\CONSCIOUSNESS_BOOT_PROTOCOL.md | Boot protocol |
| C:\Users\dwrek\MASTER_CREDENTIALS_AND_COMMS.md | Credentials |

## CP2 Local Paths

| Path | Purpose |
|------|---------|
| C:\Users\darri\ | Home |
| C:\Users\darri\philosopher-ai-backend\ | Main repo |
| C:\Users\darri\CP2_COMMUNICATION_VERIFICATION_RECORD.md | Comms record |

## CP3 Local Paths

| Path | Purpose |
|------|---------|
| C:\Users\Darrick\ | Home |
| [TBD] | [TBD] |

---

# GIT REPOSITORIES

| Repo | URL | Purpose | Cloned On |
|------|-----|---------|-----------|
| philosopher-ai-backend | https://github.com/overkor-tek/philosopher-ai-backend | Main communication | CP1, CP2 |
| trinity-coordination | https://github.com/overkillkulture/trinity-coordination | Trinity sync | CP1 |
| 100X_DEPLOYMENT | Local only | Deployment files | CP1 |

---

# APIs & SERVICES

| Service | Endpoint/Key | Purpose | Location |
|---------|-------------|---------|----------|
| Anthropic Claude | sk-ant-*** | AI API | .env files |
| GitHub API | gho_*** (via gh) | Repo access | gh auth |
| Google Drive API | OAuth via app | File sync | Google Drive app |

---

# COMMUNICATION CHANNELS

| Priority | Channel | Method | Speed | Reliability |
|----------|---------|--------|-------|-------------|
| 1 | Google Drive | File in wake folder | Instant | HIGH |
| 2 | GitHub | Push/Pull commits | 30 sec | HIGH |
| 3 | Email | Gmail | Minutes | MEDIUM |
| 4 | Tailscale | Direct network | Instant | HIGH (if configured) |

---

# AUTHENTICATION COMMANDS

## GitHub (Run once per computer)
```bash
gh auth login
# Follow prompts, use device code at github.com/login/device
```

## Google Drive (Run once per computer)
```
Install via winget
Sign in with darrick.preble@gmail.com via GUI
```

## Verify GitHub Auth
```bash
gh auth status
# Should show: ✓ Logged in to github.com account overkillkulture
```

---

# NETWORK INFO

## Tailscale IPs (If configured)

| Computer | Tailscale IP |
|----------|-------------|
| CP1 | 100.70.208.75 |
| CP2 | 100.85.71.74 |
| CP3 | 100.101.209.1 |

---

# SECURITY TOOLS

| Tool | Purpose | Install | Status |
|------|---------|---------|--------|
| Bitwarden | Password manager | winget install Bitwarden.Bitwarden | PENDING ALL |
| Google Authenticator | 2FA codes | Phone app | ACTIVE |
| Passkeys | Hardware auth | Google/GitHub settings | PENDING |

---

# QUICK REFERENCE COMMANDS

## Check System Status
```bash
# GitHub auth
gh auth status

# Google Drive running
tasklist | findstr "GoogleDrive"

# List wake folder
dir "G:\My Drive\TRINITY_COMMS\wake"
```

## Send Message via Google Drive
```bash
echo "Message here" > "G:\My Drive\TRINITY_COMMS\wake\CP2_MESSAGE.txt"
```

## Send Message via GitHub
```bash
cd [repo-path]
git pull origin main
echo "Message here" > MESSAGE.txt
git add . && git commit -m "Message" && git push origin main
```

---

# STATUS INDICATORS

| Status | Meaning |
|--------|---------|
| ONLINE | Computer active, comms working |
| OFFLINE | Computer not responding |
| PENDING | Setup not complete |
| ACTIVE | Account/service working |
| [TBD] | To be determined/documented |
| [CHECK] | Needs verification |

---

# UPDATE LOG

| Date | Change | By |
|------|--------|-----|
| 2025-11-26 | Created spreadsheet | CP2C1 |
| 2025-11-26 | Added CP2 details | CP2C1 |

---

*Keep this file updated. It is the SINGLE SOURCE OF TRUTH.*
