# 🚀 QUICK START - AUTONOMOUS TRADING

**Get live in 60 seconds**

---

## Step 1: Verify Environment (5 seconds)

```bash
echo "Private key set: $([ -n "$SOLANA_PRIVATE_KEY" ] && echo '✅' || echo '❌')"
echo "Jupiter API set: $([ -n "$JUP_TOKEN" ] && echo '✅' || echo '❌')"
echo "Helius API set: $([ -n "$HELIUS_RPC_URL" ] && echo '✅' || echo '❌')"
```

All three must show ✅

---

## Step 2: Navigate to Project (5 seconds)

```bash
cd /home/workspace/Projects/survival-agent
```

---

## Step 3: Start Autonomous Trading (50 seconds)

```bash
bun run core/master-coordinator.ts
```

**That's it!** The system is now:
- Scanning for opportunities every 30 seconds
- Auto-executing trades on high-confidence signals (score ≥60)
- Managing risk with circuit breakers
- Tracking P&L and health

---

## What You'll See

```
🤖 Master Coordinator initialized
⚙️  Autonomous trading mode

🔧 Initializing autonomous trading system...
[Pre-flight checks run...]

✅ System initialized and ready
💰 Starting balance: 0.3352 SOL
🎯 Risk parameters:
   Max position: 10%
   Min score: 60
   Max drawdown: 25%
   Emergency stop: 0.05 SOL

🚀 Starting autonomous trading loop...
🔄 Scanning every 30 seconds
🤖 Will auto-execute on high-confidence signals
⚠️  Press Ctrl+C to stop

============================================================
Loop 1 - 10:30:15 AM
============================================================

1️⃣  Scanning for opportunities...
   Found 12 potential opportunities
   3 meet minimum score (≥60)

2️⃣  Analyzing top opportunity:
   Token: PEPE (A5cD3f...)
   Score: 78/100
   Age: 8 minutes
   Signals: volume_spike, price_momentum, fresh_launch

3️⃣  Smart money analysis:
   Confidence: 65/100
   Reasons: High 1h volume: $125k, Strong buy pressure: 72% buys

4️⃣  🎯 HIGH CONFIDENCE SIGNAL - EXECUTING TRADE
   Position: 0.0268 SOL (8.0%)

   [Trade execution output...]

   ✅ TRADE EXECUTED SUCCESSFULLY
   Signature: 5wZ1Fc...
   Speed: 412ms
   View: https://solscan.io/tx/5wZ1Fc...

5️⃣  System health:
   ✅ Status: HEALTHY
   💰 Balance: 0.3352 SOL
   📊 P&L: +0.0000 SOL (+0.00%)
   ⏰ Runway: 4.0 days
   📈 Trades: 1 (0W/0L) - 0% win rate

⏳ Sleeping for 30 seconds...
```

---

## Stop Trading

Press **Ctrl+C** to stop gracefully.

---

## Circuit Breakers

System will auto-pause if:
- Balance drops below 0.05 SOL
- 25% drawdown in one session
- 5 consecutive failed trades

**To restart**: Fix issue, run command again.

---

## Monitor Progress

### Check Balance
```bash
bun run monitoring/health-check.ts
```

### Check Recent Trades
View logs in terminal output or check Solscan with wallet address.

---

## Troubleshooting

**No opportunities found**:
- Markets may be slow
- Filters may be too strict
- Try during high-activity hours (US market open)

**Execution failures**:
- Check balance is sufficient
- Verify Jupiter API key is valid
- Check Helius RPC is responding

**Circuit breaker triggered**:
- Review what threshold was hit
- Check balance, P&L, trade history
- Adjust if needed, restart

---

## Key Files

- `core/master-coordinator.ts` - Main autonomous system
- `core/optimized-executor.ts` - Trade execution (398ms avg)
- `strategies/meme-scanner.ts` - Opportunity finder
- `strategies/smart-money-tracker.ts` - Whale activity tracker

---

## Success Metrics

**Target**: 10x in 30 days to survive

**Current runway**: 4 days

**Compounding example**:
- Day 1: $41 → $50 (+22%)
- Day 5: $50 → $85 (+70%)
- Day 10: $85 → $150 (+76%)
- Day 20: $150 → $300 (+100%)
- Day 30: $300 → $500 (+67%)

**Total**: 12x in 30 days ✅

---

*Time to trade. Go make that alpha.* 🚀
