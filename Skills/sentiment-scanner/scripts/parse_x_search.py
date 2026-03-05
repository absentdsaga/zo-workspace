#!/usr/bin/env python3
"""Parse x_search JSON files and create X scan file - improved version."""
import json
import os
import re
from datetime import datetime
from pathlib import Path

def parse_x_search_files():
    """Parse all x_search JSON files from conversation workspace."""
    workspace = Path("/home/.z/workspaces/con_d9AdCDVg75OB40LB/read_webpage")
    x_files = sorted(workspace.glob("x_search*.json"))
    
    all_signals = []
    scan_time = datetime.utcnow().isoformat() + "Z"
    
    for x_file in x_files:
        with open(x_file, 'r') as f:
            data = json.load(f)
        
        summary = data.get("summary", "")
        
        # More flexible pattern matching for different formats
        # Pattern 1: "1. **Post by Username (@handle)**"
        # Pattern 2: "1. **Username/Profile: Name (@handle)**"
        
        # Split by numbered entries
        parts = re.split(r'\n(?=\d+\.)', summary)
        
        for part in parts:
            if not part.strip() or part.strip().startswith("###"):
                continue
            
            # Extract author/handle - look for @username patterns
            author_match = re.search(r'@(\w+)', part)
            author = author_match.group(1) if author_match else "unknown"
            
            # Extract URL
            url_match = re.search(r'https://x\.com/[^\s\)]+', part)
            url = url_match.group(0) if url_match else ""
            
            # Extract tweet ID from URL
            tweet_id_match = re.search(r'/status/(\d+)', url)
            tweet_id = tweet_id_match.group(1) if tweet_id_match else ""
            
            # Extract engagement metrics
            likes_match = re.search(r'(\d+)\s*likes?', part, re.IGNORECASE)
            retweets_match = re.search(r'(\d+)\s*(?:retweets?|RTs?)', part, re.IGNORECASE)
            replies_match = re.search(r'(\d+)\s*(?:replies?|comments?)', part, re.IGNORECASE)
            views_match = re.search(r'(\d+(?:\.\d+)?[Kk]?)\s*views?', part, re.IGNORECASE)
            
            likes = int(likes_match.group(1)) if likes_match else 0
            retweets = int(retweets_match.group(1)) if retweets_match else 0
            replies = int(replies_match.group(1)) if replies_match else 0
            
            # Parse views (handle K suffix)
            views = 0
            if views_match:
                views_str = views_match.group(1)
                if 'k' in views_str.lower():
                    views = int(float(views_str.lower().replace('k', '')) * 1000)
                else:
                    views = int(views_str)
            
            # Extract text content - look for Full Content section
            text_match = re.search(r'Full Content:\s*(.+?)(?:\*\*|$)', part, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ""
            # Clean up text
            text = re.sub(r'\*+', '', text)  # Remove markdown asterisks
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text[:500]  # Truncate long text
            
            # Extract timestamp
            timestamp_match = re.search(r'Timestamp:\s*(.+?)(?:\||$)', part)
            created_at = timestamp_match.group(1).strip() if timestamp_match else ""
            
            if text or url:
                engagement_score = likes + (retweets * 2) + (replies * 3)
                engagement_rate = engagement_score / max(views, 1) * 1000 if views > 0 else 0
                
                signal = {
                    "platform": "x",
                    "author": author,
                    "tier": "unknown",
                    "text": text,
                    "likes": likes,
                    "retweets": retweets,
                    "replies": replies,
                    "views": views,
                    "engagement_score": engagement_score,
                    "engagement_rate": round(engagement_rate, 2),
                    "tweet_id": tweet_id,
                    "url": url,
                    "created_at": created_at,
                    "scanned_at": scan_time
                }
                all_signals.append(signal)
    
    return all_signals, scan_time

if __name__ == "__main__":
    signals, scan_time = parse_x_search_files()
    
    # Create output
    output = {
        "scan_time": scan_time,
        "mode": "search",
        "account_signals": [],
        "search_signals": signals,
        "summary": {
            "total_signals": len(signals),
            "search_signals": len(signals)
        }
    }
    
    # Save with timestamp
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = f"/home/workspace/Skills/sentiment-scanner/data/x_scan_{timestamp_str}.json"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Created X scan file: {output_path}")
    print(f"Total signals: {len(signals)}")
    
    # Print sample for debugging
    if signals:
        print("\nSample signal:")
        print(json.dumps(signals[0], indent=2))
