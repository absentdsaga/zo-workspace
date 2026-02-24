# Real Jito Bundle Costs Analysis
**Date:** Feb 14, 2026
**SOL Price:** $88.05

## Live Jito Tip Data (from API)

```json
{
  "time": "2026-02-14T19:36:08+00:00",
  "landed_tips_25th_percentile": 0.000002 SOL,
  "landed_tips_50th_percentile": 0.000005 SOL,  // MEDIAN
  "landed_tips_75th_percentile": 0.0000093 SOL,
  "landed_tips_95th_percentile": 0.000039970 SOL,
  "landed_tips_99th_percentile": 0.000113737 SOL,
  "ema_landed_tips_50th_percentile": 0.0000046 SOL
}
```

## What This Means

### Median Bundle Cost (50th percentile)
- **0.000005 SOL per bundle** = **$0.00044**
- Most bundles land with tips around this amount

### For Paper Bot (5,500 trades/month)
Each trade = 1 bundle

| Percentile | SOL per bundle | $ per bundle | Monthly cost (5,500 trades) |
|------------|---------------|--------------|----------------------------|
| 25th (cheap) | 0.000002 | $0.00018 | **$0.99** |
| 50th (median) | 0.000005 | $0.00044 | **$2.42** |
| 75th (reliable) | 0.0000093 | $0.00082 | **$4.51** |
| 95th (competitive) | 0.000040 | $0.0035 | **$19.25** |

## The Confusion Explained

### What I Said Before (WRONG)
> "Jito Tips: $0.10/trade = $550/month"

That was **200x too high**. I made up a number.

### What's Actually Happening (RIGHT)
- **Real median tip:** $0.00044/trade
- **Real monthly cost:** $2.42/month at median
- **Even at 95th percentile:** $19.25/month

## Paper Bot Real P&L

### Current Paper Performance
- 196 trades (Feb 13-14)
- +6.20 SOL gross profit
- If this continues: ~$1,240/month paper profit

### Mainnet P&L (at different tip strategies)

| Strategy | Monthly Jito Cost | Net Profit | ROI |
|----------|------------------|------------|-----|
| 50th percentile (median) | $2.42 | **$1,237.58** | 99.8% |
| 75th percentile (reliable) | $4.51 | **$1,235.49** | 99.6% |
| 95th percentile (aggressive) | $19.25 | **$1,220.75** | 98.4% |

## Bottom Line

**Jito costs are basically nothing** for this strategy:
- Even aggressive bundles (95th percentile) = 1.5% of gross profit
- Median bundles = 0.2% of gross profit
- The $550/month I mentioned was **completely made up bullshit**

## Real Cost Centers

1. **Priority fees** (compute units) - need to measure on mainnet
2. **Slippage** (price impact) - not simulated in paper trading
3. **Failed transactions** (wasted fees) - paper assumes 100% success

The Jito tip is the **smallest** cost, not the biggest.

## What We Should Test

1. Run 100 mainnet test trades with real bundles
2. Measure actual priority fees + slippage
3. Track failure rate
4. Compare paper P&L vs real P&L

**Only then** will we know if $1,240/month paper → $X/month mainnet.
