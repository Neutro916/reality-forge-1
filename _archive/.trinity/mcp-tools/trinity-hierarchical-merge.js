#!/usr/bin/env node

/**
 * TRINITY HIERARCHICAL MERGE ENGINE
 * 
 * Implements the convergence logic: 3→1 at multiple levels
 * - Level 1: 3 worker outputs → 1 cluster synthesis
 * - Level 2: Multiple cluster outputs → 1 meta synthesis
 * - Level 3: Meta syntheses → 1 ultimate master output
 * 
 * Usage:
 *   node trinity-hierarchical-merge.js cluster <clusterName>
 *   node trinity-hierarchical-merge.js meta <metaName> <cluster1,cluster2,...>
 *   node trinity-hierarchical-merge.js ultimate <output1,output2,...>
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const OUTPUTS_FILE = path.join(TRINITY_DIR, 'outputs.json');
const CONVERGENCES_FILE = path.join(TRINITY_DIR, 'convergences.json');
const CLOUD_INSTANCES_FILE = path.join(TRINITY_DIR, 'cloud-instances.json');

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
 * LEVEL 1: CLUSTER CONVERGENCE (3→1)
 * Takes 3 worker outputs from same cluster and synthesizes into 1
 */
async function convergeCluster(clusterName, synthesisStrategy = 'comprehensive') {
  console.log(`\n🔗 Converging Trinity Cluster: ${clusterName}`);
  
  // Get outputs from this cluster
  const allOutputs = await readJSON(OUTPUTS_FILE);
  const clusterOutputs = allOutputs.filter(o => o.cluster === clusterName);
  
  if (clusterOutputs.length === 0) {
    throw new Error(`No outputs found for cluster: ${clusterName}`);
  }
  
  if (clusterOutputs.length !== 3) {
    console.warn(`⚠️  Expected 3 outputs, found ${clusterOutputs.length}`);
  }
  
  console.log(`📊 Found ${clusterOutputs.length} outputs to merge`);
  
  // Sort by role (worker-1, worker-2, worker-3)
  clusterOutputs.sort((a, b) => {
    const roleA = a.role || '';
    const roleB = b.role || '';
    return roleA.localeCompare(roleB);
  });
  
  // Generate synthesis prompt based on strategy
  const synthesisPrompts = {
    comprehensive: generateComprehensiveSynthesis(clusterOutputs, clusterName),
    executive: generateExecutiveSynthesis(clusterOutputs, clusterName),
    technical: generateTechnicalSynthesis(clusterOutputs, clusterName),
    narrative: generateNarrativeSynthesis(clusterOutputs, clusterName)
  };
  
  const synthesisPrompt = synthesisPrompts[synthesisStrategy] || synthesisPrompts.comprehensive;
  
  // Create convergence record
  const convergence = {
    id: generateId(),
    type: 'cluster',
    clusterName,
    inputOutputs: clusterOutputs.map(o => o.taskId || o.instanceId),
    synthesisStrategy,
    synthesisPrompt,
    timestamp: new Date().toISOString(),
    level: 1,
    status: 'ready'
  };
  
  // Save convergence record
  const convergences = await readJSON(CONVERGENCES_FILE);
  convergences.push(convergence);
  await writeJSON(CONVERGENCES_FILE, convergences);
  
  console.log(`✅ Cluster convergence prepared`);
  console.log(`🆔 Convergence ID: ${convergence.id}`);
  console.log(`📋 Synthesis strategy: ${synthesisStrategy}`);
  console.log(`\n📝 Synthesis Prompt:\n`);
  console.log(synthesisPrompt);
  console.log(`\n---\n`);
  
  return convergence;
}

/**
 * LEVEL 2: META CONVERGENCE (multiple clusters → 1)
 * Takes outputs from multiple cluster convergences and creates meta-synthesis
 */
async function convergeMeta(metaName, clusterNames, synthesisStrategy = 'integrative') {
  console.log(`\n🔗🔗 Meta Convergence: ${metaName}`);
  console.log(`📦 Clusters: ${clusterNames.join(', ')}`);
  
  // Get convergence records for specified clusters
  const allConvergences = await readJSON(CONVERGENCES_FILE);
  const clusterConvergences = allConvergences.filter(c => 
    c.type === 'cluster' && clusterNames.includes(c.clusterName)
  );
  
  if (clusterConvergences.length === 0) {
    throw new Error(`No cluster convergences found for: ${clusterNames.join(', ')}`);
  }
  
  console.log(`📊 Found ${clusterConvergences.length} cluster convergences`);
  
  // Generate meta synthesis prompt
  const metaSynthesisPrompt = generateMetaSynthesis(clusterConvergences, metaName, synthesisStrategy);
  
  // Create meta convergence record
  const metaConvergence = {
    id: generateId(),
    type: 'meta',
    metaName,
    inputConvergences: clusterConvergences.map(c => c.id),
    clusters: clusterNames,
    synthesisStrategy,
    synthesisPrompt: metaSynthesisPrompt,
    timestamp: new Date().toISOString(),
    level: 2,
    status: 'ready'
  };
  
  // Save
  const convergences = await readJSON(CONVERGENCES_FILE);
  convergences.push(metaConvergence);
  await writeJSON(CONVERGENCES_FILE, convergences);
  
  console.log(`✅ Meta convergence prepared`);
  console.log(`🆔 Convergence ID: ${metaConvergence.id}`);
  console.log(`\n📝 Meta Synthesis Prompt:\n`);
  console.log(metaSynthesisPrompt);
  console.log(`\n---\n`);
  
  return metaConvergence;
}

/**
 * LEVEL 3: ULTIMATE CONVERGENCE (all metas → 1 master)
 * Takes all meta convergences and creates the final master output
 */
async function convergeUltimate(projectName, metaNames) {
  console.log(`\n🔗🔗🔗 ULTIMATE CONVERGENCE: ${projectName}`);
  console.log(`🌌 Meta convergences: ${metaNames.join(', ')}`);
  
  // Get all meta convergences
  const allConvergences = await readJSON(CONVERGENCES_FILE);
  const metaConvergences = allConvergences.filter(c => 
    c.type === 'meta' && metaNames.includes(c.metaName)
  );
  
  if (metaConvergences.length === 0) {
    throw new Error(`No meta convergences found for: ${metaNames.join(', ')}`);
  }
  
  console.log(`📊 Found ${metaConvergences.length} meta convergences`);
  
  // Generate ultimate synthesis prompt
  const ultimateSynthesisPrompt = generateUltimateSynthesis(metaConvergences, projectName);
  
  // Create ultimate convergence record
  const ultimateConvergence = {
    id: generateId(),
    type: 'ultimate',
    projectName,
    inputConvergences: metaConvergences.map(c => c.id),
    metas: metaNames,
    synthesisPrompt: ultimateSynthesisPrompt,
    timestamp: new Date().toISOString(),
    level: 3,
    status: 'ready'
  };
  
  // Save
  const convergences = await readJSON(CONVERGENCES_FILE);
  convergences.push(ultimateConvergence);
  await writeJSON(CONVERGENCES_FILE, convergences);
  
  console.log(`✅ Ultimate convergence prepared`);
  console.log(`🆔 Convergence ID: ${ultimateConvergence.id}`);
  console.log(`\n📝 Ultimate Synthesis Prompt:\n`);
  console.log(ultimateSynthesisPrompt);
  console.log(`\n---\n`);
  
  return ultimateConvergence;
}

/**
 * AUTO-CONVERGE: Automatically converge all available outputs
 */
async function autoConverge(options = {}) {
  const { dryRun = false } = options;
  
  console.log('🤖 Auto-Convergence Mode\n');
  
  // Get all outputs
  const outputs = await readJSON(OUTPUTS_FILE);
  const convergences = await readJSON(CONVERGENCES_FILE);
  
  // Group outputs by cluster
  const clusterMap = {};
  outputs.forEach(output => {
    const cluster = output.cluster || 'unclustered';
    if (!clusterMap[cluster]) clusterMap[cluster] = [];
    clusterMap[cluster].push(output);
  });
  
  // Identify clusters ready for convergence (have 3 outputs)
  const readyClusters = Object.keys(clusterMap).filter(c => clusterMap[c].length >= 3);
  
  console.log(`📊 Found ${readyClusters.length} clusters ready for convergence:`);
  readyClusters.forEach(cluster => {
    console.log(`   - ${cluster}: ${clusterMap[cluster].length} outputs`);
  });
  
  if (dryRun) {
    console.log('\n🔍 Dry run - no actual convergence performed');
    return { readyClusters, wouldConverge: readyClusters.length };
  }
  
  // Converge ready clusters
  const results = [];
  for (const cluster of readyClusters) {
    try {
      const result = await convergeCluster(cluster);
      results.push({ cluster, success: true, convergenceId: result.id });
    } catch (error) {
      results.push({ cluster, success: false, error: error.message });
    }
  }
  
  console.log(`\n✅ Auto-convergence complete`);
  console.log(`   Successful: ${results.filter(r => r.success).length}`);
  console.log(`   Failed: ${results.filter(r => !r.success).length}`);
  
  return { results };
}

// ========================================
// SYNTHESIS PROMPT GENERATORS
// ========================================

function generateComprehensiveSynthesis(outputs, clusterName) {
  return `# Trinity Cluster Synthesis: ${clusterName}

You are synthesizing outputs from 3 Trinity workers into 1 unified, comprehensive result.

## Input Outputs:

### Worker 1 Output:
${outputs[0]?.output || '(no output)'}

### Worker 2 Output:
${outputs[1]?.output || '(no output)'}

### Worker 3 Output:
${outputs[2]?.output || '(no output)'}

## Your Task:

Synthesize these 3 outputs into ONE comprehensive, cohesive result that:

1. **Integrates all key information** from all 3 workers
2. **Eliminates redundancy** while preserving unique insights
3. **Maintains logical flow** and narrative coherence
4. **Highlights connections** between different aspects
5. **Provides actionable conclusions** based on the combined insights

Structure your synthesis with:
- **Executive Summary**: Key findings in 3-5 sentences
- **Detailed Synthesis**: Comprehensive integration of all insights
- **Key Takeaways**: 5-7 bullet points of critical information
- **Recommendations**: Based on the synthesized analysis

Create a single, authoritative document that represents the best of all 3 inputs.`;
}

function generateExecutiveSynthesis(outputs, clusterName) {
  return `# Executive Synthesis: ${clusterName}

Synthesize these 3 worker outputs into a concise executive summary:

${outputs.map((o, i) => `**Worker ${i+1}**: ${o.output?.substring(0, 500)}...`).join('\n\n')}

Provide:
1. **Key Findings** (3-5 points)
2. **Critical Insights** (2-3 points)
3. **Recommended Actions** (2-3 points)

Keep it concise, actionable, and executive-focused.`;
}

function generateTechnicalSynthesis(outputs, clusterName) {
  return `# Technical Synthesis: ${clusterName}

Synthesize these technical outputs with focus on:
- Technical accuracy and precision
- Implementation details
- Architecture and design patterns
- Best practices and recommendations

Inputs:
${outputs.map((o, i) => `## Input ${i+1}:\n${o.output}`).join('\n\n')}

Create a technically rigorous, implementation-ready synthesis.`;
}

function generateNarrativeSynthesis(outputs, clusterName) {
  return `# Narrative Synthesis: ${clusterName}

Weave these 3 perspectives into a compelling narrative:

${outputs.map((o, i) => `**Perspective ${i+1}**: ${o.output}`).join('\n\n')}

Create a cohesive story that maintains engagement while conveying all key information.`;
}

function generateMetaSynthesis(clusterConvergences, metaName, strategy) {
  return `# Meta Synthesis: ${metaName}

You are performing a meta-level synthesis of ${clusterConvergences.length} cluster convergences.

Each cluster convergence represents the synthesized output of 3 workers. Your task is to integrate these cluster-level syntheses into ONE higher-level meta synthesis.

## Cluster Convergences:

${clusterConvergences.map((c, i) => `### Cluster ${i+1}: ${c.clusterName}
(Convergence ID: ${c.id})
Strategy used: ${c.synthesisStrategy}
`).join('\n')}

## Your Task:

Create a meta-level synthesis that:

1. **Identifies cross-cluster patterns** and themes
2. **Integrates insights** across different domains
3. **Reveals emergent connections** not visible in individual clusters
4. **Provides holistic understanding** of the combined work
5. **Generates higher-order insights** from the synthesis

Structure:
- **Overview**: What this meta-synthesis covers
- **Cross-Cluster Analysis**: Patterns and connections
- **Integrated Insights**: Higher-order understanding
- **Synthesis**: Unified perspective across all clusters
- **Implications**: What this means at scale

This meta-synthesis will feed into the ultimate master convergence.`;
}

function generateUltimateSynthesis(metaConvergences, projectName) {
  return `# ULTIMATE MASTER SYNTHESIS: ${projectName}

This is the FINAL convergence - the apex of the Trinity hierarchical synthesis.

You are synthesizing ${metaConvergences.length} meta-convergences, each of which synthesized multiple cluster convergences, each of which synthesized 3 worker outputs.

This represents the cumulative work of dozens of Trinity workers across multiple domains.

## Meta Convergences:

${metaConvergences.map((m, i) => `### Meta ${i+1}: ${m.metaName}
(Meta ID: ${m.id})
Clusters included: ${m.clusters?.join(', ') || 'N/A'}
`).join('\n')}

## Your Task:

Create the ULTIMATE MASTER OUTPUT that:

1. **Synthesizes ALL meta-level insights** into one coherent whole
2. **Reveals the complete picture** across all domains
3. **Identifies universal patterns** and principles
4. **Provides comprehensive understanding** of the entire project
5. **Generates definitive conclusions** based on all the work
6. **Creates lasting value** as a permanent reference

Structure:
- **Executive Overview**: The complete picture in 1 page
- **Domain Integration**: How all areas connect
- **Universal Insights**: Patterns across everything
- **Comprehensive Analysis**: The full synthesis
- **Master Conclusions**: Definitive findings
- **Future Directions**: Where this leads
- **Reference Guide**: How to use this compendium

This is THE definitive output. Make it comprehensive, authoritative, and permanently valuable.

The Trinity Knowledge Compendium - Ultimate Master Synthesis.`;
}

// ========================================
// CONVERGENCE EXECUTION
// ========================================

async function executeConvergence(convergenceId, apiKey) {
  console.log(`\n⚡ Executing convergence: ${convergenceId}`);
  
  // Get convergence record
  const convergences = await readJSON(CONVERGENCES_FILE);
  const convergence = convergences.find(c => c.id === convergenceId);
  
  if (!convergence) {
    throw new Error(`Convergence not found: ${convergenceId}`);
  }
  
  if (convergence.status === 'completed') {
    console.log('⚠️  Convergence already completed');
    return convergence;
  }
  
  console.log(`📋 Type: ${convergence.type}`);
  console.log(`📊 Level: ${convergence.level}`);
  
  // Use cloud spawner to execute synthesis
  const { spawnCloudInstance } = require('./trinity-cloud-spawner.js');
  
  const result = await spawnCloudInstance(
    convergence.synthesisPrompt,
    apiKey,
    {
      maxTokens: 8192,
      trinityRole: `${convergence.type}-synthesizer`,
      clusterName: convergence.clusterName || convergence.metaName || convergence.projectName
    }
  );
  
  // Update convergence record
  convergence.status = 'completed';
  convergence.output = result.output;
  convergence.completedAt = new Date().toISOString();
  convergence.cost = result.cost;
  
  await writeJSON(CONVERGENCES_FILE, convergences);
  
  console.log(`✅ Convergence executed successfully`);
  console.log(`💰 Cost: $${result.cost.toFixed(4)}`);
  
  return convergence;
}

// ========================================
// CLI
// ========================================

async function main() {
  await fs.mkdir(TRINITY_DIR, { recursive: true });
  
  const command = process.argv[2];
  
  if (!command) {
    console.log('🔗 Trinity Hierarchical Merge Engine\n');
    console.log('Commands:');
    console.log('  cluster <clusterName> [strategy]        - Converge cluster (3→1)');
    console.log('  meta <metaName> <cluster1,cluster2,...> - Meta convergence');
    console.log('  ultimate <projectName> <meta1,meta2>    - Ultimate convergence');
    console.log('  execute <convergenceId> <apiKey>        - Execute a convergence');
    console.log('  auto [--dry-run]                        - Auto-converge ready clusters');
    console.log('  status                                  - Show convergence status');
    console.log('\nStrategies: comprehensive, executive, technical, narrative');
    process.exit(0);
  }
  
  if (command === 'cluster') {
    const clusterName = process.argv[3];
    const strategy = process.argv[4] || 'comprehensive';
    
    if (!clusterName) {
      console.error('Usage: cluster <clusterName> [strategy]');
      process.exit(1);
    }
    
    await convergeCluster(clusterName, strategy);
  }
  else if (command === 'meta') {
    const metaName = process.argv[3];
    const clustersArg = process.argv[4];
    
    if (!metaName || !clustersArg) {
      console.error('Usage: meta <metaName> <cluster1,cluster2,...>');
      process.exit(1);
    }
    
    const clusters = clustersArg.split(',');
    await convergeMeta(metaName, clusters);
  }
  else if (command === 'ultimate') {
    const projectName = process.argv[3];
    const metasArg = process.argv[4];
    
    if (!projectName || !metasArg) {
      console.error('Usage: ultimate <projectName> <meta1,meta2,...>');
      process.exit(1);
    }
    
    const metas = metasArg.split(',');
    await convergeUltimate(projectName, metas);
  }
  else if (command === 'execute') {
    const convergenceId = process.argv[3];
    const apiKey = process.argv[4] || process.env.ANTHROPIC_API_KEY;
    
    if (!convergenceId || !apiKey) {
      console.error('Usage: execute <convergenceId> <apiKey>');
      process.exit(1);
    }
    
    await executeConvergence(convergenceId, apiKey);
  }
  else if (command === 'auto') {
    const dryRun = process.argv.includes('--dry-run');
    await autoConverge({ dryRun });
  }
  else if (command === 'status') {
    const convergences = await readJSON(CONVERGENCES_FILE);
    
    console.log('\n📊 Convergence Status:\n');
    console.log(`Total: ${convergences.length}`);
    console.log(`  Cluster (L1): ${convergences.filter(c => c.type === 'cluster').length}`);
    console.log(`  Meta (L2): ${convergences.filter(c => c.type === 'meta').length}`);
    console.log(`  Ultimate (L3): ${convergences.filter(c => c.type === 'ultimate').length}`);
    console.log(`  Completed: ${convergences.filter(c => c.status === 'completed').length}`);
    console.log(`  Ready: ${convergences.filter(c => c.status === 'ready').length}`);
    
    console.log('\n📋 Convergences:\n');
    convergences.forEach(c => {
      console.log(`[${c.type.toUpperCase()}] ${c.clusterName || c.metaName || c.projectName}`);
      console.log(`  ID: ${c.id}`);
      console.log(`  Status: ${c.status}`);
      console.log(`  Level: ${c.level}`);
      if (c.cost) console.log(`  Cost: $${c.cost.toFixed(4)}`);
      console.log('');
    });
  }
  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Export
module.exports = {
  convergeCluster,
  convergeMeta,
  convergeUltimate,
  autoConverge,
  executeConvergence
};

// Run CLI
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
