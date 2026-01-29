#!/usr/bin/env node

/**
 * TRINITY MASTER ORCHESTRATOR
 * 
 * THE BRAIN - Coordinates the entire $5000 credit burn operation
 * - Generates tasks via task generator
 * - Spawns cloud instances via cloud spawner
 * - Tracks usage via account manager
 * - Executes hierarchical convergence
 * - Monitors progress
 * - Generates final output
 * 
 * Usage:
 *   node trinity-master-orchestrator.js init       - Initialize everything
 *   node trinity-master-orchestrator.js execute    - Execute full burn
 *   node trinity-master-orchestrator.js monitor    - Real-time monitoring
 *   node trinity-master-orchestrator.js converge   - Run all convergences
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const ORCHESTRATION_STATE_FILE = path.join(TRINITY_DIR, 'orchestration-state.json');

// Import other Trinity modules
const { spawnCloudInstance, spawnTrinityCluster, batchSpawn, getCloudStatus } = require('./trinity-cloud-spawner.js');
const { convergeCluster, convergeMeta, convergeUltimate, executeConvergence } = require('./trinity-hierarchical-merge.js');
const { getNextAccount, getOptimalAccount, trackUsage, getStatus: getAccountStatus } = require('./trinity-account-manager.js');
const { generateMasterManifest, TASK_TEMPLATES } = require('./trinity-task-generator.js');

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

// ========================================
// ORCHESTRATION STATE MANAGEMENT
// ========================================

async function initOrchestration() {
  console.log('🚀 INITIALIZING TRINITY ORCHESTRATION\n');
  
  const state = {
    initialized: new Date().toISOString(),
    phase: 'init',
    status: 'initializing',
    stages: {
      accountSetup: false,
      taskGeneration: false,
      clusterCreation: false,
      execution: false,
      convergence: false,
      complete: false
    },
    metrics: {
      totalBudget: 5000,
      budgetUsed: 0,
      tasksGenerated: 0,
      tasksCompleted: 0,
      clustersCreated: 0,
      convergencesCompleted: 0
    }
  };
  
  await writeJSON(ORCHESTRATION_STATE_FILE, state);
  
  console.log('✅ Orchestration state initialized');
  console.log(`📁 State file: ${ORCHESTRATION_STATE_FILE}\n`);
  
  return state;
}

async function updateState(updates) {
  const state = await readJSON(ORCHESTRATION_STATE_FILE);
  Object.assign(state, updates);
  state.lastUpdated = new Date().toISOString();
  await writeJSON(ORCHESTRATION_STATE_FILE, state);
  return state;
}

async function getState() {
  return await readJSON(ORCHESTRATION_STATE_FILE);
}

// ========================================
// ORCHESTRATION PHASES
// ========================================

/**
 * PHASE 1: Setup
 * - Verify accounts
 * - Generate task manifest
 * - Create cluster structure
 */
async function phaseSetup() {
  console.log('\n🔧 PHASE 1: SETUP\n');
  
  // Check account status
  console.log('Checking account pool...');
  const accountStatus = await getAccountStatus();
  
  if (accountStatus.accounts.active === 0) {
    console.error('❌ No active accounts! Run account-manager setup first.');
    process.exit(1);
  }
  
  console.log(`✅ Found ${accountStatus.accounts.active} active accounts`);
  console.log(`💰 Total credits: $${accountStatus.credits.total}`);
  console.log('');
  
  // Generate task manifest
  console.log('Generating task manifest...');
  const manifest = await generateMasterManifest();
  
  console.log(`✅ Generated ${manifest.totalTasks} tasks`);
  console.log(`💰 Estimated cost: $${manifest.summary.estimatedTotalCost}`);
  console.log('');
  
  // Update state
  await updateState({
    phase: 'setup-complete',
    'stages.accountSetup': true,
    'stages.taskGeneration': true,
    'metrics.tasksGenerated': manifest.totalTasks
  });
  
  return {
    accounts: accountStatus,
    manifest
  };
}

/**
 * PHASE 2: Execute Clusters
 * - Spawn cloud instances for each cluster
 * - 3 workers per cluster
 * - Track usage
 */
async function phaseExecuteClusters(dryRun = false) {
  console.log('\n⚡ PHASE 2: EXECUTE CLUSTERS\n');
  
  if (dryRun) {
    console.log('🔍 DRY RUN MODE - No actual API calls\n');
  }
  
  // Get all domains
  const domains = Object.keys(TASK_TEMPLATES);
  const results = [];
  
  for (const domainKey of domains) {
    const domain = TASK_TEMPLATES[domainKey];
    console.log(`\n🌟 Domain: ${domain.name}`);
    console.log(`📦 Clusters: ${domain.clusters.length}\n`);
    
    for (const cluster of domain.clusters) {
      console.log(`  🔱 Spawning Trinity Cluster: ${cluster.name}`);
      
      if (dryRun) {
        console.log(`    ⏩ Skipping (dry run)`);
        console.log(`    Would spawn 3 workers for:`);
        cluster.tasks.forEach((task, i) => {
          console.log(`      ${i + 1}. ${task.substring(0, 60)}...`);
        });
        continue;
      }
      
      try {
        // Get account with most credits
        const account = await getOptimalAccount();
        console.log(`    🔑 Using account: ${account.name}`);
        
        // Spawn trinity cluster
        const clusterResult = await spawnTrinityCluster(
          cluster.tasks,
          account.apiKey,
          cluster.name,
          { maxTokens: 8192 }
        );
        
        // Track usage
        for (const instance of clusterResult.instances) {
          await trackUsage(account.name, instance.cost, {
            cluster: cluster.name,
            domain: domainKey,
            instanceId: instance.id
          });
        }
        
        results.push({
          domain: domainKey,
          cluster: cluster.name,
          success: true,
          cost: clusterResult.totalCost,
          instances: clusterResult.instances.length
        });
        
        console.log(`    ✅ Cluster complete - Cost: $${clusterResult.totalCost.toFixed(4)}`);
        
        // Brief delay to avoid rate limits
        await new Promise(resolve => setTimeout(resolve, 2000));
        
      } catch (error) {
        console.error(`    ❌ Cluster failed: ${error.message}`);
        results.push({
          domain: domainKey,
          cluster: cluster.name,
          success: false,
          error: error.message
        });
      }
    }
  }
  
  // Summary
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => r.error).length;
  const totalCost = results.filter(r => r.cost).reduce((sum, r) => sum + r.cost, 0);
  
  console.log('\n📊 CLUSTER EXECUTION SUMMARY:');
  console.log(`   Successful: ${successful}`);
  console.log(`   Failed: ${failed}`);
  console.log(`   Total cost: $${totalCost.toFixed(2)}`);
  
  // Update state
  await updateState({
    phase: 'execution-complete',
    'stages.execution': true,
    'metrics.clustersCreated': successful,
    'metrics.budgetUsed': totalCost
  });
  
  return results;
}

/**
 * PHASE 3: Convergence
 * - Level 1: Cluster convergences (3→1)
 * - Level 2: Meta convergences (clusters→1)
 * - Level 3: Ultimate convergence (all→1)
 */
async function phaseConvergence(apiKey) {
  console.log('\n🔗 PHASE 3: HIERARCHICAL CONVERGENCE\n');
  
  const convergenceResults = {
    level1: [],
    level2: [],
    level3: null
  };
  
  // LEVEL 1: Converge each cluster (3→1)
  console.log('📊 LEVEL 1: Cluster Convergences\n');
  
  const domains = Object.keys(TASK_TEMPLATES);
  const clusterNames = [];
  
  for (const domainKey of domains) {
    const domain = TASK_TEMPLATES[domainKey];
    
    for (const cluster of domain.clusters) {
      console.log(`  Converging ${cluster.name}...`);
      
      try {
        const convergence = await convergeCluster(cluster.name);
        
        // Execute convergence
        const result = await executeConvergence(convergence.id, apiKey);
        
        convergenceResults.level1.push({
          cluster: cluster.name,
          convergenceId: convergence.id,
          success: true,
          cost: result.cost
        });
        
        clusterNames.push(cluster.name);
        
        console.log(`    ✅ Complete - Cost: $${result.cost.toFixed(4)}`);
        
      } catch (error) {
        console.error(`    ❌ Failed: ${error.message}`);
        convergenceResults.level1.push({
          cluster: cluster.name,
          success: false,
          error: error.message
        });
      }
    }
  }
  
  // LEVEL 2: Meta convergences (group clusters by domain)
  console.log('\n📊 LEVEL 2: Meta Convergences\n');
  
  for (const domainKey of domains) {
    const domain = TASK_TEMPLATES[domainKey];
    const domainClusters = domain.clusters.map(c => c.name);
    
    console.log(`  Meta-converging ${domain.name}...`);
    
    try {
      const metaConvergence = await convergeMeta(domain.name, domainClusters);
      const result = await executeConvergence(metaConvergence.id, apiKey);
      
      convergenceResults.level2.push({
        meta: domain.name,
        convergenceId: metaConvergence.id,
        success: true,
        cost: result.cost
      });
      
      console.log(`    ✅ Complete - Cost: $${result.cost.toFixed(4)}`);
      
    } catch (error) {
      console.error(`    ❌ Failed: ${error.message}`);
      convergenceResults.level2.push({
        meta: domain.name,
        success: false,
        error: error.message
      });
    }
  }
  
  // LEVEL 3: Ultimate convergence (all metas → 1)
  console.log('\n📊 LEVEL 3: Ultimate Master Convergence\n');
  
  const metaNames = domains.map(key => TASK_TEMPLATES[key].name);
  
  try {
    const ultimateConvergence = await convergeUltimate('Trinity Knowledge Compendium', metaNames);
    const result = await executeConvergence(ultimateConvergence.id, apiKey);
    
    convergenceResults.level3 = {
      convergenceId: ultimateConvergence.id,
      success: true,
      cost: result.cost,
      output: result.output
    };
    
    console.log(`✅ ULTIMATE CONVERGENCE COMPLETE - Cost: $${result.cost.toFixed(4)}`);
    
    // Save master output
    const masterOutputPath = path.join(TRINITY_DIR, 'MASTER_OUTPUT.md');
    await fs.writeFile(masterOutputPath, result.output, 'utf8');
    console.log(`\n📄 Master output saved to: ${masterOutputPath}`);
    
  } catch (error) {
    console.error(`❌ Ultimate convergence failed: ${error.message}`);
    convergenceResults.level3 = {
      success: false,
      error: error.message
    };
  }
  
  // Summary
  const level1Success = convergenceResults.level1.filter(r => r.success).length;
  const level2Success = convergenceResults.level2.filter(r => r.success).length;
  const totalCost = [
    ...convergenceResults.level1.filter(r => r.cost),
    ...convergenceResults.level2.filter(r => r.cost),
    ...(convergenceResults.level3?.cost ? [convergenceResults.level3] : [])
  ].reduce((sum, r) => sum + r.cost, 0);
  
  console.log('\n📊 CONVERGENCE SUMMARY:');
  console.log(`   Level 1 (Cluster): ${level1Success}/${convergenceResults.level1.length}`);
  console.log(`   Level 2 (Meta): ${level2Success}/${convergenceResults.level2.length}`);
  console.log(`   Level 3 (Ultimate): ${convergenceResults.level3?.success ? '✅' : '❌'}`);
  console.log(`   Total cost: $${totalCost.toFixed(2)}`);
  
  // Update state
  await updateState({
    phase: 'convergence-complete',
    'stages.convergence': true,
    'stages.complete': convergenceResults.level3?.success || false,
    'metrics.convergencesCompleted': level1Success + level2Success + (convergenceResults.level3?.success ? 1 : 0)
  });
  
  return convergenceResults;
}

/**
 * FULL ORCHESTRATION
 * Run the entire $5000 burn from start to finish
 */
async function fullOrchestration(options = {}) {
  const { dryRun = false, skipSetup = false, skipExecution = false, skipConvergence = false } = options;
  
  console.log('🌌 TRINITY MASTER ORCHESTRATION - $5000 CREDIT BURN');
  console.log('═'.repeat(60));
  console.log('');
  
  const startTime = Date.now();
  
  // Initialize
  await initOrchestration();
  
  // Phase 1: Setup
  let setupResults = null;
  if (!skipSetup) {
    setupResults = await phaseSetup();
  }
  
  // Phase 2: Execute clusters
  let executionResults = null;
  if (!skipExecution) {
    executionResults = await phaseExecuteClusters(dryRun);
  }
  
  // Phase 3: Convergence
  let convergenceResults = null;
  if (!skipConvergence && !dryRun) {
    // Get API key from best account
    const account = await getOptimalAccount();
    convergenceResults = await phaseConvergence(account.apiKey);
  }
  
  // Final summary
  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000 / 60).toFixed(2);
  
  const accountStatus = await getAccountStatus();
  
  console.log('\n\n🎉 ORCHESTRATION COMPLETE!');
  console.log('═'.repeat(60));
  console.log(`\n⏱️  Total time: ${duration} minutes`);
  console.log(`💰 Budget used: $${accountStatus.credits.used.toFixed(2)} / $${accountStatus.credits.total}`);
  console.log(`📊 Budget remaining: $${accountStatus.credits.remaining.toFixed(2)} (${accountStatus.credits.percentUsed}% used)`);
  console.log(`✅ Tasks completed: ${accountStatus.tasks.completed}`);
  
  if (convergenceResults?.level3?.success) {
    console.log('\n📄 MASTER OUTPUT: MASTER_OUTPUT.md');
    console.log('   The Trinity Knowledge Compendium is complete!');
  }
  
  console.log('\n🔱 Trinity orchestration successful. Universe auto-completed.');
}

/**
 * Monitor orchestration in real-time
 */
async function monitor() {
  console.log('📊 REAL-TIME ORCHESTRATION MONITOR\n');
  console.log('Refreshing every 5 seconds... (Ctrl+C to stop)\n');
  
  const showStatus = async () => {
    console.clear();
    console.log('🔱 TRINITY ORCHESTRATION MONITOR');
    console.log('═'.repeat(60));
    console.log(`Updated: ${new Date().toLocaleString()}\n`);
    
    // Get state
    const state = await getState();
    const accountStatus = await getAccountStatus();
    const cloudStatus = await getCloudStatus();
    
    // Show phase
    console.log(`Phase: ${state.phase || 'Not started'}`);
    console.log(`Status: ${state.status || 'Unknown'}\n`);
    
    // Show stages
    console.log('Stages:');
    if (state.stages) {
      Object.entries(state.stages).forEach(([stage, complete]) => {
        console.log(`  ${complete ? '✅' : '⏳'} ${stage}`);
      });
    }
    console.log('');
    
    // Show metrics
    console.log('Metrics:');
    if (state.metrics) {
      console.log(`  Budget: $${state.metrics.budgetUsed || 0} / $${state.metrics.totalBudget}`);
      console.log(`  Tasks: ${state.metrics.tasksCompleted || 0} / ${state.metrics.tasksGenerated || 0}`);
      console.log(`  Clusters: ${state.metrics.clustersCreated || 0}`);
      console.log(`  Convergences: ${state.metrics.convergencesCompleted || 0}`);
    }
    console.log('');
    
    // Show accounts
    console.log('Accounts:');
    console.log(`  Active: ${accountStatus.accounts.active}`);
    console.log(`  Credits remaining: $${accountStatus.credits.remaining.toFixed(2)}`);
    console.log(`  Tasks completed: ${accountStatus.tasks.completed}`);
    console.log('');
    
    // Show cloud instances
    console.log('Cloud Instances:');
    console.log(`  Total: ${cloudStatus.total}`);
    console.log(`  Completed: ${cloudStatus.completed}`);
    console.log(`  Failed: ${cloudStatus.failed}`);
    console.log(`  Total cost: $${cloudStatus.totalCost.toFixed(2)}`);
    console.log('');
    
    console.log('Press Ctrl+C to stop monitoring');
  };
  
  // Show immediately
  await showStatus();
  
  // Then every 5 seconds
  const interval = setInterval(showStatus, 5000);
  
  // Handle Ctrl+C
  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log('\n\nMonitoring stopped');
    process.exit(0);
  });
}

// ========================================
// CLI
// ========================================

async function main() {
  const command = process.argv[2];
  
  if (!command) {
    console.log('🔱 Trinity Master Orchestrator\n');
    console.log('Commands:');
    console.log('  init          - Initialize orchestration');
    console.log('  setup         - Run Phase 1: Setup');
    console.log('  execute       - Run Phase 2: Execute clusters');
    console.log('  converge      - Run Phase 3: Convergence');
    console.log('  full          - Run complete orchestration (all phases)');
    console.log('  monitor       - Real-time monitoring');
    console.log('  status        - Show current status');
    console.log('\nOptions:');
    console.log('  --dry-run     - Simulate without actual API calls');
    process.exit(0);
  }
  
  const dryRun = process.argv.includes('--dry-run');
  
  if (command === 'init') {
    await initOrchestration();
  }
  else if (command === 'setup') {
    await phaseSetup();
  }
  else if (command === 'execute') {
    await phaseExecuteClusters(dryRun);
  }
  else if (command === 'converge') {
    const account = await getOptimalAccount();
    await phaseConvergence(account.apiKey);
  }
  else if (command === 'full') {
    await fullOrchestration({ dryRun });
  }
  else if (command === 'monitor') {
    await monitor();
  }
  else if (command === 'status') {
    const state = await getState();
    console.log('\n📊 Orchestration Status:\n');
    console.log(JSON.stringify(state, null, 2));
  }
  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Export
module.exports = {
  initOrchestration,
  phaseSetup,
  phaseExecuteClusters,
  phaseConvergence,
  fullOrchestration,
  monitor
};

// Run CLI
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
