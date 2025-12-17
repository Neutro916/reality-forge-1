#!/usr/bin/env node

/**
 * TRINITY CLOUD SPAWNER - Anthropic API Integration
 * 
 * This is the CRITICAL PATH tool for scaling Trinity to 21+ instances.
 * Spawns cloud Claude instances via API, assigns tasks, retrieves outputs.
 * 
 * Usage:
 *   node trinity-cloud-spawner.js spawn <task> <apiKey>
 *   node trinity-cloud-spawner.js monitor <conversationId> <apiKey>
 *   node trinity-cloud-spawner.js retrieve <conversationId> <apiKey>
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const https = require('https');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const CLOUD_INSTANCES_FILE = path.join(TRINITY_DIR, 'cloud-instances.json');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');

// Anthropic API configuration
const ANTHROPIC_API_URL = 'api.anthropic.com';
const ANTHROPIC_API_VERSION = '2023-06-01';
const DEFAULT_MODEL = 'claude-sonnet-4-20250514';
const MAX_TOKENS = 8192;

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

// Generate unique ID
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Make HTTPS request to Anthropic API
function makeAnthropicRequest(apiKey, payload) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(payload);
    
    const options = {
      hostname: ANTHROPIC_API_URL,
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': ANTHROPIC_API_VERSION,
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.write(postData);
    req.end();
  });
}

// Spawn a cloud Claude instance with a task
async function spawnCloudInstance(task, apiKey, options = {}) {
  const {
    model = DEFAULT_MODEL,
    maxTokens = MAX_TOKENS,
    trinityRole = 'worker',
    clusterName = 'default',
    systemPrompt = null
  } = options;
  
  console.log('🚀 Spawning cloud Claude instance...');
  console.log(`📋 Task: ${task.substring(0, 100)}${task.length > 100 ? '...' : ''}`);
  console.log(`🔱 Role: ${trinityRole}`);
  console.log(`📦 Cluster: ${clusterName}`);
  
  // Construct system prompt for Trinity integration
  const defaultSystemPrompt = `You are a Trinity worker instance (${trinityRole}) in the ${clusterName} cluster.

Your task is part of a larger orchestrated effort. Complete your assigned work thoroughly and submit your output.

Trinity Integration:
- You are one of 3 workers in your cluster
- Your output will be merged with 2 sibling outputs
- The merged result contributes to a larger master output
- Work with precision and completeness

Execute the task and provide comprehensive results.`;

  const finalSystemPrompt = systemPrompt || defaultSystemPrompt;
  
  // Make API call
  const payload = {
    model,
    max_tokens: maxTokens,
    system: finalSystemPrompt,
    messages: [
      {
        role: 'user',
        content: task
      }
    ]
  };
  
  try {
    const startTime = Date.now();
    const response = await makeAnthropicRequest(apiKey, payload);
    const endTime = Date.now();
    
    if (response.error) {
      throw new Error(`API Error: ${response.error.message || JSON.stringify(response.error)}`);
    }
    
    // Extract the response
    const output = response.content && response.content[0] ? response.content[0].text : '';
    const usage = response.usage || {};
    
    // Calculate cost (approximate)
    const inputTokens = usage.input_tokens || 0;
    const outputTokens = usage.output_tokens || 0;
    const estimatedCost = ((inputTokens * 0.003) + (outputTokens * 0.015)) / 1000; // Sonnet 4 pricing
    
    // Create instance record
    const instance = {
      id: generateId(),
      task,
      trinityRole,
      clusterName,
      output,
      model,
      usage: {
        inputTokens,
        outputTokens,
        totalTokens: inputTokens + outputTokens
      },
      cost: estimatedCost,
      duration: endTime - startTime,
      timestamp: new Date().toISOString(),
      status: 'completed'
    };
    
    // Save instance record
    const instances = await readJSON(CLOUD_INSTANCES_FILE);
    instances.push(instance);
    await writeJSON(CLOUD_INSTANCES_FILE, instances);
    
    // Save to outputs
    const outputs = await readJSON(OUTPUTS_FILE);
    outputs.push({
      taskId: instance.id,
      instanceId: `cloud-${instance.id}`,
      output,
      timestamp: instance.timestamp,
      cluster: clusterName,
      role: trinityRole,
      cost: estimatedCost
    });
    await writeJSON(OUTPUTS_FILE, outputs);
    
    console.log('✅ Cloud instance completed!');
    console.log(`📊 Tokens: ${inputTokens} in / ${outputTokens} out`);
    console.log(`💰 Cost: $${estimatedCost.toFixed(4)}`);
    console.log(`⏱️  Duration: ${(instance.duration / 1000).toFixed(2)}s`);
    console.log(`🆔 Instance ID: ${instance.id}`);
    
    return instance;
    
  } catch (error) {
    console.error('❌ Failed to spawn cloud instance:', error.message);
    
    // Log failed attempt
    const instances = await readJSON(CLOUD_INSTANCES_FILE);
    instances.push({
      id: generateId(),
      task,
      trinityRole,
      clusterName,
      status: 'failed',
      error: error.message,
      timestamp: new Date().toISOString()
    });
    await writeJSON(CLOUD_INSTANCES_FILE, instances);
    
    throw error;
  }
}

// Spawn a trinity cluster (3 cloud instances)
async function spawnTrinityCluster(tasks, apiKey, clusterName, options = {}) {
  console.log(`\n🔱 Spawning Trinity Cluster: ${clusterName}`);
  console.log(`📋 Tasks: ${tasks.length}`);
  
  if (tasks.length !== 3) {
    throw new Error('Trinity cluster requires exactly 3 tasks');
  }
  
  const roles = ['worker-1', 'worker-2', 'worker-3'];
  const instances = [];
  
  for (let i = 0; i < 3; i++) {
    console.log(`\n--- Spawning ${roles[i]} ---`);
    const instance = await spawnCloudInstance(tasks[i], apiKey, {
      ...options,
      trinityRole: roles[i],
      clusterName
    });
    instances.push(instance);
  }
  
  console.log(`\n✅ Trinity cluster "${clusterName}" complete!`);
  console.log(`💰 Total cost: $${instances.reduce((sum, i) => sum + i.cost, 0).toFixed(4)}`);
  
  return {
    clusterName,
    instances,
    totalCost: instances.reduce((sum, i) => sum + i.cost, 0),
    timestamp: new Date().toISOString()
  };
}

// Batch spawn multiple instances
async function batchSpawn(tasksArray, apiKey, options = {}) {
  const { parallel = 3, delayMs = 1000 } = options;
  
  console.log(`🚀 Batch spawning ${tasksArray.length} instances`);
  console.log(`⚡ Parallelism: ${parallel} concurrent`);
  
  const results = [];
  const chunks = [];
  
  // Split into chunks for parallel execution
  for (let i = 0; i < tasksArray.length; i += parallel) {
    chunks.push(tasksArray.slice(i, i + parallel));
  }
  
  for (let chunkIdx = 0; chunkIdx < chunks.length; chunkIdx++) {
    const chunk = chunks[chunkIdx];
    console.log(`\n📦 Processing batch ${chunkIdx + 1}/${chunks.length} (${chunk.length} tasks)`);
    
    const promises = chunk.map(task => 
      spawnCloudInstance(task, apiKey, options)
        .catch(error => ({ error: error.message }))
    );
    
    const chunkResults = await Promise.all(promises);
    results.push(...chunkResults);
    
    // Delay between batches to avoid rate limits
    if (chunkIdx < chunks.length - 1) {
      console.log(`⏸️  Waiting ${delayMs}ms before next batch...`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
  
  const successful = results.filter(r => !r.error).length;
  const failed = results.filter(r => r.error).length;
  const totalCost = results.filter(r => !r.error).reduce((sum, r) => sum + r.cost, 0);
  
  console.log(`\n✅ Batch spawn complete!`);
  console.log(`📊 Successful: ${successful} | Failed: ${failed}`);
  console.log(`💰 Total cost: $${totalCost.toFixed(4)}`);
  
  return {
    results,
    successful,
    failed,
    totalCost
  };
}

// Get status of all cloud instances
async function getCloudStatus() {
  const instances = await readJSON(CLOUD_INSTANCES_FILE);
  
  const stats = {
    total: instances.length,
    completed: instances.filter(i => i.status === 'completed').length,
    failed: instances.filter(i => i.status === 'failed').length,
    totalCost: instances.filter(i => i.cost).reduce((sum, i) => sum + i.cost, 0),
    totalTokens: instances.filter(i => i.usage).reduce((sum, i) => sum + i.usage.totalTokens, 0),
    clusters: {}
  };
  
  // Group by cluster
  instances.forEach(instance => {
    const cluster = instance.clusterName || 'unclustered';
    if (!stats.clusters[cluster]) {
      stats.clusters[cluster] = {
        count: 0,
        cost: 0,
        completed: 0,
        failed: 0
      };
    }
    stats.clusters[cluster].count++;
    stats.clusters[cluster].cost += instance.cost || 0;
    if (instance.status === 'completed') stats.clusters[cluster].completed++;
    if (instance.status === 'failed') stats.clusters[cluster].failed++;
  });
  
  return stats;
}

// Command-line interface
async function main() {
  await fs.mkdir(TRINITY_DIR, { recursive: true });
  
  const command = process.argv[2];
  
  if (!command) {
    console.log('🔱 Trinity Cloud Spawner\n');
    console.log('Commands:');
    console.log('  spawn <task> <apiKey>              - Spawn single instance');
    console.log('  cluster <clusterName> <apiKey>     - Spawn trinity cluster (3 instances)');
    console.log('  batch <tasksFile> <apiKey>         - Batch spawn from file');
    console.log('  status                             - Show cloud instance status');
    console.log('  test <apiKey>                      - Test API connection');
    console.log('\nEnvironment variables:');
    console.log('  ANTHROPIC_API_KEY - Default API key');
    process.exit(0);
  }
  
  if (command === 'spawn') {
    const task = process.argv[3];
    const apiKey = process.argv[4] || process.env.ANTHROPIC_API_KEY;
    
    if (!task || !apiKey) {
      console.error('Usage: spawn <task> <apiKey>');
      process.exit(1);
    }
    
    await spawnCloudInstance(task, apiKey);
  }
  else if (command === 'cluster') {
    const clusterName = process.argv[3];
    const apiKey = process.argv[4] || process.env.ANTHROPIC_API_KEY;
    
    if (!clusterName || !apiKey) {
      console.error('Usage: cluster <clusterName> <apiKey>');
      process.exit(1);
    }
    
    // Demo tasks - replace with actual task generation
    const tasks = [
      `Research and summarize the latest developments in ${clusterName} - Part 1: Current state`,
      `Research and summarize the latest developments in ${clusterName} - Part 2: Future trends`,
      `Research and summarize the latest developments in ${clusterName} - Part 3: Key insights`
    ];
    
    await spawnTrinityCluster(tasks, apiKey, clusterName);
  }
  else if (command === 'batch') {
    const tasksFile = process.argv[3];
    const apiKey = process.argv[4] || process.env.ANTHROPIC_API_KEY;
    
    if (!tasksFile || !apiKey) {
      console.error('Usage: batch <tasksFile> <apiKey>');
      process.exit(1);
    }
    
    const tasksData = await fs.readFile(tasksFile, 'utf8');
    const tasks = JSON.parse(tasksData);
    
    await batchSpawn(tasks, apiKey, { parallel: 3 });
  }
  else if (command === 'status') {
    const stats = await getCloudStatus();
    console.log('\n📊 Cloud Instance Status:\n');
    console.log(JSON.stringify(stats, null, 2));
  }
  else if (command === 'test') {
    const apiKey = process.argv[3] || process.env.ANTHROPIC_API_KEY;
    
    if (!apiKey) {
      console.error('Usage: test <apiKey>');
      process.exit(1);
    }
    
    console.log('🧪 Testing API connection...');
    
    try {
      const instance = await spawnCloudInstance(
        'Reply with exactly: "Trinity Cloud Spawner test successful!"',
        apiKey,
        { maxTokens: 100 }
      );
      
      console.log('\n✅ API TEST SUCCESSFUL!');
      console.log(`Response: ${instance.output}`);
    } catch (error) {
      console.error('\n❌ API TEST FAILED!');
      console.error(error.message);
      process.exit(1);
    }
  }
  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Export for use as module
module.exports = {
  spawnCloudInstance,
  spawnTrinityCluster,
  batchSpawn,
  getCloudStatus
};

// Run CLI if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
