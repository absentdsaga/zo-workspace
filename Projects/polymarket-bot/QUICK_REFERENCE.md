# 🚀 Quick Reference Card

## Start the Bot
```bash
./run_bot.sh
```

## Monitor the Bot

### Option 1: Live Dashboard (Best)
```bash
/usr/local/bin/python3 stats_dashboard.py
```
- Real-time prices every 5 seconds
- Opportunity counter
- Best spread tracker
- Profit trend chart

### Option 2: Simple Monitor
```bash
./monitor.sh
```
Choose option 1 or 2.

## What to Look For

✅ **GOOD** - Profit ≥ 5%
```
💰 PROFIT: $0.0700 (7.00%) ⚡ OPPORTUNITY!
```

⚠️ **CLOSE** - Profit 2-5%
```
Profit: $0.0350 (3.50%)
```

❌ **NO EDGE** - Profit < 2%
```
Profit: $0.0050 (0.50%)
```

## Market Timing

- New markets every 5 minutes
- Launch at: XX:00, XX:05, XX:10, XX:15, etc.
- Best spreads in first 60 seconds

## Files You Need

| File | Purpose |
|------|---------|
| `HYBRID_bot.py` | Main bot code |
| `run_bot.sh` | Start bot |
| `stats_dashboard.py` | Live monitoring |
| `README.md` | Full documentation |
| `MONITORING.md` | Monitoring guide |

## Current Settings

```python
CHECK_INTERVAL = 10      # Check every 10 seconds
MIN_SPREAD_PROFIT = 0.05 # Alert at 5%+ profit
```

## Key Metrics

- **Price Checks**: How many times we fetched prices
- **Opportunities**: Times profit ≥ 5%
- **Best Spread**: Highest profit % seen
- **Runtime**: How long monitor has been running

## Troubleshooting

**No data showing?**
- Wait 5-10 seconds for first fetch
- Check internet connection

**Bot not finding opportunities?**
- This is normal - markets are often balanced
- Run for 30+ minutes to see multiple markets
- Best action happens in first minute of new markets

**Want to trade live?**
- See README.md "Next Steps for Live Trading"
- Add wallet + execution logic to HYBRID_bot.py
- Start small ($10-20)

## Success Criteria

Before going live, validate:
- ✅ Bot runs without errors
- ✅ Prices update every 10s
- ✅ You've seen 3+ opportunities in 1 hour
- ✅ Best spread ≥ 5% observed
- ✅ Markets auto-switch every 5 minutes

---

**Need Help?** Read the full docs in README.md and MONITORING.md
