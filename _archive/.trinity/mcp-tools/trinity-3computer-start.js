#!/usr/bin/env node

/**
 * TRINITY 3-COMPUTER STARTUP
 * 
 * Quick start for proving Trinity works with 3 local computers
 * 
 * Usage: node trinity-3computer-start.js <computer-number> [role]
 * 
 * Computer 1: Terminal Claude - Coordinator
 * Computer 2: Desktop Claude - Synthesizer  
 * Computer 3: Third Instance - Worker
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const TRINITY_DIR = path.join(require('os').homedir(), '.trinity');

// Computer configurations
const COMPUTERS = {
  1: {
    instanceId: 'claude-terminal',
    role: 'coordinator',
    description: 'Terminal Claude - Task Coordinator'
  },
  2: {
    instanceId: 'claude-desktop',
    role: 'synthesizer',
    description: 'Desktop Claude - Output Synthesizer'
  },
  3: {
    instanceId: 'claude-worker',
    role: 'worker',
    description: 'Worker Instance - Task Executor'
  }
};

async function startup(computerNum) {
  const config = COMPUTERS[computerNum];
  
  if (!config) {
    console.error(`Invalid computer number. Use 1, 2, or 3`);
    process.exit(1);
  }
  
  console.log(`\n🔱 TRINITY 3-COMPUTER STARTUP`);
  console.log(`═══════════════════════════════════════════`);
  console.log(`Computer: #${computerNum}`);
  console.log(`Instance: ${config.instanceId}`);
  console.log(`Role: ${config.role}`);
  console.log(`Description: ${config.description}`);
  console.log(`═══════════════════════════════════════════\n`);
  
  try {
    // Ensure Trinity directory exists
    if (!fs.existsSync(TRINITY_DIR)) {
      fs.mkdirSync(TRINITY_DIR, { recursive: true });
      console.log(`✅ Created Trinity directory: ${TRINITY_DIR}`);
    }
    
    // Run workspace setup
    console.log(`🎨 Setting up workspace...`);
    execSync(`node trinity-workspace-setup.js ${config.instanceId} ${config.role}`, {
      stdio: 'inherit'
    });
    
    // Run boot-up
    console.log(`\n🚀 Booting up instance...`);
    execSync(`node trinity-boot-up.js ${config.instanceId} ${config.role}`, {
      stdio: 'inherit'
    });
    
    console.log(`\n✅ STARTUP COMPLETE!`);
    console.log(`\n🎯 Next Steps:`);
    
    if (computerNum === 1) {
      console.log(`   You are the COORDINATOR.`);
      console.log(`   Your job: Assign tasks to the trinity cluster`);
      console.log(`   Command: Use trinity_assign_task`);
      console.log(`   Wait for computers 2 and 3 to come online`);
    } else if (computerNum === 2) {
      console.log(`   You are the SYNTHESIZER.`);
      console.log(`   Your job: Merge outputs from all 3 workers`);
      console.log(`   Command: Use trinity_merge_outputs`);
      console.log(`   Wait for work from coordinator`);
    } else {
      console.log(`   You are a WORKER.`);
      console.log(`   Your job: Claim and execute tasks`);
      console.log(`   Command: Use trinity_claim_task`);
      console.log(`   Or start auto-wake: node trinity-auto-wake.js ${config.instanceId}`);
    }
    
    console.log(`\n📊 Check status: Use trinity_status`);
    console.log(`📬 Check messages: Use trinity_receive_messages`);
    console.log(`🔱 Trinity network ready!\n`);
    
  } catch (error) {
    console.error(`❌ Startup failed: ${error.message}`);
    process.exit(1);
  }
}

// Main
const computerNum = parseInt(process.argv[2]);

if (!computerNum || isNaN(computerNum)) {
  console.log(`\n🔱 TRINITY 3-COMPUTER STARTUP\n`);
  console.log(`Usage: node trinity-3computer-start.js <computer-number>\n`);
  console.log(`Computer 1: Terminal Claude (Coordinator)`);
  console.log(`Computer 2: Desktop Claude (Synthesizer)`);
  console.log(`Computer 3: Worker Instance (Executor)\n`);
  console.log(`Example: node trinity-3computer-start.js 1\n`);
  process.exit(1);
}

startup(computerNum);
