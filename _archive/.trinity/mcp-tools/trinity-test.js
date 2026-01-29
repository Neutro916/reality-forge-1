#!/usr/bin/env node

/**
 * TRINITY INSTALLATION TEST
 * 
 * Run this to verify Trinity is set up correctly
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');

async function checkFile(filepath, name) {
  try {
    await fs.access(filepath);
    console.log(`✅ ${name} - Found`);
    return true;
  } catch {
    console.log(`❌ ${name} - Missing`);
    return false;
  }
}

async function createInitialFiles() {
  console.log('\n📝 Creating initial Trinity files...\n');
  
  const files = {
    'messages.json': [],
    'tasks.json': [],
    'outputs.json': [],
    'status.json': { initialized: new Date().toISOString() }
  };
  
  for (const [filename, content] of Object.entries(files)) {
    const filepath = path.join(TRINITY_DIR, filename);
    try {
      await fs.writeFile(filepath, JSON.stringify(content, null, 2));
      console.log(`✅ Created ${filename}`);
    } catch (error) {
      console.log(`❌ Failed to create ${filename}: ${error.message}`);
    }
  }
}

async function test() {
  console.log('🔱 Trinity Installation Test\n');
  console.log(`📁 Trinity Directory: ${TRINITY_DIR}\n`);
  
  // Check directory
  try {
    await fs.access(TRINITY_DIR);
    console.log('✅ Trinity directory exists\n');
  } catch {
    console.log('⚠️  Trinity directory not found - creating...\n');
    await fs.mkdir(TRINITY_DIR, { recursive: true });
    console.log('✅ Trinity directory created\n');
  }
  
  // Check core files
  console.log('📋 Checking core files:\n');
  
  const coreFiles = [
    ['trinity-mcp-server.js', 'MCP Server'],
    ['trinity-auto-wake.js', 'Auto-wake Protocol'],
    ['TRINITY_WORKSPACE.html', 'Workspace Interface'],
    ['package.json', 'Package Config']
  ];
  
  let allFound = true;
  for (const [file, name] of coreFiles) {
    const found = await checkFile(path.join(TRINITY_DIR, file), name);
    if (!found) allFound = false;
  }
  
  // Check data files
  console.log('\n📊 Checking data files:\n');
  
  const dataFiles = [
    ['messages.json', 'Messages'],
    ['tasks.json', 'Tasks'],
    ['outputs.json', 'Outputs'],
    ['status.json', 'Status']
  ];
  
  let dataFilesExist = true;
  for (const [file, name] of dataFiles) {
    const found = await checkFile(path.join(TRINITY_DIR, file), name);
    if (!found) dataFilesExist = false;
  }
  
  if (!dataFilesExist) {
    await createInitialFiles();
  }
  
  // Check dependencies
  console.log('\n📦 Checking dependencies:\n');
  
  try {
    require('@modelcontextprotocol/sdk');
    console.log('✅ MCP SDK - Installed');
  } catch {
    console.log('❌ MCP SDK - Not installed');
    console.log('   Run: npm install');
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('\n📊 Installation Summary:\n');
  
  if (allFound) {
    console.log('✅ All core files present');
  } else {
    console.log('⚠️  Some core files missing - copy them to Trinity folder');
  }
  
  if (dataFilesExist) {
    console.log('✅ Data files initialized');
  }
  
  console.log('\n🎯 Next Steps:\n');
  console.log('1. Update your MCP config to point to trinity-mcp-server.js');
  console.log('2. Restart Claude instances');
  console.log('3. Test with: trinity_status');
  console.log('4. Open TRINITY_WORKSPACE.html in browser');
  console.log('5. Start auto-wake workers: node trinity-auto-wake.js [instance-id]');
  
  console.log('\n🔥 Ready to orchestrate! 🔱\n');
}

test().catch(error => {
  console.error('Test failed:', error);
  process.exit(1);
});
