# Shocked Alpha Trading Group Integration

The paper trading bot now prioritizes alpha calls from the Shocked trading group.

## How It Works

1. **Priority System**: Shocked calls are checked FIRST before regular scanner
2. **Lower Threshold**: Shocked calls need score >= 30 (vs 40 for regular)
3. **Scoring Factors**:
   - Priority level (high/medium/low): +30/+15/+0 points
   - Freshness (<2h/6h/24h): +25/+15/+5 points
   - Momentum (price change, volume, buy pressure): up to +60 points

## Adding Shocked Calls

Use the CLI tool to add tokens from the group:

```bash
# High priority call with notes
bun add-shocked-call.ts HiNkp9CdKqTgPtB6WnnrrUAu9YwQqnrvT6Ceuxoypump Accelerando --high --notes "POW tweeted CA"

# Medium priority call
bun add-shocked-call.ts 84hqMeGHxqegpvf4kGaRp38iVd145DSoEBwnmBTtpump MooNutPeng --medium

# Low priority call (address only)
bun add-shocked-call.ts 0xa9FEE82374b20663B8702929dEF94D1D88B01E1F --low
```

## Example Calls from Recent Group Activity

Based on the Shocked chat dump, here are the recent calls:

```bash
# Accelerando (POW called it)
bun add-shocked-call.ts HiNkp9CdKqTgPtB6WnnrrUAu9YwQqnrvT6Ceuxoypump Accelerando --high --notes "POW tweeted CA"

# MooNutPeng (multiple calls)
bun add-shocked-call.ts 84hqMeGHxqegpvf4kGaRp38iVd145DSoEBwnmBTtpump MooNutPeng --high --notes "Group consensus"

# Lumen (called by multiple members)
bun add-shocked-call.ts 0xa9FEE82374b20663B8702929dEF94D1D88B01E1F Lumen --medium
```

## Watchlist Management

The watchlist is stored in `/tmp/shocked-watchlist.json` and automatically:
- ✅ Persists across bot restarts
- ✅ Removes calls older than 7 days
- ✅ Tracks priority, notes, and timing

View current watchlist:
```bash
bun add-shocked-call.ts  # Shows usage + current watchlist
```

## Integration with Paper Trader

The paper trader (`paper-trade-simple.ts`) now:

1. **Checks Shocked calls FIRST** (every 30-second scan cycle)
2. **Falls back to regular scanner** if no Shocked opportunities
3. **Logs source** so you can track which calls were traded
4. **Uses same runner strategy** (80/20 split on take profit)

Example output:
```
🎯 BUYING: Accelerando (Score: 85)
   Address: HiNkp9CdKqTgPtB6WnnrrUAu9YwQqnrvT6Ceuxoypump
   Source: SHOCKED GROUP
   ✅ Paper trade executed!
   💰 Entry price: $0.00001234
```

## Tips

- **High priority** for POW/trusted caller tweets with CA
- **Medium priority** for group consensus calls
- **Low priority** for interesting but unconfirmed mentions
- **Notes** help remember context when reviewing trades later
- **Fresh calls** (<2 hours) get the highest scoring bonus

## Starting the Bot

The Shocked integration is already built-in. Just start the paper trader normally:

```bash
bun testing/paper-trade-simple.ts
```

The bot will automatically:
- Load the Shocked watchlist
- Prioritize group calls
- Track which source each trade came from
