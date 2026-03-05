#!/usr/bin/env python3
"""Kalshi scanner — finds active markets with underpriced outcomes.
Free API, no auth needed for reading market data."""

import requests
import json
import os
import sys
from datetime import datetime, timezone

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"
KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"

def fetch_events(limit: int = 50, cursor: str = None) -> tuple[list[dict], str | None]:
    params = {"limit": limit, "status": "open"}
    if cursor:
        params["cursor"] = cursor
    try:
        resp = requests.get(f"{KALSHI_API}/events", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("events", []), data.get("cursor", None)
    except Exception as e:
        print(f"Error fetching events: {e}")
        return [], None

def fetch_markets(event_ticker: str = None, series_ticker: str = None,
                  status: str = "open", limit: int = 100, cursor: str = None) -> tuple[list[dict], str | None]:
    params = {"limit": limit, "status": status}
    if event_ticker:
        params["event_ticker"] = event_ticker
    if series_ticker:
        params["series_ticker"] = series_ticker
    if cursor:
        params["cursor"] = cursor
    try:
        resp = requests.get(f"{KALSHI_API}/markets", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("markets", []), data.get("cursor", None)
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return [], None

def analyze_market(market: dict) -> dict | None:
    ticker = market.get("ticker", "")
    title = market.get("title", market.get("subtitle", ""))
    event_ticker = market.get("event_ticker", "")
    yes_bid = market.get("yes_bid", 0) or 0
    yes_ask = market.get("yes_ask", 0) or 0
    no_bid = market.get("no_bid", 0) or 0
    no_ask = market.get("no_ask", 0) or 0
    volume = market.get("volume", 0) or 0
    volume_24h = market.get("volume_24h", 0) or 0
    open_interest = market.get("open_interest", 0) or 0
    last_price = market.get("last_price", 0) or 0
    liquidity = market.get("liquidity", 0) or 0

    yes_mid = (yes_bid + yes_ask) / 2 if yes_ask > 0 else last_price
    no_mid = (no_bid + no_ask) / 2 if no_ask > 0 else (100 - last_price)

    cheap_sides = []
    if 1 < yes_mid < 30:
        payout = round(100 / yes_mid, 1) if yes_mid > 0 else 0
        cheap_sides.append({
            "side": "YES",
            "price_cents": yes_mid,
            "implied_probability": f"{yes_mid:.0f}%",
            "payout_multiple": f"{payout}x",
        })
    if 1 < no_mid < 30:
        payout = round(100 / no_mid, 1) if no_mid > 0 else 0
        cheap_sides.append({
            "side": "NO",
            "price_cents": no_mid,
            "implied_probability": f"{no_mid:.0f}%",
            "payout_multiple": f"{payout}x",
        })

    if not cheap_sides and volume_24h < 5000:
        return None

    return {
        "platform": "kalshi",
        "ticker": ticker,
        "title": title,
        "event_ticker": event_ticker,
        "url": f"https://kalshi.com/markets/{ticker.lower()}" if ticker else "",
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "no_bid": no_bid,
        "no_ask": no_ask,
        "yes_mid": yes_mid,
        "no_mid": no_mid,
        "volume": volume,
        "volume_24h": volume_24h,
        "open_interest": open_interest,
        "last_price": last_price,
        "liquidity": liquidity,
        "cheap_sides": cheap_sides,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }

def run_scan(max_markets: int = 500) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "markets_with_edge": [],
        "high_volume_markets": [],
        "summary": {}
    }

    print(f"Fetching active Kalshi markets...")
    all_markets = []
    cursor = None
    while len(all_markets) < max_markets:
        batch, cursor = fetch_markets(status="open", limit=100, cursor=cursor)
        if not batch:
            break
        all_markets.extend(batch)
        print(f"  Fetched {len(all_markets)} markets...")
        if not cursor:
            break

    print(f"Analyzing {len(all_markets)} markets...")
    for market in all_markets:
        analysis = analyze_market(market)
        if analysis is None:
            continue

        if analysis["cheap_sides"]:
            results["markets_with_edge"].append(analysis)

        if analysis["volume_24h"] > 10000:
            results["high_volume_markets"].append(analysis)

    results["markets_with_edge"].sort(key=lambda x: x["volume_24h"], reverse=True)
    results["high_volume_markets"].sort(key=lambda x: x["volume_24h"], reverse=True)

    results["summary"] = {
        "total_scanned": len(all_markets),
        "markets_with_cheap_outcomes": len(results["markets_with_edge"]),
        "high_volume_markets": len(results["high_volume_markets"]),
    }

    outfile = os.path.join(DATA_DIR, f"kalshi_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved to {outfile}")
    print(f"Markets with cheap outcomes (<30¢): {len(results['markets_with_edge'])}")
    print(f"High volume markets: {len(results['high_volume_markets'])}")

    if results["markets_with_edge"]:
        print("\n--- TOP KALSHI OPPORTUNITIES ---")
        for m in results["markets_with_edge"][:10]:
            print(f"\n{m['title'][:80]}")
            print(f"  YES mid: {m['yes_mid']}¢ | NO mid: {m['no_mid']}¢ | Vol 24h: {m['volume_24h']}")
            for s in m["cheap_sides"]:
                print(f"  → {s['side']}: {s['implied_probability']} ({s['payout_multiple']} payout)")

    return results

if __name__ == "__main__":
    run_scan()
