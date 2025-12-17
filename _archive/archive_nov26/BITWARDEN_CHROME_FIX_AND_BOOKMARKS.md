# BITWARDEN FIX + STANDARD BOOKMARKS BAR
## For ALL 3 PCs - CP1, CP2, CP3

**Created:** 2025-11-26
**Status:** DEPLOY TO ALL COMPUTERS

---

## PART 1: FIX BITWARDEN NOT PROMPTING TO SAVE PASSWORDS

### Problem:
- Google is prompting to save passwords
- Bitwarden is NOT prompting
- We want Bitwarden to handle ALL passwords

### Step 1: DISABLE Google Password Manager

1. Open Chrome
2. Go to: `chrome://settings/passwords`
3. Turn OFF "Offer to save passwords"
4. Turn OFF "Auto Sign-in"
5. This stops Google from competing with Bitwarden

### Step 2: ENABLE Bitwarden Prompts

1. Click the Bitwarden extension icon (puzzle piece if hidden)
2. Click the gear icon (Settings)
3. Go to "Auto-fill" section
4. Enable these:
   - ✅ "Ask to add login" - prompts when you enter new credentials
   - ✅ "Ask to update existing" - prompts when password changes
   - ✅ "Auto-fill on page load" (optional - can be annoying)
   - ✅ "Default URI match detection" = Base domain

### Step 3: UNLOCK Bitwarden

**IMPORTANT:** Bitwarden only prompts when UNLOCKED!

1. Click Bitwarden extension
2. Enter your master password
3. Check "Remember" to stay logged in longer
4. Set timeout to "On Browser Restart" (not every 15 mins)

### Step 4: PIN Bitwarden Extension

1. Click puzzle piece icon (Extensions)
2. Find Bitwarden
3. Click the PIN icon to keep it visible
4. Bitwarden should now show in toolbar

---

## PART 2: STANDARD BOOKMARKS BAR

### Design Philosophy:
- Same layout on ALL 3 PCs
- Most used tools first
- Grouped by function
- No folders (everything visible)

### THE STANDARD BOOKMARKS BAR:

```
[Gmail] [Drive] [GitHub] [Netlify] [Railway] | [Consciousness Site] [Bugs] | [Bitwarden] [Tailscale] [Remote Desktop]
```

### Exact URLs:

| Name | URL |
|------|-----|
| Gmail | https://mail.google.com |
| Drive | https://drive.google.com |
| GitHub | https://github.com/overkillkulture |
| Netlify | https://app.netlify.com |
| Railway | https://railway.app/dashboard |
| Consciousness Site | https://conciousnessrevolution.io |
| Bugs | https://conciousnessrevolution.io/bugs-live.html |
| Bitwarden | https://vault.bitwarden.com |
| Tailscale | https://login.tailscale.com/admin/machines |
| Remote Desktop | https://remotedesktop.google.com/access |

### How to Set This Up:

1. Show bookmarks bar: `Ctrl+Shift+B`
2. Right-click bookmarks bar → "Add page"
3. Add each bookmark in order
4. Delete any existing bookmarks that aren't in the standard list
5. Sync should push this to other PCs (if sync is working)

### Alternative - Import Method:

If Chrome sync isn't working, export from CP1:
1. `chrome://bookmarks`
2. Three dots → Export bookmarks
3. Save to `G:\My Drive\TRINITY_COMMS\bookmarks_standard.html`
4. Import on CP2/CP3 from same location

---

## PART 3: VERIFY CHROME SYNC IS WORKING

1. Go to: `chrome://settings/syncSetup`
2. Ensure "Sync everything" is ON
3. Or manually enable:
   - ✅ Bookmarks
   - ✅ Extensions
   - ✅ Settings
   - ✅ History (optional)
   - ❌ Passwords (NO - use Bitwarden)

### Force Sync:
- Go to `chrome://settings/syncSetup/advanced`
- Click "Reset sync"
- Wait 5 minutes
- Check other computers

---

## CHECKLIST FOR EACH PC

### CP1:
- [ ] Disabled Google password manager
- [ ] Bitwarden prompts enabled
- [ ] Bitwarden pinned to toolbar
- [ ] Standard bookmarks bar set
- [ ] Chrome sync verified

### CP2:
- [ ] Disabled Google password manager
- [ ] Bitwarden prompts enabled
- [ ] Bitwarden pinned to toolbar
- [ ] Standard bookmarks bar set
- [ ] Chrome sync verified

### CP3:
- [ ] Disabled Google password manager
- [ ] Bitwarden prompts enabled
- [ ] Bitwarden pinned to toolbar
- [ ] Standard bookmarks bar set
- [ ] Chrome sync verified

---

## COMMANDER ACTION REQUIRED

Do this NOW on CP1 (the laptop you're on):

1. **Disable Google passwords:**
   - Open new tab: `chrome://settings/passwords`
   - Turn OFF both toggles

2. **Fix Bitwarden:**
   - Click Bitwarden extension
   - Settings → Auto-fill → Enable prompts
   - Pin to toolbar

3. **Set bookmarks bar:**
   - `Ctrl+Shift+B` to show bar
   - Add the standard bookmarks in order

4. **Verify sync:**
   - `chrome://settings/syncSetup`
   - Confirm "Bookmarks" is syncing

Once done on CP1, changes should sync to CP2/CP3 automatically.

---

*This file syncs to all computers via Google Drive*
