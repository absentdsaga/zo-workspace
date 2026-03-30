#!/usr/bin/env python3
"""
VURT Social Tracker — State Validator
Reads state.md and flags stale entries, missing info, and upcoming deadlines.
"""
import sys
import os
from datetime import datetime, timedelta

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state.md")

def main():
    if not os.path.exists(STATE_FILE):
        print("ERROR: state.md not found. Create it first.")
        sys.exit(1)

    with open(STATE_FILE, "r") as f:
        content = f.read()

    today = datetime.now().date()
    lines = content.split("\n")

    # Find last updated date
    for line in lines:
        if "Last Updated:" in line:
            try:
                date_str = line.split("Last Updated:")[1].strip()
                last_updated = datetime.strptime(date_str, "%Y-%m-%d").date()
                days_stale = (today - last_updated).days
                if days_stale > 2:
                    print(f"WARNING: State file is {days_stale} days old (last updated {last_updated})")
                elif days_stale == 0:
                    print(f"OK: State file is current (updated today)")
                else:
                    print(f"OK: State file updated {days_stale} day(s) ago")
            except ValueError:
                print("WARNING: Could not parse last updated date")
            break

    # Find 72-hour assessment deadlines
    for line in lines:
        if "72-hour assessment due:" in line:
            try:
                date_str = line.split("due:")[1].strip().split(" ")[0]
                due_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if due_date <= today:
                    print(f"ACTION NEEDED: 72-hour assessment is DUE or OVERDUE ({due_date})")
                elif (due_date - today).days <= 1:
                    print(f"UPCOMING: 72-hour assessment due tomorrow ({due_date})")
            except (ValueError, IndexError):
                pass

    # Flag INCOMPLETE items
    incomplete_count = content.count("INCOMPLETE")
    if incomplete_count > 0:
        print(f"INFO: {incomplete_count} INCOMPLETE item(s) need attention")

    # Flag PENDING DECISIONS
    in_pending = False
    pending_count = 0
    for line in lines:
        if "## PENDING DECISIONS" in line:
            in_pending = True
            continue
        if in_pending and line.startswith("## "):
            break
        if in_pending and line.startswith("- "):
            pending_count += 1

    if pending_count > 0:
        print(f"INFO: {pending_count} pending decision(s) to resolve")

    print("\nDone. Read state.md for full context.")

if __name__ == "__main__":
    main()
