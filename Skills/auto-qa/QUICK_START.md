# Quick Start Guide

## Run Tests in 30 Seconds

### Step 1: Start Server (if not running)

```bash
cd /home/workspace/Skills/spatial-worlds
bun run dev
```

Wait for: `🌐 http://localhost:3000`

### Step 2: Run Tests

```bash
cd /home/workspace/Skills/auto-qa
./quick-test.sh
```

### Step 3: Check Results

Look for:
```
✅ All tests passed! Ready for deployment.
```

Or:
```
⚠️ Some tests failed. Review the report.
```

### Step 4: View Report

Open the HTML report in your browser:
```bash
open test-results/reports/test-report-*.html
```

---

## What the Tests Do

The automated test suite:

1. Launches 2 browser instances (Player 1 & Player 2)
2. Connects both to your game at localhost:3000
3. Verifies they can see each other
4. Simulates Player 1 moving right
5. Checks if Player 2 sees Player 1's movement
6. Tests simultaneous movement (both players move)
7. Monitors for position drift
8. Checks for JavaScript errors
9. Takes screenshots at each step
10. Generates a detailed report

**Duration:** ~30-45 seconds

---

## When to Run Tests

### Required: Before Every Deployment
```bash
# Make changes to spatial-worlds
cd Skills/spatial-worlds
# Edit files...

# Rebuild (if you modified TypeScript)
bun build scripts/client/main-iso.ts --outdir=dist --target=browser

# TEST BEFORE DEPLOYING
cd ../auto-qa
./quick-test.sh

# ✅ All pass? → Deploy!
# ❌ Some fail? → Fix issues, repeat
```

### Optional: During Development
Run tests frequently while developing to catch issues early:

```bash
# After making changes
cd Skills/auto-qa
bun run scripts/test-simple.js  # Quick 5-second test

# Or full test
./quick-test.sh
```

---

## Understanding Results

### 100% Pass Rate ✅
```
Total Tests: 10
Passed: 10 ✅
Failed: 0 ❌
Success Rate: 100.0%
```
**Action:** Safe to deploy!

### 80-99% Pass Rate ⚠️
```
Total Tests: 10
Passed: 8 ✅
Failed: 2 ❌
Success Rate: 80.0%
```
**Action:** Check HTML report, likely minor issues

### <80% Pass Rate ❌
```
Total Tests: 10
Passed: 5 ✅
Failed: 5 ❌
Success Rate: 50.0%
```
**Action:** DO NOT DEPLOY. Fix critical issues.

---

## Common Test Failures

### "Multiplayer Connection" Failed
**Cause:** WebSocket not connecting

**Fix:**
1. Check server is running
2. Check port 3000 is available
3. Review server logs

### "Position Sync" Failed
**Cause:** Server/client movement mismatch

**Fix:**
1. Check `server.ts` movement logic
2. Verify direction mapping matches client
3. Check velocity calculations

### "Game Initialization" Failed
**Cause:** Game not loading properly

**Fix:**
1. Check `dist/main-iso.js` exists
2. Rebuild: `bun build scripts/client/main-iso.ts --outdir=dist --target=browser`
3. Check browser console in screenshots

---

## Test Scripts

### Full Test Suite
```bash
./quick-test.sh
# or
bun run test:report
```
**What it does:** All 10 tests, HTML report
**Duration:** 30-45 seconds
**Use when:** Before deployment

### Simple Connection Test
```bash
bun run scripts/test-simple.js
```
**What it does:** Quick connectivity check
**Duration:** 5-10 seconds
**Use when:** Quick sanity check during development

---

## Output Files

### Screenshots
Location: `test-results/screenshots/`

Files:
- `player1_initial_*.png` - Player 1 at start
- `player1_connected_*.png` - After connection
- `player1_after_movement_*.png` - After moving
- `player2_*.png` - Same for Player 2

**Use for:** Visual debugging, verifying game state

### JSON Reports
Location: `test-results/reports/test-report-*.json`

Contains:
- Raw test data
- Position history
- Console errors with timestamps
- All test results

**Use for:** Programmatic analysis, CI/CD integration

### HTML Reports
Location: `test-results/reports/test-report-*.html`

Contains:
- Visual test results
- Embedded screenshots
- Interactive details
- Pass/fail summary

**Use for:** Human-readable review, sharing with team

---

## Troubleshooting

### Tests Won't Start

**Error:** `Server is not running`

**Solution:**
```bash
cd /home/workspace/Skills/spatial-worlds
bun run dev
```

---

### Tests Timeout

**Error:** `Game initialization timeout`

**Solution:**
1. Check if game loads manually: `open http://localhost:3000`
2. Rebuild game: `cd Skills/spatial-worlds && bun build scripts/client/main-iso.ts --outdir=dist --target=browser`
3. Check server logs for errors

---

### Browser Errors

**Error:** `Failed to launch browser`

**Solution:**
```bash
# Install Chromium dependencies
apt-get update && apt-get install -y \
  libnss3 libatk1.0-0 libcups2 libdrm2 \
  libxkbcommon0 libxcomposite1 libxdamage1
```

---

## Integration Examples

### Manual Workflow
```bash
# 1. Make changes
vim Skills/spatial-worlds/scripts/client/scenes/IsoGameScene.ts

# 2. Rebuild
cd Skills/spatial-worlds
bun build scripts/client/main-iso.ts --outdir=dist --target=browser

# 3. Test
cd ../auto-qa
./quick-test.sh

# 4. Review report
open test-results/reports/test-report-*.html

# 5. If pass → deploy, if fail → fix and repeat
```

### Git Hook (Pre-Push)
```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running automated tests..."
cd Skills/auto-qa
./quick-test.sh

if [ $? -eq 0 ]; then
  echo "✅ Tests passed! Pushing..."
  exit 0
else
  echo "❌ Tests failed! Fix issues before pushing."
  exit 1
fi
```

---

## Tips

1. **Run tests before EVERY deployment** - Catches issues early
2. **Review HTML reports even when tests pass** - Visual verification
3. **Check screenshots for visual bugs** - Tests can pass but look wrong
4. **Keep test-results in .gitignore** - Don't commit test artifacts
5. **Run simple test frequently** - Fast feedback during development

---

## Need Help?

- Full documentation: `README.md`
- Setup details: `SETUP_COMPLETE.md`
- This guide: `QUICK_START.md`

---

**Remember: Tests exist to give you confidence. Use them!**
