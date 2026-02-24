#!/usr/local/bin/python3
"""
Scan for cheap markets with actual price movement (volatility)
This finds longshots that are ALIVE, not dead markets waiting to close
"""
import requests
import json
import time
from datetime import datetime, timedelta

def get_market_history(condition_id):
    """Fetch recent price history for a market outcome"""
    try:
        # Get last 24h of price data
        end_time = int(time.time())
        start_time = end_time - (24 * 3600)  # 24 hours ago
        
        resp = requests.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": condition_id,
                "startTs": start_time,
                "endTs": end_time,
                "interval": "1h"  # Hourly data points
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            # Data format: {"history": [{"t": timestamp, "p": price}, ...]}
            return data.get('history', [])
        
    except Exception as e:
        pass
    
    return []

def calculate_volatility(price_history):
    """Calculate price volatility from history"""
    if len(price_history) < 2:
        return 0
    
    prices = [float(h['p']) for h in price_history if 'p' in h]
    
    if len(prices) < 2:
        return 0
    
    # Calculate standard deviation of prices
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    std_dev = variance ** 0.5
    
    # Also get price range (high - low)
    price_range = max(prices) - min(prices)
    
    return {
        'std_dev': std_dev,
        'range': price_range,
        'min': min(prices),
        'max': max(prices),
        'current': prices[-1] if prices else 0,
        'data_points': len(prices)
    }

def scan_for_volatile_longshots():
    """Find cheap markets that are actually moving"""
    print("=" * 80)
    print("🔍 VOLATILE LONGSHOT SCANNER")
    print("=" * 80)
    print("Looking for sub-5¢ markets with recent price movement...\n")
    
    # Get active markets
    resp = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={
            "active": "true",
            "closed": "false",
            "limit": 200
        },
        timeout=10
    )
    
    if resp.status_code != 200:
        print(f"❌ API Error: {resp.status_code}")
        return
    
    markets = resp.json()
    print(f"✅ Fetched {len(markets)} active markets\n")
    
    volatile_longshots = []
    checked = 0
    
    for market in markets:
        try:
            # Parse market data
            question = market.get('question', '')
            slug = market.get('slug', '')
            volume = float(market.get('volume', 0))
            
            # Skip low volume
            if volume < 100:
                continue
            
            # Get outcomes and prices
            outcomes = json.loads(market.get('outcomes', '[]'))
            prices = json.loads(market.get('outcomePrices', '[]'))
            tokens = json.loads(market.get('clobTokenIds', '[]'))
            
            # Check end date - skip if resolving soon
            end_date_str = market.get('endDate', '')
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days_until_end = (end_date - datetime.now(end_date.tzinfo)).days
                    
                    # Skip markets ending in < 14 days
                    if days_until_end < 14:
                        continue
                except:
                    pass
            
            # Check each outcome
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                
                # Only check longshots (< 5¢)
                if price >= 0.05 or price <= 0:
                    continue
                
                checked += 1
                
                # Get token ID for price history
                token_id = tokens[i] if i < len(tokens) else None
                
                if not token_id:
                    continue
                
                # Fetch price history
                history = get_market_history(token_id)
                
                if not history:
                    continue
                
                # Calculate volatility
                vol = calculate_volatility(history)
                
                # Filter for ACTUAL movement
                # We want: std dev > 0.001 OR range > 0.005 (price moved at least 0.5¢)
                if vol['std_dev'] > 0.001 or vol['range'] > 0.005:
                    volatile_longshots.append({
                        'question': question,
                        'slug': slug,
                        'outcome': outcome,
                        'price': price,
                        'volume': volume,
                        'token_id': token_id,
                        'volatility': vol,
                        'end_date': end_date_str
                    })
                
                # Rate limit
                time.sleep(0.2)
                
                # Show progress
                if checked % 10 == 0:
                    print(f"   Checked {checked} longshots... Found {len(volatile_longshots)} volatile ones")
        
        except Exception as e:
            continue
    
    print(f"\n{'=' * 80}")
    print(f"📈 RESULTS: Found {len(volatile_longshots)} volatile longshots")
    print(f"{'=' * 80}\n")
    
    # Sort by volatility (range)
    volatile_longshots.sort(key=lambda x: x['volatility']['range'], reverse=True)
    
    # Display top 20
    for i, opp in enumerate(volatile_longshots[:20], 1):
        vol = opp['volatility']
        
        print(f"{i}. {opp['price']*100:.2f}¢ - {opp['outcome']}")
        print(f"   {opp['question'][:70]}")
        print(f"   📊 24h Range: {vol['min']*100:.2f}¢ → {vol['max']*100:.2f}¢ (Δ{vol['range']*100:.2f}¢)")
        print(f"   📈 Volatility: {vol['std_dev']*100:.3f}¢ std dev | {vol['data_points']} data points")
        print(f"   💰 Volume: ${opp['volume']:,.0f}")
        print(f"   📅 Ends: {opp['end_date'][:10]}")
        print(f"   🔗 https://polymarket.com/event/{opp['slug']}")
        print()
    
    return volatile_longshots

if __name__ == "__main__":
    results = scan_for_volatile_longshots()
