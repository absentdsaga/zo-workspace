#!/usr/bin/env python3
"""
VURT Capture Check — scans for uncaptured VURT information.

Compares known contacts/configs against the master doc and memory files
to flag anything that might be missing or stale.
"""

import os, json, re, sys
from datetime import datetime

MASTER_DOC = "/home/workspace/Documents/VURT-master.md"
MEMORY_DIR = "/root/.claude/projects/-home-workspace/memory"
CAPTURE_LOG = "/home/workspace/Documents/VURT-capture-log.md"
LOGS_DIR = "/home/workspace/Logs"

KNOWN_CRITICAL_CONTACTS = {
    "mark@myvurt.com": "Mark Samuels — Co-founder/Director",
    "dioni@myvurt.com": "Dioni Vasquez — Co-lead",
    "ted@thesourcegroups.com": "Ted Lucas — Investor (Slip-N-Slide)",
    "hilmon@thesourcegroups.com": "Hilmon Sorey — Lead Investor",
    "tarikamin@gmail.com": "Tarik Brooks — Advisory (Combs Enterprises/Revolt)",
    "eric@swirlfilms.com": "Eric Tomosunas — Co-founder (Swirl Films)",
    "ariella@thesourcegroups.com": "Ariella — The Source Groups",
    "dioniproduces@gmail.com": "Dioni — personal Gmail",
    "christian@simplesocial.info": "Christian — Simple Social",
    "alex@simplesocial.info": "Alex — Simple Social",
}

KNOWN_CRITICAL_CONFIGS = {
    "daily_report_agent": "a8df5858-1fd9-4b87-9481-d04aa4a75de2",
    "ga4_property_prod": "518738893",
    "ga4_property_test": "518543881",
    "report_send_method": "use_app_gmail",
    "report_schedule": "8 AM ET daily",
}


def check_master_doc():
    """Check if master doc contains all critical contacts."""
    if not os.path.exists(MASTER_DOC):
        print("WARNING: VURT master doc not found!")
        return []

    with open(MASTER_DOC) as f:
        content = f.read()

    missing = []
    for email, desc in KNOWN_CRITICAL_CONTACTS.items():
        if email not in content:
            missing.append(f"  MISSING from master doc: {email} ({desc})")

    for key, val in KNOWN_CRITICAL_CONFIGS.items():
        if val not in content:
            missing.append(f"  MISSING config from master doc: {key}={val}")

    return missing


def check_memory_files():
    """Check if memory files exist and contain critical info."""
    issues = []

    dist_file = os.path.join(MEMORY_DIR, "project_vurt_report_distribution.md")
    if not os.path.exists(dist_file):
        issues.append("  MISSING memory file: project_vurt_report_distribution.md")
    else:
        with open(dist_file) as f:
            content = f.read()
        for email in ["mark@myvurt.com", "ted@thesourcegroups.com", "hilmon@thesourcegroups.com",
                       "tarikamin@gmail.com", "eric@swirlfilms.com", "ariella@thesourcegroups.com"]:
            if email not in content:
                issues.append(f"  MISSING from distribution memory: {email}")

    role_file = os.path.join(MEMORY_DIR, "project_vurt_role.md")
    if not os.path.exists(role_file):
        issues.append("  MISSING memory file: project_vurt_role.md")

    return issues


def scan_recent_logs_for_vurt():
    """Scan today's logs for VURT-related content that might need capturing."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(LOGS_DIR, today)

    if not os.path.exists(log_dir):
        return []

    vurt_mentions = []
    for f in os.listdir(log_dir):
        filepath = os.path.join(log_dir, f)
        if not os.path.isfile(filepath):
            continue
        try:
            with open(filepath) as fh:
                content = fh.read().lower()
                if "vurt" in content:
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = set(re.findall(email_pattern, content))
                    new_emails = emails - set(e.lower() for e in KNOWN_CRITICAL_CONTACTS.keys())
                    if new_emails:
                        vurt_mentions.append(f"  New emails found in {f}: {', '.join(new_emails)}")
        except:
            pass

    return vurt_mentions


def main():
    print("=" * 60)
    print("VURT CAPTURE CHECK")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_issues = []

    print("\n[1] Checking master doc...")
    issues = check_master_doc()
    if issues:
        all_issues.extend(issues)
        for i in issues:
            print(f"  ⚠️  {i}")
    else:
        print("  ✅ All critical contacts and configs present")

    print("\n[2] Checking memory files...")
    issues = check_memory_files()
    if issues:
        all_issues.extend(issues)
        for i in issues:
            print(f"  ⚠️  {i}")
    else:
        print("  ✅ All memory files intact")

    print("\n[3] Scanning recent logs for uncaptured VURT info...")
    issues = scan_recent_logs_for_vurt()
    if issues:
        all_issues.extend(issues)
        for i in issues:
            print(f"  ⚠️  {i}")
    else:
        print("  ✅ No uncaptured emails in recent logs")

    print("\n" + "=" * 60)
    if all_issues:
        print(f"RESULT: {len(all_issues)} issue(s) found — ACTION NEEDED")
    else:
        print("RESULT: All clear — VURT context is persisted")
    print("=" * 60)

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
