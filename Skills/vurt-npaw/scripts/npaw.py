#!/usr/bin/env python3
"""VURT NPAW/Youbora analytics — pull platform viewing data from myvurt.com/app.

Uses TWO endpoints:
- /data (aggregated) — accurate totals for views, playtime, concurrent. This is the source of truth.
- /rawdata (paginated) — individual session detail (device, geo, title). Supports limit (max 500/req) + offset.
  Pass --max-sessions to control how many sessions to pull (default 500, paginate for more).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta, timezone

SYSTEM_CODE = os.environ.get("NPAW_SYSTEM_CODE", "vurt")
API_SECRET = os.environ.get("NPAW_API_SECRET", "")
BASE_URL = "https://api.youbora.com"


def sign_request(path, params):
    future_time = int(round(time.time() * 1000) + 36000)
    params_with_date = list(params) + [("dateToken", future_time)]
    qs = urllib.parse.urlencode(params_with_date, doseq=True)
    raw = f"{path}?{qs}{API_SECRET}"
    token = hashlib.md5(raw.encode()).hexdigest()
    params_with_date.append(("token", token))
    return params_with_date


def api_get(endpoint, params):
    path = f"/{SYSTEM_CODE}/{endpoint}"
    signed = sign_request(path, params)
    qs = urllib.parse.urlencode(signed, doseq=True)
    url = f"{BASE_URL}{path}?{qs}"
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url), timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body[:500]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def date_range(days):
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=days)).strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def extract_metric_value(data, metric_code):
    """Extract a single aggregate value from a /data response."""
    if not data or not data.get("data"):
        return None
    for series in data["data"]:
        for m in series.get("metrics", []):
            if m.get("code") == metric_code:
                for v in m.get("values", []):
                    for pt in v.get("data", []):
                        if isinstance(pt, dict):
                            return pt.get("value")
                        elif isinstance(pt, list) and len(pt) >= 2:
                            if pt[0] is None:
                                return pt[1]
    return None


def extract_timeseries(data, metric_code):
    """Extract daily timeseries from a /data response."""
    if not data or not data.get("data"):
        return []
    points = []
    for series in data["data"]:
        for m in series.get("metrics", []):
            if m.get("code") == metric_code:
                for v in m.get("values", []):
                    for pt in v.get("data", []):
                        if isinstance(pt, list) and len(pt) >= 2 and pt[0] is not None:
                            ts = datetime.fromtimestamp(pt[0] / 1000, tz=timezone.utc)
                            points.append((ts, pt[1]))
    return points


def get_aggregated(metrics, days=7, granularity=None):
    """Pull aggregated data from /data endpoint — accurate totals."""
    start, end = date_range(days)
    params = [
        ("metrics", metrics),
        ("fromDate", start), ("toDate", end),
        ("type", "VOD"), ("timezone", "America/New_York"),
    ]
    if granularity:
        params.append(("granularity", granularity))
    return api_get("data", params)


def get_sessions(days=7, max_sessions=500, exclude_dev=True):
    """Pull raw sessions from /rawdata with pagination.

    API supports limit (max 500/request) and offset for pagination.
    Set max_sessions > 500 to auto-paginate across multiple requests.
    When exclude_dev=True, filters out dev sessions (domain=localhost).
    """
    start, end = date_range(days)
    all_sessions = []
    offset = 0
    per_page = min(max_sessions, 500)
    dev_filtered = 0

    while len(all_sessions) < max_sessions:
        data = api_get("rawdata", [
            ("fromDate", start), ("toDate", end),
            ("type", "VOD"), ("timezone", "America/New_York"),
            ("limit", str(per_page)),
            ("offset", str(offset)),
        ])
        if not data:
            break
        sessions = data.get("data", [])
        batch = sessions[0].get("values", []) if sessions else []
        if not batch:
            break
        for s in batch:
            domain = (s.get("domain") or "").lower().strip()
            if exclude_dev and ("localhost" in domain or "10.1." in domain):
                dev_filtered += 1
                continue
            all_sessions.append(s)
        if len(batch) < per_page:
            break  # no more pages
        offset += len(batch)

    if dev_filtered > 0:
        print(f"  ⚠ Filtered {dev_filtered} dev/localhost sessions from results\n", file=sys.stderr)
    return all_sessions[:max_sessions]


def cmd_overview(days=7, **_):
    """Dashboard overview using aggregated data — accurate numbers."""
    data = get_aggregated("views,plays,playtime,concurrent_plays", days, granularity="day")
    if not data:
        print("No data."); return

    total_views = extract_metric_value(data, "views")
    total_plays = extract_metric_value(data, "plays")
    avg_playtime = extract_metric_value(data, "playtime")

    print(f"\n{'='*60}")
    print(f"  VURT Platform Overview — Last {days} Days")
    print(f"{'='*60}")
    if total_views is not None:
        print(f"  Total Views:        {total_views:,.0f}")
    if total_plays is not None:
        print(f"  Total Plays:        {total_plays:,.0f}")
    if avg_playtime is not None:
        print(f"  Avg Playtime:       {avg_playtime:.1f} min")

    daily = extract_timeseries(data, "views")
    if daily:
        print(f"\n  Daily Views:")
        for ts, val in daily:
            if val > 0:
                bar = "█" * min(int(val / 200), 40)
                print(f"    {ts.strftime('%b %d'):>6}: {val:>7,.0f}  {bar}")
        if len(daily) >= 2:
            recent = [v for _, v in daily[-3:] if v > 0]
            prior = [v for _, v in daily[:-3] if v > 0]
            if recent and prior:
                avg_recent = sum(recent) / len(recent)
                avg_prior = sum(prior) / len(prior)
                trend = ((avg_recent - avg_prior) / max(avg_prior, 1)) * 100
                direction = "↑" if trend > 0 else "↓"
                print(f"\n    Trend (last 3d vs prior): {direction} {abs(trend):.0f}%")


def cmd_top_content(days=7, limit=25, max_sessions=500, exclude_dev=True, **_):
    """Content breakdown from session sample + aggregated total."""
    data_agg = get_aggregated("views", days)
    total_real = extract_metric_value(data_agg, "views") or 0

    sessions = get_sessions(days, max_sessions, exclude_dev=exclude_dev)
    if not sessions:
        print("No sessions found."); return

    shows = defaultdict(lambda: {"plays": 0, "total_sec": 0, "users": set(), "episodes": set()})
    for s in sessions:
        ep4 = (s.get("extraparams") or {}).get("extraparam4", "")
        title = ep4 or s.get("title", "Unknown")
        ep_title = s.get("title", "Unknown")
        pt = float(s.get("play_time", 0) or 0)
        uid = s.get("user_id", "")
        shows[title]["plays"] += 1
        shows[title]["total_sec"] += pt
        shows[title]["users"].add(uid)
        shows[title]["episodes"].add(ep_title)

    sample_total = sum(d["plays"] for d in shows.values())
    scale = total_real / max(sample_total, 1) if total_real else 1

    print(f"\n  ⚠ Note: Content breakdown is from a {len(sessions)}-session sample.")
    print(f"  Real total views: {total_real:,.0f}. Percentages are from sample distribution.\n")

    rows = sorted(shows.items(), key=lambda x: x[1]["plays"], reverse=True)
    print(f"{'Show':<35} {'Sample':>7} {'Est. Views':>11} {'Share':>6} {'Eps':>4} {'Avg Min':>8}")
    print("=" * 78)
    for name, d in rows[:limit]:
        pct = round(d["plays"] / max(sample_total, 1) * 100, 1)
        est = round(d["plays"] * scale)
        am = round(d["total_sec"] / 60 / max(d["plays"], 1), 1)
        print(f"{name[:34]:<35} {d['plays']:>7} {est:>11,} {pct:>5.1f}% {len(d['episodes']):>4} {am:>7.1f}")

    print(f"\nSample: {sample_total} sessions | Real total: {total_real:,.0f} views")


def cmd_devices(days=7, max_sessions=500, exclude_dev=True, **_):
    sessions = get_sessions(days, max_sessions, exclude_dev=exclude_dev)
    if not sessions:
        print("No sessions found."); return

    types = defaultdict(int)
    vendors = defaultdict(int)
    os_counts = defaultdict(int)
    connections = defaultdict(int)
    for s in sessions:
        dev = s.get("device", {}) or {}
        types[dev.get("device_type", "Unknown")] += 1
        vendors[dev.get("device_vendor", "Unknown")] += 1
        os_counts[dev.get("os", "Unknown")] += 1
        connections[s.get("connection_type", "Unknown")] += 1

    n = len(sessions)
    print(f"\n  ⚠ Device breakdown from {n}-session sample\n")

    print(f"Device Types:")
    for k, v in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {k:<25} {v:>5}  ({round(v/n*100,1)}%)")

    print(f"\nVendors:")
    for k, v in sorted(vendors.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<25} {v:>5}  ({round(v/n*100,1)}%)")

    print(f"\nOS:")
    for k, v in sorted(os_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<25} {v:>5}  ({round(v/n*100,1)}%)")

    print(f"\nConnection:")
    for k, v in sorted(connections.items(), key=lambda x: -x[1]):
        print(f"  {k:<25} {v:>5}  ({round(v/n*100,1)}%)")


def cmd_geo(days=7, max_sessions=500, exclude_dev=True, **_):
    sessions = get_sessions(days, max_sessions, exclude_dev=exclude_dev)
    if not sessions:
        print("No sessions found."); return

    countries = defaultdict(lambda: {"plays": 0, "total_sec": 0})
    cities = defaultdict(int)
    for s in sessions:
        loc = s.get("location", {}) or {}
        c = loc.get("country", "Unknown")
        city = loc.get("city", "")
        pt = float(s.get("play_time", 0) or 0)
        countries[c]["plays"] += 1
        countries[c]["total_sec"] += pt
        if city and city != "Unknown":
            cities[f"{city}, {c}"] += 1

    n = len(sessions)
    print(f"\n  ⚠ Geo breakdown from {n}-session sample\n")

    print(f"{'Country':<35} {'Plays':>6} {'Tot Min':>8} {'Avg Min':>8}")
    print("-" * 62)
    for c, d in sorted(countries.items(), key=lambda x: -x[1]["plays"]):
        tm = round(d["total_sec"] / 60, 1)
        am = round(d["total_sec"] / 60 / max(d["plays"], 1), 1)
        print(f"{c[:34]:<35} {d['plays']:>6} {tm:>8} {am:>8}")

    if cities:
        print(f"\nTop Cities:")
        for city, cnt in sorted(cities.items(), key=lambda x: -x[1])[:15]:
            print(f"  {city:<40} {cnt:>5}")


def cmd_quality(days=7, max_sessions=500, exclude_dev=True, **_):
    sessions = get_sessions(days, max_sessions, exclude_dev=exclude_dev)
    if not sessions:
        print("No sessions found."); return

    startup_times = []
    buffer_ratios = []
    errors = 0
    happiness = []
    for s in sessions:
        st = s.get("startup_time")
        if st and str(st).replace(".", "").isdigit():
            startup_times.append(float(st))
        br = s.get("buffer_ratio")
        if br and str(br).replace(".", "").isdigit():
            val = float(br)
            if val <= 1:
                buffer_ratios.append(val)
        if s.get("error_code"):
            errors += 1
        hs = s.get("happiness_score")
        if hs and str(hs).replace(".", "").isdigit():
            happiness.append(float(hs))

    n = len(sessions)
    print(f"\n  ⚠ Quality metrics from {n}-session sample\n")
    print(f"Quality Metrics:")
    print("=" * 50)
    if startup_times:
        avg_st = round(sum(startup_times) / len(startup_times) / 1000, 2)
        p95 = round(sorted(startup_times)[int(len(startup_times) * 0.95)] / 1000, 2)
        print(f"  Avg Startup Time:  {avg_st}s")
        print(f"  P95 Startup Time:  {p95}s")
    if buffer_ratios:
        avg_br = round(sum(buffer_ratios) / len(buffer_ratios) * 100, 2)
        print(f"  Avg Buffer Ratio:  {avg_br}%")
    print(f"  Error Sessions:    {errors} ({round(errors/max(n,1)*100,1)}%)")
    if happiness:
        avg_h = round(sum(happiness) / len(happiness), 1)
        print(f"  Avg Happiness:     {avg_h}/10")


def cmd_concurrent(days=1, **_):
    data = get_aggregated("concurrent_plays", min(days, 3), granularity="hour")
    if not data:
        print("No data."); return

    points = extract_timeseries(data, "concurrent_plays")
    if not points:
        print("No concurrent data."); return

    peak = max(points, key=lambda x: x[1])
    print(f"\nConcurrent Viewers (last {days} day(s)):")
    print(f"  Peak: {peak[1]} at {peak[0].strftime('%b %d %H:%M')} UTC\n")
    for ts, val in points:
        if val > 0:
            bar = "█" * min(int(val), 30)
            print(f"  {ts.strftime('%m/%d %H:%M')} UTC  →  {val:>3} {bar}")


def cmd_raw_sessions(days=1, limit=30, max_sessions=500, exclude_dev=True, **_):
    sessions = get_sessions(min(days, 3), max_sessions, exclude_dev=exclude_dev)
    if not sessions:
        print("No sessions found."); return

    print(f"\n  Raw session sample ({len(sessions)} sessions):\n")
    print(f"{'Title':<40} {'Device':<18} {'Country':<15} {'Play':>6} {'Status':<10}")
    print("=" * 95)
    for s in sessions[:limit]:
        t = s.get("title", "Unknown")[:39]
        dev = s.get("device", {}) or {}
        d = dev.get("device_type", "?")[:17]
        loc = s.get("location", {}) or {}
        c = loc.get("country", "?")[:14]
        pt = round(float(s.get("play_time", 0) or 0) / 60, 1)
        status = s.get("happiness_score_label", "")
        print(f"  {t:<40} {d:<18} {c:<15} {pt:>5}m {status}")


def cmd_title_detail(days=30, title="", max_sessions=500, exclude_dev=True, **_):
    if not title:
        print("Provide --title 'Title Name'"); return
    sessions = get_sessions(days, max_sessions, exclude_dev=exclude_dev)
    matched = [s for s in sessions if title.lower() in (
        (s.get("extraparams") or {}).get("extraparam4", "") or s.get("title", "")
    ).lower()]
    if not matched:
        print(f"No sessions matching '{title}' in sample"); return

    print(f"\n  ⚠ From {len(sessions)}-session sample (not full count)\n")
    print(f"Title Detail: '{title}' — {len(matched)} sample sessions (last {days} days)")
    print("=" * 70)

    episodes = defaultdict(lambda: {"plays": 0, "total_sec": 0})
    for s in matched:
        ep = s.get("title", "Unknown")
        pt = float(s.get("play_time", 0) or 0)
        episodes[ep]["plays"] += 1
        episodes[ep]["total_sec"] += pt

    print(f"\n{'Episode':<50} {'Sample':>7} {'Avg Min':>8}")
    print("-" * 68)
    for ep, d in sorted(episodes.items(), key=lambda x: -x[1]["plays"]):
        am = round(d["total_sec"] / 60 / max(d["plays"], 1), 1)
        print(f"  {ep[:48]:<50} {d['plays']:>7} {am:>8}")


def cmd_daily(days=30, **_):
    """Daily views chart for the specified period."""
    data = get_aggregated("views", days, granularity="day")
    if not data:
        print("No data."); return

    total = extract_metric_value(data, "views")
    daily = extract_timeseries(data, "views")

    print(f"\n{'='*60}")
    print(f"  VURT Daily Views — Last {days} Days")
    print(f"  Total: {total:,.0f} views")
    print(f"{'='*60}\n")

    max_val = max((v for _, v in daily), default=1)
    for ts, val in daily:
        bar_len = int(val / max(max_val, 1) * 40)
        bar = "█" * bar_len
        print(f"  {ts.strftime('%b %d'):>6}  {val:>7,.0f}  {bar}")


def main():
    if not API_SECRET:
        print("Error: NPAW_API_SECRET not set.", file=sys.stderr)
        sys.exit(1)

    p = argparse.ArgumentParser(description="VURT NPAW Analytics")
    p.add_argument("--overview", action="store_true", help="Platform overview (accurate totals)")
    p.add_argument("--daily", action="store_true", help="Daily views chart (accurate)")
    p.add_argument("--top-content", action="store_true", help="Content breakdown (sampled)")
    p.add_argument("--devices", action="store_true", help="Device breakdown (sampled)")
    p.add_argument("--geo", action="store_true", help="Geographic breakdown (sampled)")
    p.add_argument("--quality", action="store_true", help="Quality metrics (sampled)")
    p.add_argument("--concurrent", action="store_true", help="Concurrent viewers (accurate)")
    p.add_argument("--raw-sessions", action="store_true", help="Raw session list (sampled)")
    p.add_argument("--title-detail", action="store_true", help="Detail for a specific title")
    p.add_argument("--all", action="store_true", help="Run all reports")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--max-sessions", type=int, default=500, help="Max sessions to pull from rawdata (default 500, paginate for more)")
    p.add_argument("--include-dev", action="store_true", help="Include dev/localhost sessions (excluded by default)")
    p.add_argument("--title", type=str, default="")
    p.add_argument("--json", action="store_true", help="Output raw JSON")
    args = p.parse_args()

    if not any([args.overview, args.daily, args.top_content, args.devices, args.geo,
                args.quality, args.concurrent, args.raw_sessions, args.title_detail, args.all]):
        p.print_help(); sys.exit(1)

    kw = {"days": args.days, "limit": args.limit, "title": args.title, "max_sessions": args.max_sessions, "exclude_dev": not args.include_dev}
    if args.overview or args.all: cmd_overview(**kw)
    if args.daily or args.all: cmd_daily(**kw)
    if args.top_content or args.all: cmd_top_content(**kw)
    if args.devices or args.all: cmd_devices(**kw)
    if args.geo or args.all: cmd_geo(**kw)
    if args.quality or args.all: cmd_quality(**kw)
    if args.concurrent or args.all: cmd_concurrent(**kw)
    if args.raw_sessions or args.all: cmd_raw_sessions(**kw)
    if args.title_detail: cmd_title_detail(**kw)


if __name__ == "__main__":
    main()
