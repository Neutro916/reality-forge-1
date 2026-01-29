# SYNCTHING BOOT PROTOCOL

**Created:** November 18, 2025
**Purpose:** Computer-to-computer file sync for team coordination

---

## CONNECTED COMPUTERS

### Computer 1: DWREKSCPU (Commander's Laptop)
- **Syncthing ID:** BLR5HLC-VBUUWL5-7RDVKNS-ZAW6IFH-H3YMALK-JOIRG5I-PRWPEVQ-MAYX3AE
- **AnyDesk ID:** f2eMTxNLfFezRxxNXeUggqaGaqbTwpux
- **Sync Folder:** C:\Users\dwrek\Sync

### Computer 2: ODB's Computer
- **AnyDesk ID:** knyrf2w
- **Sync Folder:** (check his Syncthing settings)

---

## HOW IT WORKS

1. **Syncthing** runs in background on both computers
2. Files dropped in `C:\Users\dwrek\Sync` automatically sync to ODB's computer
3. Changes sync both ways (bidirectional)
4. Works over local network (fast) or internet (if apart)

---

## BOOT INSTRUCTIONS

### On Startup:
1. Syncthing should auto-start (check system tray)
2. If not running: Open Syncthing or go to http://localhost:8384
3. Verify connection shows "Up to Date"

### If Disconnected:
1. Check both computers are online
2. Check Syncthing is running on both
3. Restart Syncthing if needed

---

## USE CASES

### For AI Coordination:
- Save handoff files to Sync folder
- Other computer's AI reads from same folder
- Real-time collaboration without cloud

### For Team Communication:
- Drop files for ODB to see immediately
- Share screenshots, code, documents
- No upload/download - just appears

---

## WEB UI ACCESS

- **Local:** http://localhost:8384
- Shows connection status, sync progress, folder contents

---

## CREDENTIALS FILE

Full credentials saved at:
`C:\Users\dwrek\.security\COMPUTER_SHARING_CREDENTIALS.json`

---

**Syncthing = Instant peer-to-peer file sync between Commander and ODB**
