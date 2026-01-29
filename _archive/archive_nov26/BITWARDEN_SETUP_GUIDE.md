# BITWARDEN SETUP & CONFIGURATION GUIDE
## How to make it auto-start, auto-fill, and work seamlessly
## Created: 2025-11-26

---

# PROBLEM: "I have to type my password every time"

## SOLUTION: Configure these settings

---

## STEP 1: AUTO-START ON BOOT

**In Bitwarden Desktop App:**
1. Open Bitwarden
2. Click **File** > **Settings** (or gear icon)
3. Find **"Start automatically on login"** or **"Start on Windows startup"**
4. ENABLE this option

**Alternative - Windows Startup:**
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create shortcut to Bitwarden in this folder

---

## STEP 2: STAY UNLOCKED LONGER

**Vault Timeout Settings:**
1. Open Bitwarden > Settings
2. Find **"Vault Timeout"**
3. Options:
   - Never (least secure, most convenient)
   - On system lock
   - On system idle (set minutes)
   - 1 hour / 4 hours / On restart

**Recommended:** Set to **"On system lock"** or **"4 hours"**

4. Find **"Vault Timeout Action"**
   - **Lock** = Requires master password again
   - **Log out** = Requires email + password again

**Recommended:** Set to **"Lock"** (not log out)

---

## STEP 3: BROWSER EXTENSION (CRITICAL FOR AUTO-FILL)

**This is what makes passwords auto-fill in websites:**

1. Open Chrome/Edge/Firefox
2. Go to browser's extension store:
   - Chrome: chrome.google.com/webstore
   - Search "Bitwarden"
3. Click **Add to Chrome** (or your browser)
4. Pin the extension to toolbar
5. Click extension icon > Log in with same account
6. Enable **"Auto-fill on page load"** in extension settings

---

## STEP 4: BROWSER EXTENSION SETTINGS

**In the browser extension:**
1. Click Bitwarden icon in browser toolbar
2. Click **Settings** (gear icon)
3. Configure:
   - **Auto-fill on page load**: ON
   - **Show auto-fill on page load**: ON
   - **Default URI match detection**: Base domain
   - **Vault timeout**: Same as desktop (e.g., 4 hours)
   - **Unlock with biometrics**: Enable if available

---

## STEP 5: UNLOCK WITH BIOMETRICS (Windows Hello)

**If your computer has fingerprint/face recognition:**
1. Bitwarden > Settings
2. Find **"Unlock with Windows Hello"**
3. Enable it
4. Now you can unlock with fingerprint instead of typing password

---

## STEP 6: PIN UNLOCK (Alternative to Master Password)

**Use a shorter PIN instead of full master password:**
1. Bitwarden > Settings
2. Find **"Unlock with PIN"**
3. Enable and set a PIN (4-8 digits)
4. Choose whether PIN requires master password on restart

---

# HOW AI INSTANCES CAN USE BITWARDEN

## Option 1: Bitwarden CLI (For Claude/AI)

**Install Bitwarden CLI:**
```bash
npm install -g @bitwarden/cli
```

**Authenticate:**
```bash
bw login
# Enter email and master password
```

**Unlock vault:**
```bash
export BW_SESSION=$(bw unlock --raw)
```

**Get a password:**
```bash
bw get password "Google"
bw get item "GitHub" --pretty
```

## Option 2: API Access (Advanced)

Bitwarden has an API but requires self-hosted server or premium.
Not recommended for basic use.

## Option 3: Share Vault Export (Careful with this)

**Export passwords (for AI reference):**
1. Bitwarden > Settings > Export Vault
2. Format: Encrypted JSON (safest)
3. Store in SECURE location

**WARNING:** Never share unencrypted password exports.

---

# RECOMMENDED SETTINGS SUMMARY

| Setting | Recommended Value |
|---------|-------------------|
| Start on boot | ON |
| Vault timeout | 4 hours or On system lock |
| Timeout action | Lock (not log out) |
| Browser extension | INSTALLED on Chrome |
| Auto-fill on page load | ON |
| Unlock with biometrics | ON (if available) |
| PIN unlock | Optional |

---

# PASSWORDS TO ADD TO BITWARDEN

**Add these accounts:**
1. Google (darrick.preble@gmail.com)
2. GitHub (overkillkulture)
3. Anthropic API key
4. Netlify
5. Railway
6. Any other service credentials

**How to add:**
1. Click + button in Bitwarden
2. Select "Login"
3. Enter:
   - Name: Service name
   - Username: Your username/email
   - Password: Your password
   - URI: Website URL (e.g., github.com)
4. Save

---

# SHARING VAULT WITH FAMILY/TEAM

**Bitwarden Organizations (Premium):**
- Create organization
- Invite members
- Share specific passwords

**Free alternative:**
- Each person has own vault
- Manually share critical passwords
- Use same master password (not recommended but works)

---

# TROUBLESHOOTING

**"Bitwarden won't auto-fill"**
1. Check browser extension is installed
2. Check extension is logged in
3. Check "auto-fill on page load" is ON
4. Check the saved URL matches the website

**"I keep getting locked out"**
1. Increase vault timeout to 4+ hours
2. Enable PIN unlock for quick access
3. Enable Windows Hello if available

**"Bitwarden doesn't start with Windows"**
1. Check startup setting in Bitwarden
2. Add to Windows startup folder manually

---

*This guide saved to Google Drive for all computers to access.*
