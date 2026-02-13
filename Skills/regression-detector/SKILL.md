---
name: regression-detector
description: Automated regression detection that catches when "working" features break during iteration. Takes baseline snapshots and compares against them after each change.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# Regression Detector - Catch Breaks Early

## Purpose

**Detects when iteration breaks previously working functionality.**

The killer of iterative development is silent regressions:
- Feature X worked after iteration 2
- You're now on iteration 7
- Feature X silently broke at iteration 5
- You don't find out until user reports it
- Now you have to debug through 5 iterations to find the break

**This skill prevents that.**

## How It Works

1. **Baseline Capture**: After each working iteration, capture state
2. **Comparison**: Before claiming "done", compare current vs baseline
3. **Alert**: If baseline tests fail, flag immediately
4. **Bisect**: Help identify which iteration broke it

## Usage

### Initial Baseline

After your FIRST working build:

```bash
# Navigate to project
cd your-project

# Capture baseline (this will be your ground truth)
node ~/Skills/regression-detector/scripts/capture-baseline.js

# This creates .regression/baseline-{timestamp}.json with:
# - List of all files and their hashes
# - Screenshot of UI (if web app)
# - Output of test commands
# - API response samples
```

### After Each Iteration

```bash
# Make your changes
# ...

# Before committing, check for regressions
node ~/Skills/regression-detector/scripts/check-regression.js

# This compares current state to baseline:
# ✅ All baseline files still exist?
# ✅ UI still looks similar? (visual diff)
# ✅ Tests still pass?
# ✅ API responses still match schema?

# If PASS: Safe to commit
git add -A && git commit -m "feat: [change]"

# Update baseline if intentional breaking change
node ~/Skills/regression-detector/scripts/update-baseline.js

# If FAIL: Regression detected!
# Shows you what broke
# DON'T commit - fix first
```

### When Regression Detected

```bash
# See detailed diff
node ~/Skills/regression-detector/scripts/show-diff.js

# Outputs:
# - Which files changed unexpectedly
# - Visual diff of UI screenshots
# - Which tests started failing
# - API response differences

# Find when it broke (if you have git history)
node ~/Skills/regression-detector/scripts/bisect.js
# Uses git bisect to find exact commit that introduced regression
```

## What Gets Checked

### 1. File Integrity
- All baseline files still exist?
- No unexpected new files? (could indicate error logs, crashes)
- Critical config files unchanged?

### 2. Visual Regression (Web Apps)
- Screenshot comparison with baseline
- Highlights visual differences
- Ignores minor rendering variations
- Flags major layout breaks

### 3. Functional Tests
- Run same test suite as baseline
- Compare pass/fail status
- Flag new failures

### 4. API Contract
- Sample API calls from baseline
- Verify response schema unchanged
- Check status codes match
- Validate data types

### 5. Performance Baselines
- Load time within 20% of baseline?
- Bundle size not grown >10%?
- Memory usage reasonable?

## Configuration

Create `.regression/config.json`:

```json
{
  "checks": {
    "fileIntegrity": true,
    "visualRegression": true,
    "functionalTests": true,
    "apiContract": true,
    "performance": true
  },
  "testCommand": "npm test",
  "devServerCommand": "npm run dev",
  "devServerUrl": "http://localhost:3000",
  "criticalPaths": [
    "/",
    "/dashboard",
    "/api/health"
  ],
  "ignorePatterns": [
    "*.log",
    ".cache/*",
    "node_modules/*"
  ],
  "visualDiffThreshold": 0.05,
  "performanceMargin": 0.2
}
```

## Integration Patterns

### With Context Guardian

```bash
# After context-guardian init
bash ~/Skills/context-guardian/scripts/init-project.sh

# Add regression detection
node ~/Skills/regression-detector/scripts/init.js

# Your workflow:
1. Read .context/state-snapshot.md  (context guardian)
2. Make change (iteration protocol)
3. Check regression (this skill)
4. Update state (context guardian)
```

### With Iteration Protocol

```bash
# Iteration protocol says: verify after EVERY change
# This skill automates that verification

# Add to your iteration workflow:
BEFORE:
  - Read state
  - Commit checkpoint

CHANGE:
  - Make ONE change

AFTER:
  - node ~/Skills/regression-detector/scripts/check-regression.js  ← ADD THIS
  - If pass: commit
  - If fail: revert OR fix
```

### With CI/CD

```yaml
# .github/workflows/test.yml
name: Regression Check
on: [push, pull_request]
jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: node ~/Skills/regression-detector/scripts/check-regression.js
      - if: failure()
        run: node ~/Skills/regression-detector/scripts/show-diff.js
```

## Baseline Management

**When to update baseline:**
- ✅ Intentional breaking change (new feature that changes UI)
- ✅ Dependency upgrade that changes output
- ✅ Performance optimization that changes metrics
- ✅ Bug fix that changes incorrect baseline

**When NOT to update baseline:**
- ❌ Tests are failing and you want them to pass
- ❌ "I changed something and now it's different" (that's a regression!)
- ❌ To make the errors go away

**Multiple baselines:**
```bash
# Keep baseline per major version
node ~/Skills/regression-detector/scripts/capture-baseline.js --tag "v1.0"
node ~/Skills/regression-detector/scripts/capture-baseline.js --tag "v2.0"

# Compare against specific baseline
node ~/Skills/regression-detector/scripts/check-regression.js --baseline "v1.0"
```

## Advanced: Bisect Automation

When you discover a regression but don't know when it was introduced:

```bash
# Automated git bisect to find breaking commit
node ~/Skills/regression-detector/scripts/bisect.js

# This will:
# 1. Use git bisect start
# 2. Mark current commit as bad
# 3. Mark baseline commit as good
# 4. Automatically test each commit
# 5. Find exact commit that broke it
# 6. Show you the diff

# Example output:
# Found regression introduced in: abc1234
# Commit: "feat: add caching layer"
# Files changed: src/cache.js, src/api.js
# Likely cause: cache.js line 42
```

## Success Metrics

**This skill is working when:**
- ✅ Regressions caught within 1 iteration (not 5 iterations later)
- ✅ User never reports "this used to work"
- ✅ Can confidently say "nothing broke" after each change
- ✅ Baseline stays stable across weeks
- ✅ Visual diffs show intentional changes only

**Warning signs:**
- 🚨 Frequently updating baseline to "fix" failures
- 🚨 Skipping regression checks because "too slow"
- 🚨 Large visual diffs that are unexplained
- 🚨 Tests passing locally but baseline failing

## Examples

**Scenario 1: Silent UI Break**

```bash
# Iteration 3: Add new feature
git commit -m "feat: add search"
node ~/Skills/regression-detector/scripts/check-regression.js

# Output:
# ❌ REGRESSION DETECTED
# Visual diff: Header disappeared
# Screenshot diff: .regression/diff-header.png
# Likely cause: CSS change affected global layout

# FIX: Scope your CSS changes
# VERIFY: Regression check passes
# COMMIT: Now safe
```

**Scenario 2: API Breaking Change**

```bash
# Iteration 5: Refactor API
git commit -m "refactor: clean up API"
node ~/Skills/regression-detector/scripts/check-regression.js

# Output:
# ❌ REGRESSION DETECTED
# API: GET /api/users
# Expected: {users: [...]}
# Got: {data: [...]}
# Schema changed - breaking for clients

# DECISION: Either:
# A) Fix to match baseline schema
# B) Intentional breaking change - update baseline AND bump version
```

**Scenario 3: Performance Regression**

```bash
# Iteration 7: Add analytics
node ~/Skills/regression-detector/scripts/check-regression.js

# Output:
# ⚠️  PERFORMANCE REGRESSION
# Load time: 450ms (baseline: 180ms)
# +250% slower
# Bundle size: 2.3MB (baseline: 0.8MB)
# +187% larger

# INVESTIGATE: What did analytics add?
# OPTIMIZE: Lazy load analytics
# VERIFY: Back to baseline performance
```

## See Also

- `context-guardian`: State management
- `iteration-protocol`: One-change-at-a-time discipline
- `self-qa`: Automated visual testing
- `build-preview`: Screenshot capture
- `enforce-qa`: Pre-deployment gate
