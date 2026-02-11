# Auto-QA Testing System

**Comprehensive automated testing for the spatial-worlds multiplayer game.**

This testing system helps you verify that multiplayer synchronization, movement, and game mechanics work correctly BEFORE showing changes to users.

---

## Features

- **Multi-Browser Testing** - Simulates 2+ players in separate browser instances
- **Real-time Sync Verification** - Validates position synchronization between players
- **Movement Testing** - Simulates keyboard input and verifies movement
- **Elevation Testing** - Tests multi-level platform support
- **Console Monitoring** - Captures and reports all browser console errors
- **Screenshot Capture** - Takes screenshots at key test points for visual verification
- **Comprehensive Reports** - Generates both JSON and HTML test reports
- **Pass/Fail Metrics** - Clear test results with success rates

---

## Installation

Dependencies are already installed if you're reading this. But if needed:

```bash
cd Skills/auto-qa
bun install
```

---

## Usage

### Prerequisites

**The spatial-worlds server MUST be running before tests can execute.**

```bash
# In a separate terminal
cd Skills/spatial-worlds
bun run dev
```

The game should be accessible at `http://localhost:3000`

### Running Tests

**Quick test:**

```bash
cd Skills/auto-qa
bun run test
```

**Full test with HTML report:**

```bash
cd Skills/auto-qa
bun run test:report
```

### Test Output

Test results are saved to:

```
Skills/auto-qa/test-results/
├── screenshots/           # PNG screenshots from both players
├── reports/
│   ├── test-report-*.json # Raw test data
│   └── test-report-*.html # Beautiful HTML reports
```

---

## What Gets Tested

### 1. Browser Launch
Verifies both browser instances can start successfully.

### 2. Game Load
Confirms the game loads in both browsers without errors.

### 3. Game Initialization
Checks that Phaser game engine and multiplayer manager initialize correctly.

### 4. Multiplayer Connection
Validates WebSocket connection between clients and server.

### 5. Mutual Visibility
Confirms both players can see each other in the game world.

### 6. Position Synchronization
Tests that when one player moves, the other player sees the movement.

**Test process:**
- Records initial positions
- Player 1 moves right for 2 seconds
- Verifies Player 1 position changed
- Verifies Player 2 sees Player 1's new position
- Validates positions are synced within acceptable tolerance (<100px)

### 7. Bidirectional Movement
Simulates both players moving simultaneously and verifies sync.

### 8. Elevation Tracking
Checks if elevation/multi-level platforms are properly tracked.

### 9. Sync Stability
Monitors position sync over 5 seconds to detect drift.

**Pass criteria:** Maximum drift <150 pixels

### 10. Console Errors
Reports any JavaScript errors or warnings during test execution.

---

## Test Reports

### JSON Report
Raw test data with all details:
- Test results with timestamps
- Position history
- Console errors with stack traces
- Screenshot metadata

### HTML Report
Beautiful, interactive report with:
- Pass/fail summary with percentages
- Visual test results list
- Embedded screenshots
- Console error details
- Expandable test details

**Open in browser:**
```bash
open test-results/reports/test-report-*.html
```

---

## Understanding Results

### Success (All Green)
```
✅ All tests passed!
Success Rate: 100%
```
Your changes are working perfectly. Safe to deploy.

### Partial Success (Some Red)
```
⚠️  Some tests failed
Success Rate: 80%
```
Review the HTML report to see which specific tests failed and why.

### Failure (Many Red)
```
❌ Multiple test failures
Success Rate: <60%
```
Critical issues detected. Do NOT deploy. Fix issues and re-test.

---

## Common Issues

### "Server is not running"
Start the spatial-worlds server:
```bash
cd Skills/spatial-worlds
bun run dev
```

### "WebSocket connection failed"
- Check that server is running on port 3000
- Verify no firewall is blocking WebSocket connections
- Check server logs for errors

### "Position sync failed"
- Server-side position calculation may be incorrect
- Check for differences between client and server movement logic
- Review velocity/direction mapping

### "Browser launch failed"
Puppeteer may need additional dependencies:
```bash
# Install Chromium dependencies (if needed)
apt-get update && apt-get install -y \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
  libcairo2 libasound2
```

---

## Customization

### Adjust Test Duration

Edit `scripts/test-multiplayer-sync.js`:

```javascript
const TEST_DURATION = 30000; // 30 seconds (adjust as needed)
const SCREENSHOT_INTERVAL = 2000; // Screenshot every 2s
const POSITION_CHECK_INTERVAL = 1000; // Check positions every 1s
```

### Add Custom Tests

Add new test cases in the `runTests()` function:

```javascript
// TEST 11: Custom test
console.log('🎯 Testing custom feature...\n');

// Your test logic here
const result = await yourTestFunction();

addTestResult('Custom Test', result.passed, result.message, result.details);
```

### Change Viewport Size

Adjust browser viewport:

```javascript
const VIEWPORT = { width: 1280, height: 720 }; // Adjust resolution
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Automated QA

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: |
          cd Skills/spatial-worlds && bun install
          cd ../auto-qa && bun install

      - name: Start game server
        run: cd Skills/spatial-worlds && bun run dev &

      - name: Wait for server
        run: sleep 5

      - name: Run tests
        run: cd Skills/auto-qa && bun run test:report

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: Skills/auto-qa/test-results/
```

---

## Pre-Deployment Checklist

Before deploying changes to spatial-worlds:

1. ✅ Start the game server
2. ✅ Run `bun run test:report`
3. ✅ Verify 100% pass rate
4. ✅ Check HTML report for any warnings
5. ✅ Review screenshots for visual issues
6. ✅ Confirm no console errors
7. ✅ Test manually if any tests failed

---

## Troubleshooting

### Tests hang or timeout

**Cause:** Game not initializing properly

**Solution:**
- Check browser console in screenshots
- Look for JavaScript errors in test report
- Verify all game assets are loading

### Position sync consistently fails

**Cause:** Server/client movement logic mismatch

**Solution:**
- Compare `server.ts` movement logic with client
- Check direction mapping matches exactly
- Verify velocity calculations are identical

### Screenshots are blank

**Cause:** Page not rendering before screenshot

**Solution:**
- Increase wait times before screenshots
- Check if game canvas is created
- Verify page is fully loaded

---

## Architecture

### Test Flow

```
1. Launch 2 browser instances (Puppeteer)
   ↓
2. Navigate to http://localhost:3000
   ↓
3. Wait for game initialization
   ↓
4. Verify WebSocket connection
   ↓
5. Execute movement commands
   ↓
6. Compare positions between instances
   ↓
7. Capture screenshots
   ↓
8. Monitor console for errors
   ↓
9. Generate JSON + HTML reports
```

### Files

- **`scripts/test-multiplayer-sync.js`** - Main test script with all test cases
- **`scripts/test-utils.js`** - Utilities for screenshot comparison and report generation
- **`scripts/run-tests.js`** - Test runner that orchestrates execution
- **`package.json`** - Dependencies and scripts

---

## Future Enhancements

Potential improvements:

- [ ] Performance testing (FPS, latency)
- [ ] Load testing (10+ concurrent players)
- [ ] Network condition simulation (lag, packet loss)
- [ ] Visual regression testing (compare screenshots over time)
- [ ] Mobile browser testing
- [ ] Voice chat testing (Daily.co integration)
- [ ] Automated deployment on successful tests

---

## Support

For issues or questions:

1. Check test reports in `test-results/reports/`
2. Review console errors in HTML report
3. Examine screenshots for visual clues
4. Check spatial-worlds server logs
5. Review this README

---

## License

MIT - Same as spatial-worlds project

---

**Remember: Always run tests BEFORE showing changes to users!**

The user will appreciate catching bugs in testing rather than in production.
