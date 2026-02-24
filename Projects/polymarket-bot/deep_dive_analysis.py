#!/usr/local/bin/python3
"""
DEEP DIVE ANALYSIS
Investigate WHY certain price ranges have edge

Questions to answer:
1. Is the edge real or data artifact?
2. Does it vary by category (sports vs politics)?
3. Does it vary by volume?
4. Does it vary by time period?
5. Are we seeing winner bias (only analyzing resolved markets)?
"""
import pandas as pd
import numpy as np
from scipy.stats import binomtest
import json

print("=" * 80)
print("🔬 DEEP DIVE: INVESTIGATING EDGE SOURCES")
print("=" * 80)
print()

# Recreate the full dataset
print("📥 Loading data...")
resolved_df = pd.read_csv('resolved_markets.csv')
trades_df = pd.read_csv('/tmp/poly_data/processed/trades.csv')
markets_df = pd.read_csv('/tmp/poly_data/markets.csv')

# Merge
trades_df = trades_df[trades_df['market_id'].notna()]
trades_df['market_id'] = trades_df['market_id'].astype(int)
markets_df['id'] = markets_df['id'].astype(int)

trades_with_condition = trades_df.merge(
    markets_df[['id', 'condition_id', 'question', 'volume']],
    left_on='market_id',
    right_on='id',
    how='left'
)

merged = trades_with_condition.merge(
    resolved_df[['condition_id', 'winner', 'category']],
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

# Add price buckets
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

buy_trades['bucket'] = buy_trades['price'].apply(get_price_bucket)

print(f"✅ Loaded {len(buy_trades):,} buy trades")
print()

# ==================== ANALYSIS 1: CATEGORY BREAKDOWN ====================
print("=" * 80)
print("📊 ANALYSIS 1: Edge by Category")
print("=" * 80)
print()

# Focus on heavy favorites (80-90%)
favorites = buy_trades[buy_trades['bucket'] == '80-90%'].copy()

print(f"Total 80-90% trades: {len(favorites):,}")
print(f"Overall win rate: {favorites['won'].mean()*100:.1f}%")
print()

# By category
print("Edge by category (80-90% range only):")
print(f"{'Category':>20} | {'N':>8} | {'Win%':>8} | {'Expected':>8} | {'Edge':>8}")
print("-" * 70)

category_results = []
for category in favorites['category'].value_counts().head(10).index:
    cat_data = favorites[favorites['category'] == category]
    n = len(cat_data)
    if n < 50:  # Minimum sample size
        continue

    win_rate = cat_data['won'].mean()
    expected = 0.85
    edge = win_rate - expected

    print(f"{category:>20} | {n:>8,} | {win_rate*100:>7.1f}% | {expected*100:>7.1f}% | {edge*100:>+7.1f}%")

    category_results.append({
        'category': category,
        'n': n,
        'win_rate': win_rate,
        'edge': edge
    })

print()

# ==================== ANALYSIS 2: VOLUME BREAKDOWN ====================
print("=" * 80)
print("📊 ANALYSIS 2: Edge by Market Volume")
print("=" * 80)
print()

# Add volume quartiles
favorites['volume_quartile'] = pd.qcut(favorites['volume'], q=4, labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)'], duplicates='drop')

print("Edge by volume quartile (80-90% range only):")
print(f"{'Quartile':>15} | {'N':>8} | {'Win%':>8} | {'Expected':>8} | {'Edge':>8}")
print("-" * 60)

for quartile in ['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)']:
    q_data = favorites[favorites['volume_quartile'] == quartile]
    n = len(q_data)
    if n < 10:
        continue

    win_rate = q_data['won'].mean()
    expected = 0.85
    edge = win_rate - expected

    print(f"{quartile:>15} | {n:>8,} | {win_rate*100:>7.1f}% | {expected*100:>7.1f}% | {edge*100:>+7.1f}%")

print()

# ==================== ANALYSIS 3: TIME PERIOD ====================
print("=" * 80)
print("📊 ANALYSIS 3: Edge by Time Period")
print("=" * 80)
print()

buy_trades['timestamp'] = pd.to_datetime(buy_trades['timestamp'])
buy_trades['month'] = buy_trades['timestamp'].dt.to_period('M')

favorites_time = buy_trades[buy_trades['bucket'] == '80-90%'].copy()
favorites_time['month'] = favorites_time['timestamp'].dt.to_period('M')

print("Edge over time (80-90% range only):")
print(f"{'Month':>15} | {'N':>8} | {'Win%':>8} | {'Expected':>8} | {'Edge':>8}")
print("-" * 60)

for month in sorted(favorites_time['month'].unique())[:12]:  # First 12 months
    month_data = favorites_time[favorites_time['month'] == month]
    n = len(month_data)
    if n < 50:
        continue

    win_rate = month_data['won'].mean()
    expected = 0.85
    edge = win_rate - expected

    print(f"{str(month):>15} | {n:>8,} | {win_rate*100:>7.1f}% | {expected*100:>7.1f}% | {edge*100:>+7.1f}%")

print()

# ==================== ANALYSIS 4: WINNER BIAS CHECK ====================
print("=" * 80)
print("📊 ANALYSIS 4: Winner Bias Check")
print("=" * 80)
print()

print("CRITICAL: Are we only seeing markets that resolved?")
print()

# Count total markets vs resolved markets
total_markets = len(markets_df)
resolved_markets = len(resolved_df)

print(f"Total markets in blockchain: {total_markets:,}")
print(f"Resolved markets in our data: {resolved_markets:,}")
print(f"Resolution rate: {resolved_markets/total_markets*100:.1f}%")
print()

# Check if resolved markets are biased toward certain outcomes
print("Winner distribution in resolved markets:")
winner_counts = resolved_df['winner'].value_counts()
print(f"Outcome 0 wins: {winner_counts.get(0, 0):,} ({winner_counts.get(0, 0)/len(resolved_df)*100:.1f}%)")
print(f"Outcome 1 wins: {winner_counts.get(1, 0):,} ({winner_counts.get(1, 0)/len(resolved_df)*100:.1f}%)")
print()

if abs(winner_counts.get(0, 0) - winner_counts.get(1, 0)) / len(resolved_df) > 0.1:
    print("⚠️  WARNING: Significant bias toward one outcome!")
    print("   This could indicate resolution bias in our dataset")

print()

# ==================== ANALYSIS 5: SAMPLE SIZE CHECK ====================
print("=" * 80)
print("📊 ANALYSIS 5: Sample Sizes")
print("=" * 80)
print()

buckets = ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%',
           '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

print(f"{'Bucket':>10} | {'N Trades':>10} | {'N Markets':>10} | {'Trades/Market':>15}")
print("-" * 60)

for bucket in buckets:
    bucket_data = buy_trades[buy_trades['bucket'] == bucket]
    n_trades = len(bucket_data)
    n_markets = bucket_data['condition_id'].nunique()

    if n_trades > 0:
        trades_per_market = n_trades / n_markets
        print(f"{bucket:>10} | {n_trades:>10,} | {n_markets:>10,} | {trades_per_market:>15.1f}")

print()
print("⚠️  If trades/market is very high, we might be seeing:")
print("   - Repeated trades on same markets")
print("   - Not independent samples")
print()

# ==================== ANALYSIS 6: PER-MARKET CALIBRATION ====================
print("=" * 80)
print("📊 ANALYSIS 6: Per-Market Analysis (80-90% range)")
print("=" * 80)
print()

# Instead of per-trade, analyze per-market
# For each market, what was the average price and did it resolve to that outcome?

favorites_markets = favorites.groupby('condition_id').agg({
    'price': 'mean',
    'won': 'first',  # All trades in same market have same outcome
    'question': 'first',
    'volume': 'first'
}).reset_index()

print(f"Unique markets in 80-90% range: {len(favorites_markets):,}")
print(f"Markets that resolved to the favorite: {favorites_markets['won'].sum():,}")
print(f"Market-level win rate: {favorites_markets['won'].mean()*100:.1f}%")
print()

# Statistical test on MARKETS not trades
n_markets = len(favorites_markets)
wins = favorites_markets['won'].sum()
expected = 0.85

binom_test = binomtest(wins, n_markets, expected, alternative='two-sided')

print(f"Statistical test (market-level):")
print(f"   Expected: {expected*100:.1f}%")
print(f"   Actual: {wins/n_markets*100:.1f}%")
print(f"   Edge: {(wins/n_markets - expected)*100:+.1f}%")
print(f"   p-value: {binom_test.pvalue:.4f}")
print(f"   Significant: {'YES' if binom_test.pvalue < 0.05 else 'NO'}")

print()
print("=" * 80)
print("🎯 CONCLUSION")
print("=" * 80)
print()
print("The per-MARKET analysis is more accurate than per-TRADE")
print("because multiple trades on same market aren't independent.")
print()
