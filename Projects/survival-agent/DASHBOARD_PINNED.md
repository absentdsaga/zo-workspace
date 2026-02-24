# Dashboard Pinned - Version Independent

**Version:** v2.0
**Date:** Feb 16, 2026
**Status:** ✅ Stable across bot upgrades

---

## What Changed

### Before (v1.0)
- Dashboard had hardcoded values
- Config mixed with display logic
- Required recreation after bot upgrades
- Broke when bot version changed

### After (v2.0)
- **Config separated** into `dashboard-config.sh`
- Display logic stable in `dashboard.sh`
- **No recreation needed** after bot upgrades
- Only edit config when settings change

---

## File Structure

```
monitoring/
├── dashboard.sh          ← Main dashboard (don't edit)
├── dashboard-config.sh   ← Edit this for config changes
├── watch-stats.sh        ← Lightweight alternative
└── README.md             ← Full documentation
```

---

## How to Upgrade Bot Without Breaking Dashboard

### When Bot Settings Change

**Example: Bot now uses 1 SOL starting balance**

**OLD WAY (broken):**
```bash
# Had to edit dashboard.sh directly:
STARTING_BAL=1.0  # Changed from 0.5
# ... recreate entire dashboard
```

**NEW WAY (stable):**
```bash
# Just edit dashboard-config.sh:
nano monitoring/dashboard-config.sh

# Change line:
export STARTING_BALANCE=1.0

# Dashboard automatically uses new value!
```

---

## Configuration File

**File:** `monitoring/dashboard-config.sh`

**What's in it:**
```bash
# Data sources
export LOG_FILE="/tmp/paper-trade.log"
export STATS_FILE="/tmp/paper-trades-master.json"

# Trading parameters (update when bot settings change)
export STARTING_BALANCE=0.5

# Display settings
export REFRESH_INTERVAL=3  # seconds
export MAX_POSITIONS=7

# Colors (don't change unless you want different colors)
export RED='\033[0;31m'
export GREEN='\033[0;32m'
# ... etc
```

---

## Common Changes

### Change Starting Balance
```bash
# When bot starts with different balance
export STARTING_BALANCE=1.0  # Changed from 0.5
```

### Change Max Positions
```bash
# When bot allows more concurrent trades
export MAX_POSITIONS=10  # Changed from 7
```

### Change Refresh Rate
```bash
# For faster/slower updates
export REFRESH_INTERVAL=1  # 1s = fast, 5s = slow
```

### Change Data Locations
```bash
# If bot writes to different files
export LOG_FILE="/tmp/new-log.log"
export STATS_FILE="/tmp/new-stats.json"
```

---

## What Dashboard Shows

### Capital Allocation (Fixed!)
- **Starting Capital:** From config
- **Free Balance:** From status.sh
- **Deployed Capital:** Sum of actual position amounts (accurate!)
- **Total Capital:** Starting + Total P&L (accurate gain %!)

**Previous bug:** Deployed was calculated as (starting - free) which was wrong after profits.

**Fixed:** Now reads actual position amounts from JSON file.

---

### Position Table
Real-time P&L for all open positions:
- Token symbol (supports mixed-case like GhostLink!)
- P&L percentage with color coding
- Age in minutes
- Confidence score
- TP1 trailing stop status
- Visual status indicator

---

### Performance Metrics
- Net P&L (realized + unrealized)
- Gross P&L (before fees)
- Total fees paid
- Gain percentage (accurate from JSON)

---

## Version History

### Bot Upgrades That Won't Break Dashboard

| Bot Version | Config Change Needed | What to Update |
|-------------|---------------------|----------------|
| v2.3 → v2.4 | None | Dashboard works as-is |
| v2.4 → v3.0 | Maybe | Only if starting balance or max positions change |
| Fresh restart | Yes | Update STARTING_BALANCE in config |
| Reset stats | Yes | Update STARTING_BALANCE in config |

---

## Benefits

### ✅ Stability
- Dashboard survives bot upgrades
- No recreation needed
- Config changes are simple edits

### ✅ Accuracy
- Deployed capital uses actual position amounts
- Total capital calculated correctly
- Gain percentage accurate from JSON

### ✅ Flexibility
- Easy to adjust refresh rate
- Simple to change starting balance
- Can point to different data sources

### ✅ Maintainability
- Config separated from logic
- Clear what to edit vs what to leave alone
- Documented in README

---

## Quick Reference

### View Dashboard
```bash
cd /home/workspace/Projects/survival-agent
bash monitoring/dashboard.sh
```

### Edit Config
```bash
nano monitoring/dashboard-config.sh
# OR
vi monitoring/dashboard-config.sh
```

### Check Current Settings
```bash
cat monitoring/dashboard-config.sh
```

### Read Full Docs
```bash
cat monitoring/README.md
```

---

## Upgrade Checklist

When upgrading bot to new version:

- [ ] Check if starting balance changed
- [ ] Check if max positions changed
- [ ] Check if log file location changed
- [ ] Edit `dashboard-config.sh` with any changes
- [ ] Test dashboard still works
- [ ] ✅ Done! No dashboard recreation needed!

---

**Created:** Feb 16, 2026
**Status:** ✅ Production ready
**Tested with:** Bot v2.3

**Next bot upgrade:** Just edit `dashboard-config.sh` - dashboard stays stable!
