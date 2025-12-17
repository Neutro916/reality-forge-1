#!/usr/bin/env node

/**
 * TRINITY DEMO - Sample Task Generator
 * 
 * This script creates sample tasks to test the Trinity system
 * Use this to verify that autonomous workers can claim and execute tasks
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');

// Sample tasks for testing
const sampleTasks = [
  {
    task: "Summarize the current state of AI research in 3 bullet points",
    assignedTo: "any",
    priority: "high",
    description: "Quick research task to test autonomous execution"
  },
  {
    task: "Generate a haiku about autonomous systems",
    assignedTo: "any",
    priority: "normal",
    description: "Creative task to test output submission"
  },
  {
    task: "Calculate 2^10 and explain the result",
    assignedTo: "any",
    priority: "normal",
    description: "Math task to test task claiming"
  },
  {
    task: "List 5 benefits of multi-agent coordination",
    assignedTo: "any",
    priority: "low",
    description: "Analytical task to test priority ordering"
  },
  {
    task: "Write a 2-sentence description of the Trinity system",
    assignedTo: "any",
    priority: "high",
    description: "Documentation task to test parallel execution"
  }
];

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

async function readJSON(filepath, fallback = []) {
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

async function createSampleTasks() {
  console.log('🔱 Trinity Demo - Sample Task Generator\n');
  
  // Ensure Trinity directory exists
  try {
    await fs.mkdir(TRINITY_DIR, { recursive: true });
  } catch (error) {
    // Directory might already exist
  }
  
  // Read existing tasks
  const tasks = await readJSON(TASKS_FILE);
  
  console.log(`📋 Current tasks in queue: ${tasks.length}\n`);
  console.log('📝 Creating sample tasks...\n');
  
  // Create sample tasks
  let count = 0;
  for (const sample of sampleTasks) {
    const newTask = {
      id: generateId(),
      task: sample.task,
      assignedTo: sample.assignedTo,
      priority: sample.priority,
      status: 'assigned',
      createdAt: new Date().toISOString(),
      claimedBy: null,
      claimedAt: null,
      output: null,
      completedAt: null,
      metadata: {
        description: sample.description,
        demo: true
      }
    };
    
    tasks.push(newTask);
    count++;
    
    console.log(`✅ Created task ${count}: "${sample.task}"`);
    console.log(`   Priority: ${sample.priority} | Assigned to: ${sample.assignedTo}`);
    console.log('');
  }
  
  // Save tasks
  await writeJSON(TASKS_FILE, tasks);
  
  console.log('═'.repeat(60));
  console.log(`\n✨ Created ${count} sample tasks!`);
  console.log(`📊 Total tasks in queue: ${tasks.length}\n`);
  
  console.log('🎯 Next Steps:\n');
  console.log('1. Start autonomous workers:');
  console.log('   node trinity-auto-wake.js claude-worker-1');
  console.log('   node trinity-auto-wake.js claude-worker-2');
  console.log('');
  console.log('2. Watch them automatically:');
  console.log('   - Claim tasks from queue');
  console.log('   - Execute the work');
  console.log('   - Submit outputs');
  console.log('');
  console.log('3. Check results:');
  console.log('   - View outputs.json for completed work');
  console.log('   - Use trinity_merge_outputs to combine');
  console.log('');
  console.log('4. Monitor via workspace:');
  console.log('   - Open TRINITY_WORKSPACE.html');
  console.log('   - See real-time status updates');
  console.log('');
  console.log('🔥 Ready to test autonomous coordination! 🔱\n');
}

async function clearCompletedTasks() {
  console.log('🗑️  Clearing completed tasks...\n');
  
  const tasks = await readJSON(TASKS_FILE);
  const activeTasks = tasks.filter(t => t.status !== 'completed');
  const removedCount = tasks.length - activeTasks.length;
  
  await writeJSON(TASKS_FILE, activeTasks);
  
  console.log(`✅ Removed ${removedCount} completed task(s)`);
  console.log(`📊 Active tasks remaining: ${activeTasks.length}\n`);
}

async function showTaskQueue() {
  console.log('📋 Current Task Queue:\n');
  
  const tasks = await readJSON(TASKS_FILE);
  
  if (tasks.length === 0) {
    console.log('   (empty)\n');
    return;
  }
  
  const statusCounts = {
    assigned: tasks.filter(t => t.status === 'assigned').length,
    'in-progress': tasks.filter(t => t.status === 'in-progress').length,
    completed: tasks.filter(t => t.status === 'completed').length
  };
  
  console.log(`   Total: ${tasks.length}`);
  console.log(`   - Assigned: ${statusCounts.assigned}`);
  console.log(`   - In Progress: ${statusCounts['in-progress']}`);
  console.log(`   - Completed: ${statusCounts.completed}`);
  console.log('');
  
  if (statusCounts.assigned > 0) {
    console.log('📌 Available tasks:');
    tasks.filter(t => t.status === 'assigned').forEach((task, i) => {
      console.log(`   ${i + 1}. [${task.priority.toUpperCase()}] ${task.task}`);
    });
    console.log('');
  }
}

// Main menu
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'create':
      await createSampleTasks();
      break;
    case 'clear':
      await clearCompletedTasks();
      break;
    case 'show':
      await showTaskQueue();
      break;
    default:
      console.log('🔱 Trinity Demo - Task Generator\n');
      console.log('Usage:');
      console.log('  node trinity-demo.js create  - Create sample tasks');
      console.log('  node trinity-demo.js show    - Show current task queue');
      console.log('  node trinity-demo.js clear   - Clear completed tasks');
      console.log('');
      await showTaskQueue();
  }
}

main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
