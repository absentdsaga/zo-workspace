#!/usr/bin/env python3
"""
Paper Trading Bot: 80-95% FAVORITES Strategy
Based on comprehensive analysis: +7.4% edge from 3,497 resolved markets
VALIDATED EDGE: 92.4% actual vs 85% expected (p < 0.001)
OPPORTUNITY RICH: 9 current opportunities vs 0 in other positive-edge ranges
"""

import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# Strategy parameters (from 41,243 market comprehensive analysis)
PRICE_MIN = 0.80
PRICE_MAX = 0.95
WIN_RATE = 0.924  # 92.4% actual win rate (3,497 markets in 80-90% range)
EXPECTED_RATE = 0.875  # Market-implied from 80-95% range midpoint
EDGE = 0.074  # +7.4% edge (highly significant, p < 0.001)
KELLY_FRACTION = 0.25  # Quarter Kelly for safety
MAX_BET_PCT = 0.05  # Max 5% of bankroll per bet
MIN_VOLUME = 50000  # $50k minimum volume
STARTING_BANKROLL = 1000
MAX_POSITIONS_PER_MARKET = 2  # Max positions per unique market (for diversification)

# TIER 1 LIQUIDITY CRISIS FIXES
MAX_DAYS_TO_RESOLUTION = 14  # Only trade markets resolving in ≤14 days
MIN_VOLUME_24HR = 1000  # Minimum $1k volume in last 24 hours (lowered to capture more opps)

# Files
POSITIONS_FILE = "paper_positions_80_95.json"
STATS_FILE = "paper_stats_80_95.json"
LOG_FILE = "paper_bot_80_95.log"

class PaperTradingBot:
    def __init__(self):
        self.bankroll = STARTING_BANKROLL
        self.positions = self.load_positions()
        self.stats = self.load_stats()

    def load_positions(self):
        """Load existing positions from file"""
        if Path(POSITIONS_FILE).exists():
            with open(POSITIONS_FILE) as f:
                return json.load(f)
        return {"open": [], "closed": []}

    def save_positions(self):
        """Save positions to file"""
        with open(POSITIONS_FILE, "w") as f:
            json.dump(self.positions, f, indent=2)

    def load_stats(self):
        """Load trading statistics"""
        if Path(STATS_FILE).exists():
            with open(STATS_FILE) as f:
                return json.load(f)
        return {
            "starting_bankroll": STARTING_BANKROLL,
            "current_bankroll": STARTING_BANKROLL,
            "total_bets": 0,
            "wins": 0,
            "losses": 0,
            "total_wagered": 0,
            "total_profit": 0,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

    def save_stats(self):
        """Save statistics to file"""
        self.stats["current_bankroll"] = self.bankroll
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=2)

    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(LOG_FILE, "a") as f:
            f.write(log_line + "\n")

    def fetch_markets(self):
        """Fetch active markets from Polymarket"""
        try:
            # Gamma API endpoint for active markets
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                "closed": "false",
                "limit": 100
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"❌ Error fetching markets: {e}")
            return []

    def calculate_bet_size(self, price):
        """Calculate optimal bet size using Kelly criterion"""
        # Kelly: f = (bp - q) / b
        # where b = odds, p = true win rate, q = 1-p
        b = (1 / price) - 1
        p = WIN_RATE
        q = 1 - WIN_RATE
        kelly = (b * p - q) / b
        kelly = max(0, kelly)

        # Use quarter Kelly for safety
        optimal_bet = self.bankroll * kelly * KELLY_FRACTION

        # Cap at max bet percentage
        max_bet = self.bankroll * MAX_BET_PCT

        return min(optimal_bet, max_bet)

    def calculate_ev(self, price):
        """Calculate expected value of a bet"""
        cost = price
        win_payout = 1.0
        loss = -price

        ev = WIN_RATE * (win_payout - cost) + (1 - WIN_RATE) * loss
        return ev

    def filter_markets(self, markets):
        """Filter markets for 30-40¢ opportunities"""
        opportunities = []

        # Count existing positions per market (for position limits)
        market_position_counts = {}
        for pos in self.positions["open"]:
            question = pos.get("question")
            market_position_counts[question] = market_position_counts.get(question, 0) + 1

        for market in markets:
            try:
                # Get market details
                condition_id = market.get("conditionId")
                question = market.get("question", "")

                # Check position limit per market
                if market_position_counts.get(question, 0) >= MAX_POSITIONS_PER_MARKET:
                    continue  # Skip markets where we already have max positions

                # TIER 1 FILTER #1: Check days to resolution
                end_date_str = market.get("endDate")
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                        days_to_resolution = (end_date - datetime.now(timezone.utc)).days
                        if days_to_resolution > MAX_DAYS_TO_RESOLUTION:
                            continue  # Skip long-dated markets
                    except:
                        pass  # If we can't parse date, skip this filter

                # Parse outcomes and prices (they're JSON strings in the API)
                outcomes_str = market.get("outcomes", "[]")
                prices_str = market.get("outcomePrices", "[]")
                tokens_str = market.get("clobTokenIds", "[]")

                outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
                prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
                tokens = json.loads(tokens_str) if isinstance(tokens_str, str) else tokens_str

                volume = float(market.get("volume", 0))
                volume_24hr = float(market.get("volume24hr", 0))

                # TIER 1 FILTER #2: Check 24hr volume
                if volume_24hr < MIN_VOLUME_24HR:
                    continue  # Skip markets with low recent activity

                # Skip if no outcomes
                if not outcomes or len(outcomes) < 2:
                    continue

                # Check each outcome
                for i, outcome_name in enumerate(outcomes):
                    if i >= len(prices) or i >= len(tokens):
                        continue

                    price = float(prices[i])
                    token_id = tokens[i]

                    # Filter criteria
                    if (PRICE_MIN <= price <= PRICE_MAX and
                        volume >= MIN_VOLUME and
                        token_id):

                        # Calculate bet metrics
                        bet_size = self.calculate_bet_size(price)
                        ev = self.calculate_ev(price)
                        roi = (ev / price) * 100

                        opportunities.append({
                            "condition_id": condition_id,
                            "token_id": token_id,
                            "question": question,
                            "outcome": outcome_name,
                            "price": price,
                            "volume": volume,
                            "bet_size": bet_size,
                            "ev": ev,
                            "roi": roi
                        })

            except Exception as e:
                self.log(f"⚠️  Error processing market: {e}")
                continue

        # Sort by EV (highest first)
        return sorted(opportunities, key=lambda x: x["ev"], reverse=True)

    def place_bet(self, opportunity):
        """Place a paper trade bet"""
        bet_size = opportunity["bet_size"]
        price = opportunity["price"]
        cost = bet_size * price

        # Check if we have enough bankroll
        if cost > self.bankroll:
            self.log(f"⚠️  Insufficient bankroll for bet (need ${cost:.2f}, have ${self.bankroll:.2f})")
            return False

        # Create position
        position = {
            "condition_id": opportunity["condition_id"],
            "token_id": opportunity["token_id"],
            "question": opportunity["question"],
            "outcome": opportunity["outcome"],
            "price": price,
            "bet_size": bet_size,
            "cost": cost,
            "potential_win": bet_size,
            "ev": opportunity["ev"],
            "roi": opportunity["roi"],
            "placed_at": datetime.now(timezone.utc).isoformat(),
            "status": "open"
        }

        # Update bankroll
        self.bankroll -= cost

        # Add to open positions
        self.positions["open"].append(position)
        self.save_positions()

        # Update stats
        self.stats["total_bets"] += 1
        self.stats["total_wagered"] += cost
        self.save_stats()

        self.log(f"📊 PAPER BET PLACED:")
        self.log(f"   Question: {opportunity['question']}")
        self.log(f"   Outcome: {opportunity['outcome']}")
        self.log(f"   Price: {price*100:.1f}¢")
        self.log(f"   Size: ${bet_size:.2f}")
        self.log(f"   Cost: ${cost:.2f}")
        self.log(f"   EV: ${opportunity['ev']:+.4f}")
        self.log(f"   ROI: {opportunity['roi']:+.1f}%")
        self.log(f"   Bankroll: ${self.bankroll:.2f}")

        return True

    def get_current_price(self, token_id):
        """Get current market price from Gamma API (most reliable)"""
        try:
            # Use Gamma API which has real-time accurate prices
            url = f"https://gamma-api.polymarket.com/markets?clob_token_ids={token_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                markets = response.json()
                if markets and len(markets) > 0:
                    market = markets[0]

                    # Parse outcomes and prices
                    tokens_str = market.get("clobTokenIds", "[]")
                    prices_str = market.get("outcomePrices", "[]")

                    tokens = json.loads(tokens_str) if isinstance(tokens_str, str) else tokens_str
                    prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str

                    # Find the price for this specific token
                    for i, tid in enumerate(tokens):
                        if tid == token_id and i < len(prices):
                            return float(prices[i])
        except Exception as e:
            pass
        return None

    def calculate_unrealized_pnl(self):
        """Calculate unrealized P&L for all open positions"""
        total_cost = 0
        total_value = 0

        for pos in self.positions["open"]:
            if pos.get("cost", 0) == 0:
                continue

            cost = pos["cost"]
            bet_size = pos["bet_size"]

            # Get current market price
            current_price = self.get_current_price(pos["token_id"])

            if current_price is not None:
                current_value = bet_size * current_price
                pos["current_price"] = current_price
                pos["current_value"] = current_value
                pos["unrealized_pnl"] = current_value - cost
            else:
                # If no price available, use entry price as estimate
                current_value = cost
                pos["current_price"] = pos["price"]
                pos["current_value"] = cost
                pos["unrealized_pnl"] = 0

            total_cost += cost
            total_value += current_value

        return {
            "total_cost": total_cost,
            "total_value": total_value,
            "total_pnl": total_value - total_cost,
            "pnl_pct": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        }

    def check_resolutions(self):
        """Check if any open positions have resolved"""
        if not self.positions["open"]:
            return

        self.log("🔍 Checking for market resolutions...")

        for position in self.positions["open"][:]:  # Copy list to modify during iteration
            try:
                # Query market status
                url = f"https://gamma-api.polymarket.com/markets/{position['condition_id']}"
                response = requests.get(url, timeout=10)

                if response.status_code != 200:
                    continue

                market = response.json()

                # Check if market is closed
                if market.get("closed", False):
                    # Check which outcome won
                    outcomes = market.get("outcomes", [])
                    winning_outcome = None

                    for outcome in outcomes:
                        if outcome.get("winner", False):
                            winning_outcome = outcome.get("outcome")
                            break

                    if winning_outcome:
                        self.resolve_position(position, winning_outcome)

            except Exception as e:
                self.log(f"⚠️  Error checking resolution for {position['question']}: {e}")
                continue

    def resolve_position(self, position, winning_outcome):
        """Resolve a position as win or loss"""
        won = (position["outcome"] == winning_outcome)

        if won:
            profit = position["bet_size"] - position["cost"]
            self.bankroll += position["bet_size"]
            self.stats["wins"] += 1
            self.stats["total_profit"] += profit

            self.log(f"✅ WIN: {position['question']}")
            self.log(f"   Outcome: {position['outcome']}")
            self.log(f"   Profit: ${profit:+.2f}")
            self.log(f"   Bankroll: ${self.bankroll:.2f}")
        else:
            loss = position["cost"]
            self.stats["losses"] += 1
            self.stats["total_profit"] -= loss

            self.log(f"❌ LOSS: {position['question']}")
            self.log(f"   Outcome: {position['outcome']} (Won: {winning_outcome})")
            self.log(f"   Loss: ${loss:.2f}")
            self.log(f"   Bankroll: ${self.bankroll:.2f}")

        # Move to closed positions
        position["resolved_at"] = datetime.now(timezone.utc).isoformat()
        position["won"] = won
        position["winning_outcome"] = winning_outcome
        position["status"] = "won" if won else "lost"

        self.positions["open"].remove(position)
        self.positions["closed"].append(position)
        self.save_positions()
        self.save_stats()

    def print_status(self):
        """Print current bot status"""
        closed = self.positions["closed"]
        open_count = len(self.positions["open"])

        # Calculate unrealized P&L
        pnl_data = self.calculate_unrealized_pnl()

        print("\n" + "=" * 80)
        print(f"📊 PAPER TRADING STATUS ({PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}% Favorites Strategy)")
        print("=" * 80)

        # True bankroll = free cash + position value
        true_bankroll = self.bankroll + pnl_data["total_value"]
        true_pnl = true_bankroll - STARTING_BANKROLL
        true_pnl_pct = (true_pnl / STARTING_BANKROLL) * 100

        print(f"\n💰 Bankroll:")
        print(f"   Free Cash: ${self.bankroll:.2f}")
        print(f"   Position Value: ${pnl_data['total_value']:.2f}")
        print(f"   TRUE BANKROLL: ${true_bankroll:.2f} (started: ${STARTING_BANKROLL})")
        print(f"   TRUE P&L: ${true_pnl:+.2f} ({true_pnl_pct:+.1f}%)")

        print(f"\n📈 Open Positions: {open_count}")

        if open_count > 0:
            print(f"   Total Cost: ${pnl_data['total_cost']:.2f}")
            print(f"   Current Value: ${pnl_data['total_value']:.2f}")
            print(f"   Unrealized P&L: ${pnl_data['total_pnl']:+.2f} ({pnl_data['pnl_pct']:+.1f}%)")

        if closed:
            wins = self.stats["wins"]
            losses = self.stats["losses"]
            total = wins + losses
            win_rate = (wins / total * 100) if total > 0 else 0

            print(f"\n📊 Closed Positions: {total}")
            print(f"   Wins: {wins}")
            print(f"   Losses: {losses}")
            print(f"   Win rate: {win_rate:.1f}% (expected: {WIN_RATE*100:.1f}%)")
            print(f"   Total profit: ${self.stats['total_profit']:+.2f}")

            # Check if win rate matches expectation
            if total >= 20:  # Only check after sufficient sample size
                if win_rate < (WIN_RATE * 100 - 10):  # 10% tolerance
                    print(f"\n⚠️  WIN RATE BELOW EXPECTED! ({win_rate:.1f}% vs {WIN_RATE*100:.1f}%)")
                    print("   Edge may not be holding - consider stopping")
                elif win_rate >= (WIN_RATE * 100 - 5):  # Within 5%
                    print(f"\n✅ Win rate tracking expected ({win_rate:.1f}% vs {WIN_RATE*100:.1f}%)")

        print("\n" + "=" * 80 + "\n")

    def run(self):
        """Main bot loop"""
        self.log("🚀 Starting Paper Trading Bot (80-95% FAVORITES STRATEGY)")
        self.log(f"   Starting bankroll: ${STARTING_BANKROLL}")
        self.log(f"   Target range: {PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}%")
        self.log(f"   Expected win rate: {WIN_RATE*100:.1f}% (from 3,497 markets)")
        self.log(f"   Expected edge: +{EDGE*100:.1f}%")
        self.log(f"   Statistical significance: p < 0.001 (highly significant)")
        self.log(f"")
        self.log(f"🔒 TIER 1 LIQUIDITY FILTERS:")
        self.log(f"   ✅ Max days to resolution: {MAX_DAYS_TO_RESOLUTION} days")
        self.log(f"   ✅ Min 24hr volume: ${MIN_VOLUME_24HR:,}")
        self.log(f"")
        self.log(f"📊 WHY FAVORITES:")
        self.log(f"   • People overestimate upset risk ('anything can happen')")
        self.log(f"   • 80-90% range: 92.4% actual vs 85% expected")
        self.log(f"   • 9 opportunities available NOW vs 0 in 40-50%")
        self.log(f"   • Lower variance = capital preservation")
        self.log("")

        try:
            while True:
                self.print_status()

                # Update unrealized P&L and save positions
                self.calculate_unrealized_pnl()
                self.save_positions()

                # Check for resolutions
                self.check_resolutions()

                # Fetch new opportunities
                self.log("🔍 Scanning for opportunities...")
                markets = self.fetch_markets()

                if not markets:
                    self.log("⚠️  No markets fetched, waiting...")
                    time.sleep(60)
                    continue

                opportunities = self.filter_markets(markets)

                if opportunities:
                    self.log(f"✅ Found {len(opportunities)} opportunities in {PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}¢ range")

                    # Take best opportunity if we have bankroll
                    best = opportunities[0]
                    if best["bet_size"] * best["price"] <= self.bankroll:
                        self.place_bet(best)
                    else:
                        self.log(f"⚠️  Best opportunity requires ${best['bet_size'] * best['price']:.2f}, but bankroll is ${self.bankroll:.2f}")
                else:
                    self.log(f"❌ No opportunities in {PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}¢ range")

                # Wait before next scan
                self.log("⏰ Waiting 5 minutes before next scan...\n")
                time.sleep(300)  # 5 minutes

        except KeyboardInterrupt:
            self.log("\n🛑 Bot stopped by user")
            self.print_status()

if __name__ == "__main__":
    bot = PaperTradingBot()
    bot.run()
