# TRINITY MCP DEPLOYMENT PACKAGE
## For T2/T3 Computers

---

## QUICK START (5 minutes)

### Step 1: Verify Google Drive is Syncing
Make sure you can see this folder:
```
G:\My Drive\TRINITY_COMMS\.trinity\
```

If your Google Drive letter is different (like D: or E:), note that letter.

### Step 2: Install Node.js (if not installed)
```
Download from: https://nodejs.org/
Install LTS version (20.x or higher)
```

### Step 3: Install MCP SDK
Open Command Prompt or PowerShell and run:
```bash
npm install -g @modelcontextprotocol/sdk
```

### Step 4: Create Your .mcp.json
Create this file: `C:\Users\YOUR_USERNAME\.mcp.json`

Replace YOUR_USERNAME with your actual Windows username.
Replace G: with your Google Drive letter if different.

```json
{
  "mcpServers": {
    "trinity": {
      "command": "node",
      "args": [
        "G:\\My Drive\\TRINITY_COMMS\\.trinity\\mcp-tools\\trinity-mcp-server.js"
      ],
      "env": {
        "TRINITY_PATH": "G:\\My Drive\\TRINITY_COMMS\\.trinity"
      }
    }
  }
}
```

### Step 5: Restart Claude Code
Close and reopen Claude Code to load the new MCP config.

### Step 6: Test Connection
In Claude Code, try:
```
mcp__trinity__trinity_status
```

You should see:
- sharedPath pointing to Google Drive
- Any messages from other computers

### Step 7: Announce Yourself
```
mcp__trinity__trinity_broadcast "T2 ONLINE from [YOUR_COMPUTER_NAME]" --from T2
```

---

## WHAT'S IN THIS FOLDER

```
.trinity/
├── mcp-tools/
│   ├── trinity-mcp-server.js    # Main MCP server (used by Claude)
│   └── trinity-http-server.js   # HTTP backup (if sync lag issues)
├── messages.json                 # Shared message queue
├── tasks.json                    # Shared task queue
├── outputs.json                  # Completed work outputs
├── heartbeats.json               # Active instance tracking
└── DEPLOY_README.md              # This file
```

---

## AVAILABLE COMMANDS

Once connected, you have these MCP tools:

| Command | Description |
|---------|-------------|
| `trinity_status` | Check system status |
| `trinity_broadcast` | Message ALL instances |
| `trinity_send_message` | Message specific instance |
| `trinity_receive_messages` | Get your messages |
| `trinity_assign_task` | Push task to instance |
| `trinity_claim_task` | Grab work from queue |
| `trinity_submit_output` | Return completed work |
| `trinity_merge_outputs` | Combine all results |
| `trinity_wake_instance` | Wake another instance |

---

## HTTP BACKUP (Optional)

If Google Drive sync has lag, run the HTTP server on C1:
```bash
cd "G:\My Drive\TRINITY_COMMS\.trinity\mcp-tools"
node trinity-http-server.js 3333
```

Then T2/T3 can access via HTTP:
- `http://C1_IP_ADDRESS:3333/status`
- `http://C1_IP_ADDRESS:3333/broadcast`
- etc.

---

## TROUBLESHOOTING

### "Trinity tools not found"
- Check `.mcp.json` path is correct
- Verify Google Drive is syncing
- Restart Claude Code

### "File not found" errors
- Your Google Drive letter might be different (D:, E:, etc.)
- Update paths in `.mcp.json`

### Messages not appearing
- Check Google Drive sync status
- Force sync by right-clicking tray icon
- Try HTTP backup if persistent

### "Cannot find module @modelcontextprotocol/sdk"
Run: `npm install -g @modelcontextprotocol/sdk`

---

## INSTANCE NAMING CONVENTION

| Instance | Computer | Role |
|----------|----------|------|
| C1 | Computer 1 (Main) | Commander Hub |
| T1 | Terminal 1 | Desktop Claude |
| T2 | Terminal 2 | Computer 2 Claude |
| T3 | Terminal 3 | Computer 3 Claude |
| TIGER | Any new member | New team member |

---

## CREATED BY
C1 Mechanic - November 30, 2025
Trinity System v3.0 - Multi-Computer Orchestration
