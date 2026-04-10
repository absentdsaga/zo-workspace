import os
import requests
import json
from datetime import datetime, timedelta

API_KEY = os.environ.get("TRELLO_VURT_API_KEY")
API_TOKEN = os.environ.get("TRELLO_VURT_API_TOKEN")
BOARD_ID = "PVtV7XaC"
BASE_URL = "https://api.trello.com/1"

LOG_DIR = "/home/workspace/Logs/live"
today = datetime.now().strftime("%Y-%m-%d")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"{today}.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def api_get(endpoint, params=None):
    params = params or {}
    params["key"] = API_KEY
    params["token"] = API_TOKEN
    resp = requests.get(f"{BASE_URL}{endpoint}", params=params)
    resp.raise_for_status()
    return resp.json()

def api_post(endpoint, data=None):
    data = data or {}
    data["key"] = API_KEY
    data["token"] = API_TOKEN
    resp = requests.post(f"{BASE_URL}{endpoint}", data=data)
    resp.raise_for_status()
    return resp.json()

def api_put(endpoint, data=None):
    data = data or {}
    data["key"] = API_KEY
    data["token"] = API_TOKEN
    resp = requests.put(f"{BASE_URL}{endpoint}", data=data)
    resp.raise_for_status()
    return resp.json()

log("=== TASK 1: Sorting 'This Week' by due date ===")
lists = api_get(f"/boards/{BOARD_ID}/lists")
log(f"Found {len(lists)} lists on board")

this_week_list = None
for lst in lists:
    if lst["name"].lower() == "this week":
        this_week_list = lst
        break

if not this_week_list:
    log("ERROR: 'This Week' list not found!")
else:
    log(f"Found 'This Week' list: {this_week_list['id']}")
    cards = api_get(f"/lists/{this_week_list['id']}/cards", {"fields": "name,due,pos"})
    log(f"Found {len(cards)} cards in 'This Week'")

    def sort_key(card):
        due = card.get("due")
        if due is None:
            return (1, "")
        return (0, due)

    sorted_cards = sorted(cards, key=sort_key)
    log("New order (by due date):")
    for i, card in enumerate(sorted_cards):
        new_pos = (i + 1) * 1024
        api_put(f"/cards/{card['id']}", {"pos": str(new_pos)})
        log(f"  {i+1}. {card['name']} - due: {card.get('due', 'None')}")

log("")
log("=== TASK 2: Flagging stale cards in 'In Progress' ===")

in_progress_list = None
for lst in lists:
    if lst["name"].lower() == "in progress":
        in_progress_list = lst
        break

if not in_progress_list:
    log("ERROR: 'In Progress' list not found!")
else:
    log(f"Found 'In Progress' list: {in_progress_list['id']}")
    cards_ip = api_get(f"/lists/{in_progress_list['id']}/cards",
                       {"fields": "name,dateLastActivity,idLabels"})
    log(f"Found {len(cards_ip)} cards in 'In Progress'")

    labels = api_get(f"/boards/{BOARD_ID}/labels")
    stale_label = None
    for lbl in labels:
        if lbl["name"].lower() == "stale":
            stale_label = lbl
            break

    if not stale_label:
        log("Creating 'Stale' label...")
        stale_label = api_post(f"/boards/{BOARD_ID}/labels",
                               {"name": "Stale", "color": "yellow"})
        log(f"Created label: {stale_label['id']}")
    else:
        log(f"Found existing 'Stale' label: {stale_label['id']}")

    stale_label_id = stale_label["id"]
    five_days_ago = datetime.now() - timedelta(days=5)
    stale_count = 0

    for card in cards_ip:
        last_activity = card.get("dateLastActivity")
        if not last_activity:
            continue

        activity_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
        activity_date_naive = activity_date.replace(tzinfo=None)

        if activity_date_naive < five_days_ago:
            current_labels = card.get("idLabels", [])
            if stale_label_id not in current_labels:
                log(f"Flagging stale: {card['name']} (inactive since {last_activity})")
                api_post(f"/cards/{card['id']}/idLabels", {"value": stale_label_id})
                stale_count += 1
            else:
                log(f"Already stale: {card['name']}")

    log(f"Total cards flagged as stale: {stale_count}")

log("")
log("=== MAINTENANCE COMPLETE ===")
