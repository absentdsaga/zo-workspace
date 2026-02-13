# Paper Trading Bot - Quick Reference Card

## 🚀 Start the Bot
```bash
cd /home/workspace/Projects/survival-agent
bash start-paper-master-fixed.sh
```

## ⚙️ Configuration

| Setting | Value | What it does |
|---------|-------|--------------|
| Scanner interval | 15s | Find new opportunities |
| Monitor interval | 5s | Check positions |
| Max positions | 10 | Concurrent tokens |
| Position size | 8% | Per trade |
| TP1 (trailing activates) | +100% | When to switch strategies |
| Trailing stop | 20% | Drop from peak |
| Stop loss (before TP1) | -30% | Regular stop |
| Max hold time | 60 min | Force exit |

## 📊 Exit Strategy

### Before +100%
- Regular stop-loss: **-30%**
- Max hold: **60 minutes**

### After +100% (TP1 Hit)
- Trailing stop: **20% from peak**
- Max hold: **60 minutes**
- **No downside limit** (already profitable)

## 🎯 What to Look For

### Good Signs ✅
- `🎯 TP1 HIT! Trailing stop activated`
- Peak prices well above entry
- Exits at +150%, +200%, +300%
- `[both]` source tags (found in both scanners)

### Warning Signs ⚠️
- Many rugged tokens (no sell route)
- Always hitting -30% stop-loss
- Never reaching TP1
- Max positions always full (missing opportunities)

## 📈 Understanding the Output

```
📊 PEPE [both]:
   Entry: $0.00001234 | Current: $0.00003500
   Peak: $0.00003500 (+183.63%)
   P&L: +183.63% (+0.0734 SOL)
   Hold time: 3.5 min
   Status: 🔥 TRAILING STOP ACTIVE
```

- **Entry**: Your buy price
- **Current**: Right now price
- **Peak**: Highest price seen
- **P&L**: Current profit/loss
- **[both]**: Found in both scanners (+20 score bonus)
- **🔥 TRAILING STOP ACTIVE**: TP1 hit, riding the wave

## 🔄 Trading Cycle

1. **Scanner finds opportunity** (15s cycle)
2. **Validates with Jupiter** (can we buy/sell?)
3. **Checks smart money** (confidence score)
4. **Enters position** (if all checks pass)
5. **Monitor checks price** (every 5s)
6. **Updates peak price** (if new high)
7. **Checks TP1** (hit +100%?)
8. **Applies exit strategy** (based on phase)
9. **Executes sell** (when conditions met)

## 🎲 Example Scenarios

### Scenario A: Early Exit
```
Entry: $100
Peak: $80 (-20%)
Exit: $70 (-30% stop-loss)
Result: -30% loss
```

### Scenario B: Modest Gain
```
Entry: $100
Peak: $150 (+50%)
Exit: Max hold time (60 min)
Result: +50% gain
```

### Scenario C: Hit TP1, Small Runner
```
Entry: $100
Peak: $220 (+120%)
Drops to: $176 (20% below peak)
Exit: Trailing stop triggered
Result: +76% gain
```

### Scenario D: Big Runner
```
Entry: $100
Peak: $500 (+400%)
Drops to: $400 (20% below peak)
Exit: Trailing stop triggered
Result: +300% gain
```

### Scenario E: Rugged
```
Entry: $100
Peak: $250 (+150%)
Jupiter: "No sell route"
Exit: Total loss
Result: -100% loss
```

## 💡 Tips

1. **Watch scanner sources**: Tokens found in `[both]` are highest confidence
2. **Peak tracking**: Big difference between peak and exit = good trailing stop
3. **TP1 frequency**: If never hitting +100%, lower threshold or improve entry
4. **Position count**: Should average 5-8 open. If always 10, scanner too aggressive
5. **Rugged rate**: >20% rugged = need better token filtering

## 📁 Documentation Files

- `UPGRADE-SUMMARY.md` - What changed and why
- `TRAILING-STOP-UPDATE.md` - Detailed trailing stop explanation
- `SYSTEM-ARCHITECTURE.md` - Visual diagrams
- `QUICK-REFERENCE.md` - This file

## 🆘 Troubleshooting

**Bot not entering positions:**
- Check scanner is finding opportunities
- Verify Jupiter routes are valid
- Smart money confidence might be too low

**Bot exiting too early:**
- Increase trailing stop % (currently 20%)
- Check if TP1 threshold is too high

**Bot holding too long:**
- Decrease max hold time
- Tighten trailing stop %

**Too many rugged tokens:**
- Increase min score threshold
- Require higher smart money confidence
