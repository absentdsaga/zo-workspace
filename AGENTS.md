# Agent Memory & Guidelines

## 🎯 Core Principle: VERIFY BEFORE CHANGE

Every project has a **PROJECT-STATE.md** or **AGENTS.md** file that documents:
- The ONE canonical file for each component
- Critical file paths and their relationships
- How to safely make changes without breaking working systems

**ALWAYS READ THIS FILE FIRST** before making changes to any project.

## 📋 Change Protocol

### Before Any Code Change:

1. **Read the project state file**
   ```bash
   cat PROJECT-STATE.md  # or AGENTS.md in subdirectory
   ```

2. **Verify current state**
   - What's running?
   - What files exist?
   - What data would be lost?

3. **Backup working state**
   ```bash
   cp file.ts file.ts.backup-$(date +%Y%m%d-%H%M)-REASON
   ```

4. **Make ONE change at a time**
   - Edit the canonical file (never create alternatives)
   - Test compilation
   - Verify it works

5. **Document the change**
   - Update PROJECT-STATE.md with what changed
   - Note any new file paths or dependencies

## 🚨 Anti-Patterns to Avoid

### ❌ Creating Alternative Versions
**NEVER:**
- `bot-v2.ts` when `bot.ts` exists
- `fixed-version.ts` when original exists  
- `new-scanner.ts` when `scanner.ts` exists

**INSTEAD:**
- Backup the original
- Edit the original in place
- Keep ONE source of truth

### ❌ File Path Mismatches
**NEVER:**
- Have bot write to `fileA.json` and monitor read from `fileB.json`
- Use hardcoded paths that differ between files

**INSTEAD:**
- Grep for all file path references before changing
- Update ALL references when paths change
- Verify after restart

### ❌ Destructive Restarts
**NEVER:**
- Restart without checking what's in memory
- Overwrite data files with empty states
- Skip the "what would be lost?" check

**INSTEAD:**
- Check current state
- Preserve open positions/data
- Load existing state on restart

## 🛠️ Common Projects

### Survival Agent (`Projects/survival-agent/`)
- **State file**: `PROJECT-STATE.md`
- **Main bot**: `testing/paper-trade-bot.ts` (ONLY ONE)
- **Trades**: `/tmp/paper-trades-master.json`
- **Critical**: Always check open positions before restart

### Spatial Worlds (`Skills/spatial-worlds/`)
- **State file**: `AGENTS.md` in skill directory
- Check for build/deployment state
- Verify client/server consistency

## 📝 Update This File

When discovering organizational issues, ADD TO THIS FILE:
- New anti-patterns observed
- Project-specific gotchas
- Recovery procedures

This file is YOUR memory across sessions. Keep it current.
