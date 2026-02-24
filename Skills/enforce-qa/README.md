# Enforce QA - Complete Verification System

Created: 2026-02-15 17:38 UTC

## Purpose

Stop the "assume it's correct" pattern that causes bugs across ALL types of work.

## The Problem

I consistently skip verification and assume my work is correct:
- Write code → claim "done" → it's broken
- Edit files → claim "fixed" → new bugs introduced  
- Deploy services → claim "running" → crashes immediately
- Build UI → claim "working" → doesn't render

## The Solution

**Mandatory verification scripts for every type of work.**

---

## Available Scripts

### 1. `code-verify.sh` - Code Syntax & Quality

**Use when:** Writing or editing ANY code file

```bash
/home/workspace/Skills/enforce-qa/code-verify.sh <file_or_directory>
```

**Checks:**
- ✅ Syntax errors (TypeScript, JavaScript, Python)
- ✅ Compilation (TypeScript builds without errors)
- ✅ Unfinished work (TODO, FIXME, XXX, HACK)
- ✅ Hardcoded secrets (password=, api_key=, etc.)
- ℹ️ Console statements (logging - informational only)

**Example:**
```bash
/home/workspace/Skills/enforce-qa/code-verify.sh \
  Projects/survival-agent/testing/paper-trade-bot-refactored.ts
```

---

### 2. `checkpoint.sh` - Refactor Verification

**Use when:** Refactoring or rewriting existing code

```bash
/home/workspace/Skills/enforce-qa/checkpoint.sh <original> <new>
```

**Checks:**
- ✅ Numeric constants preserved
- ✅ Critical thresholds (stopLoss, takeProfit, etc.)
- ✅ Method signatures not removed
- ✅ Features complete (DexScreener, Circuit Breaker, etc.)
- ⚠️ Methods removed (may be OK if refactored into modules)

**Example:**
```bash
/home/workspace/Skills/enforce-qa/checkpoint.sh \
  testing/paper-trade-bot.ts \
  testing/paper-trade-bot-refactored.ts
```

---

### 3. `service-verify.sh` - Service Health Check

**Use when:** Starting/restarting services, bots, servers

```bash
/home/workspace/Skills/enforce-qa/service-verify.sh <identifier>
```

**Identifier can be:**
- Process name (e.g., `paper-trade-bot-refactored`)
- PID (e.g., `57738`)
- Log file path (e.g., `/dev/shm/paper-trade-bot.log`)

**Checks:**
- ✅ Process is running
- ✅ Uptime (warns if < 2 minutes old)
- ✅ No errors in recent logs
- ℹ️ Provides monitor commands

**Example:**
```bash
/home/workspace/Skills/enforce-qa/service-verify.sh paper-trade-bot-refactored
```

---

### 4. `visual-verify.sh` - Visual/UI Proof (TODO)

**Use when:** Building web pages, UIs, game features

```bash
/home/workspace/Skills/enforce-qa/visual-verify.sh <url_or_path>
```

**Will check:**
- Screenshot proof captured
- Page renders without errors
- Console errors logged
- Requested features visible

**Status:** Not yet implemented (placeholder)

---

## Usage Rules

### MANDATORY Use Cases

Run verification **BEFORE** claiming:
- ✅ "Done"
- ✅ "Complete"
- ✅ "Ready"
- ✅ "Working"
- ✅ "Fixed"
- ✅ "Deployed"

Run verification **AFTER**:
- ✅ Writing any code
- ✅ Editing existing code
- ✅ Refactoring anything
- ✅ Adding features
- ✅ Fixing bugs
- ✅ Starting/restarting services

### Workflow

1. **Do the work**
2. **Run appropriate verification script**
3. **Fix any issues found**
4. **Re-run verification**
5. **Show output to user**
6. **Only then claim "done"**

### What SUCCESS Looks Like

```
User: "Add error handling to the API"
Me: *writes code*
Me: *runs code-verify.sh*
   ✅ CODE VERIFICATION PASSED
Me: *shows output to user*
Me: "Error handling added. Verification passed: no syntax errors, 
     no hardcoded secrets, builds successfully."
```

### What FAILURE Looks Like

```
User: "Add error handling to the API"
Me: *writes code*
Me: "Done! I added error handling."
Reality: Has syntax error, doesn't compile, wasn't tested
```

---

## Test Results (2026-02-15)

### Code Verification
```bash
$ /home/workspace/Skills/enforce-qa/code-verify.sh \
  Projects/survival-agent/testing/paper-trade-bot-refactored.ts

✅ PASS: Syntax check (TypeScript)
✅ PASS: No unfinished work markers
ℹ️  INFO: 99 console.log statements (intentional logging)
✅ PASS: No hardcoded secrets
✅ CODE VERIFICATION PASSED
```

### Service Verification
```bash
$ /home/workspace/Skills/enforce-qa/service-verify.sh \
  paper-trade-bot-refactored

✅ Process running (PID: 57738, Uptime: 03:23)
✅ No errors in recent logs
✅ SERVICE VERIFICATION PASSED
```

---

## Why This Works

**Forces me to:**
1. Actually test my work
2. Catch bugs before shipping
3. Provide proof, not promises
4. Fix issues immediately
5. Build trust through verification

**Prevents:**
- Shipping broken code
- Claiming done prematurely
- Making same mistakes repeatedly
- Wasting user's time
- Losing credibility

---

## Integration with Existing Skills

This skill complements:
- **context-guardian** - Prevents degradation over iterations
- **regression-detector** - Catches when working features break
- **anti-degradation-master** - Full anti-degradation stack

Together, these skills prevent:
1. Bugs from being introduced (enforce-qa)
2. State from degrading over iterations (context-guardian)
3. Working features from breaking (regression-detector)

**The complete safety net for quality work.**
