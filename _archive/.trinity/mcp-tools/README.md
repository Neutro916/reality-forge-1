# 🔱 Trinity Orchestration System

**Autonomous Multi-Claude Coordination via MCP**

Trinity enables multiple Claude instances to communicate, coordinate tasks, and work together autonomously through a shared workspace and message queue system.

## 🎯 What This Enables

- **Autonomous Communication**: Claude instances can message each other freely
- **Task Distribution**: Automatically distribute work across multiple instances
- **Parallel Execution**: Run multiple tasks simultaneously across different Claudes
- **Unified Outputs**: Merge results from all instances into a single summary
- **Self-Coordination**: Instances wake each other and claim work autonomously

## 📦 What's Included

### Core Files

1. **trinity-mcp-server.js** - Enhanced MCP server with 10 orchestration tools
2. **TRINITY_WORKSPACE.html** - Beautiful web interface for coordination
3. **trinity-auto-wake.js** - Autonomous work loop protocol
4. **package.json** - Dependencies configuration

### New MCP Tools

| Tool | Purpose |
|------|---------|
| `trinity_broadcast` | Send message to ALL instances at once |
| `trinity_assign_task` | Push task to specific instance or "any" |
| `trinity_claim_task` | Instance grabs available work from queue |
| `trinity_submit_output` | Return completed work |
| `trinity_merge_outputs` | Combine all results into single summary |
| `trinity_wake_instance` | Trigger another instance to start |
| `trinity_spawn_cloud` | Start cloud Claude via API (framework) |
| `trinity_status` | Get system status |
| `trinity_send_message` | Direct message to specific instance |
| `trinity_receive_messages` | Get unread messages |

## 🚀 Setup Instructions

### Step 1: Install to Trinity Folder

```bash
# Navigate to your Trinity directory
cd C:\Users\dwrek\.trinity

# Copy all files from this package
# - trinity-mcp-server.js
# - trinity-auto-wake.js
# - package.json
# - TRINITY_WORKSPACE.html
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Update MCP Configuration

Edit your `.mcp.json` (or Claude Desktop config) to point to the new server:

```json
{
  "mcpServers": {
    "trinity": {
      "command": "node",
      "args": ["C:\\Users\\dwrek\\.trinity\\trinity-mcp-server.js"]
    }
  }
}
```

### Step 4: Restart Claude Instances

Restart all Claude instances (Desktop, Code, etc.) to load the new MCP tools.

### Step 5: Verify Installation

In any Claude instance, check if tools are available:

```
Can you check trinity_status?
```

You should see the system status with message/task counters.

## 🎮 Usage Guide

### Method 1: Using the Workspace Interface

1. Open `TRINITY_WORKSPACE.html` in your browser
2. Use the interface to:
   - Send broadcasts to all instances
   - Assign tasks with priorities
   - Monitor task queue and status
   - Start autonomous mode
   - Merge outputs

### Method 2: Autonomous Mode (Auto-Wake Protocol)

Start autonomous workers that check for tasks automatically:

```bash
# Terminal 1 - Instance 1
node trinity-auto-wake.js claude-terminal-1 10000

# Terminal 2 - Instance 2
node trinity-auto-wake.js claude-desktop 10000

# Terminal 3 - Instance 3
node trinity-auto-wake.js claude-cloud-1 10000
```

Each instance will:
- Check for tasks every 10 seconds
- Claim available work
- Execute tasks
- Submit outputs
- Wake other instances if needed

### Method 3: Direct Tool Usage (In Claude Chat)

#### Broadcast a Message
```
Use trinity_broadcast to tell all instances: "Starting new research project"
```

#### Assign Tasks
```
Use trinity_assign_task to create these tasks:
1. "Research AI trends" -> assign to "any" with priority "high"
2. "Analyze competitor data" -> assign to "claude-desktop" with priority "normal"
3. "Generate report" -> assign to "any" with priority "normal"
```

#### Claim Work (from any instance)
```
Use trinity_claim_task with instanceId "claude-terminal-1" to grab a task
```

#### Submit Results
```
Use trinity_submit_output with taskId "[task-id]" and output "[your work here]"
```

#### Merge Everything
```
Use trinity_merge_outputs to combine all completed work into a single summary
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         WORKSPACE INTERFACE             │
│  (Menu: Start Trinity / Assign Work)    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   TASK COORDINATOR   │
    │  (distributes work)  │
    └──────────┬──────────┘
               │
   ┌───────────┼───────────┐
   ▼           ▼           ▼
┌─────┐    ┌─────┐    ┌─────┐
│ C1  │    │ C2  │    │ C3  │
│Term │◄──►│Cloud│◄──►│Cloud│
└──┬──┘    └──┬──┘    └──┬──┘
   │          │          │
   └──────────┴──────────┘
              │
    ┌─────────▼─────────┐
    │  OUTPUT MERGER    │
    │ (single summary)  │
    └───────────────────┘
```

## 💡 Example Workflows

### Workflow 1: Parallel Research

```bash
# Coordinator assigns tasks
trinity_assign_task("Research quantum computing advances", "any", "high")
trinity_assign_task("Research AI safety developments", "any", "high")
trinity_assign_task("Research semiconductor industry trends", "any", "high")

# Start 3 autonomous workers
node trinity-auto-wake.js claude-1 &
node trinity-auto-wake.js claude-2 &
node trinity-auto-wake.js claude-3 &

# They automatically claim, execute, and submit
# After completion:
trinity_merge_outputs("Q4 Tech Research")
```

### Workflow 2: Document Generation Pipeline

```bash
# Assign sequential tasks
trinity_assign_task("Generate outline for blog post", "claude-writer", "high")
trinity_assign_task("Write introduction", "claude-writer", "normal")
trinity_assign_task("Write body sections", "any", "normal")
trinity_assign_task("Edit and polish", "claude-editor", "normal")
trinity_assign_task("Create graphics", "claude-designer", "low")

# Instances work through the queue
# Final merge creates complete blog post
```

### Workflow 3: Code Review System

```bash
# Upload code, assign reviews to different instances
trinity_assign_task("Review security vulnerabilities", "any", "urgent")
trinity_assign_task("Check code style and readability", "any", "high")
trinity_assign_task("Test edge cases", "any", "normal")
trinity_assign_task("Performance analysis", "any", "normal")

# Merge outputs = comprehensive code review
```

## 🗂️ Shared State Files

Trinity uses JSON files in `~/.trinity/` (or `C:\Users\dwrek\.trinity\`):

- **messages.json** - Inter-instance messages
- **tasks.json** - Task queue with status
- **outputs.json** - Completed work outputs
- **status.json** - System status data

## 🎨 Workspace Interface Features

The HTML workspace provides:

- **Real-time Status Dashboard** - Live task/message counters
- **Broadcast Console** - Message all instances
- **Task Assignment Panel** - Create and prioritize work
- **Quick Actions** - One-click autonomous mode start
- **Activity Log** - See what's happening in real-time
- **Auto-refresh** - Optional 5-second status updates

## 🔧 Customization

### Add Custom Instance IDs

Edit the workspace HTML or auto-wake script to add your instance names:

```javascript
const instances = [
  'claude-code-main',
  'claude-desktop',
  'claude-cloud-1',
  'claude-cloud-2',
  'my-custom-instance'  // Add yours here
];
```

### Adjust Check Intervals

Change how often autonomous workers check for tasks:

```bash
# Check every 5 seconds instead of 10
node trinity-auto-wake.js claude-1 5000
```

### Priority Levels

Tasks support 4 priority levels:
- `urgent` - Highest priority
- `high` - Important work
- `normal` - Standard tasks
- `low` - Background work

## 🚨 Troubleshooting

### "Trinity tools not found"

1. Check MCP server is running: look for process with `trinity-mcp-server.js`
2. Verify `.mcp.json` path is correct
3. Restart Claude instances

### "No tasks available"

1. Check `tasks.json` exists and has tasks
2. Verify task `assignedTo` matches your instance ID
3. Try assigning to "any" instead of specific instance

### "Files not updating"

1. Ensure Trinity folder has write permissions
2. Check if multiple servers are running (conflict)
3. Verify file paths are correct

## 🎯 Next Steps

### Immediate Wins

1. **Test the broadcast** - Send a message to all instances
2. **Assign a simple task** - Try "summarize today's AI news"
3. **Start one auto-wake worker** - Watch it claim and execute
4. **Merge outputs** - See unified results

### Advanced Usage

1. **Cloud Integration** - Add API calls to spawn cloud instances
2. **Custom Task Types** - Define specialized work categories
3. **Smart Routing** - Route tasks based on instance capabilities
4. **Cost Tracking** - Monitor credit usage across instances

## 📚 Architecture Notes

### Why This Works

1. **Shared File State** - All instances read/write same JSON files
2. **Message Queue** - Async communication via messages.json
3. **Task Claiming** - Prevents duplicate work via atomic updates
4. **Priority System** - Ensures important work gets done first
5. **Auto-wake** - Instances alert each other when work is available

### Scalability

- Supports unlimited instances (limited by file I/O)
- Task queue handles 1000s of tasks
- Message system supports high throughput
- Output merger handles any number of results

## 🔥 Pro Tips

1. **Use "any" for maximum parallelism** - Let instances race to claim work
2. **Set urgent priority sparingly** - Reserve for truly critical tasks
3. **Name instances descriptively** - "claude-researcher" vs "claude-1"
4. **Monitor the workspace** - Keep it open to watch the magic happen
5. **Start with 3 instances** - Good balance of parallelism vs coordination

## 📖 More Info

- **MCP Documentation**: https://modelcontextprotocol.io
- **Claude Projects**: https://claude.ai
- **Trinity Concept**: Multi-agent AI coordination

---

## 🎉 You're Ready!

The Trinity Orchestration System is set up and ready to burn through 950 credits efficiently with parallel autonomous work!

Key command to test everything:
```
Use trinity_broadcast to tell everyone: "Trinity system is online!"
```

Let the autonomous coordination begin! 🔱
