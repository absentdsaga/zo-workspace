---
name: context-guardian
description: Prevents the catastrophic degradation pattern where builds start strong then collapse under iteration. Implements active context management, reflection-driven monitoring, and explicit state externalization to maintain coherence across long sessions.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# Context Guardian - Anti-Degradation System

## The Problem

**You've noticed this pattern:**
1. Initial build: Everything works perfectly
2. First iteration: Minor fixes, still good
3. Second iteration: Small errors creep in
4. Third+ iterations: Everything breaks, context is lost, earlier decisions are forgotten

This is **context rot** - the systematic degradation of AI agent performance as interaction history accumulates.

## Root Causes (Research-Backed)

Based on 2025-2026 research on AI agent reliability:

1. **Context Amnesia**: Critical early decisions get buried in growing history
2. **Error Anchoring**: Early mistakes become "facts" in later reasoning
3. **Semantic Drift**: Repeated summarization distorts original intent
4. **Lost-in-the-Middle**: AI focuses on recent + initial context, forgets middle
5. **Accumulation Without Pruning**: Every iteration adds noise without removing irrelevant data

## The Solution: Active Context Management

### Core Principles

**1. Explicit State Externalization**
- Store critical decisions in FILES, not just conversation
- Create snapshot files that capture "ground truth" at each major milestone
- Reference files instead of re-reading conversation history

**2. Reflection-Driven Monitoring**
- Before each change: Review what's currently working
- After each change: Verify nothing broke
- Detect misalignment early, before it compounds

**3. Rolling Refinement (Not Recursive Summarization)**
- Maintain ONE evolving state document
- Update it with corrections, don't create layers of summaries
- Each update can FIX earlier errors instead of building on them

**4. Bounded Context Windows**
- Keep active reasoning context small and relevant
- Archive detailed history to files
- Reconstruct context from snapshots + recent actions only

## Usage

### When to Activate This Skill

**ALWAYS use this skill when:**
- Building anything across 3+ conversation turns
- User says "it was working before" or "why did this break"
- Making changes to existing working code
- User mentions degradation, getting worse, or losing progress

**Activate PROACTIVELY when:**
- Starting any multi-session project
- Before making the 3rd+ iteration on the same component
- User describes a complex build with multiple features

### Workflow

**Phase 1: Initialize (First Build)**

1. **Create State Snapshot**: `state-snapshot.md`
   - What we built
   - Key architectural decisions
   - What's working and WHY it works
   - Critical dependencies and assumptions

2. **Create Test Manifest**: `verification-checklist.md`
   - How to verify core functionality
   - What MUST keep working
   - Known limitations/edge cases

3. **Create Decision Log**: `decisions.md`
   - Why we chose approach X over Y
   - What we explicitly decided NOT to do
   - Future gotchas to remember

**Phase 2: Before Each Iteration**

1. **Read State Files** (don't rely on conversation memory)
   ```bash
   cat state-snapshot.md decisions.md verification-checklist.md
   ```

2. **Pre-flight Check**
   - What's currently working?
   - What are we about to change?
   - What could this break?

3. **Bounded Context Planning**
   - Only load relevant context for THIS change
   - Archive irrelevant history

**Phase 3: After Each Change**

1. **Verification** (MANDATORY)
   - Run tests from verification-checklist.md
   - Capture screenshots if UI changed
   - Check for regressions

2. **Update State Files** (Rolling Refinement)
   - Update state-snapshot.md with new state
   - CORRECT any errors in previous understanding
   - Update decisions.md if we learned something

3. **Prune Context**
   - What can we archive?
   - What's no longer relevant?

**Phase 4: Recovery (When Things Break)**

1. **State Reconstruction**
   - Read state-snapshot.md from last known good state
   - Identify where drift started
   - Roll back to working baseline

2. **Root Cause Analysis**
   - What assumption was wrong?
   - What context was lost?
   - Update decision log to prevent recurrence

3. **Fresh Start Option**
   - Sometimes best to rebuild from clean state
   - Use state files to guide rebuild
   - Don't carry forward accumulated errors

## File Templates

### state-snapshot.md
```markdown
# Project State Snapshot
*Last Updated: [timestamp]*

## Current Working State
- Feature X: ✅ Working (tested via Y)
- Feature Z: ✅ Working (verified by screenshot)
- Known Issues: [none/list]

## Architecture
- Core stack: [technologies]
- Key files: [file1, file2]
- Critical dependencies: [what depends on what]

## What Works and WHY
- Feature X works because: [explanation]
- We're using approach Y because: [decision rationale]

## Do NOT Change
- [List of things that work and should stay untouched]
- [Patterns that are working well]
```

### decisions.md
```markdown
# Architectural Decisions

## [Decision 1]: [Choice Made]
**Date:** [timestamp]
**Context:** [What problem were we solving]
**Options Considered:**
- Option A: [why not]
- Option B: [why not]
- Option C: [why we chose this]

**Consequences:**
- [What this enables]
- [What this prevents]
- [Future constraints]

**DO NOT:** [Common mistakes to avoid]
```

### verification-checklist.md
```markdown
# Verification Checklist

## Core Functionality Tests
- [ ] Test 1: [How to verify] - Expected: [result]
- [ ] Test 2: [How to verify] - Expected: [result]

## Visual Tests (if applicable)
- [ ] Screenshot: [What to capture] - Verify: [what should appear]

## Regression Tests
- [ ] Previous bug X: [How to verify it's still fixed]

## Performance Baselines
- [ ] Load time: [expected range]
- [ ] Response time: [expected range]
```

## Integration with Existing Skills

**Works with:**
- `efficient-referencing`: Cache state files instead of re-reading
- `self-qa`: Automated verification after changes
- `build-preview`: Visual verification system
- `live-logger`: Track decision trail automatically
- `enforce-qa`: Checkpoint validation before claiming "done"

**Replaces:**
- Ad-hoc "let me check what we did" searches
- Relying on conversation history for ground truth
- Recursive debugging without state reconstruction

## Emergency Recovery

**When everything is broken:**

```bash
# 1. Find last known good state
cat state-snapshot.md | grep "Last Updated"

# 2. Check what changed since then
git diff HEAD~3 HEAD  # or check logs

# 3. Read decisions to understand original intent
cat decisions.md

# 4. Either:
#    A) Fix forward: Update state to match current + fix
#    B) Roll back: Restore to last good state + try again
```

## Success Metrics

**This skill is working when:**
- ✅ 5th iteration works as well as 1st iteration
- ✅ Can take break mid-project and resume without confusion
- ✅ Can explain WHY something works, not just THAT it works
- ✅ Regressions caught immediately, not 3 changes later
- ✅ User says "wow, you remembered that detail from earlier"

**Warning signs to watch for:**
- 🚨 "Wait, why did we do it that way?" (lost context)
- 🚨 Breaking something that was working (no verification)
- 🚨 Repeating same fix multiple times (error anchoring)
- 🚨 Contradicting earlier decisions (semantic drift)

## References

Based on cutting-edge research:
- ARC Framework (Active and Reflection-driven Context Management)
- InfiAgent (Infinite-Horizon Framework via State Externalization)
- Context Engineering principles from Inngest/AdamBernard
- N/N+1 Summarization Degradation Problem (Lexsis research)
