#!/usr/local/bin/python3
"""
COMPREHENSIVE POLYMARKET BACKTESTING ENGINE
Author: Top 0.01% Quant Analyst
Goal: Find REAL mathematical edge through rigorous statistical analysis

Methodology:
1. Collect maximum available historical data
2. Test price calibration across all ranges (0-100%)
3. Calculate Sharpe ratios, Kelly optimal sizing
4. Run Monte Carlo simulations for different strategies
5. Identify exploitable inefficiencies with statistical significance
"""
import requests
import json
import time
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from scipy import stats
import math

class PolymarketBacktester:
    def __init__(self):
        self.resolved_markets = []
        self.active_markets = []
        self.price_buckets = self.init_buckets()
        
    def init_buckets(self):
        """Initialize price range buckets for analysis"""
        return {
            '0-5%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '5-10%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '10-20%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '20-30%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '30-40%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '40-50%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '50-60%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '60-70%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '70-80%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '80-90%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
            '90-100%': {'prices': [], 'won': [], 'total': 0, 'wins': 0},
        }
    
    def get_bucket(self, price):
        """Assign price to bucket"""
        p = price * 100
        if p <= 5: return '0-5%'
        elif p <= 10: return '5-10%'
        elif p <= 20: return '10-20%'
        elif p <= 30: return '20-30%'
        elif p <= 40: return '30-40%'
        elif p <= 50: return '40-50%'
        elif p <= 60: return '50-60%'
        elif p <= 70: return '60-70%'
        elif p <= 80: return '70-80%'
        elif p <= 90: return '80-90%'
        else: return '90-100%'
    
    def fetch_resolved_markets(self, limit=500):
        """Fetch maximum resolved markets for backtesting"""
        print("=" * 80)
        print("📥 FETCHING HISTORICAL DATA")
        print("=" * 80)
        
        all_markets = []
        offset = 0
        batch_size = 100
        
        while offset < limit:
            try:
                print(f"Fetching batch {offset//batch_size + 1}...")
                resp = requests.get(
                    "https://gamma-api.polymarket.com/markets",
                    params={
                        "closed": "true",
                        "limit": batch_size,
                        "offset": offset
                    },
                    timeout=15
                )
                
                if resp.status_code == 200:
                    batch = resp.json()
                    if not batch:
                        break
                    all_markets.extend(batch)
                    offset += batch_size
                    time.sleep(0.5)  # Rate limit
                else:
                    print(f"API error: {resp.status_code}")
                    break
            
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.resolved_markets = all_markets
        print(f"\n✅ Fetched {len(all_markets)} markets\n")
        return all_markets
    
    def analyze_price_calibration(self):
        """
        Core analysis: Are prices calibrated?
        If 5% bets win 5% of time = fair
        If 5% bets win 3% of time = overpriced (retail bias)
        If 5% bets win 7% of time = underpriced (EDGE!)
        """
        print("=" * 80)
        print("📊 PRICE CALIBRATION ANALYSIS")
        print("=" * 80)
        print("Testing if market prices accurately reflect win probabilities...\n")
        
        analyzed = 0
        
        for market in self.resolved_markets:
            try:
                if not market.get('resolved'):
                    continue
                
                outcomes = json.loads(market.get('outcomes', '[]'))
                prices = json.loads(market.get('outcomePrices', '[]'))
                winning_outcome = market.get('winningOutcome')
                
                if not winning_outcome or not outcomes or not prices:
                    continue
                
                # Analyze each outcome
                for outcome, price_str in zip(outcomes, prices):
                    price = float(price_str)
                    
                    if price <= 0 or price >= 1:
                        continue
                    
                    won = 1 if outcome == winning_outcome else 0
                    bucket = self.get_bucket(price)
                    
                    self.price_buckets[bucket]['prices'].append(price)
                    self.price_buckets[bucket]['won'].append(won)
                    self.price_buckets[bucket]['total'] += 1
                    self.price_buckets[bucket]['wins'] += won
                    
                    analyzed += 1
            
            except:
                continue
        
        print(f"Analyzed {analyzed} individual outcomes across {len(self.resolved_markets)} markets\n")
        
        # Calculate statistics
        print("Price Range | Expected Win% | Actual Win% | Sample Size | Edge | p-value | Sharpe")
        print("-" * 90)
        
        results = []
        
        for bucket_name, data in self.price_buckets.items():
            if data['total'] < 10:  # Need minimum sample size
                continue
            
            # Expected win rate (midpoint of bucket)
            expected_map = {
                '0-5%': 2.5,
                '5-10%': 7.5,
                '10-20%': 15.0,
                '20-30%': 25.0,
                '30-40%': 35.0,
                '40-50%': 45.0,
                '50-60%': 55.0,
                '60-70%': 65.0,
                '70-80%': 75.0,
                '80-90%': 85.0,
                '90-100%': 95.0,
            }
            
            expected = expected_map[bucket_name]
            actual = (data['wins'] / data['total']) * 100
            edge = actual - expected
            
            # Statistical significance test (binomial test)
            p_value = stats.binom_test(
                data['wins'],
                data['total'],
                expected / 100,
                alternative='two-sided'
            )
            
            # Calculate Sharpe ratio equivalent
            # Sharpe = (mean return - risk free rate) / std dev
            prices_arr = np.array(data['prices'])
            won_arr = np.array(data['won'])
            
            # Returns for each bet
            returns = []
            for price, won in zip(data['prices'], data['won']):
                if won:
                    returns.append((1 - price) / price)  # Profit on win
                else:
                    returns.append(-1)  # Lost entire bet
            
            returns_arr = np.array(returns)
            mean_return = np.mean(returns_arr)
            std_return = np.std(returns_arr)
            sharpe = mean_return / std_return if std_return > 0 else 0
            
            results.append({
                'bucket': bucket_name,
                'expected': expected,
                'actual': actual,
                'edge': edge,
                'n': data['total'],
                'p_value': p_value,
                'sharpe': sharpe,
                'mean_return': mean_return,
                'std_return': std_return
            })
            
            # Display
            sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
            edge_color = "🟢" if edge > 0 else "🔴" if edge < 0 else "⚪"
            
            print(f"{bucket_name:11} | {expected:13.1f}% | {actual:11.1f}% | {data['total']:11} | {edge_color}{edge:+5.1f}% | {p_value:7.4f}{sig:3} | {sharpe:+6.2f}")
        
        return results
    
    def monte_carlo_simulation(self, strategy, n_simulations=10000, n_bets=100, bankroll=1000):
        """
        Run Monte Carlo simulation for a given strategy
        Returns distribution of outcomes
        """
        print(f"\n🎲 Running {n_simulations:,} Monte Carlo simulations...")
        print(f"   Strategy: {strategy['name']}")
        print(f"   Starting bankroll: ${bankroll}")
        print(f"   Bets per simulation: {n_bets}")
        
        # Get relevant data for this strategy
        target_buckets = strategy['buckets']
        bet_fraction = strategy['kelly_fraction']  # Fraction of Kelly to use
        
        # Collect all qualifying bets
        qualifying_bets = []
        for bucket in target_buckets:
            if bucket in self.price_buckets:
                data = self.price_buckets[bucket]
                for price, won in zip(data['prices'], data['won']):
                    qualifying_bets.append({'price': price, 'won': won})
        
        if len(qualifying_bets) < 20:
            print(f"   ⚠️  Insufficient data ({len(qualifying_bets)} bets)")
            return None
        
        print(f"   Qualifying historical bets: {len(qualifying_bets)}")
        
        # Run simulations
        final_bankrolls = []
        
        for sim in range(n_simulations):
            current_bankroll = bankroll
            
            for bet_num in range(n_bets):
                if current_bankroll <= 0:
                    break
                
                # Sample a random bet from historical data
                bet = qualifying_bets[np.random.randint(len(qualifying_bets))]
                price = bet['price']
                won = bet['won']
                
                # Kelly criterion: f* = (bp - q) / b
                # where b = odds, p = true prob, q = 1-p
                # For simplicity, use price as probability estimate
                true_prob = price  # Market price (our estimate)
                odds = (1 - price) / price
                
                kelly = (odds * true_prob - (1 - true_prob)) / odds
                kelly = max(0, kelly)  # Don't bet if negative edge
                
                # Bet fractional Kelly (more conservative)
                bet_size = current_bankroll * kelly * bet_fraction
                bet_size = min(bet_size, current_bankroll * 0.10)  # Cap at 10% of bankroll
                
                if bet_size < 1:
                    continue
                
                # Outcome
                if won:
                    profit = bet_size * odds
                    current_bankroll += profit
                else:
                    current_bankroll -= bet_size
            
            final_bankrolls.append(current_bankroll)
        
        # Statistics
        final_array = np.array(final_bankrolls)
        
        results = {
            'mean': np.mean(final_array),
            'median': np.median(final_array),
            'std': np.std(final_array),
            'min': np.min(final_array),
            'max': np.max(final_array),
            'prob_profit': np.sum(final_array > bankroll) / n_simulations,
            'prob_double': np.sum(final_array > bankroll * 2) / n_simulations,
            'prob_ruin': np.sum(final_array < bankroll * 0.1) / n_simulations,
            'percentile_5': np.percentile(final_array, 5),
            'percentile_95': np.percentile(final_array, 95),
        }
        
        print(f"\n   📈 Results after {n_bets} bets:")
        print(f"      Mean final bankroll:  ${results['mean']:.2f}")
        print(f"      Median final:         ${results['median']:.2f}")
        print(f"      5th percentile:       ${results['percentile_5']:.2f}")
        print(f"      95th percentile:      ${results['percentile_95']:.2f}")
        print(f"      Prob of profit:       {results['prob_profit']*100:.1f}%")
        print(f"      Prob of 2x:           {results['prob_double']*100:.1f}%")
        print(f"      Prob of ruin (<10%):  {results['prob_ruin']*100:.1f}%")
        
        return results
    
    def compare_strategies(self):
        """Test multiple strategies with Monte Carlo"""
        print("\n" + "=" * 80)
        print("🔬 STRATEGY COMPARISON (Monte Carlo)")
        print("=" * 80)
        
        strategies = [
            {
                'name': 'Longshot Strategy (0-10%)',
                'buckets': ['0-5%', '5-10%'],
                'kelly_fraction': 0.25
            },
            {
                'name': 'Value Range (10-20%)',
                'buckets': ['10-20%'],
                'kelly_fraction': 0.25
            },
            {
                'name': 'Golden Range (20-40%)',
                'buckets': ['20-30%', '30-40%'],
                'kelly_fraction': 0.25
            },
            {
                'name': 'Coin Flip Zone (40-60%)',
                'buckets': ['40-50%', '50-60%'],
                'kelly_fraction': 0.25
            },
            {
                'name': 'Favorites (70-90%)',
                'buckets': ['70-80%', '80-90%'],
                'kelly_fraction': 0.25
            },
        ]
        
        comparison = []
        
        for strategy in strategies:
            result = self.monte_carlo_simulation(strategy, n_simulations=5000, n_bets=50, bankroll=1000)
            if result:
                comparison.append({
                    'name': strategy['name'],
                    'expected_value': result['mean'] - 1000,
                    'median_value': result['median'] - 1000,
                    'prob_profit': result['prob_profit'],
                    'sharpe': (result['mean'] - 1000) / result['std'] if result['std'] > 0 else 0
                })
        
        print("\n" + "=" * 80)
        print("📊 STRATEGY RANKINGS")
        print("=" * 80)
        print()
        print("Strategy                     | Expected P&L | Prob Profit | Sharpe")
        print("-" * 80)
        
        comparison.sort(key=lambda x: x['expected_value'], reverse=True)
        
        for i, strat in enumerate(comparison, 1):
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{rank_emoji} {strat['name']:26} | ${strat['expected_value']:+11.2f} | {strat['prob_profit']*100:10.1f}% | {strat['sharpe']:+6.2f}")
        
        return comparison

def main():
    print("=" * 80)
    print("🎯 POLYMARKET COMPREHENSIVE BACKTESTING ENGINE")
    print("=" * 80)
    print("Mathematical analysis of market inefficiencies\n")
    
    bt = PolymarketBacktester()
    
    # Step 1: Fetch data
    bt.fetch_resolved_markets(limit=500)
    
    # Step 2: Price calibration analysis
    calibration_results = bt.analyze_price_calibration()
    
    # Step 3: Strategy comparison
    strategy_results = bt.compare_strategies()
    
    # Step 4: Final recommendation
    print("\n" + "=" * 80)
    print("💡 FINAL RECOMMENDATIONS")
    print("=" * 80)
    
    if strategy_results:
        best = strategy_results[0]
        print(f"\n🏆 Best Strategy: {best['name']}")
        print(f"   Expected P&L: ${best['expected_value']:+.2f} per 50 bets on $1000 bankroll")
        print(f"   Probability of Profit: {best['prob_profit']*100:.1f}%")
        print(f"   Sharpe Ratio: {best['sharpe']:+.2f}")
        
        if best['expected_value'] > 0:
            print(f"\n   ✅ POSITIVE EXPECTED VALUE - This strategy has mathematical edge")
        else:
            print(f"\n   ❌ NEGATIVE EXPECTED VALUE - This strategy loses money long-term")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
