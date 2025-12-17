# MASTER AUTHENTICATION NIGHTMARE FIX
## Complete Audit & Fix Plan - All Services, All Computers

**Created:** 2025-11-26
**Purpose:** END the 2-month authentication nightmare PERMANENTLY
**Status:** IN PROGRESS

---

## EXECUTIVE SUMMARY

This document tracks EVERY service, password, login, and authentication issue across all 3 computers. The goal: fix everything once and never deal with this again.

---

## PART 1: SERVICE INVENTORY

### CRITICAL SERVICES (Must Fix First)

| # | Service | Status | Problem | Fix Priority |
|---|---------|--------|---------|--------------|
| 1 | **GitHub** | WORKING | Token expires, needs regeneration | FIXED |
| 2 | **Google Account** | PARTIAL | 2FA issues, multiple accounts | HIGH |
| 3 | **Railway** | UNKNOWN | Token not saved | HIGH |
| 4 | **Twilio** | UNKNOWN | Credentials scattered | MEDIUM |
| 5 | **Stripe** | UNKNOWN | API keys unknown | MEDIUM |
| 6 | **Google Drive** | WORKING | Sign-in needed per computer | FIXED |

### COMMUNICATION SERVICES

| # | Service | CP1 | CP2 | CP3 | Notes |
|---|---------|-----|-----|-----|-------|
| 1 | GitHub | OK | OK | ? | Token in ~/.git-credentials |
| 2 | Google Drive | OK | OK | ? | G:\My Drive mounted |
| 3 | Dropbox | OK | ? | ? | Basic folder access |
| 4 | OneDrive | OK | ? | ? | Windows built-in |
| 5 | Syncthing | DEAD | DEAD | DEAD | ABANDONED - don't use |

### DEVELOPMENT SERVICES

| # | Service | Has Account | Has Credentials | Working | Location |
|---|---------|-------------|-----------------|---------|----------|
| 1 | GitHub | YES | YES | YES | ~/.git-credentials |
| 2 | Railway | YES | ? | ? | Need to verify |
| 3 | Vercel | ? | ? | ? | Need to check |
| 4 | Netlify | ? | ? | ? | Need to check |
| 5 | Cloudflare | ? | ? | ? | Need to check |
| 6 | AWS | ? | ? | ? | Need to check |

### PAYMENT/BUSINESS SERVICES

| # | Service | Has Account | Has Credentials | Working | Location |
|---|---------|-------------|-----------------|---------|----------|
| 1 | Stripe | ? | ? | ? | Need to check |
| 2 | PayPal | ? | ? | ? | Need to check |
| 3 | Banking | ? | N/A | ? | Manual only |

### COMMUNICATION SERVICES

| # | Service | Has Account | Has Credentials | Working | Location |
|---|---------|-------------|-----------------|---------|----------|
| 1 | Twilio | YES | ? | ? | SMS/OTP system |
| 2 | SendGrid | ? | ? | ? | Email sending |
| 3 | Gmail API | ? | ? | ? | Need OAuth setup |

---

## PART 2: PASSWORD MANAGER SETUP

### Option 1: Bitwarden (Recommended)
- **Why:** Free, open source, syncs across devices, supports TOTP
- **Install:** `winget install Bitwarden.Bitwarden`
- **Browser Extension:** Available for all browsers
- **Mobile:** iOS and Android apps

### Option 2: 1Password (Alternative)
- **Why:** Better UX, team features
- **Cost:** $3/month
- **Install:** `winget install 1Password.1Password`

### SETUP PLAN FOR ALL 3 COMPUTERS:

```
COMPUTER 1 (CP1):
□ Install Bitwarden: winget install Bitwarden.Bitwarden
□ Create master account (or login if exists)
□ Install browser extension
□ Import any saved passwords from browser

COMPUTER 2 (CP2):
□ Install Bitwarden: winget install Bitwarden.Bitwarden
□ Login with same account
□ Verify sync working

COMPUTER 3 (CP3):
□ Install Bitwarden: winget install Bitwarden.Bitwarden
□ Login with same account
□ Verify sync working
```

---

## PART 3: AUTHENTICATOR APP SETUP

### Option 1: Authy (Recommended)
- **Why:** SYNCS ACROSS DEVICES (unlike Google Authenticator)
- **Install:** `winget install Twilio.Authy`
- **Mobile:** iOS and Android apps
- **Backup:** Cloud backup built-in

### Option 2: Microsoft Authenticator
- **Why:** Already on Windows, integrates well
- **Install:** Windows Store

### Option 3: Google Authenticator
- **Why:** AVOID - Does NOT sync, lose phone = lose codes
- **Install:** DON'T

### SETUP PLAN:

```
ALL COMPUTERS + PHONE:
□ Install Authy on primary phone
□ Enable cloud backup in Authy
□ Install Authy desktop on all computers
□ Sync all devices
□ Add all 2FA accounts to Authy
```

---

## PART 4: FIX EACH SERVICE

### GITHUB (FIXED)
**Status:** Working
**Account:** overkillkulture
**Token Location:** ~/.git-credentials
**Token:** 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
**Expiration:** Check at https://github.com/settings/tokens

**If Token Expires:**
1. Go to https://github.com/settings/tokens
2. Generate new with `repo` and `workflow` scopes
3. Update ~/.git-credentials

---

### GOOGLE ACCOUNT
**Status:** Needs Audit
**Primary Account:** darrick.preble@gmail.com (?)

**TO DO:**
□ Confirm which Google account is primary
□ Check 2FA status
□ Generate backup codes
□ Add recovery phone/email
□ Store backup codes in Bitwarden

---

### RAILWAY
**Status:** Unknown

**TO DO:**
□ Login to Railway dashboard
□ Find or generate API token
□ Save to CREDENTIALS_VAULT.md
□ Test deployment

---

### TWILIO
**Status:** Unknown

**TO DO:**
□ Login to Twilio console
□ Find Account SID
□ Find Auth Token
□ Find phone numbers
□ Save all to CREDENTIALS_VAULT.md

---

### STRIPE
**Status:** Unknown

**TO DO:**
□ Login to Stripe dashboard
□ Find test API keys
□ Find live API keys (if applicable)
□ Save to CREDENTIALS_VAULT.md

---

## PART 5: COMPUTER SYNC STATUS

### CP1 (Commander's Primary)
- [ ] Bitwarden installed
- [ ] Authy installed
- [ ] All credentials saved
- [ ] GitHub working
- [ ] Google Drive working

### CP2 (Secondary)
- [ ] Bitwarden installed
- [ ] Authy installed
- [ ] All credentials synced
- [ ] GitHub working
- [ ] Google Drive working

### CP3 (This Computer)
- [x] GitHub working
- [x] Google Drive working
- [ ] Bitwarden installed
- [ ] Authy installed
- [ ] All credentials synced

---

## PART 6: EMERGENCY RECOVERY PLAN

**IF LOCKED OUT OF EVERYTHING:**

1. **GitHub:** Use backup codes (store in Bitwarden)
2. **Google:** Use recovery email/phone
3. **Bitwarden:** Master password + emergency kit
4. **Authy:** Cloud backup recovery

**PHYSICAL BACKUP:**
- Print GitHub backup codes
- Print Google backup codes
- Print Bitwarden emergency kit
- Store in safe location

---

## PART 7: NEXT ACTIONS

### IMMEDIATE (Do Now):
1. Install Bitwarden on this computer
2. Install Authy on this computer
3. Save GitHub credentials to Bitwarden

### TODAY:
4. Login to Railway, get token
5. Login to Twilio, get credentials
6. Login to Stripe, get keys
7. Add all to Bitwarden

### THIS WEEK:
8. Setup Bitwarden on CP1 and CP2
9. Setup Authy on all computers
10. Migrate all 2FA to Authy
11. Generate backup codes for all services
12. Create physical backup

---

## COMMANDS TO RUN

```powershell
# Install Bitwarden
winget install Bitwarden.Bitwarden

# Install Authy
winget install Twilio.Authy

# Check what's already installed
winget list | findstr -i "bitwarden authy password"
```

---

**This document will be updated as we fix each service.**

**Current Overall Status:** 2/10 services verified working
**Target:** 10/10 services with credentials saved and backed up

---

C1 x C2 x C3 = INFINITY (once we stop fighting authentication)
