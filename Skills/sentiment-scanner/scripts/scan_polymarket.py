#!/usr/bin/env python3
"""Polymarket scanner — finds active markets with potential sentiment edges.
Focuses on markets where odds < 30% (cheap bets with upside multiples)
and markets with recent volume spikes indicating smart money movement."""

import requests
import json
import os
import sys
from datetime import datetime, timezone, timedelta

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

INTERESTING_TAGS = [
    "Politics", "Crypto", "AI", "Elections", "U.S. Politics",
    "Trump", "Geopolitics", "Finance", "Technology", "Culture",
    "Sports", "Entertainment", "Science"
]

def fetch_active_markets(limit: int = 100, offset: int = 0) -> list[dict]:
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={
                "limit": limit,
                "offset": offset,
                "active": "true",
                "closed": "false",
                "order": "volume24hr",
                "ascending": "false",
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

def fetch_market_events(limit: int = 50) -> list[dict]:
    try:
        resp = requests.get(
            f"{GAMMA_API}/events",
            params={
                "limit": limit,
                "active": "true",
                "closed": "false",
                "order": "volume24hr",
                "ascending": "false",
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def analyze_market(market: dict) -> dict | None:
    question = market.get("question", "")
    desc = market.get("description", "")[:300]
    slug = market.get("slug", market.get("market_slug", ""))

    outcomes = market.get("outcomePrices", market.get("outcomes", ""))
    if isinstance(outcomes, str):
        try:
            outcomes = json.loads(outcomes)
        except:
            outcomes = []

    volume_24h = float(market.get("volume24hr", 0) or 0)
    total_volume = float(market.get("volume", 0) or 0)
    liquidity = float(market.get("liquidity", 0) or 0)

    end_date = market.get("endDate", market.get("end_date_iso", ""))
    tags = market.get("tags", [])

    # Parse prices
    prices = []
    if isinstance(outcomes, list):
        for p in outcomes:
            try:
                prices.append(float(p))
            except (ValueError, TypeError):
                pass

    # Find cheap YES outcomes (< 30 cents = >3.3x payout potential)
    cheap_outcomes = []
    outcome_labels = market.get("outcomes", [])
    if isinstance(outcome_labels, str):
        try:
            outcome_labels = json.loads(outcome_labels)
        except:
            outcome_labels = []

    for i, price in enumerate(prices):
        if 0.01 < price < 0.30:
            label = outcome_labels[i] if i < len(outcome_labels) else f"Outcome {i}"
            payout_multiple = round(1 / price, 1) if price > 0 else 0
            cheap_outcomes.append({
                "outcome": label,
                "price": price,
                "implied_probability": f"{price*100:.1f}%",
                "payout_multiple": f"{payout_multiple}x",
            })

    if not cheap_outcomes and not volume_24h > 50000:
        return None

    # Volume spike detection
    volume_ratio = volume_24h / max(total_volume / 30, 1) if total_volume > 0 else 0

    return {
        "platform": "polymarket",
        "question": question,
        "description": desc,
        "slug": slug,
        "url": f"https://polymarket.com/event/{slug}" if slug else "",
        "volume_24h": volume_24h,
        "total_volume": total_volume,
        "liquidity": liquidity,
        "volume_spike_ratio": round(volume_ratio, 2),
        "cheap_outcomes": cheap_outcomes,
        "tags": tags if isinstance(tags, list) else [],
        "end_date": end_date,
        "prices": prices,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }

def run_scan(max_markets: int = 200) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "markets_with_edge": [],
        "volume_spike_markets": [],
        "summary": {}
    }

    print(f"Fetching up to {max_markets} active Polymarket markets...")
    all_markets = []
    for offset in range(0, max_markets, 100):
        batch = fetch_active_markets(limit=100, offset=offset)
        if not batch:
            break
        all_markets.extend(batch)
        print(f"  Fetched {len(all_markets)} markets so far...")

    print(f"Analyzing {len(all_markets)} markets...")
    for market in all_markets:
        analysis = analyze_market(market)
        if analysis is None:
            continue

        if analysis["cheap_outcomes"]:
            results["markets_with_edge"].append(analysis)

        if analysis["volume_spike_ratio"] > 3.0:
            results["volume_spike_markets"].append(analysis)

    # Sort by volume
    results["markets_with_edge"].sort(key=lambda x: x["volume_24h"], reverse=True)
    results["volume_spike_markets"].sort(key=lambda x: x["volume_spike_ratio"], reverse=True)

    results["summary"] = {
        "total_scanned": len(all_markets),
        "markets_with_cheap_outcomes": len(results["markets_with_edge"]),
        "volume_spike_markets": len(results["volume_spike_markets"]),
        "top_5_edge": [
            {
                "question": m["question"][:100],
                "best_cheap": m["cheap_outcomes"][0] if m["cheap_outcomes"] else None,
                "volume_24h": m["volume_24h"],
            }
            for m in results["markets_with_edge"][:5]
        ]
    }

    outfile = os.path.join(DATA_DIR, f"polymarket_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved to {outfile}")
    print(f"Markets with cheap outcomes (<30¢): {len(results['markets_with_edge'])}")
    print(f"Volume spike markets (>3x avg): {len(results['volume_spike_markets'])}")

    if results["markets_with_edge"]:
        print("\n--- TOP OPPORTUNITIES ---")
        for m in results["markets_with_edge"][:10]:
            print(f"\n{m['question'][:80]}")
            print(f"  24h vol: ${m['volume_24h']:,.0f} | Liquidity: ${m['liquidity']:,.0f}")
            for o in m["cheap_outcomes"][:3]:
                print(f"  → {o['outcome']}: {o['implied_probability']} ({o['payout_multiple']} payout)")

    return results

if __name__ == "__main__":
    max_m = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    run_scan(max_m)
