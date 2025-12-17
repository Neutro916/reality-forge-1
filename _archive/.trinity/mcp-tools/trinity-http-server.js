#!/usr/bin/env node

/**
 * TRINITY HTTP SERVER - Real-time Multi-Computer Communication
 *
 * BACKUP for when cloud sync has lag. Run this on Computer 1 (main),
 * other computers connect to it via HTTP.
 *
 * Usage:
 *   node trinity-http-server.js [port]
 *   Default port: 3333
 *
 * Endpoints:
 *   GET  /status              - System status
 *   GET  /messages/:instanceId - Get messages for instance
 *   POST /message             - Send message
 *   POST /broadcast           - Broadcast to all
 *   GET  /tasks/:instanceId   - Get tasks for instance
 *   POST /task                - Assign task
 *   POST /task/:id/claim      - Claim task
 *   POST /task/:id/complete   - Complete task
 *   GET  /outputs             - Get all outputs
 *   POST /wake/:instanceId    - Wake an instance
 */

const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const url = require('url');

const PORT = process.argv[2] || process.env.TRINITY_HTTP_PORT || 3333;

// Use same shared path as MCP server
function getTrinityPath() {
  if (process.env.TRINITY_PATH) return process.env.TRINITY_PATH;
  const homeDir = os.homedir();
  const sharedPaths = [
    path.join(homeDir, 'OneDrive', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, 'Google Drive', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, 'Dropbox', 'Trinity_Shared', '.trinity'),
    path.join(homeDir, '.trinity')
  ];
  for (const p of sharedPaths) {
    try { require('fs').accessSync(p); return p; } catch (e) { continue; }
  }
  return path.join(homeDir, 'OneDrive', 'Trinity_Shared', '.trinity');
}

const TRINITY_DIR = getTrinityPath();
const MESSAGES_FILE = path.join(TRINITY_DIR, 'messages.json');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');
const HEARTBEAT_FILE = path.join(TRINITY_DIR, 'heartbeats.json');

// Helper functions
async function readJSON(filepath, fallback = []) {
  try {
    return JSON.parse(await fs.readFile(filepath, 'utf8'));
  } catch (e) {
    return fallback;
  }
}

async function writeJSON(filepath, data) {
  await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf8');
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

async function updateHeartbeat(instanceId) {
  const heartbeats = await readJSON(HEARTBEAT_FILE, {});
  heartbeats[instanceId] = {
    lastSeen: new Date().toISOString(),
    computer: os.hostname(),
    platform: os.platform(),
    via: 'http'
  };
  await writeJSON(HEARTBEAT_FILE, heartbeats);
}

// Parse JSON body from request
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        resolve({});
      }
    });
    req.on('error', reject);
  });
}

// Send JSON response
function sendJSON(res, data, status = 200) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data, null, 2));
}

// Request handler
async function handleRequest(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    return res.end();
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  try {
    // GET /status
    if (req.method === 'GET' && pathname === '/status') {
      const messages = await readJSON(MESSAGES_FILE);
      const tasks = await readJSON(TASKS_FILE);
      const outputs = await readJSON(OUTPUTS_FILE);
      const heartbeats = await readJSON(HEARTBEAT_FILE, {});

      return sendJSON(res, {
        status: 'Trinity HTTP Server operational',
        server: os.hostname(),
        port: PORT,
        sharedPath: TRINITY_DIR,
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
        activeInstances: Object.entries(heartbeats)
          .filter(([id, d]) => Date.now() - new Date(d.lastSeen).getTime() < 300000)
          .map(([id, d]) => ({ id, ...d }))
      });
    }

    // GET /messages/:instanceId
    if (req.method === 'GET' && pathname.startsWith('/messages/')) {
      const instanceId = pathname.split('/')[2];
      await updateHeartbeat(instanceId);

      const messages = await readJSON(MESSAGES_FILE);
      const instanceMessages = messages.filter(m =>
        (m.to === instanceId || m.to === 'all') && !m.read
      );

      // Mark as read
      instanceMessages.forEach(msg => {
        const idx = messages.findIndex(m => m.id === msg.id);
        if (idx !== -1) {
          messages[idx].read = true;
          messages[idx].readBy = instanceId;
          messages[idx].readAt = new Date().toISOString();
        }
      });
      await writeJSON(MESSAGES_FILE, messages);

      return sendJSON(res, { messages: instanceMessages, count: instanceMessages.length });
    }

    // POST /message
    if (req.method === 'POST' && pathname === '/message') {
      const body = await parseBody(req);
      const { to, message, from } = body;

      if (!to || !message) {
        return sendJSON(res, { error: 'Missing to or message' }, 400);
      }

      const messages = await readJSON(MESSAGES_FILE);
      const newMessage = {
        id: generateId(),
        from: from || 'http-client',
        to,
        message,
        timestamp: new Date().toISOString(),
        read: false,
        fromComputer: os.hostname(),
        via: 'http'
      };
      messages.push(newMessage);
      await writeJSON(MESSAGES_FILE, messages);

      if (from) await updateHeartbeat(from);

      return sendJSON(res, { success: true, messageId: newMessage.id });
    }

    // POST /broadcast
    if (req.method === 'POST' && pathname === '/broadcast') {
      const body = await parseBody(req);
      const { message, from } = body;

      if (!message) {
        return sendJSON(res, { error: 'Missing message' }, 400);
      }

      const messages = await readJSON(MESSAGES_FILE);
      const broadcastMessage = {
        id: generateId(),
        type: 'broadcast',
        from: from || 'http-client',
        to: 'all',
        message,
        timestamp: new Date().toISOString(),
        read: false,
        computer: os.hostname(),
        via: 'http'
      };
      messages.push(broadcastMessage);
      await writeJSON(MESSAGES_FILE, messages);

      if (from) await updateHeartbeat(from);

      return sendJSON(res, { success: true, messageId: broadcastMessage.id });
    }

    // GET /tasks/:instanceId
    if (req.method === 'GET' && pathname.startsWith('/tasks/')) {
      const instanceId = pathname.split('/')[2];
      await updateHeartbeat(instanceId);

      const tasks = await readJSON(TASKS_FILE);
      const availableTasks = tasks.filter(t =>
        t.status === 'assigned' &&
        (t.assignedTo === instanceId || t.assignedTo === 'any')
      );

      return sendJSON(res, { tasks: availableTasks, count: availableTasks.length });
    }

    // POST /task
    if (req.method === 'POST' && pathname === '/task') {
      const body = await parseBody(req);
      const { task, assignedTo, priority } = body;

      if (!task || !assignedTo) {
        return sendJSON(res, { error: 'Missing task or assignedTo' }, 400);
      }

      const tasks = await readJSON(TASKS_FILE);
      const newTask = {
        id: generateId(),
        task,
        assignedTo,
        priority: priority || 'normal',
        status: 'assigned',
        createdAt: new Date().toISOString(),
        createdBy: os.hostname(),
        via: 'http'
      };
      tasks.push(newTask);
      await writeJSON(TASKS_FILE, tasks);

      return sendJSON(res, { success: true, taskId: newTask.id });
    }

    // POST /task/:id/claim
    if (req.method === 'POST' && pathname.match(/^\/task\/[^/]+\/claim$/)) {
      const taskId = pathname.split('/')[2];
      const body = await parseBody(req);
      const { instanceId } = body;

      if (!instanceId) {
        return sendJSON(res, { error: 'Missing instanceId' }, 400);
      }

      await updateHeartbeat(instanceId);

      const tasks = await readJSON(TASKS_FILE);
      const taskIndex = tasks.findIndex(t => t.id === taskId);

      if (taskIndex === -1) {
        return sendJSON(res, { error: 'Task not found' }, 404);
      }

      if (tasks[taskIndex].status !== 'assigned') {
        return sendJSON(res, { error: 'Task already claimed or completed' }, 400);
      }

      tasks[taskIndex].claimedBy = instanceId;
      tasks[taskIndex].claimedAt = new Date().toISOString();
      tasks[taskIndex].claimedOnComputer = os.hostname();
      tasks[taskIndex].status = 'in-progress';

      await writeJSON(TASKS_FILE, tasks);

      return sendJSON(res, { success: true, task: tasks[taskIndex] });
    }

    // POST /task/:id/complete
    if (req.method === 'POST' && pathname.match(/^\/task\/[^/]+\/complete$/)) {
      const taskId = pathname.split('/')[2];
      const body = await parseBody(req);
      const { instanceId, output } = body;

      if (!instanceId || !output) {
        return sendJSON(res, { error: 'Missing instanceId or output' }, 400);
      }

      await updateHeartbeat(instanceId);

      const tasks = await readJSON(TASKS_FILE);
      const taskIndex = tasks.findIndex(t => t.id === taskId);

      if (taskIndex === -1) {
        return sendJSON(res, { error: 'Task not found' }, 404);
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
        timestamp: new Date().toISOString(),
        via: 'http'
      });
      await writeJSON(OUTPUTS_FILE, outputs);

      return sendJSON(res, { success: true });
    }

    // GET /outputs
    if (req.method === 'GET' && pathname === '/outputs') {
      const outputs = await readJSON(OUTPUTS_FILE);
      const tasks = await readJSON(TASKS_FILE);

      const merged = outputs.map(o => {
        const task = tasks.find(t => t.id === o.taskId);
        return {
          task: task ? task.task : 'Unknown',
          instance: o.instanceId,
          computer: o.computer,
          output: o.output,
          timestamp: o.timestamp
        };
      });

      return sendJSON(res, {
        outputs: merged,
        count: outputs.length,
        instances: [...new Set(outputs.map(o => o.instanceId))],
        computers: [...new Set(outputs.map(o => o.computer))]
      });
    }

    // POST /wake/:instanceId
    if (req.method === 'POST' && pathname.startsWith('/wake/')) {
      const instanceId = pathname.split('/')[2];
      const body = await parseBody(req);
      const { reason } = body;

      const messages = await readJSON(MESSAGES_FILE);
      messages.push({
        id: generateId(),
        type: 'wake',
        to: instanceId,
        reason: reason || 'Wake up request',
        timestamp: new Date().toISOString(),
        fromComputer: os.hostname(),
        via: 'http'
      });
      await writeJSON(MESSAGES_FILE, messages);

      return sendJSON(res, { success: true, message: `Wake signal sent to ${instanceId}` });
    }

    // 404 for unknown routes
    return sendJSON(res, { error: 'Not found', availableEndpoints: [
      'GET /status',
      'GET /messages/:instanceId',
      'POST /message { to, message, from }',
      'POST /broadcast { message, from }',
      'GET /tasks/:instanceId',
      'POST /task { task, assignedTo, priority }',
      'POST /task/:id/claim { instanceId }',
      'POST /task/:id/complete { instanceId, output }',
      'GET /outputs',
      'POST /wake/:instanceId { reason }'
    ]}, 404);

  } catch (error) {
    console.error('Error:', error);
    return sendJSON(res, { error: error.message }, 500);
  }
}

// Start server
const server = http.createServer(handleRequest);

server.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║         TRINITY HTTP SERVER v1.0 - RUNNING                   ║
╠══════════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                            ║
║  Host:        0.0.0.0 (all interfaces)                       ║
║  Shared Path: ${TRINITY_DIR.substring(0, 45).padEnd(45)}║
║  Computer:    ${os.hostname().padEnd(45)}║
╠══════════════════════════════════════════════════════════════╣
║  ENDPOINTS:                                                  ║
║    GET  /status              - System status                 ║
║    GET  /messages/:id        - Get messages                  ║
║    POST /message             - Send message                  ║
║    POST /broadcast           - Broadcast to all              ║
║    GET  /tasks/:id           - Get tasks                     ║
║    POST /task                - Assign task                   ║
║    POST /task/:id/claim      - Claim task                    ║
║    POST /task/:id/complete   - Complete task                 ║
║    GET  /outputs             - Get all outputs               ║
║    POST /wake/:id            - Wake instance                 ║
╠══════════════════════════════════════════════════════════════╣
║  OTHER COMPUTERS CONNECT VIA:                                ║
║    http://${os.hostname()}:${PORT}/status                             ║
║    Or use this computer's IP address                         ║
╚══════════════════════════════════════════════════════════════╝
  `);
});
