#!/usr/bin/env python3
"""
Polymarket 5-Minute Market Trading Bot
Strategies: Spread Arbitrage + Momentum Scalping
Target: 20-30% profit per trade, 60-70% win rate
"""

import asyncio
import json
import time
import os
from datetime import datetime
from py_clob_client.client import ClobClient
import requests

class FiveMinuteBot:
    def __init__(self, paper_trading=True):
        self.client = ClobClient('https://clob.polymarket.com')
        self.paper_trading = paper_trading
        self.paper_balance = 100.0
        self.trades = []
        self.active_positions = {}
        
        print("="*70)
        print("🚀 POLYMARKET 5-MINUTE MARKET BOT")
        print("="*70)
        if paper_trading:
            print("⚠️  PAPER TRADING MODE - ZERO RISK")
            print(f"   Starting balance: ${self.paper_balance:.2f}")
        print("="*70)
        print()
    
    def find_five_min_markets(self):
        """Find active 5-minute BTC/ETH markets"""
        print("🔍 Scanning for 5-minute markets...")
        
        # Polymarket uses predictable slugs for these markets
        # Format: btc-updown-5m-{timestamp} or eth-updown-5m-{timestamp}
        
        try:
            # Try to get markets from API
            url = 'https://clob.polymarket.com/markets'
            params = {'limit': 200, 'closed': False}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', data) if isinstance(data, dict) else data
                
                five_min_markets = []
                for m in markets:
                    question = m.get('question', '').lower()
                    slug = m.get('market_slug', '')
                    
                    # Look for 5-min crypto markets
                    if ('5m' in slug or ('5' in question and 'minute' in question)) and \
                       ('btc' in question or 'bitcoin' in question or 'eth' in question or 'ethereum' in question) and \
                       ('up' in question or 'down' in question):
                        
                        if m.get('active') and not m.get('closed'):
                            five_min_markets.append(m)
                            print(f"   ✅ {m['question'][:60]}...")
                
                return five_min_markets
        except Exception as e:
            print(f"   ⚠️  API error: {e}")
        
        return []
    
    async def get_market_prices(self, market):
        """Get current bid/ask prices for a market"""
        try:
            tokens = market.get('tokens', [])
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
            
            # Best prices (asks sorted high to low, take LAST)
            yes_price = float(yes_asks[-1]['price'])
            no_price = float(no_asks[-1]['price'])
            
            return {
                'yes_price': yes_price,
                'no_price': no_price,
                'yes_token': yes_token,
                'no_token': no_token,
                'question': market['question']
            }
        except Exception as e:
            return None
    
    def check_spread_arbitrage(self, prices):
        """
        Strategy #1: Spread Arbitrage
        Buy both YES and NO when total < $1.00
        Target: 25% profit when spread is wide enough
        """
        total_cost = prices['yes_price'] + prices['no_price']
        
        # For 5-min markets, we want BIG spreads (not 0.3% like before)
        # Target: total cost < $0.90 for 10%+ profit minimum
        if total_cost < 0.90:
            profit_pct = ((1.0 - total_cost) / total_cost) * 100
            return {
                'type': 'spread_arb',
                'total_cost': total_cost,
                'profit_pct': profit_pct,
                'action': 'BUY_BOTH'
            }
        
        return None
    
    def check_momentum_opportunity(self, prices, market_start_time=None):
        """
        Strategy #2: Momentum Scalping
        Wait 30-60s after market opens, then buy the side moving up
        
        This requires tracking price movements over time
        For now, we'll implement a simple version
        """
        # If one side is significantly cheaper (< 40¢), that's the momentum play
        # The crowd is piling into the expensive side, creating value on the cheap side
        
        if prices['yes_price'] < 0.40:
            return {
                'type': 'momentum',
                'side': 'YES',
                'entry_price': prices['yes_price'],
                'target_exit': 0.95,
                'profit_potential': ((0.95 - prices['yes_price']) / prices['yes_price']) * 100
            }
        
        if prices['no_price'] < 0.40:
            return {
                'type': 'momentum',
                'side': 'NO',
                'entry_price': prices['no_price'],
                'target_exit': 0.95,
                'profit_potential': ((0.95 - prices['no_price']) / prices['no_price']) * 100
            }
        
        return None
    
    def execute_paper_trade(self, market, strategy):
        """Simulate a trade in paper trading mode"""
        trade_id = len(self.trades) + 1
        
        print(f"\n💎 PAPER TRADE #{trade_id}")
        print(f"   Market: {market['question'][:50]}...")
        print(f"   Strategy: {strategy['type']}")
        
        if strategy['type'] == 'spread_arb':
            position_size = 10.0  # $10 micro-position
            cost = position_size * strategy['total_cost']
            potential_profit = position_size * (1.0 - strategy['total_cost'])
            
            print(f"   Action: BUY YES + NO")
            print(f"   Position Size: ${position_size:.2f}")
            print(f"   Total Cost: ${cost:.2f}")
            print(f"   Potential Profit: ${potential_profit:.2f} ({strategy['profit_pct']:.1f}%)")
            
            self.paper_balance -= cost
            
            # Record trade
            trade = {
                'id': trade_id,
                'timestamp': datetime.now().isoformat(),
                'market': market['question'],
                'strategy': 'spread_arb',
                'cost': cost,
                'potential_profit': potential_profit,
                'status': 'OPEN'
            }
            self.trades.append(trade)
            
        elif strategy['type'] == 'momentum':
            position_size = 20.0  # $20 for momentum plays
            cost = position_size * strategy['entry_price']
            potential_profit = position_size * (strategy['target_exit'] - strategy['entry_price'])
            
            print(f"   Action: BUY {strategy['side']}")
            print(f"   Entry Price: ${strategy['entry_price']:.2f}")
            print(f"   Target Exit: ${strategy['target_exit']:.2f}")
            print(f"   Position Size: ${position_size:.2f}")
            print(f"   Cost: ${cost:.2f}")
            print(f"   Potential Profit: ${potential_profit:.2f} ({strategy['profit_potential']:.1f}%)")
            
            self.paper_balance -= cost
            
            trade = {
                'id': trade_id,
                'timestamp': datetime.now().isoformat(),
                'market': market['question'],
                'strategy': 'momentum',
                'side': strategy['side'],
                'cost': cost,
                'potential_profit': potential_profit,
                'status': 'OPEN'
            }
            self.trades.append(trade)
        
        print(f"   Remaining Balance: ${self.paper_balance:.2f}")
        return trade
    
    async def scan_and_trade(self):
        """Main trading loop"""
        print("\n🎯 Starting trading loop...")
        print("   Scanning every 10 seconds for opportunities\n")
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"📊 SCAN #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            
            # Find 5-min markets
            markets = self.find_five_min_markets()
            
            if not markets:
                print("   ⚠️  No 5-minute markets found")
                print("   This is normal if markets haven't been created yet")
                print("   5-min markets are created every 5 minutes during active hours")
                await asyncio.sleep(10)
                continue
            
            print(f"   Found {len(markets)} active 5-minute markets")
            
            # Scan each market for opportunities
            for market in markets:
                prices = await self.get_market_prices(market)
                
                if not prices:
                    continue
                
                # Check for spread arbitrage
                spread_opp = self.check_spread_arbitrage(prices)
                if spread_opp:
                    print(f"\n🔥 SPREAD ARBITRAGE OPPORTUNITY!")
                    self.execute_paper_trade(market, spread_opp)
                
                # Check for momentum opportunity
                momentum_opp = self.check_momentum_opportunity(prices)
                if momentum_opp and momentum_opp['profit_potential'] > 50:  # Only if 50%+ upside
                    print(f"\n🚀 MOMENTUM OPPORTUNITY!")
                    self.execute_paper_trade(market, momentum_opp)
            
            # Show summary every 5 scans
            if iteration % 5 == 0:
                self.print_summary()
            
            await asyncio.sleep(10)
    
    def print_summary(self):
        """Print trading summary"""
        print(f"\n{'='*70}")
        print("📈 TRADING SUMMARY")
        print(f"{'='*70}")
        print(f"Paper Balance: ${self.paper_balance:.2f}")
        print(f"Open Trades: {len([t for t in self.trades if t['status'] == 'OPEN'])}")
        print(f"Total Trades: {len(self.trades)}")
        
        if self.trades:
            total_potential = sum(t.get('potential_profit', 0) for t in self.trades if t['status'] == 'OPEN')
            print(f"Potential Profit (if all win): ${total_potential:.2f}")
        
        print(f"{'='*70}\n")

async def main():
    bot = FiveMinuteBot(paper_trading=True)
    await bot.scan_and_trade()

if __name__ == "__main__":
    asyncio.run(main())
