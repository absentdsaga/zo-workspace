#!/usr/bin/env python3
"""VURT Trello Weekly Triage Card Creator
Creates a triage card on the VURT Production Trello board every Monday.
"""

import os
import requests
import json
from datetime import datetime

# Config
API_KEY = os.environ.get("TRELLO_VURT_API_KEY")
API_TOKEN = os.environ.get("TRELLO_VURT_API_TOKEN")
BOARD_SHORT_ID = "PVtV7XaC"
BASE_URL = "https://api.trello.com/1"

# Log file - use today's date
TODAY = datetime.utcnow().strftime("%Y-%m-%d")
LOG_DIR = "/home/workspace/Logs/live"
LOG_FILE = os.path.join(LOG_DIR, f"vurt_weekly_triage_{TODAY}.jsonl")

def log(level: str, message: str, data: dict = None):
    """Write log entry to file"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
    }
    if data:
        entry["data"] = data
    
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{level}] {message}")
    if data:
        print(f"  Data: {json.dumps(data)}")

def api_get(endpoint: str, params: dict = None) -> dict:
    """Make GET request to Trello API"""
    url = f"{BASE_URL}{endpoint}"
    defaults = {"key": API_KEY, "token": API_TOKEN}
    if params:
        defaults.update(params)
    resp = requests.get(url, params=defaults)
    resp.raise_for_status()
    return resp.json()

def api_post(endpoint: str, data: dict = None) -> dict:
    """Make POST request to Trello API"""
    url = f"{BASE_URL}{endpoint}"
    defaults = {"key": API_KEY, "token": API_TOKEN}
    if data:
        defaults.update(data)
    resp = requests.post(url, data=defaults)
    resp.raise_for_status()
    return resp.json()

def find_list_by_name(lists: list, name: str) -> dict:
    """Find a list by name"""
    for lst in lists:
        if lst["name"].lower() == name.lower():
            return lst
    return None

def main():
    log("task_start", "Starting VURT Weekly Triage Card Creation")
    
    try:
        # Step 1: Get all lists on the board to find "This Week"
        log("info", "Fetching board lists...")
        lists = api_get(f"/boards/{BOARD_SHORT_ID}/lists")
        log("result", f"Found {len(lists)} lists on board", {"lists": [l["name"] for l in lists]})
        
        # Find "This Week" list
        this_week_list = find_list_by_name(lists, "This Week")
        if not this_week_list:
            log("error", "Could not find 'This Week' list")
            return
        
        log("info", f"Found 'This Week' list", {"list_id": this_week_list["id"]})
        
        # Step 2: Create the triage card
        # Due date: today (Monday) at end of day
        due_date = f"{TODAY}T23:59:00.000Z"
        
        card_data = {
            "idList": this_week_list["id"],
            "name": "Weekly Triage: Review Inbox, prioritize This Week",
            "desc": """Monday triage checklist:
- [ ] Review all Inbox cards
- [ ] Move priority items to This Week
- [ ] Archive anything in Inbox older than 3 weeks
- [ ] Check Review/Blocked for stuck items
- [ ] 15 minutes max""",
            "pos": "top",
            "due": due_date
        }
        
        log("info", "Creating triage card...", {"card_data": card_data})
        new_card = api_post("/cards", card_data)
        
        log("result", "Successfully created triage card", {
            "card_id": new_card.get("id"),
            "card_name": new_card.get("name"),
            "card_url": new_card.get("shortUrl"),
            "due": due_date
        })
        
        log("task_complete", "VURT Weekly Triage Card created successfully")
        
    except Exception as e:
        log("error", f"Failed to create triage card: {str(e)}")
        raise

if __name__ == "__main__":
    main()