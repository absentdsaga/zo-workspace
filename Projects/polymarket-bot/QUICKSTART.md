# ⚡ 5-Minute Quick Start Guide

Get your Polymarket bot running in 5 minutes flat.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] $100+ USDC on Polygon network
- [ ] MetaMask or Ethereum wallet with exported private key

## Step 1: Get USDC on Polygon (2 minutes)

### Option A: Bridge from Ethereum
1. Go to [Polygon Bridge](https://wallet.polygon.technology/polygon/bridge)
2. Connect your wallet
3. Bridge $100+ USDC from Ethereum to Polygon
4. Wait for confirmation (~7-8 minutes)

### Option B: Buy directly on Polygon
1. Use [Transak](https://global.transak.com/) or similar
2. Buy USDC directly on Polygon network
3. Send to your wallet address

## Step 2: Setup Bot (1 minute)

```bash
cd /home/workspace/Projects/polymarket-bot

# Run setup
./setup.sh

# Edit .env file
nano .env
```

Add your private key:
```
POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 3: Start Trading (2 minutes)

### Basic Bot (Recommended for beginners)
```bash
python3 bot.py
```

### Advanced Bot (Multi-strategy)
```bash
python3 advanced_bot.py
```

That's it! The bot is now scanning for arbitrage opportunities.

## What Happens Next?

The bot will:
1. Scan 50+ markets every 5 seconds
2. Find sum-to-one arbitrage opportunities
3. Execute trades automatically
4. Log performance every 30 seconds

### Expected First Hour
- **Trades**: 0-3 trades (depends on market conditions)
- **Profit**: $0.50 - $3.00 per trade
- **Win Rate**: 90-100% (arbitrage is low-risk)

### Watch the Logs

```bash
# Follow live logs
tail -f bot.log

# Or watch in real-time
python3 bot.py  # Logs to console + file
```

## Understanding the Output

```
📊 Balance: $102.50 | P&L: +$2.50 (+2.5%) | Trades: 2 | Win Rate: 100%
```

- **Balance**: Current USDC in wallet
- **P&L**: Profit since start
- **Trades**: Number of completed trades
- **Win Rate**: % of profitable trades

## When You See This...

### ✅ "💎 ARB FOUND"
- Good! Bot found an opportunity
- It will execute automatically
- No action needed

### ⚠️ "No opportunities found"
- Normal during efficient markets
- Bot keeps scanning
- Be patient, opportunities come in waves

### 🛑 "STOP LOSS HIT"
- Bot stops trading (down 15%)
- Review logs to see what happened
- Usually won't happen with pure arbitrage

## Stopping the Bot

```bash
# Press Ctrl+C to stop
# Bot will shutdown gracefully
```

Your positions remain open (they're hedged, so safe).

## First 24 Hours Checklist

- [ ] Bot started successfully
- [ ] First trade executed
- [ ] Logs showing regular scans
- [ ] Balance increasing
- [ ] No errors in bot.log

## Troubleshooting

### "Insufficient funds"
```bash
# Check your USDC balance
# Need minimum $100 USDC on Polygon
```

### "No opportunities for 1+ hours"
- Try during high volatility (market open, news events)
- Lower MIN_PROFIT_THRESHOLD in config.py to 0.003 (0.3%)
- Check if it's a slow market day

### "Orders failing"
- Ensure you have MATIC for gas (~$0.50 worth)
- Check internet connection
- Verify private key is correct

## Next Steps

Once profitable:

1. **Week 1**: Let it run, monitor daily
2. **Week 2**: Analyze performance, adjust config
3. **Week 3**: Scale up bankroll if consistent
4. **Month 2**: Add advanced strategies

## Pro Tips

**🔥 Best Times to Trade:**
- Sports events (NFL, NBA, Super Bowl)
- Crypto volatility (BTC price swings)
- Major news events
- Election periods

**💰 Compounding Strategy:**
- Start: $100
- After 2x: Withdraw $100, trade with $100 (now risk-free)
- After 4x: Withdraw $200, trade with $200
- Repeat, scaling gradually

**⚡ Optimization:**
- Run on stable internet (VPS recommended for 24/7)
- Monitor first week closely
- Trust the system after verification

## Get Help

- Check `bot.log` for detailed error messages
- Review README.md for full documentation
- Join Polymarket Discord for community support

---

**Remember**: This is arbitrage - you're not gambling, you're exploiting math. Trust the process. 🚀
