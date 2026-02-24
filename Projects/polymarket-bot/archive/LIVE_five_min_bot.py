#!/usr/bin/env python3
"""
WORKING 5-Minute Market Bot - FINDS LIVE MARKETS
"""

import asyncio
import time
from datetime import datetime, timezone, timedelta
from py_clob_client.client import ClobClient
import requests

class LiveFiveMinBot:
    def __init__(self):
        self.client = ClobClient('https://clob.polymarket.com')
        self.paper_balance = 100.0
        self.trades = []
        
        print("="*70)
        print("🔥 LIVE 5-MINUTE MARKET BOT")
        print("="*70)
        print(f"💰 Starting balance: ${self.paper_balance:.2f}")
        print("="*70)
        print()
    
    def get_live_markets(self):
        """Get currently active 5-min markets"""
        now = datetime.now(timezone.utc)
        et_now = now - timedelta(hours=5)
        
        # Round to nearest 5-min
        current_min = (et_now.minute // 5) * 5
        market_time = et_now.replace(minute=current_min, second=0, microsecond=0)
        
        # Check current + next 2 intervals (15 min window)
        markets = []
        for offset in [0, 5, 10]:
            t = market_time + timedelta(minutes=offset)
            ts = int((t + timedelta(hours=5)).timestamp())
            slug = f"btc-updown-5m-{ts}"
            url = f"https://polymarket.com/event/{slug}"
            
            try:
                resp = requests.get(url, timeout=3, allow_redirects=False)
                if resp.status_code == 200:
                    markets.append({
                        'slug': slug,
                        'timestamp': ts,
                        'time_et': t.strftime('%I:%M %p ET'),
                        'url': url
                    })
            except:
                pass
        
        return markets
    
    def get_market_data(self, market):
        """Get orderbook data for a market"""
        try:
            # Extract market from Polymarket API
            resp = requests.get(f"https://gamma-api.polymarket.com/markets?slug={market['slug']}", timeout=5)
            if resp.status_code != 200:
                return None
            
            data = resp.json()
            if not data:
                return None
            
            market_data = data[0] if isinstance(data, list) else data
            tokens = market_data.get('tokens', [])
            
            if len(tokens) < 2:
                return None
            
            yes_token = tokens[0]['token_id']
            no_token = tokens[1]['token_id']
            
            # Get orderbooks
            yes_book = self.client.get_order_book(yes_token)
            no_book = self.client.get_order_book(no_token)
            
            yes_asks = yes_book.get('asks', [])
            no_asks = no_book.get('asks', [])
            
            if not yes_asks or not no_asks:
                return None
            
            # Best prices
            yes_price = float(yes_asks[-1]['price'])
            no_price = float(no_asks[-1]['price'])
            
            return {
                'yes_price': yes_price,
                'no_price': no_price,
                'total_cost': yes_price + no_price,
                'question': market_data.get('question', market['slug'])
            }
        except Exception as e:
            print(f"   ⚠️  Error getting market data: {e}")
            return None
    
    def check_opportunity(self, market, prices):
        """Check for trading opportunities"""
        total = prices['total_cost']
        
        # Spread arbitrage: total < $0.90 = 10%+ profit
        if total < 0.90:
            profit_pct = ((1.0 - total) / total) * 100
            return {
                'type': 'SPREAD_ARB',
                'profit_pct': profit_pct,
                'total_cost': total
            }
        
        # Momentum: one side < 40¢
        if prices['yes_price'] < 0.40:
            potential = ((0.95 - prices['yes_price']) / prices['yes_price']) * 100
            if potential > 50:
                return {
                    'type': 'MOMENTUM',
                    'side': 'YES',
                    'entry': prices['yes_price'],
                    'potential': potential
                }
        
        if prices['no_price'] < 0.40:
            potential = ((0.95 - prices['no_price']) / prices['no_price']) * 100
            if potential > 50:
                return {
                    'type': 'MOMENTUM',
                    'side': 'NO',
                    'entry': prices['no_price'],
                    'potential': potential
                }
        
        return None
    
    async def run(self):
        """Main trading loop"""
        scan = 0
        
        while True:
            scan += 1
            print(f"\n{'='*70}")
            print(f"📊 SCAN #{scan} - {datetime.now().strftime('%I:%M:%S %p ET')}")
            print(f"{'='*70}")
            
            # Find live markets
            markets = self.get_live_markets()
            
            if not markets:
                print("⚠️  No live markets found (this shouldn't happen!)")
                await asyncio.sleep(10)
                continue
            
            print(f"✅ Found {len(markets)} live 5-minute markets:\n")
            
            for m in markets:
                print(f"  🎯 {m['time_et']} - {m['slug']}")
                
                # Get prices
                prices = self.get_market_data(m)
                if not prices:
                    print(f"     ⚠️  No liquidity")
                    continue
                
                print(f"     YES: ${prices['yes_price']:.3f} | NO: ${prices['no_price']:.3f} | Sum: ${prices['total_cost']:.3f}")
                
                # Check for opportunity
                opp = self.check_opportunity(m, prices)
                if opp:
                    if opp['type'] == 'SPREAD_ARB':
                        print(f"     🔥 SPREAD ARB: {opp['profit_pct']:.1f}% profit!")
                    elif opp['type'] == 'MOMENTUM':
                        print(f"     🚀 MOMENTUM: {opp['side']} at ${opp['entry']:.3f} ({opp['potential']:.1f}% upside)")
                    
                    # Would execute trade here
                    self.trades.append({
                        'time': datetime.now().isoformat(),
                        'market': m['slug'],
                        'opportunity': opp
                    })
            
            # Summary
            if scan % 3 == 0:
                print(f"\n📈 SUMMARY: {len(self.trades)} opportunities found")
                print(f"💰 Balance: ${self.paper_balance:.2f}")
            
            await asyncio.sleep(15)  # Scan every 15 seconds

async def main():
    bot = LiveFiveMinBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
