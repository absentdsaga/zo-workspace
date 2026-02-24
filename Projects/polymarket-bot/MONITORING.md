# 📊 Monitoring Guide

## Quick Start

```bash
./monitor.sh
```

Choose option 1 for the **Live Stats Dashboard** (recommended).

## Option 1: Live Stats Dashboard 📊

**Best for:** Watching the bot in real-time, tracking opportunities

```bash
/usr/local/bin/python3 stats_dashboard.py
```

### Features:
- ✅ Real-time price updates (every 5 seconds)
- ✅ Live profit calculations
- ✅ Opportunity counter
- ✅ Best spread tracker
- ✅ Profit trend chart
- ✅ Current market info
- ✅ Volume tracking

### What You'll See:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 POLYMARKET 5-MINUTE BOT - LIVE DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Runtime: 00:05:23
📊 Price Checks: 64
🎯 Opportunities Found: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 CURRENT MARKET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Market: btc-updown-5m-1771025400
UP Price:   $0.4800
DOWN Price: $0.4500
Total Cost: $0.9300
💰 PROFIT: $0.0700 (7.00%) ⚡ OPPORTUNITY!
Volume: $682.14

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 BEST SPREAD TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Profit: 12.50%
Market: btc-updown-5m-1771024800
Time: 18:23:45

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RECENT OPPORTUNITIES (Last 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[18:23:45] 12.50% profit - btc-updown-5m-1771024800
[18:25:12] 8.30% profit - btc-updown-5m-1771025100
[18:31:05] 7.00% profit - btc-updown-5m-1771025400

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PROFIT TREND (Last 20 checks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
18:31:05 | +7.00% | ████████████████ ⚡
18:31:10 | +2.50% | ██████
18:31:15 | +0.50% | █
18:31:20 | -1.00% | ░░
```

## Option 2: Simple Log Monitor 📋

**Best for:** Debugging, seeing raw output

```bash
./monitor_hybrid.sh
```

### Features:
- ✅ Color-coded output
- ✅ Real-time log streaming
- ✅ Shows bot errors
- ✅ Process status

**Note:** This requires the bot to be running with output redirected to `hybrid_bot.log`

## Running the Bot + Monitor

### Method 1: Two Terminals (Recommended)

**Terminal 1:**
```bash
./run_bot.sh
```

**Terminal 2:**
```bash
/usr/local/bin/python3 stats_dashboard.py
```

### Method 2: Background Bot + Dashboard

```bash
# Start bot in background
./run_bot.sh > hybrid_bot.log 2>&1 &

# Run dashboard
/usr/local/bin/python3 stats_dashboard.py
```

### Method 3: Just Dashboard (No Bot)

The dashboard works independently - it fetches prices directly from the API.
You don't need the bot running to see current market data.

```bash
/usr/local/bin/python3 stats_dashboard.py
```

## What the Dashboard Shows

### Metrics Explained:

- **Runtime**: How long the dashboard has been running
- **Price Checks**: Total number of times prices were fetched
- **Opportunities Found**: Times when profit ≥ 5% (UP + DOWN < $0.95)
- **UP/DOWN Price**: Current prices for each outcome
- **Total Cost**: Sum of UP + DOWN prices
- **Profit**: $1.00 - Total Cost (your guaranteed profit if you buy both)
- **Volume**: Trading volume for current market
- **Best Spread**: Highest profit % seen during this session

### Profit Indicators:

- ⚡ **Red bars**: Profit ≥ 5% = OPPORTUNITY!
- **Gray bars**: Profit 0-5% = Close but not quite
- **Light bars**: Negative profit = No edge

## Tips

1. **Let it run for 30+ minutes** to see multiple markets cycle
2. **Best opportunities** often appear in first 60 seconds of new market
3. **Markets rotate every 5 minutes** at :X0 and :X5
4. **Press Ctrl+C** to exit and see final stats
5. **Dashboard uses ~1 API call every 5 seconds** - very lightweight

## Troubleshooting

### Dashboard shows "Waiting for data..."
- Normal for first 5 seconds
- If it persists, check your internet connection
- Try: `curl https://gamma-api.polymarket.com/markets?slug=btc-updown-5m-1771025400`

### "No such file or directory: hybrid_bot.log"
- This is for monitor_hybrid.sh only
- Run the bot first: `./run_bot.sh > hybrid_bot.log 2>&1 &`

### Prices are always 0.50/0.50
- Market is perfectly balanced (no edge)
- Wait for next market or volatility
- This is normal - not all markets have arbitrage

---

**Pro Tip:** Run the dashboard on your main screen while doing other work. It updates automatically and will catch your attention when opportunities appear (look for the ⚡ symbol).
