#!/usr/bin/env python3
"""NPAW Youbora Data API client for VURT analytics."""

import hashlib
import math
import os
import time
from urllib.parse import urlencode

import requests

NPAW_API_SECRET = os.environ.get("NPAW_API_SECRET", "")
NPAW_SYSTEM_CODE = os.environ.get("NPAW_SYSTEM_CODE", "vurt")
NPAW_BASE = "https://api.youbora.com"
OFFSET = 36000  # ms offset for dateToken


def _sign_request(path, params):
    """Add NPAW dateToken + MD5 security token."""
    p = list(params.items()) if isinstance(params, dict) else list(params)
    future_time = int(round(time.time() * 1000) + OFFSET)
    p.append(("dateToken", future_time))
    qs = urlencode(p, doseq=True)
    m = hashlib.md5()
    m.update(f"{path}?{qs}{NPAW_API_SECRET}".encode())
    p.append(("token", m.hexdigest()))
    return p


def npaw_request(metrics, from_date="yesterday", to_date=None, group_by=None,
                 granularity="day", content_type=None, limit=50, timeout=90):
    """Make an authenticated request to the NPAW Data API."""
    if not NPAW_API_SECRET:
        raise ValueError("NPAW_API_SECRET not set")

    path = f"/{NPAW_SYSTEM_CODE}/data"
    params = {
        "metrics": metrics if isinstance(metrics, str) else ",".join(metrics),
        "fromDate": from_date,
        "granularity": granularity,
        "limit": limit,
    }
    if to_date:
        params["toDate"] = to_date
    if group_by:
        params["groupBy"] = group_by
    if content_type:
        params["type"] = content_type

    signed = _sign_request(path, params)
    resp = requests.get(f"{NPAW_BASE}{path}", params=signed, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _extract_metrics(response):
    """
    Parse NPAW's nested response format into a flat dict.
    Structure: data[0].metrics[] -> {code, label, values[0].data[0][1]}
    """
    result = {}
    try:
        block = response.get("data", [{}])[0]
        for metric in block.get("metrics", []):
            code = metric.get("code", "")
            try:
                val = metric["values"][0]["data"][0][1]
            except (IndexError, KeyError, TypeError):
                val = None
            result[code] = val
    except Exception:
        pass
    return result


def _extract_grouped_metrics(response):
    """
    Parse NPAW grouped response (e.g. groupBy=title).
    Returns list of dicts: [{title, plays, views, ...}, ...]
    Title comes from block["name"]; metric values are summed across daily data points.
    """
    rows = []
    try:
        for block in response.get("data", []):
            row = {"title": block.get("name") or "(unknown)"}
            for metric in block.get("metrics", []):
                code = metric.get("code", "")
                try:
                    data_points = metric["values"][0]["data"]
                    vals = [p[1] for p in data_points if p[1] is not None]
                    AVG_METRICS = {"completionRate", "avgCompletionRate", "bufferRatio", "errorRate"}
                    if code.startswith("avg") or code in AVG_METRICS:
                        # averages: use mean of daily averages
                        val = sum(vals) / len(vals) if vals else None
                    else:
                        # totals: sum all daily values
                        val = sum(vals) if vals else None
                except (IndexError, KeyError, TypeError):
                    val = None
                row[code] = val
            rows.append(row)
    except Exception:
        pass
    return rows


def get_top_content(days=7, limit=20):
    """Content ranked by plays for the last N days (pull more, score + slice in formatter)."""
    return npaw_request(
        metrics=["views", "completionRate", "effectiveTime"],
        from_date=f"last{days}days",
        group_by="title",
        limit=limit,
        timeout=120,
    )


def get_daily_video_overview(date="yesterday"):
    """Daily aggregate video metrics."""
    return npaw_request(
        metrics=["plays", "views", "errors", "bufferRatio", "uniqueUsers"],
        from_date=date,
        to_date=date,
        granularity="day",
    )


def get_content_quality(days=7, limit=20):
    """Buffer ratio and error rate by title — surfaces QoS issues per show."""
    return npaw_request(
        metrics=["views", "bufferRatio", "errors"],
        from_date=f"last{days}days",
        group_by="title",
        limit=limit,
        timeout=120,
    )


def get_device_breakdown(days=7):
    """Video views broken down by device type (web vs app)."""
    return npaw_request(
        metrics=["views", "completionRate"],
        from_date=f"last{days}days",
        group_by="device",
        limit=20,
    )


def get_cdn_breakdown(days=7):
    """Buffer ratio and views by CDN."""
    return npaw_request(
        metrics=["views", "bufferRatio", "errors"],
        from_date=f"last{days}days",
        group_by="cdn",
        limit=10,
    )


def get_country_breakdown(days=7):
    """Views and buffer ratio by country."""
    return npaw_request(
        metrics=["views", "bufferRatio"],
        from_date=f"last{days}days",
        group_by="country",
        limit=10,
    )


def get_isp_breakdown(days=7):
    """Views and buffer ratio by ISP."""
    return npaw_request(
        metrics=["views", "bufferRatio"],
        from_date=f"last{days}days",
        group_by="isp",
        limit=10,
    )


def fmt_val(v, decimals=2):
    """Format a metric value for display."""
    if v is None:
        return "N/A"
    try:
        f = float(v)
        if f == int(f):
            return f"{int(f):,}"
        return f"{f:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(v)


def _engagement_score(plays, completion_rate):
    """Engagement Score = completion_rate * log10(plays + 1). Balances quality vs reach."""
    try:
        return float(completion_rate) * math.log10(float(plays) + 1)
    except (TypeError, ValueError):
        return 0.0


def format_npaw_report(top_content_raw, daily_overview_raw, device_breakdown_raw=None,
                       cdn_raw=None, country_raw=None, isp_raw=None, content_quality_raw=None):
    """Format NPAW data as markdown for the daily report."""
    lines = []
    lines.append("## Video Performance (NPAW)")
    lines.append("")

    # Daily overview
    try:
        m = _extract_metrics(daily_overview_raw)
        plays = m.get("plays")
        views = m.get("views")
        errors = m.get("errors")
        buf_ratio = m.get("bufferRatio")
        unique = m.get("uniqueUsers")
        error_rate = f"{(float(errors) / float(views) * 100):.1f}%" if views and errors and float(views) > 0 else "0%"
        buf_str = f"{float(buf_ratio):.1f}%" if buf_ratio is not None else "N/A"
        buf_flag = " ⚠️" if buf_ratio and float(buf_ratio) > 2 else ""
        lines.append("### Yesterday")
        lines.append("")
        lines.append("| Unique Viewers | Play Starts | View Events | Errors | Error Rate | Buffer Ratio |")
        lines.append("|----------------|-------------|-------------|--------|------------|--------------|")
        lines.append(f"| {fmt_val(unique)} | {fmt_val(plays)} | {fmt_val(views)} | {fmt_val(errors)} | {error_rate} | {buf_str}{buf_flag} |")
        lines.append("")
    except Exception as e:
        lines.append(f"*Daily video overview unavailable: {e}*\n")

    # Top content — two cuts
    try:
        rows = _extract_grouped_metrics(top_content_raw)
        if rows:
            # Score every row
            for row in rows:
                row["_score"] = _engagement_score(row.get("views", 0), row.get("completionRate", 0))

            by_engagement = sorted(rows, key=lambda r: r["_score"], reverse=True)[:5]
            by_plays = sorted(rows, key=lambda r: float(r.get("views") or 0), reverse=True)[:5]

            lines.append("### Top 5 by Engagement Score (7d) — quality × reach")
            lines.append("*Score = completion rate × log10(plays). Best candidates for paid traffic.*")
            lines.append("")
            lines.append("| # | Title | Views | Completion Rate | Score |")
            lines.append("|---|-------|-------|-----------------|-------|")
            for i, row in enumerate(by_engagement, 1):
                lines.append(f"| {i} | {row.get('title','?')} | {fmt_val(row.get('views'))} | {fmt_val(row.get('completionRate'))}% | {row['_score']:.1f} |")
            lines.append("")

            lines.append("### Top 5 by Raw Views (7d) — volume leaders")
            lines.append("")
            lines.append("| # | Title | Views | Completion Rate | Eff. Playtime (hrs) |")
            lines.append("|---|-------|-------|-----------------|---------------------|")
            for i, row in enumerate(by_plays, 1):
                lines.append(f"| {i} | {row.get('title','?')} | {fmt_val(row.get('views'))} | {fmt_val(row.get('completionRate'))}% | {fmt_val(row.get('effectiveTime'))} |")
            lines.append("")

            # At-risk content: high views but low completion (people abandoning)
            at_risk = [r for r in rows
                       if float(r.get("views") or 0) >= 10
                       and r.get("completionRate") is not None
                       and float(r.get("completionRate") or 100) < 30]
            at_risk = sorted(at_risk, key=lambda r: float(r.get("views") or 0), reverse=True)[:5]
            if at_risk:
                lines.append("### At-Risk Content (7d) — high views but viewers not finishing")
                lines.append("*These shows have audience but are losing them. Investigate episode hooks and pacing — early drop-off (first 30s) = weak hook, gradual decline = pacing issue. Check completion rate trend week-over-week.*")
                lines.append("")
                lines.append("| Title | Views | Completion Rate |")
                lines.append("|-------|-------|-----------------|")
                for row in at_risk:
                    lines.append(f"| {row.get('title','?')} | {fmt_val(row.get('views'))} | {fmt_val(row.get('completionRate'))}% |")
                lines.append("")
        else:
            lines.append("*No top content data returned.*\n")
    except Exception as e:
        lines.append(f"*Top content unavailable: {e}*\n")

    # Content QoS — buffer ratio per title (surfaces show-specific streaming issues)
    if content_quality_raw:
        try:
            cq_rows = _extract_grouped_metrics(content_quality_raw)
            if cq_rows:
                # Only flag shows with notable buffer issues (>5%) AND enough views to matter (>=5)
                problem_titles = [
                    r for r in cq_rows
                    if r.get("bufferRatio") is not None
                    and float(r.get("bufferRatio") or 0) > 5
                    and float(r.get("views") or 0) >= 5
                ]
                problem_titles = sorted(problem_titles, key=lambda r: float(r.get("bufferRatio") or 0), reverse=True)[:8]
                if problem_titles:
                    lines.append("### Content QoS Issues (7d) — shows with high buffer ratio")
                    lines.append("*Flag to Enveu/CDN team. High buffer ratio = viewers experiencing stalls.*")
                    lines.append("")
                    lines.append("| Title | Views | Buffer Ratio | Errors |")
                    lines.append("|-------|-------|--------------|--------|")
                    for r in problem_titles:
                        buf = r.get("bufferRatio")
                        buf_str = f"{float(buf):.1f}%  ⚠️" if buf is not None else "—"
                        lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {buf_str} | {fmt_val(r.get('errors'))} |")
                    lines.append("")
        except Exception as e:
            lines.append(f"*Content QoS unavailable: {e}*\n")

    # Device breakdown (web vs app)
    if device_breakdown_raw:
        try:
            device_rows = _extract_grouped_metrics(device_breakdown_raw)
            if device_rows:
                WEB_DEVICES = {"pc( windows )", "pc( mac )", "chrome os", "pc"}
                web_views = sum(r.get("views") or 0 for r in device_rows if r.get("title","").lower() in WEB_DEVICES)
                total_views = sum(r.get("views") or 0 for r in device_rows)
                web_pct = f"{web_views/total_views*100:.0f}%" if total_views else "0%"
                lines.append("### Video Views by Device (7d)")
                lines.append(f"*Web: {fmt_val(web_views)} views ({web_pct} of total) — App: {fmt_val(total_views - web_views)} views*")
                lines.append("")
                lines.append("| Device | Views | % of Total |")
                lines.append("|--------|-------|------------|")
                for r in sorted(device_rows, key=lambda x: float(x.get("views") or 0), reverse=True):
                    pct = f"{float(r.get('views') or 0)/total_views*100:.0f}%" if total_views else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {pct} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*Device breakdown unavailable: {e}*\n")

    # CDN breakdown
    if cdn_raw:
        try:
            cdn_rows = _extract_grouped_metrics(cdn_raw)
            if cdn_rows:
                lines.append("### CDN Quality (7d)")
                lines.append("")
                lines.append("| CDN | Views | Buffer Ratio | Errors |")
                lines.append("|-----|-------|--------------|--------|")
                for r in sorted(cdn_rows, key=lambda x: float(x.get("views") or 0), reverse=True):
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.1f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {buf_str} | {fmt_val(r.get('errors'))} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*CDN breakdown unavailable: {e}*\n")

    # Country breakdown
    if country_raw:
        try:
            country_rows = _extract_grouped_metrics(country_raw)
            if country_rows:
                total = sum(float(r.get("views") or 0) for r in country_rows)
                lines.append("### Viewership by Country (7d)")
                lines.append("")
                lines.append("| Country | Views | % | Buffer Ratio |")
                lines.append("|---------|-------|---|--------------|")
                for r in sorted(country_rows, key=lambda x: float(x.get("views") or 0), reverse=True):
                    pct = f"{float(r.get('views') or 0)/total*100:.0f}%" if total else "—"
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.1f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {pct} | {buf_str} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*Country breakdown unavailable: {e}*\n")

    # ISP breakdown
    if isp_raw:
        try:
            isp_rows = _extract_grouped_metrics(isp_raw)
            if isp_rows:
                lines.append("### Buffer Ratio by ISP (7d) — top 10 by views")
                lines.append("")
                lines.append("| ISP | Views | Buffer Ratio |")
                lines.append("|-----|-------|--------------|")
                for r in sorted(isp_rows, key=lambda x: float(x.get("views") or 0), reverse=True):
                    buf = r.get("bufferRatio")
                    buf_str = f"{float(buf):.1f}%{'  ⚠️' if buf and float(buf) > 5 else ''}" if buf is not None else "—"
                    lines.append(f"| {r.get('title','?')} | {fmt_val(r.get('views'))} | {buf_str} |")
                lines.append("")
        except Exception as e:
            lines.append(f"*ISP breakdown unavailable: {e}*\n")

    return "\n".join(lines)
