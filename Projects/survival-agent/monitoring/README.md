# Trading Bot Monitoring Dashboard

Version-independent monitoring dashboard that remains stable across bot upgrades.

## Files

### `dashboard.sh` (Main Dashboard)
The primary monitoring interface. Shows:
- Bot status (running/stopped)
- Capital allocation (starting, free, deployed, total)
- Performance (P&L, fees, gross/net)
- Open positions with real-time P&L
- Scanner status
- Recent activity stats

**Usage:**
```bash
bash monitoring/dashboard.sh
```

**Auto-refresh:** Every 3 seconds (configurable in `dashboard-config.sh`)

---

### `dashboard-config.sh` (Configuration)
**STABLE CONFIG FILE - Edit this, not dashboard.sh!**

This file contains all configuration that might change between bot versions:

```bash
# Data sources
LOG_FILE="/tmp/paper-trade.log"
STATS_FILE="/tmp/paper-trades-master.json"

# Trading parameters
STARTING_BALANCE=0.5

# Display settings
REFRESH_INTERVAL=3  # seconds
MAX_POSITIONS=7
```

**Why separate config?**
- Dashboard logic stays stable across upgrades
- Only update config when bot settings change
- No need to recreate dashboard after bot updates

---

### `watch-stats.sh` (Simpler Monitor)
Lightweight alternative to dashboard.sh:
- Simpler layout
- Faster refresh
- Good for quick checks

**Usage:**
```bash
bash monitoring/watch-stats.sh
```

---

## Upgrading the Bot

When you upgrade the bot version:

### ✅ DO:
1. Edit `dashboard-config.sh` if settings changed:
   ```bash
   # Example: Bot now starts with 1 SOL
   export STARTING_BALANCE=1.0

   # Example: Bot now allows 10 positions
   export MAX_POSITIONS=10
   ```

2. Keep using the same `dashboard.sh` - no changes needed!

### ❌ DON'T:
- Don't edit `dashboard.sh` directly for config changes
- Don't recreate the dashboard from scratch
- Don't hardcode values into the dashboard

---

## Configuration Options

### `STARTING_BALANCE`
Initial capital for P&L calculations.

**Change when:**
- Bot starts with different balance
- You do a reset or fresh start

**Current:** 0.5 SOL

---

### `MAX_POSITIONS`
Maximum concurrent positions the bot can hold.

**Change when:**
- Bot settings change `MAX_CONCURRENT_POSITIONS`

**Current:** 7 positions

---

### `REFRESH_INTERVAL`
Dashboard auto-refresh frequency (seconds).

**Recommended:**
- 3s: Normal monitoring
- 1s: Active trading (more CPU)
- 5s: Casual monitoring

**Current:** 3 seconds

---

### `LOG_FILE` and `STATS_FILE`
Data source locations.

**Change when:**
- Bot writes to different log locations
- Using different stats file

**Current:**
- Log: `/tmp/paper-trade.log`
- Stats: `/tmp/paper-trades-master.json`

---

## Dashboard Features

### Capital Allocation
Shows real-time breakdown:
- **Starting Capital:** Initial balance
- **Free Balance:** Available for new positions
- **Deployed Capital:** Sum of open position amounts (accurate!)
- **Total Capital:** Starting + Total P&L (accurate gain %)

**Fixed in latest version:**
- Now calculates deployed capital from actual position amounts
- Previously calculated as (starting - free) which was wrong after profits
- Now shows correct total capital and gain percentage

---

### Position Table
Live P&L for all open positions:

| Column | Description |
|--------|-------------|
| TOKEN | Token symbol |
| P&L % | Current profit/loss percentage |
| AGE | Minutes since entry |
| CONF | Smart money confidence score (0-100) |
| TP1 | Trailing stop status (active after +100%) |
| STATUS | Visual indicator (🚀/📈/➚/━/➘/📉/💀) |

**Color coding:**
- Green: Profitable positions
- Red: Losing positions

**Status indicators:**
- 🚀 MOON: +50% or higher
- 📈 UP: +20% to +50%
- ➚ GAIN: 0% to +20%
- ━ FLAT: 0%
- ➘ DOWN: 0% to -10%
- 📉 LOSS: -10% to -20%
- 💀 RUG: -20% or worse

---

### Scanner Status
Shows latest scan results:
- Number of opportunities found
- Top scanner scores
- Last token analyzed
- Confidence scores

---

### Recent Activity
Counts from last 100 log events:
- ✅ Trades executed
- ❌ Tokens skipped (low confidence)
- ⏭️ All rejected (no valid opportunities)
- 🔍 Scans completed
- Skip rate percentage

---

## Troubleshooting

### Dashboard shows "No P&L data yet"
**Cause:** Bot hasn't logged P&L update yet.

**Fix:** Wait for next monitor cycle (~5 seconds).

---

### Dashboard shows wrong starting balance
**Cause:** `STARTING_BALANCE` in config doesn't match bot.

**Fix:** Edit `dashboard-config.sh`:
```bash
export STARTING_BALANCE=1.0  # Match bot's actual starting balance
```

---

### Position not showing in table
**Cause:** Mixed-case token names (fixed in latest version).

**Fix:** Already fixed - dashboard now handles CamelCase tokens like GhostLink.

---

### Deployed capital seems wrong
**Cause:** Old dashboard used (starting - free) calculation.

**Fix:** Already fixed - now reads actual position amounts from JSON.

---

## Version History

### v2.0 (Current)
- Separated config from dashboard logic
- Fixed deployed capital calculation (uses actual position amounts)
- Fixed total capital calculation (starting + totalPnl)
- Fixed gain percentage (accurate from JSON data)
- Added support for mixed-case token names
- Version-independent design

### v1.0
- Initial dashboard with hardcoded values
- Incorrect deployed capital calculation
- Required recreation after bot upgrades

---

**Last Updated:** Feb 16, 2026
**Compatible with:** Bot v2.3+
