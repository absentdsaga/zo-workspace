---
name: iteration-protocol
description: Strict protocol for iterative changes that prevents error accumulation. Each iteration starts from verified baseline, makes minimal changes, and validates before proceeding. Prevents the "change everything and hope" anti-pattern.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# Iteration Protocol - Minimal Change Discipline

## The Anti-Pattern

**What causes degradation:**
1. Make 5 changes at once
2. Something breaks
3. Can't tell which change caused it
4. Try to fix by making 5 MORE changes
5. Now 3 things are broken
6. Spiral continues until total rewrite needed

**This is why builds degrade.**

## The Protocol

**RULE: One change at a time. Verify. Then next change.**

### Before ANY Change

```bash
# 1. Verify current state works
npm run dev  # or whatever starts your app
# Manually test core functionality
# Take screenshot if UI-based

# 2. Commit current working state (even if WIP)
git add -A
git commit -m "checkpoint: working state before [change description]"

# 3. Document what you're about to change
echo "$(date): Changing X because Y" >> .context/iteration-log.txt
```

### Making the Change

**ONLY change ONE thing:**
- ✅ Fix one bug
- ✅ Add one small feature
- ✅ Refactor one function
- ❌ "While I'm here, let me also..."
- ❌ "I'll just quickly fix this other thing..."

**If you catch yourself making multiple changes, STOP:**
```bash
# Commit what you have so far
git add -A
git commit -m "partial: [first change]"

# Then make second change separately
```

### After the Change

```bash
# 1. IMMEDIATELY verify
npm run dev
# Test the thing you just changed
# Test that nothing else broke

# 2. If it works:
git add -A
git commit -m "feat: [what changed and why it works]"
echo "$(date): ✅ [change] - verified working" >> .context/iteration-log.txt

# 3. If it breaks:
git diff  # See what you changed
git checkout .  # Revert
# Try again with smaller change OR different approach
echo "$(date): ❌ [change] - reverted, trying different approach" >> .context/iteration-log.txt
```

## Emergency: When You've Already Made Too Many Changes

**You're here because you changed 10 things and now it's broken.**

```bash
# 1. See what you changed
git diff HEAD

# 2. Stash everything
git stash

# 3. Verify the base still works
npm run dev  # Should work now

# 4. Apply changes ONE AT A TIME
git stash show -p | head -50  # See first change
# Manually apply JUST that one change
# Test it
# Commit if works

# Repeat until you find the breaking change
```

## Integration with Context Guardian

```bash
# Initialize both systems
cd your-project
bash ~/Skills/context-guardian/scripts/init-project.sh
echo "# Iteration Log" > .context/iteration-log.txt
git init  # If not already a git repo

# Before each session
cat .context/state-snapshot.md  # Know what's working
git status  # Clean slate or WIP?

# During iteration
# Use this protocol for EVERY change

# After session
bash ~/Skills/context-guardian/scripts/update-state.sh "Session complete: [summary]"
git log --oneline -10  # Review your iteration trail
```

## When to Break the Protocol

**Never.** 

Well, almost never. The only exception:
- Emergency production fix where verification would take longer than risk tolerance

Otherwise: **One change. Verify. Commit. Repeat.**

## Why This Works

**From research on error accumulation:**

1. **Isolated Changes**: When something breaks, you know exactly what caused it
2. **Revertability**: Can undo last change without losing other work  
3. **Verification Points**: Catch errors immediately, not 10 changes later
4. **Psychological Safety**: Small changes less scary than big rewrites
5. **Blame Clarity**: Git history shows exact change that introduced bug

**The discipline prevents:**
- ❌ Error anchoring (building on broken foundation)
- ❌ Lost-in-the-middle (can't remember what you changed)
- ❌ Accumulation debt (changes piling up unverified)
- ❌ Context amnesia (commits document reasoning)

## Common Objections

**"This is too slow"**
- No. What's slow is making 10 changes, breaking everything, spending 2 hours debugging which change broke it, then starting over.
- This protocol is FASTER in total time.

**"I know these changes are all related"**
- They're still separate changes. Make them separately.
- Each one might work. The combination might not. Test incrementally.

**"I'm just prototyping"**
- Then you're not iterating, you're exploring. That's fine.
- But when prototype becomes "the code", switch to this protocol.

## Success Metrics

**This protocol is working when:**
- ✅ You can explain exactly what the last commit changed
- ✅ If something breaks, reverting one commit fixes it
- ✅ 10 iterations later, nothing is broken from iteration 1
- ✅ Git history reads like a clear story
- ✅ You catch bugs in minutes, not hours

**Red flags:**
- 🚨 Commits that say "fix stuff" or "various changes"
- 🚨 Can't remember what you changed in last 30 minutes
- 🚨 "Everything was working, now nothing works"
- 🚨 Git diffs that are hundreds of lines
- 🚨 Afraid to run the app because it might be broken

## Quick Reference Card

```
ITERATION PROTOCOL
==================

BEFORE: 
□ Current state works?
□ Git committed?
□ Know what I'm changing?

CHANGE:
□ ONE thing only
□ No "while I'm here" additions

AFTER:
□ Test the change
□ Test nothing broke
□ Commit OR revert
□ Log result

STUCK?
□ git diff HEAD
□ Revert to last working commit
□ Smaller change
```

## Examples

**❌ BAD Iteration:**
```bash
# Makes 5 changes at once
- Update API endpoint
- Change CSS styling  
- Add new feature
- Refactor old code
- Update dependency

# 2 hours later: "Something is broken, not sure what"
```

**✅ GOOD Iteration:**
```bash
# Commit 1
git commit -m "feat: update API endpoint to v2 - tested with curl"

# Verify, works

# Commit 2  
git commit -m "style: center header - screenshot verified"

# Verify, works

# Commit 3
git commit -m "feat: add search filter - tested with 3 queries"

# Verify, BREAKS

# Immediate revert
git revert HEAD
# Try different approach to search filter
```

## See Also

- `context-guardian`: State management across sessions
- `webapp-testing`: Automated verification
- `self-qa`: Automated screenshot testing
- `enforce-qa`: Pre-deployment checkpoint
