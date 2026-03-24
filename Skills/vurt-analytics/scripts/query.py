#!/usr/bin/env python3
"""On-demand GA4 queries for VURT analytics."""

import sys, os, argparse
sys.path.insert(0, os.path.dirname(__file__))

from ga4_client import *

def report_engagement(days):
    result = run_report(
        date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        metrics=["averageSessionDuration", "userEngagementDuration", "engagedSessions",
                 "sessionsPerUser", "engagementRate", "activeUsers", "sessions"]
    )
    rows = extract_rows(result)
    if not rows:
        print("No data available")
        return
    r = rows[0]
    print(f"## Engagement Report ({days}d)\n")
    print(f"- Active Users: {fmt_num(r.get('activeUsers','0'))}")
    print(f"- Sessions: {fmt_num(r.get('sessions','0'))}")
    print(f"- Sessions/User: {float(r.get('sessionsPerUser','0')):.1f}")
    print(f"- Avg Session Duration: {fmt_duration(r.get('averageSessionDuration','0'))}")
    print(f"- Total Engagement Time: {fmt_duration(r.get('userEngagementDuration','0'))}")
    print(f"- Engaged Sessions: {fmt_num(r.get('engagedSessions','0'))}")
    print(f"- Engagement Rate: {fmt_pct(r.get('engagementRate','0'))}")

def report_traffic(days):
    result = run_report(
        date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration"],
        dimensions=["sessionDefaultChannelGroup"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=15
    )
    rows = extract_rows(result)
    if not rows:
        print("No traffic data")
        return
    print(f"## Traffic Sources ({days}d)\n")
    print("| Channel | Users | Sessions | Eng Rate | Avg Duration |")
    print("|---------|-------|----------|----------|-------------|")
    for r in rows:
        print(f"| {r.get('sessionDefaultChannelGroup','?')} | {fmt_num(r.get('activeUsers','0'))} | {fmt_num(r.get('sessions','0'))} | {fmt_pct(r.get('engagementRate','0'))} | {fmt_duration(r.get('averageSessionDuration','0'))} |")

def report_content(days):
    result = run_report(
        date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        metrics=["screenPageViews", "activeUsers", "userEngagementDuration"],
        dimensions=["unifiedScreenName"],
        order_bys=[{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        limit=20
    )
    rows = extract_rows(result)
    if not rows:
        print("No content data")
        return
    print(f"## Top Content ({days}d)\n")
    print("| Screen/Page | Views | Users | Eng Time |")
    print("|-------------|-------|-------|----------|")
    for r in rows:
        print(f"| {r.get('unifiedScreenName','?')[:60]} | {fmt_num(r.get('screenPageViews','0'))} | {fmt_num(r.get('activeUsers','0'))} | {fmt_duration(r.get('userEngagementDuration','0'))} |")

def report_retention(days):
    result = run_report(
        date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "newUsers"],
        dimensions=["newVsReturning"]
    )
    rows = extract_rows(result)
    if not rows:
        print("No retention data")
        return
    print(f"## User Retention ({days}d)\n")
    for r in rows:
        label = r.get("newVsReturning", "?")
        print(f"- {label}: {fmt_num(r.get('activeUsers','0'))} users")
    
    total = sum(float(r.get("activeUsers", 0)) for r in rows)
    returning = sum(float(r.get("activeUsers", 0)) for r in rows if r.get("newVsReturning") == "returning")
    if total > 0:
        print(f"\n**Return rate: {returning/total*100:.1f}%**")

def report_realtime():
    result = run_realtime_report(
        metrics=["activeUsers"],
        dimensions=["platform"]
    )
    rows = extract_rows(result)
    print("## Realtime Active Users\n")
    total = 0
    for r in rows:
        n = int(r.get("activeUsers", 0))
        total += n
        print(f"- {r.get('platform','?')}: {n}")
    print(f"\n**Total active now: {total}**")

def query_metric(metric, days):
    result = run_report(
        date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        metrics=[metric],
        dimensions=["date"],
        order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
    )
    rows = extract_rows(result)
    if not rows:
        print(f"No data for {metric}")
        return
    print(f"## {metric} ({days}d)\n")
    print("| Date | Value |")
    print("|------|-------|")
    for r in rows:
        d = r.get("date", "")
        date_fmt = f"{d[4:6]}/{d[6:8]}" if len(d) == 8 else d
        print(f"| {date_fmt} | {r.get(metric, '0')} |")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VURT GA4 Analytics Query Tool")
    parser.add_argument("--report", choices=["engagement", "traffic", "content", "retention", "realtime"], help="Run a preset report")
    parser.add_argument("--metric", help="Query a specific metric over time (e.g., activeUsers, sessions)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    args = parser.parse_args()

    if args.report == "engagement":
        report_engagement(args.days)
    elif args.report == "traffic":
        report_traffic(args.days)
    elif args.report == "content":
        report_content(args.days)
    elif args.report == "retention":
        report_retention(args.days)
    elif args.report == "realtime":
        report_realtime()
    elif args.metric:
        query_metric(args.metric, args.days)
    else:
        parser.print_help()
