#!/usr/bin/env python3
"""Resolve Mux playback IDs to show / episode titles via the public Enveu API.

Mux player config doesn't currently set videoTitle / videoSeries, so the Mux
Data API only knows opaque playback IDs. This script walks the public Enveu
storefront API used by myvurt.com (no auth, just the public x-api-key the
browser uses) and builds a JSON map:

    {
      "<mux_playback_id>": {
        "series_id": 1163,
        "series_title": "Do It For The Gram",
        "episode_id": 1168,
        "episode_title": "Episode 1",
        "episode_no": 1,
        "season_no": null,
        "media_type": "MICRO_SERIES",
        "slug": "do-it-for-the-gram"
      },
      ...
    }

Cache is written to data/mux_title_map.json next to this script's package.
The daily report calls load_map() to enrich top-content rows.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests

API_KEY = "WuxER0N62t73ifozgYFEga8TjXbEKDaX138vt2WC"
MENU_BASE = "https://api-us1.myvurt.com"
BASE_PUBLIC = "https://frontend-api-us1.myvurt.com"
BASE_CF = "https://frontend-api-us1-cf.enveu.io"

HEADERS = {
    "x-api-key": API_KEY,
    "x-platform": "web",
    "x-device": "desktop",
    "x-app-version": "null",
    "x-device-identifier": "null",
    "x-device-name": "null",
    "x-device-platform": "null",
    "x-device-type": "null",
    "x-tracking-sdk-version": "null",
    "Origin": "https://www.myvurt.com",
    "Referer": "https://www.myvurt.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36",
}

OUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_FILE = OUT_DIR / "mux_title_map.json"


def _get(url, params=None, timeout=30):
    resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def list_menu_screens():
    """Return all screen IDs reachable from the main menu (Home, Categories, ...)."""
    url = f"{MENU_BASE}/experience-manager-fe-api/app/api/v2/menuManager/getMenuDetails"
    body = _get(url, params={"locale": "en-US"})
    screens = []
    for it in (body.get("data") or {}).get("orderedMenuItems", []) or []:
        m = it.get("menuItem") or {}
        sid = m.get("screenId")
        if sid:
            screens.append({"screenId": sid, "displayName": m.get("displayName")})
    return screens


def list_screen_playlists(screen_id):
    url = f"{BASE_PUBLIC}/enveu_prod/v2/screen"
    body = _get(url, params={"screenId": screen_id, "locale": "en-US"})
    out = []
    for w in (body.get("data", {}) or {}).get("widgets", []) or []:
        pl = (w.get("item") or {}).get("playlist") or {}
        pid = pl.get("enveuPlaylistId")
        if pid:
            out.append({"playlistId": pid, "name": w.get("name"), "displayOrder": w.get("displayOrder")})
    return out


def list_playlist_contents(playlist_id, page_size=50):
    url = f"{BASE_PUBLIC}/media-centre/fe/api/v5_0/mediaPlaylist/getPlaylistDetails"
    body = _get(url, params={"playlistId": playlist_id, "page": 0, "size": page_size, "locale": "en-US"})
    items = ((body.get("data") or {}).get("contents") or {}).get("items") or []
    return [it.get("content") for it in items if it.get("content")]


def list_series_episodes(series_id, page_size=200):
    url = f"{BASE_PUBLIC}/media-centre/fe/api/v5_0/mediaContent/listAll"
    cd = f"micro-episode-micro-series-id|OR:{series_id}"
    body = _get(url, params={"customData": cd, "page": 0, "size": page_size, "locale": "en-US"})
    return (body.get("data") or {}).get("items") or []


def get_content(content_id):
    url = f"{BASE_PUBLIC}/media-centre/fe/api/v5_0/mediaContent"
    body = _get(url, params={"mediaContentId": content_id, "locale": "en-US"})
    return body.get("data")


def _clean_episode_title(raw, ep_no, series_title):
    """Episode titles are raw filenames like 'VURT_DIFTG_EP01_9x16_v1-'.
    Convert to 'Episode 1' if we have an ep number, else fall back to a tidy
    version of the filename (drop trailing _v1-, dimensions, dashes).
    """
    if ep_no:
        return f"Episode {ep_no}"
    if not raw:
        return series_title or "Untitled"
    s = re.sub(r"_v\d+-?$", "", raw)
    s = re.sub(r"_\d+x\d+", "", s)
    s = s.replace("_", " ").strip(" -")
    return s or (series_title or "Untitled")


def _content_to_entry(content, playback_id=None):
    """Convert an Enveu content payload to a resolver-map entry."""
    if not content:
        return None
    title = content.get("title") or ""
    cd = (content.get("customData") or {}).get("micro-episode-micro-series-id") or {}
    series_title = cd.get("title")
    series_id = cd.get("id")
    media_type = content.get("mediaType") or content.get("contentType") or ""
    v = content.get("video") or {}
    ep_no = v.get("episodeNo")

    if series_title:
        ep_title = _clean_episode_title(title, ep_no, series_title)
    elif "TRAILER" in media_type.upper():
        # Trailer titles look like "KARMA_IN_HEELS_TRAILER_MASTER_9x16" -- split
        # on TRAILER to peel off a series-ish name.
        m = re.split(r"[_ ]TRAILER", title, maxsplit=1, flags=re.IGNORECASE)
        guess = m[0].replace("_", " ").title().strip() if m else title
        series_title = guess
        ep_title = "Trailer"
    else:
        series_title = title
        ep_title = title

    return {
        "series_id": series_id or content.get("id"),
        "series_title": series_title,
        "episode_id": content.get("id"),
        "episode_title": ep_title,
        "episode_no": ep_no,
        "season_no": v.get("seasonNo"),
        "media_type": media_type,
        "slug": content.get("contentSlug") or (content.get("slugs") or {}).get("default"),
    }


def _mux_video_creds():
    tid = os.environ.get("VURT_MUX_TOKEN_ID")
    tsec = os.environ.get("VURT_MUX_TOKEN_SECRET")
    return (tid, tsec) if tid and tsec else None


def resolve_via_mux(playback_id):
    """Fallback for IDs not in the home/category map.
    Uses the Mux Video API to read the asset's passthrough field (= Enveu
    content ID), then looks up that content via the public Enveu API.
    Returns a map entry or None. Requires VURT_MUX_TOKEN_ID/SECRET.
    """
    auth = _mux_video_creds()
    if not auth:
        return None
    try:
        r = requests.get(f"https://api.mux.com/video/v1/playback-ids/{playback_id}",
                         auth=auth, timeout=15)
        r.raise_for_status()
        asset_id = ((r.json().get("data") or {}).get("object") or {}).get("id")
        if not asset_id:
            return None
        r = requests.get(f"https://api.mux.com/video/v1/assets/{asset_id}",
                         auth=auth, timeout=15)
        r.raise_for_status()
        passthrough = (r.json().get("data") or {}).get("passthrough")
        if not passthrough:
            return None
        try:
            content_id = int(passthrough)
        except (TypeError, ValueError):
            return None
        content = get_content(content_id)
        return _content_to_entry(content, playback_id)
    except (requests.HTTPError, requests.RequestException, ValueError):
        return None


def build_map(verbose=True):
    """Walk every screen reachable from the main menu, every playlist on each
    screen, and every show, collecting every episode's playbackIds. Returns
    {playback_id -> {series_title, episode_title, ...}}."""
    mapping = {}
    seen_series = set()
    seen_playlist_ids = set()
    playlists = []
    screens = list_menu_screens()
    if verbose:
        print(f"[mux-resolver] {len(screens)} screens in main menu", file=sys.stderr)
    for s in screens:
        try:
            for pl in list_screen_playlists(s["screenId"]):
                if pl["playlistId"] in seen_playlist_ids:
                    continue
                seen_playlist_ids.add(pl["playlistId"])
                pl["screenId"] = s["screenId"]
                playlists.append(pl)
        except requests.HTTPError as e:
            if verbose:
                print(f"[mux-resolver]   screen {s['screenId']} failed: {e}", file=sys.stderr)
    if verbose:
        print(f"[mux-resolver] {len(playlists)} unique playlists across screens", file=sys.stderr)

    for pl in playlists:
        try:
            shows = list_playlist_contents(pl["playlistId"])
        except requests.HTTPError as e:
            if verbose:
                print(f"[mux-resolver]   playlist {pl['playlistId']} failed: {e}", file=sys.stderr)
            continue
        if verbose:
            print(f"[mux-resolver] playlist {pl['playlistId']} ({pl['name']}): {len(shows)} shows", file=sys.stderr)

        for show in shows:
            sid = show.get("id")
            if not sid or sid in seen_series:
                continue
            seen_series.add(sid)
            stitle = show.get("title") or ""
            stype = show.get("mediaType") or show.get("contentType") or ""
            sslug = show.get("contentSlug") or (show.get("slugs") or {}).get("default")

            # Single-video content: playbackIds live on show.video directly
            video = show.get("video")
            if video and (video.get("playbackIds") or []):
                for pid in video.get("playbackIds") or []:
                    mapping[pid] = {
                        "series_id": sid,
                        "series_title": stitle,
                        "episode_id": sid,
                        "episode_title": stitle,
                        "episode_no": video.get("episodeNo"),
                        "season_no": video.get("seasonNo"),
                        "media_type": stype,
                        "slug": sslug,
                    }
                continue

            # Series: enumerate episodes
            try:
                episodes = list_series_episodes(sid)
            except requests.HTTPError as e:
                if verbose:
                    print(f"[mux-resolver]   series {sid} ({stitle}): {e}", file=sys.stderr)
                continue
            if verbose:
                print(f"[mux-resolver]   series {sid} ({stitle}): {len(episodes)} episodes", file=sys.stderr)

            for ep in episodes:
                ev = ep.get("video") or {}
                pids = ev.get("playbackIds") or []
                if not pids:
                    continue
                ep_no = ev.get("episodeNo")
                ep_title = _clean_episode_title(ep.get("title"), ep_no, stitle)
                # Prefer the series title from the episode's customData (authoritative)
                cd = (ep.get("customData") or {}).get("micro-episode-micro-series-id") or {}
                series_title = cd.get("title") or stitle
                for pid in pids:
                    mapping[pid] = {
                        "series_id": sid,
                        "series_title": series_title,
                        "episode_id": ep.get("id"),
                        "episode_title": ep_title,
                        "episode_no": ep_no,
                        "season_no": ev.get("seasonNo"),
                        "media_type": stype,
                        "slug": sslug,
                    }
            time.sleep(0.05)

    if verbose:
        print(f"[mux-resolver] mapped {len(mapping)} playback IDs across {len(seen_series)} shows",
              file=sys.stderr)
    return mapping


def save_map(mapping, path=OUT_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": int(time.time()),
        "count": len(mapping),
        "map": mapping,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_map(path=OUT_FILE, max_age_hours=48):
    """Load the cached map. Returns {} if file missing or stale."""
    try:
        payload = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    if max_age_hours:
        age = time.time() - payload.get("generatedAt", 0)
        if age > max_age_hours * 3600:
            return {}
    return payload.get("map", {})


def _label(info):
    if not info:
        return None
    series = info.get("series_title") or ""
    ep = info.get("episode_title") or ""
    if ep and ep != series:
        return f"{series} — {ep}".strip(" —")
    return series or ep or None


def resolve_title(playback_id, mapping=None, persist_orphans=True):
    """Return a human label for a Mux playback ID, or the ID itself if unknown.
    If the cache misses and Mux Video API creds are present, fall back to
    looking up the asset's passthrough field and persist the result so future
    calls hit the cache."""
    if mapping is None:
        mapping = load_map()
    info = mapping.get(playback_id)
    if info:
        return _label(info) or playback_id
    info = resolve_via_mux(playback_id)
    if info:
        mapping[playback_id] = info
        if persist_orphans:
            try:
                save_map(mapping)
            except OSError:
                pass
        return _label(info) or playback_id
    return playback_id


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        m = build_map()
        path = save_map(m)
        print(f"Wrote {len(m)} entries to {path}")
    elif cmd == "show":
        m = load_map(max_age_hours=0)
        print(json.dumps(m, indent=2)[:4000])
    elif cmd == "resolve":
        pid = sys.argv[2]
        print(resolve_title(pid))
    else:
        print(f"Usage: {sys.argv[0]} [build|show|resolve <playback_id>]")
