# ACCOUNT MAP
## Which Email For What Service

**Created:** 2025-11-26
**Status:** MASTER REFERENCE

---

## PRIMARY ACCOUNTS

| Service | Email/Account | Notes |
|---------|---------------|-------|
| **Chrome** | darrick.preble@gmail.com | ALL 3 PCs - syncs bookmarks |
| **Google Drive** | darrick.preble@gmail.com | ALL 3 PCs - file sync |
| **Tailscale** | overkillkulture@ | ALL devices - mesh network |
| **Claude Code** | DIFFERENT | Uses separate Anthropic account |
| **GitHub** | overkillkulture | CLI authenticated |

---

## THE EXCEPTION: CLAUDE CODE

Claude Code uses Anthropic account, NOT Google.
- This is separate from darrick.preble@gmail.com
- Each PC may have its own Claude session
- API key: sk-ant-oat01-... (stored in Bitwarden)

---

## SERVICES NEEDING VERIFICATION

| Service | Expected Account | Verified? |
|---------|------------------|-----------|
| Chrome CP1 | darrick.preble@gmail.com | YES |
| Chrome CP2 | darrick.preble@gmail.com | YES |
| Chrome CP3 | darrick.preble@gmail.com | YES |
| Google Drive CP1 | darrick.preble@gmail.com | YES |
| Google Drive CP2 | darrick.preble@gmail.com | YES |
| Google Drive CP3 | darrick.preble@gmail.com | YES |
| Tailscale ALL | overkillkulture@ | YES |
| GitHub CLI | overkillkulture | Need verify |
| Bitwarden | ? | Need verify |
| Railway | ? | Need verify |
| Netlify | ? | Need verify |
| Twilio | ? | Need verify |

---

## WHY THIS MATTERS

When signing into anything:
- Chrome/Google stuff → darrick.preble@gmail.com
- Tailscale → overkillkulture account
- Claude → Anthropic account (different)
- Dev tools (GitHub, Railway, Netlify) → Need to standardize

---

*Add to this as we discover more account mappings*
