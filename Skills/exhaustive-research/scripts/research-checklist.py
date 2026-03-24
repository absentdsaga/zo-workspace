#!/usr/bin/env python3
"""Generate a structured research checklist for exhaustive content research."""

import argparse
import json
import os
from datetime import datetime

def generate_checklist(topic: str, platforms: list[str], output_path: str):
    checklist = {
        "topic": topic,
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "platforms": {},
        "completeness": {
            "expected_count": "TBD",
            "found_count": 0,
            "gap_analysis": "",
            "verified_complete": False
        },
        "inventory": []
    }

    for platform in platforms:
        checklist["platforms"][platform] = {
            "searched": False,
            "queries_used": [],
            "pages_checked": 0,
            "media_tab_exhausted": False,
            "cross_references_followed": False,
            "items_found": 0
        }

    md_output = f"""# Research Checklist: {topic}
Created: {checklist['created']}
Status: IN PROGRESS

## Platforms to Search
"""
    for p in platforms:
        md_output += f"""
### {p}
- [ ] Initial search completed
- [ ] All result pages checked
- [ ] Media tab fully scrolled
- [ ] Cross-references followed
- [ ] Items found: 0
- Queries used: (list each query)
"""

    md_output += f"""
## Completeness Check
- [ ] Expected content count estimated
- [ ] Found count matches expected
- [ ] Gap analysis done
- [ ] All cross-references followed
- [ ] Multiple search approaches tried
- [ ] VERIFIED COMPLETE

## Content Inventory
| # | URL | Platform | Date | Type | Description | Downloaded | Transcribed | Analyzed |
|---|-----|----------|------|------|-------------|------------|-------------|----------|
| 1 | | | | | | [ ] | [ ] | [ ] |

## Gap Analysis
Expected: TBD
Found: 0
Missing: TBD
"""

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(md_output)

    json_path = output_path.replace(".md", ".json")
    with open(json_path, "w") as f:
        json.dump(checklist, f, indent=2)

    print(f"Checklist created: {output_path}")
    print(f"JSON tracker: {json_path}")
    print(f"Platforms: {', '.join(platforms)}")
    print(f"\nNext steps:")
    print(f"1. Estimate expected content count")
    print(f"2. Search each platform exhaustively")
    print(f"3. Log every item in the inventory table")
    print(f"4. Run completeness check before declaring done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exhaustive research checklist")
    parser.add_argument("topic", help="Research topic or subject")
    parser.add_argument("--platforms", nargs="+", default=["x_twitter", "website", "youtube"],
                       help="Platforms to search (default: x_twitter website youtube)")
    parser.add_argument("--output", "-o", default=None,
                       help="Output path (default: <topic>-research-checklist.md)")
    args = parser.parse_args()

    if not args.output:
        slug = args.topic.lower().replace(" ", "-").replace("/", "-")[:50]
        args.output = f"{slug}-research-checklist.md"

    generate_checklist(args.topic, args.platforms, args.output)
