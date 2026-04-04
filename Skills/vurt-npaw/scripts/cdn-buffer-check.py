#!/usr/bin/env python3
"""Check CDN distribution and buffer ratios after CloudFront switch.

Pulls raw sessions from NPAW /rawdata, extracts CDN, buffer_ratio, device info,
and compares quality by CDN provider.
"""

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


def get_sessions(hours=4, max_sessions=500):
    """Pull raw sessions for the last N hours."""
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    all_sessions = []
    offset = 0
    per_page = min(max_sessions, 500)

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
            if "localhost" in domain or "10.1." in domain:
                continue
            all_sessions.append(s)
        if len(batch) < per_page:
            break
        offset += len(batch)

    return all_sessions[:max_sessions]


def analyze_cdn_buffering(sessions):
    """Analyze sessions by CDN and buffer ratio."""
    cdn_stats = defaultdict(lambda: {
        "count": 0, "buffer_ratios": [], "startup_times": [],
        "errors": 0, "happiness": [], "devices": defaultdict(int),
        "play_times": []
    })

    no_cdn_count = 0
    total = len(sessions)

    for s in sessions:
        # CDN field - check multiple possible locations
        cdn = s.get("cdn", "") or ""
        if not cdn:
            cdn = s.get("cdn_name", "") or ""
        if not cdn:
            ep = s.get("extraparams", {}) or {}
            cdn = ep.get("extraparam1", "") or ep.get("extraparam2", "") or ""
        if not cdn:
            # Check resource URL for CDN hints
            resource = s.get("resource", "") or ""
            if "cloudfront" in resource.lower():
                cdn = "CloudFront (from URL)"
            elif "fastly" in resource.lower():
                cdn = "Fastly (from URL)"
            elif "akamai" in resource.lower():
                cdn = "Akamai (from URL)"
            else:
                cdn = "Unknown/Not reported"
                no_cdn_count += 1

        stats = cdn_stats[cdn]
        stats["count"] += 1

        # Buffer ratio
        br = s.get("buffer_ratio")
        if br is not None:
            try:
                val = float(br)
                if 0 <= val <= 1:
                    stats["buffer_ratios"].append(val)
            except (ValueError, TypeError):
                pass

        # Startup time
        st = s.get("startup_time")
        if st is not None:
            try:
                stats["startup_times"].append(float(st))
            except (ValueError, TypeError):
                pass

        # Play time
        pt = s.get("play_time")
        if pt is not None:
            try:
                stats["play_times"].append(float(pt))
            except (ValueError, TypeError):
                pass

        # Errors
        if s.get("error_code"):
            stats["errors"] += 1

        # Happiness
        hs = s.get("happiness_score")
        if hs is not None:
            try:
                stats["happiness"].append(float(hs))
            except (ValueError, TypeError):
                pass

        # Device
        dev = s.get("device", {}) or {}
        dtype = dev.get("device_type", "Unknown")
        stats["devices"][dtype] += 1

    # Print results
    print(f"\n{'='*70}")
    print(f"  CDN & BUFFERING ANALYSIS -- Last 4 Hours")
    print(f"  Total sessions analyzed: {total}")
    print(f"{'='*70}\n")

    if no_cdn_count > 0:
        print(f"  NOTE: {no_cdn_count}/{total} sessions had no CDN field reported.\n")

    print(f"{'CDN':<30} {'Sessions':>8} {'Buf%':>7} {'Startup':>8} {'Errors':>7} {'Happy':>6}")
    print("-" * 70)

    for cdn_name, stats in sorted(cdn_stats.items(), key=lambda x: -x[1]["count"]):
        n = stats["count"]
        avg_buf = "--"
        if stats["buffer_ratios"]:
            avg_buf = f"{sum(stats['buffer_ratios'])/len(stats['buffer_ratios'])*100:.1f}%"
        avg_st = "--"
        if stats["startup_times"]:
            avg_st = f"{sum(stats['startup_times'])/len(stats['startup_times'])/1000:.2f}s"
        err_pct = f"{stats['errors']}/{n}"
        avg_h = "--"
        if stats["happiness"]:
            avg_h = f"{sum(stats['happiness'])/len(stats['happiness']):.1f}"
        print(f"  {cdn_name:<28} {n:>8} {avg_buf:>7} {avg_st:>8} {err_pct:>7} {avg_h:>6}")

    # Detailed breakdown per CDN
    for cdn_name, stats in sorted(cdn_stats.items(), key=lambda x: -x[1]["count"]):
        n = stats["count"]
        print(f"\n--- {cdn_name} ({n} sessions) ---")

        if stats["buffer_ratios"]:
            brs = sorted(stats["buffer_ratios"])
            p50 = brs[len(brs)//2] * 100
            p95 = brs[int(len(brs)*0.95)] * 100
            zero_buf = sum(1 for b in brs if b == 0)
            high_buf = sum(1 for b in brs if b > 0.05)
            print(f"  Buffer ratio: median={p50:.1f}%, p95={p95:.1f}%, zero-buffer={zero_buf}, high(>5%)={high_buf}")

        if stats["startup_times"]:
            sts = sorted(stats["startup_times"])
            p50 = sts[len(sts)//2] / 1000
            p95 = sts[int(len(sts)*0.95)] / 1000
            print(f"  Startup time: median={p50:.2f}s, p95={p95:.2f}s")

        if stats["play_times"]:
            pts = sorted(stats["play_times"])
            avg_pt = sum(pts) / len(pts) / 60
            print(f"  Avg play time: {avg_pt:.1f} min")

        if stats["devices"]:
            devs = sorted(stats["devices"].items(), key=lambda x: -x[1])
            dev_str = ", ".join(f"{k}={v}" for k, v in devs[:5])
            print(f"  Devices: {dev_str}")

    # Also dump a few raw session examples with CDN/buffer fields
    print(f"\n{'='*70}")
    print(f"  SAMPLE RAW SESSIONS (first 10)")
    print(f"{'='*70}\n")

    for i, s in enumerate(sessions[:10]):
        cdn = s.get("cdn", "") or s.get("cdn_name", "") or ""
        resource = (s.get("resource", "") or "")[:80]
        br = s.get("buffer_ratio", "N/A")
        st = s.get("startup_time", "N/A")
        title = (s.get("title", "Unknown") or "Unknown")[:40]
        dev = s.get("device", {}) or {}
        dtype = dev.get("device_type", "?")
        os_name = dev.get("os", "?")

        print(f"  [{i+1}] {title}")
        print(f"      CDN: '{cdn}' | Buffer: {br} | Startup: {st}ms")
        print(f"      Device: {dtype}/{os_name} | Resource: {resource}")
        print()

    # Check resource URLs for CDN patterns
    print(f"\n{'='*70}")
    print(f"  RESOURCE URL CDN DETECTION")
    print(f"{'='*70}\n")

    url_patterns = defaultdict(int)
    for s in sessions:
        resource = (s.get("resource", "") or "").lower()
        if "cloudfront" in resource:
            url_patterns["CloudFront"] += 1
        elif "fastly" in resource:
            url_patterns["Fastly"] += 1
        elif "akamai" in resource:
            url_patterns["Akamai"] += 1
        elif "cdn" in resource:
            url_patterns["Other CDN keyword"] += 1
        else:
            url_patterns["No CDN in URL"] += 1

    for pattern, count in sorted(url_patterns.items(), key=lambda x: -x[1]):
        print(f"  {pattern:<30} {count:>5} sessions ({count/max(total,1)*100:.1f}%)")

    # Extract unique hostnames from resource URLs
    print(f"\n  Unique resource hostnames:")
    hostnames = defaultdict(int)
    for s in sessions:
        resource = s.get("resource", "") or ""
        if resource:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(resource)
                if parsed.hostname:
                    hostnames[parsed.hostname] += 1
            except:
                pass

    for host, count in sorted(hostnames.items(), key=lambda x: -x[1])[:15]:
        print(f"    {host:<50} {count:>5}")


def main():
    if not API_SECRET:
        print("Error: NPAW_API_SECRET not set.", file=sys.stderr)
        sys.exit(1)

    print("Pulling sessions from NPAW rawdata API...")
    sessions = get_sessions(hours=4, max_sessions=500)

    if not sessions:
        print("No sessions found in the last 4 hours.")
        # Try wider window
        print("\nTrying last 24 hours instead...")
        sessions = get_sessions(hours=24, max_sessions=500)
        if not sessions:
            print("No sessions found in the last 24 hours either.")
            sys.exit(1)
        print(f"Found {len(sessions)} sessions in last 24 hours.\n")
    else:
        print(f"Found {len(sessions)} sessions in last 4 hours.\n")

    analyze_cdn_buffering(sessions)


if __name__ == "__main__":
    main()
