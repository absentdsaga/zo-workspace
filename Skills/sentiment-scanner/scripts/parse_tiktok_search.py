#!/usr/bin/env python3
"""Parse web_search results and create TikTok scan file - fixed version."""
import json
import os
import re
from datetime import datetime
from pathlib import Path

def parse_tiktok_search():
    """Parse TikTok web_search results."""
    workspace = Path("/home/.z/workspaces/con_d9AdCDVg75OB40LB/read_webpage")
    tiktok_file = workspace / "web_search~~3a1772717612987.json"
    
    scan_time = datetime.utcnow().isoformat() + "Z"
    signals = []
    
    if not tiktok_file.exists():
        print(f"File not found: {tiktok_file}")
        return signals, scan_time
    
    with open(tiktok_file, 'r') as f:
        data = json.load(f)
    
    # Parse as list
    results = data if isinstance(data, list) else []
    
    for item in results:
        url = item.get('url', '')
        title = item.get('title', '')
        text = item.get('text', '')
        
        # Only process TikTok URLs (exclude Instagram, MEXC news, etc)
        if 'tiktok.com' not in url:
            continue
        
        # Extract creator from URL
        creator_match = re.search(r'@([^/]+)', url)
        creator = creator_match.group(1) if creator_match else "unknown"
        
        # Extract hashtags from title and text
        all_text = f"{title} {text}"
        hashtags = re.findall(r'#(\w+)', all_text)
        
        # Determine crypto relevance
        crypto_keywords = ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 
                          'memecoin', 'memecoin', 'token', 'coin', 'pump', 'trading', 
                          'invest', 'xrp', 'war']
        is_crypto = any(kw in all_text.lower() for kw in crypto_keywords)
        
        # Calculate engagement (likes, comments)
        likes_match = re.search(r'([\d.]+[Kk]?)\s*Likes?', text, re.IGNORECASE)
        likes = 0
        if likes_match:
            likes_str = likes_match.group(1)
            if 'k' in likes_str.lower():
                likes = int(float(likes_str.lower().replace('k', '')) * 1000)
            else:
                likes = int(likes_str)
        
        # Caption from title
        caption = title.replace(' | TikTok', '').strip()
        
        signal = {
            "caption": caption[:300],
            "url": url,
            "creator": creator,
            "hashtags": list(set(hashtags[:10])),
            "crypto_relevant": is_crypto,
            "engagement_score": likes,
            "transcript": ""
        }
        signals.append(signal)
    
    return signals, scan_time

if __name__ == "__main__":
    signals, scan_time = parse_tiktok_search()
    
    # Create output
    output = {
        "scan_time": scan_time,
        "hashtag_signals": signals,
        "summary": {
            "total_videos": len(signals),
            "crypto_relevant": sum(1 for s in signals if s.get('crypto_relevant', False))
        }
    }
    
    # Save with timestamp
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = f"/home/workspace/Skills/sentiment-scanner/data/tiktok_scan_{timestamp_str}.json"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Created TikTok scan file: {output_path}")
    print(f"Total videos: {len(signals)}")
    print(f"Crypto relevant: {output['summary']['crypto_relevant']}")
