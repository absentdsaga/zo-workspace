# Versioning System - MANDATORY

## Rule: ALWAYS Check Version Before Creating Docs

### Step 1: Check Current Bot Version
```bash
head -10 Projects/survival-agent/testing/paper-trade-bot.ts | grep "COORDINATOR v"
```

### Step 2: Check Git Commit
```bash
cd Projects/survival-agent && git log --oneline -1
```

### Step 3: Check Current Settings
```bash
cat Projects/survival-agent/CURRENT_VERSION.md
```

### Step 4: Use Version Header Template
```markdown
**Version:** v[X.Y.Z]
**Date:** YYYY-MM-DD HH:MM UTC
**Bot Version:** v[from step 1]
**Git Commit:** [from step 2]
**Status:** CURRENT
```

## Rule: Update CURRENT_VERSION.md When Settings Change

Whenever you change:
- MIN_LIQUIDITY
- MIN_VOLUME_24H
- Any trading threshold
- Bot version

You MUST update `Projects/survival-agent/CURRENT_VERSION.md`

## Rule: Mark Old Docs as SUPERSEDED

When creating new analysis that replaces old:
1. Change old doc status: CURRENT → SUPERSEDED
2. Add note pointing to new doc
3. Optionally rename: filename.md → filename.md.SUPERSEDED

## Enforcement

This is in user rules (conditional):
- CONDITION: Creating any analysis, status, or settings document
- RULE: Use versioned-docs skill to add version header

## Quick Reference

**Current bot version:** v2.3
**Template location:** `/.version-template.md`
**Current state:** `Projects/survival-agent/CURRENT_VERSION.md`
