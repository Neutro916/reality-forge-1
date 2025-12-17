# FOUNDATIONAL APPS MASTER GUIDE
## Know EVERYTHING About Our Core Tools

**Created:** 2025-11-26
**Purpose:** Complete reference for all foundational apps - every feature, CLI command, hidden setting

---

## THE BIG 6 FOUNDATIONAL APPS

| App | Purpose | Has CLI? | Has API? | Priority |
|-----|---------|----------|----------|----------|
| Bitwarden | Password/Secrets | YES (bw) | YES | CRITICAL |
| Tailscale | Secure Network | YES | YES | CRITICAL |
| GitHub | Code/Comms | YES (gh) | YES | CRITICAL |
| Google Drive | File Sync | NO (rclone) | YES | CRITICAL |
| Railway | Hosting | YES | YES | HIGH |
| Twilio | SMS/Voice | NO | YES | HIGH |

---

## 1. BITWARDEN - PASSWORD FORTRESS

### What It Does
- Stores all passwords, API keys, secrets
- Auto-fills login forms in browser
- Generates secure passwords
- Stores TOTP 2FA codes (replaces Google Authenticator!)
- Syncs across all devices instantly

### CLI Commands (bw)
```bash
# LOGIN AND SESSION
bw login                          # First time login
bw unlock                         # Unlock vault, get session
export BW_SESSION="session_key"   # Set session for automation

# GET SECRETS
bw get password "GitHub"          # Get password by name
bw get username "GitHub"          # Get username
bw get totp "GitHub"              # Get 2FA code (if stored)
bw get item "GitHub" | jq         # Get full item as JSON
bw get uri "GitHub"               # Get URL

# SEARCH
bw list items --search "github"   # Search items
bw list items --folderid null     # Items without folder
bw list folders                   # List all folders

# CREATE/EDIT
bw create item '{json}'           # Create new item
bw edit item {id} '{json}'        # Edit item
bw delete item {id}               # Delete item

# SYNC
bw sync                           # Force sync with cloud

# GENERATE
bw generate -ulns --length 32     # Generate password (upper, lower, number, special)
```

### Browser Extension Settings (MUST CONFIGURE)
```
Vault Timeout: "On Browser Restart" or "4 hours"
Vault Timeout Action: "Lock" (not Log out)
Unlock with PIN: ENABLED (set 4-6 digit PIN)
Auto-fill on page load: ENABLED
Show auto-fill menu: ENABLED
Ask to add login: ENABLED
Ask to update: ENABLED
```

### Hidden Features
- **TOTP Built-in**: Can store 2FA codes - no need for Google Authenticator
- **Password Generator**: Built into every password field
- **Secure Notes**: Store API keys, SSH keys, any text
- **Custom Fields**: Add extra fields to any item
- **Emergency Access**: Let trusted person access if you're incapacitated
- **Send**: Share encrypted text/files with expiration

### Python Integration
```python
import subprocess
import json

def get_password(name):
    result = subprocess.run(['bw', 'get', 'password', name],
                          capture_output=True, text=True)
    return result.stdout.strip()

def get_totp(name):
    result = subprocess.run(['bw', 'get', 'totp', name],
                          capture_output=True, text=True)
    return result.stdout.strip()

# Usage
github_token = get_password("GitHub Token")
github_2fa = get_totp("GitHub")
```

---

## 2. TAILSCALE - SECURE MESH NETWORK

### What It Does
- Creates encrypted VPN between all your devices
- No port forwarding needed
- SSH/RDP to any device by name
- Access home network from anywhere

### CLI Commands
```bash
# CONNECT
tailscale up                      # Start and connect
tailscale down                    # Disconnect
tailscale logout                  # Full logout

# STATUS
tailscale status                  # Show all connected devices
tailscale ip                      # Show your Tailscale IP
tailscale ping [device]           # Ping another device

# SSH (Magic!)
tailscale ssh user@device         # SSH without config
tailscale ssh darri@cp2           # SSH to CP2

# FILE TRANSFER
tailscale file cp file.txt device:  # Send file to device
tailscale file get                   # Receive pending files

# NETWORK
tailscale netcheck                # Diagnose connection
tailscale bugreport               # Generate debug info
```

### Key IPs (Our Network)
```
CP1 (dwrek):    100.70.208.75
CP2 (darri):    100.85.71.74
CP3 (Darrick):  100.101.209.1
```

### SSH After Tailscale
```bash
# From CP1, connect to CP2
tailscale ssh darri@100.85.71.74

# Once connected, you're ON that computer
winget list                        # See installed apps
winget install AppName             # Install anything
# Full control!
```

### Hidden Features
- **MagicDNS**: Use device names instead of IPs
- **Funnel**: Expose local services to internet
- **Exit Nodes**: Route all traffic through specific device
- **ACLs**: Control who can access what
- **Subnet Routing**: Access entire home network remotely

---

## 3. GITHUB - CODE & COMMUNICATION HUB

### What It Does
- Version control for all code
- Communication channel between computers
- Issue tracking for bugs
- Actions for automation
- Releases for deployments

### CLI Commands (gh)
```bash
# AUTH
gh auth login                     # Authenticate
gh auth status                    # Check auth

# REPOS
gh repo list                      # List your repos
gh repo clone user/repo           # Clone repo
gh repo create                    # Create new repo
gh repo view                      # View current repo

# ISSUES (Great for communication!)
gh issue create                   # Create issue
gh issue list                     # List issues
gh issue view 123                 # View issue #123
gh issue close 123                # Close issue
gh issue comment 123 -b "message" # Add comment

# PULL REQUESTS
gh pr create                      # Create PR
gh pr list                        # List PRs
gh pr merge                       # Merge PR
gh pr checkout 123                # Checkout PR locally

# RELEASES
gh release create v1.0            # Create release
gh release list                   # List releases
gh release download               # Download release assets

# ACTIONS
gh run list                       # List workflow runs
gh run view                       # View run details
gh run watch                      # Watch running workflow
```

### Git Commands
```bash
# BASICS
git status                        # Check status
git add .                         # Stage all changes
git commit -m "message"           # Commit
git push                          # Push to remote
git pull                          # Pull latest

# BRANCHES
git branch                        # List branches
git checkout -b feature           # Create and switch
git merge feature                 # Merge branch

# COMMUNICATION VIA COMMITS
git log --oneline -10             # Recent commits (see what others did)
git diff HEAD~1                   # See last change
```

### Hidden Features
- **GitHub CLI Extensions**: Extend gh with custom commands
- **GitHub Pages**: Free static hosting
- **GitHub Actions**: Free CI/CD automation
- **Gists**: Quick code sharing
- **Codespaces**: Full dev environment in browser
- **Secret Scanning**: Alerts if you commit secrets

---

## 4. GOOGLE DRIVE - FILE SYNC HUB

### What It Does
- Sync files between all computers instantly
- G:/My Drive/ accessible everywhere
- TRINITY_COMMS/wake/ folder for AI communication

### No Official CLI, Use rclone
```bash
# INSTALL
winget install Rclone.Rclone

# CONFIGURE
rclone config                     # Setup Google Drive remote

# COMMANDS
rclone ls gdrive:                 # List files
rclone copy gdrive:file.txt .     # Download file
rclone copy file.txt gdrive:      # Upload file
rclone sync ./folder gdrive:folder  # Sync folder
```

### PowerShell for Local Drive
```powershell
# Find Google Drive letter
Get-PSDrive | Where-Object {$_.Description -like "*Google*"}

# Copy to Google Drive
Copy-Item file.txt "G:\My Drive\TRINITY_COMMS\"

# Watch for changes
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "G:\My Drive\TRINITY_COMMS\wake"
$watcher.EnableRaisingEvents = $true
```

### Key Paths
```
G:\My Drive\TRINITY_COMMS\          # Main comms folder
G:\My Drive\TRINITY_COMMS\wake\     # AI check-in folder
G:\My Drive\TRINITY_COMMS\logs\     # Log files
```

### Hidden Features
- **Desktop Sync**: Any folder can sync to Drive
- **Offline Mode**: Files available without internet
- **Version History**: Recover old versions
- **Shared Drives**: Team storage
- **Google Docs**: Real-time collaboration

---

## 5. RAILWAY - INSTANT HOSTING

### What It Does
- Deploy apps in seconds
- Free tier for small projects
- Auto-deploys from GitHub
- Databases included

### CLI Commands
```bash
# AUTH
railway login                     # Login to Railway

# PROJECTS
railway init                      # Initialize project
railway link                      # Link to existing project
railway status                    # Project status

# DEPLOY
railway up                        # Deploy current directory
railway logs                      # View logs
railway run [command]             # Run command in Railway env

# ENVIRONMENT
railway variables                 # List env vars
railway variables set KEY=value   # Set env var

# DATABASE
railway add                       # Add service (postgres, redis, etc)
```

### Deploy from GitHub
```bash
# In your project
railway init
railway up                        # First deploy

# Then push to GitHub
git push                          # Auto-deploys!
```

### Hidden Features
- **Preview Deployments**: Each PR gets preview URL
- **Cron Jobs**: Scheduled tasks
- **Private Networking**: Services talk securely
- **TCP Proxy**: Expose any port
- **Nixpacks**: Auto-detect build system

---

## 6. TWILIO - COMMUNICATION GATEWAY

### What It Does
- Send/receive SMS
- Make/receive phone calls
- Voice verification
- WhatsApp integration

### No CLI, API Only
```python
from twilio.rest import Client

# Setup
account_sid = 'your_sid'
auth_token = 'your_token'
client = Client(account_sid, auth_token)

# SEND SMS
message = client.messages.create(
    body="Hello from Trinity!",
    from_='+1234567890',  # Your Twilio number
    to='+0987654321'       # Recipient
)

# SEND VERIFICATION CODE
verification = client.verify.v2.services('service_sid') \
    .verifications.create(to='+0987654321', channel='sms')

# CHECK CODE
check = client.verify.v2.services('service_sid') \
    .verification_checks.create(to='+0987654321', code='123456')
```

### API Endpoints
```
SMS: https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages
Calls: https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls
Verify: https://verify.twilio.com/v2/Services/{sid}/Verifications
```

### Hidden Features
- **Webhooks**: Get notified of incoming SMS/calls
- **TwiML**: Script call flows
- **Conversations**: Multi-party messaging
- **Lookup**: Validate phone numbers
- **Voice Intelligence**: Call transcription

---

## QUICK REFERENCE: ALL CLI COMMANDS

```bash
# BITWARDEN
bw login / bw unlock / bw get password "name" / bw get totp "name"

# TAILSCALE
tailscale up / tailscale status / tailscale ssh user@device

# GITHUB
gh auth login / gh repo list / gh issue create / gh pr create

# RAILWAY
railway login / railway up / railway logs / railway variables

# GOOGLE DRIVE (via rclone)
rclone config / rclone copy / rclone sync
```

---

## AUTOMATION PATTERNS

### Get Secret and Use It
```bash
# Get API key from Bitwarden, use it
export API_KEY=$(bw get password "OpenAI API")
curl -H "Authorization: Bearer $API_KEY" https://api.openai.com/v1/models
```

### Deploy to Railway
```bash
# One command deploy
cd project && railway up
```

### SSH to Remote and Run Commands
```bash
# Connect and run
tailscale ssh darri@cp2 "winget install Bitwarden.Bitwarden"
```

### Sync File to All Computers
```bash
# Copy to Google Drive, all computers get it
cp important.txt "G:/My Drive/TRINITY_COMMS/"
```

---

## INSTALL COMMANDS (Run on Any Computer)

```powershell
# Install all foundational apps
winget install Bitwarden.Bitwarden
winget install Bitwarden.CLI
winget install Tailscale.Tailscale
winget install GitHub.cli
winget install Rclone.Rclone
winget install Railway.Railway

# Verify installations
bw --version
tailscale version
gh --version
railway version
rclone version
```

---

*This file syncs to all computers via Google Drive*
*Master every tool. Know every command. Control everything.*
