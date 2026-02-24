#!/usr/bin/env python3
"""
Paper Trading Bot: 30-40¢ Strategy
Based on per-market calibration: +14% edge from 96 resolved markets
"""

import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# Strategy parameters (from per-market calibration)
PRICE_MIN = 0.30
PRICE_MAX = 0.40
WIN_RATE = 0.49  # 49% actual vs 35% expected
EDGE = 0.14  # +14% edge
KELLY_FRACTION = 0.25  # Quarter Kelly for safety
MAX_BET_PCT = 0.05  # Max 5% of bankroll per bet
MIN_VOLUME = 50000  # $50k minimum volume
STARTING_BANKROLL = 1000
MAX_POSITIONS_PER_MARKET = 2  # Max positions per unique market (for diversification)

# TIER 1 LIQUIDITY CRISIS FIXES
MAX_DAYS_TO_RESOLUTION = 14  # Only trade markets resolving in ≤14 days
MIN_VOLUME_24HR = 5000  # Minimum $5k volume in last 24 hours

# Files
POSITIONS_FILE = "paper_positions_30_40.json"
STATS_FILE = "paper_stats_30_40.json"
LOG_FILE = "paper_bot_30_40.log"

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

        print("\n" + "=" * 80)
        print("📊 PAPER TRADING STATUS (30-40¢ Strategy)")
        print("=" * 80)
        print(f"\n💰 Bankroll: ${self.bankroll:.2f} (started: ${STARTING_BANKROLL})")
        print(f"   P&L: ${self.bankroll - STARTING_BANKROLL:+.2f} ({(self.bankroll/STARTING_BANKROLL - 1)*100:+.1f}%)")
        print(f"\n📈 Open Positions: {open_count}")

        if open_count > 0:
            total_exposure = sum(p["cost"] for p in self.positions["open"])
            print(f"   Total exposure: ${total_exposure:.2f}")

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
        self.log("🚀 Starting Paper Trading Bot (30-40¢ Strategy) - TIER 1 FILTERS ACTIVE")
        self.log(f"   Starting bankroll: ${STARTING_BANKROLL}")
        self.log(f"   Target range: {PRICE_MIN*100:.0f}-{PRICE_MAX*100:.0f}¢")
        self.log(f"   Expected edge: +{EDGE*100:.1f}%")
        self.log(f"   Expected win rate: {WIN_RATE*100:.1f}%")
        self.log(f"   Based on: 96 resolved markets (per-market analysis)")
        self.log(f"")
        self.log(f"🔒 TIER 1 LIQUIDITY FILTERS:")
        self.log(f"   ✅ Max days to resolution: {MAX_DAYS_TO_RESOLUTION} days")
        self.log(f"   ✅ Min 24hr volume: ${MIN_VOLUME_24HR:,}")
        self.log("")

        try:
            while True:
                self.print_status()

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
