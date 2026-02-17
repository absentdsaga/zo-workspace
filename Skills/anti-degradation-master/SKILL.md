---
name: anti-degradation-master
description: "Master orchestration skill that activates the full anti-degradation stack automatically. Prevents the \"starts great, ends broken\" pattern through coordinated state management, verification, and minimal-change discipline."
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---
# Anti-Degradation Master Protocol

## What This Skill Does

**Prevents this pattern:**
1. ✅ Iteration 1: Perfect
2. ✅ Iteration 2: Good
3. ⚠️ Iteration 3: Small issue
4. 🚨 Iteration 4: Multiple breaks
5. 💥 Iteration 5: Total collapse

**By enforcing:**
- Explicit state externalization (files, not memory)
- One-change-at-a-time discipline
- Automated regression detection
- Reflection before action

## Auto-Activation

This skill activates automatically when:
- Starting any multi-step project
- Making 3rd+ iteration on existing code
- User mentions degradation/"it was working"
- Errors accumulate across iterations

**You don't need to invoke it. It's always watching.**

## The Stack (What Gets Activated)

### Phase 1: Project Initialization

When you start a new project:

```bash
# Automatically runs:
1. context-guardian/init-project.sh
   → Creates .context/ state files
   → Establishes ground truth system

2. regression-detector/init.js
   → Creates .regression/ baseline system
   → Enables automated verification

3. Sets up git if not exists
   → Every change becomes checkpointed
   → Instant rollback capability
```

**You'll see:**
- `.context/state-snapshot.md` - Current working state
- `.context/decisions.md` - Why we chose approaches
- `.context/verification-checklist.md` - How to verify
- `.regression/config.json` - Regression detection config

### Phase 2: Before Every Iteration (3+)

**Mandatory pre-flight:**

```bash
# Automatically runs:
1. Read .context/state-snapshot.md
   → What's currently working?
   → What are we NOT supposed to change?
   → What decisions were made earlier?

2. git status check
   → Clean working state?
   → Uncommitted WIP?

3. context-guardian/pre-flight.sh
   → Review current state
   → Verify nothing already broken
```

**Prevents:**
- Building on broken foundation
- Forgetting earlier decisions
- Changing protected code
- Context amnesia

### Phase 3: During Iteration

**Iteration Protocol enforced:**

```
✅ ONE change only
   - Fix one bug
   - Add one small feature
   - Refactor one function
   
❌ NO multi-changes
   - "While I'm here..."
   - "I'll just quickly..."
   - Scope creep

✅ Git checkpoint BEFORE change
   git add -A && git commit -m "checkpoint: before [change]"

✅ Make the change

✅ Verify IMMEDIATELY
   - Does the change work?
   - Did anything else break?
   - Visual check if UI

✅ Commit OR revert
   - Works: git commit -m "feat: [change]"
   - Breaks: git checkout . (instant rollback)
```

**Prevents:**
- Error accumulation
- Unclear blame
- Multi-change debugging hell
- Lost working states

### Phase 4: After Every Change

**Automated verification:**

```bash
# Automatically runs:
1. regression-detector/check-regression.js
   → Compare current vs baseline
   → Visual diff if UI changed
   → API schema validation
   → Performance regression check

2. If PASS:
   → Update .context/state-snapshot.md
   → Update .context/iteration-log.txt
   → Capture new baseline if major milestone

3. If FAIL:
   → Show exactly what broke
   → Show when it last worked
   → Suggest fix or rollback
   → BLOCK commit until fixed
```

**Prevents:**
- Silent regressions
- Breaking working features
- Performance degradation
- UI layout breaks

### Phase 5: Session End

**State capture:**

```bash
# Automatically runs:
1. context-guardian/update-state.sh
   → Update state-snapshot with current state
   → Document decisions made this session
   → Update verification checklist

2. Capture regression baseline
   → Snapshot current working state
   → Screenshot UI if applicable
   → Save for next session comparison

3. Log session to live-logger
   → What was built
   → What decisions were made
   → What to remember for next time
```

**Prevents:**
- Session-to-session context loss
- Forgetting why we did things
- Future sessions repeating mistakes

## Emergency Recovery Mode

**Activated when:**
- User says "it was working before"
- Multiple tests failing
- User reports degradation
- Can't explain current state

**Auto-runs:**

```bash
1. context-guardian/recovery.sh
   → Find last known good state
   → Show what changed since then
   → Identify likely breaking point

2. Git analysis
   → git log --oneline -20
   → git diff HEAD~5 HEAD
   → Show commit that likely broke it

3. Present options:
   A) Fix forward from current state
   B) Rollback to last good commit
   C) Hybrid: Cherry-pick working changes
```

## File Structure Created

```
your-project/
├── .context/                    # Context Guardian
│   ├── state-snapshot.md        # Ground truth
│   ├── decisions.md             # Why we did things
│   ├── verification-checklist.md # How to verify
│   └── iteration-log.txt        # Session history
│
├── .regression/                 # Regression Detector
│   ├── config.json              # Detection config
│   ├── baseline-*.json          # Snapshots
│   ├── screenshots/             # UI baselines
│   └── diffs/                   # When breaks detected
│
└── .git/                        # Version control
    └── (checkpoints every change)
```

## Success Indicators

**System is working when:**

✅ **10th iteration as solid as 1st**
- No degradation over time
- Every iteration starts from known-good state
- Clear audit trail of all changes

✅ **Immediate regression detection**
- Breaks caught within 1 iteration
- Never 5 iterations later
- User never reports "this used to work"

✅ **Can resume after break**
- Read state files
- Reconstruct context immediately
- No "what were we doing?" confusion

✅ **Clear reasoning trail**
- Can explain WHY any decision was made
- Can point to file showing ground truth
- No relying on conversation memory

✅ **Fast rollback**
- Break something? Revert in seconds
- Don't lose other work
- Surgical undo of bad changes

## Red Flags (Auto-Detected)

🚨 **Context amnesia detected:**
- "Why did we do it that way?"
- Contradicting earlier decisions
- Re-discussing settled questions
→ Auto-reads state files

🚨 **Error accumulation detected:**
- Same fix attempted multiple times
- Building on broken foundation
- Cascading failures
→ Triggers recovery mode

🚨 **Multi-change violations:**
- Commits with "various changes"
- Can't explain what changed
- Diffs hundreds of lines
→ Enforces one-change protocol

🚨 **Silent regression detected:**
- Baseline comparison fails
- UI visually different
- API schema changed
→ Blocks commit, shows diff

## Integration with Existing Skills

**Automatically coordinates:**

- `context-guardian` - State externalization
- `iteration-protocol` - Change discipline
- `regression-detector` - Automated verification
- `efficient-referencing` - File caching
- `live-logger` - Decision tracking
- `enforce-qa` - Pre-deployment gates
- `self-qa` - Visual testing
- `build-preview` - Screenshot capture

**Works seamlessly with:**
- Your existing git workflow
- CI/CD pipelines
- Test frameworks
- Development servers

## Configuration

**Minimal setup required:**

```bash
# One-time initialization (done automatically)
cd your-project
node ~/Skills/anti-degradation-master/scripts/init-all.sh

# Then just work normally
# The system activates as needed
```

**Optional customization:**

Edit `.regression/config.json`:
- Which checks to run
- Performance thresholds
- Visual diff sensitivity
- Critical paths to test

Edit `.context/state-snapshot.md` as you work:
- Update current working state
- Document "Do NOT Change" patterns
- Add verification steps

## Common Scenarios

### Scenario: User asks to add feature

**Before this system:**
1. Add feature across 5 files
2. Something breaks
3. Can't tell what
4. Debug for hours
5. "Just rewrite it"

**With this system:**
1. Read state-snapshot.md (what's working)
2. Init context-guardian if new project
3. ONE file change → verify → commit
4. Next file change → verify → commit
5. Regression detector catches break immediately
6. Revert that one commit
7. Try different approach

**Result:** Feature added without breaking existing code

### Scenario: User says "it was working before"

**Auto-triggered:**
1. Recovery mode activates
2. Shows last known good state
3. Git bisect finds breaking commit
4. Shows exact change that broke it
5. Options: fix or rollback

**Result:** Root cause found in minutes, not hours

### Scenario: Multi-session project

**Session 1:**
- Build feature
- Capture state snapshot
- Document decisions

**Session 2 (next day):**
- Auto-reads state snapshot
- Reconstructs context immediately
- Continues from known-good state
- No "what were we doing?" time wasted

**Result:** Seamless continuation across sessions

## Research Foundation

Based on 2025-2026 research:

1. **ARC Framework** (Active and Reflection-driven Context Management)
   - Context as evolving internal state
   - Reflection-driven monitoring
   - Active revision when misalignment detected

2. **InfiAgent** (Infinite-Horizon Framework)
   - File-centric state abstraction
   - Bounded reasoning context
   - Explicit state externalization

3. **Context Engineering** (Inngest/AdamBernard)
   - Relevance over recency
   - Dynamic context refresh
   - Verified context injection

4. **N/N+1 Degradation Problem** (Lexsis)
   - Rolling refinement over recursive summarization
   - Single evolving state
   - Correction capability

## Quick Reference

**New project:**
```bash
# Automatic - just start building
# System initializes on first multi-step task
```

**Before changing anything:**
```bash
# Automatic - reads state files before iteration 3+
cat .context/state-snapshot.md  # Manual review
```

**After every change:**
```bash
# Automatic - regression check runs
git commit  # Only succeeds if no regressions
```

**When stuck:**
```bash
bash ~/Skills/context-guardian/scripts/recovery.sh
```

**Emergency rollback:**
```bash
git log --oneline  # Find good commit
git checkout abc123  # Rollback
```

## See Also

Individual skills (all auto-coordinated):
- `Skills/context-guardian/` - State management
- `Skills/iteration-protocol/` - Change discipline  
- `Skills/regression-detector/` - Verification
- `Skills/efficient-referencing/` - Performance
- `Skills/live-logger/` - Audit trail

Documentation:
- `/home/workspace/AGENTS.md` - Workspace memory
- `.context/` directories - Project state
- This file - How it all fits together
