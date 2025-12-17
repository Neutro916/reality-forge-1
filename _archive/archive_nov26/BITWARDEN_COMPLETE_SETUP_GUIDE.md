# BITWARDEN COMPLETE SETUP GUIDE
## Make It Actually Useful - Auto-Fill, Auto-Unlock, No Hassle

**Created:** 2025-11-26
**Purpose:** Set up Bitwarden so it WORKS automatically, not another password nightmare

---

## WHAT WE NEED BITWARDEN TO DO:

1. ✅ Auto-fill passwords in browser (no typing)
2. ✅ Auto-popup when it sees a login form
3. ✅ Stay unlocked (not ask for master password constantly)
4. ✅ Sync across all computers instantly
5. ✅ CLI access for automation scripts
6. ✅ API access for our AI systems
7. ✅ Passkey/WebAuthn support (no passwords at all)

---

## PART 1: WHAT TO INSTALL WHERE

### Desktop App (Optional)
- NOT required if using browser extension
- Good for: Managing vault, organizing folders
- Install: `winget install Bitwarden.Bitwarden`

### Browser Extension (REQUIRED - This is the main thing)
- Chrome: https://chrome.google.com/webstore/detail/bitwarden
- Edge: https://microsoftedge.microsoft.com/addons/detail/bitwarden
- Firefox: https://addons.mozilla.org/firefox/addon/bitwarden-password-manager/

### CLI (For automation)
- Already installed on CP1: `bw` command
- Install: `winget install Bitwarden.CLI`
- Used by scripts to get/set passwords programmatically

---

## PART 2: BROWSER EXTENSION SETTINGS (THE IMPORTANT PART)

After installing browser extension, click the Bitwarden icon > Settings (gear):

### VAULT TIMEOUT SETTINGS:
```
Vault Timeout: "Never" (or "On Browser Restart" for more security)
Vault Timeout Action: "Lock" (not Log out)
```
This means: Don't ask for master password constantly

### AUTO-FILL SETTINGS:
```
✅ Auto-fill on page load (fills password automatically)
✅ Show auto-fill menu on form fields
✅ Auto-fill login when clicking on card (shows popup near login fields)
Default URI match detection: "Base domain"
```

### NOTIFICATION SETTINGS:
```
✅ Ask to add login (popup when you enter a new password)
✅ Ask to update existing login (when password changes)
```

### UNLOCK WITH:
```
✅ Unlock with PIN (set a 4-6 digit PIN instead of master password)
✅ Unlock with biometrics (fingerprint/face if available)
```

---

## PART 3: STAY LOGGED IN / AUTO-UNLOCK OPTIONS

### Option A: PIN Unlock (Recommended)
1. Settings > Security > Unlock with PIN
2. Set a short PIN (4-6 digits)
3. Now you type PIN instead of master password

### Option B: Biometrics (If available)
1. Settings > Security > Unlock with biometrics
2. Uses Windows Hello (fingerprint, face, or Windows PIN)
3. Fastest option

### Option C: Never Lock (Least secure but most convenient)
1. Settings > Security > Vault Timeout > Never
2. Stays unlocked forever until you manually lock
3. Good for home computers only

---

## PART 4: CLI SETUP FOR AUTOMATION

The CLI lets scripts access passwords without human interaction.

### Login to CLI:
```bash
bw login
# Enter email and master password once
# It saves a session token
```

### Keep Session Active:
```bash
# Get session key (valid for 2 weeks)
export BW_SESSION=$(bw unlock --raw)

# Now you can use bw commands without password:
bw list items
bw get item github
bw get password "GitHub"
```

### Auto-Unlock Script (save as unlock_bitwarden.sh):
```bash
#!/bin/bash
# Unlock Bitwarden and export session
export BW_SESSION=$(bw unlock --raw --passwordfile ~/.bw_master)
# Now scripts can use: bw get password "ServiceName"
```

### Store Master Password for Automation (CAREFUL):
```bash
# Create secure file with master password
echo "YourMasterPasswordHere" > ~/.bw_master
chmod 600 ~/.bw_master
# Now scripts can unlock without human
```

---

## PART 5: API ACCESS FOR AI SYSTEMS

Bitwarden has a REST API but it's for self-hosted only.
For cloud Bitwarden, use CLI in scripts.

### Get Password in Python:
```python
import subprocess
import os

def get_password(item_name):
    # Assumes BW_SESSION is set
    result = subprocess.run(
        ['bw', 'get', 'password', item_name],
        capture_output=True, text=True
    )
    return result.stdout.strip()

# Usage:
github_token = get_password("GitHub Token")
```

### Get Password in Bash:
```bash
# Get GitHub token
GITHUB_TOKEN=$(bw get password "GitHub Token")

# Get API key
API_KEY=$(bw get password "Anthropic API")
```

---

## PART 6: PASSKEYS / WEBAUTHN (PASSWORDLESS)

Bitwarden supports passkeys - no password needed at all!

### How Passkeys Work:
1. Website asks "Create passkey?"
2. Bitwarden stores the passkey
3. Next login: Website asks for passkey
4. Bitwarden provides it automatically
5. NO PASSWORD TYPED EVER

### Enable Passkeys:
1. Settings > Security > Enable passkey storage
2. When a site offers passkey, click "Save to Bitwarden"
3. Future logins are automatic

### Sites That Support Passkeys:
- Google
- Microsoft
- GitHub
- PayPal
- Many more...

---

## PART 7: RECOMMENDED SETUP FOR TRINITY

### ALL COMPUTERS:
1. Install browser extension
2. Login with SAME Bitwarden account
3. Set Vault Timeout: "On Browser Restart"
4. Enable PIN unlock (same PIN on all computers)
5. Enable "Auto-fill on page load"
6. Enable "Ask to add login"

### FOR AUTOMATION (CP1):
1. CLI already installed
2. Create session unlock script
3. Store BW_SESSION in environment
4. Scripts can now get passwords automatically

### MASTER PASSWORD RULES:
- Use a LONG passphrase: "correct-horse-battery-staple-2024"
- Write it down ONCE, store physically
- Use PIN for daily unlocking
- Master password only for new device setup

---

## PART 8: QUICK START COMMANDS

### Install Everything:
```powershell
# Desktop app (optional)
winget install Bitwarden.Bitwarden

# CLI (for automation)
winget install Bitwarden.CLI

# Browser extension - install from browser store
```

### First Time Setup:
```bash
# Create account (if new)
bw login
# Enter email and master password

# Unlock vault
bw unlock
# Enter master password
# COPY the session key it shows

# Set session for this terminal
export BW_SESSION="paste_session_key_here"

# Verify it works
bw list items
```

### Add a Password:
```bash
# Via CLI:
bw create item '{"type":1,"name":"GitHub","login":{"username":"overkillkulture","password":"your_token_here"}}'

# Or just use browser extension - it auto-asks to save
```

---

## SUMMARY: MAKE IT NOT ANNOYING

| Setting | Value | Why |
|---------|-------|-----|
| Vault Timeout | On Browser Restart | Don't ask constantly |
| Unlock Method | PIN | Faster than master password |
| Auto-fill | ON | Fills passwords automatically |
| Ask to add | ON | Prompts to save new passwords |
| Ask to update | ON | Catches password changes |

**The goal: Install once, set PIN, never think about passwords again.**

---

## COMMANDER ACTION ITEMS:

1. [ ] Create Bitwarden account (or login if exists)
2. [ ] Install browser extension on CP1
3. [ ] Set PIN unlock
4. [ ] Set vault timeout to "On Browser Restart"
5. [ ] Enable auto-fill
6. [ ] Add first password (test it works)
7. [ ] Have CP2/CP3 login to SAME account
8. [ ] Verify sync works

---

*This file syncs to all computers via Google Drive*
