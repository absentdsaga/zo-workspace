#!/usr/bin/env python3
"""
Enveu CMS SEO Field Filler for VURT (v3)

Uses show_metadata.json (from VURT Social Media Production Tracker spreadsheet)
for real descriptions, genres, cast, and keywords.

v3 changes from v2:
- Title: "Watch Free" moved before brand, 60-char hard limit
- Description: synopsis-first with cast + episode count, unique per item
- Long description: synopsis + credits + format + CTA (not boilerplate)
- Parental rating: genre-aware (not blanket MA)
- Content tags: genre/culture/mood only (no platform marketing)
- Keywords: includes cast names, director, competitor terms
- Year in movie titles
- Trailer title dedup fix

Usage:
    python3 enveu-seo.py audit
    python3 enveu-seo.py preview --show "Karma In Heels"
    python3 enveu-seo.py preview --id 3742
    python3 enveu-seo.py fill --id 90
    python3 enveu-seo.py fill --show "Karma In Heels"
    python3 enveu-seo.py fill --all --confirm
    python3 enveu-seo.py export-csv
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

BASE_URL = "https://studio-api-us1.enveu.tv/media-centre/studio/api"
RATE_LIMIT_DELAY = 0.5
SCRIPT_DIR = Path(__file__).parent
MAX_TITLE_LEN = 60
MAX_DESC_LEN = 155

SHOW_NAME_OVERRIDES = {
    "mardigras": "Mardi Gras",
    "mardi gras": "Mardi Gras",
    "myfirstlove": "My First Love",
    "my first love": "My First Love",
    "karma in heels": "Karma In Heels",
    "karmainheels": "Karma In Heels",
    "marry me for christmas": "Marry Me For Christmas",
    "something like business": "Something Like Business",
    "the parking lot": "The Parking Lot",
    "come back dad": "Come Back Dad",
    "comebackdad": "Come Back Dad",
    "chicago boogie": "Chicago Boogie",
    "the love letter": "The Love Letter",
    "shadows of tomorrow": "Shadows of Tomorrow",
    "bitterpill": "Bitter Pill",
    "bitter pill": "Bitter Pill",
    "babymama": "My Baby Mama",
    "baby mama": "My Baby Mama",
    "another merry deranged": "Another Merry Deranged Holy Unhinged Christmas Affair",
    "baby daddy alibi 2": "Baby Daddy Alibi",
    "double deception e1": "Double Deception",
    "double deception e10": "Double Deception",
    "double deception e11": "Double Deception",
    "double deception e12": "Double Deception",
    "double deception e13": "Double Deception",
    "double deception e14": "Double Deception",
    "double deception e15": "Double Deception",
    "legallovedurham": "Legal Love",
    "legal love": "Legal Love",
    "loveletter": "The Love Letter",
    "love letter": "The Love Letter",
    "my first love": "My First Love",
    "thug holiday": "Thug Holiday",
    "thechurchboy": "The Church Boy",
    "the church boy": "The Church Boy",
    "lowkeyhustle": "Low Key Hustle",
    "low key hustle": "Low Key Hustle",
    "lord all men cant be dogs": "Lord All Men Can't Be Dogs",
    "womanof god": "Woman of God",
    "woman of god": "Woman of God",
    "husband material": "Husband Material",
    "miamiconfidential": "Miami Confidential",
    "miami confidential": "Miami Confidential",
    "wrong choice jan8": "Wrong Choice",
    "wrong choice": "Wrong Choice",
    "girlinthe closet": "Girl in the Closet",
    "girl in the closet": "Girl in the Closet",
    "lifehappened": "Life Happened",
    "life happened": "Life Happened",
    "bmon": "BMON",
    "mr and mrs right": "Mr and Mrs Right",
    "mr babysitter": "Mr Babysitter",
    "framedbymy ex": "Framed by My Ex",
    "framed by my ex": "Framed by My Ex",
    "saving westbrook": "Saving Westbrook",
    "pride and prejudice atl": "Pride and Prejudice ATL",
    "killer stepdad": "Killer Stepdad",
    "fellin love witha fed": "Fell in Love with a Fed",
    "fell in love with a fed": "Fell in Love with a Fed",
    "one nightin lagos": "One Night in Lagos",
    "one night in lagos": "One Night in Lagos",
    "songof love": "Song of Love",
    "song of love": "Song of Love",
    "the special one": "The Special One",
    "lil duval living my best life": "Lil Duval Living My Best Life",
    "diftg": "DIFTG",
    "tara mist": "Tara Mist",
    "welcome to the a": "Welcome to the A",
    "miami kingpins": "Miami Kingpins",
    "beyond the horizon": "Beyond the Horizon",
    "the last melody": "The Last Melody",
    "the last message": "The Last Message",
    "35 & ticking": "35 and Ticking",
}

SPREADSHEET_ALIASES = {
    "mardi gras": "mardi gras reunion",
    "something like business": "something like a business",
    "baby daddy alibi 2": "baby daddy alibi",
    "another merry deranged": "another merry deranged holy unhinged christmas affair",
    "35 & ticking": "35 and ticking",
    "my baby mama": "my baby mama",
    "baby mama": "my baby mama",
    "bitter pill": "bitter pill",
    "girl in the closet": "girl in the closet",
    "pride and prejudice atl": "pride and prejudice atl",
    "saving westbrook": "saving westbrook",
    "killer stepdad": "killer stepdad",
    "lord all men can't be dogs": "lord all men can't be dogs",
    "fell in love with a fed": "fell in love with a fed",
    "one night in lagos": "one night in lagos",
    "lil duval living my best life": "lil duval living my best life",
}

# Genre -> culture mapping (items can have multiple cultures)
# Culture tags are applied per-show via metadata, NOT blanket.
# Only map genres to their *specific* culture when it's distinctive.
GENRE_TO_CULTURE = {
    "Horror": ["horror culture"],
    "Slasher": ["horror culture"],
    "Psychological Thriller": ["horror culture"],
    "Music": ["hip hop culture"],
    "Stand-Up": ["hip hop culture"],
    "Reality": ["hip hop culture"],
    "Lifestyle": ["hip hop culture"],
    "Cooking": ["hip hop culture"],
    "Film Noir": ["film noir"],
}
# Shows get culture tags from their metadata "culture" field (if set),
# or from genre mapping above.  No blanket "black cinema" on everything.

# Genre -> parental rating defaults
GENRE_RATING_MAP = {
    "Horror": "TV-MA",
    "Slasher": "TV-MA",
    "Crime": "TV-MA",
    "Thriller": "TV-MA",
    "Psychological Thriller": "TV-MA",
    "Action": "TV-14",
    "Drama": "TV-14",
    "Romance": "TV-14",
    "Comedy": "TV-14",
    "Documentary": "TV-14",
    "Music": "TV-14",
    "Musical": "TV-14",
    "Mystery": "TV-14",
    "Suspense": "TV-14",
    "Sport": "TV-14",
    "Stand-Up": "TV-14",
    "Reality": "TV-14",
    "Family": "TV-PG",
    "Holiday": "TV-PG",
    "Lifestyle": "TV-PG",
    "Cooking": "TV-PG",
}

# Explicit rating normalization
RATING_NORMALIZE = {
    "R": "TV-MA",
    "PG-13": "TV-14",
    "PG": "TV-PG",
    "G": "TV-G",
    "NC-17": "TV-MA",
    "NR": "TV-14",
    "TV-MA": "TV-MA",
    "TV-14": "TV-14",
    "TV-PG": "TV-PG",
    "TV-G": "TV-G",
}

# ---------------------------------------------------------------------------
# Metadata Loader
# ---------------------------------------------------------------------------

_show_metadata_cache = None

def load_show_metadata() -> dict:
    global _show_metadata_cache
    if _show_metadata_cache is not None:
        return _show_metadata_cache
    meta_path = SCRIPT_DIR / "show_metadata.json"
    if not meta_path.exists():
        print(f"WARNING: {meta_path} not found. Using generated-only SEO.")
        _show_metadata_cache = {}
        return _show_metadata_cache
    with open(meta_path) as f:
        _show_metadata_cache = json.load(f)
    return _show_metadata_cache


def lookup_show(show_name: str) -> dict | None:
    meta = load_show_metadata()
    key = show_name.lower().strip()
    if key in meta:
        return meta[key]
    alias_key = SPREADSHEET_ALIASES.get(key)
    if alias_key and alias_key in meta:
        return meta[alias_key]
    if key.startswith("the "):
        bare = key[4:]
        if bare in meta:
            return meta[bare]
    return None


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

class EnveuClient:
    def __init__(self):
        self.auth_token = os.environ.get("ENVEU_AUTH_TOKEN")
        self.project_id = os.environ.get("ENVEU_PROJECT_ID")
        self.tenant_id = os.environ.get("ENVEU_TENANT_ID")
        missing = []
        if not self.auth_token: missing.append("ENVEU_AUTH_TOKEN")
        if not self.project_id: missing.append("ENVEU_PROJECT_ID")
        if not self.tenant_id: missing.append("ENVEU_TENANT_ID")
        if missing:
            print(f"ERROR: Missing environment variables: {', '.join(missing)}")
            sys.exit(1)
        self.session = requests.Session()
        self.session.headers.update({
            "A_t": self.auth_token,
            "P_i": self.project_id,
            "T_i": self.tenant_id,
            "Content-Type": "application/json",
        })

    def list_all(self, page=0, size=30):
        url = f"{BASE_URL}/v5_0/mediaContent/listAll"
        resp = self.session.post(url, json={"page": page, "size": size}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_item(self, media_content_id: int):
        url = f"{BASE_URL}/v5_0/mediaContent"
        resp = self.session.get(url, params={"mediaContentId": media_content_id}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update_item(self, full_object: dict):
        url = f"{BASE_URL}/v5_0/mediaContent/update"
        resp = self.session.patch(url, json=full_object, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def fetch_all_items(self, progress=True):
        items = []
        page = 0
        total_pages = None
        while True:
            if progress:
                label = f"{page + 1}/{total_pages}" if total_pages else f"{page + 1}"
                print(f"\r  Fetching page {label} ...", end="", flush=True)
            try:
                result = self.list_all(page=page, size=30)
            except requests.RequestException as e:
                print(f"\n  ERROR on page {page}: {e}")
                break
            data = result.get("data", {})
            page_items = data.get("items", [])
            if not page_items:
                break
            items.extend(page_items)
            if total_pages is None:
                total_pages = data.get("totalPages", 0)
                total_elements = data.get("totalElements", 0)
                if progress:
                    print(f"\r  Total items: {total_elements}, pages: {total_pages}       ")
            page += 1
            if total_pages and page >= total_pages:
                break
            time.sleep(RATE_LIMIT_DELAY)
        if progress:
            print(f"\n  Fetched {len(items)} items total.")
        return items


# ---------------------------------------------------------------------------
# Title Parsing
# ---------------------------------------------------------------------------

def parse_title(raw_title: str) -> dict:
    if not raw_title:
        return {"show": "", "episode": None, "raw": raw_title or ""}
    title = raw_title.strip()
    episode = None
    ep_match = re.search(r'[_\s-]?[Ee][Pp]\.?\s*(\d+)', title)
    if ep_match:
        episode = int(ep_match.group(1))
        title_for_show = title[:ep_match.start()]
    else:
        title_for_show = title

    title_for_show = re.sub(r'^VURT[_\s]+', '', title_for_show, flags=re.IGNORECASE)
    title_for_show = re.sub(r'[_-](?:9x16|16x9|v\d+)\s*$', '', title_for_show, flags=re.IGNORECASE)
    title_for_show = re.sub(r'[_-](?:9x16|16x9|v\d+)$', '', title_for_show, flags=re.IGNORECASE)
    title_for_show = title_for_show.strip(" _-")

    show_name = _humanize_show_name(title_for_show)
    show_lower = show_name.lower().strip()
    if show_lower in SHOW_NAME_OVERRIDES:
        show_name = SHOW_NAME_OVERRIDES[show_lower]
    show_nospace = show_lower.replace(" ", "")
    if show_nospace in SHOW_NAME_OVERRIDES:
        show_name = SHOW_NAME_OVERRIDES[show_nospace]

    return {"show": show_name, "episode": episode, "raw": raw_title}


def _humanize_show_name(name):
    if not name:
        return ""
    if " " in name and not name.isupper():
        return _title_case(name)
    name = name.replace("_", " ")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return _title_case(name)


def _title_case(s):
    words = s.split()
    if not words:
        return ""
    small_words = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "but", "or", "me"}
    result = []
    for i, w in enumerate(words):
        if i == 0 or w.lower() not in small_words:
            result.append(w.capitalize())
        else:
            result.append(w.lower())
    return " ".join(result)


# ---------------------------------------------------------------------------
# SEO Generation (v3)
# ---------------------------------------------------------------------------

TYPE_MICRO_EPISODES = "MICRO_EPISODES"
TYPE_MICRO_SEASON = "MICRO_SEASON"
TYPE_MICRO_DRAMA_SERIES = "MICRO_DRAMA_SERIES"
TYPE_SERIES = "Series"
TYPE_MOVIE = "Movies"
TYPE_CLIP = "Clips"
TYPE_TRAILER = "Trailers"


def get_content_type(item: dict) -> str:
    ct = item.get("mediaType") or ""
    if ct: return ct
    ct = item.get("mediaContentType") or ""
    if ct: return ct
    ct_id = item.get("contentTypeId")
    if ct_id == 15: return TYPE_MICRO_DRAMA_SERIES
    if ct_id == 14: return TYPE_SERIES
    return "UNKNOWN"


def _truncate_title(title: str, max_len: int = MAX_TITLE_LEN) -> str:
    if len(title) <= max_len:
        return title
    pipe_idx = title.rfind("|")
    if pipe_idx > 0:
        suffix = title[pipe_idx:]
        available = max_len - len(suffix) - 3
        if available > 10:
            return title[:available].rstrip() + "..." + suffix
    return title[:max_len - 3].rstrip() + "..."


def _clean_synopsis(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    if text.lower().startswith("description - "):
        text = text[14:]
    return text


def _is_trailer(item: dict, parsed: dict) -> bool:
    ct = get_content_type(item)
    if ct == TYPE_TRAILER:
        return True
    raw = (parsed.get("raw") or "").lower()
    return "trailer" in raw


def generate_seo(item: dict, parsed: dict) -> dict:
    show = parsed["show"] or "Untitled"
    episode = parsed["episode"]
    content_type = get_content_type(item)
    is_trailer = _is_trailer(item, parsed)
    meta = lookup_show(show)

    year = meta.get("year", "") if meta else ""

    # --- SEO Title (v3: "Watch Free" before brand, 60 char limit) ---
    if is_trailer:
        seo_title = f"{show} - Official Trailer | VURT"
        seo_heading = f"{show} - Official Trailer"
    elif content_type == TYPE_MICRO_EPISODES and episode is not None:
        seo_title = f"{show} Ep {episode} | Watch Free on VURT"
        seo_heading = f"{show} Episode {episode}"
    elif content_type == TYPE_MICRO_SEASON:
        seo_title = f"{show} Season {episode or 1} | Stream Free on VURT"
        seo_heading = f"{show} Season {episode or 1}"
    elif content_type in (TYPE_MICRO_DRAMA_SERIES, TYPE_SERIES):
        seo_title = f"{show} - Free Micro-Series | VURT"
        seo_heading = show
    elif content_type == TYPE_MOVIE:
        if year:
            seo_title = f"{show} ({year}) | Watch Free on VURT"
        else:
            seo_title = f"{show} | Watch Free on VURT"
        seo_heading = show
    else:
        if episode is not None:
            seo_title = f"{show} Ep {episode} | Watch Free on VURT"
            seo_heading = f"{show} Episode {episode}"
        else:
            seo_title = f"{show} | Watch Free on VURT"
            seo_heading = show

    seo_title = _truncate_title(seo_title)

    # --- SEO Description (v3: synopsis-first, cast, episode count) ---
    synopsis = _clean_synopsis(meta.get("description", "")) if meta else ""
    cast_names = meta.get("cast", [])[:3] if meta else []
    cast_str = ", ".join(cast_names) if cast_names else ""

    if synopsis:
        if episode is not None:
            seo_desc = f"Watch {show} Ep {episode} free on VURT. {synopsis[:90]}"
        else:
            seo_desc = f"Watch {show} free on VURT. {synopsis[:90]}"
        if cast_str and len(seo_desc) + len(f" Starring {cast_names[0]}.") <= MAX_DESC_LEN:
            seo_desc += f" Starring {cast_names[0]}."
    else:
        genres = meta.get("genres", []) if meta else []
        genre_str = ", ".join(genres[:2]).lower() if genres else "micro-drama"
        if episode is not None:
            seo_desc = f"Watch {show} Ep {episode} free on VURT. A {genre_str} micro-series. No paywall, no subscription."
        else:
            seo_desc = f"Watch {show} free on VURT. A {genre_str} micro-series. No paywall, no subscription."

    if len(seo_desc) > MAX_DESC_LEN + 5:
        seo_desc = seo_desc[:MAX_DESC_LEN - 3].rstrip() + "..."

    # --- Description (short, CMS field - pure synopsis) ---
    if synopsis:
        description = synopsis
    else:
        if episode is not None:
            description = f"{show} Episode {episode}. Watch free on VURT."
        else:
            description = f"{show}. Watch free on VURT."

    # --- Long Description (v3: synopsis + credits + format + CTA) ---
    long_desc = _generate_long_description(show, episode, content_type, meta, year)

    # --- SEO Tags ---
    seo_tags = _generate_seo_tags(show, content_type, meta, cast_names)

    # --- Content Tags (v3: genre/culture/mood ONLY, no platform marketing) ---
    content_tags = _generate_content_tags(show, content_type, meta, cast_names)

    # --- Keywords (v3: includes cast, director, competitor terms) ---
    keywords = _generate_keywords(show, content_type, meta)

    # --- Parental Rating (v3: genre-aware) ---
    rating = _determine_rating(meta)

    return {
        "seo_title": seo_title,
        "seo_description": seo_desc,
        "seo_tags": seo_tags,
        "seo_heading": seo_heading,
        "description": description,
        "long_description": long_desc,
        "keywords": keywords,
        "content_tags": content_tags,
        "parentalRating": rating,
        "meta_source": "spreadsheet" if meta else "generated",
    }


def _generate_long_description(show, episode, content_type, meta, year):
    parts = []

    synopsis = _clean_synopsis(meta.get("description", "")) if meta else ""
    if synopsis:
        parts.append(synopsis)

    if meta:
        credits = []
        if meta.get("director"):
            credits.append(f"Directed by {meta['director']}.")
        if meta.get("cast"):
            top_cast = meta["cast"][:5]
            credits.append(f"Starring {', '.join(top_cast)}.")
        if credits:
            parts.append(" ".join(credits))

    # Format line
    genres = meta.get("genres", []) if meta else []
    genre_str = ", ".join(genres[:3]) if genres else ""
    ct_label = "micro-series" if content_type in (TYPE_MICRO_EPISODES, TYPE_MICRO_DRAMA_SERIES, TYPE_SERIES) else "film"
    if content_type == TYPE_MOVIE:
        ct_label = "film"

    format_parts = []
    if year:
        format_parts.append(f"({year})")
    if genre_str:
        format_parts.append(genre_str)
    if format_parts:
        parts.append(f"A VURT original {ct_label} {' -- '.join(format_parts)}.")

    if episode is not None:
        parts.append(f"Watch Episode {episode} free on VURT. Vertical-first streaming designed for your phone. No paywall, no subscription. Stream at myvurt.com.")
    else:
        parts.append("Watch free on VURT. Vertical-first streaming designed for your phone. No paywall, no subscription. Stream at myvurt.com.")

    return " ".join(parts)


def _generate_seo_tags(show, content_type, meta, cast_names):
    tags = [show.lower(), "VURT", "watch free", "free streaming", "no paywall"]

    if meta and meta.get("genres"):
        for g in meta["genres"][:4]:
            tag = g.lower()
            if tag not in [t.lower() for t in tags]:
                tags.append(tag)

    for actor in cast_names:
        if actor.strip():
            tags.append(actor.strip().lower())

    if meta and meta.get("director"):
        tags.append(meta["director"].lower())

    type_tags = {
        TYPE_MICRO_EPISODES: "micro-series",
        TYPE_MICRO_SEASON: "full season",
        TYPE_MICRO_DRAMA_SERIES: "micro-series",
        TYPE_SERIES: "micro-series",
        TYPE_MOVIE: "movie",
        TYPE_TRAILER: "trailer",
    }
    if content_type in type_tags:
        tags.append(type_tags[content_type])

    tags.extend(["vertical drama", "mobile streaming", "myvurt"])
    return _dedup(tags)


def _generate_content_tags(show, content_type, meta, cast_names):
    """v3: Content tags are for discovery/recommendation only.
    No platform marketing terms. Genre + culture + mood + talent + theme."""
    tags = []

    # Genre tags
    if meta and meta.get("genres"):
        for g in meta["genres"]:
            tags.append(g.lower())

    # Culture tags from metadata or genre mapping
    cultures_added = set()
    if meta and meta.get("culture"):
        for c in (meta["culture"] if isinstance(meta["culture"], list) else [meta["culture"]]):
            c = c.strip().lower()
            if c and c not in cultures_added:
                tags.append(c)
                cultures_added.add(c)
    if meta and meta.get("genres"):
        for g in meta["genres"]:
            for culture in GENRE_TO_CULTURE.get(g, GENRE_TO_CULTURE.get(g.title(), [])):
                if culture not in cultures_added:
                    tags.append(culture)
                    cultures_added.add(culture)

    # Show name
    tags.append(show.lower())

    # Content type
    if content_type in (TYPE_MICRO_EPISODES, TYPE_MICRO_DRAMA_SERIES, TYPE_SERIES):
        tags.append("micro-series")
    elif content_type == TYPE_MOVIE:
        tags.append("movie")

    # Talent tags (for cast-driven discovery)
    for actor in cast_names[:3]:
        if actor.strip():
            tags.append(actor.strip().lower())

    # Mood/vibe tags from genre
    if meta and meta.get("genres"):
        genre_set = {g.lower() for g in meta["genres"]}
        if "romance" in genre_set:
            tags.append("date-night")
        if "comedy" in genre_set:
            tags.append("feel-good")
        if genre_set & {"thriller", "crime", "horror", "suspense", "mystery"}:
            tags.append("edge-of-your-seat")
        if "holiday" in genre_set:
            tags.append("holiday-vibes")
        if "family" in genre_set:
            tags.append("family-watch")
        if genre_set & {"drama", "romance"}:
            tags.append("binge-worthy")

    return _dedup(tags)


def _generate_keywords(show, content_type, meta):
    keywords = [show.lower(), "vurt", "free streaming", "watch free", "no paywall", "myvurt"]

    if meta:
        if meta.get("genres"):
            for g in meta["genres"][:4]:
                kw = g.lower()
                if kw not in keywords:
                    keywords.append(kw)

        if meta.get("cast"):
            for actor in meta["cast"][:3]:
                kw = actor.strip().lower()
                if kw and kw not in keywords:
                    keywords.append(kw)

        if meta.get("director"):
            kw = meta["director"].strip().lower()
            if kw and kw not in keywords:
                keywords.append(kw)

        if meta.get("keywords") and meta["keywords"].strip():
            for kw in meta["keywords"].split(","):
                kw = kw.strip().lower()
                if kw and kw not in keywords:
                    keywords.append(kw)

    keywords.extend(["vertical video", "micro drama", "mobile streaming",
                     "micro-series", "free drama app",
                     "binge worthy", "short form series"])

    return _dedup(keywords)


def _determine_rating(meta) -> str:
    if meta and meta.get("rating"):
        normalized = RATING_NORMALIZE.get(meta["rating"].strip(), "")
        if normalized:
            return normalized

    if meta and meta.get("genres"):
        # Use most restrictive genre
        priority = ["TV-MA", "TV-14", "TV-PG", "TV-G"]
        best = "TV-14"  # default
        for g in meta["genres"]:
            r = GENRE_RATING_MAP.get(g, "TV-14")
            if priority.index(r) < priority.index(best):
                best = r
        return best

    return "TV-MA"  # safe default when no genre info


def _dedup(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_audit(client, args):
    print("=== ENVEU SEO AUDIT (v3) ===\n")
    items = client.fetch_all_items()
    if not items:
        print("No items found."); return

    stats = {
        "total": len(items),
        "empty_seo_title": 0, "empty_seo_desc": 0, "empty_seo_tags": 0,
        "empty_seo_heading": 0, "empty_description": 0, "empty_long_description": 0,
        "empty_keywords": 0, "empty_targeting_tags": 0,
        "null_parental_rating": 0, "has_spreadsheet_match": 0, "unparseable_title": 0,
        "by_type": {},
    }

    for item in items:
        content_type = get_content_type(item)
        seo_info = item.get("seoInfo") or {}
        stats["by_type"].setdefault(content_type, 0)
        stats["by_type"][content_type] += 1

        parsed = parse_title(item.get("title", "") or "")
        meta = lookup_show(parsed["show"]) if parsed["show"] else None
        if meta: stats["has_spreadsheet_match"] += 1
        if not parsed["show"]: stats["unparseable_title"] += 1

        if not (seo_info.get("title") or "").strip(): stats["empty_seo_title"] += 1
        if not (seo_info.get("description") or "").strip(): stats["empty_seo_desc"] += 1
        if not seo_info.get("tags"): stats["empty_seo_tags"] += 1
        if not (seo_info.get("heading") or "").strip(): stats["empty_seo_heading"] += 1
        if not (item.get("description") or "").strip(): stats["empty_description"] += 1
        if not (item.get("longDescription") or "").strip(): stats["empty_long_description"] += 1
        if not item.get("keywords"): stats["empty_keywords"] += 1
        if not item.get("targetingTags"): stats["empty_targeting_tags"] += 1
        if not item.get("parentalRating"): stats["null_parental_rating"] += 1

    print(f"Total items:              {stats['total']}")
    print(f"Spreadsheet matches:      {stats['has_spreadsheet_match']}")
    print(f"Empty seoInfo.title:      {stats['empty_seo_title']}")
    print(f"Empty seoInfo.description:{stats['empty_seo_desc']}")
    print(f"Empty description:        {stats['empty_description']}")
    print(f"Empty longDescription:    {stats['empty_long_description']}")
    print(f"Empty keywords:           {stats['empty_keywords']}")
    print(f"Empty targetingTags:      {stats['empty_targeting_tags']}")
    print(f"Null parentalRating:      {stats['null_parental_rating']}")
    print(f"\n--- BY CONTENT TYPE ---")
    for ct, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {ct}: {count}")


def cmd_preview(client, args):
    print("=== ENVEU SEO PREVIEW v3 (dry run) ===\n")

    if hasattr(args, 'id') and args.id is not None:
        try:
            result = client.get_item(args.id)
        except Exception as e:
            print(f"ERROR fetching item {args.id}: {e}"); return
        item_data = result.get("data", result)
        _preview_item(item_data)
        return

    items = client.fetch_all_items()
    if not items:
        print("No items found."); return

    show_filter = (args.show or "").strip().lower() if args.show else None
    if not show_filter and not args.all:
        print("ERROR: Must specify --show, --all, or --id"); sys.exit(1)

    count = 0
    for item in items:
        title = item.get("title", "") or ""
        parsed = parse_title(title)
        if show_filter and parsed["show"].lower() != show_filter:
            continue
        _preview_item(item)
        count += 1
    print(f"Total items previewed: {count}")


def _preview_item(item):
    title = item.get("title", "") or ""
    item_id = item.get("id", "?")
    content_type = get_content_type(item)
    parsed = parse_title(title)
    seo = generate_seo(item, parsed)

    print(f"--- Item {item_id}: {title} ({content_type}) ---")
    print(f"  Source:               {seo['meta_source']}")
    print(f"  seoInfo.title:        {seo['seo_title']} ({len(seo['seo_title'])} chars)")
    print(f"  seoInfo.desc:         {seo['seo_description']}")
    print(f"  seoInfo.heading:      {seo['seo_heading']}")
    print(f"  description:          {seo['description'][:100]}...")
    print(f"  longDescription:      {seo['long_description'][:120]}...")
    print(f"  keywords:             {', '.join(seo['keywords'][:8])}...")
    print(f"  contentTags:          {', '.join(seo['content_tags'][:10])}...")
    print(f"  parentalRating:       {seo['parentalRating']}")
    print()


def cmd_fill(client, args):
    if args.all and not args.confirm:
        print("ERROR: --all requires --confirm flag.")
        sys.exit(1)

    if not args.show and not args.all and args.id is None:
        print("ERROR: Must specify --show, --all, or --id")
        sys.exit(1)

    print("=== ENVEU SEO FILL v3 ===\n")

    if args.id is not None:
        _fill_single_item(client, args.id)
        return

    items = client.fetch_all_items()
    if not items:
        print("No items found."); return

    show_filter = (args.show or "").strip().lower() if args.show else None
    targets = []
    for item in items:
        title = item.get("title", "") or ""
        parsed = parse_title(title)
        if show_filter and parsed["show"].lower() != show_filter:
            continue
        targets.append((item, parsed))

    if not targets:
        print("No items matched filter."); return

    print(f"Will update {len(targets)} items.\n")
    changes_log = []

    for i, (item, parsed) in enumerate(targets):
        item_id = item.get("id")
        title = item.get("title", "")
        print(f"[{i+1}/{len(targets)}] Updating item {item_id}: {title}")
        change = _fill_item(client, item_id, parsed)
        if change:
            changes_log.append(change)
        time.sleep(RATE_LIMIT_DELAY)

    _save_changes_log(changes_log)
    print(f"\nDone. Updated {len(changes_log)} items.")


def _fill_single_item(client, item_id):
    print(f"Fetching item {item_id} ...")
    try:
        result = client.get_item(item_id)
    except requests.RequestException as e:
        print(f"ERROR: {e}"); return
    item_data = result.get("data", result)
    title = item_data.get("title", "") or ""
    parsed = parse_title(title)
    print(f"  Title: {title}")
    print(f"  Parsed: show={parsed['show']}, episode={parsed['episode']}")
    change = _fill_item(client, item_id, parsed)
    if change:
        _save_changes_log([change])
        print("Done.")


def _fill_item(client, item_id, parsed):
    try:
        result = client.get_item(item_id)
    except requests.RequestException as e:
        print(f"  ERROR fetching: {e}"); return None

    full_obj = result.get("data", result)
    content_type = get_content_type(full_obj)
    seo = generate_seo(full_obj, parsed)

    # SEO info (always overwrite)
    if "seoInfo" not in full_obj or full_obj["seoInfo"] is None:
        full_obj["seoInfo"] = {}
    full_obj["seoInfo"]["title"] = seo["seo_title"]
    full_obj["seoInfo"]["description"] = seo["seo_description"]
    full_obj["seoInfo"]["tags"] = seo["seo_tags"]
    full_obj["seoInfo"]["heading"] = seo["seo_heading"]

    # Only fill if empty
    if not (full_obj.get("description") or "").strip():
        full_obj["description"] = seo["description"]
    if not (full_obj.get("longDescription") or "").strip():
        full_obj["longDescription"] = seo["long_description"]
    if not full_obj.get("keywords"):
        full_obj["keywords"] = seo["keywords"]
    if not full_obj.get("targetingTags"):
        full_obj["targetingTags"] = seo["content_tags"]
    if not full_obj.get("parentalRating"):
        full_obj["parentalRating"] = seo["parentalRating"]

    try:
        client.update_item(full_obj)
        print(f"  Updated item {item_id} OK ({seo['meta_source']})")
    except requests.RequestException as e:
        print(f"  ERROR updating: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try: print(f"  Response: {e.response.text[:500]}")
            except: pass
        return None

    return {
        "id": item_id,
        "title": full_obj.get("title", ""),
        "content_type": content_type,
        "parsed_show": parsed["show"],
        "parsed_episode": parsed["episode"],
        "meta_source": seo["meta_source"],
        "rating": seo["parentalRating"],
        "timestamp": datetime.now().isoformat(),
    }


def _classify_item(title, content_type, parsed, meta):
    """Classify item status for v2 CSV."""
    title_lower = (title or "").lower().strip()

    if any(title_lower.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif', '.webp', '.svg', '.mp4', '.mov']):
        return "asset-image", "Filename as title — likely a thumbnail/banner/test upload"
    if not title_lower:
        return "blank", "No title — test or incomplete upload"
    if content_type in ("16x9", "9x16", "1x1") and not parsed.get("episode"):
        if any(title_lower.endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
            return "asset-image", "Image asset in aspect ratio bucket"
        if len(title_lower) < 5 or title_lower.startswith("pexels-") or title_lower.startswith("gratisography"):
            return "asset-image", "Stock photo / placeholder"
        return "asset-maybe", f"Aspect ratio type ({content_type}) with no episode — verify if real content"

    if "trailer" in title_lower:
        if meta:
            return "actionable", "Trailer with metadata"
        return "actionable-generic", "Trailer — no show metadata"

    if meta:
        has_desc = bool((meta.get("description") or "").strip())
        has_cast = bool(meta.get("cast"))
        if has_desc and has_cast:
            return "actionable", "Full metadata available"
        missing = []
        if not has_desc: missing.append("synopsis")
        if not has_cast: missing.append("cast")
        return "actionable-partial", f"Has metadata but missing: {', '.join(missing)}"

    show = parsed.get("show", "").strip()
    if not show:
        return "unclassified", "Could not parse show name from title"

    return "needs-metadata", f"No metadata for '{show}' — getting generic SEO copy"


def cmd_export_csv(client, args):
    """Export all items with current vs proposed SEO for review."""
    version = getattr(args, 'v2', False)
    label = "v2" if version else "v3"
    print(f"=== EXPORT SEO PREVIEW CSV ({label}) ===\n")
    items = client.fetch_all_items()
    if not items:
        print("No items found."); return

    rows = []
    status_counts = {}
    for item in items:
        item_id = item.get("id", "?")
        title = item.get("title", "") or ""
        content_type = get_content_type(item)
        parsed = parse_title(title)
        seo = generate_seo(item, parsed)
        meta = lookup_show(parsed["show"]) if parsed["show"] else None

        cur_seo = item.get("seoInfo") or {}
        cur_desc = (item.get("description") or "").strip()
        cur_long = (item.get("longDescription") or "").strip()
        cur_kw = item.get("keywords") or []
        cur_tags = item.get("targetingTags") or []
        cur_rating = item.get("parentalRating") or ""

        status, review_flag = _classify_item(title, content_type, parsed, meta)
        status_counts[status] = status_counts.get(status, 0) + 1

        row = {
            "ID": item_id,
            "Status": status,
            "Review Flag": review_flag,
            "CMS Title": title,
            "Content Type": content_type,
            "Parsed Show": parsed["show"],
            "Episode": parsed["episode"] or "",
            "Source": seo["meta_source"],
            "Current SEO Title": cur_seo.get("title", ""),
            "NEW SEO Title": seo["seo_title"],
            "Current Description": cur_desc if cur_desc else "(empty)",
            "NEW Description": seo["description"],
            "Current Long Desc": cur_long if cur_long else "(empty)",
            "NEW Long Desc": seo["long_description"],
            "Current Keywords": ", ".join(cur_kw) if cur_kw else "(empty)",
            "NEW Keywords": ", ".join(seo["keywords"]),
            "Current Tags": ", ".join(cur_tags) if cur_tags else "(empty)",
            "NEW Content Tags": ", ".join(seo["content_tags"]),
            "Current Rating": cur_rating or "(empty)",
            "NEW Rating": seo["parentalRating"],
            "NEW SEO Desc": seo["seo_description"],
            "NEW Heading": seo["seo_heading"],
        }
        rows.append(row)

    # Sort: actionable first, then needs-metadata, then assets/blanks
    status_order = {"actionable": 0, "actionable-partial": 1, "actionable-generic": 2,
                    "needs-metadata": 3, "asset-maybe": 4, "unclassified": 5,
                    "asset-image": 6, "blank": 7}
    rows.sort(key=lambda r: (status_order.get(r["Status"], 99), r["Parsed Show"], str(r.get("Episode", ""))))

    csv_name = "VURT-SEO-Fill-Preview-v2.csv" if version else "VURT-SEO-Fill-Preview.csv"
    csv_path = Path(f"/home/workspace/Documents/{csv_name}")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nExported {len(rows)} items to {csv_path}")
    print(f"\n--- STATUS BREAKDOWN ---")
    for status, count in sorted(status_counts.items(), key=lambda x: status_order.get(x[0], 99)):
        print(f"  {status:<25} {count:>5}")
    print(f"  {'TOTAL':<25} {len(rows):>5}")


def _save_changes_log(changes):
    if not changes: return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = SCRIPT_DIR / f"seo-changes-{ts}.json"
    with open(log_path, "w") as f:
        json.dump(changes, f, indent=2)
    print(f"Changes logged: {log_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Enveu CMS SEO Field Filler v3")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("audit")

    sub_preview = subparsers.add_parser("preview")
    sub_preview.add_argument("--show", type=str)
    sub_preview.add_argument("--all", action="store_true")
    sub_preview.add_argument("--id", type=int)

    sub_fill = subparsers.add_parser("fill")
    sub_fill.add_argument("--show", type=str)
    sub_fill.add_argument("--all", action="store_true")
    sub_fill.add_argument("--confirm", action="store_true")
    sub_fill.add_argument("--id", type=int)

    sub_export = subparsers.add_parser("export-csv")
    sub_export.add_argument("--v2", action="store_true", help="Export v2 format with Status/Review columns")

    args = parser.parse_args()
    if not args.command:
        parser.print_help(); sys.exit(1)

    client = EnveuClient()

    if args.command == "audit":
        cmd_audit(client, args)
    elif args.command == "preview":
        cmd_preview(client, args)
    elif args.command == "fill":
        cmd_fill(client, args)
    elif args.command == "export-csv":
        cmd_export_csv(client, args)


if __name__ == "__main__":
    main()
