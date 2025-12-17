#!/usr/bin/env node

/**
 * TRINITY CREDIT BURN TASK GENERATOR
 * 
 * Generates comprehensive task queues for burning $5000 in credits
 * Creates the actual work manifests for the Trinity Knowledge Compendium
 * 
 * Usage:
 *   node trinity-task-generator.js generate <domain> <numTasks>
 *   node trinity-task-generator.js manifest
 *   node trinity-task-generator.js preview <domain>
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRINITY_DIR = path.join(os.homedir(), '.trinity');
const TASKS_FILE = path.join(TRINITY_DIR, 'tasks.json');
const MASTER_MANIFEST_FILE = path.join(TRINITY_DIR, 'master-task-manifest.json');

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

// ========================================
// TASK TEMPLATES BY DOMAIN
// ========================================

const TASK_TEMPLATES = {
  'technology': {
    name: 'Technology Frontier',
    clusters: [
      {
        name: 'AI-ML-Research',
        tasks: [
          'Comprehensive analysis of transformer architecture evolution from GPT-3 to current models',
          'Survey of multimodal AI systems: capabilities, limitations, and future directions',
          'Deep dive into AI alignment research: current approaches and open problems'
        ]
      },
      {
        name: 'Quantum-Computing',
        tasks: [
          'Analysis of quantum computing breakthroughs in 2024-2025',
          'Quantum algorithms with near-term practical applications',
          'Quantum error correction: state of the art and timeline to fault tolerance'
        ]
      },
      {
        name: 'Blockchain-Web3',
        tasks: [
          'Evolution of DeFi: protocols, risks, and regulatory landscape',
          'Web3 infrastructure: decentralized storage, compute, and identity',
          'NFT and digital ownership: beyond art into utility and governance'
        ]
      }
    ]
  },
  
  'science': {
    name: 'Scientific Foundations',
    clusters: [
      {
        name: 'Physics-Frontiers',
        tasks: [
          'Quantum mechanics and emergent phenomena: latest experimental results',
          'Cosmology and the early universe: JWST findings and implications',
          'Condensed matter physics: exotic materials and quantum states'
        ]
      },
      {
        name: 'Biology-Neuroscience',
        tasks: [
          'CRISPR and gene editing: current capabilities and ethical considerations',
          'Neuroscience of consciousness: theories, experiments, and open questions',
          'Synthetic biology: designing life and engineering organisms'
        ]
      },
      {
        name: 'Chemistry-Materials',
        tasks: [
          'Advanced materials science: metamaterials and programmable matter',
          'Green chemistry and sustainable synthesis methods',
          'Computational chemistry and drug discovery pipelines'
        ]
      }
    ]
  },
  
  'business': {
    name: 'Business & Economics',
    clusters: [
      {
        name: 'Market-Dynamics',
        tasks: [
          'Analysis of emerging markets: opportunities and risks in 2025',
          'Economic impact of AI on labor markets and productivity',
          'Cryptocurrency and digital assets: market structure and regulation'
        ]
      },
      {
        name: 'Strategy-Innovation',
        tasks: [
          'Platform business models: network effects and competitive dynamics',
          'Disruption patterns: how industries transform in the digital age',
          'Innovation frameworks: from idea generation to market success'
        ]
      },
      {
        name: 'Ecosystem-Building',
        tasks: [
          'Building and scaling multi-sided platforms',
          'Open innovation and strategic partnerships',
          'Network orchestration and ecosystem governance'
        ]
      }
    ]
  },
  
  'philosophy': {
    name: 'Philosophy & Ethics',
    clusters: [
      {
        name: 'AI-Ethics',
        tasks: [
          'AI alignment problem: philosophical foundations and technical approaches',
          'Ethics of autonomous systems: responsibility and decision-making',
          'AI safety governance: frameworks for beneficial AI development'
        ]
      },
      {
        name: 'Epistemology',
        tasks: [
          'Nature of knowledge in the age of AI: truth, reasoning, and understanding',
          'Bayesian epistemology and rational belief updating',
          'Distributed cognition: how collectives know and learn'
        ]
      },
      {
        name: 'Applied-Philosophy',
        tasks: [
          'Decision theory for real-world applications',
          'Rationality: instrumental and epistemic perspectives',
          'Ethics of emerging technologies: frameworks for evaluation'
        ]
      }
    ]
  },
  
  'developer-tools': {
    name: 'Developer\'s Universe',
    clusters: [
      {
        name: 'Architecture-Patterns',
        tasks: [
          'Modern web application architecture: patterns and anti-patterns',
          'Microservices vs monoliths: decision frameworks and tradeoffs',
          'Distributed systems design: consistency, availability, partition tolerance'
        ]
      },
      {
        name: 'Tools-Libraries',
        tasks: [
          'Build a production-ready REST API framework with authentication and rate limiting',
          'Create a developer toolkit for rapid prototyping and deployment',
          'Design a code quality and security analysis tool'
        ]
      },
      {
        name: 'Best-Practices',
        tasks: [
          'Software engineering best practices: code review, testing, deployment',
          'Database design patterns for scalability and performance',
          'Security practices for modern web applications'
        ]
      }
    ]
  },
  
  'creative': {
    name: 'Creative & Design',
    clusters: [
      {
        name: 'Design-Systems',
        tasks: [
          'Comprehensive design system: principles, components, and guidelines',
          'User experience patterns: navigation, feedback, and interaction',
          'Accessibility in design: WCAG compliance and inclusive practices'
        ]
      },
      {
        name: 'Content-Creation',
        tasks: [
          'Content strategy frameworks: planning, creation, distribution',
          'Storytelling techniques across media: written, visual, interactive',
          'Brand voice and messaging: consistency and authenticity'
        ]
      },
      {
        name: 'Innovation-Methods',
        tasks: [
          'Creative problem-solving methodologies and techniques',
          'Design thinking process: empathize, define, ideate, prototype, test',
          'Innovation culture: fostering creativity in organizations'
        ]
      }
    ]
  },
  
  'integration': {
    name: 'Integration & Synthesis',
    clusters: [
      {
        name: 'Cross-Domain',
        tasks: [
          'Connections between AI, neuroscience, and cognitive science',
          'Physics principles applied to information systems',
          'Economic models for decentralized networks'
        ]
      },
      {
        name: 'Meta-Patterns',
        tasks: [
          'Universal patterns across domains: emergence, feedback, optimization',
          'Systems thinking: holistic approaches to complex problems',
          'Information theory and its applications across disciplines'
        ]
      },
      {
        name: 'Unified-Theory',
        tasks: [
          'Towards a unified framework for understanding complex systems',
          'Principles of effective knowledge synthesis and integration',
          'Building interconnected knowledge graphs: structure and navigation'
        ]
      }
    ]
  }
};

// ========================================
// TASK GENERATION
// ========================================

async function generateTasksForDomain(domainKey, options = {}) {
  const { multiplier = 1 } = options;
  
  const domain = TASK_TEMPLATES[domainKey];
  if (!domain) {
    throw new Error(`Unknown domain: ${domainKey}`);
  }
  
  console.log(`\n📋 Generating tasks for: ${domain.name}`);
  
  const allTasks = [];
  
  for (const cluster of domain.clusters) {
    console.log(`\n  📦 Cluster: ${cluster.name}`);
    
    for (let i = 0; i < multiplier; i++) {
      for (const taskDescription of cluster.tasks) {
        const task = {
          id: generateId(),
          task: taskDescription,
          assignedTo: 'any',
          priority: 'high',
          status: 'assigned',
          domain: domainKey,
          domainName: domain.name,
          clusterName: cluster.name,
          createdAt: new Date().toISOString(),
          metadata: {
            iteration: i + 1,
            totalIterations: multiplier
          }
        };
        
        allTasks.push(task);
        console.log(`    ✓ ${taskDescription.substring(0, 60)}...`);
      }
    }
  }
  
  console.log(`\n  ✅ Generated ${allTasks.length} tasks for ${domain.name}`);
  
  return allTasks;
}

async function generateMasterManifest() {
  console.log('\n🌌 GENERATING MASTER TASK MANIFEST');
  console.log('Trinity Knowledge Compendium - $5000 Credit Burn\n');
  
  const manifest = {
    project: 'Trinity Knowledge Compendium',
    version: '1.0.0',
    target: {
      totalBudget: 5000,
      targetTasks: 1050,
      estimatedCostPerTask: 4.76
    },
    domains: [],
    totalTasks: 0,
    generatedAt: new Date().toISOString()
  };
  
  // Generate tasks for all domains
  const domainKeys = Object.keys(TASK_TEMPLATES);
  
  for (const domainKey of domainKeys) {
    const tasks = await generateTasksForDomain(domainKey, { multiplier: 5 }); // 5x to hit 1000+ tasks
    
    manifest.domains.push({
      key: domainKey,
      name: TASK_TEMPLATES[domainKey].name,
      clusters: TASK_TEMPLATES[domainKey].clusters.length,
      tasks: tasks.length,
      estimatedCost: (tasks.length * manifest.target.estimatedCostPerTask).toFixed(2)
    });
    
    manifest.totalTasks += tasks.length;
    
    // Add to tasks file
    const existingTasks = await readJSON(TASKS_FILE);
    existingTasks.push(...tasks);
    await writeJSON(TASKS_FILE, existingTasks);
  }
  
  manifest.summary = {
    totalTasks: manifest.totalTasks,
    estimatedTotalCost: (manifest.totalTasks * manifest.target.estimatedCostPerTask).toFixed(2),
    domains: manifest.domains.length,
    clusters: manifest.domains.reduce((sum, d) => sum + d.clusters, 0)
  };
  
  // Save manifest
  await writeJSON(MASTER_MANIFEST_FILE, manifest);
  
  console.log('\n📊 MASTER MANIFEST GENERATED:\n');
  console.log(`   Total tasks: ${manifest.totalTasks}`);
  console.log(`   Domains: ${manifest.domains.length}`);
  console.log(`   Clusters: ${manifest.summary.clusters}`);
  console.log(`   Estimated cost: $${manifest.summary.estimatedTotalCost}`);
  console.log(`\n   Breakdown by domain:`);
  
  manifest.domains.forEach(d => {
    console.log(`     - ${d.name}: ${d.tasks} tasks ($${d.estimatedCost})`);
  });
  
  console.log(`\n✅ Manifest saved to: ${MASTER_MANIFEST_FILE}`);
  console.log(`✅ Tasks added to: ${TASKS_FILE}`);
  
  return manifest;
}

async function previewDomain(domainKey) {
  const domain = TASK_TEMPLATES[domainKey];
  if (!domain) {
    throw new Error(`Unknown domain: ${domainKey}`);
  }
  
  console.log(`\n📋 DOMAIN PREVIEW: ${domain.name}\n`);
  
  domain.clusters.forEach((cluster, idx) => {
    console.log(`${idx + 1}. Cluster: ${cluster.name}`);
    cluster.tasks.forEach((task, taskIdx) => {
      console.log(`   ${taskIdx + 1}. ${task}`);
    });
    console.log('');
  });
  
  const tasksPerCluster = domain.clusters.reduce((sum, c) => sum + c.tasks.length, 0);
  console.log(`Total tasks in domain: ${tasksPerCluster}`);
  console.log(`With 5x multiplier: ${tasksPerCluster * 5} tasks`);
}

async function listDomains() {
  console.log('\n📚 AVAILABLE DOMAINS:\n');
  
  Object.entries(TASK_TEMPLATES).forEach(([key, domain]) => {
    const clusters = domain.clusters.length;
    const tasks = domain.clusters.reduce((sum, c) => sum + c.tasks.length, 0);
    
    console.log(`${key.padEnd(20)} - ${domain.name}`);
    console.log(`${''.padEnd(20)}   ${clusters} clusters, ${tasks} base tasks (${tasks * 5} with 5x multiplier)`);
    console.log('');
  });
}

async function generateCustomTask(description, options = {}) {
  const {
    assignedTo = 'any',
    priority = 'normal',
    domain = 'custom',
    clusterName = 'custom-tasks'
  } = options;
  
  const task = {
    id: generateId(),
    task: description,
    assignedTo,
    priority,
    status: 'assigned',
    domain,
    clusterName,
    createdAt: new Date().toISOString()
  };
  
  const tasks = await readJSON(TASKS_FILE);
  tasks.push(task);
  await writeJSON(TASKS_FILE, tasks);
  
  console.log(`✅ Custom task created: ${task.id}`);
  
  return task;
}

async function clearTasks() {
  await writeJSON(TASKS_FILE, []);
  console.log('🗑️  All tasks cleared');
}

// ========================================
// CLI
// ========================================

async function main() {
  await fs.mkdir(TRINITY_DIR, { recursive: true });
  
  const command = process.argv[2];
  
  if (!command) {
    console.log('📋 Trinity Task Generator\n');
    console.log('Commands:');
    console.log('  manifest                       - Generate complete master manifest (1000+ tasks)');
    console.log('  generate <domain> [multiplier] - Generate tasks for specific domain');
    console.log('  preview <domain>               - Preview domain structure');
    console.log('  list                           - List all available domains');
    console.log('  custom <description>           - Add custom task');
    console.log('  clear                          - Clear all tasks');
    console.log('  status                         - Show task queue status');
    console.log('\nAvailable domains:');
    console.log('  technology, science, business, philosophy, developer-tools, creative, integration');
    process.exit(0);
  }
  
  if (command === 'manifest') {
    await generateMasterManifest();
  }
  else if (command === 'generate') {
    const domain = process.argv[3];
    const multiplier = parseInt(process.argv[4]) || 1;
    
    if (!domain) {
      console.error('Usage: generate <domain> [multiplier]');
      process.exit(1);
    }
    
    await generateTasksForDomain(domain, { multiplier });
  }
  else if (command === 'preview') {
    const domain = process.argv[3];
    
    if (!domain) {
      console.error('Usage: preview <domain>');
      process.exit(1);
    }
    
    await previewDomain(domain);
  }
  else if (command === 'list') {
    await listDomains();
  }
  else if (command === 'custom') {
    const description = process.argv.slice(3).join(' ');
    
    if (!description) {
      console.error('Usage: custom <description>');
      process.exit(1);
    }
    
    await generateCustomTask(description);
  }
  else if (command === 'clear') {
    await clearTasks();
  }
  else if (command === 'status') {
    const tasks = await readJSON(TASKS_FILE);
    const manifest = await readJSON(MASTER_MANIFEST_FILE, null);
    
    console.log('\n📊 Task Queue Status:\n');
    console.log(`Total tasks: ${tasks.length}`);
    
    if (manifest) {
      console.log(`\nFrom manifest: ${manifest.project}`);
      console.log(`Generated: ${new Date(manifest.generatedAt).toLocaleString()}`);
      console.log(`Estimated cost: $${manifest.summary?.estimatedTotalCost || 'N/A'}`);
    }
    
    const byDomain = {};
    tasks.forEach(t => {
      const domain = t.domain || 'unknown';
      byDomain[domain] = (byDomain[domain] || 0) + 1;
    });
    
    console.log('\nBy domain:');
    Object.entries(byDomain).forEach(([domain, count]) => {
      console.log(`  ${domain}: ${count} tasks`);
    });
  }
  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Export
module.exports = {
  generateTasksForDomain,
  generateMasterManifest,
  previewDomain,
  listDomains,
  generateCustomTask,
  TASK_TEMPLATES
};

// Run CLI
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
