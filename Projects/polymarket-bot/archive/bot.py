#!/usr/bin/env python3
"""
Polymarket Pro Trading Bot - $100 to Sustainable Profits
Multi-strategy arbitrage system optimized for 5-minute execution cycles
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, MarketOrderArgs, BookParams
from py_clob_client.constants import POLYGON
import aiohttp

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class PolymarketBot:
    def __init__(self, private_key: str, host: str = "https://clob.polymarket.com"):
        self.client = ClobClient(host, key=private_key, chain_id=POLYGON)
        self.bankroll = 100.0
        self.initial_bankroll = 100.0
        self.positions = {}
        self.trades = []
        self.running = False
        
    async def start(self):
        logger.info("🚀 Starting Polymarket Bot - $100 Challenge")
        self.running = True
        
        try:
            async with aiohttp.ClientSession() as session:
                self.session = session
                await asyncio.gather(
                    self.trade_loop(),
                    self.monitor_loop()
                )
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
    
    async def trade_loop(self):
        """Main trading loop - scans every 5 seconds"""
        while self.running:
            try:
                markets = await self.fetch_markets()
                
                # Find sum-to-one arbitrage
                for market in markets:
                    if not self.should_trade():
                        break
                    
                    opp = await self.check_sum_to_one_arb(market)
                    if opp:
                        await self.execute_arb(opp)
                
                await asyncio.sleep(config.MARKET_SCAN_INTERVAL)
            except Exception as e:
                logger.error(f"Trade loop error: {e}")
                await asyncio.sleep(5)
    
    async def monitor_loop(self):
        """Monitor positions and log status"""
        while self.running:
            try:
                profit = self.bankroll - self.initial_bankroll
                win_rate = (len([t for t in self.trades if t['profit'] > 0]) / len(self.trades) * 100) if self.trades else 0
                
                logger.info(
                    f"📊 Balance: ${self.bankroll:.2f} | "
                    f"P&L: ${profit:+.2f} ({profit/self.initial_bankroll*100:+.1f}%) | "
                    f"Trades: {len(self.trades)} | Win Rate: {win_rate:.0f}%"
                )
                
                # Stop loss check
                if profit <= -15:
                    logger.error("STOP LOSS HIT")
                    self.running = False
                
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(10)
    
    async def fetch_markets(self) -> List[Dict]:
        """Fetch active markets from Polymarket"""
        try:
            # Use Gamma API for market list
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'limit': 100,
                'closed': False,
                'active': True
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Filter for binary markets with volume
                    markets = [
                        m for m in data
                        if m.get('outcomes_count') == 2 and float(m.get('volume', 0)) > 5000
                    ]
                    return markets[:50]  # Top 50 by volume
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
        return []
    
    async def check_sum_to_one_arb(self, market: Dict) -> Optional[Dict]:
        """Check if YES + NO prices allow for arbitrage"""
        try:
            condition_id = market.get('condition_id')
            if not condition_id:
                return None
            
            # Get tokens for YES and NO
            tokens = market.get('tokens', [])
            if len(tokens) != 2:
                return None
            
            token_yes = tokens[0]['token_id']
            token_no = tokens[1]['token_id']
            
            # Get orderbooks
            book_yes = self.client.get_order_book(token_yes)
            book_no = self.client.get_order_book(token_no)
            
            # Get best ask prices (what we pay to buy)
            yes_asks = book_yes.get('asks', [])
            no_asks = book_no.get('asks', [])
            
            if not yes_asks or not no_asks:
                return None
            
            yes_price = float(yes_asks[0]['price'])
            no_price = float(no_asks[0]['price'])
            total_cost = yes_price + no_price
            
            # Arbitrage exists if total < 1.0
            if total_cost < 0.995:  # Leave 0.5% margin for slippage
                profit_per_dollar = 1.0 - total_cost
                
                if profit_per_dollar >= config.MIN_PROFIT_THRESHOLD:
                    position_size = min(
                        config.MAX_POSITION_SIZE,
                        self.bankroll * 0.4  # Max 40% per trade
                    )
                    
                    return {
                        'market': market,
                        'token_yes': token_yes,
                        'token_no': token_no,
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'total_cost': total_cost,
                        'size': position_size,
                        'expected_profit': position_size * profit_per_dollar
                    }
        except Exception as e:
            logger.debug(f"Error checking market: {e}")
        return None
    
    async def execute_arb(self, opp: Dict):
        """Execute arbitrage trade"""
        try:
            logger.info(
                f"💎 ARB FOUND: {opp['market'].get('question', '')[:60]} | "
                f"Cost: ${opp['total_cost']:.4f} | "
                f"Expected profit: ${opp['expected_profit']:.2f}"
            )
            
            # Buy YES
            yes_size = opp['size'] / opp['yes_price']
            no_size = opp['size'] / opp['no_price']
            
            # Place market orders
            yes_order = self.client.create_market_order(
                MarketOrderArgs(
                    token_id=opp['token_yes'],
                    amount=yes_size,
                    price=opp['yes_price'] * 1.01  # 1% slippage tolerance
                )
            )
            
            no_order = self.client.create_market_order(
                MarketOrderArgs(
                    token_id=opp['token_no'],
                    amount=no_size,
                    price=opp['no_price'] * 1.01
                )
            )
            
            if yes_order and no_order:
                # Record trade
                trade_id = f"{opp['market']['id']}_{int(time.time())}"
                self.positions[trade_id] = {
                    'market': opp['market'],
                    'cost': opp['size'],
                    'expected_profit': opp['expected_profit'],
                    'timestamp': datetime.now()
                }
                
                logger.info(f"✅ Position opened: ${opp['size']:.2f} invested")
                
                # Update bankroll (conservative estimate)
                self.bankroll -= opp['size']
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def should_trade(self) -> bool:
        """Check if we should continue trading"""
        # Don't trade if we're low on funds
        if self.bankroll < 10:
            return False
        
        # Don't exceed max concurrent positions
        if len(self.positions) >= config.MAX_CONCURRENT_TRADES:
            return False
        
        return True


async def main():
    load_dotenv()
    
    private_key = os.getenv('POLYMARKET_PRIVATE_KEY')
    if not private_key:
        print("❌ Error: POLYMARKET_PRIVATE_KEY not found in .env file")
        print("\nSetup instructions:")
        print("1. Create a .env file in this directory")
        print("2. Add your private key: POLYMARKET_PRIVATE_KEY=0x...")
        print("3. Fund your wallet with USDC on Polygon")
        return
    
    bot = PolymarketBot(private_key)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
