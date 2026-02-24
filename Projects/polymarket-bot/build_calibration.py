#!/usr/local/bin/python3
"""
BUILD PRICE CALIBRATION
Matches blockchain trades with market resolutions to calculate actual win rates

This is the CRITICAL analysis that tells us:
- Do 20¢ bets actually win 20% of the time?
- Which price ranges have positive/negative edge?
- Is the Golden Range (20-40¢) hypothesis TRUE or FALSE?
"""
import pandas as pd
import numpy as np
from scipy.stats import binomtest
from collections import defaultdict
import json

print("=" * 80)
print("🔬 BUILDING PRICE CALIBRATION FROM REAL DATA")
print("=" * 80)
print()

# Load resolved markets
print("📥 Loading resolved markets...")
resolved_df = pd.read_csv('resolved_markets.csv')
print(f"✅ Loaded {len(resolved_df):,} resolved markets")

# Load blockchain trades
print("📥 Loading blockchain trades...")
trades_df = pd.read_csv('/tmp/poly_data/processed/trades.csv')
print(f"✅ Loaded {len(trades_df):,} trades")

# Load markets to get condition_id mapping
print("📥 Loading markets metadata...")
markets_df = pd.read_csv('/tmp/poly_data/markets.csv')
print(f"✅ Loaded {len(markets_df):,} markets")
print()

# Match: trades.market_id → markets.id → markets.condition_id → resolved.condition_id
# First, add condition_id to trades
# Remove NaN market_ids
trades_df = trades_df[trades_df['market_id'].notna()]
trades_df['market_id'] = trades_df['market_id'].astype(int)
markets_df['id'] = markets_df['id'].astype(int)

trades_with_condition = trades_df.merge(
    markets_df[['id', 'condition_id']],
    left_on='market_id',
    right_on='id',
    how='left'
)

print(f"🔗 Added condition_ids to {(trades_with_condition['condition_id'].notna()).sum():,} trades")

# Now merge with resolutions
print("🔗 Matching with resolutions...")
merged = trades_with_condition.merge(
    resolved_df[['condition_id', 'winner', 'question', 'outcomes']],
    on='condition_id',
    how='inner'
)
print(f"✅ Matched {len(merged):,} trades to resolved markets")
print(f"   ({len(merged)/len(trades_df)*100:.1f}% of all trades)")
print()

# CRITICAL INSIGHT: Each trade has a maker and taker
# We need to analyze from the BUYER's perspective only
# The 'price' field is: USDC paid / outcome tokens received
# This is the price the BUYER paid

# Filter to only BUY trades (where taker bought the outcome token)
buy_trades = merged[merged['taker_direction'] == 'BUY'].copy()

print(f"📊 Analyzing {len(buy_trades):,} BUY trades (ignoring SELL side)")
print()

# For buy trades:
# - nonusdc_side tells us which token was bought (token1 or token2)
# - price is what they paid for it
# - winner tells us which outcome won (0 or 1)

def did_buy_trade_win(row):
    """Check if a buy trade won"""
    try:
        # token1 = outcome 0, token2 = outcome 1
        if row['nonusdc_side'] == 'token1':
            bought_outcome = 0
        else:
            bought_outcome = 1

        return bought_outcome == row['winner']
    except:
        return None

buy_trades['won'] = buy_trades.apply(did_buy_trade_win, axis=1)
buy_trades = buy_trades[buy_trades['won'].notna()]

# Use buy_trades instead of merged
merged = buy_trades

print(f"📊 Analyzed {len(merged):,} trades with outcomes")
print()

# Build price calibration buckets
def get_price_bucket(price):
    """Categorize price into buckets"""
    if price < 0.05:
        return '0-5%'
    elif price < 0.10:
        return '5-10%'
    elif price < 0.20:
        return '10-20%'
    elif price < 0.30:
        return '20-30%'
    elif price < 0.40:
        return '30-40%'
    elif price < 0.50:
        return '40-50%'
    elif price < 0.60:
        return '50-60%'
    elif price < 0.70:
        return '60-70%'
    elif price < 0.80:
        return '70-80%'
    elif price < 0.90:
        return '80-90%'
    else:
        return '90-100%'

merged['bucket'] = merged['price'].apply(get_price_bucket)

# Calculate actual win rates per bucket
print("=" * 80)
print("🎯 PRICE CALIBRATION RESULTS")
print("=" * 80)
print()

calibration = {}

buckets = ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%',
           '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

print(f"{'Bucket':>10} | {'N Trades':>10} | {'Expected':>10} | {'Actual':>10} | {'Edge':>10} | {'p-value':>10} | {'Sig':>5}")
print("-" * 80)

results = []

for bucket in buckets:
    bucket_data = merged[merged['bucket'] == bucket]

    if len(bucket_data) < 10:  # Need minimum sample size
        continue

    n = len(bucket_data)
    wins = bucket_data['won'].sum()
    win_rate = wins / n

    # Expected probability (midpoint of bucket)
    bucket_ranges = {
        '0-5%': 0.025,
        '5-10%': 0.075,
        '10-20%': 0.15,
        '20-30%': 0.25,
        '30-40%': 0.35,
        '40-50%': 0.45,
        '50-60%': 0.55,
        '60-70%': 0.65,
        '70-80%': 0.75,
        '80-90%': 0.85,
        '90-100%': 0.95
    }

    expected_prob = bucket_ranges[bucket]
    edge = win_rate - expected_prob

    # Statistical significance
    binom_test = binomtest(wins, n, expected_prob, alternative='two-sided')
    p_value = binom_test.pvalue

    significant = "✓" if p_value < 0.05 else ""

    print(f"{bucket:>10} | {n:>10,} | {expected_prob*100:>9.1f}% | {win_rate*100:>9.1f}% | {edge*100:>+9.1f}% | {p_value:>10.4f} | {significant:>5}")

    calibration[bucket] = {
        'n': n,
        'expected': expected_prob * 100,
        'actual': win_rate * 100,
        'edge': edge * 100,
        'p_value': p_value
    }

    results.append({
        'bucket': bucket,
        'n': n,
        'expected': expected_prob,
        'actual': win_rate,
        'edge': edge,
        'p_value': p_value
    })

print()
print("=" * 80)
print("💎 KEY FINDINGS")
print("=" * 80)

# Find buckets with significant positive edge
positive_edge = [r for r in results if r['edge'] > 0 and r['p_value'] < 0.05]
negative_edge = [r for r in results if r['edge'] < 0 and r['p_value'] < 0.05]

if positive_edge:
    print("\n✅ POSITIVE EDGE (statistically significant):")
    for r in sorted(positive_edge, key=lambda x: x['edge'], reverse=True):
        print(f"   {r['bucket']}: +{r['edge']*100:.1f}% edge (n={r['n']:,}, p={r['p_value']:.4f})")

if negative_edge:
    print("\n❌ NEGATIVE EDGE (statistically significant):")
    for r in sorted(negative_edge, key=lambda x: x['edge']):
        print(f"   {r['bucket']}: {r['edge']*100:.1f}% edge (n={r['n']:,}, p={r['p_value']:.4f})")

# Check Golden Range specifically
print()
print("=" * 80)
print("🥇 GOLDEN RANGE (20-40¢) ANALYSIS")
print("=" * 80)

golden_buckets = ['20-30%', '30-40%']
golden_data = merged[merged['bucket'].isin(golden_buckets)]

if len(golden_data) > 0:
    total_trades = len(golden_data)
    total_wins = golden_data['won'].sum()
    win_rate = total_wins / total_trades
    expected = 0.30  # Midpoint of 20-40%
    edge = win_rate - expected

    binom_test = binomtest(total_wins, total_trades, expected, alternative='two-sided')

    print(f"\n📊 Combined 20-40¢ range:")
    print(f"   Total trades: {total_trades:,}")
    print(f"   Win rate: {win_rate*100:.2f}%")
    print(f"   Expected: {expected*100:.1f}%")
    print(f"   Edge: {edge*100:+.2f}%")
    print(f"   p-value: {binom_test.pvalue:.4f}")
    print(f"   Statistically significant: {'✅ YES' if binom_test.pvalue < 0.05 else '❌ NO'}")

    if edge > 0 and binom_test.pvalue < 0.05:
        print(f"\n🎯 CONCLUSION: Golden Range hypothesis CONFIRMED!")
        print(f"   Betting in 20-40¢ range has +{edge*100:.2f}% edge")
    elif edge < 0 and binom_test.pvalue < 0.05:
        print(f"\n❌ CONCLUSION: Golden Range hypothesis REJECTED!")
        print(f"   20-40¢ range has {edge*100:.2f}% edge (NEGATIVE)")
    else:
        print(f"\n⚠️  CONCLUSION: Inconclusive (not statistically significant)")

# Save calibration
print()
with open('price_calibration.json', 'w') as f:
    json.dump(calibration, f, indent=2)
print("💾 Calibration saved to: price_calibration.json")

print()
print("=" * 80)
