# PHONE REMOTE CONTROL - CAMPING EDITION
## Control all 3 computers from your phone

---

## HOW IT WORKS

The computers watch the `commands/` folder in Google Drive.
Create a file from your phone → Computer executes command → File deleted.

---

## COMMANDS (create empty files in `commands/` folder)

### Wake Computers
| File to Create | What it Does |
|---------------|--------------|
| `WAKE_ALL.cmd` | Wakes ALL Claude windows on ALL computers |
| `WAKE_CP1.cmd` | Wakes CP1 (Derek) only |
| `WAKE_CP2.cmd` | Wakes CP2 (Josh) only |
| `WAKE_CP3.cmd` | Wakes CP3 (Darrick) only |

### Get Status
| File to Create | What it Does |
|---------------|--------------|
| `STATUS.cmd` | All computers report to sync folder |

### Send Tasks
| File to Create | What it Does |
|---------------|--------------|
| `TASK_CP1.cmd` | Put task text in file, CP1 receives it |
| `TASK_CP2.cmd` | Put task text in file, CP2 receives it |
| `TASK_CP3.cmd` | Put task text in file, CP3 receives it |

### Broadcast
| File to Create | What it Does |
|---------------|--------------|
| `BROADCAST.cmd` | Put message in file, all windows receive it |

---

## STEP BY STEP FROM PHONE

1. Open Google Drive app
2. Navigate to: `TRINITY_COMMS/sync/commands/`
3. Tap the + button → Create new file
4. Name it (e.g., `WAKE_ALL.cmd`)
5. Save (content can be empty for wake commands)
6. Within 10 seconds, computers will respond
7. Check `REMOTE_COMMAND_LOG.txt` for confirmation

---

## SETUP REQUIRED (ONE TIME)

On each computer, run:
```
START_REMOTE_COMMAND_DAEMON.bat
```
(On Desktop or copy from sync folder)

---

## EXAMPLE: WAKE ALL COMPUTERS WHILE CAMPING

1. Phone → Google Drive → `TRINITY_COMMS/sync/commands/`
2. Create file: `WAKE_ALL.cmd`
3. All 3 computers wake up and continue autonomous work
4. Check `REMOTE_COMMAND_LOG.txt` to confirm

---

## EXAMPLE: SEND A TASK TO CP1

1. Phone → Google Drive → `TRINITY_COMMS/sync/commands/`
2. Create file: `TASK_CP1.cmd`
3. Edit file, add: `Run scans and fix any failures`
4. Save
5. CP1 receives the task in its Claude window

---

## TROUBLESHOOTING

- **No response?** Check that REMOTE_COMMAND_DAEMON is running
- **File not deleted?** Computer might be asleep or daemon stopped
- **Check status:** Look at `CP1_REMOTE_STATUS.json`, etc.

---

## TECHNICAL DETAILS

- Poll interval: 10 seconds
- Uses pyautogui for screen control
- Daemon auto-reports status on startup
- Log file: `REMOTE_COMMAND_LOG.txt`

---

**CAMPING MODE ACTIVATED**

*You can now command the fleet from anywhere with cell service.*
