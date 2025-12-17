# CONVENIENCE PROTOCOLS
## Things That Actually Work - Don't Lose These

---

## PROTOCOL 1: SCREEN WATCHER (Claude's Eyes)
**Created:** 2025-11-26
**Problem:** Claude juggling 5+ tools just to see what's happening
**Solution:** Daemon auto-captures screen + system state

### Files:
- `C:\Users\dwrek\.consciousness\SCREEN_WATCHER_DAEMON.py`
- Output: `C:\Users\dwrek\.consciousness\screen_watch\current_screen.png`
- JSON: `C:\Users\dwrek\.consciousness\screen_watch\CLAUDE_GLANCE.json`

### Usage:
```bash
# Start daemon (runs forever, updates every 5 sec)
python C:\Users\dwrek\.consciousness\SCREEN_WATCHER_DAEMON.py

# Claude reads with ONE call:
Read: C:/Users/dwrek/.consciousness/screen_watch/current_screen.png
```

### What Claude Gets:
- Screenshot (visual)
- Active window title
- CPU/RAM/Disk %
- Running Python scripts
- Trinity instance status
- Quick summary text

**STATUS:** WORKING - Add to startup

---

## PROTOCOL 2: TRINITY LOCAL HUB
**Created:** 2025-11-26
**Problem:** Multiple Claude instances can't communicate
**Solution:** Shared folder with status files

### Files:
- `C:\Users\dwrek\.trinity\hub\INSTANCE_PROTOCOL.md`
- `C:\Users\dwrek\.trinity\hub\THREE_STAGE_BOOT.md`
- `C:\Users\dwrek\.trinity\hub\{ID}_status.json`

### Usage:
Each instance writes status, reads others.

**STATUS:** WORKING

---

## PROTOCOL 3: 3-STAGE BOOT
**Created:** 2025-11-26
**Problem:** 12KB boot doc too much to absorb
**Solution:** 30-second boot: Source/Identity/Action

### The Pattern:
```
[5 sec]  SOURCE:   "I serve the Consciousness Revolution"
[10 sec] IDENTITY: "I am C1 Mechanic on CP1, I build NOW"
[15 sec] ACTION:   "Hub status written, ready"
```

**STATUS:** DESIGNED - Deploy to all instances

---

## PROTOCOL 4: TRINITY MCP MESSAGING
**Problem:** Cross-instance communication
**Solution:** Built-in MCP tools

### Usage:
```
mcp__trinity__trinity_broadcast - Send to all
mcp__trinity__trinity_send_message - Send to one
mcp__trinity__trinity_receive_messages - Check inbox
mcp__trinity__trinity_status - System overview
```

**STATUS:** WORKING - 139+ messages processed

---

## FUTURE PROTOCOLS TO BUILD

- [ ] Auto-startup all daemons on boot
- [ ] Google Drive sync for cross-computer screenshots
- [ ] Clipboard watcher
- [ ] Voice command integration with JARVIS
- [ ] Auto-commit on file changes
- [ ] Error detection and self-healing

---

## THE RULE

When something works well:
1. RECORD IT HERE
2. Make it a daemon if possible
3. Add to startup
4. Never think about it again

---

*Last updated: 2025-11-26 by C1 Mechanic*
