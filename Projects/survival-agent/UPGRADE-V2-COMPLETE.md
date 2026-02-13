# ✅ Upgrade v2.0 - COMPLETE

**Date**: 2026-02-12  
**Status**: Implemented & Ready to Test

---

## 🎯 Changes Made

### 1. Position Size Increase
- **Before**: 10% of balance
- **After**: 12% of balance
- **Location**: Line 62 in `paper-trade-master.ts`

```typescript
private readonly MAX_POSITION_SIZE = 0.12; // 12% of balance (was 0.10)
```

### 2. Source Filter Added
- **New**: Exclude smart-money-only signals (dexscreener source)
- **Location**: Lines 148-156 in `paper-trade-master.ts`

```typescript
// NEW: Exclude smart-money-only signals (v2.0 upgrade)
const beforeSourceFilter = qualified.length;
qualified = qualified.filter(opp => (opp as any).source !== 'dexscreener');
const excluded = beforeSourceFilter - qualified.length;
if (excluded > 0) {
  console.log(`   ⏭️  Excluded ${excluded} smart-money-only signal(s)`);
}
console.log(`   ${qualified.length} qualified after filters\n`);
```

### 3. Logic Flow
- ✅ Scan opportunities
- ✅ Filter by score (≥60)
- ✅ **NEW**: Filter out dexscreener-only
- ✅ Check smart money confidence (≥35)
- ✅ Execute trade (12% position size)
- ✅ Monitor exits
- ✅ Report health

---

## 📊 Expected Impact

### Current (v1.0)
- 234 trades @ 10% position
- 35.5% win rate
- +0.021 SOL mainnet

### After Upgrade (v2.0)
- 83 trades @ 12% position
- 38.6% win rate
- +0.073 SOL mainnet

**Expected Improvement**: **3.5x better** (+0.052 SOL)

---

## 💾 Backup

Current settings safely backed up to:
- `config-backup-v1.0-current.json`

Contains:
- All v1.0 settings
- Performance metrics
- Source breakdown
- Revert instructions

---

## 🚀 How to Test

### 1. Run Paper Trading (Safe)
```bash
cd /home/workspace/Projects/survival-agent
bun run testing/paper-trade-master.ts
```

Watch for:
- "⏭️  Excluded N smart-money-only signal(s)" messages
- Fewer total trades (expected)
- Higher position sizes (0.06 SOL instead of 0.05 SOL)

### 2. Monitor Key Metrics

After 24 hours, check:
- **Win Rate**: Should be 38-40% (up from 35%)
- **Trade Frequency**: ~1-2 trades/hour (down from 3-4/hour)
- **P&L**: Should trend positive
- **Source Mix**: 0 dexscreener-only trades

### 3. Live Deployment (When Ready)

If paper trading looks good after 48 hours:
```bash
# Stop current bot
pkill -f master-coordinator

# Update live bot with same changes
# (apply same edits to core/master-coordinator.ts)

# Restart
./start-master.sh
```

---

## ⏮️ How to Revert

If performance worsens:

1. **Stop the bot**
```bash
pkill -f paper-trade-master
```

2. **Check the backup**
```bash
cat config-backup-v1.0-current.json
```

3. **Revert changes**
- Change `MAX_POSITION_SIZE` back to `0.10`
- Remove the source filter (lines 148-156)

---

## 📈 What Changed & Why

### Why Exclude Dexscreener-Only?
Your backtest showed:
- **Dexscreener-only**: 161 trades, 33.3% WR ❌
- **Both signals**: 70 trades, 37.1% WR ✅
- **Shocked-only**: 3 trades (too few to judge)

The breakthrough insight:
> "When shocked AND smart money agree (even at low confidence 45-50), it's a strong signal (57.1% WR)"

Pure smart money without shocked confirmation = weak signal.

### Why 12% Position Size?
With 65% fewer trades:
- Lower cumulative fees
- Better capital efficiency
- Larger positions on higher-quality signals

The math:
- **234 trades @ 10%** = lots of fees eating profits
- **83 trades @ 12%** = fewer fees, better returns per trade

---

## 🔍 Monitor These Logs

### Good Signs
```
✅ "Excluded N smart-money-only signal(s)" appears regularly
✅ Win rate trending 38-40%
✅ P&L positive over 24 hours
✅ Fewer trades, but better quality
```

### Warning Signs
```
⚠️  Win rate drops below 35%
⚠️  No trades for 6+ hours
⚠️  Missing obvious opportunities (check old logs)
⚠️  P&L significantly negative
```

---

## 📝 Technical Details

### Files Modified
1. `/home/workspace/Projects/survival-agent/testing/paper-trade-master.ts`
   - Line 62: Position size 0.10 → 0.12
   - Lines 148-156: Added source filter

### Files Created
1. `/home/workspace/Projects/survival-agent/config-backup-v1.0-current.json`
2. `/home/workspace/Projects/survival-agent/UPGRADE-V2-ANALYSIS.md`
3. `/home/workspace/Projects/survival-agent/UPGRADE-V2-COMPLETE.md` (this file)

### Unchanged
- Score threshold: 60 ✓
- Smart money threshold: 35 ✓
- Take profit: 100% ✓
- Stop loss: -30% ✓
- Max hold time: 60 min ✓
- Scan interval: 30 sec ✓

---

## 🎯 Success Criteria

Consider v2.0 successful if after **48 hours**:

1. ✅ Win rate ≥ 38%
2. ✅ P&L positive
3. ✅ No major bugs/crashes
4. ✅ Still finding good opportunities (not too restrictive)

Consider reverting if:
1. ❌ Win rate < 35% (worse than v1.0)
2. ❌ P&L significantly negative
3. ❌ < 1 trade per 12 hours (too restrictive)

---

## 🚀 Ready to Run

The upgrade is complete and ready to test. Run the paper trader to see it in action:

```bash
cd /home/workspace/Projects/survival-agent
bun run testing/paper-trade-master.ts
```

Good luck! 🎯
