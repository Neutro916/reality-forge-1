# MASTER CREDENTIALS & COMMUNICATION CHANNELS
## UNTYING THE KNOT - ALL ACCESS IN ONE PLACE
## Created: 2025-11-26 05:30 AM

---

# COMPUTERS IN THE NETWORK

| Computer | Username | Location |
|----------|----------|----------|
| CP1 (C1) | dwrek | Commander's main |
| CP2 | darri | Darrick's computer 1 |
| CP3 | Darrick | Darrick's computer 2 |

---

# COMMUNICATION CHANNELS (Priority Order)

## 1. GOOGLE DRIVE (INSTANT - SAME ACCOUNT)
- **How**: All computers signed into same Google account
- **Path on CP1**: `G:\My Drive\TRINITY_COMMS\wake\`
- **Path on CP2**: `G:\My Drive\TRINITY_COMMS\wake\` (or whatever drive letter)
- **Path on CP3**: `G:\My Drive\TRINITY_COMMS\wake\`
- **To communicate**: Create a .txt file, it appears on all computers
- **No passwords needed** - same account

## 2. GITHUB
- **Repo**: https://github.com/overkillkulture/philosopher-ai-backend
- **Username**: overkillkulture
- **Auth method**: gh auth login (generates code for github.com/login/device)
- **To communicate**:
  - `git pull origin main` (get messages)
  - Create file, `git add .`, `git commit -m "message"`, `git push origin main`

## 3. EMAIL
- **Account**: [FILL IN - what Gmail account?]
- **How to access**:
  - Browser: gmail.com
  - Sign in with Google account
- **To communicate**: Email between computers or to yourself

## 4. SYNCTHING (BROKEN - DO NOT USE)
- Wasted 3+ hours
- Path mismatches between computers
- Not reliable

---

# ACCOUNTS & CREDENTIALS

## Google Account
- **Email**: [FILL IN]
- **Password**: [STORED WHERE?]
- **2FA Method**: [Phone? Authenticator app?]
- **Recovery email**: [FILL IN]

## GitHub Account
- **Username**: overkillkulture
- **Email**: [FILL IN]
- **Auth**: Use `gh auth login` - no password needed
- **2FA**: Device code at github.com/login/device

## Anthropic/Claude
- **API Key Location**: Environment variables or .env files
- **Key starts with**: sk-ant-...

## Netlify
- **Account**: [FILL IN]
- **Site**: verdant-tulumba-fa2a5a.netlify.app

## Railway
- **Account**: [FILL IN]
- **Project**: cloud-funnel-production

---

# PASSWORD MANAGER / PASSKEYS

## Current Status
- [ ] Password manager installed on CP1?
- [ ] Password manager installed on CP2?
- [ ] Password manager installed on CP3?
- [ ] All passwords synced?

## Recommended: Bitwarden (Free, cross-platform)
- Download: https://bitwarden.com/download/
- Install on ALL computers
- One master password
- All credentials sync automatically

---

# AUTHENTICATOR APPS

## Current Status
- [ ] What authenticator is used? (Google Authenticator? Authy? Microsoft?)
- [ ] Installed on phone?
- [ ] Backup codes saved?

## Setup for each computer:
1. Phone has authenticator app
2. Scan QR code when setting up 2FA
3. Codes rotate every 30 seconds
4. SAVE BACKUP CODES somewhere safe

---

# HOW TO AUTHENTICATE GITHUB ON ANY COMPUTER

```bash
# Step 1: Run this in terminal
gh auth login

# Step 2: Select options:
# - GitHub.com
# - HTTPS
# - Yes (authenticate with browser)

# Step 3: It shows a code like: AB12-CD34

# Step 4: Go to https://github.com/login/device

# Step 5: Enter the code

# Step 6: Click Authorize

# Done - that computer can now push/pull
```

---

# HOW TO COMMUNICATE (STEP BY STEP)

## Via Google Drive (EASIEST)
```bash
# Create a message
echo "Hello from CP1" > "G:/My Drive/TRINITY_COMMS/wake/CP1_MESSAGE.txt"

# Check for messages
ls "G:/My Drive/TRINITY_COMMS/wake/"

# Read a message
cat "G:/My Drive/TRINITY_COMMS/wake/CP2_MESSAGE.txt"
```

## Via GitHub
```bash
# Get latest messages
cd /path/to/repo
git pull origin main

# Send a message
echo "Hello from CP1" > MESSAGE_FROM_CP1.txt
git add .
git commit -m "Message from CP1"
git push origin main
```

## Via Email
1. Open gmail.com
2. Compose email to self or other account
3. Attach file if needed
4. Send

---

# FOLDER PATHS ON EACH COMPUTER

## CP1 (dwrek)
- Home: `C:\Users\dwrek\`
- Google Drive: `G:\My Drive\`
- Trinity Shared: `C:\Users\dwrek\trinity_shared\`
- 100X Deployment: `C:\Users\dwrek\100X_DEPLOYMENT\`

## CP2 (darri)
- Home: `C:\Users\darri\`
- Google Drive: `[FILL IN DRIVE LETTER]:\My Drive\`
- Trinity Shared: `C:\Users\darri\trinity_shared\`

## CP3 (Darrick)
- Home: `C:\Users\Darrick\`
- Google Drive: `[FILL IN DRIVE LETTER]:\My Drive\`
- Trinity Shared: `C:\Users\Darrick\trinity_shared\`

---

# EMERGENCY ACCESS

If locked out of everything:
1. Use phone to access Gmail
2. Reset passwords from phone
3. Use recovery codes for 2FA
4. Call/text Commander directly

---

# ACTION ITEMS

- [ ] Fill in all [FILL IN] sections above
- [ ] Install Bitwarden on all 3 computers
- [ ] Save all passwords to Bitwarden
- [ ] Verify Google Drive letter on CP2 and CP3
- [ ] Run `gh auth login` on CP2 and CP3
- [ ] Test Google Drive communication
- [ ] Test GitHub communication
- [ ] Delete Syncthing from all computers

---

# NOTES

Add any issues, discoveries, or changes here:

- 2025-11-26: Syncthing wasted 3+ hours due to path mismatches
- 2025-11-26: GitHub works but needs auth on CP2
- 2025-11-26: Google Drive at G:\ on CP1

