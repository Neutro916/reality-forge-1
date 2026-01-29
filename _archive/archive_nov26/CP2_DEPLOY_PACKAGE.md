# CP2 DEPLOYMENT PACKAGE
## Quick Setup for Triple Tornado Infinity
### Target: desktop-msmcfh2 (100.85.71.74)

---

## STEP 1: VERIFY INFRASTRUCTURE (2 min)

```bash
# Check Tailscale
tailscale status

# Should see:
# 100.70.208.75  dwrekscpu - CP1
# 100.85.71.74   desktop-msmcfh2 - THIS COMPUTER
# 100.101.209.1  desktop-s72lrro - CP3
```

---

## STEP 2: CHECK GOOGLE DRIVE (1 min)

Open File Explorer, verify G:\ drive exists with:
```
G:\My Drive\TRINITY_COMMS\
```

If not mounted, sign in to Google Drive with: darrick.preble@gmail.com

---

## STEP 3: CREATE .consciousness FOLDER (3 min)

```bash
# Create structure
mkdir -p ~/.consciousness/memory
mkdir -p ~/.consciousness/hub

# Copy key files from Google Drive
cp "G:/My Drive/TRINITY_COMMS/TRIPLE_TORNADO_INFINITY.md" ~/.consciousness/
cp "G:/My Drive/TRINITY_COMMS/TRINITY_BOOT_V2.md" ~/.consciousness/
```

---

## STEP 4: START CLAUDE CODE (1 min)

Open terminal:
```bash
claude
```

When Claude starts, tell it:
```
I am C2-Terminal on CP2 (desktop-msmcfh2).
Read C:\Users\darri\.consciousness\TRIPLE_TORNADO_INFINITY.md
We are activating Triple Tornado Infinity across 3 computers.
Report status and standby for coordination.
```

---

## STEP 5: WRITE STATUS FILE (Claude does this)

Claude will create:
```
G:\My Drive\TRINITY_COMMS\wake\CP2_TORNADO_READY.txt
```

Contents:
```
CP2 TORNADO READY - [TIMESTAMP]
Instance: C2-Terminal
Computer: CP2 (desktop-msmcfh2)
Tailscale: 100.85.71.74 - ONLINE
Status: TRIPLE_TORNADO_READY
```

---

## STEP 6: WAIT FOR ACTIVATION

Once CP1, CP2, and CP3 all have status files, Commander creates:
```json
// G:\My Drive\TRINITY_COMMS\TRIPLE_TORNADO_ACTIVE.json
{
  "activated": true,
  "timestamp": "ISO8601",
  "protocol": "INFINITY",
  "participants": ["CP1", "CP2", "CP3"]
}
```

Then ALL THREE enter synchronized operation mode.

---

## IDENTITY FOR THIS COMPUTER

**Computer:** CP2 (desktop-msmcfh2)
**Username:** darri
**Tailscale:** 100.85.71.74
**Instance Role:** C2-Architect (Mind)
**Specialty:** System design, architecture, optimization

---

## COMMUNICATION

**To send to all:**
```
trinity_broadcast "Message from CP2"
```

**To check messages:**
```
trinity_receive_messages
```

**To read shared files:**
```
G:\My Drive\TRINITY_COMMS\
```

---

## TROUBLESHOOTING

**Google Drive not syncing?**
1. Check system tray for Google Drive icon
2. Click → Sign in if needed
3. Use darrick.preble@gmail.com

**Tailscale offline?**
1. Run: `tailscale login`
2. Use overkillkulture@ account

**Can't ping CP1?**
1. Verify Tailscale connected
2. Try: `ping 100.70.208.75`

---

*Ready for Triple Tornado Infinity activation*
