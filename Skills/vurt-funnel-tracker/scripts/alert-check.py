#!/usr/bin/env python3
"""VURT Funnel Alert Check -- lightweight regression detector for scheduled runs.

Only checks for regressions and outputs alerts. No full report.
Exit code 0 = clean, exit code 1 = regressions found, exit code 2 = env error.

Usage:
    python3 alert-check.py                        # Check with default 15% threshold
    python3 alert-check.py --alert-threshold 20   # Custom threshold
    python3 alert-check.py --json                 # Machine-readable output
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone


# ============================================================================
# Configuration
# ============================================================================

PROPERTY_ID = "518738893"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"

FUNNEL_METRICS = [
    "sessions",
    "engagedSessions",
    "bounceRate",
    "engagementRate",
]

CONVERSION_EVENTS = [
    "play_content",
    "sign_up",
    "app_cta_click",
    "share_content",
]


# ============================================================================
# GA4 Auth + API (self-contained, no imports from funnel-check)
# ============================================================================

_cached_token = None

def get_access_token():
    global _cached_token
    if _cached_token is not None:
        return _cached_token
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
    _cached_token = json.loads(resp.read())["access_token"]
    return _cached_token


def run_report(date_ranges, metrics, dimensions=None, dimension_filter=None,
               order_bys=None, limit=None):
    token = get_access_token()
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
    rows = []
    dim_headers = [h["name"] for h in result.get("dimensionHeaders", [])]
    met_headers = [h["name"] for h in result.get("metricHeaders", [])]
    for row in result.get("rows", []):
        dims = {h: v["value"] for h, v in zip(dim_headers, row.get("dimensionValues", []))}
        mets = {h: v["value"] for h, v in zip(met_headers, row.get("metricValues", []))}
        rows.append({**dims, **mets})
    return rows


# ============================================================================
# Date Ranges -- uses yesterday vs 7-day baseline (most complete data)
# ============================================================================

def get_date_ranges():
    return {
        "today": [{"startDate": "yesterday", "endDate": "yesterday", "name": "today"}],
        "seven_day": [{"startDate": "9daysAgo", "endDate": "3daysAgo", "name": "seven_day"}],
    }


# ============================================================================
# Regression Logic
# ============================================================================

def compute_regression(today_val, avg_7d_val, threshold_pct, inverted=False):
    try:
        t = float(today_val)
        a = float(avg_7d_val)
    except (TypeError, ValueError):
        return None, None

    if a == 0:
        return None, None

    delta_pct = ((t - a) / a) * 100

    if inverted:
        regression_pct = delta_pct
    else:
        regression_pct = -delta_pct

    critical_threshold = threshold_pct * 2

    if regression_pct > critical_threshold:
        return delta_pct, "CRITICAL"
    elif regression_pct > threshold_pct:
        return delta_pct, "WARNING"
    return delta_pct, None


def fmt_pct(val):
    try:
        f = float(val)
    except (TypeError, ValueError):
        return "N/A"
    return f"{f * 100:.1f}%" if f <= 1.0 else f"{f:.1f}%"


def fmt_num(val):
    try:
        n = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{int(n)}" if n == int(n) else f"{n:.1f}"


# ============================================================================
# Alert Collection
# ============================================================================

def collect_alerts(threshold_pct):
    """Fetch minimal GA4 data and check for regressions. Returns list of alerts."""
    alerts = []
    dr = get_date_ranges()
    all_ranges = dr["today"] + dr["seven_day"]

    # -- Overall metrics --
    try:
        resp = run_report(
            date_ranges=all_ranges,
            metrics=FUNNEL_METRICS + ["activeUsers", "newUsers"],
        )
        rows = extract_rows(resp)
        today_ov = {}
        seven_ov = {}
        for row in rows:
            period = row.pop("dateRange", "today")
            if period == "today":
                today_ov = row
            elif period == "seven_day":
                seven_ov = row

        checks = [
            ("sessions", "Site Sessions", False),
            ("engagedSessions", "Engaged Sessions", False),
            ("bounceRate", "Site Bounce Rate", True),
            ("engagementRate", "Site Engagement Rate", False),
            ("activeUsers", "Active Users", False),
            ("newUsers", "New Users", False),
        ]
        for key, label, inverted in checks:
            t_val = today_ov.get(key)
            s_val = seven_ov.get(key)
            if t_val is None or s_val is None:
                continue
            if key in ("bounceRate", "engagementRate"):
                avg_val = s_val
            else:
                try:
                    avg_val = str(float(s_val) / 7)
                except (TypeError, ValueError):
                    continue
            delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted)
            if severity:
                alerts.append({
                    "severity": severity,
                    "metric": label,
                    "today": t_val,
                    "seven_day_avg": avg_val,
                    "delta_pct": round(delta, 1) if delta else None,
                })
    except Exception as e:
        alerts.append({"severity": "ERROR", "metric": "Overall fetch failed", "error": str(e)})

    # -- Channel breakdown --
    try:
        resp = run_report(
            date_ranges=all_ranges,
            metrics=FUNNEL_METRICS,
            dimensions=["sessionDefaultChannelGroup"],
            order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
            limit=15,
        )
        rows = extract_rows(resp)
        today_ch = {}
        seven_ch = {}
        for row in rows:
            period = row.pop("dateRange", "today")
            ch = row.get("sessionDefaultChannelGroup", "(unknown)")
            if period == "today":
                today_ch[ch] = row
            elif period == "seven_day":
                seven_ch[ch] = row

        for channel, t_row in today_ch.items():
            s_row = seven_ch.get(channel, {})
            if not s_row:
                continue
            for key, label_suffix, inverted in [
                ("bounceRate", "Bounce Rate", True),
                ("engagementRate", "Engagement Rate", False),
                ("sessions", "Sessions", False),
            ]:
                t_val = t_row.get(key)
                s_val = s_row.get(key)
                if t_val is None or s_val is None:
                    continue
                if key in ("bounceRate", "engagementRate"):
                    avg_val = s_val
                else:
                    try:
                        avg_val = str(float(s_val) / 7)
                    except (TypeError, ValueError):
                        continue
                delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted)
                if severity:
                    alerts.append({
                        "severity": severity,
                        "metric": f"{channel} {label_suffix}",
                        "today": t_val,
                        "seven_day_avg": avg_val,
                        "delta_pct": round(delta, 1) if delta else None,
                    })
    except Exception as e:
        alerts.append({"severity": "ERROR", "metric": "Channel fetch failed", "error": str(e)})

    # -- Conversion events --
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
            t_val = "0"
            s_val = "0"
            for row in rows:
                period = row.get("dateRange", "today")
                if period == "today":
                    t_val = row.get("eventCount", "0")
                elif period == "seven_day":
                    s_val = row.get("eventCount", "0")

            try:
                avg_val = str(float(s_val) / 7)
            except (TypeError, ValueError):
                continue

            delta, severity = compute_regression(t_val, avg_val, threshold_pct, inverted=False)
            if severity:
                pretty = event_name.replace("_", " ").title()
                alerts.append({
                    "severity": severity,
                    "metric": f"{pretty} Events",
                    "today": t_val,
                    "seven_day_avg": avg_val,
                    "delta_pct": round(delta, 1) if delta else None,
                })
        except Exception:
            pass  # Skip individual event failures silently

    return alerts


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VURT Funnel Alert Check -- lightweight regression detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  No regressions found
  1  Regressions detected
  2  Environment/config error

Environment variables:
  VURT_GOOGLE_OAUTH_CLIENT        Google OAuth client JSON
  VURT_ANALYTICS_REFRESH_TOKEN    GA4 OAuth refresh token
        """,
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output JSON instead of plain text",
    )
    parser.add_argument(
        "--alert-threshold", type=float, default=15.0, dest="alert_threshold",
        help="Regression threshold %% for WARNING (default: 15). CRITICAL = 2x.",
    )
    args = parser.parse_args()

    # Validate env
    missing = []
    for var in ("VURT_GOOGLE_OAUTH_CLIENT", "VURT_ANALYTICS_REFRESH_TOKEN"):
        if not os.environ.get(var):
            missing.append(var)
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    # Collect
    alerts = collect_alerts(args.alert_threshold)

    # Filter out ERROR-type alerts for exit code logic
    real_alerts = [a for a in alerts if a["severity"] in ("WARNING", "CRITICAL")]

    if args.json_output:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "threshold_pct": args.alert_threshold,
            "alert_count": len(real_alerts),
            "has_alerts": len(real_alerts) > 0,
            "alerts": alerts,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if real_alerts:
            critical = [a for a in real_alerts if a["severity"] == "CRITICAL"]
            warnings = [a for a in real_alerts if a["severity"] == "WARNING"]

            print(f"\n  VURT FUNNEL ALERT CHECK  |  {now} UTC")
            print(f"  Threshold: {args.alert_threshold}% (WARNING) / {args.alert_threshold * 2}% (CRITICAL)")
            print(f"  {len(real_alerts)} regression{'s' if len(real_alerts) != 1 else ''} found\n")

            if critical:
                print(f"  CRITICAL ({len(critical)}):")
                for a in critical:
                    metric = a["metric"]
                    dp = a.get("delta_pct", "?")
                    if "Bounce" in metric or "Engagement" in metric or "Rate" in metric:
                        tv = fmt_pct(a["today"])
                        av = fmt_pct(a["seven_day_avg"])
                    else:
                        tv = fmt_num(a["today"])
                        av = fmt_num(a["seven_day_avg"])
                    print(f"    - {metric}: today {tv} vs 7d avg {av} ({dp}%)")

            if warnings:
                print(f"  WARNING ({len(warnings)}):")
                for a in warnings:
                    metric = a["metric"]
                    dp = a.get("delta_pct", "?")
                    if "Bounce" in metric or "Engagement" in metric or "Rate" in metric:
                        tv = fmt_pct(a["today"])
                        av = fmt_pct(a["seven_day_avg"])
                    else:
                        tv = fmt_num(a["today"])
                        av = fmt_num(a["seven_day_avg"])
                    print(f"    - {metric}: today {tv} vs 7d avg {av} ({dp}%)")

            print()
        else:
            print(f"\n  VURT FUNNEL ALERT CHECK  |  {now} UTC")
            print(f"  All clear. No regressions above {args.alert_threshold}% threshold.\n")

        # Print any errors
        errors = [a for a in alerts if a["severity"] == "ERROR"]
        if errors:
            for e in errors:
                print(f"  [ERROR] {e['metric']}: {e.get('error', 'unknown')}", file=sys.stderr)

    # Exit code
    if real_alerts:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
