#!/usr/bin/env python3
"""NPAW diagnostic: CDN buffer ratios, device breakdown, ISP analysis for VURT.

Pulls raw sessions from the last 12 hours, filters out dev/localhost,
and breaks down buffering performance by CDN, device type, and ISP.
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
        resp = urllib.request.urlopen(urllib.request.Request(url), timeout=60)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body[:500]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def get_sessions(hours=12, max_sessions=2500):
    """Pull raw sessions with pagination, filtering dev/localhost."""
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    all_sessions = []
    offset = 0
    per_page = 500
    dev_filtered = 0

    print(f"Pulling sessions from {start} to {end} (last {hours}h)...")
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
            if "localhost" in domain or "10.1." in domain or "127.0.0.1" in domain or "0.0.0.0" in domain:
                dev_filtered += 1
                continue
            all_sessions.append(s)

        print(f"  Page {offset // per_page + 1}: got {len(batch)} sessions (total kept: {len(all_sessions)}, filtered dev: {dev_filtered})")
        if len(batch) < per_page:
            break
        offset += len(batch)

    print(f"\nTotal sessions: {len(all_sessions)} (filtered {dev_filtered} dev/localhost)\n")
    return all_sessions[:max_sessions]


def detect_cdn(session):
    """Detect CDN from session fields and resource URL."""
    cdn = session.get("cdn", "") or ""
    if not cdn:
        cdn = session.get("cdn_name", "") or ""
    if not cdn:
        ep = session.get("extraparams", {}) or {}
        cdn = ep.get("extraparam1", "") or ep.get("extraparam2", "") or ""
    if not cdn:
        resource = (session.get("resource", "") or "").lower()
        if "cloudfront" in resource:
            cdn = "CloudFront (URL)"
        elif "fastly" in resource:
            cdn = "Fastly (URL)"
        elif "akamai" in resource:
            cdn = "Akamai (URL)"
        elif "cdn" in resource:
            cdn = "Other CDN (URL)"
        else:
            cdn = "Unknown"
    return cdn.strip() or "Unknown"


def get_device_category(session):
    """Classify device into mobile/desktop/tablet/other."""
    dev = session.get("device", {}) or {}
    dtype = (dev.get("device_type", "") or "").lower()
    if "phone" in dtype or "smartphone" in dtype:
        return "Mobile"
    elif "tablet" in dtype or "ipad" in dtype:
        return "Tablet"
    elif "pc" in dtype or "desktop" in dtype:
        return "Desktop"
    elif "tv" in dtype or "smart" in dtype:
        return "Smart TV"
    elif dtype:
        return dtype.title()
    return "Unknown"


def safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def analyze_sessions(sessions):
    if not sessions:
        print("No sessions to analyze.")
        return

    n = len(sessions)

    # ============================================================
    # 1. CDN BREAKDOWN
    # ============================================================
    cdn_data = defaultdict(lambda: {
        "count": 0, "buffer_ratios": [], "startup_times": [],
        "errors": 0, "play_times": [], "happiness": []
    })

    for s in sessions:
        cdn = detect_cdn(s)
        d = cdn_data[cdn]
        d["count"] += 1

        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)

        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            d["startup_times"].append(st)

        pt = safe_float(s.get("play_time"))
        if pt is not None:
            d["play_times"].append(pt)

        if s.get("error_code"):
            d["errors"] += 1

        hs = safe_float(s.get("happiness_score"))
        if hs is not None:
            d["happiness"].append(hs)

    print("=" * 80)
    print("  1. CDN BREAKDOWN -- Buffer Ratio per CDN Provider")
    print("=" * 80)
    print()
    print(f"  {'CDN':<35} {'Sessions':>8} {'Avg Buf%':>9} {'Med Buf%':>9} {'P95 Buf%':>9} {'Startup':>8} {'Errors':>7}")
    print("  " + "-" * 78)

    for cdn_name, d in sorted(cdn_data.items(), key=lambda x: -x[1]["count"]):
        cnt = d["count"]

        avg_buf = med_buf = p95_buf = "--"
        if d["buffer_ratios"]:
            brs = sorted(d["buffer_ratios"])
            avg_buf = f"{sum(brs)/len(brs)*100:.1f}%"
            med_buf = f"{brs[len(brs)//2]*100:.1f}%"
            p95_buf = f"{brs[min(int(len(brs)*0.95), len(brs)-1)]*100:.1f}%"

        avg_st = "--"
        if d["startup_times"]:
            avg_st = f"{sum(d['startup_times'])/len(d['startup_times'])/1000:.2f}s"

        err_str = f"{d['errors']}"
        print(f"  {cdn_name:<35} {cnt:>8} {avg_buf:>9} {med_buf:>9} {p95_buf:>9} {avg_st:>8} {err_str:>7}")

    # Detail per CDN
    for cdn_name, d in sorted(cdn_data.items(), key=lambda x: -x[1]["count"]):
        if d["count"] < 3:
            continue
        print(f"\n  --- {cdn_name} ({d['count']} sessions) ---")
        if d["buffer_ratios"]:
            brs = sorted(d["buffer_ratios"])
            zero = sum(1 for b in brs if b == 0)
            low = sum(1 for b in brs if 0 < b <= 0.02)
            mid = sum(1 for b in brs if 0.02 < b <= 0.10)
            high = sum(1 for b in brs if b > 0.10)
            print(f"    Buffer distribution: zero={zero}, low(0-2%)={low}, mid(2-10%)={mid}, HIGH(>10%)={high}")
        if d["happiness"]:
            avg_h = sum(d["happiness"]) / len(d["happiness"])
            print(f"    Avg happiness: {avg_h:.1f}/10")
        if d["play_times"]:
            avg_pt = sum(d["play_times"]) / len(d["play_times"]) / 60
            print(f"    Avg play time: {avg_pt:.1f} min")

    # ============================================================
    # 2. DEVICE BREAKDOWN
    # ============================================================
    device_data = defaultdict(lambda: {
        "count": 0, "buffer_ratios": [], "errors": 0, "os": defaultdict(int)
    })

    for s in sessions:
        cat = get_device_category(s)
        d = device_data[cat]
        d["count"] += 1

        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)

        if s.get("error_code"):
            d["errors"] += 1

        dev = s.get("device", {}) or {}
        os_name = dev.get("os", "Unknown") or "Unknown"
        d["os"][os_name] += 1

    print(f"\n\n{'=' * 80}")
    print("  2. DEVICE BREAKDOWN -- Mobile vs Desktop vs Tablet")
    print("=" * 80)
    print()
    print(f"  {'Category':<20} {'Sessions':>8} {'% Total':>8} {'Avg Buf%':>9} {'Errors':>7} {'Top OS':<30}")
    print("  " + "-" * 78)

    for cat, d in sorted(device_data.items(), key=lambda x: -x[1]["count"]):
        cnt = d["count"]
        pct = f"{cnt/n*100:.1f}%"

        avg_buf = "--"
        if d["buffer_ratios"]:
            avg_buf = f"{sum(d['buffer_ratios'])/len(d['buffer_ratios'])*100:.1f}%"

        top_os = sorted(d["os"].items(), key=lambda x: -x[1])
        os_str = ", ".join(f"{k}({v})" for k, v in top_os[:3])

        print(f"  {cat:<20} {cnt:>8} {pct:>8} {avg_buf:>9} {d['errors']:>7} {os_str:<30}")

    # ============================================================
    # 3. ISP BREAKDOWN -- Top buffer offenders
    # ============================================================
    isp_data = defaultdict(lambda: {
        "count": 0, "buffer_ratios": [], "errors": 0
    })

    for s in sessions:
        loc = s.get("location", {}) or {}
        isp = loc.get("isp", "") or s.get("isp", "") or "Unknown"
        if not isp or isp.strip() == "":
            isp = "Unknown"
        d = isp_data[isp]
        d["count"] += 1

        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)

        if s.get("error_code"):
            d["errors"] += 1

    print(f"\n\n{'=' * 80}")
    print("  3. ISP BREAKDOWN -- Top Buffer Offenders")
    print("=" * 80)
    print()

    # Sort by avg buffer ratio (descending), but only ISPs with 3+ sessions
    isp_ranked = []
    for isp_name, d in isp_data.items():
        if d["count"] >= 3 and d["buffer_ratios"]:
            avg = sum(d["buffer_ratios"]) / len(d["buffer_ratios"]) * 100
            isp_ranked.append((isp_name, d, avg))

    isp_ranked.sort(key=lambda x: -x[2])

    print(f"  {'ISP':<40} {'Sessions':>8} {'Avg Buf%':>9} {'Med Buf%':>9} {'Errors':>7}")
    print("  " + "-" * 72)

    for isp_name, d, avg in isp_ranked[:20]:
        cnt = d["count"]
        brs = sorted(d["buffer_ratios"])
        med = brs[len(brs)//2] * 100
        print(f"  {isp_name[:39]:<40} {cnt:>8} {avg:>8.1f}% {med:>8.1f}% {d['errors']:>7}")

    # ISPs with fewer sessions but very high buffer
    small_bad = [(name, d, avg) for name, d, avg in
                 [(k, v, sum(v["buffer_ratios"])/len(v["buffer_ratios"])*100 if v["buffer_ratios"] else 0)
                  for k, v in isp_data.items() if v["count"] < 3 and v["buffer_ratios"]]
                 if avg > 20]
    if small_bad:
        print(f"\n  Small ISPs with high buffer (< 3 sessions, >20% buffer):")
        for name, d, avg in sorted(small_bad, key=lambda x: -x[2])[:10]:
            print(f"    {name[:50]:<50} {d['count']} sessions, {avg:.1f}% buffer")

    # ============================================================
    # 4. RESOURCE URL / CDN HOSTNAME ANALYSIS
    # ============================================================
    print(f"\n\n{'=' * 80}")
    print("  4. RESOURCE URL CDN DETECTION")
    print("=" * 80)
    print()

    hostnames = defaultdict(lambda: {"count": 0, "buffer_ratios": []})
    for s in sessions:
        resource = s.get("resource", "") or ""
        if resource:
            try:
                parsed = urllib.parse.urlparse(resource)
                host = parsed.hostname or "no-host"
            except Exception:
                host = "parse-error"
        else:
            host = "no-resource"

        h = hostnames[host]
        h["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            h["buffer_ratios"].append(br)

    print(f"  {'Hostname':<55} {'Sessions':>8} {'Avg Buf%':>9}")
    print("  " + "-" * 72)
    for host, d in sorted(hostnames.items(), key=lambda x: -x[1]["count"])[:20]:
        avg_buf = "--"
        if d["buffer_ratios"]:
            avg_buf = f"{sum(d['buffer_ratios'])/len(d['buffer_ratios'])*100:.1f}%"
        print(f"  {host[:54]:<55} {d['count']:>8} {avg_buf:>9}")

    # ============================================================
    # 5. OVERALL SUMMARY
    # ============================================================
    all_br = []
    all_st = []
    all_err = 0
    for s in sessions:
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            all_br.append(br)
        st = safe_float(s.get("startup_time"))
        if st is not None:
            all_st.append(st)
        if s.get("error_code"):
            all_err += 1

    print(f"\n\n{'=' * 80}")
    print("  5. OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n  Total sessions analyzed: {n}")
    if all_br:
        brs = sorted(all_br)
        print(f"  Buffer ratio: avg={sum(brs)/len(brs)*100:.1f}%, median={brs[len(brs)//2]*100:.1f}%, p95={brs[min(int(len(brs)*0.95),len(brs)-1)]*100:.1f}%")
        zero = sum(1 for b in brs if b == 0)
        high = sum(1 for b in brs if b > 0.10)
        print(f"    Zero buffer: {zero} ({zero/len(brs)*100:.0f}%), High buffer (>10%): {high} ({high/len(brs)*100:.0f}%)")
    if all_st:
        sts = sorted(all_st)
        print(f"  Startup time: avg={sum(sts)/len(sts)/1000:.2f}s, median={sts[len(sts)//2]/1000:.2f}s, p95={sts[min(int(len(sts)*0.95),len(sts)-1)]/1000:.2f}s")
    print(f"  Error sessions: {all_err} ({all_err/n*100:.1f}%)")

    # ============================================================
    # 6. SAMPLE RAW SESSIONS (high buffer)
    # ============================================================
    high_buf_sessions = sorted(
        [s for s in sessions if safe_float(s.get("buffer_ratio")) is not None],
        key=lambda s: safe_float(s.get("buffer_ratio"), 0),
        reverse=True
    )[:15]

    if high_buf_sessions:
        print(f"\n\n{'=' * 80}")
        print("  6. WORST BUFFER SESSIONS (top 15)")
        print("=" * 80)
        print()
        for i, s in enumerate(high_buf_sessions):
            br = safe_float(s.get("buffer_ratio"), 0) * 100
            title = (s.get("title", "Unknown") or "Unknown")[:45]
            dev = s.get("device", {}) or {}
            dtype = dev.get("device_type", "?")
            os_name = dev.get("os", "?")
            loc = s.get("location", {}) or {}
            isp = loc.get("isp", "") or s.get("isp", "") or "?"
            country = loc.get("country", "?")
            cdn = detect_cdn(s)
            pt = safe_float(s.get("play_time"), 0) / 60
            st = safe_float(s.get("startup_time"), 0) / 1000

            print(f"  [{i+1:>2}] Buffer: {br:.1f}% | {title}")
            print(f"       CDN: {cdn} | Device: {dtype}/{os_name} | ISP: {isp[:35]} | {country}")
            print(f"       Play: {pt:.1f}min | Startup: {st:.2f}s")
            print()


def main():
    if not API_SECRET:
        print("Error: NPAW_API_SECRET not set.", file=sys.stderr)
        sys.exit(1)

    sessions = get_sessions(hours=12, max_sessions=2500)
    if not sessions:
        print("No sessions found in the last 12 hours.")
        sys.exit(1)

    analyze_sessions(sessions)


if __name__ == "__main__":
    main()
