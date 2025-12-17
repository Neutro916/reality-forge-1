#!/usr/bin/env node

/**
 * TRINITY MCP SERVER v3.0 - Multi-Computer Orchestration
 *
 * SHARED FOLDER VERSION - All computers point to same OneDrive/Google Drive folder
 *
 * Configuration:
 * - Set TRINITY_PATH environment variable to shared folder location
 * - Default: Uses OneDrive Trinity_Shared folder
 *
 * Tools Available:
 * - trinity_status: Get system status
 * - trinity_send_message: Direct message to instance
 * - trinity_receive_messages: Get your messages
 * - trinity_broadcast: Message all instances
 * - trinity_assign_task: Push task to instance
 * - trinity_claim_task: Grab work from queue
 * - trinity_submit_output: Return completed work
 * - trinity_merge_outputs: Combine all results
 * - trinity_wake_instance: Trigger another instance
 * - trinity_spawn_cloud: Start cloud Claude via API
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

// ========================================
// PATH CONFIGURATION - SHARED FOLDER
// ========================================

// Priority order for TRINITY_PATH:
// 1. Environment variable TRINITY_PATH
// 2. OneDrive shared folder
// 3. Google Drive shared folder
// 4. Dropbox shared folder
// 5. Local fallback

function getTrinityPath() {
  // Check environment variable first
  if (process.env.TRINITY_PATH) {
    return process.env.TRINITY_PATH;
  }

  const homeDir = os.homedir();

  // Try shared cloud folders in order
  const sharedPaths = [
    path.join(homeDir, 'OneDrive', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, 'Google Drive', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, 'GoogleDrive', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, 'Dropbox', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, '.trinity')  // Local fallback
  ];

  // Return first path that exists or default to OneDrive
  for (const p of sharedPaths) {
    try {
      require('fs').accessSync(p);
      return p;
    } catch (e) {
      continue;
    }
  }

  // Default to OneDrive path (will be created)
  return path.join(homeDir, 'OneDrive', 'Trinity_Shared', '.trinity');
}

const TRINITY_DIR = getTrinityPath();
const MESSAGES_FILE = path.join(TRINITY_DIR, 'messages.json');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');
const STATUS_FILE = path.join(TRINITY_DIR, 'status.json');
const HEARTBEAT_FILE = path.join(TRINITY_DIR, 'heartbeats.json');

// Log the path being used
console.error(`Trinity MCP Server v3.0 - Using path: ${TRINITY_DIR}`);

// ========================================
// FILE OPERATIONS WITH RETRY
// ========================================

async function ensureTrinityDir() {
  try {
    await fs.mkdir(TRINITY_DIR, { recursive: true });
  } catch (error) {
    // Directory might already exist
  }
}

// Read JSON with retry (handles cloud sync conflicts)
async function readJSON(filepath, fallback = [], retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const data = await fs.readFile(filepath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      if (i === retries - 1) return fallback;
      await new Promise(r => setTimeout(r, 100 * (i + 1)));
    }
  }
  return fallback;
}

// Write JSON with atomic write (temp file + rename)
async function writeJSON(filepath, data) {
  const tempPath = filepath + '.tmp.' + Date.now();
  try {
    await fs.writeFile(tempPath, JSON.stringify(data, null, 2), 'utf8');
    await fs.rename(tempPath, filepath);
  } catch (error) {
    // Cleanup temp file on error
    try { await fs.unlink(tempPath); } catch (e) {}
    throw error;
  }
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// ========================================
// HEARTBEAT SYSTEM (Track active instances)
// ========================================

async function updateHeartbeat(instanceId) {
  await ensureTrinityDir();
  const heartbeats = await readJSON(HEARTBEAT_FILE, {});
  heartbeats[instanceId] = {
    lastSeen: new Date().toISOString(),
    computer: os.hostname(),
    platform: os.platform()
  };
  await writeJSON(HEARTBEAT_FILE, heartbeats);
}

async function getActiveInstances() {
  const heartbeats = await readJSON(HEARTBEAT_FILE, {});
  const now = Date.now();
  const activeThreshold = 5 * 60 * 1000; // 5 minutes

  return Object.entries(heartbeats)
    .filter(([id, data]) => now - new Date(data.lastSeen).getTime() < activeThreshold)
    .map(([id, data]) => ({ id, ...data }));
}

// ========================================
// TRINITY ORCHESTRATION FUNCTIONS
// ========================================

async function trinityBroadcast(message, from) {
  await ensureTrinityDir();
  const messages = await readJSON(MESSAGES_FILE);

  const broadcastMessage = {
    id: generateId(),
    type: 'broadcast',
    from: from || 'system',
    to: 'all',
    message,
    timestamp: new Date().toISOString(),
    read: false,
    computer: os.hostname()
  };

  messages.push(broadcastMessage);
  await writeJSON(MESSAGES_FILE, messages);

  if (from) await updateHeartbeat(from);

  return {
    success: true,
    messageId: broadcastMessage.id,
    message: `Broadcast sent to all instances: "${message}"`,
    sharedPath: TRINITY_DIR
  };
}

async function trinityAssignTask(task, assignedTo, priority = 'normal') {
  await ensureTrinityDir();
  const tasks = await readJSON(TASKS_FILE);

  const newTask = {
    id: generateId(),
    task,
    assignedTo,
    priority,
    status: 'assigned',
    createdAt: new Date().toISOString(),
    createdBy: os.hostname(),
    claimedBy: null,
    claimedAt: null,
    output: null,
    completedAt: null
  };

  tasks.push(newTask);
  await writeJSON(TASKS_FILE, tasks);

  await trinityBroadcast(`New task assigned to ${assignedTo}: ${task}`, 'task-coordinator');

  return {
    success: true,
    taskId: newTask.id,
    message: `Task assigned to ${assignedTo}: "${task}"`
  };
}

async function trinityClaimTask(instanceId) {
  await ensureTrinityDir();
  await updateHeartbeat(instanceId);

  const tasks = await readJSON(TASKS_FILE);
  const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };

  const availableTasks = tasks.filter(t =>
    t.status === 'assigned' &&
    (t.assignedTo === instanceId || t.assignedTo === 'any')
  );

  if (availableTasks.length === 0) {
    return { success: false, message: 'No available tasks to claim' };
  }

  availableTasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  const taskToClaim = availableTasks[0];
  taskToClaim.claimedBy = instanceId;
  taskToClaim.claimedAt = new Date().toISOString();
  taskToClaim.claimedOnComputer = os.hostname();
  taskToClaim.status = 'in-progress';

  await writeJSON(TASKS_FILE, tasks);

  return {
    success: true,
    task: taskToClaim,
    message: `Claimed task: "${taskToClaim.task}"`
  };
}

async function trinitySubmitOutput(taskId, output, instanceId) {
  await ensureTrinityDir();
  await updateHeartbeat(instanceId);

  const tasks = await readJSON(TASKS_FILE);
  const taskIndex = tasks.findIndex(t => t.id === taskId);

  if (taskIndex === -1) {
    return { success: false, message: `Task ${taskId} not found` };
  }

  tasks[taskIndex].output = output;
  tasks[taskIndex].completedBy = instanceId;
  tasks[taskIndex].completedAt = new Date().toISOString();
  tasks[taskIndex].completedOnComputer = os.hostname();
  tasks[taskIndex].status = 'completed';

  await writeJSON(TASKS_FILE, tasks);

  const outputs = await readJSON(OUTPUTS_FILE);
  outputs.push({
    taskId,
    instanceId,
    output,
    computer: os.hostname(),
    timestamp: new Date().toISOString()
  });
  await writeJSON(OUTPUTS_FILE, outputs);

  return {
    success: true,
    message: `Task ${taskId} completed and output submitted`
  };
}

async function trinityMergeOutputs(projectName) {
  await ensureTrinityDir();
  const outputs = await readJSON(OUTPUTS_FILE);
  const tasks = await readJSON(TASKS_FILE);

  if (outputs.length === 0) {
    return { success: false, message: 'No outputs to merge' };
  }

  const mergedData = {
    project: projectName || 'Trinity Project',
    generatedAt: new Date().toISOString(),
    totalTasks: tasks.length,
    completedTasks: tasks.filter(t => t.status === 'completed').length,
    outputs: outputs.map(o => {
      const task = tasks.find(t => t.id === o.taskId);
      return {
        task: task ? task.task : 'Unknown',
        instance: o.instanceId,
        computer: o.computer,
        output: o.output,
        timestamp: o.timestamp
      };
    })
  };

  const summary = {
    overview: `Trinity orchestration completed ${mergedData.completedTasks} of ${mergedData.totalTasks} tasks`,
    instances: [...new Set(outputs.map(o => o.instanceId))],
    computers: [...new Set(outputs.map(o => o.computer))],
    outputs: mergedData.outputs
  };

  return {
    success: true,
    summary,
    message: `Merged ${outputs.length} outputs from ${summary.instances.length} instances across ${summary.computers.length} computers`
  };
}

async function trinityWakeInstance(instanceId, reason) {
  await ensureTrinityDir();

  const wakeMessage = {
    id: generateId(),
    type: 'wake',
    to: instanceId,
    reason,
    timestamp: new Date().toISOString(),
    fromComputer: os.hostname()
  };

  const messages = await readJSON(MESSAGES_FILE);
  messages.push(wakeMessage);
  await writeJSON(MESSAGES_FILE, messages);

  return {
    success: true,
    message: `Wake signal sent to ${instanceId}: ${reason}`
  };
}

async function trinitySpawnCloud(taskDescription) {
  return {
    success: true,
    message: 'Cloud spawn functionality ready - requires API key configuration',
    instructions: [
      '1. Set ANTHROPIC_API_KEY environment variable',
      '2. Cloud instance will auto-register in shared .trinity folder',
      '3. Task will be auto-assigned to new instance',
      `4. Task: "${taskDescription}"`
    ]
  };
}

async function trinityStatus() {
  await ensureTrinityDir();

  const messages = await readJSON(MESSAGES_FILE);
  const tasks = await readJSON(TASKS_FILE);
  const outputs = await readJSON(OUTPUTS_FILE);
  const activeInstances = await getActiveInstances();

  return {
    status: 'Trinity system operational',
    sharedPath: TRINITY_DIR,
    thisComputer: os.hostname(),
    messages: {
      total: messages.length,
      unread: messages.filter(m => !m.read).length
    },
    tasks: {
      total: tasks.length,
      active: tasks.filter(t => t.status === 'in-progress').length,
      completed: tasks.filter(t => t.status === 'completed').length,
      pending: tasks.filter(t => t.status === 'assigned').length
    },
    outputs: { total: outputs.length },
    activeInstances
  };
}

async function trinitySendMessage(to, message, from) {
  await ensureTrinityDir();
  const messages = await readJSON(MESSAGES_FILE);

  const newMessage = {
    id: generateId(),
    from: from || 'unknown',
    to,
    message,
    timestamp: new Date().toISOString(),
    read: false,
    fromComputer: os.hostname()
  };

  messages.push(newMessage);
  await writeJSON(MESSAGES_FILE, messages);

  if (from) await updateHeartbeat(from);

  return { success: true, messageId: newMessage.id };
}

async function trinityReceiveMessages(instanceId) {
  await ensureTrinityDir();
  await updateHeartbeat(instanceId);

  const messages = await readJSON(MESSAGES_FILE);

  const instanceMessages = messages.filter(m =>
    (m.to === instanceId || m.to === 'all') && !m.read
  );

  instanceMessages.forEach(msg => {
    const index = messages.findIndex(m => m.id === msg.id);
    if (index !== -1) {
      messages[index].read = true;
      messages[index].readBy = instanceId;
      messages[index].readAt = new Date().toISOString();
    }
  });

  await writeJSON(MESSAGES_FILE, messages);

  return {
    messages: instanceMessages,
    count: instanceMessages.length
  };
}

// ========================================
// MCP SERVER SETUP
// ========================================

const server = new Server(
  { name: 'trinity-orchestration', version: '3.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'trinity_status',
        description: 'Get current status of Trinity system',
        inputSchema: { type: 'object', properties: {} }
      },
      {
        name: 'trinity_send_message',
        description: 'Send message to specific Trinity instance',
        inputSchema: {
          type: 'object',
          properties: {
            to: { type: 'string', description: 'Target instance ID' },
            message: { type: 'string', description: 'Message content' },
            from: { type: 'string', description: 'Sender instance ID' }
          },
          required: ['to', 'message']
        }
      },
      {
        name: 'trinity_receive_messages',
        description: 'Receive unread messages for this instance',
        inputSchema: {
          type: 'object',
          properties: {
            instanceId: { type: 'string', description: 'This instance ID' }
          },
          required: ['instanceId']
        }
      },
      {
        name: 'trinity_broadcast',
        description: 'Send message to ALL Trinity instances at once',
        inputSchema: {
          type: 'object',
          properties: {
            message: { type: 'string', description: 'Message to broadcast' },
            from: { type: 'string', description: 'Sender instance ID' }
          },
          required: ['message']
        }
      },
      {
        name: 'trinity_assign_task',
        description: 'Assign a task to a specific instance or "any"',
        inputSchema: {
          type: 'object',
          properties: {
            task: { type: 'string', description: 'Task description' },
            assignedTo: { type: 'string', description: 'Instance ID or "any"' },
            priority: {
              type: 'string',
              enum: ['urgent', 'high', 'normal', 'low'],
              default: 'normal'
            }
          },
          required: ['task', 'assignedTo']
        }
      },
      {
        name: 'trinity_claim_task',
        description: 'Claim an available task from the queue',
        inputSchema: {
          type: 'object',
          properties: {
            instanceId: { type: 'string', description: 'This instance ID' }
          },
          required: ['instanceId']
        }
      },
      {
        name: 'trinity_submit_output',
        description: 'Submit completed task output',
        inputSchema: {
          type: 'object',
          properties: {
            taskId: { type: 'string', description: 'Task ID' },
            output: { type: 'string', description: 'Task output/result' },
            instanceId: { type: 'string', description: 'This instance ID' }
          },
          required: ['taskId', 'output', 'instanceId']
        }
      },
      {
        name: 'trinity_merge_outputs',
        description: 'Combine all outputs into single summary',
        inputSchema: {
          type: 'object',
          properties: {
            projectName: { type: 'string', description: 'Optional project name' }
          }
        }
      },
      {
        name: 'trinity_wake_instance',
        description: 'Trigger another instance to start/wake up',
        inputSchema: {
          type: 'object',
          properties: {
            instanceId: { type: 'string', description: 'Target instance ID' },
            reason: { type: 'string', description: 'Reason for waking' }
          },
          required: ['instanceId', 'reason']
        }
      },
      {
        name: 'trinity_spawn_cloud',
        description: 'Spawn a new cloud Claude instance via API',
        inputSchema: {
          type: 'object',
          properties: {
            taskDescription: { type: 'string', description: 'Task for new instance' }
          },
          required: ['taskDescription']
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'trinity_status':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityStatus(), null, 2) }] };
      case 'trinity_send_message':
        return { content: [{ type: 'text', text: JSON.stringify(await trinitySendMessage(args.to, args.message, args.from), null, 2) }] };
      case 'trinity_receive_messages':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityReceiveMessages(args.instanceId), null, 2) }] };
      case 'trinity_broadcast':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityBroadcast(args.message, args.from), null, 2) }] };
      case 'trinity_assign_task':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityAssignTask(args.task, args.assignedTo, args.priority), null, 2) }] };
      case 'trinity_claim_task':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityClaimTask(args.instanceId), null, 2) }] };
      case 'trinity_submit_output':
        return { content: [{ type: 'text', text: JSON.stringify(await trinitySubmitOutput(args.taskId, args.output, args.instanceId), null, 2) }] };
      case 'trinity_merge_outputs':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityMergeOutputs(args.projectName), null, 2) }] };
      case 'trinity_wake_instance':
        return { content: [{ type: 'text', text: JSON.stringify(await trinityWakeInstance(args.instanceId, args.reason), null, 2) }] };
      case 'trinity_spawn_cloud':
        return { content: [{ type: 'text', text: JSON.stringify(await trinitySpawnCloud(args.taskDescription), null, 2) }] };
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true
    };
  }
});

async function main() {
  await ensureTrinityDir();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`Trinity MCP Server v3.0 running - Shared path: ${TRINITY_DIR}`);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
