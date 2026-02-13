# 📄 Paper Trader Upgrades

## ✅ Fixed Issues

### 1. **Exit Logic Now Running**
Previously: Positions opened but never closed
Now:
- Checks all open positions every loop
- Take profit at +100%
- Stop loss at -30%
- Max hold time: 60 minutes
- Auto-closes and returns SOL to balance

### 2. **Duplicate Prevention**
Previously: Bought "Hot dog" 6 times in a row
Now:
- Checks if token already held before buying
- Only one position per token at a time
- Scans for next best opportunity if top pick is already owned

### 3. **Position Tracking**
Now tracks:
- Entry price (simulated)
- Current price (simulated with random walk)
- P&L per position in SOL and %
- Hold time in minutes
- Exit reason when closed

### 4. **Real-Time Holdings Tracker**
New tool: `monitoring/holdings-tracker.ts`
- Parses log file for open positions
- Fetches live prices from DexScreener API
- Shows current P&L
- Groups duplicate positions
- Detects rugged/delisted tokens

## 🚀 New Commands

**Start Paper Trader (with upgrades):**
```bash
cd /home/workspace/Projects/survival-agent && \
nohup bun run testing/paper-trade-master.ts > /tmp/paper-trade-final.log 2>&1 & \
echo "Started with PID: $!"
```

**Monitor (spam-resistant):**
```bash
/home/workspace/Projects/survival-agent/monitoring/watch-paper-summary.sh
```

**Check Holdings:**
```bash
bun run /home/workspace/Projects/survival-agent/monitoring/holdings-tracker.ts
```

**Quick Status:**
```bash
/home/workspace/Projects/survival-agent/monitoring/show-holdings.sh
```

**Stop:**
```bash
pkill -f paper-trade-master
```

## 📊 What You'll See Now

### Entry (Buy)
```
4️⃣  🎯 HIGH CONFIDENCE SIGNAL - EXECUTING TRADE
   Position: 0.0496 SOL (10.0%)

   📄 PAPER TRADING - SIMULATING TRADE...

   ✅ TRADE SIMULATED SUCCESSFULLY
```

### Position Monitoring (Every Loop)
```
💼 Checking 1 open position(s)...

   📊 PEPE:
      Entry: $0.00005230 | Current: $0.00006145
      P&L: +17.50% (+0.0087 SOL)
      Hold time: 15.3 min
      ⏳ Holding...
```

### Exit (Sell)
```
   📊 PEPE:
      Entry: $0.00005230 | Current: $0.00011506
      P&L: +120.04% (+0.0595 SOL)
      Hold time: 45.2 min
      🚪 EXITING: Take profit hit (+100%)
      ✅ Position closed
```

### System Health
```
5️⃣  System health:
   ✅ Status: HEALTHY
   💰 Balance: 0.5550 SOL
   📊 P&L: +0.0595 SOL (+12.01%)
   ⏰ Runway: 6.6 days
   📈 Total Trades: 3 | Open: 1 | Closed: 2 (2W/0L) - 100% win rate
```

## 🔄 Next Steps

1. **Clear old log** (6 bad Hot dog positions):
   ```bash
   rm /tmp/paper-trade-final.log
   ```

2. **Start fresh run**:
   ```bash
   cd /home/workspace/Projects/survival-agent && \
   nohup bun run testing/paper-trade-master.ts > /tmp/paper-trade-final.log 2>&1 &
   ```

3. **Monitor in real-time**:
   ```bash
   /home/workspace/Projects/survival-agent/monitoring/watch-paper-summary.sh
   ```

4. **Check holdings anytime**:
   ```bash
   bun run /home/workspace/Projects/survival-agent/monitoring/holdings-tracker.ts
   ```

## 🎯 Expected Behavior

- Scans every 30 seconds
- Finds opportunities scoring ≥60
- Only buys tokens not already held
- Monitors all open positions every loop
- Auto-exits at +100%, -30%, or 60min
- Shows live P&L for each position
- Tracks win rate and total P&L
- Stops if balance drops below 0.05 SOL or 25% drawdown

## ⚠️ Notes

- Price movement is simulated (-20% to +20% random walk per loop)
- In real trading, would fetch actual prices from DexScreener
- Entry prices are randomized for simulation purposes
- This is a 1:1 simulation of the master coordinator logic
