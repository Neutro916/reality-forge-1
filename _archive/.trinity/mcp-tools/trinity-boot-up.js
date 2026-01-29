#!/usr/bin/env node

/**
 * TRINITY BOOT-UP PROTOCOL
 * 
 * Initializes a Trinity instance on startup:
 * - Restores previous state
 * - Registers instance in network
 * - Checks for pending tasks
 * - Announces availability
 * - Loads pattern theory framework
 * - Initializes seven domain structure
 * 
 * Usage: node trinity-boot-up.js <instanceId> [role]
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const INSTANCES_FILE = path.join(TRINITY_DIR, 'instances.json');
const STATE_FILE = path.join(TRINITY_DIR, 'state.json');
const MESSAGES_FILE = path.join(TRINITY_DIR, 'messages.json');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const PATTERN_THEORY_FILE = path.join(TRINITY_DIR, 'pattern-theory.json');
const SEVEN_DOMAINS_FILE = path.join(TRINITY_DIR, 'seven-domains.json');

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
 * Initialize Seven Domains structure
 */
async function initSevenDomains() {
  const domains = {
    version: '1.0.0',
    initialized: new Date().toISOString(),
    domains: [
      {
        id: 1,
        name: 'Technology',
        description: 'AI, quantum computing, blockchain, emerging tech',
        clusters: ['AI-ML', 'Quantum', 'Blockchain'],
        status: 'initialized'
      },
      {
        id: 2,
        name: 'Science',
        description: 'Physics, biology, chemistry, fundamental research',
        clusters: ['Physics', 'Biology', 'Chemistry'],
        status: 'initialized'
      },
      {
        id: 3,
        name: 'Business',
        description: 'Markets, strategy, economics, organizational systems',
        clusters: ['Markets', 'Strategy', 'Ecosystems'],
        status: 'initialized'
      },
      {
        id: 4,
        name: 'Philosophy',
        description: 'Ethics, epistemology, reasoning, decision theory',
        clusters: ['Ethics', 'Epistemology', 'Applied'],
        status: 'initialized'
      },
      {
        id: 5,
        name: 'Engineering',
        description: 'Architecture, tools, systems, best practices',
        clusters: ['Architecture', 'Tools', 'Practices'],
        status: 'initialized'
      },
      {
        id: 6,
        name: 'Creative',
        description: 'Design, content, innovation, synthesis',
        clusters: ['Design', 'Content', 'Innovation'],
        status: 'initialized'
      },
      {
        id: 7,
        name: 'Integration',
        description: 'Cross-domain patterns, meta-theory, unified understanding',
        clusters: ['Cross-Domain', 'Meta-Patterns', 'Synthesis'],
        status: 'initialized'
      }
    ]
  };
  
  await writeJSON(SEVEN_DOMAINS_FILE, domains);
  return domains;
}

/**
 * Initialize Pattern Theory framework
 */
async function initPatternTheory() {
  const patternTheory = {
    version: '1.0.0',
    initialized: new Date().toISOString(),
    framework: {
      name: 'Trinity Pattern Theory',
      description: 'Universal patterns across seven domains',
      principles: [
        'Emergence: Complex systems arise from simple rules',
        'Recursion: Patterns repeat at different scales',
        'Convergence: Multiple paths lead to similar solutions',
        'Synthesis: Integration creates new understanding',
        'Iteration: Refinement through feedback loops',
        'Distribution: Parallel processing and coordination',
        'Coherence: Unified output from diverse inputs'
      ]
    },
    patterns: {
      structural: {
        trinity: '3 → 1 convergence pattern',
        hierarchy: 'Multi-level synthesis',
        network: 'Distributed coordination',
        feedback: 'Continuous improvement'
      },
      operational: {
        autonomous: 'Self-directed task execution',
        collaborative: 'Multi-agent coordination',
        adaptive: 'Dynamic response to conditions',
        iterative: 'Progressive refinement'
      },
      cognitive: {
        analysis: 'Break down into components',
        synthesis: 'Combine into unified whole',
        pattern_matching: 'Recognize recurring structures',
        abstraction: 'Extract essential principles'
      }
    },
    applications: {
      task_distribution: 'Assign work across instances',
      output_convergence: 'Merge results hierarchically',
      knowledge_synthesis: 'Build integrated understanding',
      continuous_learning: 'Improve through iteration'
    }
  };
  
  await writeJSON(PATTERN_THEORY_FILE, patternTheory);
  return patternTheory;
}

/**
 * Register instance in Trinity network
 */
async function registerInstance(instanceId, role, metadata = {}) {
  const instances = await readJSON(INSTANCES_FILE, { active: [], history: [] });
  
  // Check if already registered
  const existing = instances.active.find(i => i.id === instanceId);
  if (existing) {
    console.log(`⚠️  Instance ${instanceId} already active`);
    existing.lastBootUp = new Date().toISOString();
    existing.bootCount = (existing.bootCount || 0) + 1;
    await writeJSON(INSTANCES_FILE, instances);
    return existing;
  }
  
  // Register new instance
  const instance = {
    id: instanceId,
    role: role || 'worker',
    status: 'online',
    registered: new Date().toISOString(),
    lastBootUp: new Date().toISOString(),
    bootCount: 1,
    hostname: os.hostname(),
    platform: os.platform(),
    metadata
  };
  
  instances.active.push(instance);
  await writeJSON(INSTANCES_FILE, instances);
  
  console.log(`✅ Registered: ${instanceId} (${role})`);
  return instance;
}

/**
 * Restore previous state
 */
async function restoreState(instanceId) {
  const state = await readJSON(STATE_FILE, { instances: {} });
  const instanceState = state.instances[instanceId];
  
  if (instanceState) {
    console.log(`📂 Restored state from: ${instanceState.lastShutdown || 'N/A'}`);
    console.log(`   Tasks completed: ${instanceState.tasksCompleted || 0}`);
    console.log(`   Last active: ${instanceState.lastActive || 'N/A'}`);
    return instanceState;
  }
  
  console.log(`📂 No previous state found (first boot)`);
  return null;
}

/**
 * Check for pending work
 */
async function checkPendingWork(instanceId) {
  const tasks = await readJSON(TASKS_FILE, []);
  
  // Find tasks assigned to this instance
  const myTasks = tasks.filter(t => 
    (t.assignedTo === instanceId || t.assignedTo === 'any') && 
    t.status === 'assigned'
  );
  
  // Find unread messages
  const messages = await readJSON(MESSAGES_FILE, []);
  const unreadMessages = messages.filter(m => 
    (m.to === instanceId || m.to === 'all') && !m.read
  );
  
  console.log(`📋 Pending work:`);
  console.log(`   Tasks: ${myTasks.length}`);
  console.log(`   Unread messages: ${unreadMessages.length}`);
  
  return {
    tasks: myTasks,
    messages: unreadMessages
  };
}

/**
 * Announce availability to network
 */
async function announceAvailability(instanceId, role) {
  const messages = await readJSON(MESSAGES_FILE, []);
  
  const announcement = {
    id: generateId(),
    type: 'boot-announcement',
    from: instanceId,
    to: 'all',
    message: `${instanceId} (${role}) is now online and available`,
    timestamp: new Date().toISOString(),
    read: false
  };
  
  messages.push(announcement);
  await writeJSON(MESSAGES_FILE, messages);
  
  console.log(`📢 Announced availability to network`);
}

/**
 * Initialize workspace
 */
async function initWorkspace(instanceId, role) {
  console.log(`\n🔱 TRINITY BOOT-UP PROTOCOL`);
  console.log(`═══════════════════════════════════════════`);
  console.log(`Instance: ${instanceId}`);
  console.log(`Role: ${role}`);
  console.log(`Host: ${os.hostname()}`);
  console.log(`Platform: ${os.platform()}`);
  console.log(`Time: ${new Date().toLocaleString()}`);
  console.log(`═══════════════════════════════════════════\n`);
  
  // Ensure Trinity directory exists
  await fs.mkdir(TRINITY_DIR, { recursive: true });
  console.log(`✅ Trinity directory: ${TRINITY_DIR}`);
  
  // Initialize Seven Domains
  const domains = await initSevenDomains();
  console.log(`✅ Seven Domains initialized`);
  
  // Initialize Pattern Theory
  const patternTheory = await initPatternTheory();
  console.log(`✅ Pattern Theory loaded`);
  
  // Register instance
  const instance = await registerInstance(instanceId, role);
  
  // Restore previous state
  const previousState = await restoreState(instanceId);
  
  // Check for pending work
  const pending = await checkPendingWork(instanceId);
  
  // Announce availability
  await announceAvailability(instanceId, role);
  
  console.log(`\n✅ Boot-up complete!`);
  console.log(`🔱 ${instanceId} is online and ready\n`);
  
  return {
    instance,
    previousState,
    pending,
    domains,
    patternTheory
  };
}

/**
 * Display boot summary
 */
async function displayBootSummary(instanceId) {
  const instances = await readJSON(INSTANCES_FILE, { active: [] });
  const domains = await readJSON(SEVEN_DOMAINS_FILE, { domains: [] });
  const tasks = await readJSON(TASKS_FILE, []);
  
  console.log(`📊 TRINITY NETWORK STATUS:`);
  console.log(`   Active instances: ${instances.active.length}`);
  instances.active.forEach(inst => {
    const marker = inst.id === instanceId ? '👉' : '  ';
    console.log(`   ${marker} ${inst.id} (${inst.role}) - ${inst.status}`);
  });
  
  console.log(`\n📚 SEVEN DOMAINS:`);
  domains.domains?.forEach(d => {
    console.log(`   ${d.id}. ${d.name} - ${d.clusters.length} clusters`);
  });
  
  console.log(`\n📋 TASK QUEUE:`);
  const assigned = tasks.filter(t => t.status === 'assigned').length;
  const inProgress = tasks.filter(t => t.status === 'in-progress').length;
  const completed = tasks.filter(t => t.status === 'completed').length;
  console.log(`   Assigned: ${assigned} | In Progress: ${inProgress} | Completed: ${completed}`);
  
  console.log(`\n🎯 READY TO WORK\n`);
}

/**
 * Main boot sequence
 */
async function main() {
  const instanceId = process.argv[2] || `instance-${os.hostname()}`;
  const role = process.argv[3] || 'worker';
  
  try {
    const bootResult = await initWorkspace(instanceId, role);
    await displayBootSummary(instanceId);
    
    // If there's pending work, notify
    if (bootResult.pending.tasks.length > 0) {
      console.log(`⚡ ${bootResult.pending.tasks.length} tasks waiting!`);
      console.log(`   Start auto-wake to process: node trinity-auto-wake.js ${instanceId}`);
    }
    
    if (bootResult.pending.messages.length > 0) {
      console.log(`📬 ${bootResult.pending.messages.length} unread messages!`);
      console.log(`   Check messages: Use trinity_receive_messages`);
    }
    
    console.log(`\n🔱 Trinity instance initialized successfully\n`);
    
  } catch (error) {
    console.error(`❌ Boot-up failed: ${error.message}`);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

// Export for use as module
module.exports = {
  initWorkspace,
  registerInstance,
  restoreState,
  checkPendingWork,
  announceAvailability,
  initSevenDomains,
  initPatternTheory
};
