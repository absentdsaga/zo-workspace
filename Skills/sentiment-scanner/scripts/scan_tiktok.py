#!/usr/bin/env python3
"""TikTok trending crypto/memecoin scanner.
Uses agent-browser CLI to scrape public TikTok hashtag pages.
Falls back to Zo web_search for TikTok content if scraping fails."""

import subprocess
import json
import os
import re
import sys
from datetime import datetime, timezone

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"

CRYPTO_HASHTAGS = [
    "memecoin", "solana", "crypto", "cryptotok", "defi",
    "altcoin", "web3", "pumpdotfun", "degen", "bitcoin",
    "memecoins", "solanamemecoin", "cryptotrading", "100x",
]

def scrape_tiktok_hashtag(hashtag: str) -> list[dict]:
    """Use agent-browser to open TikTok hashtag page and extract video info."""
    url = f"https://www.tiktok.com/tag/{hashtag}"
    session = f"tiktok_{hashtag}"
    try:
        # Open the page
        subprocess.run(
            ["agent-browser", "--session", session, "open", url],
            capture_output=True, text=True, timeout=30
        )
        # Wait for content to load
        subprocess.run(
            ["agent-browser", "--session", session, "wait", "3000"],
            capture_output=True, text=True, timeout=10
        )
        # Scroll to load more content
        subprocess.run(
            ["agent-browser", "--session", session, "scroll", "down", "2000"],
            capture_output=True, text=True, timeout=10
        )
        subprocess.run(
            ["agent-browser", "--session", session, "wait", "2000"],
            capture_output=True, text=True, timeout=10
        )
        # Get the page text
        result = subprocess.run(
            ["agent-browser", "--session", session, "snapshot", "--compact"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return parse_tiktok_snapshot(result.stdout, hashtag)
    except subprocess.TimeoutExpired:
        print(f"  Timeout scraping #{hashtag}")
    except FileNotFoundError:
        print("  agent-browser not found")
    except Exception as e:
        print(f"  Error scraping #{hashtag}: {e}")
    return []

def parse_tiktok_snapshot(snapshot: str, source_hashtag: str) -> list[dict]:
    """Parse agent-browser snapshot output to extract video info."""
    videos = []
    lines = snapshot.split("\n")
    
    current_video = {}
    for line in lines:
        line = line.strip()
        # Look for video descriptions/captions
        if any(kw in line.lower() for kw in ["#", "caption", "desc"]):
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', line.lower())
            if hashtags or any(kw in line.lower() for kw in ["crypto", "memecoin", "solana", "bitcoin", "pump"]):
                current_video = {
                    "caption": line[:500],
                    "hashtags": hashtags,
                    "source_hashtag": source_hashtag,
                }
        # Look for view/like counts
        view_match = re.search(r'(\d+\.?\d*[KMBkmb]?)\s*(views?|plays?)', line, re.IGNORECASE)
        like_match = re.search(r'(\d+\.?\d*[KMBkmb]?)\s*(likes?|hearts?)', line, re.IGNORECASE)
        comment_match = re.search(r'(\d+\.?\d*[KMBkmb]?)\s*(comments?)', line, re.IGNORECASE)
        
        if view_match and current_video:
            current_video["views"] = parse_count(view_match.group(1))
        if like_match and current_video:
            current_video["likes"] = parse_count(like_match.group(1))
        if comment_match and current_video:
            current_video["comments"] = parse_count(comment_match.group(1))
        
        # Look for usernames
        user_match = re.search(r'@(\w+)', line)
        if user_match and current_video:
            current_video["creator"] = user_match.group(1)
            # Save completed video and start fresh
            if current_video.get("caption"):
                videos.append(current_video)
                current_video = {}
    
    # Don't forget last video
    if current_video.get("caption"):
        videos.append(current_video)
    
    return videos

def parse_count(text: str) -> int:
    if not text or not isinstance(text, str):
        return 0
    text = text.strip().upper().replace(",", "")
    multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(float(text))
    except ValueError:
        return 0

def fallback_web_search(hashtag: str) -> list[dict]:
    """Use Zo API to web search for TikTok content about this hashtag."""
    import asyncio
    import aiohttp
    
    async def search():
        token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
        if not token:
            return []
        
        prompt = f"""Use the web_search tool to search for: "tiktok {hashtag} crypto memecoin trending" with time_range="week".

Then extract from the results any specific crypto tokens, memecoins, or trending narratives mentioned. 
Return a JSON array where each item has:
- "caption": the relevant text/snippet
- "creator": source or author if known (empty string if unknown)
- "hashtags": array of relevant hashtags
- "views": estimated views (0 if unknown)
- "likes": estimated likes (0 if unknown)
- "source_url": the URL

Return ONLY the JSON array, no other text. If no results, return [].
"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.zo.computer/zo/ask",
                    headers={
                        "authorization": token,
                        "content-type": "application/json"
                    },
                    json={
                        "input": prompt,
                        "model_name": "byok:22a22d9b-6586-4137-82dc-c97f9e0efecc",
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    output = data.get("output", "")
                    if isinstance(output, list):
                        return output
                    if isinstance(output, str):
                        start = output.find("[")
                        end = output.rfind("]")
                        if start >= 0 and end > start:
                            try:
                                return json.loads(output[start:end+1])
                            except json.JSONDecodeError:
                                pass
                    return []
        except Exception as e:
            print(f"  Web search fallback error: {e}")
            return []
    
    return asyncio.run(search())

def process_video(video: dict, source_hashtag: str = "") -> dict:
    caption = video.get("caption", video.get("description", video.get("text", "")))
    creator = video.get("username", video.get("creator", video.get("user", "")))
    views = parse_count(str(video.get("views", video.get("view_count", 0))))
    likes = parse_count(str(video.get("likes", video.get("like_count", 0))))
    comments = parse_count(str(video.get("comments", video.get("comment_count", 0))))

    video_url = video.get("url", video.get("video_url", video.get("link", video.get("source_url", ""))))
    video_id = video.get("id", video.get("video_id", ""))

    hashtags = video.get("hashtags", [])
    if not hashtags:
        hashtags = re.findall(r'#(\w+)', (caption or "").lower())
    if source_hashtag and source_hashtag not in hashtags:
        hashtags.append(source_hashtag)

    crypto_relevant = any(h in ["crypto", "memecoin", "solana", "bitcoin", "defi", "web3",
                                "altcoin", "degen", "pumpdotfun", "memecoins", "100x",
                                "cryptotok", "cryptotrading", "solanamemecoin"]
                         for h in hashtags)

    return {
        "platform": "tiktok",
        "creator": creator,
        "caption": caption[:500] if caption else "",
        "video_url": video_url,
        "video_id": video_id,
        "views": views,
        "likes": likes,
        "comments": comments,
        "hashtags": hashtags,
        "source_hashtag": source_hashtag,
        "crypto_relevant": crypto_relevant,
        "engagement_score": likes + comments * 3,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }

def run_scan(hashtags: list[str] = None) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if hashtags is None:
        hashtags = CRYPTO_HASHTAGS

    results = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "hashtag_signals": [],
        "discover_signals": [],
        "summary": {}
    }

    print(f"Scanning {len(hashtags)} TikTok hashtags...")
    
    # Try agent-browser first for top 5 hashtags, fall back to web search
    for i, tag in enumerate(hashtags):
        videos = []
        if i < 5:  # Only browser-scrape top 5 to save time
            videos = scrape_tiktok_hashtag(tag)
        
        if not videos:
            print(f"  #{tag}: browser scrape got 0, trying web search fallback...")
            videos = fallback_web_search(tag)
        
        for v in videos:
            processed = process_video(v, source_hashtag=tag)
            results["hashtag_signals"].append(processed)
        print(f"  #{tag}: {len(videos)} videos")

    crypto_signals = [s for s in results["hashtag_signals"] if s.get("crypto_relevant")]
    results["hashtag_signals"].sort(key=lambda x: x.get("engagement_score", 0), reverse=True)

    results["summary"] = {
        "total_videos_scanned": len(results["hashtag_signals"]),
        "crypto_relevant": len(crypto_signals),
        "discover_items": 0,
        "top_creators": list(set(s["creator"] for s in crypto_signals[:20] if s.get("creator"))),
        "trending_hashtags": list(set(
            h for s in crypto_signals for h in s.get("hashtags", [])
        ))[:20],
    }

    outfile = os.path.join(DATA_DIR, f"tiktok_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved to {outfile}")
    print(f"Total videos: {len(results['hashtag_signals'])} | Crypto relevant: {len(crypto_signals)}")

    return results

if __name__ == "__main__":
    transcribe = "--transcribe" in sys.argv
    results = run_scan()
    
    if transcribe:
        print("\n--- Running transcription on top videos ---")
        from transcribe_tiktok import transcribe_video
        top_videos = [s for s in results["hashtag_signals"] 
                      if s.get("video_url") and s.get("crypto_relevant")]
        top_videos.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        
        for v in top_videos[:10]:
            url = v["video_url"]
            print(f"\nTranscribing: {url}")
            t = transcribe_video(url)
            if t.get("transcript"):
                v["transcript"] = t["transcript"]
                v["transcript_method"] = t["method"]
                print(f"  Got transcript: {t['transcript'][:100]}...")
        
        outfile = os.path.join(DATA_DIR, f"tiktok_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_transcribed.json")
        with open(outfile, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nSaved transcribed scan to {outfile}")
