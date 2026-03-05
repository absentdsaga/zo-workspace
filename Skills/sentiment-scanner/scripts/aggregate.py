#!/usr/bin/env python3
"""Signal aggregator — combines all platform scans into ranked signals.
Cross-references social sentiment with prediction market odds to find edges.

Improved cross-referencing:
1. Extracts specific entities (tokens, people, events) from social signals
2. Extracts core topics from prediction market questions
3. Uses multi-term matching with partial overlap scoring
4. Tracks raw tweet/post text for context in the output
"""

import json
import os
import glob
import re
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"
OUTPUT_DIR = "/home/workspace/Skills/sentiment-scanner/data/signals"

# Common words to ignore when matching
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "will", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "but", "and", "or", "if", "in",
    "on", "at", "to", "for", "of", "with", "by", "from", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "up", "down", "out",
    "off", "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "just", "should", "now", "what", "which",
    "who", "whom", "this", "that", "these", "those", "its", "my", "your", "his",
    "her", "their", "our", "it", "he", "she", "we", "they", "me", "him", "us",
    "about", "price", "market", "will", "reach", "end", "year", "month", "day",
    "yes", "no", "win", "lose", "above", "below", "over", "under", "before",
    "after", "next", "last", "first", "new", "many", "much", "get", "got",
    "make", "made", "like", "know", "think", "take", "come", "could", "would",
    "may", "might", "shall", "must",
}

# Generic keywords that shouldn't be used for market matching
GENERIC_CRYPTO_KEYWORDS = {
    "pump", "moon", "bullish", "bearish", "dump", "rug",
    "launch", "listing", "airdrop", "narrative", "meta",
    "trend", "viral", "breakout", "100x", "gem", "degen",
    "memecoin", "memecoins", "crypto", "defi", "web3",
    "altcoin", "trading", "trader", "token", "coin",
    # These are too generic / match too many markets as substrings
    "sol", "solana", "eth", "btc", "ai", "bet", "prediction",
    "polymarket", "kalshi", "market", "price", "buy", "sell",
    "one", "two", "three", "four", "five", "six", "sec", "day",
    "top", "big", "run", "win", "hit", "set", "put", "call",
    "high", "low", "long", "short", "next", "last", "real",
    "best", "free", "good", "bad", "hot", "old", "new",
    "war", "ban", "nfl", "nba", "fed", "gdp", "cpi",
    "etf", "doge", "pepe", "shiba", "bonk", "wif", "jup",
}

def load_latest_scan(prefix: str) -> dict | None:
    pattern = os.path.join(DATA_DIR, f"{prefix}_scan_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return None
    cutoff = datetime.now() - timedelta(hours=2)
    for f in files:
        try:
            ts_str = os.path.basename(f).replace(f"{prefix}_scan_", "").replace(".json", "")
            # Strip _transcribed suffix if present
            ts_str = ts_str.replace("_transcribed", "")
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            if ts > cutoff:
                with open(f) as fh:
                    return json.load(fh)
        except (ValueError, json.JSONDecodeError):
            continue
    if files:
        with open(files[0]) as f:
            return json.load(f)
    return None

def extract_entities_from_text(text: str) -> dict:
    """Extract meaningful entities from text for cross-referencing."""
    entities = {
        "tokens": [],      # $BTC, $SOL, etc
        "names": [],        # Proper nouns, people, companies
        "topics": [],       # Key topic phrases
    }
    if not text:
        return entities
    
    # Extract $TOKEN mentions
    tokens = re.findall(r'\$([A-Z]{2,10})', text)
    entities["tokens"] = list(set(tokens))
    
    # Extract @mentions
    mentions = re.findall(r'@(\w+)', text)
    entities["names"].extend(mentions)
    
    # Extract capitalized proper nouns (2+ chars, not all-caps noise)
    words = text.split()
    for word in words:
        clean = re.sub(r'[^a-zA-Z]', '', word)
        if (len(clean) >= 3 and clean[0].isupper() and not clean.isupper()
                and clean.lower() not in STOP_WORDS 
                and clean.lower() not in GENERIC_CRYPTO_KEYWORDS):
            entities["names"].append(clean)
    
    # Extract key topic phrases: known entities
    known_entities = [
        "bitcoin", "ethereum", "solana",
        "trump", "biden", "elon musk", "spacex", "tesla",
        "polymarket", "kalshi", "fomc", "inflation",
        "interest rate", "rate cut", "rate hike",
        "election", "congress", "senate",
        "gensler", "blackrock", "spot etf",
        "openai", "chatgpt", "nvidia",
        "super bowl", "olympics", "world cup",
        "ukraine", "russia", "taiwan", "iran", "israel",
        "tariff", "trade war",
        "recession", "unemployment", "jobs report",
        "spx6900", "dogecoin",
        "raydium", "jupiter",
    ]
    text_lower = text.lower()
    for entity in known_entities:
        if entity in text_lower:
            entities["topics"].append(entity)
    
    entities["names"] = list(set(entities["names"]))
    entities["topics"] = list(set(entities["topics"]))
    
    return entities

def extract_market_keywords(question: str, description: str = "") -> set[str]:
    """Extract meaningful keywords from a prediction market question."""
    combined = (question + " " + description).lower()
    
    # First check for known entities
    known_matches = set()
    known_entities = [
        "bitcoin", "ethereum", "solana",
        "trump", "biden", "elon musk", "spacex", "tesla",
        "polymarket", "kalshi", "fomc", "inflation",
        "interest rate", "rate cut", "rate hike",
        "election", "congress", "senate",
        "gensler", "blackrock", "spot etf",
        "openai", "chatgpt", "nvidia",
        "super bowl", "olympics", "world cup",
        "ukraine", "russia", "taiwan", "iran", "israel",
        "tariff", "trade war",
        "recession", "unemployment", "jobs report",
        "spx6900", "dogecoin",
        "raydium", "jupiter",
    ]
    for entity in known_entities:
        if entity in combined:
            known_matches.add(entity)
    
    # Also extract capitalized words as potential entity matches
    words = (question + " " + description).split()
    for word in words:
        clean = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
        if (len(clean) >= 3 and clean not in STOP_WORDS 
                and clean not in GENERIC_CRYPTO_KEYWORDS):
            known_matches.add(clean)
    
    return known_matches

def extract_topics_from_x(x_data: dict) -> dict[str, dict]:
    """Extract trending topics/tokens from X signals with entity extraction."""
    topics = defaultdict(lambda: {
        "mentions": 0, "total_engagement": 0, "top_authors": [],
        "top_tweets": [], "sentiment_hints": [], "platforms": set(),
        "entities": {"tokens": [], "names": [], "topics": []},
        "sample_texts": [],
    })

    all_signals = x_data.get("account_signals", []) + x_data.get("search_signals", [])

    token_pattern = re.compile(r'\$([A-Z]{2,10})')

    for sig in all_signals:
        text = sig.get("text", "")
        text_lower = text.lower()
        author = sig.get("author", "")
        engagement = sig.get("engagement_score", 0)
        tier = sig.get("tier", "unknown")

        # Extract entities from this tweet
        entities = extract_entities_from_text(text)

        # Track by $TOKEN mentions
        tokens = token_pattern.findall(text)
        for token in tokens:
            t = topics[f"${token}"]
            t["mentions"] += 1
            t["total_engagement"] += engagement
            t["platforms"].add("x")
            if author and author != "unknown" and author not in t["top_authors"]:
                t["top_authors"].append(author)
            if text[:200] not in t["sample_texts"]:
                t["sample_texts"].append(text[:200])
            # Merge entities
            for k in entities:
                t["entities"][k] = list(set(t["entities"].get(k, []) + entities[k]))
            if tier == "tier1_caller":
                t["mentions"] += 2
                t["total_engagement"] += engagement * 2

        # Track by topic entities (more useful for market matching)
        for topic in entities["topics"]:
            t = topics[topic]
            t["mentions"] += 1
            t["total_engagement"] += engagement
            t["platforms"].add("x")
            if author and author != "unknown" and author not in t["top_authors"]:
                t["top_authors"].append(author)
            if text[:200] not in t["sample_texts"]:
                t["sample_texts"].append(text[:200])
            for k in entities:
                t["entities"][k] = list(set(t["entities"].get(k, []) + entities[k]))

        # Also track generic sentiment keywords (lower priority)
        topic_keywords = [
            "pump", "moon", "bullish", "bearish", "dump",
            "launch", "listing", "airdrop", "breakout",
        ]
        for kw in topic_keywords:
            if kw in text_lower:
                t = topics[kw]
                t["mentions"] += 1
                t["total_engagement"] += engagement
                t["platforms"].add("x")

    return topics

def extract_topics_from_tiktok(tt_data: dict) -> dict[str, dict]:
    """Extract trending topics from TikTok signals."""
    topics = defaultdict(lambda: {
        "mentions": 0, "total_engagement": 0, "top_authors": [],
        "top_tweets": [], "sentiment_hints": [], "platforms": set(),
        "entities": {"tokens": [], "names": [], "topics": []},
        "sample_texts": [],
    })

    token_pattern = re.compile(r'\$([A-Z]{2,10})')

    for sig in tt_data.get("hashtag_signals", []):
        if not sig.get("crypto_relevant"):
            continue
        caption = sig.get("caption", "")
        transcript = sig.get("transcript", "")
        creator = sig.get("creator", "")
        engagement = sig.get("engagement_score", 0)
        combined_text = caption + " " + transcript

        entities = extract_entities_from_text(combined_text)

        for hashtag in sig.get("hashtags", []):
            if hashtag in GENERIC_CRYPTO_KEYWORDS:
                continue
            t = topics[f"#{hashtag}"]
            t["mentions"] += 1
            t["total_engagement"] += engagement
            t["platforms"].add("tiktok")
            if creator and creator not in t["top_authors"]:
                t["top_authors"].append(creator)

        tokens = token_pattern.findall(combined_text.upper())
        for token in tokens:
            t = topics[f"${token}"]
            t["mentions"] += 1
            t["total_engagement"] += engagement
            t["platforms"].add("tiktok")
            if creator and creator not in t["top_authors"]:
                t["top_authors"].append(creator)

        for topic in entities["topics"]:
            t = topics[topic]
            t["mentions"] += 1
            t["total_engagement"] += engagement
            t["platforms"].add("tiktok")
            if creator and creator not in t["top_authors"]:
                t["top_authors"].append(creator)
            if combined_text[:200] not in t["sample_texts"]:
                t["sample_texts"].append(combined_text[:200])

    return topics

def find_prediction_market_matches(topics: dict, poly_data: dict, kalshi_data: dict) -> list[dict]:
    """Find prediction markets related to trending social topics.
    Uses multi-term overlap scoring instead of strict keyword matching."""
    matches = []

    # Build a set of all social terms for matching
    social_terms = {}
    for topic_name, topic_data in topics.items():
        clean = topic_name.replace("$", "").replace("#", "").lower()
        if len(clean) < 3:
            continue
        if clean in GENERIC_CRYPTO_KEYWORDS:
            continue
        social_terms[clean] = topic_name

    # Check Polymarket
    for market in poly_data.get("markets_with_edge", []):
        question = market.get("question", "")
        desc = market.get("description", "")
        market_keywords = extract_market_keywords(question, desc)
        
        # Find overlap between social terms and market keywords
        # Use word boundary matching to avoid "sol" matching "console" etc
        matching_topics = []
        market_text_lower = (question + " " + desc).lower()
        for social_term in social_terms:
            if social_term in market_keywords:
                matching_topics.append(social_term)
            elif len(social_term) >= 4:
                # Word boundary check in actual market text
                pattern = r'\b' + re.escape(social_term) + r'\b'
                if re.search(pattern, market_text_lower):
                    matching_topics.append(social_term)

        if not matching_topics:
            continue

        social_engagement = sum(
            topics.get(social_terms.get(t, t), {}).get("total_engagement", 0)
            for t in matching_topics
        )
        social_mentions = sum(
            topics.get(social_terms.get(t, t), {}).get("mentions", 0)
            for t in matching_topics
        )
        
        # Better scoring: more matching topics = higher quality
        match_quality = (
            len(matching_topics) * 15 +
            min(social_engagement / 10, 50) +
            min(social_mentions * 3, 30)
        )

        # Get sample social content for context
        sample_texts = []
        for t in matching_topics[:3]:
            topic_key = social_terms.get(t, t)
            texts = topics.get(topic_key, {}).get("sample_texts", [])
            sample_texts.extend(texts[:2])

        matches.append({
            "type": "polymarket",
            "question": market["question"],
            "url": market.get("url", ""),
            "matching_social_topics": matching_topics,
            "cheap_outcomes": market.get("cheap_outcomes", []),
            "volume_24h": market.get("volume_24h", 0),
            "social_engagement": social_engagement,
            "social_mentions": social_mentions,
            "match_quality": round(match_quality),
            "social_context": sample_texts[:3],
        })

    # Check Kalshi
    for market in kalshi_data.get("markets_with_edge", []):
        title = market.get("title", "")
        market_keywords = extract_market_keywords(title)
        
        matching_topics = []
        title_lower = title.lower()
        for social_term in social_terms:
            if social_term in market_keywords:
                matching_topics.append(social_term)
            elif len(social_term) >= 4:
                pattern = r'\b' + re.escape(social_term) + r'\b'
                if re.search(pattern, title_lower):
                    matching_topics.append(social_term)

        if not matching_topics:
            continue

        social_engagement = sum(
            topics.get(social_terms.get(t, t), {}).get("total_engagement", 0)
            for t in matching_topics
        )
        social_mentions = sum(
            topics.get(social_terms.get(t, t), {}).get("mentions", 0)
            for t in matching_topics
        )
        match_quality = (
            len(matching_topics) * 15 +
            min(social_engagement / 10, 50) +
            min(social_mentions * 3, 30)
        )

        sample_texts = []
        for t in matching_topics[:3]:
            topic_key = social_terms.get(t, t)
            texts = topics.get(topic_key, {}).get("sample_texts", [])
            sample_texts.extend(texts[:2])

        matches.append({
            "type": "kalshi",
            "question": market["title"],
            "url": market.get("url", ""),
            "matching_social_topics": matching_topics,
            "cheap_sides": market.get("cheap_sides", []),
            "volume_24h": market.get("volume_24h", 0),
            "social_engagement": social_engagement,
            "social_mentions": social_mentions,
            "match_quality": round(match_quality),
            "social_context": sample_texts[:3],
        })

    matches.sort(key=lambda x: (x["match_quality"], x["social_engagement"]), reverse=True)
    return matches

def score_signal(topic_name: str, topic_data: dict, platform_count: int) -> dict:
    mentions = topic_data["mentions"]
    engagement = topic_data["total_engagement"]
    platforms = len(topic_data.get("platforms", set()))
    tier1_authors = [a for a in topic_data.get("top_authors", [])
                     if a in ["MustStopMurad", "RookieXBT", "cometcalls", "thisisdjen",
                             "free_electron0", "flooksta", "levigem", "gammichan"]]

    mention_score = min(mentions * 10, 100)
    engagement_score = min(engagement / 100, 100)
    platform_score = platforms * 30
    tier1_score = len(tier1_authors) * 25

    total = min(mention_score + engagement_score + platform_score + tier1_score, 100)

    confidence = "low"
    if total > 70:
        confidence = "high"
    elif total > 40:
        confidence = "medium"

    return {
        "topic": topic_name,
        "score": round(total),
        "confidence": confidence,
        "mentions": mentions,
        "engagement": engagement,
        "platforms": list(topic_data.get("platforms", [])),
        "platform_count": platforms,
        "top_authors": topic_data["top_authors"][:5],
        "tier1_callers": tier1_authors,
        "has_tier1_signal": len(tier1_authors) > 0,
        "sample_texts": topic_data.get("sample_texts", [])[:3],
    }

def run_aggregation() -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading latest scan data...")
    x_data = load_latest_scan("x") or {"account_signals": [], "search_signals": []}
    poly_data = load_latest_scan("polymarket") or {"markets_with_edge": []}
    kalshi_data = load_latest_scan("kalshi") or {"markets_with_edge": []}
    tt_data = load_latest_scan("tiktok") or {"hashtag_signals": []}

    x_acct = len(x_data.get('account_signals', []))
    x_search = len(x_data.get('search_signals', []))
    x_with_author = len([s for s in x_data.get('account_signals', []) + x_data.get('search_signals', [])
                         if s.get('author', 'unknown') != 'unknown'])
    print(f"  X signals: {x_acct + x_search} ({x_with_author} with known author)")
    print(f"  Polymarket opportunities: {len(poly_data.get('markets_with_edge', []))}")
    print(f"  Kalshi opportunities: {len(kalshi_data.get('markets_with_edge', []))}")
    print(f"  TikTok signals: {len(tt_data.get('hashtag_signals', []))}")

    # Merge topics across platforms
    x_topics = extract_topics_from_x(x_data)
    tt_topics = extract_topics_from_tiktok(tt_data)

    all_topics = defaultdict(lambda: {
        "mentions": 0, "total_engagement": 0, "top_authors": [],
        "platforms": set(), "entities": {"tokens": [], "names": [], "topics": []},
        "sample_texts": [],
    })

    for name, data in x_topics.items():
        t = all_topics[name]
        t["mentions"] += data["mentions"]
        t["total_engagement"] += data["total_engagement"]
        t["top_authors"].extend(data["top_authors"])
        t["platforms"].update(data["platforms"])
        t["sample_texts"].extend(data.get("sample_texts", []))
        for k in data.get("entities", {}):
            t["entities"][k] = list(set(t["entities"].get(k, []) + data["entities"].get(k, [])))

    for name, data in tt_topics.items():
        t = all_topics[name]
        t["mentions"] += data["mentions"]
        t["total_engagement"] += data["total_engagement"]
        t["top_authors"].extend(data["top_authors"])
        t["platforms"].update(data["platforms"])
        t["sample_texts"].extend(data.get("sample_texts", []))
        for k in data.get("entities", {}):
            t["entities"][k] = list(set(t["entities"].get(k, []) + data["entities"].get(k, [])))

    # Topics that are useful for market matching but not actionable signals
    NOISE_SIGNAL_TOPICS = {
        "bitcoin", "ethereum", "solana", "polymarket", "kalshi",
        "pump", "bullish", "bearish", "moon", "launch", "listing",
        "airdrop", "breakout", "dump",
    }

    # Score all topics
    scored = []
    for name, data in all_topics.items():
        if data["mentions"] < 2:
            continue
        clean_name = name.replace("$", "").replace("#", "").lower()
        if clean_name in NOISE_SIGNAL_TOPICS:
            continue
        signal = score_signal(name, data, len(all_topics))
        scored.append(signal)

    scored.sort(key=lambda x: x["score"], reverse=True)

    # Find prediction market matches
    pm_matches = find_prediction_market_matches(all_topics, poly_data, kalshi_data)

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_signals": scored[:30],
        "prediction_market_edges": pm_matches[:20],
        "polymarket_top_opportunities": [
            {
                "question": m["question"][:120],
                "cheap_outcomes": m.get("cheap_outcomes", []),
                "volume_24h": m.get("volume_24h", 0),
                "url": m.get("url", ""),
            }
            for m in poly_data.get("markets_with_edge", [])[:15]
        ],
        "kalshi_top_opportunities": [
            {
                "title": m["title"][:120],
                "cheap_sides": m.get("cheap_sides", []),
                "volume_24h": m.get("volume_24h", 0),
                "url": m.get("url", ""),
            }
            for m in kalshi_data.get("markets_with_edge", [])[:15]
        ],
        "summary": {
            "total_topics_tracked": len(all_topics),
            "high_confidence_signals": len([s for s in scored if s["confidence"] == "high"]),
            "medium_confidence_signals": len([s for s in scored if s["confidence"] == "medium"]),
            "cross_platform_signals": len([s for s in scored if s["platform_count"] > 1]),
            "tier1_backed_signals": len([s for s in scored if s["has_tier1_signal"]]),
            "prediction_market_matches": len(pm_matches),
            "x_signals_quality": {
                "total": x_acct + x_search,
                "with_known_author": x_with_author,
                "with_engagement": len([s for s in x_data.get('account_signals', []) + x_data.get('search_signals', [])
                                       if s.get('engagement_score', 0) > 0]),
            },
            "tiktok_signals_quality": {
                "total": len(tt_data.get('hashtag_signals', [])),
                "crypto_relevant": len([s for s in tt_data.get('hashtag_signals', []) if s.get('crypto_relevant')]),
            },
        }
    }

    outfile = os.path.join(OUTPUT_DIR, f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, default=str)

    latest_file = os.path.join(OUTPUT_DIR, "latest.json")
    with open(latest_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved to {outfile}")
    print(f"Symlinked to {latest_file}")
    print(f"\n{'='*60}")
    print(f"SIGNAL SUMMARY")
    print(f"{'='*60}")
    print(f"High confidence: {results['summary']['high_confidence_signals']}")
    print(f"Medium confidence: {results['summary']['medium_confidence_signals']}")
    print(f"Cross-platform: {results['summary']['cross_platform_signals']}")
    print(f"Tier1 backed: {results['summary']['tier1_backed_signals']}")
    print(f"Prediction market matches: {results['summary']['prediction_market_matches']}")

    if scored:
        print(f"\n--- TOP 10 SIGNALS ---")
        for s in scored[:10]:
            platforms = ", ".join(s["platforms"])
            t1 = " *T1" if s["has_tier1_signal"] else ""
            print(f"  [{s['confidence'].upper():6s}] {s['topic']:20s} | Score: {s['score']:3d} | "
                  f"Mentions: {s['mentions']:3d} | Platforms: {platforms}{t1}")

    if pm_matches:
        print(f"\n--- PREDICTION MARKET EDGES (social cross-referenced) ---")
        for m in pm_matches[:5]:
            print(f"\n  [{m['type'].upper()}] {m['question'][:70]}")
            print(f"  Social topics: {', '.join(m['matching_social_topics'])}")
            print(f"  Social engagement: {m['social_engagement']} | Match quality: {m['match_quality']}")
            if m.get("social_context"):
                print(f"  Context: {m['social_context'][0][:100]}...")
            outcomes = m.get("cheap_outcomes", m.get("cheap_sides", []))
            for o in outcomes[:2]:
                side = o.get("outcome", o.get("side", "?"))
                prob = o.get("implied_probability", "?")
                payout = o.get("payout_multiple", "?")
                print(f"  -> {side}: {prob} ({payout} payout)")
    else:
        print(f"\n--- NO PREDICTION MARKET MATCHES ---")
        print(f"  Social topics found: {len(social_terms_debug(all_topics))}")
        print(f"  Polymarket questions: {len(poly_data.get('markets_with_edge', []))}")
        print(f"  Try: check if X scan is returning real data (not @unknown)")

    return results

def social_terms_debug(topics):
    """Debug helper to show what social terms would be used for matching."""
    terms = {}
    for topic_name in topics:
        clean = topic_name.replace("$", "").replace("#", "").lower()
        if len(clean) >= 3 and clean not in GENERIC_CRYPTO_KEYWORDS:
            terms[clean] = topic_name
    return terms

if __name__ == "__main__":
    run_aggregation()
