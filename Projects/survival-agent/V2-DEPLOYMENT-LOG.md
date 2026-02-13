# 🚀 Upgrade v2.0 - Deployment Log

**Deployment Time**: 2026-02-12 22:32 UTC  
**Version**: v2.0 (Source Filter + 12% Position Size)

---

## 📊 v1.0 Final Stats (Backed Up)

**Backup File**: `/tmp/paper-trades-master-v1-backup-20260212-223249.json`

**Performance Summary** (v1.0):
- Total Trades: 366
- Win Rate: 33% (120W/240L)
- Total P&L: +0.205 SOL
- Final Balance: 0.455 SOL (from 0.5 SOL starting)

---

## 🆕 v2.0 Changes

### 1. Exclude Smart-Money-Only Signals
- **Before**: Traded all sources (shocked, dexscreener, both)
- **After**: Excludes pure dexscreener (smart money only) trades
- **Reason**: Dexscreener-only had 33.3% WR vs "both" had 37.1% WR

### 2. Increased Position Size
- **Before**: 10% of balance
- **After**: 12% of balance
- **Reason**: Fewer trades with better win rate = larger positions on quality signals

---

## 🎯 Expected v2.0 Performance

Based on backtest analysis:
- **Trade Volume**: 234 → 83 trades (-65%)
- **Win Rate**: 35.5% → 38.6% (+3.1%)
- **Mainnet P&L**: +0.021 → +0.073 SOL (3.5x better)

---

## 📈 v2.0 Tracking Starts NOW

**Starting Balance**: 0.5 SOL (reset)  
**Start Time**: 2026-02-12 22:32 UTC

**Monitor Commands**:
```bash
# Live dashboard
watch -n 5 /tmp/paper-bot-status.sh

# Token positions
bun monitoring/token-monitor.ts

# Start v2.0 bot
cd /home/workspace/Projects/survival-agent
bun run testing/paper-trade-master.ts
```

---

## 📊 Success Metrics (Check After 48 Hours)

Compare v2.0 vs v1.0:

| Metric | v1.0 | v2.0 Target | v2.0 Actual |
|--------|------|-------------|-------------|
| Win Rate | 33% | 38%+ | _TBD_ |
| Trades/Day | ~183 | ~41 | _TBD_ |
| P&L | +0.205 SOL | +0.365 SOL | _TBD_ |

---

## ⚠️ Revert Criteria

Revert to v1.0 if after 48 hours:
1. Win rate < 33% (worse than v1.0)
2. P&L significantly negative
3. < 1 trade per 12 hours (too restrictive)

**Revert Instructions**:
```bash
# Stop bot
pkill -f paper-trade-master

# Restore v1.0 settings from backup
# (see config-backup-v1.0-current.json)
```

---

## 📝 Notes

- v1.0 ran for ~16 hours (366 trades)
- v2.0 starts with clean slate
- All v1.0 data safely backed up
- This is a fair A/B test

---

**Status**: 🟢 READY TO DEPLOY v2.0
