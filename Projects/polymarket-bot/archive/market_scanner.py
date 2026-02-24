#!/usr/bin/env python3
"""
Polymarket Market Scanner - Find REAL Opportunities
Scans all active markets for inefficiencies
"""
import requests
import json
import time
from datetime import datetime

def scan_all_markets():
    """Scan all active Polymarket markets"""
    print("🔍 Scanning Polymarket markets...")
    
    resp = requests.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=100")
    markets = resp.json()
    
    print(f"Found {len(markets)} active markets\n")
    return markets

def analyze_market(market):
    """Analyze a single market for opportunities"""
    try:
        # Get basic data
        question = market.get('question', 'Unknown')
        slug = market.get('slug', '')
        volume = float(market.get('volume', 0))
        liquidity = float(market.get('liquidityNum', 0))
        
        # Get prices
        prices_str = market.get('outcomePrices', '[]')
        prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
        
        if len(prices) != 2:
            return None
        
        p1 = float(prices[0])
        p2 = float(prices[1])
        
        # Check for inefficiencies
        total = p1 + p2
        spread = abs(1.0 - total)
        
        # Get outcomes
        outcomes_str = market.get('outcomes', '[]')
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        
        fee = market.get('takerBaseFee', 0) / 100
        
        return {
            'question': question,
            'slug': slug,
            'volume': volume,
            'liquidity': liquidity,
            'outcomes': outcomes,
            'prices': [p1, p2],
            'total': total,
            'spread': spread,
            'fee': fee
        }
    except Exception as e:
        return None

def find_opportunities(markets):
    """Find trading opportunities"""
    opportunities = []
    
    for market in markets:
        analysis = analyze_market(market)
        if not analysis:
            continue
        
        # Criteria for opportunities:
        # 1. High volume (active market)
        # 2. Spread > 2% (mispricing)
        # 3. Decent liquidity
        
        if analysis['volume'] > 10000 and analysis['spread'] > 0.02 and analysis['liquidity'] > 1000:
            opportunities.append(analysis)
    
    return opportunities

def check_5min_alternatives():
    """Check if 5-min markets ever have opportunities"""
    print("\n🔍 Checking 5-minute markets...")
    
    current_time = int(time.time())
    market_time = (current_time // 300) * 300
    
    slugs_to_check = [
        f"btc-updown-5m-{market_time}",
        f"eth-updown-5m-{market_time}",
    ]
    
    for slug in slugs_to_check:
        try:
            resp = requests.get(f"https://gamma-api.polymarket.com/markets?slug={slug}")
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    market = data[0]
                    print(f"\n{slug}:")
                    print(f"  Volume: ${float(market.get('volume', 0)):,.2f}")
                    print(f"  Fee: {market.get('takerBaseFee', 0)/100:.1f}%")
                    
                    prices_str = market.get('outcomePrices', '[]')
                    prices = json.loads(prices_str)
                    if len(prices) == 2:
                        total = float(prices[0]) + float(prices[1])
                        print(f"  Prices: {prices[0]} + {prices[1]} = {total:.4f}")
                        print(f"  Spread: {abs(1.0 - total)*100:.2f}%")
        except:
            continue

def main():
    print("=" * 80)
    print("POLYMARKET MARKET SCANNER")
    print("=" * 80)
    print()
    
    # Scan all markets
    markets = scan_all_markets()
    
    # Find opportunities
    opportunities = find_opportunities(markets)
    
    if opportunities:
        print(f"\n✅ Found {len(opportunities)} potential opportunities:\n")
        
        for i, opp in enumerate(sorted(opportunities, key=lambda x: x['spread'], reverse=True)[:10], 1):
            print(f"{i}. {opp['question'][:70]}")
            print(f"   Spread: {opp['spread']*100:.2f}% | Vol: ${opp['volume']:,.0f} | Fee: {opp['fee']:.1f}%")
            print(f"   Prices: {opp['prices'][0]:.3f} ({opp['outcomes'][0]}) + {opp['prices'][1]:.3f} ({opp['outcomes'][1]})")
            print(f"   URL: https://polymarket.com/event/{opp['slug']}")
            print()
    else:
        print("\n❌ No opportunities found with current criteria")
        print("   (Volume > $10K, Spread > 2%, Liquidity > $1K)")
    
    # Check 5-min markets
    check_5min_alternatives()
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print()
    print("1. Main markets have 0% fees but are very efficient")
    print("2. 5-min markets have 10% fees and are also efficient")
    print("3. Best strategy: Manual research on specific events")
    print("4. Alternative: News-based trading (be first on breaking news)")
    print()
    print("For $100 budget:")
    print("  - Pick 1-2 events you have edge on")
    print("  - Research thoroughly")
    print("  - Place directional bets")
    print("  - Not arbitrage, but informed speculation")

if __name__ == "__main__":
    main()
