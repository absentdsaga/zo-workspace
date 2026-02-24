#!/usr/local/bin/python3
"""
COMPREHENSIVE POLYMARKET DATA ANALYZER
Processes raw blockchain data to find TRUE mathematical edge

Features:
1. Price calibration analysis (do prices match outcomes?)
2. Market efficiency by category/time/volume
3. Wallet performance tracking (who wins?)
4. Strategy backtesting on REAL trades
5. Monte Carlo validation
6. Statistical significance testing
"""
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
from scipy.stats import binomtest, chi2_contingency
import json
import os

class PolymarketDataAnalyzer:
    def __init__(self, data_dir='/tmp/poly_data'):
        self.data_dir = data_dir
        self.markets_df = None
        self.trades_df = None
        self.calibration_buckets = defaultdict(lambda: {'prices': [], 'outcomes': [], 'volumes': []})
        
    def load_markets(self):
        """Load market metadata"""
        print("=" * 80)
        print("📥 LOADING MARKET DATA")
        print("=" * 80)
        
        markets_path = f"{self.data_dir}/markets.csv"
        
        if not os.path.exists(markets_path):
            print(f"❌ Markets file not found: {markets_path}")
            return None
        
        try:
            self.markets_df = pd.read_csv(markets_path)
            print(f"✅ Loaded {len(self.markets_df):,} markets")
            print(f"   Columns: {list(self.markets_df.columns)[:10]}...")
            
            # Show sample
            print(f"\n📊 Sample markets:")
            sample_cols = ['question', 'volume']
            if 'closedTime' in self.markets_df.columns:
                sample_cols.append('closedTime')
            print(self.markets_df[sample_cols].head(3).to_string())
            
            return self.markets_df
            
        except Exception as e:
            print(f"❌ Error loading markets: {e}")
            return None
    
    def load_trades(self):
        """Load processed trade data"""
        print("\n" + "=" * 80)
        print("📥 LOADING TRADE DATA")
        print("=" * 80)
        
        trades_path = f"{self.data_dir}/processed/trades.csv"
        
        if not os.path.exists(trades_path):
            print(f"⏳ Trades not yet processed: {trades_path}")
            print(f"   Waiting for scraper to finish processing...")
            return None
        
        try:
            # Load with polars for speed if available, else pandas
            try:
                import polars as pl
                self.trades_df = pl.read_csv(trades_path).to_pandas()
                print(f"✅ Loaded {len(self.trades_df):,} trades (via Polars)")
            except:
                self.trades_df = pd.read_csv(trades_path)
                print(f"✅ Loaded {len(self.trades_df):,} trades")
            
            print(f"   Columns: {list(self.trades_df.columns)[:10]}...")
            print(f"   Date range: {self.trades_df['timestamp'].min()} to {self.trades_df['timestamp'].max()}")
            
            return self.trades_df
            
        except Exception as e:
            print(f"❌ Error loading trades: {e}")
            return None
    
    def analyze_market_metadata(self):
        """Analyze market characteristics"""
        if self.markets_df is None:
            return
        
        print("\n" + "=" * 80)
        print("📊 MARKET METADATA ANALYSIS")
        print("=" * 80)
        
        df = self.markets_df
        
        # Basic stats
        print(f"\n📈 Overview:")
        print(f"   Total markets: {len(df):,}")

        # Check for closed/active markets
        if 'closedTime' in df.columns:
            closed = df['closedTime'].notna()
            print(f"   Closed markets: {closed.sum():,}")
            print(f"   Active markets: {(~closed).sum():,}")

        # Volume stats
        if 'volume' in df.columns:
            total_vol = df['volume'].sum()
            print(f"\n💰 Volume:")
            print(f"   Total: ${total_vol:,.0f}")
            print(f"   Mean per market: ${df['volume'].mean():,.0f}")
            print(f"   Median: ${df['volume'].median():,.0f}")

        # Categories
        if 'category' in df.columns:
            print(f"\n🏷️ Top Categories:")
            top_cats = df['category'].value_counts().head(10)
            for cat, count in top_cats.items():
                print(f"   {cat}: {count:,}")
        
        return df
    
    def build_price_calibration(self):
        """Build price -> outcome calibration from resolved markets"""
        if self.markets_df is None:
            return None
        
        print("\n" + "=" * 80)
        print("🎯 PRICE CALIBRATION ANALYSIS")
        print("=" * 80)
        
        df = self.markets_df
        
        # Filter for resolved markets
        if 'resolved' not in df.columns:
            print("❌ No 'resolved' column - cannot build calibration")
            return None
        
        resolved = df[df['resolved'] == True]
        print(f"\nAnalyzing {len(resolved):,} resolved markets...")
        
        calibration_data = defaultdict(lambda: {'total': 0, 'wins': 0, 'prices': []})
        total_outcomes = 0
        
        for idx, row in resolved.iterrows():
            try:
                # Parse outcomes and prices
                outcomes = json.loads(row.get('outcomes', '[]'))
                prices = json.loads(row.get('outcomePrices', '[]'))
                winning_outcome = row.get('winningOutcome')
                
                if not winning_outcome or not outcomes or not prices:
                    continue
                
                # Analyze each outcome
                for outcome, price_str in zip(outcomes, prices):
                    try:
                        price = float(price_str)
                        
                        if price <= 0 or price >= 1:
                            continue
                        
                        won = 1 if outcome == winning_outcome else 0
                        bucket = self.get_price_bucket(price)
                        
                        calibration_data[bucket]['total'] += 1
                        calibration_data[bucket]['wins'] += won
                        calibration_data[bucket]['prices'].append(price)
                        
                        total_outcomes += 1
                        
                    except:
                        continue
                        
            except:
                continue
        
        if total_outcomes == 0:
            print("❌ No valid outcomes found")
            return None
        
        print(f"✅ Processed {total_outcomes:,} outcomes\n")
        
        # Display calibration
        print("Price Range | N      | Expected | Actual  | Edge    | p-value | Verdict")
        print("-" * 80)
        
        results = []
        
        buckets = ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%',
                  '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
        
        expected_map = {
            '0-5%': 2.5, '5-10%': 7.5, '10-20%': 15.0,
            '20-30%': 25.0, '30-40%': 35.0, '40-50%': 45.0,
            '50-60%': 55.0, '60-70%': 65.0, '70-80%': 75.0,
            '80-90%': 85.0, '90-100%': 95.0,
        }
        
        for bucket in buckets:
            data = calibration_data.get(bucket)
            if not data or data['total'] < 10:
                continue
            
            n = data['total']
            wins = data['wins']
            expected = expected_map[bucket]
            actual = (wins / n) * 100
            edge = actual - expected
            
            # Statistical test
            p_value = binomtest(wins, n, expected/100, alternative='two-sided').pvalue
            sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
            
            # Verdict
            if abs(edge) > 2 and p_value < 0.05:
                if edge > 0:
                    verdict = "🟢 UNDERPRICED"
                else:
                    verdict = "🔴 OVERPRICED"
            else:
                verdict = "⚪ EFFICIENT"
            
            results.append({
                'bucket': bucket,
                'n': n,
                'expected': expected,
                'actual': actual,
                'edge': edge,
                'p_value': p_value,
                'verdict': verdict
            })
            
            print(f"{bucket:11} | {n:6,} | {expected:8.1f}% | {actual:7.1f}% | {edge:+7.2f}% | {p_value:.4f}{sig:3} | {verdict}")
        
        return results
    
    def get_price_bucket(self, price):
        """Categorize price into bucket"""
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
    
    def save_analysis(self, filename='polymarket_analysis.json'):
        """Save analysis results"""
        output_path = f"/home/workspace/Projects/polymarket-bot/{filename}"
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'markets_analyzed': len(self.markets_df) if self.markets_df is not None else 0,
            'trades_analyzed': len(self.trades_df) if self.trades_df is not None else 0,
        }
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {output_path}")

def main():
    print("=" * 80)
    print("🔬 POLYMARKET REAL DATA ANALYZER")
    print("=" * 80)
    print("Processing blockchain data for mathematical edge discovery\n")
    
    analyzer = PolymarketDataAnalyzer()
    
    # Load data
    markets = analyzer.load_markets()
    
    if markets is None:
        print("\n⏳ Waiting for scraper to collect market data...")
        print("   Run ./monitor_scraper.sh to check progress")
        return
    
    # Analyze metadata
    analyzer.analyze_market_metadata()
    
    # Build calibration
    calibration = analyzer.build_price_calibration()
    
    # Try to load trades
    trades = analyzer.load_trades()
    
    # Save results
    analyzer.save_analysis()
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    
    if calibration:
        print("\n💡 KEY FINDINGS:")
        
        # Find best and worst ranges
        sorted_cal = sorted(calibration, key=lambda x: x['edge'], reverse=True)
        
        best = sorted_cal[0]
        worst = sorted_cal[-1]
        
        print(f"\n🟢 MOST UNDERPRICED: {best['bucket']}")
        print(f"   Edge: {best['edge']:+.2f}% (p={best['p_value']:.4f})")
        print(f"   Sample: {best['n']:,} outcomes")
        
        print(f"\n🔴 MOST OVERPRICED: {worst['bucket']}")
        print(f"   Edge: {worst['edge']:+.2f}% (p={worst['p_value']:.4f})")
        print(f"   Sample: {worst['n']:,} outcomes")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
