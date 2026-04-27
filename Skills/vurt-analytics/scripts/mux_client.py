#!/usr/bin/env python3
"""Mux Data API client for VURT analytics.

Replaces npaw_client.py. Uses HTTP Basic auth with VURT_MUX_DATA_TOKEN_ID /
VURT_MUX_DATA_TOKEN_SECRET (separate from VURT_MUX_TOKEN_* which the subtitle
skill uses against the Video API).

Public function signatures intentionally mirror npaw_client.py so daily-report.py
and vurt-birdseye/snapshot.py can swap imports with minimal diff. Normalized
row dicts use the same keys that the existing report formatter expects:
title, views, completionRate, effectiveTime, bufferRatio, errors.
"""

import math
import os
from datetime import datetime, timedelta, timezone

import requests

MUX_TOKEN_ID = os.environ.get("VURT_MUX_DATA_TOKEN_ID", "")
MUX_TOKEN_SECRET = os.environ.get("VURT_MUX_DATA_TOKEN_SECRET", "")
MUX_BASE = "https://api.mux.com/data/v1"


def _auth():
    if not MUX_TOKEN_ID or not MUX_TOKEN_SECRET:
        raise ValueError("VURT_MUX_DATA_TOKEN_ID / VURT_MUX_DATA_TOKEN_SECRET not set")
    return (MUX_TOKEN_ID, MUX_TOKEN_SECRET)


def _timeframe(days=7, date=None):
    """Mux accepts either timeframe[]=7:days or two unix timestamps.
    For 'yesterday' we use an explicit UTC day window.
    """
    if date == "yesterday":
        y = datetime.now(timezone.utc).date() - timedelta(days=1)
        start = int(datetime(y.year, y.month, y.day, tzinfo=timezone.utc).timestamp())
        end = start + 86400 - 1
        return [("timeframe[]", str(start)), ("timeframe[]", str(end))]
    if date and date != "yesterday":
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            start = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())
            end = start + 86400 - 1
            return [("timeframe[]", str(start)), ("timeframe[]", str(end))]
        except ValueError:
            pass
    return [("timeframe[]", f"{days}:days")]


def _get(path, params, timeout=60):
    resp = requests.get(f"{MUX_BASE}{path}", params=params, auth=_auth(), timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# -------- Raw endpoints --------

def overall(metric, days=7, date=None):
    """Single-metric overall value for a timeframe."""
    params = _timeframe(days=days, date=date)
    return _get(f"/metrics/{metric}/overall", params)


def breakdown(group_by, days=7, limit=25, metric="views", measurement=None,
              order_by=None, order_direction="desc"):
    """Breakdown of a metric by a dimension.

    For metric='views' Mux accepts measurement=count|sum and order_by=views.
    For quality metrics (rebuffer_percentage, playback_failure_percentage),
    pass no measurement and let Mux order by the metric itself.
    """
    params = _timeframe(days=days) + [
        ("group_by", group_by),
        ("limit", str(limit)),
        ("order_direction", order_direction),
    ]
    if metric == "views":
        params.append(("measurement", measurement or "count"))
        params.append(("order_by", order_by or "views"))
    elif order_by:
        params.append(("order_by", order_by))
    return _get(f"/metrics/{metric}/breakdown", params)


def timeseries(metric="views", days=7, group_by="day"):
    """Daily (or hourly) time series for a single metric."""
    params = _timeframe(days=days) + [("group_by", group_by)]
    return _get(f"/metrics/{metric}/timeseries", params)


# -------- Normalized helpers (mirror NPAW shape) --------

def fmt_val(v, decimals=2):
    if v is None:
        return "N/A"
    try:
        f = float(v)
        if f == int(f):
            return f"{int(f):,}"
        return f"{f:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(v)


def _ms_to_hours(ms):
    try:
        return float(ms) / 1000.0 / 3600.0
    except (TypeError, ValueError):
        return None


def _label(field, group_by):
    """Humanize a breakdown field value."""
    if field is None or field == "":
        return "(unknown)"
    if group_by == "viewer_device_category":
        return str(field).title()
    return str(field)


def _merge_breakdown(views_resp, rebuffer_resp, failure_resp, group_by):
    """Merge views, rebuffer %, and failure % breakdowns into unified rows.

    Returns list of dicts with keys: title, views, completionRate, effectiveTime,
    bufferRatio, errors (errors = failure_pct * views, approximated).
    The 'completionRate' is approximated as playing_time / watch_time * 100.
    """
    rebuffer_by_field = {}
    for row in (rebuffer_resp or {}).get("data", []):
        rebuffer_by_field[row.get("field")] = row.get("value")

    failure_by_field = {}
    for row in (failure_resp or {}).get("data", []):
        failure_by_field[row.get("field")] = row.get("value")

    rows = []
    for row in (views_resp or {}).get("data", []):
        field = row.get("field")
        views = row.get("views") or 0
        playing = row.get("total_playing_time") or 0
        watching = row.get("total_watch_time") or 0
        completion_rate = None
        if watching and playing:
            completion_rate = min(100.0, (playing / watching) * 100.0)
        buf = rebuffer_by_field.get(field)
        buf_pct = (buf * 100.0) if isinstance(buf, (int, float)) else None
        fail = failure_by_field.get(field)
        errors = None
        if isinstance(fail, (int, float)) and views:
            errors = int(round(fail * views))

        rows.append({
            "title": _label(field, group_by),
            "views": views,
            "completionRate": completion_rate,
            "effectiveTime": _ms_to_hours(playing),
            "bufferRatio": buf_pct,
            "errors": errors,
        })
    return rows


# -------- Public functions (match npaw_client signatures) --------

def get_daily_video_overview(date="yesterday"):
    """Return yesterday (or given date) overall metrics as a dict."""
    views_r = overall("views", date=date)
    rebuf_r = overall("rebuffer_percentage", date=date)
    fail_r = overall("playback_failure_percentage", date=date)
    startup_r = overall("video_startup_time", date=date)

    views_d = (views_r or {}).get("data", {}) or {}
    total_views = views_d.get("total_views") or views_d.get("value") or 0
    playing = views_d.get("total_playing_time") or 0
    watching = views_d.get("total_watch_time") or 0

    rebuf_val = (rebuf_r or {}).get("data", {}).get("value")
    buffer_pct = (rebuf_val * 100.0) if isinstance(rebuf_val, (int, float)) else None
    fail_val = (fail_r or {}).get("data", {}).get("value")
    errors = int(round(fail_val * total_views)) if isinstance(fail_val, (int, float)) and total_views else 0
    startup_ms = (startup_r or {}).get("data", {}).get("value")

    completion_rate = None
    if watching and playing:
        completion_rate = min(100.0, (playing / watching) * 100.0)

    return {
        "plays": total_views,
        "views": total_views,
        "errors": errors,
        "bufferRatio": buffer_pct,
        "uniqueUsers": None,
        "completionRate": completion_rate,
        "startupTimeMs": startup_ms,
        "playingHours": _ms_to_hours(playing),
        "watchHours": _ms_to_hours(watching),
        "_raw": {
            "views": views_r, "rebuffer": rebuf_r,
            "failure": fail_r, "startup": startup_r,
        },
    }


def get_top_content(days=7, limit=30, resolve_titles=True):
    """Top content by views, joined with rebuffer and failure metrics.

    Mux player doesn't populate video_title metadata, so we group by video_id
    and use the public Enveu API to resolve playback IDs to show/episode names
    via mux_title_resolver. If the cache is missing or a row isn't in the map,
    the raw playback ID is returned as title.
    """
    views_r = breakdown("video_id", days=days, limit=limit, metric="views")
    rebuf_r = breakdown("video_id", days=days, limit=limit, metric="rebuffer_percentage")
    fail_r = breakdown("video_id", days=days, limit=limit, metric="playback_failure_percentage")
    rows = _merge_breakdown(views_r, rebuf_r, fail_r, "video_id")
    if resolve_titles:
        try:
            from mux_title_resolver import load_map, resolve_title
            mapping = load_map()
            for r in rows:
                pid = r.get("title")
                r["playbackId"] = pid
                r["title"] = resolve_title(pid, mapping)
        except Exception:
            pass
    return rows


def get_content_quality(days=7, limit=30):
    """Video-level QoS: rebuffer % + failure rate per video_id."""
    return get_top_content(days=days, limit=limit)


def get_device_breakdown(days=7):
    """Views + completion by viewer_device_category (desktop/mobile/tablet/tv)."""
    views_r = breakdown("viewer_device_category", days=days, limit=10)
    return _merge_breakdown(views_r, None, None, "viewer_device_category")


def get_cdn_breakdown(days=7):
    """Views + rebuffer % + failure % by CDN."""
    views_r = breakdown("cdn", days=days, limit=10)
    rebuf_r = breakdown("cdn", days=days, limit=10, metric="rebuffer_percentage")
    fail_r = breakdown("cdn", days=days, limit=10, metric="playback_failure_percentage")
    return _merge_breakdown(views_r, rebuf_r, fail_r, "cdn")


def get_country_breakdown(days=7):
    """Views + rebuffer % by country (Mux 'country' is an advanced dimension)."""
    views_r = breakdown("country", days=days, limit=15)
    rebuf_r = breakdown("country", days=days, limit=15, metric="rebuffer_percentage")
    return _merge_breakdown(views_r, rebuf_r, None, "country")


def get_isp_breakdown(days=7):
    """Views + rebuffer % by ASN (closest equivalent to ISP in Mux)."""
    try:
        views_r = breakdown("asn", days=days, limit=10)
        rebuf_r = breakdown("asn", days=days, limit=10, metric="rebuffer_percentage")
        return _merge_breakdown(views_r, rebuf_r, None, "asn")
    except requests.HTTPError:
        return []


def get_browser_breakdown(days=7):
    """Views + rebuffer % by browser."""
    views_r = breakdown("browser", days=days, limit=10)
    rebuf_r = breakdown("browser", days=days, limit=10, metric="rebuffer_percentage")
    return _merge_breakdown(views_r, rebuf_r, None, "browser")


def get_os_breakdown(days=7):
    """Views + rebuffer % by operating system."""
    views_r = breakdown("operating_system", days=days, limit=10)
    rebuf_r = breakdown("operating_system", days=days, limit=10, metric="rebuffer_percentage")
    return _merge_breakdown(views_r, rebuf_r, None, "operating_system")


def get_daily_buffer_trend(days=7):
    """Daily views + rebuffer % trend for the last N days."""
    views_ts = timeseries("views", days=days, group_by="day")
    rebuf_ts = timeseries("rebuffer_percentage", days=days, group_by="day")
    return {"views": views_ts, "rebuffer": rebuf_ts}


def _extract_timeseries_pairs(ts_resp):
    """Mux timeseries data is [[iso_date, value, value], ...]."""
    points = []
    for row in (ts_resp or {}).get("data", []):
        if isinstance(row, list) and len(row) >= 2:
            try:
                dt = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
                ts_ms = int(dt.timestamp() * 1000)
                points.append([ts_ms, row[1]])
            except (ValueError, TypeError, AttributeError):
                continue
    return sorted(points, key=lambda x: x[0])


# -------- Engagement score (carry-over from NPAW) --------

def _engagement_score(views, completion_rate):
    """Engagement Score = completion_rate * log10(views+1). Balances quality vs reach."""
    try:
        return float(completion_rate or 0) * math.log10(float(views or 0) + 1)
    except (TypeError, ValueError):
        return 0.0


# -------- Markdown formatter for daily report --------

def format_mux_report(top_content, daily_overview, device_breakdown=None,
                      cdn_breakdown=None, country_breakdown=None, isp_breakdown=None,
                      content_quality=None, daily_buffer_trend=None):
    """Format Mux data as markdown for the daily report email."""
    lines = []
    lines.append("## Video Performance (Mux)")
    lines.append("")

    # --- Yesterday overview ---
    try:
        o = daily_overview or {}
        views = o.get("views")
        errors = o.get("errors")
        buf = o.get("bufferRatio")
        compl = o.get("completionRate")
        startup = o.get("startupTimeMs")
        play_hrs = o.get("playingHours")
        error_rate = f"{(float(errors)/float(views)*100):.2f}%" if views and errors else "0%"
        buf_str = f"{float(buf):.2f}%" if buf is not None else "N/A"
        compl_str = f"{float(compl):.1f}%" if compl is not None else "N/A"
        startup_str = f"{float(startup):.0f} ms" if startup is not None else "N/A"
        play_str = f"{float(play_hrs):.0f} hrs" if play_hrs is not None else "N/A"
        lines.append("### Yesterday")
        lines.append("")
        lines.append("| Views | Playing Time | Completion | Startup Time | Errors | Rebuffer % |")
        lines.append("|-------|--------------|------------|--------------|--------|------------|")
        lines.append(f"| {fmt_val(views)} | {play_str} | {compl_str} | {startup_str} | {fmt_val(errors)} ({error_rate}) | {buf_str} |")
        lines.append("")
    except Exception as e:
        lines.append(f"*Daily overview unavailable: {e}*\n")

    # --- Daily trend ---
    if daily_buffer_trend:
        try:
            views_pairs = _extract_timeseries_pairs(daily_buffer_trend.get("views"))
            rebuf_pairs = _extract_timeseries_pairs(daily_buffer_trend.get("rebuffer"))
            rebuf_by_ts = {p[0]: p[1] for p in rebuf_pairs}
            if views_pairs:
                lines.append("### Daily Trend (last 7 days)")
                lines.append("")
                lines.append("| Date | Views | Rebuffer % |")
                lines.append("|------|-------|------------|")
                for ts, v in views_pairs:
                    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                    date_str = dt.strftime("%m/%d")
                    buf = rebuf_by_ts.get(ts)
                    buf_str = f"{float(buf)*100:.2f}%" if isinstance(buf, (int, float)) else "—"
                    if isinstance(buf, (int, float)) and buf * 100 > 5:
                        buf_str += "  ⚠️"
                    lines.append(f"| {date_str} | {fmt_val(v)} | {buf_str} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*Daily trend unavailable: {e}*\n")

    # --- Top content ---
    try:
        if top_content:
            for row in top_content:
                row["_score"] = _engagement_score(row.get("views"), row.get("completionRate"))
            by_eng = sorted(top_content, key=lambda r: r["_score"], reverse=True)[:5]
            by_views = sorted(top_content, key=lambda r: float(r.get("views") or 0), reverse=True)[:5]
            lines.append("### Top 5 by Engagement (7d) — completion × reach")
            lines.append("*Score = completion × log10(views). Best candidates for paid traffic.*")
            lines.append("")
            lines.append("| # | Title | Views | Completion | Score |")
            lines.append("|---|-------|-------|------------|-------|")
            for i, r in enumerate(by_eng, 1):
                compl = r.get("completionRate")
                compl_str = f"{float(compl):.1f}%" if compl is not None else "N/A"
                lines.append(f"| {i} | {r.get('title','?')[:60]} | {fmt_val(r.get('views'))} | {compl_str} | {r['_score']:.1f} |")
            lines.append("")
            lines.append("### Top 5 by Raw Views (7d) — volume leaders")
            lines.append("")
            lines.append("| # | Title | Views | Completion | Play Time (hrs) |")
            lines.append("|---|-------|-------|------------|-----------------|")
            for i, r in enumerate(by_views, 1):
                compl = r.get("completionRate")
                compl_str = f"{float(compl):.1f}%" if compl is not None else "N/A"
                lines.append(f"| {i} | {r.get('title','?')[:60]} | {fmt_val(r.get('views'))} | {compl_str} | {fmt_val(r.get('effectiveTime'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Top content unavailable: {e}*\n")

    # --- Device breakdown ---
    if device_breakdown:
        try:
            rows = sorted(device_breakdown, key=lambda r: float(r.get("views") or 0), reverse=True)
            total = sum(float(r.get("views") or 0) for r in rows)
            if rows and total:
                lines.append("### Views by Device Category (7d)")
                lines.append("")
                lines.append("| Device | Views | % of Total |")
                lines.append("|--------|-------|------------|")
                for r in rows:
                    pct = f"{float(r.get('views') or 0)/total*100:.0f}%"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {pct} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*Device breakdown unavailable: {e}*\n")

    # --- CDN breakdown ---
    if cdn_breakdown:
        try:
            rows = sorted(cdn_breakdown, key=lambda r: float(r.get("views") or 0), reverse=True)
            if rows:
                lines.append("### CDN Performance (7d)")
                lines.append("")
                lines.append("| CDN | Views | Rebuffer % | Failures |")
                lines.append("|-----|-------|------------|----------|")
                for r in rows:
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.2f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {buf_str} | {fmt_val(r.get('errors'))} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*CDN breakdown unavailable: {e}*\n")

    # --- Country breakdown ---
    if country_breakdown:
        try:
            rows = sorted(country_breakdown, key=lambda r: float(r.get("views") or 0), reverse=True)
            total = sum(float(r.get("views") or 0) for r in rows)
            if rows and total:
                lines.append("### Top Countries by Views (7d)")
                lines.append("")
                lines.append("| Country | Views | % | Rebuffer % |")
                lines.append("|---------|-------|---|------------|")
                for r in rows[:10]:
                    pct = f"{float(r.get('views') or 0)/total*100:.0f}%"
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.2f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {pct} | {buf_str} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*Country breakdown unavailable: {e}*\n")

    # --- ISP/ASN breakdown (optional) ---
    if isp_breakdown:
        try:
            rows = sorted(isp_breakdown, key=lambda r: float(r.get("views") or 0), reverse=True)[:10]
            if rows:
                lines.append("### Top ASNs by Views (7d)")
                lines.append("")
                lines.append("| ASN | Views | Rebuffer % |")
                lines.append("|-----|-------|------------|")
                for r in rows:
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.2f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {buf_str} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*ASN breakdown unavailable: {e}*\n")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    import json as _json
    cmd = sys.argv[1] if len(sys.argv) > 1 else "overview"
    if cmd == "overview":
        print(_json.dumps(get_daily_video_overview(), indent=2, default=str))
    elif cmd == "top":
        print(_json.dumps(get_top_content(days=7, limit=5), indent=2, default=str))
    elif cmd == "country":
        print(_json.dumps(get_country_breakdown(days=7), indent=2, default=str))
    elif cmd == "cdn":
        print(_json.dumps(get_cdn_breakdown(days=7), indent=2, default=str))
    elif cmd == "device":
        print(_json.dumps(get_device_breakdown(days=7), indent=2, default=str))
    elif cmd == "trend":
        print(_json.dumps(get_daily_buffer_trend(days=7), indent=2, default=str))
    elif cmd == "report":
        top = get_top_content(days=7, limit=20)
        ov = get_daily_video_overview()
        dev = get_device_breakdown(days=7)
        cdn = get_cdn_breakdown(days=7)
        ctry = get_country_breakdown(days=7)
        trend = get_daily_buffer_trend(days=7)
        print(format_mux_report(top, ov, dev, cdn, ctry, daily_buffer_trend=trend))
    else:
        print(f"Unknown command: {cmd}. Use: overview | top | country | cdn | device | trend | report")
