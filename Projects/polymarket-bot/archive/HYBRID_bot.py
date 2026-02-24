#!/usr/bin/env python3
"""
Polymarket 5-Minute Market Bot - FIXED VERSION v2
Uses REAL orderbook ask prices + accounts for 10% taker fees
"""
import requests
import json
import time
import re
from datetime import datetime
from py_clob_client.client import ClobClient

# Configuration
CHECK_INTERVAL = 10  # Check prices every 10 seconds
TAKER_FEE = 0.10  # 10% taker fee (1000 bps)
MIN_NET_PROFIT = 0.05  # Target 5% NET profit after fees
MIN_ORDER_SIZE = 5  # Minimum shares required

# Calculate required spread for target net profit
# Formula: (1 - net_profit) / (1 + fee) = max_cost
# For 5% net profit with 10% fee: (1 - 0.05) / 1.10 = 0.8636
# So spread must be: 1 - 0.8636 = 0.1364 (13.64%)
MIN_SPREAD_PROFIT = (1 - MIN_NET_PROFIT) / (1 + TAKER_FEE)
MIN_SPREAD_PROFIT = 1 - MIN_SPREAD_PROFIT  # Convert to spread

# Initialize CLOB client
clob_client = ClobClient("https://clob.polymarket.com")

def get_current_market_slug():
    """Get the slug for the current 5-minute market"""
    current_time = int(time.time())
    interval_start = (current_time // 300) * 300  # Round down to 5-min interval
    return f"btc-updown-5m-{interval_start}"

def get_token_ids(slug):
    """Get token IDs for a market from gamma-api"""
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
        resp = requests.get(url, timeout=5)

        if resp.status_code != 200:
            return None, None

        data = resp.json()
        if not data:
            return None, None

        market = data[0] if isinstance(data, list) else data

        # Get token IDs from clobTokenIds field
        token_ids_str = market.get('clobTokenIds', '[]')
        token_ids = json.loads(token_ids_str)

        if len(token_ids) < 2:
            return None, None

        # token_ids[0] = UP, token_ids[1] = DOWN
        return token_ids[0], token_ids[1]

    except Exception as e:
        print(f"❌ Error getting token IDs: {e}")
        return None, None

def get_real_prices(up_token_id, down_token_id):
    """Get REAL executable prices from CLOB orderbook asks"""
    try:
        # Get orderbooks for both tokens
        up_book = clob_client.get_order_book(up_token_id)
        down_book = clob_client.get_order_book(down_token_id)

        # Check if orderbooks have asks
        if not up_book.asks or not down_book.asks:
            return None, None

        # Asks are sorted high to low - LAST element is best (lowest) price
        best_up_ask = float(up_book.asks[-1].price)
        best_down_ask = float(down_book.asks[-1].price)

        return best_up_ask, best_down_ask

    except Exception as e:
        print(f"❌ Error getting orderbook prices: {e}")
        return None, None

def check_arbitrage(up_price, down_price):
    """Check if there's a profitable arbitrage opportunity (accounting for fees)"""
    if up_price is None or down_price is None:
        return False, 0, 0, 0

    # Calculate cost before fees
    cost_before_fee = up_price + down_price

    # Calculate 10% taker fee
    fee_amount = cost_before_fee * TAKER_FEE

    # Total cost including fees
    total_cost = cost_before_fee + fee_amount

    # Net profit after fees
    net_profit = 1.0 - total_cost

    # Gross profit before fees (for display)
    gross_profit = 1.0 - cost_before_fee

    # Is it profitable after fees?
    is_profitable = net_profit >= MIN_NET_PROFIT

    return is_profitable, gross_profit, fee_amount, net_profit

def main():
    print("🚀 Starting 5-Minute Market Bot (FIXED v2 - Fees Included)")
    print(f"⏱️  Check interval: {CHECK_INTERVAL}s")
    print(f"💰 Target NET profit: {MIN_NET_PROFIT*100}%")
    print(f"📊 Taker fee: {TAKER_FEE*100}%")
    print(f"🎯 Required spread: ≥{MIN_SPREAD_PROFIT*100:.1f}% (to achieve {MIN_NET_PROFIT*100}% after fees)")
    print(f"💵 Min order size: {MIN_ORDER_SIZE} shares")
    print("✅ Using CLOB orderbook ASK prices (real executable)")
    print("-" * 60)

    current_slug = None
    up_token_id = None
    down_token_id = None

    while True:
        try:
            # Check if we need to switch to a new market
            new_slug = get_current_market_slug()

            if new_slug != current_slug:
                print(f"\n🔄 New market detected: {new_slug}")
                current_slug = new_slug

                # Get token IDs for this market
                print(f"🔍 Fetching token IDs...")
                up_token_id, down_token_id = get_token_ids(current_slug)

                if up_token_id and down_token_id:
                    print(f"✅ Found token IDs")
                    print(f"   UP:   {up_token_id[:20]}...")
                    print(f"   DOWN: {down_token_id[:20]}...")
                else:
                    print(f"⚠️  Could not get token IDs, will retry")
                    time.sleep(CHECK_INTERVAL)
                    continue

            # Get REAL prices from orderbook
            up_price, down_price = get_real_prices(up_token_id, down_token_id)

            if up_price is None or down_price is None:
                print(f"⚠️  No orderbook data available yet")
                time.sleep(CHECK_INTERVAL)
                continue

            # Check for arbitrage
            is_profitable, gross_profit, fee_amount, net_profit = check_arbitrage(up_price, down_price)

            timestamp = datetime.now().strftime("%H:%M:%S")

            if is_profitable:
                cost = up_price + down_price
                min_capital = cost * MIN_ORDER_SIZE

                print(f"\n🎯 [{timestamp}] ARBITRAGE OPPORTUNITY!")
                print(f"   UP ask:   ${up_price:.4f}")
                print(f"   DOWN ask: ${down_price:.4f}")
                print(f"   ─────────────────────────")
                print(f"   Cost:     ${cost:.4f}")
                print(f"   Fee (10%): ${fee_amount:.4f}")
                print(f"   Total:    ${cost + fee_amount:.4f}")
                print(f"   Payout:   $1.0000")
                print(f"   ─────────────────────────")
                print(f"   💰 NET PROFIT: ${net_profit:.4f} ({net_profit*100:.2f}%)")
                print(f"   💵 Min capital needed: ${min_capital:.2f} ({MIN_ORDER_SIZE} shares)")
                print(f"   📊 Market: {current_slug}")
            else:
                # Just show current prices (no spam)
                total = up_price + down_price
                print(f"[{timestamp}] UP: ${up_price:.4f} | DOWN: ${down_price:.4f} | Sum: ${total:.4f} | Net: {net_profit*100:+.2f}% (after fee)", end='\r')

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down bot...")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
