#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

PRICE_MIN = 0.30
PRICE_MAX = 0.40
MIN_VOLUME = 50000

# Fetch markets once
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

def test_filters(max_days, min_24hr_vol):
    """Test how many markets match with given thresholds"""
    matches = 0
    for market in markets:
        try:
            # Check days to resolution
            end_date_str = market.get("endDate")
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (end_date - datetime.now(timezone.utc)).days
                    if days_to_resolution > max_days:
                        continue
                except:
                    pass
            
            # Parse data
            outcomes_str = market.get("outcomes", "[]")
            prices_str = market.get("outcomePrices", "[]")
            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
            
            volume = float(market.get("volume", 0))
            volume_24hr = float(market.get("volume24hr", 0))
            
            # Check filters
            if volume_24hr < min_24hr_vol:
                continue
            if volume < MIN_VOLUME:
                continue
            if not outcomes or len(outcomes) < 2:
                continue
            
            # Check price range
            for i, price in enumerate(prices):
                price = float(price)
                if PRICE_MIN <= price <= PRICE_MAX:
                    matches += 1
                    break
                    
        except:
            continue
    
    return matches

print("🧪 TESTING DIFFERENT FILTER COMBINATIONS")
print("=" * 80)

# Test matrix
days_options = [7, 14, 30, 60]
vol_options = [1000, 2500, 5000, 10000]

print(f"\n{'Days':<8} | ", end="")
for vol in vol_options:
    print(f"${vol:>6,} 24hr vol", end=" | ")
print()
print("-" * 80)

for days in days_options:
    print(f"{days:>3}d    | ", end="")
    for vol in vol_options:
        count = test_filters(days, vol)
        emoji = "✅" if count > 0 else "❌"
        print(f"   {emoji} {count:>2} opps   ", end=" | ")
    print()

print("\n" + "=" * 80)
print("\n💡 RECOMMENDATIONS:")

# Find sweet spot
best = None
for days in [30, 21, 14]:
    for vol in [1000, 2500, 5000]:
        count = test_filters(days, vol)
        if count >= 3:  # Want at least 3 opportunities
            if best is None or (days < best[0]):  # Prefer shorter days
                best = (days, vol, count)

if best:
    print(f"\n🎯 OPTIMAL: {best[0]} days + ${best[1]:,} 24hr volume")
    print(f"   → Gives {best[2]} opportunities")
    print(f"   → Balances liquidity safety with opportunity flow")
else:
    print(f"\n⚠️  May need to:")
    print(f"   • Wait for more active markets")
    print(f"   • Consider different price range (45-55¢ or 60-80¢)")
    print(f"   • Lower volume requirements temporarily")
