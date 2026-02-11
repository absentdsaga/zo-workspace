# Auto-QA Skill

**Purpose:** Unified skill that automatically verifies, validates, and iterates on fixes until the output matches specifications.

## What This Skill Does

Combines three critical verification layers:
1. **Technical QA** - TypeScript compilation, builds, server health
2. **Visual Verification** - What humans actually see vs what code claims
3. **Auto-Fix Loop** - Iterates on fixes until spec is met

## The Problem This Solves

**Common Failure Pattern:**
```
AI: "I built feature X!"
Code: ✅ Compiles
Build: ✅ Succeeds
Server: ✅ Running
User: "I see a black screen"
Reality: ❌ Feature not visible
```

## Core Principle

**Code working ≠ Visually correct ≠ Spec compliant**

This skill ensures all three are true before claiming completion.

## Usage

```bash
# Run full auto-QA cycle
./auto-qa.sh <project-path> <spec-file> <screenshot-path>

# Example:
./auto-qa.sh /home/workspace/Skills/spatial-worlds VISUAL-SPEC.md screenshot.png
```

## What It Does

1. **Pre-Flight Technical Checks**
   - TypeScript compilation
   - Build success
   - Server running
   - HTTP responding
   - Output artifacts exist

2. **Visual Verification**
   - Compare screenshot against visual spec
   - Identify what's missing
   - Identify what's incorrect
   - Flag perception gaps

3. **Root Cause Analysis**
   - Analyze rendering pipeline
   - Check coordinate systems
   - Verify graphics API calls
   - Inspect depth/z-index issues

4. **Auto-Fix Iteration**
   - Generate fix hypotheses
   - Apply fixes
   - Rebuild
   - Request new screenshot
   - Repeat until spec met

## Files

- `SKILL.md` - This documentation
- `auto-qa.sh` - Main entry point
- `scripts/technical-qa.sh` - Pre-flight technical checks
- `scripts/visual-verify.sh` - Visual verification against spec
- `scripts/root-cause.sh` - Debug rendering issues
- `scripts/auto-fix.sh` - Iterative fix loop

## Integration

This skill should be invoked:
- After implementing any visual feature
- When user reports "I don't see X"
- Before claiming "feature complete"
- When debugging rendering issues

## Success Criteria

Only exits when ALL are true:
- ✅ Technical QA passes
- ✅ Visual verification passes
- ✅ User confirms spec met
