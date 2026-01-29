#!/usr/bin/env node

/**
 * TRINITY AUTO-WAKE PROTOCOL
 * 
 * This script enables autonomous operation:
 * 1. Checks for assigned tasks
 * 2. Claims available work
 * 3. Executes tasks
 * 4. Submits outputs
 * 5. Wakes other instances if needed
 * 
 * Usage: node trinity-auto-wake.js [instanceId] [interval]
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const MESSAGES_FILE = path.join(TRINITY_DIR, 'messages.json');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');

// Get instance ID from command line or use default
const INSTANCE_ID = process.argv[2] || `claude-${Date.now()}`;
const CHECK_INTERVAL = parseInt(process.argv[3] || '10000'); // 10 seconds default

console.log(`🔱 Trinity Auto-Wake Protocol`);
console.log(`📍 Instance: ${INSTANCE_ID}`);
console.log(`⏱️  Check interval: ${CHECK_INTERVAL}ms`);
console.log(`📁 Trinity folder: ${TRINITY_DIR}`);
console.log('');

// Read JSON file
async function readJSON(filepath, fallback = []) {
  try {
    const data = await fs.readFile(filepath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return fallback;
  }
}

// Write JSON file
async function writeJSON(filepath, data) {
  await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf8');
}

// Check for messages
async function checkMessages() {
  const messages = await readJSON(MESSAGES_FILE);
  const myMessages = messages.filter(m => 
    (m.to === INSTANCE_ID || m.to === 'all') && !m.read
  );
  
  if (myMessages.length > 0) {
    console.log(`📬 ${myMessages.length} new message(s):`);
    myMessages.forEach(msg => {
      console.log(`   From: ${msg.from} | ${msg.message}`);
      
      // Mark as read
      const index = messages.findIndex(m => m.id === msg.id);
      if (index !== -1) {
        messages[index].read = true;
      }
    });
    
    await writeJSON(MESSAGES_FILE, messages);
  }
  
  return myMessages;
}

// Check for tasks
async function checkTasks() {
  const tasks = await readJSON(TASKS_FILE);
  
  // Find tasks assigned to this instance or 'any'
  const availableTasks = tasks.filter(t => 
    t.status === 'assigned' && 
    (t.assignedTo === INSTANCE_ID || t.assignedTo === 'any')
  );
  
  if (availableTasks.length > 0) {
    console.log(`📋 ${availableTasks.length} available task(s)`);
    return availableTasks;
  }
  
  return [];
}

// Claim a task
async function claimTask(taskId) {
  const tasks = await readJSON(TASKS_FILE);
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    console.log(`❌ Task ${taskId} not found`);
    return null;
  }
  
  // Check if still available
  if (tasks[taskIndex].status !== 'assigned') {
    console.log(`⚠️  Task ${taskId} already claimed`);
    return null;
  }
  
  // Claim it
  tasks[taskIndex].claimedBy = INSTANCE_ID;
  tasks[taskIndex].claimedAt = new Date().toISOString();
  tasks[taskIndex].status = 'in-progress';
  
  await writeJSON(TASKS_FILE, tasks);
  
  console.log(`✅ Claimed task: "${tasks[taskIndex].task}"`);
  return tasks[taskIndex];
}

// Submit output for a task
async function submitOutput(taskId, output) {
  const tasks = await readJSON(TASKS_FILE);
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    console.log(`❌ Task ${taskId} not found`);
    return false;
  }
  
  tasks[taskIndex].output = output;
  tasks[taskIndex].completedBy = INSTANCE_ID;
  tasks[taskIndex].completedAt = new Date().toISOString();
  tasks[taskIndex].status = 'completed';
  
  await writeJSON(TASKS_FILE, tasks);
  
  // Save to outputs
  const outputs = await readJSON(OUTPUTS_FILE);
  outputs.push({
    taskId,
    instanceId: INSTANCE_ID,
    output,
    timestamp: new Date().toISOString()
  });
  await writeJSON(OUTPUTS_FILE, outputs);
  
  console.log(`✅ Submitted output for task ${taskId}`);
  return true;
}

// Simulate task execution (in real use, Claude would actually do the work)
async function executeTask(task) {
  console.log(`🔧 Executing: "${task.task}"`);
  
  // In a real scenario, this would be where Claude actually performs the task
  // For this protocol, we'll simulate work
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const output = {
    task: task.task,
    result: `Task completed by ${INSTANCE_ID}`,
    timestamp: new Date().toISOString(),
    note: 'This is a simulated result - in production, Claude would execute the actual task'
  };
  
  return output;
}

// Wake other instances if there are unclaimed tasks
async function wakeOthersIfNeeded() {
  const tasks = await readJSON(TASKS_FILE);
  const unclaimedTasks = tasks.filter(t => t.status === 'assigned');
  
  if (unclaimedTasks.length > 0) {
    console.log(`⏰ ${unclaimedTasks.length} unclaimed task(s) - checking if others need wake-up`);
    
    // Send wake messages to other instances
    const messages = await readJSON(MESSAGES_FILE);
    const otherInstances = ['claude-code-main', 'claude-desktop', 'claude-cloud-1', 'claude-cloud-2']
      .filter(id => id !== INSTANCE_ID);
    
    for (const otherId of otherInstances) {
      messages.push({
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'wake',
        from: INSTANCE_ID,
        to: otherId,
        message: `Wake up! ${unclaimedTasks.length} unclaimed task(s) available`,
        timestamp: new Date().toISOString(),
        read: false
      });
    }
    
    await writeJSON(MESSAGES_FILE, messages);
    console.log(`📢 Sent wake-up calls to other instances`);
  }
}

// Main autonomous loop
async function autonomousLoop() {
  console.log('🔄 Checking for work...\n');
  
  try {
    // 1. Check messages
    const messages = await checkMessages();
    
    // 2. Check for tasks
    const availableTasks = await checkTasks();
    
    if (availableTasks.length > 0) {
      // Sort by priority
      const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
      availableTasks.sort((a, b) => 
        priorityOrder[a.priority] - priorityOrder[b.priority]
      );
      
      // Claim and execute the highest priority task
      const taskToClaim = availableTasks[0];
      const claimedTask = await claimTask(taskToClaim.id);
      
      if (claimedTask) {
        // Execute the task
        const output = await executeTask(claimedTask);
        
        // Submit output
        await submitOutput(claimedTask.id, JSON.stringify(output, null, 2));
        
        // Wake others if more tasks remain
        await wakeOthersIfNeeded();
      }
    } else {
      console.log('💤 No tasks available\n');
    }
    
  } catch (error) {
    console.error('❌ Error in autonomous loop:', error.message);
  }
}

// Status check
async function showStatus() {
  const tasks = await readJSON(TASKS_FILE);
  const messages = await readJSON(MESSAGES_FILE);
  const outputs = await readJSON(OUTPUTS_FILE);
  
  console.log('📊 Status:');
  console.log(`   Tasks: ${tasks.length} total`);
  console.log(`   - Assigned: ${tasks.filter(t => t.status === 'assigned').length}`);
  console.log(`   - In Progress: ${tasks.filter(t => t.status === 'in-progress').length}`);
  console.log(`   - Completed: ${tasks.filter(t => t.status === 'completed').length}`);
  console.log(`   Messages: ${messages.length} total`);
  console.log(`   Outputs: ${outputs.length} total`);
  console.log('');
}

// Start the protocol
async function start() {
  console.log('🚀 Starting autonomous work protocol...\n');
  
  // Initial status
  await showStatus();
  
  // Run immediately once
  await autonomousLoop();
  
  // Then run on interval
  setInterval(async () => {
    await autonomousLoop();
    await showStatus();
  }, CHECK_INTERVAL);
  
  console.log(`✅ Autonomous mode active - checking every ${CHECK_INTERVAL}ms`);
  console.log('Press Ctrl+C to stop\n');
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down autonomous protocol...');
  console.log(`📊 Instance ${INSTANCE_ID} going offline`);
  process.exit(0);
});

// Start
start().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
