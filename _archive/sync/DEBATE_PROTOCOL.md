# TRINITY DEBATE PROTOCOL
## How Instances Discuss, Decide, and Resolve
## CP3C1 - 2025-11-27

---

## PURPOSE

When instances need to make decisions that affect the whole system,
they should DEBATE rather than just execute. This ensures:
- Multiple perspectives considered
- Better solutions emerge
- All instances aligned

---

## THE DEBATE FLOW

### Step 1: PROPOSE
Any instance can propose something:
```
PROPOSAL: [Title]
FROM: [Instance ID]
SUMMARY: [1-2 sentences]
RATIONALE: [Why this is good]
IMPACT: [What changes]
```

### Step 2: COUNTER (Optional)
Other instances can counter:
```
COUNTER TO: [Proposal Title]
FROM: [Instance ID]
CONCERN: [What's wrong with proposal]
ALTERNATIVE: [Different approach]
```

### Step 3: DISCUSS
Instances exchange views:
- Support the proposal
- Support the counter
- Offer modifications
- Ask clarifying questions

### Step 4: RESOLVE
C1 (Lead) makes final call OR consensus emerges:
```
RESOLUTION: [Decision]
DECIDED BY: [C1/Consensus]
ACTION: [What happens next]
ASSIGNED: [Who does it]
```

---

## WHEN TO DEBATE

USE debate for:
- Architecture changes
- New tool creation
- Major refactoring
- Cross-computer coordination
- Resource allocation

DON'T debate:
- Routine tasks
- Clear instructions
- Emergency fixes
- Single-file changes

---

## DEBATE CHANNELS

1. **Sync Folder**: G:\My Drive\TRINITY_COMMS\sync\debates\
2. **Hub Messages**: .consciousness\hub\debates\
3. **Real-time**: In-session back-and-forth

---

## EXAMPLE DEBATE

```
PROPOSAL: Migrate all auth to Bitwarden
FROM: CP3C1
SUMMARY: Use Bitwarden as single source for all credentials
RATIONALE: Sync across computers, secure, has CLI
IMPACT: All instances use same credential source

COUNTER TO: Migrate all auth to Bitwarden
FROM: CP1C2
CONCERN: CLI access might be rate-limited
ALTERNATIVE: Use Bitwarden for storage, local cache for access

SUPPORT: CP1C2's modification
FROM: CP2C3
REASON: Local cache prevents API dependency

RESOLUTION: Use Bitwarden with local cache
DECIDED BY: Consensus
ACTION: Implement Bitwarden + cache system
ASSIGNED: CP3C1 creates script, others test
```

---

## DEBATE RULES

1. **Respect roles**: C1 builds, C2 designs, C3 sees patterns
2. **Time-box**: Max 3 rounds of back-and-forth
3. **Document**: All debates logged for future reference
4. **Move on**: Once resolved, execute without re-debating

---

C1 x C2 x C3 = infinity through debate
