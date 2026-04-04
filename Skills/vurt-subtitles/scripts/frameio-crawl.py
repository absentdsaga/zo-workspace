"""
Frame.io v4 crawler — enumerate all video files with durations.
Outputs exact file count, total minutes, and cost estimate.
No transcription — just inventory.
"""
import json, urllib.request, urllib.parse, os, sys, csv
from datetime import datetime, timezone

SECRETS_PATH = "/home/workspace/.secrets/adobe-tokens.json"
CLIENT_ID = os.environ.get("VURT_ADOBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("VURT_ADOBE_CLIENT_SECRET", "")
ACCT = "6c77dc3c-f088-486d-a8e3-678fc0fcbd70"
PROJECT = "6a0a9a57-379a-4d48-a7ba-f63982fa3acc"
BASE = f"https://api.frame.io/v4/accounts/{ACCT}"
UA = "VURT-Subtitle-Pipeline/2.0"
OUT_DIR = "/home/workspace/Documents/frameio-srt-test"

def get_token():
    tokens = json.load(open(SECRETS_PATH))
    obtained_str = tokens.get("obtained_at", "2000-01-01T00:00:00+00:00").replace("Z", "+00:00")
    obtained = datetime.fromisoformat(obtained_str)
    if (datetime.now(timezone.utc) - obtained).total_seconds() > 3000:
        return refresh_token(tokens)
    return tokens["access_token"]

def refresh_token(tokens=None):
    if tokens is None:
        tokens = json.load(open(SECRETS_PATH))
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://ims-na1.adobelogin.com/ims/token/v3",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        new = json.loads(r.read())
    new["obtained_at"] = datetime.now(timezone.utc).isoformat()
    with open(SECRETS_PATH, "w") as f:
        json.dump(new, f, indent=2)
    print("  [Token refreshed]")
    return new["access_token"]

def fio(path):
    token = get_token()
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {token}", "x-api-key": CLIENT_ID, "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("  [403 - refreshing...]")
            token = refresh_token()
            req = urllib.request.Request(
                f"{BASE}{path}",
                headers={"Authorization": f"Bearer {token}", "x-api-key": CLIENT_ID, "User-Agent": UA},
            )
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        raise

def crawl_folder(folder_id, path="", depth=0):
    """Recursively crawl a folder and collect all video files."""
    files = []
    next_url = f"/folders/{folder_id}/children?page_size=25"
    while next_url:
        try:
            # Handle full URLs from pagination links
            if next_url.startswith("http"):
                token = get_token()
                req = urllib.request.Request(next_url, headers={
                    "Authorization": f"Bearer {token}", "x-api-key": CLIENT_ID, "User-Agent": UA,
                })
                with urllib.request.urlopen(req) as r:
                    resp = json.loads(r.read())
            else:
                resp = fio(next_url)
        except Exception as e:
            print(f"  {'  '*depth}ERROR crawling {folder_id}: {e}")
            break

        items = resp.get("data", [])
        if not items:
            break

        # Handle cursor-based pagination
        links = resp.get("links", {})
        next_url = links.get("next")  # None or full URL

        for item in items:
            name = item.get("name", "unknown")
            item_type = item.get("type", "")
            item_id = item.get("id", "")

            if item_type == "folder":
                sub_path = f"{path}/{name}" if path else name
                print(f"  {'  '*depth}[FOLDER] {sub_path}")
                files.extend(crawl_folder(item_id, sub_path, depth + 1))

            elif item_type == "version_stack":
                # Version stacks contain the actual files
                sub_path = f"{path}/{name}" if path else name
                print(f"  {'  '*depth}[VSTACK] {sub_path}")
                try:
                    vs_resp = fio(f"/version_stacks/{item_id}/children?page_size=5")
                    vs_items = vs_resp.get("data", [])
                    if vs_items:
                        # Latest version is first
                        latest = vs_items[0]
                        dur = latest.get("duration", 0) or 0  # seconds
                        fsize = latest.get("file_size", 0) or 0
                        view = item.get("view_url", "") or latest.get("view_url", "")
                        files.append({
                            "id": latest.get("id", item_id),
                            "name": name,
                            "path": sub_path,
                            "type": "version_stack",
                            "duration_sec": dur,
                            "file_size": fsize,
                            "media_type": latest.get("media_type", ""),
                            "view_url": view,
                        })
                except Exception as e:
                    print(f"  {'  '*depth}  ERROR on vstack {item_id}: {e}")
                    files.append({
                        "id": item_id,
                        "name": name,
                        "path": sub_path,
                        "type": "version_stack",
                        "duration_sec": 0,
                        "file_size": 0,
                        "media_type": "unknown",
                        "error": str(e),
                    })

            elif item_type == "file":
                dur = item.get("duration", 0) or 0
                fsize = item.get("file_size", 0) or 0
                mt = item.get("media_type", "")
                view = item.get("view_url", "")
                sub_path = f"{path}/{name}" if path else name
                # Only count video/audio files
                if mt.startswith("video/") or mt.startswith("audio/") or name.lower().endswith((".mp4", ".mov", ".mkv", ".wav", ".mp3")):
                    files.append({
                        "id": item_id,
                        "name": name,
                        "path": sub_path,
                        "type": "file",
                        "duration_sec": dur,
                        "file_size": fsize,
                        "media_type": mt,
                        "view_url": view,
                    })
                    print(f"  {'  '*depth}[FILE] {name} ({dur/60:.1f}min, {fsize/1e6:.0f}MB)")
                else:
                    print(f"  {'  '*depth}[SKIP] {name} ({mt})")

    return files


# === Main ===
print("=" * 60)
print("VURT Frame.io Inventory Crawl")
print("=" * 60)

# Get project root folder
print(f"\nGetting project {PROJECT}...")
proj = fio(f"/projects/{PROJECT}")
root_folder_id = proj["data"]["root_folder_id"]
print(f"Root folder: {root_folder_id}")

print(f"\nCrawling root folder...")
root = fio(f"/folders/{root_folder_id}/children?page_size=50")
root_items = root.get("data", [])

print(f"Found {len(root_items)} top-level items:\n")
for item in root_items:
    print(f"  {item.get('type', '?'):15s} {item.get('name', '?')}")

all_files = []
for item in root_items:
    if item.get("type") == "folder":
        folder_name = item.get("name", "unknown")
        folder_id = item.get("id", "")
        print(f"\n--- Crawling: {folder_name} ---")
        folder_files = crawl_folder(folder_id, folder_name)
        all_files.extend(folder_files)
        print(f"  -> {len(folder_files)} video files found")

# === Summary ===
print(f"\n{'=' * 60}")
print("INVENTORY SUMMARY")
print(f"{'=' * 60}")

total_files = len(all_files)
total_dur_sec = sum(f["duration_sec"] for f in all_files)
total_dur_min = total_dur_sec / 60
total_size_gb = sum(f["file_size"] for f in all_files) / 1e9

# Files with no duration (may need individual lookup)
no_dur = [f for f in all_files if f["duration_sec"] == 0]

print(f"Total video files: {total_files}")
print(f"Total duration: {total_dur_min:.0f} minutes ({total_dur_min/60:.1f} hours)")
print(f"Total size: {total_size_gb:.1f} GB")
print(f"Files with no duration data: {len(no_dur)}")

# Cost estimates
pro_rate = 0.00617  # universal-3-pro per minute
std_rate = 0.0025   # universal-2 per minute
print(f"\nCost estimates:")
print(f"  universal-3-pro: ${total_dur_min * pro_rate:.2f}")
print(f"  universal-2:     ${total_dur_min * std_rate:.2f}")

# Group by top-level folder
from collections import defaultdict
by_folder = defaultdict(list)
for f in all_files:
    top = f["path"].split("/")[0] if "/" in f["path"] else f["path"]
    by_folder[top].append(f)

print(f"\nBreakdown by folder:")
for folder, files in sorted(by_folder.items()):
    dur = sum(f["duration_sec"] for f in files) / 60
    print(f"  {folder}: {len(files)} files, {dur:.0f} min")

# Save inventory
inventory_path = os.path.join(OUT_DIR, "frameio-inventory.json")
os.makedirs(OUT_DIR, exist_ok=True)
with open(inventory_path, "w") as f:
    json.dump({
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "project_id": PROJECT,
        "total_files": total_files,
        "total_duration_min": round(total_dur_min, 1),
        "total_size_gb": round(total_size_gb, 2),
        "files_without_duration": len(no_dur),
        "cost_estimate_pro": round(total_dur_min * pro_rate, 2),
        "cost_estimate_std": round(total_dur_min * std_rate, 2),
        "files": all_files,
    }, f, indent=2)
print(f"\nInventory saved to {inventory_path}")

# Save CSV for easy viewing
csv_path = os.path.join(OUT_DIR, "frameio-inventory.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file_id", "name", "path", "type", "duration_min", "size_mb", "media_type"])
    for item in sorted(all_files, key=lambda x: x["path"]):
        w.writerow([
            item["id"],
            item["name"],
            item["path"],
            item["type"],
            round(item["duration_sec"] / 60, 1),
            round(item["file_size"] / 1e6, 0),
            item["media_type"],
        ])
print(f"CSV saved to {csv_path}")
