# Mainnet Readiness Checklist

## ✅ COMPLETED: Retry Logic & Priority Fees (Option A)

### What Was Added:

**1. Optimized Executor Improvements** (`core/optimized-executor.ts`)
   - ✅ Exponential backoff retry logic (max 3 retries)
   - ✅ Dynamic priority fee multipliers:
     - Attempt 1: 1x base fee (~$0.0006)
     - Retry 1: 2x base fee (~$0.0012) after 3s delay
     - Retry 2: 5x base fee (~$0.0030) after 8s delay
     - Retry 3: 10x base fee (~$0.0060) after additional delay
   - ✅ Smart error classification:
     - **Retryable**: Network issues, timeouts, RPC errors, expired blockhash
     - **Non-retryable**: Slippage errors, insufficient liquidity, invalid signatures
   - ✅ Retry metrics tracking (retryCount, totalFeesSpent)

### Cost Analysis:
- **Monthly fees at current pace**: $1-3/month (even in high congestion)
- **Per trade**: $0.0006 - $0.0108 (worst case with all retries)
- **Compared to profit**: 0.022% of avg profit per trade
- **Cost/benefit**: Priority fees are **4,615x smaller** than avg profit

---

## ⏳ PENDING: Connect Paper Bot to Executor

**Current State**: Paper bot simulates trades with fake signatures
```typescript
signature: 'PAPER_TRADE_' + Date.now()  // ← Not using real executor
```

**Next Step**: Make paper bot call `executor.executeTrade()` in "dry-run" mode
- This will test the FULL execution path (quotes, swaps, retries) without actually sending transactions
- Benefits:
  - Test retry logic in paper mode
  - Validate priority fee calculations
  - Catch executor bugs before mainnet
  - Get realistic timing data

---

## 🎯 MAINNET LAUNCH CHECKLIST

### Before Going Live:

#### 1. **Start Small**
- [ ] Begin with **0.1 SOL** total capital
- [ ] Reduce position size from 12% → **5%** 
- [ ] Reduce max concurrent positions from 7 → **2-3**

#### 2. **Tighten Risk Controls**
- [ ] Lower stop loss from -30% → **-20%** (to account for real slippage)
- [ ] Lower slippage tolerance from 15% → **10%** (avoid catastrophic fills)
- [ ] Consider: Increase min smart money confidence from 45 → 50+

#### 3. **Monitor & Validate**
- [ ] Run paper trading for 1-2 more weeks
- [ ] Verify 30%+ win rate holds across different market conditions
- [ ] Check that profit/trade stays above $2 (to justify priority fees)

#### 4. **Test Executor Separately** (OPTIONAL)
```bash
cd Projects/survival-agent
bun run core/optimized-executor.ts --test
```
This will execute a real 0.005 SOL → USDC swap (~$0.60) to verify:
- Priority fees work
- Retry logic works
- Transaction confirmation works

#### 5. **When Ready for Mainnet**
- [ ] Change `PAPER_TRADE = true` → `PAPER_TRADE = false` in paper-trade-bot.ts
- [ ] Update bot to call `executor.executeTrade()` instead of simulating
- [ ] Start with 0.1 SOL and monitor for 24 hours
- [ ] Gradually increase capital only after proven stability

---

## 📊 Expected Mainnet Differences

| Factor | Paper Trading | Mainnet Reality |
|--------|--------------|-----------------|
| **Slippage** | 15% quoted | Can be 20-30% on meme coins |
| **Transaction Fees** | $0 | $0.0006 - $0.0108 per trade |
| **Failure Rate** | 0% | 5-10% even with retries |
| **MEV/Front-running** | None | 5-10% worse entry/exit prices |
| **Timing** | Instant | 400ms - 5s confirmation |
| **Rug Detection** | After the fact | Lose SOL before detecting |

**Bottom Line**: Your 32% win rate and $3.52 avg profit will likely decrease on mainnet, but should remain profitable if you start small and adjust parameters based on real data.

---

## 🚀 Performance Optimizations Already in Place

- ✅ Helius Gatekeeper RPC (4-7x faster)
- ✅ Priority Fee API integration
- ✅ Skip preflight for speed
- ✅ WebSocket confirmations
- ✅ Dynamic compute units
- ✅ Shocked alpha integration (priority signals)
- ✅ Jupiter price validation (not DexScreener)
- ✅ Rugged token blacklist

---

## 📝 Notes

**Created**: 2026-02-13
**Status**: Ready for paper testing with executor, NOT ready for mainnet yet
**Next Action**: User will decide when to test on mainnet
