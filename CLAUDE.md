# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**BusinessPlanEcosystem** ("Crypto-Ralph") is a cryptographically-verified business plan management system that tracks project progress using blockchain technology combined with Merkle tree integrity verification. The system maintains an immutable, verifiable ledger of completed user stories and validates document integrity.

## Quick Start

### Running the Project

```bash
python -m src.crypto_ralph.agent
```

This launches the main agent loop, which:
1. Reads the `PRD.json` file for pending user stories
2. Identifies the next task by priority
3. Executes the task logic
4. Mines a proof-of-work (with configurable difficulty)
5. Records completion to the blockchain (`progress.txt`)

### Current Status

- **Completed User Stories:** 3 of 4 (US-001, US-002, US-003)
- **Pending:** US-004 (Research sacred geometry and Dong Son drum principles)
- **Blockchain Height:** 4 blocks (genesis + 3 records in `progress.txt`)

## Code Architecture

The project uses a modular Python package structure under `src/crypto_ralph/`:

### Core Modules

**`blockchain.py` (125 lines)**
- Class: `Blockchain`
- Manages the cryptographic ledger for project progress tracking
- Key methods:
  - `mine_proof()`: Implements proof-of-work mining with configurable difficulty (via `PRD.json`)
  - `add_block()`: Records completed tasks as immutable blocks
  - `_load_ledger()`: Reads blockchain from `progress.txt`
  - `_create_genesis_block()`: Initializes chain
- Uses SHA-256 hashing with nonce-based mining
- Difficulty and max proof time configured in `PRD.json`

**`merkletree.py` (51 lines)**
- Functions for building cryptographic Merkle trees
- `build_merkle_tree()`: Constructs complete tree from hash list (handles odd-numbered nodes by duplicating last)
- `hash_pair()`: Creates parent node hashes from two children
- Purpose: Ensures integrity of document collections; outputs root hash representing entire document set state

**`agent.py` (81 lines)**
- Class: `CryptoRalphAgent`
- Main orchestrator implementing the "Mandala Protocol"
- Key methods:
  - `__init__()`: Initializes from project directory and `PRD.json`
  - `get_next_task()`: Identifies pending tasks by priority
  - `run_main_loop()`: Executes one cycle: Center → Recurse → Expand → Act → Record
- Workflow: Reads PRD, finds next pending task, executes it, mines proof, updates ledger

### Key Files

**`PRD.json`** - Product Requirements Document
- Defines consensus rules: `difficulty` (2 leading zeros), `required_verifiers` (1), `max_proof_time` (300s), `hash_algorithm` (sha256)
- Contains 4 user stories with priorities 1-4
- Tracks completion status, proof hashes, and verification data

**`progress.txt`** - Blockchain Ledger
- Append-only human-readable ledger of all completed user stories
- Contains 3 recorded blocks (Genesis + US-001, US-002, US-003)
- Each block includes: timestamp, previous hash, proof data, completion data
- Cannot be modified without invalidating chain

**`output/`** - Generated Artifacts
- `document_index.json`: Index of 56 business plan documents with SHA-256 hashes
- `merkle_tree.json`: Tree structure with root hash for verification (6 levels, 56 leaves)
- `document-summary.md`: Human-readable summary of indexed documents

## Development Environment

- **Language:** Python 3.14 (configured in `.vscode/settings.json`)
- **Terminal:** Git Bash (Windows)
- **Dependencies:** Standard library only (json, hashlib, datetime, pathlib, time) - no external packages required

## Design Patterns

1. **Blockchain-Based Progress Tracking**: Each completed user story becomes an immutable block; proof-of-work ensures computational validation; previous hash chain prevents tampering

2. **Modular Package Structure**: Separation of concerns (blockchain, merkletree, agent); enables independent testing and reuse

3. **Dual-Layer Verification**: Blockchain tracks task completion; Merkle tree ensures document integrity

4. **Mandala Protocol**: 5-step execution cycle reflecting philosophical approach to project execution

## Important Notes

- The `utils.py` module is currently a placeholder (2 lines) for future utility functions
- The `/data/` and `/docs/` directories are reserved for future use
- No external dependencies are currently required - all functionality uses Python standard library
- User stories are tracked with priorities; agent always executes the lowest-numbered pending story next
- Proof-of-work difficulty is consensus-based via `PRD.json` - changing it requires agreement from `required_verifiers`
