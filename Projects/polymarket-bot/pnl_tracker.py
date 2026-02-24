#!/usr/local/bin/python3
"""
Real-time P&L tracker for longshot positions
Fetches current prices and calculates unrealized gains/losses
"""
import requests
import json
import time
from datetime import datetime

LOG_FILE = "/dev/shm/longshot_bot.log"

def parse_positions():
    """Extract positions from bot log"""
    positions = {}

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]

        if "PAPER TRADE: Buy" in line:
            try:
                # Parse shares and outcome from trade line
                # Format: "📝 PAPER TRADE: Buy 10000.0 shares of 'Yes'"
                shares_str = line.split("Buy ")[1].split(" shares")[0]
                shares = float(shares_str)
                outcome = line.split("of '")[1].split("'")[0]

                # Next lines have market, price, cost, potential, URL
                market_line = lines[i+1] if i+1 < len(lines) else ""
                price_line = lines[i+2] if i+2 < len(lines) else ""
                url_line = lines[i+5] if i+5 < len(lines) else ""

                market_name = market_line.split("Market: ")[1].strip() if "Market:" in market_line else "Unknown"
                buy_price_str = price_line.split("$")[1].split()[0] if "$" in price_line else "0"
                buy_price = float(buy_price_str)
                slug = url_line.split("event/")[1].strip() if "event/" in url_line else ""

                # Use slug+outcome as key to dedupe
                key = f"{slug}_{outcome}"

                if key and key not in positions:
                    positions[key] = {
                        'market': market_name,
                        'outcome': outcome,
                        'slug': slug,
                        'shares': shares,
                        'buy_price': buy_price,
                        'cost': shares * buy_price
                    }
            except Exception as e:
                pass

        i += 1

    return positions

def get_current_price(slug):
    """Fetch current market prices from Polymarket"""
    try:
        resp = requests.get(
            f"https://gamma-api.polymarket.com/markets/{slug}",
            timeout=5
        )
        
        if resp.status_code == 200:
            market = resp.json()
            
            # Get outcomes and prices
            outcomes_str = market.get('outcomes', '[]')
            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
            
            prices_str = market.get('outcomePrices', '[]')
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
            
            # Return dict of outcome -> price
            return dict(zip(outcomes, [float(p) for p in prices]))
        
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
    
    return {}

def main():
    print("=" * 80)
    print("💰 LONGSHOT BOT - P&L TRACKER")
    print("=" * 80)
    print()
    
    # Parse positions from log
    print("📊 Loading positions from log...")
    positions = parse_positions()
    
    if not positions:
        print("❌ No positions found!")
        return
    
    print(f"✅ Found {len(positions)} positions\n")
    time.sleep(1)
    
    # Fetch current prices
    print("🔍 Fetching current prices...\n")
    
    total_cost = 0
    total_value = 0
    winners = []
    losers = []
    flat = []
    
    for key, pos in positions.items():
        slug = pos['slug']
        outcome = pos['outcome']
        
        # Get current price
        prices = get_current_price(slug)
        current_price = prices.get(outcome, pos['buy_price'])
        
        # Calculate P&L
        cost = pos['cost']
        current_value = pos['shares'] * current_price
        pnl = current_value - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        
        total_cost += cost
        total_value += current_value
        
        # Display
        pnl_color = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        
        print(f"{pnl_color} {outcome} - {pos['market'][:50]}")
        print(f"   Buy: ${pos['buy_price']:.4f} → Now: ${current_price:.4f}")
        print(f"   Shares: {pos['shares']:.0f} | Cost: ${cost:.2f} → Value: ${current_value:.2f}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
        print()
        
        # Categorize
        if pnl > 0.5:
            winners.append((pos['market'][:40], pnl, pnl_pct))
        elif pnl < -0.5:
            losers.append((pos['market'][:40], pnl, pnl_pct))
        else:
            flat.append(pos['market'][:40])
        
        time.sleep(0.5)  # Rate limit
    
    # Summary
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    
    print("=" * 80)
    print("📈 PORTFOLIO SUMMARY")
    print("=" * 80)
    print(f"Total Cost:      ${total_cost:.2f}")
    print(f"Current Value:   ${total_value:.2f}")
    
    pnl_symbol = "🟢" if total_pnl >= 0 else "🔴"
    print(f"Unrealized P&L:  {pnl_symbol} ${total_pnl:+.2f} ({total_pnl_pct:+.1f}%)")
    print()
    print(f"Winners: {len(winners)} | Losers: {len(losers)} | Flat: {len(flat)}")
    
    if winners:
        print("\n🏆 TOP GAINERS:")
        for market, pnl, pct in sorted(winners, key=lambda x: x[1], reverse=True)[:3]:
            print(f"  • {market}: ${pnl:+.2f} ({pct:+.1f}%)")
    
    if losers:
        print("\n📉 BIGGEST LOSERS:")
        for market, pnl, pct in sorted(losers, key=lambda x: x[1])[:3]:
            print(f"  • {market}: ${pnl:+.2f} ({pct:+.1f}%)")

if __name__ == "__main__":
    main()
