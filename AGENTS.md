# Workspace Memory & Anti-Degradation System

## Critical Pattern: Prevent Build Degradation

**THE PROBLEM YOU'VE OBSERVED:**
Builds start perfect, then progressively degrade with each iteration until everything breaks.

**ROOT CAUSE (Research-Backed):**
- Context rot: AI loses track of earlier decisions as conversation grows
- Error anchoring: Early mistakes become "facts" in later reasoning  
- Accumulation without pruning: Every iteration adds noise without removing irrelevant data
- No verification: Changes made without checking what breaks

**THE SOLUTION (Now Implemented):**

### 1. Context Guardian (`Skills/context-guardian/`)
**Explicit state externalization** - Don't rely on conversation memory
- Before iteration 3+: Read `.context/state-snapshot.md` for ground truth
- After each change: Update state files with rolling refinement (correct errors, don't layer)
- Files are source of truth, not conversation history

### 2. Iteration Protocol (`Skills/iteration-protocol/`)
**One change at a time discipline**
- ONE change → Verify → Commit → Next change
- Never "while I'm here" multi-changes
- Git checkpoint before every change for instant rollback
- Catch errors immediately, not 5 iterations later

### 3. Regression Detector (`Skills/regression-detector/`)
**Automated baseline comparison**
- Capture working state after each successful build
- Before claiming "done", verify nothing broke since baseline
- Visual diffs, API schema checks, performance regression detection

## Active Rules (Automatically Applied)

1. **Before 3rd+ iteration**: Activate context-guardian, read state files
2. **User reports degradation**: Immediately run recovery.sh, check state-snapshot.md
3. **Starting new project**: Proactively init context-guardian to prevent degradation
4. **After working build**: Capture regression baseline

## Skills Ecosystem

**Anti-Degradation Stack:**
- `context-guardian` - State externalization across sessions
- `iteration-protocol` - Minimal change discipline  
- `regression-detector` - Automated regression catching
- `efficient-referencing` - Cache file structure, avoid re-reading
- `live-logger` - Track decision trail automatically
- `enforce-qa` - Pre-deployment checkpoint validation
- `self-qa` - Automated visual testing
- `build-preview` - Screenshot capture and review

**Other Skills:**
- `spatial-worlds` - Proximity voice chat worlds with Chrono Trigger art
- `isometric-sprite-gen` - Chrono Trigger style sprite generation
- `phaser-iso-engine` - Optimized Phaser for isometric worlds
- `multiplayer-sync-iso` - Real-time multiplayer for isometric games
- `workflow-orchestrator` - Master orchestration of all skills
- ... (see Skills/ directory for full list)

## Projects

### Survival Agent (`Projects/survival-agent/`)
**Paper trading bot with live P&L tracking**
- Status: Active development
- Stack: TypeScript, Helius API, Jupiter, Shocked extraction
- Key files: 
  - `testing/paper-trade-bot.ts` - Main trading logic
  - `core/jupiter-validator.ts` - Swap validation
  - `testing/CRITICAL-BUG-FIX.md` - Known issues and fixes

## Working with Dioni

**Preferences:**
- Extreme concision - fewest words that fully solve the task
- No filler ("Great question!", "I'd be happy to help!")
- Actions over words - just do it
- Be resourceful before asking - try to figure it out first
- Build quality over speed - but both matter

**Communication style:**
- Have opinions, preferences
- Allowed to disagree
- Skip jargon unless user is technical
- Assume non-technical by default unless clear otherwise

**Anti-Patterns to Avoid:**
- ❌ Changing 10 things at once then debugging
- ❌ Relying on conversation history for ground truth
- ❌ "I think this works" without verification
- ❌ Building on broken foundation
- ❌ Losing track of earlier decisions

## Emergency Recovery

When builds have degraded:

```bash
# 1. Find last known good state
cd <project>
cat .context/state-snapshot.md

# 2. Check git history
git log --oneline -20
git diff HEAD~5 HEAD

# 3. Identify where it broke
bash ~/Skills/context-guardian/scripts/recovery.sh

# 4. Either:
#    A) Fix forward from current state
#    B) Rollback to last good commit and rebuild
```

## Context Management Strategy

**Bounded Context Windows:**
1. Store detailed decisions in FILES (.context/, AGENTS.md)
2. Keep active reasoning context small and relevant
3. Reconstruct context from snapshots + recent actions only
4. Archive history to files, don't carry it all in conversation

**Rolling Refinement:**
- ONE evolving state document per project
- Update with corrections (don't create layers of summaries)
- Each update can FIX earlier errors instead of building on them

**Reflection-Driven Monitoring:**
- Before each change: Review what's currently working
- After each change: Verify nothing broke
- Detect misalignment early, before it compounds

## Success Metrics

**Anti-degradation system is working when:**
- ✅ 10th iteration works as well as 1st iteration
- ✅ Can take break mid-project and resume without confusion  
- ✅ Can explain WHY something works, not just THAT it works
- ✅ Regressions caught immediately, not 3 changes later
- ✅ User never says "it was working before"
- ✅ Git history reads like a clear story

**Red flags:**
- 🚨 "Wait, why did we do it that way?"
- 🚨 Breaking something that was working
- 🚨 Repeating same fix multiple times
- 🚨 Contradicting earlier decisions
- 🚨 "Everything was working, now nothing works"

---

*This file is your long-term memory. Update it as context evolves. Read it at session start.*
