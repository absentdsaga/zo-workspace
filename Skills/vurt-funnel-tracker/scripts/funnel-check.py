#!/usr/bin/env python3
"""VURT Conversion Funnel Tracker -- GA4 traffic source and campaign analysis.

Pulls bounce rate, engagement rate, sessions, and conversion events from GA4,
broken down by traffic source and campaign name. Compares today vs yesterday
vs 7-day rolling average and flags regressions.

Usage:
    python3 funnel-check.py                        # Full daily report
    python3 funnel-check.py --hours 6              # Last 6 hours
    python3 funnel-check.py --json                 # JSON output only
    python3 funnel-check.py --alert-threshold 25   # Custom sensitivity (default 15%)
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


# ============================================================================
# Configuration
# ============================================================================

PROPERTY_ID = "518738893"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"

LOG_DIR = "/home/workspace/Logs/live"

# Metrics we pull for channel/campaign breakdowns
FUNNEL_METRICS = [
    "sessions",
    "engagedSessions",
    "bounceRate",
    "engagementRate",
]

# Conversion events to track
CONVERSION_EVENTS = [
    "play_content",
    "sign_up",
    "app_cta_click",
    "share_content",
]


# ============================================================================
# GA4 Auth + API
# ============================================================================

def get_access_token():
    """Exchange refresh token for a GA4 access token."""
    oauth_json = os.environ.get("VURT_GOOGLE_OAUTH_CLIENT")
    refresh_token = os.environ.get("VURT_ANALYTICS_REFRESH_TOKEN")
    if not oauth_json:
        raise EnvironmentError("Missing VURT_GOOGLE_OAUTH_CLIENT env var")
    if not refresh_token:
        raise EnvironmentError("Missing VURT_ANALYTICS_REFRESH_TOKEN env var")

    oauth = json.loads(oauth_json)
    params = urllib.parse.urlencode({
        "client_id": oauth["installed"]["client_id"],
        "client_secret": oauth["installed"]["client_secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=params, method="POST")
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())["access_token"]


# Cache the token for the duration of a single run
_cached_token = None

def _get_token():
    global _cached_token
    if _cached_token is None:
        _cached_token = get_access_token()
    return _cached_token


def run_report(date_ranges, metrics, dimensions=None, dimension_filter=None,
               order_bys=None, limit=None):
    """Execute a GA4 Data API v1beta runReport request."""
    token = _get_token()
    body = {
        "dateRanges": date_ranges,
        "metrics": [{"name": m} for m in metrics],
    }
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
    if dimension_filter:
        body["dimensionFilter"] = dimension_filter
    if order_bys:
        body["orderBys"] = order_bys
    if limit:
        body["limit"] = str(limit)

    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{DATA_API}/properties/{PROPERTY_ID}:runReport",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())


def extract_rows(result):
    """Parse GA4 response into a list of flat dicts."""
    rows = []
    dim_headers = [h["name"] for h in result.get("dimensionHeaders", [])]
    met_headers = [h["name"] for h in result.get("metricHeaders", [])]
    for row in result.get("rows", []):
        dims = {h: v["value"] for h, v in zip(dim_headers, row.get("dimensionValues", []))}
        mets = {h: v["value"] for h, v in zip(met_headers, row.get("metricValues", []))}
        rows.append({**dims, **mets})
    return rows


# ============================================================================
# Date Range Helpers
# ============================================================================

def build_date_ranges(hours=None):
    """Build GA4 date ranges for today, yesterday, and 7-day window.

    If --hours is set (< 24), we use 'today' as the current period.
    Otherwise we use 'yesterday' (most complete data).

    Returns a dict with keys: today, yesterday, seven_day, and labels.
    """
    if hours and hours < 24:
        # Intraday mode: "today" vs "yesterday" vs 7-day
        return {
            "today": [{"startDate": "today", "endDate": "today", "name": "today"}],
            "yesterday": [{"startDate": "yesterday", "endDate": "yesterday", "name": "yesterday"}],
            "seven_day": [{"startDate": "8daysAgo", "endDate": "2daysAgo", "name": "seven_day"}],
            "today_label": "today (partial)",
            "yesterday_label": "yesterday",
            "seven_day_label": "7-day avg (8d-2d ago)",
        }
    else:
        # Full day mode: "yesterday" vs "2daysAgo" vs 7-day
        return {
            "today": [{"startDate": "yesterday", "endDate": "yesterday", "name": "today"}],
            "yesterday": [{"startDate": "2daysAgo", "endDate": "2daysAgo", "name": "yesterday"}],
            "seven_day": [{"startDate": "9daysAgo", "endDate": "3daysAgo", "name": "seven_day"}],
            "today_label": "yesterday (latest full day)",
            "yesterday_label": "2 days ago",
            "seven_day_label": "7-day avg (9d-3d ago)",
        }


# ============================================================================
# Data Collection
# ============================================================================

def fetch_channel_breakdown(date_ranges):
    """Pull funnel metrics by sessionDefaultChannelGroup for all three periods."""
    all_ranges = (
        date_ranges["today"] +
        date_ranges["yesterday"] +
        date_ranges["seven_day"]
    )
    resp = run_report(
        date_ranges=all_ranges,
        metrics=FUNNEL_METRICS,
        dimensions=["sessionDefaultChannelGroup"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=20,
    )
    rows = extract_rows(resp)

    result = {"today": [], "yesterday": [], "seven_day": []}
    for row in rows:
        dr = row.pop("dateRange", "today")
        result.get(dr, []).append(row)
    return result


def fetch_campaign_breakdown(date_ranges):
    """Pull funnel metrics by sessionCampaignName for all three periods."""
    all_ranges = (
        date_ranges["today"] +
        date_ranges["yesterday"] +
        date_ranges["seven_day"]
    )
    resp = run_report(
        date_ranges=all_ranges,
        metrics=FUNNEL_METRICS,
        dimensions=["sessionCampaignName"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=20,
    )
    rows = extract_rows(resp)

    result = {"today": [], "yesterday": [], "seven_day": []}
    for row in rows:
        dr = row.pop("dateRange", "today")
        result.get(dr, []).append(row)
    return result


def fetch_conversion_events(date_ranges):
    """Pull event counts for each conversion event across all three periods."""
    results = {}
    all_ranges = (
        date_ranges["today"] +
        date_ranges["yesterday"] +
        date_ranges["seven_day"]
    )

    for event_name in CONVERSION_EVENTS:
        try:
            resp = run_report(
                date_ranges=all_ranges,
                metrics=["eventCount"],
                dimension_filter={
                    "filter": {
                        "fieldName": "eventName",
                        "stringFilter": {"value": event_name, "matchType": "EXACT"},
                    }
                },
            )
            rows = extract_rows(resp)
            event_data = {"today": "0", "yesterday": "0", "seven_day": "0"}
            for row in rows:
                dr = row.get("dateRange", "today")
                event_data[dr] = row.get("eventCount", "0")
            results[event_name] = event_data
        except Exception as e:
            results[event_name] = {"today": "0", "yesterday": "0", "seven_day": "0", "error": str(e)}

    return results


def fetch_overall_metrics(date_ranges):
    """Pull site-wide overview metrics for all three periods."""
    all_ranges = (
        date_ranges["today"] +
        date_ranges["yesterday"] +
        date_ranges["seven_day"]
    )
    resp = run_report(
        date_ranges=all_ranges,
        metrics=FUNNEL_METRICS + ["activeUsers", "newUsers", "averageSessionDuration",
                                   "screenPageViews"],
    )
    rows = extract_rows(resp)
    result = {}
    for row in rows:
        dr = row.pop("dateRange", "today")
        result[dr] = row
    return result


# ============================================================================
# Regression Detection
# ============================================================================

def compute_regression(today_val, avg_7d_val, threshold_pct, inverted=False):
    """Check if today's value regressed vs the 7-day average.

    inverted=True means higher is worse (e.g., bounce rate).

    Returns: (delta_pct, severity) where severity is None, "WARNING", or "CRITICAL".
    """
    try:
        t = float(today_val)
        a = float(avg_7d_val)
    except (TypeError, ValueError):
        return None, None

    if a == 0:
        return None, None

    delta_pct = ((t - a) / a) * 100

    # For inverted metrics (bounce rate), a positive delta is bad
    # For normal metrics (sessions, engagement), a negative delta is bad
    if inverted:
        regression_pct = delta_pct  # positive = worse
    else:
        regression_pct = -delta_pct  # negative delta = positive regression_pct = worse

    critical_threshold = threshold_pct * 2  # default: 30%

    if regression_pct > critical_threshold:
        return delta_pct, "CRITICAL"
    elif regression_pct > threshold_pct:
        return delta_pct, "WARNING"
    return delta_pct, None


def detect_regressions(data, threshold_pct):
    """Scan all collected data for regressions. Returns list of alert dicts."""
    alerts = []

    # -- Overall metrics --
    overview = data.get("overview", {})
    today_ov = overview.get("today", {})
    seven_ov = overview.get("seven_day", {})

    metric_checks = [
        ("sessions", "Site Sessions", False),
        ("engagedSessions", "Engaged Sessions", False),
        ("bounceRate", "Site Bounce Rate", True),
        ("engagementRate", "Site Engagement Rate", False),
        ("activeUsers", "Active Users", False),
        ("newUsers", "New Users", False),
    ]
    for metric_key, label, inverted in metric_checks:
        t_val = today_ov.get(metric_key)
        # 7-day range covers 7 days; for count metrics divide by 7, for rate metrics use as-is
        a_val = seven_ov.get(metric_key)
        if t_val is not None and a_val is not None:
            # Rate metrics (bounceRate, engagementRate) are already averages from GA4
            # Count metrics from 7-day need to be divided by 7 for daily average
            if metric_key in ("bounceRate", "engagementRate"):
                avg_val = a_val
            else:
                try:
                    avg_val = str(float(a_val) / 7)
                except (TypeError, ValueError):
                    continue

            delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted)
            if severity:
                alerts.append({
                    "scope": "overall",
                    "metric": label,
                    "today": t_val,
                    "seven_day_avg": avg_val,
                    "delta_pct": round(delta, 1) if delta else None,
                    "severity": severity,
                })

    # -- Channel breakdown --
    channels = data.get("channels", {})
    today_channels = {r.get("sessionDefaultChannelGroup"): r for r in channels.get("today", [])}
    seven_channels = {r.get("sessionDefaultChannelGroup"): r for r in channels.get("seven_day", [])}

    for channel, today_row in today_channels.items():
        seven_row = seven_channels.get(channel, {})
        if not seven_row:
            continue

        channel_checks = [
            ("bounceRate", f"{channel} Bounce Rate", True),
            ("engagementRate", f"{channel} Engagement Rate", False),
            ("sessions", f"{channel} Sessions", False),
        ]
        for metric_key, label, inverted in channel_checks:
            t_val = today_row.get(metric_key)
            a_val = seven_row.get(metric_key)
            if t_val is None or a_val is None:
                continue
            if metric_key in ("bounceRate", "engagementRate"):
                avg_val = a_val
            else:
                try:
                    avg_val = str(float(a_val) / 7)
                except (TypeError, ValueError):
                    continue

            delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted)
            if severity:
                alerts.append({
                    "scope": "channel",
                    "channel": channel,
                    "metric": label,
                    "today": t_val,
                    "seven_day_avg": avg_val,
                    "delta_pct": round(delta, 1) if delta else None,
                    "severity": severity,
                })

    # -- Campaign breakdown --
    campaigns = data.get("campaigns", {})
    today_campaigns = {r.get("sessionCampaignName"): r for r in campaigns.get("today", [])}
    seven_campaigns = {r.get("sessionCampaignName"): r for r in campaigns.get("seven_day", [])}

    for campaign, today_row in today_campaigns.items():
        if campaign in ("(not set)", "(direct)", "(organic)"):
            continue  # Skip non-campaign entries; they're covered by channel
        seven_row = seven_campaigns.get(campaign, {})
        if not seven_row:
            continue

        campaign_checks = [
            ("bounceRate", f"Campaign '{campaign}' Bounce Rate", True),
            ("engagementRate", f"Campaign '{campaign}' Engagement Rate", False),
            ("sessions", f"Campaign '{campaign}' Sessions", False),
        ]
        for metric_key, label, inverted in campaign_checks:
            t_val = today_row.get(metric_key)
            a_val = seven_row.get(metric_key)
            if t_val is None or a_val is None:
                continue
            if metric_key in ("bounceRate", "engagementRate"):
                avg_val = a_val
            else:
                try:
                    avg_val = str(float(a_val) / 7)
                except (TypeError, ValueError):
                    continue

            delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted)
            if severity:
                alerts.append({
                    "scope": "campaign",
                    "campaign": campaign,
                    "metric": label,
                    "today": t_val,
                    "seven_day_avg": avg_val,
                    "delta_pct": round(delta, 1) if delta else None,
                    "severity": severity,
                })

    # -- Conversion events --
    events = data.get("events", {})
    for event_name, event_data in events.items():
        if "error" in event_data:
            continue
        t_val = event_data.get("today", "0")
        a_val = event_data.get("seven_day", "0")
        try:
            avg_val = str(float(a_val) / 7)
        except (TypeError, ValueError):
            continue

        delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted=False)
        if severity:
            pretty_name = event_name.replace("_", " ").title()
            alerts.append({
                "scope": "event",
                "event": event_name,
                "metric": f"{pretty_name} Events",
                "today": t_val,
                "seven_day_avg": avg_val,
                "delta_pct": round(delta, 1) if delta else None,
                "severity": severity,
            })

    return alerts


# ============================================================================
# Formatting Helpers
# ============================================================================

def fmt_num(val):
    try:
        n = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{int(n)}" if n == int(n) else f"{n:.1f}"


def fmt_pct(val):
    try:
        f = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if f <= 1.0:
        return f"{f * 100:.1f}%"
    return f"{f:.1f}%"


def fmt_duration(val):
    try:
        s = float(val)
    except (TypeError, ValueError):
        return "N/A"
    m, sec = divmod(int(s), 60)
    return f"{m}m {sec}s"


def delta_str(today_val, compare_val, inverted=False):
    """Return a delta string like '+12.3%' or '-5.1%' with directional indicator."""
    try:
        t = float(today_val)
        c = float(compare_val)
    except (TypeError, ValueError):
        return "  --"
    if c == 0:
        return "  --" if t == 0 else "  +inf"
    delta = ((t - c) / c) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"


# ============================================================================
# Report Output
# ============================================================================

def print_header(text):
    print(f"\n{'=' * 76}")
    print(f"  {text}")
    print(f"{'=' * 76}")


def print_subheader(text):
    print(f"\n  --- {text} ---")


def print_report(data, date_ranges, threshold_pct):
    """Print the full funnel report to stdout."""
    now = datetime.now(timezone.utc)
    alerts = data.get("alerts", [])

    print(f"\n  VURT FUNNEL TRACKER")
    print(f"  Run: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  Current period:  {date_ranges['today_label']}")
    print(f"  Previous period: {date_ranges['yesterday_label']}")
    print(f"  Baseline:        {date_ranges['seven_day_label']}")
    print(f"  Alert threshold: {threshold_pct}%")

    # -- Alerts --
    if alerts:
        print_header(f"ALERTS ({len(alerts)} regression{'s' if len(alerts) != 1 else ''} detected)")
        for i, a in enumerate(alerts, 1):
            sev = a["severity"]
            tag = f"[{sev}]"
            metric = a["metric"]
            today_v = a["today"]
            avg_v = a["seven_day_avg"]
            dp = a.get("delta_pct", "?")

            # Format values nicely
            if "Bounce" in metric or "Engagement" in metric or "Rate" in metric:
                tv = fmt_pct(today_v)
                av = fmt_pct(avg_v)
            else:
                tv = fmt_num(today_v)
                av = fmt_num(avg_v)

            print(f"    {i}. {tag:10s} {metric}")
            print(f"       Today: {tv}  |  7-day avg: {av}  |  Delta: {dp}%")
    else:
        print_header("NO REGRESSIONS DETECTED")
        print(f"    All metrics within {threshold_pct}% of 7-day averages.")

    # -- Overall Metrics --
    overview = data.get("overview", {})
    today_ov = overview.get("today", {})
    yest_ov = overview.get("yesterday", {})
    seven_ov = overview.get("seven_day", {})

    print_header("SITE OVERVIEW")
    row_fmt = "    {:<28s} {:>10s}   {:>10s} {:>8s}   {:>10s} {:>8s}"
    print(row_fmt.format("Metric", "Today", "Yesterday", "vs Yd", "7d Avg", "vs 7d"))
    print(f"    {'-' * 76}")

    overview_metrics = [
        ("Sessions", "sessions", fmt_num, False),
        ("Active Users", "activeUsers", fmt_num, False),
        ("New Users", "newUsers", fmt_num, False),
        ("Engaged Sessions", "engagedSessions", fmt_num, False),
        ("Engagement Rate", "engagementRate", fmt_pct, False),
        ("Bounce Rate", "bounceRate", fmt_pct, True),
        ("Avg Session Duration", "averageSessionDuration", fmt_duration, False),
        ("Page Views", "screenPageViews", fmt_num, False),
    ]
    for label, key, fmt_fn, inverted in overview_metrics:
        t_val = today_ov.get(key, "0")
        y_val = yest_ov.get(key, "0")
        s_val = seven_ov.get(key, "0")

        # For count metrics, compute daily average from 7-day total
        if key not in ("bounceRate", "engagementRate"):
            try:
                s_avg = str(float(s_val) / 7)
            except (TypeError, ValueError):
                s_avg = s_val
        else:
            s_avg = s_val

        print(row_fmt.format(
            label,
            fmt_fn(t_val),
            fmt_fn(y_val),
            delta_str(t_val, y_val, inverted),
            fmt_fn(s_avg),
            delta_str(t_val, s_avg, inverted),
        ))

    # -- Channel Breakdown --
    channels = data.get("channels", {})
    today_ch = channels.get("today", [])
    yest_ch = {r.get("sessionDefaultChannelGroup"): r for r in channels.get("yesterday", [])}
    seven_ch = {r.get("sessionDefaultChannelGroup"): r for r in channels.get("seven_day", [])}

    if today_ch:
        print_header("BY TRAFFIC SOURCE (sessionDefaultChannelGroup)")

        for ch_row in today_ch:
            channel = ch_row.get("sessionDefaultChannelGroup", "(unknown)")
            y_row = yest_ch.get(channel, {})
            s_row = seven_ch.get(channel, {})

            print_subheader(channel)
            ch_metrics = [
                ("Sessions", "sessions", fmt_num, False),
                ("Engaged Sessions", "engagedSessions", fmt_num, False),
                ("Bounce Rate", "bounceRate", fmt_pct, True),
                ("Engagement Rate", "engagementRate", fmt_pct, False),
            ]
            for label, key, fmt_fn, inverted in ch_metrics:
                t_val = ch_row.get(key, "0")
                y_val = y_row.get(key, "0")
                s_val = s_row.get(key, "0")

                if key not in ("bounceRate", "engagementRate"):
                    try:
                        s_avg = str(float(s_val) / 7)
                    except (TypeError, ValueError):
                        s_avg = s_val
                else:
                    s_avg = s_val

                print(row_fmt.format(
                    label,
                    fmt_fn(t_val),
                    fmt_fn(y_val),
                    delta_str(t_val, y_val, inverted),
                    fmt_fn(s_avg),
                    delta_str(t_val, s_avg, inverted),
                ))

    # -- Campaign Breakdown --
    campaigns = data.get("campaigns", {})
    today_ca = campaigns.get("today", [])
    yest_ca = {r.get("sessionCampaignName"): r for r in campaigns.get("yesterday", [])}
    seven_ca = {r.get("sessionCampaignName"): r for r in campaigns.get("seven_day", [])}

    # Filter to actual campaigns
    real_campaigns = [r for r in today_ca if r.get("sessionCampaignName") not in ("(not set)", "(direct)", "(organic)")]
    if real_campaigns:
        print_header("BY CAMPAIGN NAME (sessionCampaignName)")

        for ca_row in real_campaigns:
            campaign = ca_row.get("sessionCampaignName", "(unknown)")
            y_row = yest_ca.get(campaign, {})
            s_row = seven_ca.get(campaign, {})

            name_display = campaign if len(campaign) <= 50 else campaign[:47] + "..."
            print_subheader(name_display)
            for label, key, fmt_fn, inverted in ch_metrics:
                t_val = ca_row.get(key, "0")
                y_val = y_row.get(key, "0")
                s_val = s_row.get(key, "0")

                if key not in ("bounceRate", "engagementRate"):
                    try:
                        s_avg = str(float(s_val) / 7)
                    except (TypeError, ValueError):
                        s_avg = s_val
                else:
                    s_avg = s_val

                print(row_fmt.format(
                    label,
                    fmt_fn(t_val),
                    fmt_fn(y_val),
                    delta_str(t_val, y_val, inverted),
                    fmt_fn(s_avg),
                    delta_str(t_val, s_avg, inverted),
                ))
    elif today_ca:
        print_header("BY CAMPAIGN NAME")
        print("    No named campaigns with traffic in this period.")

    # -- Conversion Events --
    events = data.get("events", {})
    print_header("CONVERSION EVENTS")
    ev_fmt = "    {:<28s} {:>10s}   {:>10s} {:>8s}   {:>10s} {:>8s}"
    print(ev_fmt.format("Event", "Today", "Yesterday", "vs Yd", "7d Avg", "vs 7d"))
    print(f"    {'-' * 76}")

    for event_name in CONVERSION_EVENTS:
        ev = events.get(event_name, {})
        if "error" in ev:
            print(f"    {event_name:<28s} (error: {ev['error'][:40]})")
            continue
        t_val = ev.get("today", "0")
        y_val = ev.get("yesterday", "0")
        s_val = ev.get("seven_day", "0")
        try:
            s_avg = str(float(s_val) / 7)
        except (TypeError, ValueError):
            s_avg = s_val

        pretty = event_name.replace("_", " ").title()
        print(ev_fmt.format(
            pretty,
            fmt_num(t_val),
            fmt_num(y_val),
            delta_str(t_val, y_val),
            fmt_num(s_avg),
            delta_str(t_val, s_avg),
        ))

    # -- Summary --
    print_header("SUMMARY")
    critical = [a for a in alerts if a["severity"] == "CRITICAL"]
    warnings = [a for a in alerts if a["severity"] == "WARNING"]
    if critical:
        print(f"    CRITICAL: {len(critical)} metric{'s' if len(critical) != 1 else ''} regressed >{ threshold_pct * 2}% from 7-day average")
        for a in critical:
            print(f"      - {a['metric']}: {a.get('delta_pct', '?')}%")
    if warnings:
        print(f"    WARNING:  {len(warnings)} metric{'s' if len(warnings) != 1 else ''} regressed {threshold_pct}-{threshold_pct * 2}% from 7-day average")
        for a in warnings:
            print(f"      - {a['metric']}: {a.get('delta_pct', '?')}%")
    if not alerts:
        print(f"    All clear. No regressions above {threshold_pct}% threshold.")

    print(f"\n{'=' * 76}")
    print(f"  GA4 Property: {PROPERTY_ID}")
    print(f"{'=' * 76}\n")


# ============================================================================
# JSON Log
# ============================================================================

def save_json_log(data, date_ranges):
    """Save the full data payload to Logs/live/ with today's date."""
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_funnel-check.json"
    filepath = os.path.join(LOG_DIR, filename)

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date_ranges": {
            "today_label": date_ranges["today_label"],
            "yesterday_label": date_ranges["yesterday_label"],
            "seven_day_label": date_ranges["seven_day_label"],
        },
        "data": data,
    }

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    return filepath


# ============================================================================
# Main
# ============================================================================

def collect_all_data(date_ranges, threshold_pct):
    """Fetch all GA4 data and run regression detection."""
    data = {}

    # Overall
    try:
        data["overview"] = fetch_overall_metrics(date_ranges)
    except Exception as e:
        data["overview"] = {"error": str(e)}
        print(f"  [WARN] Failed to fetch overview: {e}", file=sys.stderr)

    # Channels
    try:
        data["channels"] = fetch_channel_breakdown(date_ranges)
    except Exception as e:
        data["channels"] = {"error": str(e)}
        print(f"  [WARN] Failed to fetch channels: {e}", file=sys.stderr)

    # Campaigns
    try:
        data["campaigns"] = fetch_campaign_breakdown(date_ranges)
    except Exception as e:
        data["campaigns"] = {"error": str(e)}
        print(f"  [WARN] Failed to fetch campaigns: {e}", file=sys.stderr)

    # Conversion events
    try:
        data["events"] = fetch_conversion_events(date_ranges)
    except Exception as e:
        data["events"] = {"error": str(e)}
        print(f"  [WARN] Failed to fetch events: {e}", file=sys.stderr)

    # Regression detection
    data["alerts"] = detect_regressions(data, threshold_pct)

    return data


def main():
    parser = argparse.ArgumentParser(
        description="VURT Funnel Tracker -- GA4 traffic source and campaign analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 funnel-check.py                        Full daily report
  python3 funnel-check.py --hours 6              Last 6 hours (intraday)
  python3 funnel-check.py --json                 Machine-readable JSON only
  python3 funnel-check.py --alert-threshold 25   Custom sensitivity

Environment variables:
  VURT_GOOGLE_OAUTH_CLIENT        Google OAuth client JSON
  VURT_ANALYTICS_REFRESH_TOKEN    GA4 OAuth refresh token

Regression severity:
  WARNING   Metric regressed 15-30%% from 7-day average
  CRITICAL  Metric regressed >30%% from 7-day average
        """,
    )
    parser.add_argument(
        "--hours", type=int, default=None,
        help="Check last N hours instead of full day (uses 'today' as current period)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output machine-readable JSON instead of formatted text",
    )
    parser.add_argument(
        "--alert-threshold", type=float, default=15.0, dest="alert_threshold",
        help="Regression threshold percentage for WARNING alerts (default: 15). CRITICAL = 2x this value.",
    )
    args = parser.parse_args()

    # Validate env
    missing = []
    for var in ("VURT_GOOGLE_OAUTH_CLIENT", "VURT_ANALYTICS_REFRESH_TOKEN"):
        if not os.environ.get(var):
            missing.append(var)
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    # Build date ranges
    date_ranges = build_date_ranges(args.hours)

    # Collect data
    data = collect_all_data(date_ranges, args.alert_threshold)

    # Save JSON log
    try:
        log_path = save_json_log(data, date_ranges)
    except Exception as e:
        log_path = None
        print(f"  [WARN] Could not save log: {e}", file=sys.stderr)

    # Output
    if args.json_output:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "date_ranges": {
                "today_label": date_ranges["today_label"],
                "yesterday_label": date_ranges["yesterday_label"],
                "seven_day_label": date_ranges["seven_day_label"],
            },
            "alert_count": len(data.get("alerts", [])),
            "has_alerts": len(data.get("alerts", [])) > 0,
            "alerts": data.get("alerts", []),
            "data": data,
            "log_path": log_path,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_report(data, date_ranges, args.alert_threshold)
        if log_path:
            print(f"  Log saved: {log_path}")

    # Exit code 1 if alerts detected
    if data.get("alerts"):
        sys.exit(1)


if __name__ == "__main__":
    main()
