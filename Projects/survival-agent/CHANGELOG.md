# Paper Trading Bot - Version Changelog

## Version History

### v2.1 (Feb 16, 2026)
**3-Loss Blacklist System**

**New Features:**
- 🚫 Auto-blacklist tokens after 3 consecutive losses
- Blacklist persists across bot restarts
- Console alerts when tokens are blacklisted
- Prevents repeat trading of proven losers (e.g., TRUMP2)

**Technical Changes:**
- Added `checkAndBlacklistLosers()` method
- Integrated blacklist check into both exit paths (stop loss + rugged)
- Blacklist stored in `/tmp/paper-trades-blacklist.json`

**Expected Impact:**
- Prevent ~50% of losses from repeat-loser tokens
- Improve win rate by 2-5% points
- Save ~0.06 SOL per bad token

**Files Modified:**
- `testing/paper-trade-bot.ts` - Added blacklist logic (lines 807-840, 641, 690)

---

### v2.0 (Feb 12, 2026)
**Dual-Loop Architecture & Advanced Features**

**New Features:**
- ⚡ Dual-loop architecture: Scanner (15s) + Monitor (5s)
- 💎 Trailing stop: 20% from peak after hitting +100% TP1
- 📊 Scanner source tracking (pumpfun/dexscreener/both/shocked)
- 🎯 Up to 10 concurrent positions for diversification
- ✅ Jupiter-validated prices and routes (entry + exit)
- 💀 Proper handling of rugged tokens (no sell route = total loss)
- 🔥 Real Jito bundle costs (p75 tier: ~$0.0088/trade)
- 📈 Live P&L tracking in open positions

**Trading Parameters:**
- Position size: 12% of balance
- Stop loss: -30% (before TP1)
- Take profit 1: +100% (activates trailing stop)
- Trailing stop: 20% from peak (after TP1)
- Max hold time: 60 minutes
- Min confidence: 45 (smart money tracker)
- Min shocked score: 30

**Performance vs v1.0:**
- v1.0: 366 trades, 33% WR, +0.205 SOL (+41%)
- v2.0: TBD (testing in progress)

**Files Modified:**
- `testing/paper-trade-bot.ts` - Complete rewrite with dual-loop
- Added state persistence and real-time monitoring

---

### v1.0 (Feb 2026)
**Initial Paper Trading Bot**

**Features:**
- Single-loop scanner (15s intervals)
- Basic stop loss (-30%) and take profit (+100%)
- Smart money tracker integration
- Jupiter swap validation
- Paper trading simulation

**Historical Performance:**
- 366 trades, 33% win rate
- +0.205 SOL profit (+41%)
- Deleted after archive

---

## Versioning System

**Format:** vX.Y
- **X (Major)**: User-controlled version bumps (v2 → v3)
- **Y (Minor)**: Incremental patches/upgrades (v2.1 → v2.2 → v2.3)

**When to bump:**
- **Minor (Y)**: Bug fixes, small features, optimizations
- **Major (X)**: Significant architecture changes, strategy overhauls (user decides)

**Current Version:** v2.1

---

## Upcoming Features (Future Versions)

### Planned for v2.2+
- Dynamic position sizing based on win/loss streaks
- Token-specific performance tracking
- Auto-adjust confidence thresholds based on historical accuracy
- Blacklist decay (remove from blacklist after X days)

### Planned for v3.0 (TBD)
- Multi-strategy coordination (meme + arbitrage + perp)
- Machine learning confidence scoring
- Real-time market regime detection
- Adaptive parameter tuning

---

## Archive Master Replication Project

**Goal:** Replicate Archive Master's 626% profit run

**Archive Master Stats (Feb 15, 2026):**
- 295 trades, 38.9% win rate
- +3.13 SOL (+626%)
- 2.52x win/loss ratio
- Sources: DexScreener (229), both (61), PumpFun (5)
- **Age filter:** Broken (never filtered anything)

**Current Approach (v2.1):**
- ✅ No age filter (like Archive Master)
- ✅ 3-loss blacklist (improvement)
- 🔄 12% position size (Archive Master used 10% - need to change)
- 🔄 Remove subagent/shocked sources (if present)

**Next Steps:**
- Change position size to 10%
- Verify only 3 sources active (DexScreener, both, PumpFun)
- Run 50+ trades and compare to Archive Master baseline

---

**Last Updated:** Feb 16, 2026
**Maintainer:** Claude + User
