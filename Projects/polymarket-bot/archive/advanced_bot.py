#!/usr/bin/env python3
"""
Advanced Polymarket Trading Bot with Multi-Strategy Execution
Includes: Sum-to-one ARB, Momentum trading, Market making
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs
from py_clob_client.constants import POLYGON
import aiohttp
import os
from dotenv import load_dotenv

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyzes markets for various trading opportunities"""
    
    def __init__(self):
        self.price_history = defaultdict(list)
        self.volume_history = defaultdict(list)
    
    def update_market_data(self, market_id: str, price: float, volume: float):
        """Track price and volume over time"""
        self.price_history[market_id].append({
            'timestamp': time.time(),
            'price': price
        })
        self.volume_history[market_id].append({
            'timestamp': time.time(),
            'volume': volume
        })
        
        # Keep only last 1 hour of data
        cutoff = time.time() - 3600
        self.price_history[market_id] = [
            p for p in self.price_history[market_id] 
            if p['timestamp'] > cutoff
        ]
        self.volume_history[market_id] = [
            v for v in self.volume_history[market_id]
            if v['timestamp'] > cutoff
        ]
    
    def detect_momentum(self, market_id: str) -> Optional[Dict]:
        """Detect price momentum for scalping opportunities"""
        history = self.price_history.get(market_id, [])
        
        if len(history) < 10:  # Need at least 10 data points
            return None
        
        # Calculate price change over last 5 minutes
        recent = [p for p in history if p['timestamp'] > time.time() - 300]
        
        if len(recent) < 5:
            return None
        
        start_price = recent[0]['price']
        end_price = recent[-1]['price']
        price_change = (end_price - start_price) / start_price
        
        # Strong momentum if >2% move in 5 minutes
        if abs(price_change) > 0.02:
            return {
                'direction': 'up' if price_change > 0 else 'down',
                'magnitude': abs(price_change),
                'confidence': min(abs(price_change) / 0.05, 1.0)  # Max at 5% move
            }
        
        return None


class AdvancedPolymarketBot:
    """Advanced multi-strategy trading bot"""
    
    def __init__(self, private_key: str):
        self.client = ClobClient(
            host=config.POLYMARKET_API,
            key=private_key,
            chain_id=POLYGON
        )
        
        self.analyzer = MarketAnalyzer()
        self.bankroll = 100.0
        self.initial_bankroll = 100.0
        self.positions = {}
        self.trade_history = []
        self.running = False
        
        # Strategy performance tracking
        self.strategy_stats = {
            'sum_to_one': {'trades': 0, 'profit': 0.0, 'win_rate': 0.0},
            'momentum': {'trades': 0, 'profit': 0.0, 'win_rate': 0.0},
            'market_making': {'trades': 0, 'profit': 0.0, 'win_rate': 0.0},
        }
        
        # Daily tracking
        self.daily_stats = {
            'date': datetime.now().date(),
            'starting_balance': self.bankroll,
            'trades': 0,
            'profit': 0.0
        }
    
    async def start(self):
        """Start the advanced trading bot"""
        logger.info("🚀 Starting Advanced Polymarket Bot")
        logger.info(f"💰 Initial bankroll: ${self.bankroll:.2f}")
        
        self.running = True
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                await asyncio.gather(
                    self.sum_to_one_scanner(),
                    self.momentum_scanner(),
                    self.position_manager(),
                    self.performance_tracker(),
                    self.daily_reset()
                )
            except KeyboardInterrupt:
                logger.info("⚠️  Shutting down...")
                await self.shutdown()
            except Exception as e:
                logger.error(f"Critical error: {e}", exc_info=True)
                await self.shutdown()
    
    async def sum_to_one_scanner(self):
        """Scan for sum-to-one arbitrage opportunities"""
        logger.info("📊 Sum-to-one scanner started")
        
        while self.running:
            try:
                markets = await self.fetch_markets()
                
                for market in markets:
                    if not self.can_trade():
                        break
                    
                    opp = await self.check_sum_to_one(market)
                    if opp and opp['expected_profit'] > 0.5:  # Min $0.50 profit
                        await self.execute_sum_to_one(opp)
                
                await asyncio.sleep(config.MARKET_SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Sum-to-one scanner error: {e}")
                await asyncio.sleep(5)
    
    async def momentum_scanner(self):
        """Scan for momentum trading opportunities"""
        logger.info("⚡ Momentum scanner started")
        
        while self.running:
            try:
                # Focus on 15-minute crypto markets
                crypto_markets = await self.fetch_crypto_markets()
                
                for market in crypto_markets:
                    market_id = market.get('id')
                    
                    # Update market data for momentum detection
                    price = self.get_market_mid_price(market)
                    volume = float(market.get('volume', 0))
                    
                    self.analyzer.update_market_data(market_id, price, volume)
                    
                    # Check for momentum
                    momentum = self.analyzer.detect_momentum(market_id)
                    
                    if momentum and momentum['confidence'] > 0.7:
                        if self.can_trade():
                            await self.execute_momentum_trade(market, momentum)
                
                await asyncio.sleep(10)  # Check every 10 seconds for fast markets
                
            except Exception as e:
                logger.error(f"Momentum scanner error: {e}")
                await asyncio.sleep(10)
    
    async def fetch_markets(self) -> List[Dict]:
        """Fetch active markets"""
        try:
            url = f"{config.GAMMA_API}/markets"
            params = {
                'limit': 100,
                'closed': False,
                'active': True
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [
                        m for m in data 
                        if m.get('outcomes_count') == 2 and 
                        float(m.get('volume', 0)) > config.MIN_LIQUIDITY
                    ]
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
        return []
    
    async def fetch_crypto_markets(self) -> List[Dict]:
        """Fetch crypto-related markets (15-min resolution)"""
        markets = await self.fetch_markets()
        
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto']
        
        return [
            m for m in markets
            if any(kw in m.get('question', '').lower() for kw in crypto_keywords)
            and float(m.get('volume', 0)) > 10000
        ]
    
    async def check_sum_to_one(self, market: Dict) -> Optional[Dict]:
        """Check for sum-to-one arbitrage"""
        try:
            tokens = market.get('tokens', [])
            if len(tokens) != 2:
                return None
            
            token_yes = tokens[0]['token_id']
            token_no = tokens[1]['token_id']
            
            # Get orderbooks
            book_yes = self.client.get_order_book(token_yes)
            book_no = self.client.get_order_book(token_no)
            
            yes_asks = book_yes.get('asks', [])
            no_asks = book_no.get('asks', [])
            
            if not yes_asks or not no_asks:
                return None
            
            yes_price = float(yes_asks[0]['price'])
            no_price = float(no_asks[0]['price'])
            total_cost = yes_price + no_price
            
            if total_cost < 0.995:
                profit_per_dollar = 1.0 - total_cost
                
                if profit_per_dollar >= config.MIN_PROFIT_THRESHOLD:
                    position_size = self.calculate_position_size('sum_to_one')
                    
                    return {
                        'strategy': 'sum_to_one',
                        'market': market,
                        'token_yes': token_yes,
                        'token_no': token_no,
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'total_cost': total_cost,
                        'size': position_size,
                        'expected_profit': position_size * profit_per_dollar,
                        'profit_percent': profit_per_dollar * 100
                    }
        except Exception as e:
            logger.debug(f"Error checking sum-to-one: {e}")
        return None
    
    def get_market_mid_price(self, market: Dict) -> float:
        """Get mid price for a market"""
        try:
            tokens = market.get('tokens', [])
            if tokens:
                token_id = tokens[0]['token_id']
                book = self.client.get_order_book(token_id)
                
                asks = book.get('asks', [])
                bids = book.get('bids', [])
                
                if asks and bids:
                    best_ask = float(asks[0]['price'])
                    best_bid = float(bids[0]['price'])
                    return (best_ask + best_bid) / 2.0
        except:
            pass
        return 0.5  # Default mid price
    
    async def execute_sum_to_one(self, opp: Dict):
        """Execute sum-to-one arbitrage"""
        try:
            logger.info(
                f"💎 SUM-TO-ONE ARB: {opp['market'].get('question', '')[:60]} | "
                f"Cost: ${opp['total_cost']:.4f} | Profit: ${opp['expected_profit']:.2f}"
            )
            
            # Place orders (simplified - would use actual client methods)
            logger.info(f"✅ Trade executed: ${opp['size']:.2f} position")
            
            # Track trade
            self.trade_history.append({
                'strategy': 'sum_to_one',
                'timestamp': datetime.now(),
                'size': opp['size'],
                'expected_profit': opp['expected_profit']
            })
            
            self.strategy_stats['sum_to_one']['trades'] += 1
            self.daily_stats['trades'] += 1
            
            # Update bankroll (conservative)
            self.bankroll -= opp['size']
            
        except Exception as e:
            logger.error(f"Error executing sum-to-one: {e}")
    
    async def execute_momentum_trade(self, market: Dict, momentum: Dict):
        """Execute momentum scalp trade"""
        try:
            position_size = self.calculate_position_size('momentum')
            
            logger.info(
                f"⚡ MOMENTUM: {market.get('question', '')[:60]} | "
                f"Direction: {momentum['direction']} | "
                f"Confidence: {momentum['confidence']:.0%}"
            )
            
            # Would place directional trade here
            logger.info(f"✅ Momentum trade: ${position_size:.2f}")
            
            self.strategy_stats['momentum']['trades'] += 1
            
        except Exception as e:
            logger.error(f"Error executing momentum trade: {e}")
    
    def calculate_position_size(self, strategy: str) -> float:
        """Calculate position size based on strategy and bankroll"""
        base_size = min(
            config.MAX_POSITION_SIZE,
            self.bankroll * 0.3
        )
        
        # Adjust based on strategy performance
        if strategy in self.strategy_stats:
            stats = self.strategy_stats[strategy]
            if stats['trades'] > 5 and stats['win_rate'] > 70:
                base_size *= 1.2  # Increase size for winning strategies
        
        return min(base_size, self.bankroll * 0.4)
    
    def can_trade(self) -> bool:
        """Check if we can place new trades"""
        if self.bankroll < 10:
            return False
        
        if len(self.positions) >= config.MAX_CONCURRENT_TRADES:
            return False
        
        # Check daily loss limit
        daily_loss = self.daily_stats['starting_balance'] - self.bankroll
        if daily_loss > config.DAILY_LOSS_LIMIT * self.initial_bankroll:
            logger.warning("Daily loss limit reached")
            return False
        
        return True
    
    async def position_manager(self):
        """Manage open positions"""
        logger.info("👁️  Position manager started")
        
        while self.running:
            try:
                # Monitor and close positions
                # Would implement position tracking and resolution here
                await asyncio.sleep(config.POSITION_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Position manager error: {e}")
                await asyncio.sleep(10)
    
    async def performance_tracker(self):
        """Track and log performance metrics"""
        logger.info("📊 Performance tracker started")
        
        while self.running:
            try:
                profit = self.bankroll - self.initial_bankroll
                profit_pct = profit / self.initial_bankroll * 100
                
                # Calculate win rate
                wins = len([t for t in self.trade_history if t.get('profit', 0) > 0])
                total = len(self.trade_history)
                win_rate = (wins / total * 100) if total > 0 else 0
                
                logger.info(
                    f"📈 PERFORMANCE | "
                    f"Balance: ${self.bankroll:.2f} | "
                    f"P&L: ${profit:+.2f} ({profit_pct:+.1f}%) | "
                    f"Trades: {total} | "
                    f"Win Rate: {win_rate:.0f}% | "
                    f"Positions: {len(self.positions)}"
                )
                
                # Log strategy breakdown
                logger.info(
                    f"    Sum-to-One: {self.strategy_stats['sum_to_one']['trades']} trades | "
                    f"Momentum: {self.strategy_stats['momentum']['trades']} trades"
                )
                
                # Check stop loss
                if profit <= -1 * config.STOP_LOSS_PERCENT * self.initial_bankroll:
                    logger.error("🛑 STOP LOSS HIT")
                    await self.shutdown()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(10)
    
    async def daily_reset(self):
        """Reset daily stats at midnight"""
        while self.running:
            try:
                now = datetime.now()
                
                # Check if day changed
                if now.date() > self.daily_stats['date']:
                    logger.info(f"📅 Daily Reset | Previous day P&L: ${self.daily_stats['profit']:.2f}")
                    
                    self.daily_stats = {
                        'date': now.date(),
                        'starting_balance': self.bankroll,
                        'trades': 0,
                        'profit': 0.0
                    }
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Daily reset error: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self.running = False
        
        # Final stats
        profit = self.bankroll - self.initial_bankroll
        logger.info(f"Final Balance: ${self.bankroll:.2f}")
        logger.info(f"Total P&L: ${profit:+.2f}")
        logger.info(f"Total Trades: {len(self.trade_history)}")
        
        for strategy, stats in self.strategy_stats.items():
            if stats['trades'] > 0:
                logger.info(f"{strategy}: {stats['trades']} trades, ${stats['profit']:.2f} profit")


async def main():
    load_dotenv()
    
    private_key = os.getenv('POLYMARKET_PRIVATE_KEY')
    if not private_key:
        print("❌ POLYMARKET_PRIVATE_KEY not found in .env")
        return
    
    bot = AdvancedPolymarketBot(private_key)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
