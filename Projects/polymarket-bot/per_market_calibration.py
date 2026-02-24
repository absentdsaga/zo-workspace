#!/usr/local/bin/python3
"""
PER-MARKET CALIBRATION
The CORRECT way to analyze - treating each market as one sample
"""
import pandas as pd
import numpy as np
from scipy.stats import binomtest
import json

print("=" * 80)
print("🔬 PER-MARKET CALIBRATION (CORRECT METHOD)")
print("=" * 80)
print()

# Load data
resolved_df = pd.read_csv('resolved_markets.csv')
trades_df = pd.read_csv('/tmp/poly_data/processed/trades.csv')
markets_df = pd.read_csv('/tmp/poly_data/markets.csv')

# Merge
trades_df = trades_df[trades_df['market_id'].notna()]
trades_df['market_id'] = trades_df['market_id'].astype(int)
markets_df['id'] = markets_df['id'].astype(int)

trades_with_condition = trades_df.merge(
    markets_df[['id', 'condition_id']],
    left_on='market_id',
    right_on='id',
    how='left'
)

merged = trades_with_condition.merge(
    resolved_df[['condition_id', 'winner', 'question']],
    on='condition_id',
    how='inner'
)

# Get buy trades only
buy_trades = merged[merged['taker_direction'] == 'BUY'].copy()

# Determine winner
def did_buy_trade_win(row):
    try:
        if row['nonusdc_side'] == 'token1':
            bought_outcome = 0
        else:
            bought_outcome = 1
        return bought_outcome == row['winner']
    except:
        return None

buy_trades['won'] = buy_trades.apply(did_buy_trade_win, axis=1)
buy_trades = buy_trades[buy_trades['won'].notna()]

print(f"✅ Loaded {len(buy_trades):,} buy trades")
print()

# Group by market and get average price
market_summary = buy_trades.groupby('condition_id').agg({
    'price': 'mean',  # Average price traded at
    'won': 'first',   # Did this outcome win? (same for all trades in market)
    'question': 'first'
}).reset_index()

print(f"✅ Aggregated into {len(market_summary):,} unique markets")
print()

# Bucket by average price
def get_price_bucket(price):
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

market_summary['bucket'] = market_summary['price'].apply(get_price_bucket)

# Calculate calibration
print("=" * 80)
print("🎯 PER-MARKET CALIBRATION")
print("=" * 80)
print()

buckets = ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%',
           '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

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

print(f"{'Bucket':>10} | {'N Markets':>10} | {'Expected':>10} | {'Actual':>10} | {'Edge':>10} | {'p-value':>10} | {'Sig':>5}")
print("-" * 85)

results = []

for bucket in buckets:
    bucket_data = market_summary[market_summary['bucket'] == bucket]

    if len(bucket_data) < 10:
        continue

    n = len(bucket_data)
    wins = bucket_data['won'].sum()
    win_rate = wins / n
    expected = bucket_ranges[bucket]
    edge = win_rate - expected

    binom_test = binomtest(wins, n, expected, alternative='two-sided')
    p_value = binom_test.pvalue
    significant = "✓" if p_value < 0.05 else ""

    print(f"{bucket:>10} | {n:>10,} | {expected*100:>9.1f}% | {win_rate*100:>9.1f}% | {edge*100:>+9.1f}% | {p_value:>10.4f} | {significant:>5}")

    results.append({
        'bucket': bucket,
        'n_markets': n,
        'expected': expected,
        'actual': win_rate,
        'edge': edge,
        'p_value': p_value
    })

print()
print("=" * 80)
print("💎 KEY FINDINGS")
print("=" * 80)

positive_edge = [r for r in results if r['edge'] > 0 and r['p_value'] < 0.05]
negative_edge = [r for r in results if r['edge'] < 0 and r['p_value'] < 0.05]

if positive_edge:
    print("\n✅ POSITIVE EDGE (statistically significant):")
    for r in sorted(positive_edge, key=lambda x: x['edge'], reverse=True):
        print(f"   {r['bucket']}: +{r['edge']*100:.1f}% edge (n={r['n_markets']:,}, p={r['p_value']:.4f})")
else:
    print("\n❌ NO STATISTICALLY SIGNIFICANT POSITIVE EDGE FOUND")

if negative_edge:
    print("\n❌ NEGATIVE EDGE (statistically significant):")
    for r in sorted(negative_edge, key=lambda x: x['edge']):
        print(f"   {r['bucket']}: {r['edge']*100:.1f}% edge (n={r['n_markets']:,}, p={r['p_value']:.4f})")
else:
    print("\n✅ NO STATISTICALLY SIGNIFICANT NEGATIVE EDGE FOUND")

# Golden Range check
print()
print("=" * 80)
print("🥇 GOLDEN RANGE (20-40¢) ANALYSIS")
print("=" * 80)

golden_data = market_summary[market_summary['bucket'].isin(['20-30%', '30-40%'])]

if len(golden_data) > 0:
    n = len(golden_data)
    wins = golden_data['won'].sum()
    win_rate = wins / n
    expected = 0.30
    edge = win_rate - expected

    binom_test = binomtest(wins, n, expected, alternative='two-sided')

    print(f"\n📊 Combined 20-40¢ range:")
    print(f"   Markets: {n:,}")
    print(f"   Win rate: {win_rate*100:.2f}%")
    print(f"   Expected: {expected*100:.1f}%")
    print(f"   Edge: {edge*100:+.2f}%")
    print(f"   p-value: {binom_test.pvalue:.4f}")
    print(f"   Statistically significant: {'✅ YES' if binom_test.pvalue < 0.05 else '❌ NO'}")

# Save results
with open('per_market_calibration.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print()
print("💾 Per-market calibration saved to: per_market_calibration.json")
print()
print("=" * 80)
