#!/usr/bin/env python3
"""VURT Trello Daily Maintenance Script
- Task 1: Sort "This Week" list by due date ascending
- Task 2: Flag stale cards in "In Progress" (inactive > 5 days)
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Config
API_KEY = os.environ.get("TRELLO_VURT_API_KEY")
API_TOKEN = os.environ.get("TRELLO_VURT_API_TOKEN")
BOARD_SHORT_ID = "PVtV7XaC"
BOARD_FULL_ID = "69c067605dae4ae03cd62807"
BASE_URL = "https://api.trello.com/1"

# Log file
LOG_DIR = "/home/workspace/Logs/live"
LOG_FILE = os.path.join(LOG_DIR, "vurt_trello_maintenance_2026-03-23.jsonl")

def log(level: str, message: str, data: dict = None):
    """Write log entry to file"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
    }
    if data:
        entry["data"] = data
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

def api_put(endpoint: str, data: dict = None) -> dict:
    """Make PUT request to Trello API"""
    url = f"{BASE_URL}{endpoint}"
    defaults = {"key": API_KEY, "token": API_TOKEN}
    if data:
        defaults.update(data)
    resp = requests.put(url, data=defaults)
    resp.raise_for_status()
    return resp.json()

def find_list_by_name(lists: list, name: str) -> dict:
    """Find a list by name"""
    for lst in lists:
        if lst["name"].lower() == name.lower():
            return lst
    return None

def get_board_labels() -> list:
    """Get all labels on the board"""
    return api_get(f"/boards/{BOARD_FULL_ID}/labels", {"fields": "id,name,color"})

def main():
    log("task_start", "Starting VURT Trello Daily Maintenance")
    
    # ========== TASK 1: Sort "This Week" list ==========
    log("info", "=== TASK 1: Sorting 'This Week' list by due date ===")
    
    try:
        # Get all lists on the board
        lists = api_get(f"/boards/{BOARD_SHORT_ID}/lists")
        log("result", f"Found {len(lists)} lists on board", {"lists": [l["name"] for l in lists]})
        
        # Find "This Week" list
        this_week_list = find_list_by_name(lists, "This Week")
        if not this_week_list:
            log("error", "Could not find 'This Week' list")
        else:
            log("info", f"Found 'This Week' list", {"list_id": this_week_list["id"], "name": this_week_list["name"]})
            
            # Get cards in "This Week"
            cards = api_get(f"/lists/{this_week_list['id']}/cards", {"fields": "id,name,due,pos"})
            log("result", f"Found {len(cards)} cards in 'This Week'", {"card_count": len(cards)})
            
            # Sort cards: non-null due dates first (ascending), nulls last
            def sort_key(card):
                due = card.get("due")
                if due is None:
                    return (1, "")  # nulls go last
                return (0, due)    # sort by due date ascending
            
            sorted_cards = sorted(cards, key=sort_key)
            
            # Log sorted order
            for i, card in enumerate(sorted_cards):
                log("info", f"Card sorted order: {i+1}", {"id": card["id"], "name": card["name"], "due": card.get("due")})
            
            # Update positions: 1024, 2048, 3072, etc.
            for i, card in enumerate(sorted_cards):
                new_pos = (i + 1) * 1024
                api_put(f"/cards/{card['id']}", {"pos": str(new_pos)})
                log("result", f"Updated card position", {"card_id": card["id"], "name": card["name"], "new_pos": new_pos})
            
            log("info", f"TASK 1 COMPLETE: Sorted {len(sorted_cards)} cards in 'This Week'")
    
    except Exception as e:
        log("error", f"TASK 1 FAILED: {str(e)}")
    
    # ========== TASK 2: Flag stale cards in "In Progress" ==========
    log("info", "=== TASK 2: Flagging stale cards in 'In Progress' ===")
    
    try:
        # Get all lists (may need to refetch)
        lists = api_get(f"/boards/{BOARD_SHORT_ID}/lists")
        
        # Find "In Progress" list
        in_progress_list = find_list_by_name(lists, "In Progress")
        if not in_progress_list:
            log("error", "Could not find 'In Progress' list")
        else:
            log("info", f"Found 'In Progress' list", {"list_id": in_progress_list["id"]})
            
            # Get cards with required fields
            cards = api_get(f"/lists/{in_progress_list['id']}/cards", 
                           {"fields": "name,dateLastActivity,idLabels"})
            log("result", f"Found {len(cards)} cards in 'In Progress'", {"card_count": len(cards)})
            
            # Get existing board labels to find "Stale"
            board_labels = get_board_labels()
            stale_label = None
            for label in board_labels:
                if label.get("name", "").lower() == "stale":
                    stale_label = label
                    break
            
            # Create "Stale" label if it doesn't exist
            if not stale_label:
                log("info", "Creating 'Stale' label on board")
                new_label = api_post(f"/boards/{BOARD_FULL_ID}/labels", 
                                    {"name": "Stale", "color": "yellow"})
                stale_label = new_label
                log("result", "Created 'Stale' label", {"label_id": stale_label["id"]})
            else:
                log("info", "'Stale' label already exists", {"label_id": stale_label["id"]})
            
            stale_label_id = stale_label["id"]
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            stale_cards_count = 0
            
            for card in cards:
                # Parse dateLastActivity
                last_activity_str = card.get("dateLastActivity")
                if not last_activity_str:
                    log("info", f"Card has no activity date, skipping", {"card_id": card["id"], "name": card["name"]})
                    continue
                
                last_activity = datetime.fromisoformat(last_activity_str.replace("Z", "+00:00"))
                last_activity_naive = last_activity.replace(tzinfo=None) if last_activity.tzinfo else last_activity
                
                # Check if older than 5 days
                if last_activity_naive < five_days_ago:
                    card_labels = card.get("idLabels", [])
                    
                    # Check if already has Stale label
                    if stale_label_id in card_labels:
                        log("info", f"Card already has Stale label, skipping", {"card_id": card["id"], "name": card["name"]})
                    else:
                        # Add Stale label to card
                        api_post(f"/cards/{card['id']}/idLabels", {"value": stale_label_id})
                        log("result", f"Added 'Stale' label to stale card", 
                            {"card_id": card["id"], "name": card["name"], "last_activity": last_activity_str})
                        stale_cards_count += 1
            
            log("info", f"TASK 2 COMPLETE: Flagged {stale_cards_count} stale cards in 'In Progress'")
    
    except Exception as e:
        log("error", f"TASK 2 FAILED: {str(e)}")
    
    log("task_complete", "VURT Trello Daily Maintenance completed successfully")

if __name__ == "__main__":
    main()
