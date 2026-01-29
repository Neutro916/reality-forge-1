#!/usr/bin/env node

/**
 * TRINITY BOOT-DOWN PROTOCOL
 * 
 * Gracefully shuts down a Trinity instance:
 * - Saves current state
 * - Completes pending tasks (with timeout)
 * - Notifies other instances
 * - Unregisters from network
 * - Preserves work in progress
 * 
 * Usage: node trinity-boot-down.js <instanceId> [--force] [--timeout=30]
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const INSTANCES_FILE = path.join(TRINITY_DIR, 'instances.json');
const STATE_FILE = path.join(TRINITY_DIR, 'state.json');
const MESSAGES_FILE = path.join(TRINITY_DIR, 'messages.json');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');

async function readJSON(filepath, fallback = {}) {
  try {
    const data = await fs.readFile(filepath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return fallback;
  }
}

async function writeJSON(filepath, data) {
  await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf8');
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Save current state
 */
async function saveState(instanceId, metrics = {}) {
  const state = await readJSON(STATE_FILE, { instances: {} });
  
  state.instances[instanceId] = {
    lastShutdown: new Date().toISOString(),
    lastActive: new Date().toISOString(),
    tasksCompleted: metrics.tasksCompleted || 0,
    tasksInProgress: metrics.tasksInProgress || 0,
    messagesProcessed: metrics.messagesProcessed || 0,
    uptime: metrics.uptime || 0,
    status: 'shutdown-clean'
  };
  
  await writeJSON(STATE_FILE, state);
  console.log(`💾 State saved for ${instanceId}`);
}

/**
 * Handle in-progress tasks
 */
async function handleInProgressTasks(instanceId, force = false) {
  const tasks = await readJSON(TASKS_FILE, []);
  
  // Find tasks this instance was working on
  const myInProgressTasks = tasks.filter(t => 
    t.status === 'in-progress' && t.claimedBy === instanceId
  );
  
  if (myInProgressTasks.length === 0) {
    console.log(`✅ No in-progress tasks to handle`);
    return { handled: 0, reassigned: 0 };
  }
  
  console.log(`📋 Found ${myInProgressTasks.length} in-progress tasks`);
  
  if (force) {
    // Force shutdown: reassign tasks
    console.log(`⚠️  Force shutdown: reassigning tasks to queue`);
    
    myInProgressTasks.forEach(task => {
      task.status = 'assigned';
      task.claimedBy = null;
      task.claimedAt = null;
      task.notes = (task.notes || []);
      task.notes.push({
        timestamp: new Date().toISOString(),
        message: `Task reassigned due to force shutdown of ${instanceId}`
      });
    });
    
    await writeJSON(TASKS_FILE, tasks);
    console.log(`✅ ${myInProgressTasks.length} tasks reassigned`);
    
    return { handled: myInProgressTasks.length, reassigned: myInProgressTasks.length };
  } else {
    // Graceful: keep tasks as in-progress
    console.log(`⏸️  Graceful shutdown: preserving in-progress state`);
    console.log(`   Tasks will resume on next boot-up`);
    
    return { handled: myInProgressTasks.length, reassigned: 0 };
  }
}

/**
 * Announce shutdown to network
 */
async function announceShutdown(instanceId, reason = 'normal') {
  const messages = await readJSON(MESSAGES_FILE, []);
  
  const announcement = {
    id: generateId(),
    type: 'shutdown-announcement',
    from: instanceId,
    to: 'all',
    message: `${instanceId} is shutting down (reason: ${reason})`,
    timestamp: new Date().toISOString(),
    read: false
  };
  
  messages.push(announcement);
  await writeJSON(MESSAGES_FILE, messages);
  
  console.log(`📢 Announced shutdown to network`);
}

/**
 * Unregister from network
 */
async function unregisterInstance(instanceId) {
  const instances = await readJSON(INSTANCES_FILE, { active: [], history: [] });
  
  // Find this instance
  const instanceIndex = instances.active.findIndex(i => i.id === instanceId);
  
  if (instanceIndex === -1) {
    console.log(`⚠️  Instance ${instanceId} not found in active list`);
    return;
  }
  
  // Move to history
  const instance = instances.active[instanceIndex];
  instance.status = 'offline';
  instance.lastShutdown = new Date().toISOString();
  
  instances.history = instances.history || [];
  instances.history.push(instance);
  
  // Remove from active
  instances.active.splice(instanceIndex, 1);
  
  await writeJSON(INSTANCES_FILE, instances);
  console.log(`✅ Unregistered ${instanceId} from active instances`);
}

/**
 * Calculate metrics
 */
async function calculateMetrics(instanceId, startTime) {
  const tasks = await readJSON(TASKS_FILE, []);
  const outputs = await readJSON(OUTPUTS_FILE, []);
  const messages = await readJSON(MESSAGES_FILE, []);
  
  // Count tasks this instance completed
  const tasksCompleted = tasks.filter(t => 
    t.status === 'completed' && t.completedBy === instanceId
  ).length;
  
  // Count tasks still in progress
  const tasksInProgress = tasks.filter(t => 
    t.status === 'in-progress' && t.claimedBy === instanceId
  ).length;
  
  // Count outputs
  const outputsCreated = outputs.filter(o => 
    o.instanceId === instanceId || o.instanceId === `cloud-${instanceId}`
  ).length;
  
  // Count messages processed (rough estimate)
  const messagesProcessed = messages.filter(m => 
    m.from === instanceId
  ).length;
  
  // Calculate uptime
  const uptime = startTime ? Date.now() - startTime : 0;
  
  return {
    tasksCompleted,
    tasksInProgress,
    outputsCreated,
    messagesProcessed,
    uptime
  };
}

/**
 * Display shutdown summary
 */
function displayShutdownSummary(instanceId, metrics, taskHandling) {
  console.log(`\n📊 SHUTDOWN SUMMARY:`);
  console.log(`   Instance: ${instanceId}`);
  console.log(`   Tasks completed: ${metrics.tasksCompleted}`);
  console.log(`   Tasks in progress: ${metrics.tasksInProgress}`);
  console.log(`   Tasks reassigned: ${taskHandling.reassigned}`);
  console.log(`   Outputs created: ${metrics.outputsCreated}`);
  console.log(`   Messages sent: ${metrics.messagesProcessed}`);
  console.log(`   Uptime: ${(metrics.uptime / 1000 / 60).toFixed(2)} minutes`);
  console.log(``);
}

/**
 * Main shutdown sequence
 */
async function shutdown(instanceId, options = {}) {
  const { force = false, timeout = 30, reason = 'normal', startTime = null } = options;
  
  console.log(`\n🔱 TRINITY BOOT-DOWN PROTOCOL`);
  console.log(`═══════════════════════════════════════════`);
  console.log(`Instance: ${instanceId}`);
  console.log(`Mode: ${force ? 'FORCE' : 'GRACEFUL'}`);
  console.log(`Timeout: ${timeout}s`);
  console.log(`Time: ${new Date().toLocaleString()}`);
  console.log(`═══════════════════════════════════════════\n`);
  
  try {
    // Calculate metrics
    console.log(`📊 Calculating metrics...`);
    const metrics = await calculateMetrics(instanceId, startTime);
    
    // Handle in-progress tasks
    console.log(`📋 Handling in-progress tasks...`);
    const taskHandling = await handleInProgressTasks(instanceId, force);
    
    // Save state
    console.log(`💾 Saving state...`);
    await saveState(instanceId, metrics);
    
    // Announce shutdown
    console.log(`📢 Announcing shutdown...`);
    await announceShutdown(instanceId, reason);
    
    // Unregister from network
    console.log(`📤 Unregistering from network...`);
    await unregisterInstance(instanceId);
    
    // Display summary
    displayShutdownSummary(instanceId, metrics, taskHandling);
    
    console.log(`✅ Shutdown complete!`);
    console.log(`🔱 ${instanceId} is offline\n`);
    
    return {
      success: true,
      metrics,
      taskHandling
    };
    
  } catch (error) {
    console.error(`❌ Shutdown error: ${error.message}`);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Emergency shutdown (for signal handlers)
 */
async function emergencyShutdown(instanceId) {
  console.log(`\n🚨 EMERGENCY SHUTDOWN INITIATED`);
  
  await shutdown(instanceId, {
    force: true,
    reason: 'emergency',
    timeout: 5
  });
  
  process.exit(0);
}

/**
 * Main
 */
async function main() {
  const instanceId = process.argv[2];
  
  if (!instanceId) {
    console.error('Usage: node trinity-boot-down.js <instanceId> [--force] [--timeout=30]');
    process.exit(1);
  }
  
  const force = process.argv.includes('--force');
  const timeoutArg = process.argv.find(arg => arg.startsWith('--timeout='));
  const timeout = timeoutArg ? parseInt(timeoutArg.split('=')[1]) : 30;
  
  const result = await shutdown(instanceId, { force, timeout });
  
  if (!result.success) {
    process.exit(1);
  }
}

// Handle signals for emergency shutdown
if (require.main === module) {
  const instanceId = process.argv[2];
  
  if (instanceId) {
    process.on('SIGINT', () => emergencyShutdown(instanceId));
    process.on('SIGTERM', () => emergencyShutdown(instanceId));
  }
  
  main();
}

// Export for use as module
module.exports = {
  shutdown,
  emergencyShutdown,
  saveState,
  handleInProgressTasks,
  announceShutdown,
  unregisterInstance,
  calculateMetrics
};
