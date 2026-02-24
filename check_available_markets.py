#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

# Our filter criteria
PRICE_MIN = 0.30
PRICE_MAX = 0.40
MAX_DAYS_TO_RESOLUTION = 14
MIN_VOLUME_24HR = 5000
MIN_VOLUME = 50000

print("🔍 Checking Polymarket for markets matching TIER 1 filters...")
print(f"   Price range: {PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}¢")
print(f"   Max days to resolution: {MAX_DAYS_TO_RESOLUTION}")
print(f"   Min 24hr volume: ${MIN_VOLUME_24HR:,}")
print(f"   Min total volume: ${MIN_VOLUME:,}")
print("=" * 80)

# Fetch markets
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        markets = json.loads(response.read().decode())
except Exception as e:
    print(f"❌ Error fetching markets: {e}")
    exit(1)

print(f"📊 Fetched {len(markets)} total active markets\n")

# Filter markets
matches = []
stats = {
    'total': len(markets),
    'failed_price': 0,
    'failed_days': 0,
    'failed_24hr_vol': 0,
    'failed_total_vol': 0,
    'failed_outcomes': 0
}

for market in markets:
    try:
        question = market.get("question", "")
        
        # Check days to resolution
        end_date_str = market.get("endDate")
        days_to_resolution = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days_to_resolution = (end_date - datetime.now(timezone.utc)).days
                if days_to_resolution > MAX_DAYS_TO_RESOLUTION:
                    stats['failed_days'] += 1
                    continue
            except:
                pass
        
        # Parse outcomes and prices
        outcomes_str = market.get("outcomes", "[]")
        prices_str = market.get("outcomePrices", "[]")
        
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
        
        volume = float(market.get("volume", 0))
        volume_24hr = float(market.get("volume24hr", 0))
        
        # Check volumes
        if volume_24hr < MIN_VOLUME_24HR:
            stats['failed_24hr_vol'] += 1
            continue
            
        if volume < MIN_VOLUME:
            stats['failed_total_vol'] += 1
            continue
        
        # Check outcomes
        if not outcomes or len(outcomes) < 2:
            stats['failed_outcomes'] += 1
            continue
        
        # Check prices
        found_match = False
        for i, outcome_name in enumerate(outcomes):
            if i >= len(prices):
                continue
            price = float(prices[i])
            if PRICE_MIN <= price <= PRICE_MAX:
                matches.append({
                    'question': question,
                    'outcome': outcome_name,
                    'price': price,
                    'volume': volume,
                    'volume_24hr': volume_24hr,
                    'days_to_resolution': days_to_resolution
                })
                found_match = True
                break
        
        if not found_match:
            stats['failed_price'] += 1
            
    except Exception as e:
        continue

print(f"📈 RESULTS:")
print(f"   ✅ Markets matching ALL filters: {len(matches)}")
print(f"\n📉 FILTER BREAKDOWN:")
print(f"   ❌ Failed price range (30-40¢): {stats['failed_price']}")
print(f"   ❌ Failed days to resolution (>{MAX_DAYS_TO_RESOLUTION}d): {stats['failed_days']}")
print(f"   ❌ Failed 24hr volume (<${MIN_VOLUME_24HR:,}): {stats['failed_24hr_vol']}")
print(f"   ❌ Failed total volume (<${MIN_VOLUME:,}): {stats['failed_total_vol']}")
print(f"   ❌ Failed outcomes check: {stats['failed_outcomes']}")

if matches:
    print(f"\n✅ MATCHING OPPORTUNITIES ({len(matches)}):")
    print("=" * 80)
    for m in matches[:10]:  # Show first 10
        days_str = f"{m['days_to_resolution']}d" if m['days_to_resolution'] else "?"
        print(f"\n📊 {m['question'][:70]}")
        print(f"   Outcome: {m['outcome']}")
        print(f"   Price: {m['price']*100:.1f}¢")
        print(f"   Volume: ${m['volume']:,.0f} (24hr: ${m['volume_24hr']:,.0f})")
        print(f"   Resolves in: {days_str}")
    
    if len(matches) > 10:
        print(f"\n   ... and {len(matches) - 10} more")
else:
    print(f"\n⚠️  NO MARKETS CURRENTLY MATCH ALL FILTERS")
    print("\nThis means:")
    print("  • Filters may be too strict for current market conditions")
    print("  • May need to adjust thresholds (days, volume, or price range)")
    print("  • Or wait for more active markets to appear")
