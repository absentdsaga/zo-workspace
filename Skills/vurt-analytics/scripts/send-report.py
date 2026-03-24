#!/usr/bin/env python3
"""Generate VURT daily report and prepare for sending.

Includes a sent-flag guard to prevent duplicate sends.
Usage:
  python3 send-report.py generate   # Generate report, output metadata
  python3 send-report.py mark-sent  # Mark today's report as sent
  python3 send-report.py check      # Check if already sent today
"""

import sys, os, json, fcntl
from datetime import datetime

FLAG_DIR = "/home/workspace/Skills/vurt-analytics/.sent-flags"
REPORT_DIR = "/home/workspace/Documents/analytics-reports"
LOCK_FILE = "/home/workspace/Skills/vurt-analytics/.sent-flags/report.lock"

def flag_path():
    return os.path.join(FLAG_DIR, f"sent-{datetime.now().strftime('%Y-%m-%d')}.flag")

def already_sent():
    return os.path.exists(flag_path())

def acquire_lock():
    os.makedirs(FLAG_DIR, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fd
    except BlockingIOError:
        print("LOCKED")
        print("Another process is already generating/sending the report. Exiting.")
        sys.exit(0)

def mark_sent():
    os.makedirs(FLAG_DIR, exist_ok=True)
    with open(flag_path(), "w") as f:
        f.write(datetime.now().isoformat())
    print(f"Marked as sent: {flag_path()}")

def generate():
    if already_sent():
        print("ALREADY_SENT")
        print(f"Today's report was already sent. Flag: {flag_path()}")
        print("Do NOT send again. Your job is done.")
        sys.exit(0)

    lock_fd = acquire_lock()

    if already_sent():
        print("ALREADY_SENT")
        print("Race condition caught: another process sent while we waited for lock.")
        sys.exit(0)

    mark_sent()
    print("Flag set BEFORE generation to prevent duplicates.")

    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    dr = import_module("daily-report")

    report = dr.build_report()
    os.makedirs(REPORT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    md_path = f"{REPORT_DIR}/vurt-daily-{date_str}.md"
    with open(md_path, "w") as f:
        f.write(report)

    from email_renderer import markdown_to_html
    html = markdown_to_html(report)
    html_path = f"{REPORT_DIR}/vurt-daily-{date_str}.html"
    with open(html_path, "w") as f:
        f.write(html)

    date_display = datetime.now().strftime("%B %d, %Y")

    metadata = {
        "status": "READY_TO_SEND",
        "html_path": html_path,
        "subject": f"VURT Daily Analytics Report — {date_display}",
        "to": ["dioni@myvurt.com"],
        "cc": [],
    }

    print("REPORT_METADATA_START")
    print(json.dumps(metadata, indent=2))
    print("REPORT_METADATA_END")
    print(f"\nHTML file: {html_path} ({os.path.getsize(html_path)} bytes)")

    lock_fd.close()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if cmd == "generate":
        generate()
    elif cmd == "mark-sent":
        mark_sent()
    elif cmd == "check":
        if already_sent():
            print("ALREADY_SENT")
        else:
            print("NOT_SENT")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
