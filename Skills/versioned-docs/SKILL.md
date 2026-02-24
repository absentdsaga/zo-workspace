---
name: versioned-docs
description: Enforce version headers on all analysis documents to prevent referencing outdated/wrong information
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Versioned Documentation System

## Problem This Solves

AI creates analysis documents that become outdated when settings change. Without version tracking:
- References wrong/old settings in responses
- Claims settings are X when they're actually Y
- Creates confusion about "current" state
- No way to know if document is trustworthy

## Solution

Every analysis/status document MUST have version header at the top.

## Required Header Format

```markdown
# Document Title

**Version:** vX.Y.Z
**Date:** YYYY-MM-DD HH:MM UTC
**Bot Version:** vX.Y (from paper-trade-bot.ts header)
**Git Commit:** [short-hash] [commit message]
**Status:** [CURRENT | SUPERSEDED | ARCHIVED]

---

[document content]
```

## Version Number Rules

**Format:** vMAJOR.MINOR.PATCH

- **MAJOR (X):** Bot version changed, strategy overhaul, major setting changes
  - Example: v1.0.0 → v2.0.0 when bot v2.0 → v2.1

- **MINOR (Y):** New analysis data, setting adjustments, meaningful updates
  - Example: v2.0.0 → v2.1.0 when MIN_LIQUIDITY changed

- **PATCH (Z):** Typo fixes, clarifications, no content change
  - Example: v2.1.0 → v2.1.1 when fixing grammar

## Status Tags

1. **CURRENT** = This is accurate right now, trust this
2. **SUPERSEDED** = Replaced by newer doc, don't reference
3. **ARCHIVED** = Historical record only, outdated

## Document Types That Need Versions

**Required:**
- ✅ Settings breakdowns (e.g., COMPLETE_SETTINGS_BREAKDOWN.md)
- ✅ Performance analysis
- ✅ Bug reports and fixes
- ✅ Strategy changes
- ✅ Filter/threshold updates
- ✅ Status updates

**Not Required:**
- ❌ Raw logs (use timestamps)
- ❌ Trade history files
- ❌ Temporary scratch work

## Enforcement Rules

### When Creating New Docs

1. Start with version header (use template in `/.version-template.md`)
2. Check current bot version: `head -10 testing/paper-trade-bot.ts | grep VERSION`
3. Check git commit: `git log --oneline -1`
4. Set status to CURRENT
5. Initial version: v1.0.0

### When Updating Existing Docs

1. Increment version number (major/minor/patch)
2. Update date
3. If content is completely replaced: mark old as SUPERSEDED
4. If minor update: increment version, keep CURRENT status

### When Doc Becomes Outdated

1. Change status from CURRENT → SUPERSEDED
2. Add note pointing to replacement doc
3. Optionally rename file: `FILENAME.md → FILENAME.md.SUPERSEDED`

## Example: Real Case

**Problem:** Created FILTERS_UPGRADED.md claiming:
```
MIN_VOLUME_24H: $1k → $500k
```

**Reality:** Volume was never changed to $500k, stayed at $1k.

**Result:** AI referenced wrong document and told user incorrect info.

**Solution with Versioning:**

```markdown
# Filter Upgrade Complete

**Version:** v1.0.0
**Date:** 2026-02-16 12:26 UTC
**Bot Version:** v2.1
**Git Commit:** 58d9673
**Status:** SUPERSEDED (INCORRECT - see CURRENT_VERSION.md)

## CORRECTION
This document claimed MIN_VOLUME changed to $500k.
That was WRONG. Volume is still $1k.

See CURRENT_VERSION.md for accurate settings.
```

## Reference Document

**Always maintain:** `CURRENT_VERSION.md` in project root

This is the single source of truth showing:
- Current bot version
- All current settings
- What changed since last git commit
- Quick verification commands

## Usage

### Before Creating Analysis Doc

1. Read current version:
   ```bash
   cat Projects/survival-agent/CURRENT_VERSION.md
   ```

2. Use template:
   ```bash
   cat /.version-template.md
   ```

3. Fill in version info at top of doc

### Before Referencing a Doc

1. Check status tag:
   - CURRENT? Safe to reference
   - SUPERSEDED? Find replacement
   - ARCHIVED? Don't use

2. Check date:
   - Recent? Probably accurate
   - Old? Verify with current code

3. Check bot version:
   - Matches current? Good
   - Different? Settings may have changed

## Implementation

This skill doesn't have scripts - it's a **discipline/process**.

Enforce it by:
1. Always adding version headers
2. Updating CURRENT_VERSION.md when settings change
3. Marking old docs as SUPERSEDED
4. Checking version tags before referencing docs

## Template Location

**Global template:** `/.version-template.md`
**Current state:** `Projects/survival-agent/CURRENT_VERSION.md`

## Version History

- v1.0.0 (2026-02-16): Initial skill created after $500k volume confusion
