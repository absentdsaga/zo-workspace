#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

# Fetch markets
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

print("🌍 POLYMARKET LANDSCAPE ANALYSIS")
print("=" * 80)

# Analyze by price range
price_buckets = {
    '1-10¢': (0.01, 0.10),
    '10-20¢': (0.10, 0.20),
    '20-30¢': (0.20, 0.30),
    '30-40¢': (0.30, 0.40),
    '40-50¢': (0.40, 0.50),
    '50-60¢': (0.50, 0.60),
    '60-70¢': (0.60, 0.70),
    '70-80¢': (0.70, 0.80),
    '80-90¢': (0.80, 0.90),
    '90-99¢': (0.90, 0.99),
}

bucket_stats = {name: {'count': 0, 'total_vol': 0, 'vol_24hr': 0, 'examples': []} 
                for name in price_buckets}

MIN_VOLUME = 50000
MIN_24HR = 1000

for market in markets:
    try:
        outcomes_str = market.get("outcomes", "[]")
        prices_str = market.get("outcomePrices", "[]")
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
        
        volume = float(market.get("volume", 0))
        volume_24hr = float(market.get("volume24hr", 0))
        question = market.get("question", "")
        
        # Check filters
        if volume < MIN_VOLUME or volume_24hr < MIN_24HR:
            continue
        
        # Days to resolution
        end_date_str = market.get("endDate")
        days = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days = (end_date - datetime.now(timezone.utc)).days
            except:
                pass
        
        for i, price in enumerate(prices):
            price = float(price)
            outcome = outcomes[i] if i < len(outcomes) else "Unknown"
            
            # Find bucket
            for bucket_name, (min_p, max_p) in price_buckets.items():
                if min_p <= price < max_p:
                    bucket_stats[bucket_name]['count'] += 1
                    bucket_stats[bucket_name]['total_vol'] += volume
                    bucket_stats[bucket_name]['vol_24hr'] += volume_24hr
                    
                    if len(bucket_stats[bucket_name]['examples']) < 3:
                        bucket_stats[bucket_name]['examples'].append({
                            'question': question[:50],
                            'outcome': outcome,
                            'price': price,
                            'volume': volume,
                            'vol_24hr': volume_24hr,
                            'days': days
                        })
                    break
    except:
        continue

print(f"\n📊 ACTIVE MARKETS BY PRICE RANGE")
print(f"   (Min ${MIN_VOLUME:,} volume + ${MIN_24HR:,} 24hr volume)")
print("=" * 80)

for bucket_name in price_buckets:
    stats = bucket_stats[bucket_name]
    if stats['count'] > 0:
        avg_vol = stats['total_vol'] / stats['count']
        avg_24hr = stats['vol_24hr'] / stats['count']
        
        print(f"\n{bucket_name:>10}: {stats['count']:>3} opportunities")
        print(f"            Avg volume: ${avg_vol:>10,.0f} (24hr: ${avg_24hr:>8,.0f})")
        
        if stats['examples']:
            print(f"            Examples:")
            for ex in stats['examples'][:2]:
                days_str = f"{ex['days']}d" if ex['days'] is not None else "?"
                print(f"              • {ex['question']}... ({ex['outcome']}) @ {ex['price']*100:.1f}¢")
                print(f"                Vol: ${ex['volume']:,.0f} | {days_str} to resolution")

print("\n" + "=" * 80)
print("\n💡 KEY INSIGHTS:")

# Find most active range
most_active = max(bucket_stats.items(), key=lambda x: x[1]['count'])
print(f"\n   🔥 Most active: {most_active[0]} with {most_active[1]['count']} opportunities")

# Check our target range
our_range = bucket_stats['30-40¢']
print(f"\n   🎯 Our target (30-40¢): {our_range['count']} opportunities")
if our_range['count'] == 0:
    print(f"      ⚠️  This range is DEAD right now - consider pivoting")

# Suggest alternatives
alternatives = [(name, stats['count']) for name, stats in bucket_stats.items() 
                if stats['count'] >= 3 and name != '30-40¢']
if alternatives:
    print(f"\n   💡 Active alternatives:")
    for name, count in sorted(alternatives, key=lambda x: x[1], reverse=True)[:3]:
        print(f"      • {name}: {count} opportunities")
