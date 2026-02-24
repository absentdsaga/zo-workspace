# 📊 Monitoring Your Paper Trading Bot

## Quick Commands

### 1. Live Monitor Dashboard (Recommended)
```bash
./monitor_paper_trading.sh
```
- Shows live performance stats
- Recent opportunities
- Latest activity
- Auto-refreshes every 5 seconds

### 2. View Logs (Multiple Options)
```bash
./view_logs.sh
```
Choose from:
- Live tail (real-time)
- Last 50 lines
- All opportunities found
- Performance summaries
- Check if bot is running

### 3. Follow Log in Real-Time
```bash
tail -f paper_trading.log
```
See every line as it's written (Ctrl+C to exit)

### 4. Check if Bot is Running
```bash
ps aux | grep paper_trading_bot
```

### 5. View Results File (After Running)
```bash
cat paper_trading_results.json
```
Full session results in JSON format

## What to Look For

### ✅ Good Signs

```
💎 ARBITRAGE OPPORTUNITY FOUND (PAPER TRADE)
Market: Will Bitcoin be above $100K...
Expected profit: $0.85
✅ PAPER TRADE COMPLETED
   Simulated profit: $0.85
```

**Meaning:** Bot found and executed a profitable opportunity!

### 📊 Performance Update

```
Paper Balance: $103.50
Paper P&L: +$3.50 (+3.5%)
Opportunities Found: 5
Profitable Trades: 5
Win Rate: 100%
```

**Meaning:** Bot is finding opportunities and would be profitable

### ⚠️ Normal (Not Bad)

```
Opportunities Found: 0
```

**Meaning:** No opportunities right now (happens during efficient markets)

**Action:** Let it keep running - opportunities come in waves

## Monitoring Workflow

### During First Hour
```bash
# Start bot
./run_paper_trading.sh

# In another terminal, watch live
./monitor_paper_trading.sh
```

**What to expect:**
- May find 0-2 opportunities (normal)
- Bot scanning markets every 5 seconds
- Performance updates every 30 seconds

### After 4-8 Hours
```bash
# Check performance
./view_logs.sh
# Choose option 4 (Performance summaries)
```

**What to look for:**
- Total opportunities found
- Win rate (should be near 100%)
- Simulated profit

### After 24-48 Hours
```bash
# Stop bot (Ctrl+C in bot terminal)
# View final results
cat paper_trading_results.json
```

**Decision time:**
- 10+ trades, 90%+ win rate, positive profit → Deploy real money
- Less than 10 trades → Run longer
- Negative profit → Don't deploy (saved yourself!)

## Common Monitoring Scenarios

### "Is the bot working?"

```bash
./view_logs.sh
# Choose option 5 (Check if running)
```

Should show: ✅ Bot IS running

### "Has it found anything?"

```bash
./view_logs.sh
# Choose option 3 (View opportunities)
```

Will show all opportunities found

### "What's the current status?"

```bash
./monitor_paper_trading.sh
```

Live dashboard with all stats

### "I want to see everything happening"

```bash
tail -f paper_trading.log
```

Raw log output in real-time

## Files Generated

| File | Purpose |
|------|---------|
| `paper_trading.log` | Full session log (all activity) |
| `paper_trading_results.json` | Final results summary |

## Stopping the Bot

```bash
# In the terminal where bot is running
Press Ctrl+C
```

Bot will show final summary:
- Total trades
- Win rate  
- Total simulated profit
- Projections if you deployed real money

## Quick Reference

| Command | What It Shows |
|---------|---------------|
| `./monitor_paper_trading.sh` | Live dashboard |
| `./view_logs.sh` | Interactive log viewer |
| `tail -f paper_trading.log` | Real-time log feed |
| `cat paper_trading_results.json` | Final results |
| `ps aux | grep paper_trading` | Check if running |

## Troubleshooting

### "No opportunities for hours"

**Normal during:**
- Overnight (low volume)
- Efficient market periods
- After major news (markets adjust)

**Try:**
- Let it run longer (24+ hours)
- Run during high-volume times (market hours, sports events)
- Lower MIN_PROFIT_THRESHOLD in config.py to 0.003 (0.3%)

### "Monitor shows old data"

**Cause:** Bot might have stopped

**Check:**
```bash
ps aux | grep paper_trading_bot
```

If not running, restart:
```bash
./run_paper_trading.sh
```

### "Can't find paper_trading.log"

**Cause:** Bot hasn't been run yet

**Solution:**
```bash
./run_paper_trading.sh
```

## Next Steps

After 24-48 hours:

1. Stop bot (Ctrl+C)
2. Review `paper_trading_results.json`
3. If validated → Deploy real money (see QUICKSTART.md)
4. If not → Adjust config or run longer

---

**Start monitoring now:**

```bash
./monitor_paper_trading.sh
```

Or for simple real-time view:

```bash
tail -f paper_trading.log
```
