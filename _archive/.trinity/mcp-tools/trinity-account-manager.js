#!/usr/bin/env node

/**
 * TRINITY ACCOUNT POOL MANAGER
 * 
 * Manages multiple Anthropic API keys (5 accounts × $1000 = $5000)
 * - Round-robin key rotation
 * - Credit tracking per account
 * - Usage monitoring
 * - Auto-rotation on rate limits
 * 
 * Usage:
 *   node trinity-account-manager.js add <name> <apiKey> <initialCredits>
 *   node trinity-account-manager.js list
 *   node trinity-account-manager.js next
 *   node trinity-account-manager.js track <accountName> <cost>
 *   node trinity-account-manager.js status
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const ACCOUNTS_FILE = path.join(TRINITY_DIR, 'accounts.json');
const USAGE_LOG_FILE = path.join(TRINITY_DIR, 'usage-log.json');

// Read/write JSON helpers
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

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Add an account to the pool
 */
async function addAccount(name, apiKey, initialCredits = 1000) {
  console.log(`➕ Adding account: ${name}`);
  
  const accounts = await readJSON(ACCOUNTS_FILE);
  
  // Check if account already exists
  const existing = accounts.find(a => a.name === name);
  if (existing) {
    console.error(`❌ Account "${name}" already exists`);
    process.exit(1);
  }
  
  // Validate API key format (basic check)
  if (!apiKey.startsWith('sk-ant-')) {
    console.warn('⚠️  Warning: API key format looks incorrect (should start with sk-ant-)');
  }
  
  const account = {
    id: generateId(),
    name,
    apiKey,
    initialCredits,
    creditsRemaining: initialCredits,
    creditsUsed: 0,
    tasksCompleted: 0,
    status: 'active',
    addedAt: new Date().toISOString(),
    lastUsed: null
  };
  
  accounts.push(account);
  await writeJSON(ACCOUNTS_FILE, accounts);
  
  console.log(`✅ Account added successfully`);
  console.log(`   Credits: $${initialCredits}`);
  console.log(`   Status: ${account.status}`);
  
  return account;
}

/**
 * Remove an account from the pool
 */
async function removeAccount(name) {
  console.log(`🗑️  Removing account: ${name}`);
  
  const accounts = await readJSON(ACCOUNTS_FILE);
  const filtered = accounts.filter(a => a.name !== name);
  
  if (filtered.length === accounts.length) {
    console.error(`❌ Account "${name}" not found`);
    process.exit(1);
  }
  
  await writeJSON(ACCOUNTS_FILE, filtered);
  console.log(`✅ Account removed`);
}

/**
 * List all accounts
 */
async function listAccounts() {
  const accounts = await readJSON(ACCOUNTS_FILE);
  
  if (accounts.length === 0) {
    console.log('📭 No accounts configured');
    return;
  }
  
  console.log(`\n📋 Account Pool (${accounts.length} accounts):\n`);
  
  accounts.forEach((account, idx) => {
    const percentUsed = ((account.creditsUsed / account.initialCredits) * 100).toFixed(1);
    const status = account.status === 'active' ? '✅' : '🔴';
    
    console.log(`${idx + 1}. ${status} ${account.name}`);
    console.log(`   API Key: ${account.apiKey.substring(0, 15)}...`);
    console.log(`   Credits: $${account.creditsRemaining.toFixed(2)} / $${account.initialCredits} (${percentUsed}% used)`);
    console.log(`   Tasks: ${account.tasksCompleted}`);
    console.log(`   Status: ${account.status}`);
    if (account.lastUsed) {
      console.log(`   Last used: ${new Date(account.lastUsed).toLocaleString()}`);
    }
    console.log('');
  });
  
  // Summary stats
  const totalInitial = accounts.reduce((sum, a) => sum + a.initialCredits, 0);
  const totalUsed = accounts.reduce((sum, a) => sum + a.creditsUsed, 0);
  const totalRemaining = accounts.reduce((sum, a) => sum + a.creditsRemaining, 0);
  const totalTasks = accounts.reduce((sum, a) => sum + a.tasksCompleted, 0);
  const activeAccounts = accounts.filter(a => a.status === 'active').length;
  
  console.log('📊 Summary:');
  console.log(`   Total credits: $${totalInitial}`);
  console.log(`   Used: $${totalUsed.toFixed(2)} (${((totalUsed/totalInitial)*100).toFixed(1)}%)`);
  console.log(`   Remaining: $${totalRemaining.toFixed(2)}`);
  console.log(`   Tasks completed: ${totalTasks}`);
  console.log(`   Active accounts: ${activeAccounts}/${accounts.length}`);
  console.log('');
}

/**
 * Get next available account (round-robin)
 */
async function getNextAccount() {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const activeAccounts = accounts.filter(a => a.status === 'active' && a.creditsRemaining > 0);
  
  if (activeAccounts.length === 0) {
    throw new Error('No active accounts with remaining credits');
  }
  
  // Sort by last used (null first, then oldest)
  activeAccounts.sort((a, b) => {
    if (!a.lastUsed) return -1;
    if (!b.lastUsed) return 1;
    return new Date(a.lastUsed) - new Date(b.lastUsed);
  });
  
  const account = activeAccounts[0];
  
  console.log(`🔑 Next account: ${account.name}`);
  console.log(`   Credits remaining: $${account.creditsRemaining.toFixed(2)}`);
  console.log(`   API Key: ${account.apiKey.substring(0, 15)}...`);
  
  return account;
}

/**
 * Track usage for an account
 */
async function trackUsage(accountName, cost, details = {}) {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const account = accounts.find(a => a.name === accountName);
  
  if (!account) {
    throw new Error(`Account not found: ${accountName}`);
  }
  
  // Update account
  account.creditsUsed += cost;
  account.creditsRemaining -= cost;
  account.tasksCompleted += 1;
  account.lastUsed = new Date().toISOString();
  
  // Check if depleted
  if (account.creditsRemaining <= 0) {
    account.status = 'depleted';
    console.log(`⚠️  Account "${accountName}" is now depleted`);
  }
  
  await writeJSON(ACCOUNTS_FILE, accounts);
  
  // Log usage
  const usageLog = await readJSON(USAGE_LOG_FILE);
  usageLog.push({
    id: generateId(),
    accountName,
    cost,
    timestamp: new Date().toISOString(),
    details
  });
  await writeJSON(USAGE_LOG_FILE, usageLog);
  
  console.log(`✅ Usage tracked for ${accountName}`);
  console.log(`   Cost: $${cost.toFixed(4)}`);
  console.log(`   Remaining: $${account.creditsRemaining.toFixed(2)}`);
  
  return account;
}

/**
 * Get account by name
 */
async function getAccount(name) {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const account = accounts.find(a => a.name === name);
  
  if (!account) {
    throw new Error(`Account not found: ${name}`);
  }
  
  return account;
}

/**
 * Get comprehensive status
 */
async function getStatus() {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const usageLog = await readJSON(USAGE_LOG_FILE);
  
  const totalInitial = accounts.reduce((sum, a) => sum + a.initialCredits, 0);
  const totalUsed = accounts.reduce((sum, a) => sum + a.creditsUsed, 0);
  const totalRemaining = accounts.reduce((sum, a) => sum + a.creditsRemaining, 0);
  const totalTasks = accounts.reduce((sum, a) => sum + a.tasksCompleted, 0);
  const activeAccounts = accounts.filter(a => a.status === 'active').length;
  const depletedAccounts = accounts.filter(a => a.status === 'depleted').length;
  
  // Calculate burn rate
  const recentUsage = usageLog.slice(-100); // Last 100 tasks
  const avgCostPerTask = recentUsage.length > 0 
    ? recentUsage.reduce((sum, u) => sum + u.cost, 0) / recentUsage.length
    : 0;
  
  // Estimate time to depletion
  const tasksRemaining = avgCostPerTask > 0 ? Math.floor(totalRemaining / avgCostPerTask) : 0;
  
  const status = {
    accounts: {
      total: accounts.length,
      active: activeAccounts,
      depleted: depletedAccounts
    },
    credits: {
      total: totalInitial,
      used: totalUsed,
      remaining: totalRemaining,
      percentUsed: ((totalUsed / totalInitial) * 100).toFixed(1)
    },
    tasks: {
      completed: totalTasks,
      avgCostPerTask: avgCostPerTask.toFixed(4),
      estimatedTasksRemaining: tasksRemaining
    },
    usage: {
      logEntries: usageLog.length,
      recentAvgCost: avgCostPerTask.toFixed(4)
    },
    projection: {
      canComplete: tasksRemaining,
      budgetExhausted: totalRemaining <= 0
    }
  };
  
  return status;
}

/**
 * Setup initial 5 accounts
 */
async function setupInitial() {
  console.log('🚀 Initial Account Setup\n');
  console.log('This will configure 5 accounts with $1000 each = $5000 total');
  console.log('You will need to provide 5 Anthropic API keys\n');
  
  const accounts = await readJSON(ACCOUNTS_FILE);
  if (accounts.length > 0) {
    console.log('⚠️  Accounts already exist. Use "add" command to add more.');
    return;
  }
  
  console.log('Enter API keys for 5 accounts:');
  console.log('(Format: sk-ant-...)\n');
  
  // This would be interactive in a real CLI
  // For now, show instructions
  console.log('Run these commands with your actual API keys:');
  console.log('');
  console.log('node trinity-account-manager.js add max-account-1 YOUR_API_KEY_1 1000');
  console.log('node trinity-account-manager.js add max-account-2 YOUR_API_KEY_2 1000');
  console.log('node trinity-account-manager.js add max-account-3 YOUR_API_KEY_3 1000');
  console.log('node trinity-account-manager.js add max-account-4 YOUR_API_KEY_4 1000');
  console.log('node trinity-account-manager.js add max-account-5 YOUR_API_KEY_5 1000');
  console.log('');
}

/**
 * Smart account rotation
 * Returns account with most credits available
 */
async function getOptimalAccount() {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const activeAccounts = accounts.filter(a => a.status === 'active' && a.creditsRemaining > 0);
  
  if (activeAccounts.length === 0) {
    throw new Error('No active accounts with remaining credits');
  }
  
  // Sort by credits remaining (highest first)
  activeAccounts.sort((a, b) => b.creditsRemaining - a.creditsRemaining);
  
  return activeAccounts[0];
}

/**
 * Batch allocate accounts for multiple tasks
 */
async function allocateAccountsForBatch(numTasks) {
  const accounts = await readJSON(ACCOUNTS_FILE);
  const activeAccounts = accounts.filter(a => a.status === 'active' && a.creditsRemaining > 0);
  
  if (activeAccounts.length === 0) {
    throw new Error('No active accounts available');
  }
  
  // Distribute tasks across accounts
  const allocation = [];
  for (let i = 0; i < numTasks; i++) {
    const accountIndex = i % activeAccounts.length;
    allocation.push(activeAccounts[accountIndex]);
  }
  
  console.log(`📊 Batch allocation for ${numTasks} tasks:`);
  
  const accountCounts = {};
  allocation.forEach(account => {
    accountCounts[account.name] = (accountCounts[account.name] || 0) + 1;
  });
  
  Object.entries(accountCounts).forEach(([name, count]) => {
    console.log(`   ${name}: ${count} tasks`);
  });
  
  return allocation;
}

// ========================================
// CLI
// ========================================

async function main() {
  await fs.mkdir(TRINITY_DIR, { recursive: true });
  
  const command = process.argv[2];
  
  if (!command) {
    console.log('🔑 Trinity Account Pool Manager\n');
    console.log('Commands:');
    console.log('  setup                                    - Initial 5-account setup guide');
    console.log('  add <name> <apiKey> [initialCredits]     - Add account to pool');
    console.log('  remove <name>                            - Remove account');
    console.log('  list                                     - List all accounts');
    console.log('  next                                     - Get next account (round-robin)');
    console.log('  optimal                                  - Get account with most credits');
    console.log('  track <name> <cost>                      - Track usage');
    console.log('  status                                   - Comprehensive status');
    console.log('  allocate <numTasks>                      - Batch allocate for tasks');
    console.log('\nDefault initial credits: $1000 per account');
    process.exit(0);
  }
  
  if (command === 'setup') {
    await setupInitial();
  }
  else if (command === 'add') {
    const name = process.argv[3];
    const apiKey = process.argv[4];
    const credits = parseFloat(process.argv[5]) || 1000;
    
    if (!name || !apiKey) {
      console.error('Usage: add <name> <apiKey> [initialCredits]');
      process.exit(1);
    }
    
    await addAccount(name, apiKey, credits);
  }
  else if (command === 'remove') {
    const name = process.argv[3];
    
    if (!name) {
      console.error('Usage: remove <name>');
      process.exit(1);
    }
    
    await removeAccount(name);
  }
  else if (command === 'list') {
    await listAccounts();
  }
  else if (command === 'next') {
    const account = await getNextAccount();
    console.log(`\n🔑 Use this API key: ${account.apiKey}`);
  }
  else if (command === 'optimal') {
    const account = await getOptimalAccount();
    console.log(`\n🎯 Optimal account: ${account.name}`);
    console.log(`   Credits: $${account.creditsRemaining.toFixed(2)}`);
    console.log(`   API Key: ${account.apiKey}`);
  }
  else if (command === 'track') {
    const name = process.argv[3];
    const cost = parseFloat(process.argv[4]);
    
    if (!name || isNaN(cost)) {
      console.error('Usage: track <name> <cost>');
      process.exit(1);
    }
    
    await trackUsage(name, cost);
  }
  else if (command === 'status') {
    const status = await getStatus();
    console.log('\n📊 Trinity Account Pool Status:\n');
    console.log(JSON.stringify(status, null, 2));
  }
  else if (command === 'allocate') {
    const numTasks = parseInt(process.argv[3]);
    
    if (!numTasks || isNaN(numTasks)) {
      console.error('Usage: allocate <numTasks>');
      process.exit(1);
    }
    
    await allocateAccountsForBatch(numTasks);
  }
  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Export
module.exports = {
  addAccount,
  removeAccount,
  listAccounts,
  getNextAccount,
  getOptimalAccount,
  trackUsage,
  getAccount,
  getStatus,
  allocateAccountsForBatch
};

// Run CLI
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
