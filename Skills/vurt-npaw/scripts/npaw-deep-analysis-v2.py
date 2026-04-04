#!/usr/bin/env python3
"""Deep NPAW analysis v2 - corrected field names and buffer_ratio interpretation.

Key corrections from v1:
- buffer_ratio is ALREADY a percentage (e.g. 95.03 = 95.03%), NOT 0-1
- Timestamp field is init_at / init_at_unix
- Referrer field is referral / referral_type / referral_domain
- ISP is top-level field, not under location
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
        resp = urllib.request.urlopen(urllib.request.Request(url), timeout=90)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body[:500]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def get_sessions(from_date, to_date, max_sessions=3000):
    all_sessions = []
    offset = 0
    per_page = 500
    dev_filtered = 0

    print(f"Pulling sessions {from_date} to {to_date}...", file=sys.stderr)
    while len(all_sessions) < max_sessions:
        data = api_get("rawdata", [
            ("fromDate", from_date), ("toDate", to_date),
            ("type", "VOD"), ("timezone", "America/New_York"),
            ("limit", str(per_page)), ("offset", str(offset)),
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
        print(f"  Page {offset // per_page + 1}: {len(batch)} rows (kept: {len(all_sessions)}, dev: {dev_filtered})", file=sys.stderr)
        if len(batch) < per_page:
            break
        offset += len(batch)

    print(f"  Total: {len(all_sessions)} sessions", file=sys.stderr)
    return all_sessions[:max_sessions]


def sf(val, default=None):
    if val is None or val == "":
        return default
    try:
        return float(val)
    except:
        return default


def get_hour(s):
    ts = s.get("init_at_unix")
    if ts:
        try:
            dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d %H:00 UTC")
        except:
            pass
    ia = s.get("init_at", "")
    if ia and len(ia) >= 13:
        return ia[:13] + ":00 ET"
    return "Unknown"


def get_date(s):
    ia = s.get("init_at", "")
    if ia and len(ia) >= 10:
        return ia[:10]
    ts = s.get("init_at_unix")
    if ts:
        try:
            return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        except:
            pass
    return "Unknown"


def get_cdn(s):
    cdn = (s.get("cdn", "") or "").strip()
    if cdn:
        return cdn
    resource = (s.get("media_resource", "") or s.get("resource", "") or "").lower()
    if "cloudfront" in resource:
        return "CloudFront (URL)"
    elif "fastly" in resource:
        return "Fastly (URL)"
    elif "cloudflare" in resource:
        return "Cloudflare (URL)"
    return "Unknown"


def get_device(s):
    dev = s.get("device", {}) or {}
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


def get_referrer(s):
    ref = (s.get("referral", "") or "").lower()
    ref_type = (s.get("referral_type", "") or "").lower()
    ref_domain = (s.get("referral_domain", "") or "").lower()
    page = (s.get("page", "") or "").lower()
    combined = f"{ref} {ref_type} {ref_domain} {page}"

    if "facebook" in combined or "fb." in combined or "fbclid" in combined:
        return "Facebook"
    elif "instagram" in combined or "ig." in combined:
        return "Instagram"
    elif "tiktok" in combined or "tt." in combined:
        return "TikTok"
    elif "google" in combined or "gclid" in combined:
        return "Google"
    elif "youtube" in combined or "yt." in combined:
        return "YouTube"
    elif "twitter" in combined or "t.co" in combined or "x.com" in combined:
        return "X/Twitter"
    elif ref and ref not in ["", "none", "null", "(none)"]:
        if "myvurt" in ref:
            return "Internal"
        return f"Other ({ref_domain or ref[:40]})"
    else:
        return "Direct/None"


def percentile(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    idx = min(int(len(s) * p), len(s) - 1)
    return s[idx]


def stats_for(vals):
    if not vals:
        return {}
    s = sorted(vals)
    return {
        "count": len(s),
        "avg": round(sum(s) / len(s), 2),
        "median": round(s[len(s) // 2], 2),
        "p5": round(s[min(int(len(s) * 0.05), len(s) - 1)], 2),
        "p95": round(s[min(int(len(s) * 0.95), len(s) - 1)], 2),
        "min": round(s[0], 2),
        "max": round(s[-1], 2),
    }


def analyze(sessions):
    n = len(sessions)
    results = {"total_sessions": n}

    # Collect per-session enriched data
    enriched = []
    for s in sessions:
        enriched.append({
            "hour": get_hour(s),
            "date": get_date(s),
            "cdn": get_cdn(s),
            "device": get_device(s),
            "referrer": get_referrer(s),
            "buffer_ratio": sf(s.get("buffer_ratio")),  # Already a percentage
            "startup_time": sf(s.get("startup_time")),   # ms
            "play_time": sf(s.get("play_time")),          # seconds
            "error_code": s.get("error_code", ""),
            "happiness": sf(s.get("happiness_score")),
            "isp": s.get("isp", "") or "",
            "title": s.get("title", ""),
            "os": (s.get("device", {}) or {}).get("os", ""),
            "init_at": s.get("init_at", ""),
            "referral_raw": s.get("referral", ""),
            "referral_type_raw": s.get("referral_type", ""),
            "referral_domain_raw": s.get("referral_domain", ""),
            "page_raw": s.get("page", ""),
        })

    # ===== 1. BUFFER RATIO BY HOUR =====
    by_hour = defaultdict(list)
    for e in enriched:
        by_hour[e["hour"]].append(e)

    hourly_out = {}
    for h in sorted(by_hour.keys()):
        group = by_hour[h]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        errs = sum(1 for e in group if e["error_code"])
        hourly_out[h] = {
            "sessions": len(group),
            "errors": errs,
            "buffer_ratio_stats": stats_for(brs),
            "zero_buffer_sessions": sum(1 for b in brs if b == 0),
            "high_buffer_gt10pct": sum(1 for b in brs if b > 10),
            "startup_ms_stats": stats_for(sts),
            "play_sec_stats": stats_for(pts),
            "zero_play_count": sum(1 for p in pts if p == 0),
        }
    results["by_hour"] = hourly_out

    # ===== 2. BUFFER RATIO BY CDN =====
    by_cdn = defaultdict(list)
    for e in enriched:
        by_cdn[e["cdn"]].append(e)

    cdn_out = {}
    for cdn_name in sorted(by_cdn.keys(), key=lambda x: -len(by_cdn[x])):
        group = by_cdn[cdn_name]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        hps = [e["happiness"] for e in group if e["happiness"] is not None]
        errs = sum(1 for e in group if e["error_code"])
        cdn_out[cdn_name] = {
            "sessions": len(group),
            "errors": errs,
            "buffer_ratio_stats": stats_for(brs),
            "zero_buffer": sum(1 for b in brs if b == 0),
            "high_buffer_gt10pct": sum(1 for b in brs if b > 10),
            "startup_ms_stats": stats_for(sts),
            "play_sec_stats": stats_for(pts),
            "zero_play": sum(1 for p in pts if p == 0),
            "happiness_stats": stats_for(hps),
        }
    results["by_cdn"] = cdn_out

    # ===== 3. BUFFER RATIO BY DEVICE =====
    by_device = defaultdict(list)
    for e in enriched:
        by_device[e["device"]].append(e)

    device_out = {}
    for dname in sorted(by_device.keys(), key=lambda x: -len(by_device[x])):
        group = by_device[dname]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        os_counts = defaultdict(int)
        for e in group:
            os_counts[e["os"] or "Unknown"] += 1
        device_out[dname] = {
            "sessions": len(group),
            "pct_of_total": round(len(group) / max(n, 1) * 100, 1),
            "buffer_ratio_stats": stats_for(brs),
            "high_buffer_gt10pct": sum(1 for b in brs if b > 10),
            "startup_ms_stats": stats_for(sts),
            "play_sec_stats": stats_for(pts),
            "zero_play": sum(1 for p in pts if p == 0),
            "os_breakdown": dict(sorted(os_counts.items(), key=lambda x: -x[1])[:5]),
        }
    results["by_device"] = device_out

    # ===== 4. BUFFER RATIO BY REFERRER =====
    by_ref = defaultdict(list)
    for e in enriched:
        by_ref[e["referrer"]].append(e)

    ref_out = {}
    for rname in sorted(by_ref.keys(), key=lambda x: -len(by_ref[x])):
        group = by_ref[rname]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        ref_out[rname] = {
            "sessions": len(group),
            "pct_of_total": round(len(group) / max(n, 1) * 100, 1),
            "buffer_ratio_stats": stats_for(brs),
            "startup_ms_stats": stats_for(sts),
            "play_sec_stats": stats_for(pts),
            "zero_play": sum(1 for p in pts if p == 0),
            "under_5s_play": sum(1 for p in pts if 0 < p < 5),
        }
    results["by_referrer"] = ref_out

    # ===== 5. SOCIAL vs DIRECT =====
    social = [e for e in enriched if e["referrer"] in ("Facebook", "Instagram")]
    direct = [e for e in enriched if e["referrer"] in ("Direct/None", "Internal")]

    def group_summary(group, label):
        if not group:
            return {"label": label, "count": 0}
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        return {
            "label": label, "count": len(group),
            "buffer_ratio_stats": stats_for(brs),
            "startup_ms_stats": stats_for(sts),
            "play_sec_stats": stats_for(pts),
            "zero_play": sum(1 for p in pts if p == 0),
            "under_10s_play": sum(1 for p in pts if 0 < p < 10),
            "errors": sum(1 for e in group if e["error_code"]),
        }

    results["social_vs_direct"] = {
        "fb_ig": group_summary(social, "Facebook+Instagram"),
        "direct": group_summary(direct, "Direct/Internal"),
    }

    # ===== 6. STARTUP TIME BY DATE =====
    by_date = defaultdict(list)
    for e in enriched:
        by_date[e["date"]].append(e)

    date_out = {}
    for d in sorted(by_date.keys()):
        group = by_date[d]
        sts = [e["startup_time"] for e in group if e["startup_time"] is not None]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        errs = sum(1 for e in group if e["error_code"])
        cdns = defaultdict(int)
        for e in group:
            cdns[e["cdn"]] += 1
        date_out[d] = {
            "sessions": len(group),
            "errors": errs,
            "startup_ms_stats": stats_for(sts),
            "buffer_ratio_stats": stats_for(brs),
            "play_sec_stats": stats_for(pts),
            "zero_play": sum(1 for p in pts if p == 0),
            "cdn_breakdown": dict(cdns),
        }
    results["by_date"] = date_out

    # ===== 7. ERROR ANALYSIS =====
    error_sessions = [e for e in enriched if e["error_code"]]
    error_codes = defaultdict(int)
    for e in error_sessions:
        error_codes[str(e["error_code"])] += 1
    results["errors"] = {
        "total": len(error_sessions),
        "rate_pct": round(len(error_sessions) / max(n, 1) * 100, 2),
        "codes": dict(error_codes),
    }

    # ===== 8. PLAY TIME DISTRIBUTION =====
    all_pts = [e["play_time"] for e in enriched if e["play_time"] is not None]
    if all_pts:
        results["play_time_distribution"] = {
            "total_sessions_with_playtime": len(all_pts),
            "stats": stats_for(all_pts),
            "buckets": {
                "0s_exactly": sum(1 for p in all_pts if p == 0),
                "1_to_5s": sum(1 for p in all_pts if 0 < p <= 5),
                "5_to_10s": sum(1 for p in all_pts if 5 < p <= 10),
                "10_to_30s": sum(1 for p in all_pts if 10 < p <= 30),
                "30s_to_1min": sum(1 for p in all_pts if 30 < p <= 60),
                "1_to_5min": sum(1 for p in all_pts if 60 < p <= 300),
                "5_to_15min": sum(1 for p in all_pts if 300 < p <= 900),
                "15min_plus": sum(1 for p in all_pts if p > 900),
            },
        }

    # ===== 9. RAW REFERRAL FIELD DUMP (for debugging) =====
    ref_raw_samples = set()
    for e in enriched:
        combo = f"referral={e['referral_raw']}|type={e['referral_type_raw']}|domain={e['referral_domain_raw']}|page={e['page_raw']}"
        ref_raw_samples.add(combo)
    results["raw_referral_samples"] = sorted(list(ref_raw_samples))[:50]

    # ===== 10. TOP ISPs =====
    by_isp = defaultdict(list)
    for e in enriched:
        by_isp[e["isp"] or "Unknown"].append(e)

    isp_out = {}
    for isp in sorted(by_isp.keys(), key=lambda x: -len(by_isp[x]))[:20]:
        group = by_isp[isp]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        isp_out[isp] = {
            "sessions": len(group),
            "buffer_ratio_stats": stats_for(brs),
            "high_buffer_gt10pct": sum(1 for b in brs if b > 10),
        }
    results["top_isps"] = isp_out

    # ===== 11. TOP TITLES =====
    by_title = defaultdict(list)
    for e in enriched:
        by_title[e["title"] or "Unknown"].append(e)

    title_out = {}
    for t in sorted(by_title.keys(), key=lambda x: -len(by_title[x]))[:15]:
        group = by_title[t]
        brs = [e["buffer_ratio"] for e in group if e["buffer_ratio"] is not None]
        pts = [e["play_time"] for e in group if e["play_time"] is not None]
        title_out[t] = {
            "sessions": len(group),
            "buffer_ratio_stats": stats_for(brs),
            "play_sec_stats": stats_for(pts),
        }
    results["top_titles"] = title_out

    return results


def main():
    if not API_SECRET:
        print("Error: NPAW_API_SECRET not set.", file=sys.stderr)
        sys.exit(1)

    # Pull Apr 1-4 (wide window to see CDN transition and pre/post deploy)
    sessions = get_sessions("2026-04-01", "2026-04-04", max_sessions=3000)
    if not sessions:
        print("No sessions found.", file=sys.stderr)
        sys.exit(1)

    results = analyze(sessions)

    # Also pull Mar 30-31 for pre-deploy baseline
    print("\nPulling pre-deploy baseline (Mar 30-31)...", file=sys.stderr)
    baseline = get_sessions("2026-03-30", "2026-03-31", max_sessions=2000)
    if baseline:
        results["baseline_mar30_31"] = analyze(baseline)

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
