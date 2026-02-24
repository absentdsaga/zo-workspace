#!/usr/local/bin/python3
"""
GOLDEN RANGE BOT (20-40¢)
Paper trading the research-backed "Golden Range" strategy

Strategy:
- Only bet on markets priced 20-40¢
- High volume markets (>$10k)
- Use 1/4 Kelly sizing
- Track real performance vs blockchain data

This runs in parallel with blockchain scraping to validate hypothesis
"""
import requests
import json
import time
from datetime import datetime

class GoldenRangeBot:
    def __init__(self):
        self.positions = {}
        self.bankroll = 1000
        self.trades_log = []
        
    def find_opportunities(self):
        """Find markets in 20-40¢ range"""
        try:
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
                return []
            
            markets = resp.json()
            opportunities = []
            
            for market in markets:
                try:
                    question = market.get('question', '')
                    volume = float(market.get('volume', 0))
                    
                    if volume < 10000:  # Min $10k volume
                        continue
                    
                    outcomes = json.loads(market.get('outcomes', '[]'))
                    prices = json.loads(market.get('outcomePrices', '[]'))
                    slug = market.get('slug', '')
                    
                    for outcome, price_str in zip(outcomes, prices):
                        price = float(price_str)
                        
                        # GOLDEN RANGE: 20-40¢
                        if 0.20 <= price <= 0.40:
                            opportunities.append({
                                'question': question,
                                'outcome': outcome,
                                'price': price,
                                'volume': volume,
                                'slug': slug
                            })
                
                except:
                    continue
            
            return opportunities
            
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def execute_trade(self, opp):
        """Execute paper trade with Kelly sizing"""
        price = opp['price']
        
        # Kelly criterion: f = (bp - q) / b
        # where b = odds, p = estimated prob, q = 1-p
        # Using research: 20-40¢ bets win ~2% more than expected
        estimated_prob = price + 0.02  # Research edge
        odds = (1 - price) / price
        
        kelly = (odds * estimated_prob - (1 - estimated_prob)) / odds
        kelly = max(0, kelly)
        
        # Use 1/4 Kelly for safety
        bet_fraction = kelly * 0.25
        bet_size = self.bankroll * bet_fraction
        bet_size = min(bet_size, self.bankroll * 0.05)  # Max 5% per bet
        
        if bet_size < 1:
            return False
        
        # Log trade
        trade = {
            'timestamp': datetime.now().isoformat(),
            'question': opp['question'][:60],
            'outcome': opp['outcome'],
            'price': price,
            'bet_size': bet_size,
            'kelly_fraction': bet_fraction,
            'url': f"https://polymarket.com/event/{opp['slug']}"
        }
        
        self.trades_log.append(trade)
        
        print(f"📝 TRADE: {trade['outcome']} @ {price*100:.1f}¢")
        print(f"   Market: {trade['question']}")
        print(f"   Bet: ${bet_size:.2f} (Kelly: {bet_fraction*100:.1f}%)")
        print(f"   URL: {trade['url']}")
        print()
        
        return True
    
    def run(self, max_trades=10):
        """Run the bot"""
        print("=" * 80)
        print("🎯 GOLDEN RANGE BOT (20-40¢)")
        print("=" * 80)
        print(f"Strategy: Research-backed golden range")
        print(f"Bankroll: ${self.bankroll}")
        print(f"Max trades: {max_trades}")
        print("=" * 80)
        print()
        
        print("🔍 Scanning for opportunities...")
        opportunities = self.find_opportunities()
        
        print(f"✅ Found {len(opportunities)} markets in 20-40¢ range\n")
        
        # Show top opportunities
        opportunities.sort(key=lambda x: x['volume'], reverse=True)
        
        print("Top opportunities by volume:")
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{i}. {opp['price']*100:.1f}¢ - {opp['outcome']}")
            print(f"   {opp['question'][:60]}")
            print(f"   Volume: ${opp['volume']:,.0f}")
            print()
        
        # Execute trades
        trades_made = 0
        for opp in opportunities[:max_trades]:
            if self.execute_trade(opp):
                trades_made += 1
                time.sleep(0.5)
        
        print("=" * 80)
        print(f"✅ Executed {trades_made} trades")
        print("=" * 80)
        
        # Save log
        with open('golden_range_trades.json', 'w') as f:
            json.dump(self.trades_log, f, indent=2)
        
        print("\n💾 Trades logged to: golden_range_trades.json")

if __name__ == "__main__":
    bot = GoldenRangeBot()
    bot.run(max_trades=5)  # Start with 5 trades
