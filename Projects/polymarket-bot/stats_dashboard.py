#!/usr/bin/env python3
"""
Real-time Stats Dashboard for Polymarket 5-Minute Bot
FIXED v2: Real orderbook prices + 10% fee calculation
"""
import requests
import json
import time
import os
from datetime import datetime
from collections import deque
from py_clob_client.client import ClobClient

# Configuration
REFRESH_INTERVAL = 5  # Refresh every 5 seconds
HISTORY_SIZE = 20  # Keep last 20 price checks
TAKER_FEE = 0.10  # 10% taker fee
MIN_NET_PROFIT = 0.05  # Target 5% NET profit after fees

class Dashboard:
    def __init__(self):
        self.opportunities = []
        self.price_history = deque(maxlen=HISTORY_SIZE)
        self.checks_count = 0
        self.start_time = time.time()
        self.current_market = None
        self.best_spread = {"profit": 0, "market": None, "timestamp": None}
        self.clob_client = ClobClient("https://clob.polymarket.com")
        
    def get_current_market_slug(self):
        current_time = int(time.time())
        interval_start = (current_time // 300) * 300
        return f"btc-updown-5m-{interval_start}"
    
    def get_prices(self, slug):
        try:
            # Get token IDs from gamma-api
            url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                return None, None, None
            
            data = resp.json()
            if not data:
                return None, None, None
            
            market = data[0] if isinstance(data, list) else data
            
            # Get token IDs
            token_ids = json.loads(market.get('clobTokenIds', '[]'))
            if len(token_ids) < 2:
                return None, None, None
            
            # Get REAL orderbook prices
            up_book = self.clob_client.get_order_book(token_ids[0])
            down_book = self.clob_client.get_order_book(token_ids[1])
            
            if not up_book.asks or not down_book.asks:
                return None, None, None
            
            # Best ask is LAST element (sorted high to low)
            up_price = float(up_book.asks[-1].price)
            down_price = float(down_book.asks[-1].price)
            volume = float(market.get('volume', 0))
            
            return up_price, down_price, volume
        except:
            return None, None, None
    
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def render(self):
        self.clear_screen()
        
        # Header
        print("━" * 80)
        print("🤖 POLYMARKET 5-MINUTE BOT - LIVE DASHBOARD (Fees Included)")
        print("━" * 80)
        print()
        
        # Runtime stats
        runtime = int(time.time() - self.start_time)
        hours = runtime // 3600
        minutes = (runtime % 3600) // 60
        seconds = runtime % 60
        
        print(f"⏱️  Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"📊 Price Checks: {self.checks_count}")
        print(f"🎯 Opportunities Found: {len(self.opportunities)}")
        print(f"✅ Using CLOB orderbook ASK prices (real executable)")
        print()
        
        # Current Market
        print("━" * 80)
        print("📍 CURRENT MARKET")
        print("━" * 80)
        
        if self.current_market:
            slug, up, down, volume = self.current_market
            total = up + down if (up and down) else 0
            # Calculate profit with 10% fee
            cost = up + down
            fee = cost * TAKER_FEE
            total_cost = cost + fee
            net_profit = 1.0 - total_cost
            profit = net_profit  # Use net profit for comparisons if total > 0 else 0
            
            print(f"Market: {slug}")
            print(f"UP ask:     ${up:.4f}" if up else "UP ask:   N/A")
            print(f"DOWN ask:   ${down:.4f}" if down else "DOWN ask: N/A")
            print(f"Total Cost: ${total:.4f}" if total > 0 else "Total Cost: N/A")
            
            if total > 0:
                if profit >= MIN_NET_PROFIT:
                    print(f"💰 PROFIT: ${profit:.4f} ({profit*100:.2f}%) ⚡ OPPORTUNITY!")
                elif profit > 0:
                    print(f"Profit: ${profit:.4f} ({profit*100:.2f}%) - Below 5% threshold")
                else:
                    print(f"Profit: ${profit:.4f} ({profit*100:.2f}%) - No arbitrage")
            
            if volume:
                print(f"Volume: ${volume:,.2f}")
        else:
            print("Waiting for data...")
        
        print()
        
        # Best Spread Today
        if self.best_spread["profit"] > 0:
            print("━" * 80)
            print("🏆 BEST SPREAD TODAY")
            print("━" * 80)
            print(f"Profit: {self.best_spread['profit']*100:.2f}%")
            print(f"Market: {self.best_spread['market']}")
            print(f"Time: {self.best_spread['timestamp']}")
            print()
        
        # Recent Opportunities
        if self.opportunities:
            print("━" * 80)
            print("🎯 RECENT OPPORTUNITIES (Last 10)")
            print("━" * 80)
            for opp in self.opportunities[-10:]:
                print(f"[{opp['time']}] {opp['profit']*100:.2f}% profit - {opp['market']}")
            print()
        
        # Price History Chart
        if len(self.price_history) > 5:
            print("━" * 80)
            print("📈 PROFIT TREND (Last 10 checks)")
            print("━" * 80)
            
            for entry in list(self.price_history)[-10:]:
                profit = entry['profit']
                bars = int(abs(profit) * 200)
                
                if profit >= MIN_NET_PROFIT:
                    bar = "█" * min(bars, 60)
                    print(f"{entry['time']} | {profit*100:+6.2f}% | {bar} ⚡")
                elif profit > 0:
                    bar = "▓" * min(bars, 60)
                    print(f"{entry['time']} | {profit*100:+6.2f}% | {bar}")
                else:
                    bar = "░" * min(bars, 60)
                    print(f"{entry['time']} | {profit*100:+6.2f}% | {bar}")
            print()
        
        print("━" * 80)
        print("Press Ctrl+C to exit | Note: Negative profit = No arbitrage right now")
        print("━" * 80)
    
    def update(self):
        slug = self.get_current_market_slug()
        up, down, volume = self.get_prices(slug)
        
        self.checks_count += 1
        self.current_market = (slug, up, down, volume)
        
        if up and down:
            total = up + down
            # Calculate profit with 10% fee
            cost = up + down
            fee = cost * TAKER_FEE
            total_cost = cost + fee
            net_profit = 1.0 - total_cost
            profit = net_profit  # Use net profit for comparisons
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Add to history
            self.price_history.append({
                "time": timestamp,
                "profit": profit,
                "up": up,
                "down": down
            })
            
            # Check for opportunity
            if profit >= MIN_NET_PROFIT:
                self.opportunities.append({
                    "time": timestamp,
                    "profit": profit,
                    "market": slug,
                    "up": up,
                    "down": down
                })
                
                # Update best spread
                if profit > self.best_spread["profit"]:
                    self.best_spread = {
                        "profit": profit,
                        "market": slug,
                        "timestamp": timestamp
                    }
    
    def run(self):
        try:
            while True:
                self.update()
                self.render()
                time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard closed")
            print(f"📊 Final Stats:")
            print(f"   Total Checks: {self.checks_count}")
            print(f"   Opportunities: {len(self.opportunities)}")
            if self.best_spread["profit"] > 0:
                print(f"   Best Spread: {self.best_spread['profit']*100:.2f}%")

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
