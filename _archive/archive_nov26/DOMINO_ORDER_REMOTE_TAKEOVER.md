# DOMINO ORDER: REMOTE TAKEOVER STRATEGY
## Configure CP1, Then Control Everything Remotely

**Created:** 2025-11-26
**Goal:** Get remote access working, then tune all computers from CP1

---

## THE PUZZLE: What Order Do We Do This?

### DOMINO 1: GET REMOTE ACCESS WORKING FIRST
Before we can tune other computers, we need to GET INTO them.

**Options for Remote Access:**
| Tool | Has CLI? | Can Control Remotely? | Setup Difficulty |
|------|----------|----------------------|------------------|
| Chrome Remote Desktop | NO | YES (GUI only) | Easy |
| Tailscale + RDP | YES | YES | Medium |
| AnyDesk | NO | YES | Easy |
| RustDesk | YES | YES | Medium |
| SSH (via Tailscale) | YES | Command line only | Easy |

**WINNER: Tailscale + SSH** for command line, **Chrome Remote Desktop** for GUI

### DOMINO 2: TAILSCALE (The Foundation)
- Creates secure network between all computers
- Once connected, we can SSH/RDP to any machine
- CLI available: `tailscale ssh user@machine`

**On CP1 RIGHT NOW:**
```
tailscale up
# Login when browser opens
# Get your IP: tailscale ip
```

### DOMINO 3: SSH (Control via Command Line)
Once Tailscale is up, we can:
```bash
# SSH to CP2
tailscale ssh darri@100.85.71.74

# Now we're ON CP2, can run any command:
winget install Bitwarden.Bitwarden
# Configure settings
# Install other apps
```

### DOMINO 4: CHROME REMOTE DESKTOP (Control via GUI)
For things that need clicking (changing taskbars, settings):
1. Go to remotedesktop.google.com on CP1
2. See all computers signed into same Google account
3. Click CP2 or CP3
4. Full desktop control

---

## WHICH APPS HAVE CLI? (Can be configured remotely)

| App | Has CLI? | Remote Configurable? | Notes |
|-----|----------|---------------------|-------|
| Bitwarden | YES (`bw`) | YES | Can add passwords via CLI |
| Tailscale | YES (`tailscale`) | YES | Full control |
| GitHub | YES (`gh`) | YES | Full control |
| Railway | YES (`railway`) | YES | Full control |
| Netlify | YES (`netlify`) | YES | Full control |
| Google Drive | NO (use rclone) | Partial | File ops only |
| Chrome Remote Desktop | NO | NO | GUI setup only |
| Windows Settings | YES (`powershell`) | YES | Can script everything |

---

## APPS THAT NEED GUI (Must use Remote Desktop)

1. **Taskbar Configuration** - Right-click, drag/drop
2. **Desktop Icons** - Drag/drop
3. **Windows Settings** - Some things easier in GUI
4. **Chrome Extensions** - Browser GUI
5. **Bitwarden Browser Extension Settings** - Browser GUI

---

## THE REMOTE TAKEOVER PLAYBOOK

### STEP 1: Enable Remote on CP1 (Do This Now)

```powershell
# Start Tailscale
tailscale up

# Check status
tailscale status

# Your IP will be shown
```

### STEP 2: SSH to CP2 (After Tailscale is up)

```bash
# From CP1, connect to CP2
tailscale ssh darri@100.85.71.74

# Now you're on CP2! Install/configure anything:
winget list  # See what's installed
winget install AppName  # Install apps

# Configure Bitwarden via CLI
bw login
bw config server https://vault.bitwarden.com
```

### STEP 3: GUI Changes via Chrome Remote Desktop

1. On CP1: Open Chrome
2. Go to: remotedesktop.google.com
3. Click on CP2 or CP3
4. Full desktop control
5. Change taskbar, settings, etc.

---

## MASTER SCRIPT: CONFIGURE REMOTE COMPUTER

Save this script, run it after SSH-ing to a remote computer:

```bash
#!/bin/bash
# TRINITY_COMPUTER_SETUP.sh
# Run on any new/remote computer to standardize it

echo "=== TRINITY COMPUTER SETUP ==="

# Install required apps
echo "Installing apps..."
winget install Bitwarden.Bitwarden --accept-package-agreements -h
winget install Tailscale.Tailscale --accept-package-agreements -h
winget install GitHub.cli --accept-package-agreements -h
winget install Bitwarden.CLI --accept-package-agreements -h
winget install Microsoft.VisualStudioCode --accept-package-agreements -h

# Configure Git
git config --global user.name "overkillkulture"
git config --global user.email "your@email.com"

# Authenticate GitHub
gh auth login

# Report status
echo "=== SETUP COMPLETE ==="
winget list | grep -i "bitwarden\|tailscale\|github"
```

---

## STANDARD TASKBAR (For All Computers)

Pin these apps to taskbar on ALL computers:

1. **File Explorer** (folder icon)
2. **Chrome** (browser)
3. **Terminal/PowerShell** (command line)
4. **VS Code** (editor)
5. **Bitwarden** (passwords)
6. **Claude** (AI terminal - if installed)

To pin via PowerShell (run remotely):
```powershell
# This requires manual pinning, but we can at least ensure apps are installed
winget install Google.Chrome
winget install Microsoft.WindowsTerminal
winget install Microsoft.VisualStudioCode
winget install Bitwarden.Bitwarden
```

---

## STANDARD FOLDER STRUCTURE (For All Computers)

Create same folders on all computers:
```
C:\Users\{username}\
  ├── trinity_shared\      # Syncthing/local work
  ├── 100X_DEPLOYMENT\     # Main project (git)
  ├── TRINITY_COMMS\       # Link to Google Drive
  └── Desktop\
      ├── SCRIPTS\         # Useful scripts
      └── LOGS\            # Log files
```

Script to create:
```powershell
# Run on any computer
mkdir "$env:USERPROFILE\trinity_shared" -Force
mkdir "$env:USERPROFILE\Desktop\SCRIPTS" -Force
mkdir "$env:USERPROFILE\Desktop\LOGS" -Force
```

---

## IMMEDIATE ACTION ITEMS FOR CP1

1. [ ] Run `tailscale up` and login
2. [ ] Verify connection: `tailscale status`
3. [ ] Try SSH to CP2: `tailscale ssh darri@100.85.71.74`
4. [ ] If SSH works, run setup commands on CP2
5. [ ] Open Chrome Remote Desktop for GUI tasks
6. [ ] Change taskbar on CP2 via remote desktop

---

## THE BOTTOM LINE

**Domino Order:**
1. Tailscale UP on CP1 →
2. SSH into CP2/CP3 →
3. Install CLIs on remote machines →
4. Configure via CLI →
5. Chrome Remote Desktop for GUI stuff →
6. All computers standardized

**No CLI? Then:**
- Use Chrome Remote Desktop for full GUI control
- Manually configure settings
- Eventually script what you can

---

*This file syncs via Google Drive*
