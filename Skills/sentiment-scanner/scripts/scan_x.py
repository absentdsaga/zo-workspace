#!/usr/bin/env python3
"""X/Twitter sentiment scanner using Zo's x_search tool.
Scans key CT accounts and trending topics for fresh signals.
Uses the Zo API to call x_search since we don't have direct Twitter API access."""

import json
import os
import sys
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta

TIER1_CALLERS = [
    "MustStopMurad", "RookieXBT", "cometcalls", "thisisdjen", "free_electron0",
    "flooksta", "levigem", "gammichan", "Palgrani2", "_Shadow36"
]

TIER2_ONCHAIN = [
    "W0LF0FCRYPT0", "nofxlines", "sro_cto", "zinceth", "badattrading_"
]

TIER3_CULTURE = [
    "Chubbicorn230", "Ga__ke", "BRADLEYBANNED", "frankdegods", "Agnesrium"
]

ALL_ACCOUNTS = TIER1_CALLERS + TIER2_ONCHAIN + TIER3_CULTURE

SEARCH_QUERIES = [
    "solana memecoin pump",
    "new token launch solana",
    "$SOL trending",
    "polymarket bet prediction",
    "kalshi prediction market",
    "crypto sentiment bullish bearish",
    "memecoin 100x gem",
    "pump.fun trending",
]

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"
MODEL_NAME = "byok:22a22d9b-6586-4137-82dc-c97f9e0efecc"
ZO_API = "https://api.zo.computer/zo/ask"

def get_tier(author: str) -> str:
    handle = author.lstrip("@")
    if handle in TIER1_CALLERS:
        return "tier1_caller"
    elif handle in TIER2_ONCHAIN:
        return "tier2_onchain"
    elif handle in TIER3_CULTURE:
        return "tier3_culture"
    return "unknown"

async def zo_x_search(session: aiohttp.ClientSession, query: str, search_type: str = "search") -> list[dict]:
    """Call Zo's x_search via the /zo/ask API and get structured tweet data back."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("  WARNING: ZO_CLIENT_IDENTITY_TOKEN not set")
        return []

    prompt = f"""Use the x_search tool to search X/Twitter with this query: "{query}"

After getting results, extract ALL tweets/posts and return them as a JSON array. Each item should have:
- "author": the username/handle (without @)
- "text": the full tweet text
- "likes": number of likes (0 if unknown)
- "retweets": number of retweets (0 if unknown)  
- "replies": number of replies (0 if unknown)
- "views": number of views (0 if unknown)
- "tweet_id": the tweet ID if available
- "created_at": when it was posted if available

Return ONLY the JSON array, no other text. If no results, return [].
"""

    try:
        async with session.post(
            ZO_API,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "model_name": MODEL_NAME,
            },
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            if resp.status != 200:
                print(f"  Zo API error: {resp.status}")
                return []
            data = await resp.json()
            output = data.get("output", "")
            
            # Try to parse JSON from output
            if isinstance(output, list):
                return output
            if isinstance(output, str):
                # Find JSON array in the response
                start = output.find("[")
                end = output.rfind("]")
                if start >= 0 and end > start:
                    try:
                        return json.loads(output[start:end+1])
                    except json.JSONDecodeError:
                        pass
            return []
    except Exception as e:
        print(f"  Error calling Zo API: {e}")
        return []

async def scan_accounts_batch(session: aiohttp.ClientSession, accounts: list[str]) -> list[dict]:
    """Scan multiple accounts by batching them into x_search queries."""
    signals = []
    # Batch accounts into groups of 5 for efficiency
    for i in range(0, len(accounts), 5):
        batch = accounts[i:i+5]
        handles = " OR ".join([f"from:{a}" for a in batch])
        query = handles
        print(f"  Scanning batch: {', '.join(batch)}...")
        tweets = await zo_x_search(session, query, "accounts")
        for t in tweets:
            author = t.get("author", "unknown")
            text = t.get("text", "")
            if not text:
                continue
            likes = int(t.get("likes", 0) or 0)
            retweets = int(t.get("retweets", 0) or 0)
            replies = int(t.get("replies", 0) or 0)
            views = int(t.get("views", 0) or 0)
            engagement = likes + retweets * 2 + replies * 3
            tier = get_tier(author)
            if tier == "tier1_caller":
                engagement = int(engagement * 3)
            
            signals.append({
                "platform": "x",
                "author": author,
                "tier": tier,
                "text": text[:500],
                "likes": likes,
                "retweets": retweets,
                "replies": replies,
                "views": views,
                "engagement_score": engagement,
                "engagement_rate": round(engagement / max(views, 1) * 100, 2) if views else 0,
                "tweet_id": str(t.get("tweet_id", "")),
                "url": f"https://x.com/{author}/status/{t.get('tweet_id', '')}" if t.get("tweet_id") else "",
                "created_at": t.get("created_at", ""),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            })
        # Small delay between batches
        await asyncio.sleep(1)
    return signals

async def scan_searches(session: aiohttp.ClientSession) -> list[dict]:
    """Run search queries concurrently."""
    signals = []
    # Run searches with some concurrency control
    semaphore = asyncio.Semaphore(3)
    
    async def search_one(query):
        async with semaphore:
            print(f"  Searching: '{query}'...")
            tweets = await zo_x_search(session, query)
            results = []
            for t in tweets:
                author = t.get("author", "unknown")
                text = t.get("text", "")
                if not text:
                    continue
                likes = int(t.get("likes", 0) or 0)
                retweets = int(t.get("retweets", 0) or 0)
                replies = int(t.get("replies", 0) or 0)
                views = int(t.get("views", 0) or 0)
                engagement = likes + retweets * 2 + replies * 3
                tier = get_tier(author)
                
                results.append({
                    "platform": "x",
                    "author": author,
                    "tier": tier,
                    "text": text[:500],
                    "likes": likes,
                    "retweets": retweets,
                    "replies": replies,
                    "views": views,
                    "engagement_score": engagement,
                    "engagement_rate": round(engagement / max(views, 1) * 100, 2) if views else 0,
                    "tweet_id": str(t.get("tweet_id", "")),
                    "url": f"https://x.com/{author}/status/{t.get('tweet_id', '')}" if t.get("tweet_id") else "",
                    "created_at": t.get("created_at", ""),
                    "scanned_at": datetime.now(timezone.utc).isoformat(),
                })
            return results
    
    tasks = [search_one(q) for q in SEARCH_QUERIES]
    batch_results = await asyncio.gather(*tasks)
    for batch in batch_results:
        signals.extend(batch)
    return signals

async def run_full_scan_async(mode: str = "full") -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "account_signals": [],
        "search_signals": [],
        "trending": [],
        "summary": {}
    }

    async with aiohttp.ClientSession() as session:
        if mode in ("full", "accounts"):
            print(f"Scanning {len(ALL_ACCOUNTS)} CT accounts via Zo x_search...")
            results["account_signals"] = await scan_accounts_batch(session, ALL_ACCOUNTS)

        if mode in ("full", "search"):
            print(f"\nRunning {len(SEARCH_QUERIES)} search queries...")
            results["search_signals"] = await scan_searches(session)

    # Deduplicate by tweet_id
    seen_ids = set()
    deduped_account = []
    for s in results["account_signals"]:
        tid = s.get("tweet_id")
        if tid and tid in seen_ids:
            continue
        if tid:
            seen_ids.add(tid)
        deduped_account.append(s)
    results["account_signals"] = deduped_account
    
    deduped_search = []
    for s in results["search_signals"]:
        tid = s.get("tweet_id")
        if tid and tid in seen_ids:
            continue
        if tid:
            seen_ids.add(tid)
        deduped_search.append(s)
    results["search_signals"] = deduped_search

    total = len(results["account_signals"]) + len(results["search_signals"])
    results["summary"] = {
        "total_signals": total,
        "account_signals": len(results["account_signals"]),
        "search_signals": len(results["search_signals"]),
        "high_engagement": len([s for s in results["account_signals"] + results["search_signals"]
                               if s.get("engagement_score", 0) > 100]),
        "tier1_signals": len([s for s in results["account_signals"]
                             if s.get("tier") == "tier1_caller"]),
    }

    outfile = os.path.join(DATA_DIR, f"x_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {outfile}")
    print(f"Total signals: {total} | High engagement: {results['summary']['high_engagement']} | Tier1: {results['summary']['tier1_signals']}")

    return results

def run_full_scan(mode: str = "full") -> dict:
    return asyncio.run(run_full_scan_async(mode))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    run_full_scan(mode)
