#!/usr/bin/env python3
"""
Polymarket 5-Minute Market Bot - HYBRID APPROACH
- Scrapes HTML to get condition_id
- Polls gamma-api for orderbook prices
- No WebSocket complexity needed
"""
import requests
import json
import time
import re
from datetime import datetime
from py_clob_client.client import ClobClient

# Configuration
CHECK_INTERVAL = 10  # Check prices every 10 seconds
MIN_SPREAD_PROFIT = 0.05  # 5% minimum profit (UP + DOWN < 0.95)

def get_current_market_slug():
    """Get the slug for the current 5-minute market"""
    current_time = int(time.time())
    interval_start = (current_time // 300) * 300  # Round down to 5-min interval
    return f"btc-updown-5m-{interval_start}"

def extract_condition_id(slug):
    """Extract condition_id from market HTML"""
    try:
        url = f"https://polymarket.com/event/{slug}"
        resp = requests.get(url, timeout=5)

        if resp.status_code != 200:
            return None

        # Find condition_id in HTML
        matches = re.findall(r'"conditionId"\s*:\s*"(0x[a-fA-F0-9]+)"', resp.text)
        if matches:
            return matches[0]  # Return first match
        return None
    except Exception as e:
        print(f"❌ Error extracting condition_id: {e}")
        return None

def get_prices_from_gamma(slug):
    """Get current prices from gamma-api using market slug"""
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
        resp = requests.get(url, timeout=5)

        if resp.status_code != 200:
            return None, None

        data = resp.json()
        if not data:
            return None, None

        market = data[0] if isinstance(data, list) else data

        # Get outcome prices - they're stored as JSON string
        outcome_prices_str = market.get('outcomePrices', '[]')
        outcome_prices = json.loads(outcome_prices_str)

        if len(outcome_prices) < 2:
            return None, None

        # Prices are in order: ["Up", "Down"] or ["Yes", "No"]
        # For BTC markets: 0=Up, 1=Down
        up_price = float(outcome_prices[0])
        down_price = float(outcome_prices[1])

        return up_price, down_price

    except Exception as e:
        print(f"❌ Error getting prices: {e}")
        return None, None

def check_arbitrage(up_price, down_price):
    """Check if there's a profitable arbitrage opportunity"""
    if up_price is None or down_price is None:
        return False, 0

    total_cost = up_price + down_price
    profit = 1.0 - total_cost  # Payout is always $1.00

    return profit >= MIN_SPREAD_PROFIT, profit

def main():
    print("🚀 Starting 5-Minute Market Bot (HYBRID)")
    print(f"⏱️  Check interval: {CHECK_INTERVAL}s")
    print(f"💰 Min profit threshold: {MIN_SPREAD_PROFIT*100}%")
    print("-" * 60)

    current_slug = None
    condition_id = None

    while True:
        try:
            # Check if we need to switch to a new market
            new_slug = get_current_market_slug()

            if new_slug != current_slug:
                print(f"\n🔄 New market detected: {new_slug}")
                current_slug = new_slug

                # Extract condition_id from HTML
                print(f"🔍 Extracting condition_id...")
                condition_id = extract_condition_id(current_slug)

                if condition_id:
                    print(f"✅ Found condition_id: {condition_id[:20]}...")
                else:
                    print(f"⚠️  Could not extract condition_id, will retry")
                    time.sleep(CHECK_INTERVAL)
                    continue

            # Get current prices
            up_price, down_price = get_prices_from_gamma(current_slug)

            if up_price is None or down_price is None:
                print(f"⚠️  No price data available yet")
                time.sleep(CHECK_INTERVAL)
                continue

            # Check for arbitrage
            is_profitable, profit = check_arbitrage(up_price, down_price)

            timestamp = datetime.now().strftime("%H:%M:%S")

            if is_profitable:
                print(f"\n🎯 [{timestamp}] ARBITRAGE OPPORTUNITY!")
                print(f"   UP: ${up_price:.4f} | DOWN: ${down_price:.4f}")
                print(f"   Total: ${up_price + down_price:.4f}")
                print(f"   💰 PROFIT: ${profit:.4f} ({profit*100:.2f}%)")
                print(f"   📊 Market: {current_slug}")
            else:
                # Just show current prices (no spam)
                print(f"[{timestamp}] UP: ${up_price:.4f} | DOWN: ${down_price:.4f} | Sum: ${up_price + down_price:.4f} | Profit: {profit*100:+.2f}%", end='\r')

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down bot...")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
