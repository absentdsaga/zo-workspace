# Jito Competitive Reality Check

## Your Experience vs API Data

### Current Jito API (Feb 14, 2026)
| Percentile | SOL | USD |
|------------|-----|-----|
| 50th (median) | 0.000005 | $0.00044 |
| 75th | 0.000039 | $0.0035 |
| 95th | 0.001 | $0.088 |
| **99th** | **0.011** | **$0.98** |

### Your Bot Trading Experience
- **Typical competitive tip:** 0.1 SOL ($8.80)
- **Context:** Bid war with other bots
- **10x higher than current 99th percentile**

## The Critical Questions

### 1. When Was Your 0.1 SOL Experience?
- **Year/timeframe?**
- **SOL price then?** (0.1 SOL at $20 = $2, at $200 = $20)
- **Type of bot?** (MEV, token launch, arbitrage)

### 2. Was 0.1 SOL for EVERY Trade?
- Or just during peak competition?
- Average across all trades?
- Or specifically for profitable opportunities?

### 3. Smart Money Tracking Competition
- **Are other bots watching these wallets?**
- **How competitive is this alpha vs traditional MEV?**

## Worst Case Math (0.1 SOL/trade)

| Metric | Value |
|--------|-------|
| Paper profit | $1,240/month |
| Jito tips (5,500 trades × 0.1 SOL × $88) | **-$48,400/month** |
| **NET PROFIT** | **-$47,160** |

☠️ **COMPLETELY DEAD STRATEGY**

## Best Case Math (0.011 SOL/trade - 99th percentile)

| Metric | Value |
|--------|-------|
| Paper profit | $1,240/month |
| Jito tips (5,500 trades × 0.011 SOL × $88) | **-$5,324/month** |
| **NET PROFIT** | **-$4,084** |

💀 **STILL DEAD**

## Breakeven Analysis

For $1,240 paper profit with 5,500 trades:

**Max viable Jito tip:** $1,240 ÷ 5,500 = **$0.225 per trade**

In SOL @ $88: **0.0026 SOL per trade**

This is between **95th percentile (0.001 SOL)** and **99th percentile (0.011 SOL)**

## The Real Question

**Does smart money tracking require competitive Jito tips?**

- Traditional MEV (arbitrage, liquidations) = **HIGHLY competitive**
- Token launches = **HIGHLY competitive**
- Smart money copy trading = **???**

If there are 100 other bots watching the same wallets, you need competitive tips.

If there are only a few, you can use median tips.

## What We Need to Know

1. **Your historical context** (when, SOL price, bot type)
2. **Test on mainnet** with varying tip levels:
   - Start at 75th percentile (0.000039 SOL = $0.0035)
   - Track success rate
   - Increase tips only if bundles fail to land
3. **Monitor competition** - are our bundles landing or getting outbid?

## My Suspicion

I think 0.1 SOL tips were either:
- During high SOL price ($200+) = $20 per trade
- During extreme MEV competition (2021-2022 bot wars)
- For high-value opportunities only (not every trade)

Current 99th percentile is 0.011 SOL ($0.98), which suggests the **competitive tip level is closer to $1-2**, not $10.

But we won't know until we test on mainnet.
