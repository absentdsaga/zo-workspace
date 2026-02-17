---
name: enforce-qa
description: Mandatory QA enforcement for ALL code work. Prevents claiming "done" without verification. Auto-activates after any code writing, editing, or feature implementation.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: "2.0.0"
  created: "2026-02-15"
  updated: "2026-02-15"
---

# Enforce QA

**Purpose:** Stop the "assume it's correct" pattern that leads to bugs in ALL work, not just refactors.

## When This Activates (MANDATORY)

This skill **MUST** be used after:

### Code Work
1. Writing any new code file
2. Editing existing code
3. Refactoring anything
4. Adding new features
5. Fixing bugs
6. Updating configuration

### Visual/UI Work
7. Creating web pages
8. Building game features
9. Implementing UI components
10. Deploying sites or services

### Before Claiming Done
11. Before saying "done", "complete", "ready", "working"
12. Before restarting any service/bot/server
13. Before asking user to test/review

**RULE:** If you touched code or created something visual, you MUST verify before claiming done.

## The Problem

I make the same mistake across ALL types of work:
- Write code → assume it works → claim "done" → it's broken
- Edit file → assume it's correct → ship it → bugs appear
- Create UI → assume it looks right → don't check → it's wrong
- Add feature → assume it's complete → it's missing parts
- Fix bug → assume it's fixed → introduce new bugs

**Pattern:**
1. Do the work
2. Assume it's correct
3. Skip verification
4. Claim "done"
5. User finds bugs

## The Solution

**MANDATORY VERIFICATION based on work type:**

### For Code Changes (new, edit, refactor)
```bash
/home/workspace/Skills/enforce-qa/code-verify.sh <file_or_directory>
```

**Checks:**
- Syntax errors (compile/parse)
- Missing imports/dependencies
- Undefined variables/functions
- Type errors (if TypeScript)
- Logic errors (basic static analysis)
- TODO/FIXME comments (unfinished work)

### For Refactors/Rewrites
```bash
/home/workspace/Skills/enforce-qa/checkpoint.sh <original> <new>
```

**Checks:**
- Numeric constants match
- Critical thresholds preserved
- Methods not removed
- Features complete
- Logic equivalent

### For Visual/UI Work
```bash
/home/workspace/Skills/enforce-qa/visual-verify.sh <url_or_path>
```

**Checks:**
- Capture screenshot proof
- Verify it renders
- Check for console errors
- Verify requested features visible
- Compare before/after if updating

### For Service Restarts
```bash
/home/workspace/Skills/enforce-qa/service-verify.sh <service_name>
```

**Checks:**
- Process actually running
- No startup errors in logs
- Health check passes
- Expected behavior working
- Performance acceptable

## Enforcement Rules

### NEVER:
- Claim "done" without running appropriate verify script
- Say "looks good", "should work", "probably fine" without proof
- Skip verification because "it's a small change"
- Trust memory over actual verification
- Assume the user can test it themselves

### ALWAYS:
1. **Complete the work**
2. **Run appropriate verification script**
3. **Show verification output to user**
4. **Fix ALL issues found**
5. **Re-run verification after fixes**
6. **Only claim "done" when verification PASSES**

## Verification Matrix

| Work Type | Script | What It Checks |
|-----------|--------|----------------|
| New code file | `code-verify.sh` | Syntax, imports, types, TODOs |
| Edit existing code | `code-verify.sh` | Same + no regressions |
| Refactor | `checkpoint.sh` | Feature parity, no removals |
| New feature | `code-verify.sh` + manual test | Works as requested |
| Bug fix | `code-verify.sh` + reproduce bug | Bug actually fixed |
| Web page | `visual-verify.sh` | Renders, no errors, looks right |
| Game feature | `visual-verify.sh` + manual test | Interactive proof |
| Deploy site | `service-verify.sh` | Running, accessible, working |
| Restart bot | `service-verify.sh` | Process up, no errors, trading |

## Success Criteria

**A task is NOT DONE until:**

1. ✅ Appropriate verification script run
2. ✅ Verification PASSED (no errors/warnings)
3. ✅ Output shown to user as proof
4. ✅ For visual work: screenshot captured
5. ✅ For services: health check passes
6. ✅ User confirms or explicitly approves proceeding

**No shortcuts. No assumptions. Only proof.**

## Examples

### Bad (OLD WAY):
```
User: "Add a login button"
Me: *writes code* "Done! I added the login button."
Reality: Button doesn't work, wrong color, missing icon
```

### Good (NEW WAY):
```
User: "Add a login button"
Me: *writes code*
Me: *runs code-verify.sh* → finds missing onClick handler
Me: *fixes handler*
Me: *runs visual-verify.sh* → captures screenshot
Me: *shows screenshot to user* "Login button added, here's proof"
Reality: Button works, looks right, user can see it
```

## Why This Works

**It forces me to:**
1. Actually test my work
2. Catch bugs before shipping
3. Provide proof, not promises
4. Fix issues immediately
5. Build user trust through demonstration

**It prevents:**
- Shipping broken code
- Claiming done prematurely
- Making same mistakes repeatedly
- Wasting user's time on broken work
- Losing credibility through carelessness
