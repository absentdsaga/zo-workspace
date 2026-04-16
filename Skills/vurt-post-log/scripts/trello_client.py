#!/usr/bin/env python3
"""Pull show/title info from VURT Content Programming Grid on Trello."""

import json
import os
import re
import sys
import urllib.request
import urllib.parse

BOARD_ID = "qMUj0uK8"
TRELLO_BASE = "https://api.trello.com/1"


def get_env(key):
    val = os.environ.get(key)
    if not val:
        print(f"Error: {key} not set.", file=sys.stderr)
        sys.exit(1)
    return val


def trello_get(path, extra_params=None):
    api_key = get_env("TRELLO_VURT_API_KEY")
    token = get_env("TRELLO_VURT_API_TOKEN")
    params = {"key": api_key, "token": token}
    if extra_params:
        params.update(extra_params)
    url = f"{TRELLO_BASE}{path}?{urllib.parse.urlencode(params)}"
    return json.loads(urllib.request.urlopen(url).read())


def _parse_handles_from_text(text):
    """Extract social handles from text (comments, descriptions).
    Mark uses full URLs in Trello comments — parse those into platform + handle."""
    handles = {"instagram": [], "tiktok": [], "youtube": [], "facebook": [], "linkedin": [], "imdb": []}
    seen = set()

    ig_urls = re.findall(r'https?://(?:www\.)?instagram\.com/([\w.]+)/?', text)
    for h in ig_urls:
        if h not in seen:
            handles["instagram"].append({"handle": f"@{h}", "url": f"https://www.instagram.com/{h}/"})
            seen.add(h)

    tt_urls = re.findall(r'https?://(?:www\.)?tiktok\.com/@?([\w.]+)/?', text)
    for h in tt_urls:
        if h not in seen:
            handles["tiktok"].append({"handle": f"@{h}", "url": f"https://www.tiktok.com/@{h}"})
            seen.add(h)

    yt_urls = re.findall(r'https?://(?:www\.)?youtube\.com/([\w.]+)/?', text)
    for h in yt_urls:
        if h not in seen:
            handles["youtube"].append({"handle": h, "url": f"https://www.youtube.com/{h}"})
            seen.add(h)

    fb_urls = re.findall(r'https?://(?:www\.)?facebook\.com/([\w.]+)/?', text)
    for h in fb_urls:
        if h not in seen:
            handles["facebook"].append({"handle": h, "url": f"https://www.facebook.com/{h}"})
            seen.add(h)

    li_urls = re.findall(r'https?://(?:www\.)?linkedin\.com/in/([\w\-]+)/?', text)
    for h in li_urls:
        if h not in seen:
            handles["linkedin"].append({"handle": h, "url": f"https://www.linkedin.com/in/{h}/"})
            seen.add(h)

    imdb_urls = re.findall(r'(?:https?://)?(?:www\.)?imdb\.(?:com|me)/([\w/]+)', text)
    for h in imdb_urls:
        if h not in seen:
            handles["imdb"].append({"url": f"https://www.imdb.me/{h}"})
            seen.add(h)

    at_handles = re.findall(r'\(@([\w.]+)\)', text)
    for h in at_handles:
        if h not in seen:
            handles["instagram"].append({"handle": f"@{h}"})
            seen.add(h)

    handles = {k: v for k, v in handles.items() if v}
    return handles


def _parse_people_from_comment(text):
    """Parse structured people info from Mark's handle comments.
    Format: role headers followed by bullet-point URLs, then 'Cast –' with name - URL lines."""
    people = []
    current_person = None
    collecting_urls = False

    lines = text.split("\n")
    for line in lines:
        line = line.strip().lstrip("- ").strip()
        if not line or line.startswith("!["): # skip images
            continue

        # Role header: "Producer/Director/Editor – Racheal Leigh" or "Screenplay by Brandi Self"
        role_match = re.match(
            r'((?:Producer|Director|Editor|Screenplay|Writer|Executive Producer)[/\w\s]*?)(?:\s*[-–—]\s*|\s+by\s+)([\w\s.]+?)(?:\s*$)',
            line, re.IGNORECASE
        )
        # Cast header: "Cast –" (no name on this line)
        cast_header = re.match(r'^Cast\s*[-–—]?\s*$', line, re.IGNORECASE)
        # Cast member: "Stephanie Lightman - [url]" or "Stephanie Lightman - https://..."
        cast_member = re.match(r'^([\w\s.]+?)\s*[-–—]\s*(?:\[|\xa0|http|$)', line)

        if role_match:
            name = role_match.group(2).strip()
            role = role_match.group(1).strip()
            current_person = {"name": name, "role": role, "handles": {}}
            people.append(current_person)
            collecting_urls = True
            handles = _parse_handles_from_text(line)
            for p, entries in handles.items():
                current_person["handles"].setdefault(p, []).extend(entries)
        elif cast_header:
            current_person = None
            collecting_urls = True
        elif cast_member and not line.startswith("http") and not line.startswith("["):
            name = cast_member.group(1).strip()
            if name and len(name) > 1:
                handles = _parse_handles_from_text(line)
                current_person = {"name": name, "role": "Cast", "handles": handles}
                people.append(current_person)
        elif collecting_urls and current_person and ("http" in line or "@" in line):
            handles = _parse_handles_from_text(line)
            for p, entries in handles.items():
                current_person["handles"].setdefault(p, []).extend(entries)

    return people


def get_card_comments(card_id):
    """Get all comments on a Trello card."""
    actions = trello_get(f"/cards/{card_id}/actions", {
        "filter": "commentCard",
        "limit": 50,
    })
    return [{"author": a["memberCreator"]["fullName"], "text": a["data"]["text"], "date": a["date"]} for a in actions]


def get_all_titles():
    """Get all title cards from the Content Programming Grid with parsed metadata."""
    lists = trello_get(f"/boards/{BOARD_ID}/lists", {"fields": "name"})
    list_map = {l["id"]: l["name"] for l in lists}

    cards = trello_get(f"/boards/{BOARD_ID}/cards", {
        "fields": "name,desc,labels,idList,url",
        "limit": 100,
    })

    titles = []
    for card in cards:
        name = card["name"]
        if "DO NOT DELETE" in name or "template" in name.lower():
            continue

        desc = card.get("desc", "")
        parsed = _parse_card_desc(desc)
        parsed["title"] = name
        parsed["card_id"] = card["id"]
        parsed["list"] = list_map.get(card["idList"], "")
        parsed["labels"] = [l["name"] for l in card.get("labels", [])]
        parsed["trello_url"] = card.get("url", "")
        titles.append(parsed)

    return titles


def _parse_card_desc(desc):
    """Extract structured info from card description markdown."""
    result = {
        "director_producer": "",
        "type": "",
        "premiere_date": "",
        "notes": "",
        "cast": [],
        "google_drive": "",
    }

    dp = re.search(r"\*\*Director\s*/\s*Producer:\*\*\s*(.+)", desc)
    if dp:
        result["director_producer"] = dp.group(1).strip()

    tp = re.search(r"\*\*Type:\*\*\s*(.+)", desc)
    if tp:
        result["type"] = tp.group(1).strip()

    pd = re.search(r"\*\*(?:Scheduled )?Premiere Date\*?\*?:?\*?\*?\s*(.+)", desc)
    if pd:
        result["premiere_date"] = pd.group(1).strip()

    notes = re.search(r"\*\*(?:Issues / )?Notes:?\*\*\s*(.+?)(?:\n\n|\n---|\n\*\*)", desc, re.DOTALL)
    if notes:
        result["notes"] = notes.group(1).strip()

    gd = re.search(r"(https://drive\.google\.com/\S+)", desc)
    if gd:
        result["google_drive"] = gd.group(1)

    return result


def get_title_with_handles(show_name):
    """Get title info + social handles from comments for a specific show."""
    info = get_title_info(show_name)
    if not info:
        return None

    comments = get_card_comments(info["card_id"])

    all_people = []
    all_handles = {"instagram": [], "tiktok": [], "youtube": [], "facebook": [], "linkedin": [], "imdb": []}

    for comment in comments:
        text = comment["text"]
        if "handle" in text.lower() or "@" in text or "instagram" in text.lower() or "tiktok" in text.lower():
            people = _parse_people_from_comment(text)
            all_people.extend(people)
            comment_handles = _parse_handles_from_text(text)
            for platform, entries in comment_handles.items():
                all_handles.setdefault(platform, []).extend(entries)

    info["people"] = all_people
    info["social_handles"] = {k: v for k, v in all_handles.items() if v}
    return info


def get_title_info(show_name):
    """Get info for a specific show by fuzzy name match."""
    titles = get_all_titles()
    show_lower = show_name.lower()
    show_words = set(re.findall(r'\w+', show_lower))

    for t in titles:
        if show_lower in t["title"].lower():
            return t

    best_match = None
    best_score = 0
    for t in titles:
        title_words = set(re.findall(r'\w+', t["title"].lower()))
        overlap = len(show_words & title_words)
        if overlap >= 2 and overlap / len(show_words) > 0.5:
            if overlap > best_score:
                best_score = overlap
                best_match = t

    return best_match


def print_title(t):
    print(f"  Title: {t['title']}")
    print(f"  Status: {t['list']}")
    if t.get("director_producer"):
        print(f"  Director/Producer: {t['director_producer']}")
    if t.get("type"):
        print(f"  Type: {t['type']}")
    if t.get("premiere_date"):
        print(f"  Premiere: {t['premiere_date']}")
    if t.get("notes"):
        print(f"  Notes: {t['notes'][:200]}")
    if t.get("labels"):
        print(f"  Labels: {', '.join(t['labels'])}")
    if t.get("people"):
        print(f"  People ({len(t['people'])}):")
        for p in t["people"]:
            handles_str = ""
            for platform, entries in p.get("handles", {}).items():
                for e in entries:
                    h = e.get("handle", e.get("name", e.get("url", "")))
                    handles_str += f" {platform}:{h}"
            print(f"    {p.get('role','')}: {p['name']}{handles_str}")
    if t.get("social_handles"):
        print(f"  All handles: {json.dumps(t['social_handles'], indent=4)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="VURT Content Programming Grid reader")
    parser.add_argument("--all", action="store_true", help="List all titles")
    parser.add_argument("--show", type=str, help="Get info for a specific show")
    parser.add_argument("--handles", type=str, help="Get social handles for a show (pulls from comments)")
    parser.add_argument("--live", action="store_true", help="Show only Live on VURT titles")
    parser.add_argument("--scheduled", action="store_true", help="Show only Scheduled titles")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.handles:
        t = get_title_with_handles(args.handles)
        if t:
            if args.json:
                print(json.dumps(t, indent=2))
            else:
                print_title(t)
        else:
            print(f"No title matching '{args.handles}' found.")

    elif args.show:
        t = get_title_info(args.show)
        if t:
            if args.json:
                print(json.dumps(t, indent=2))
            else:
                print_title(t)
        else:
            print(f"No title matching '{args.show}' found.")

    elif args.live or args.scheduled:
        titles = get_all_titles()
        filter_list = "Live on VURT" if args.live else "Scheduled"
        filtered = [t for t in titles if t["list"] == filter_list]
        print(f"{len(filtered)} titles in '{filter_list}':\n")
        for t in filtered:
            print_title(t)
            print()

    elif args.all:
        titles = get_all_titles()
        if args.json:
            print(json.dumps(titles, indent=2))
        else:
            from collections import Counter
            by_list = Counter(t["list"] for t in titles)
            for list_name, count in by_list.most_common():
                print(f"\n=== {list_name} ({count}) ===")
                for t in titles:
                    if t["list"] == list_name:
                        print(f"  {t['title']} — {t.get('director_producer','')}")
    else:
        parser.print_help()
