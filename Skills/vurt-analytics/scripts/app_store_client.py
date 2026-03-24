#!/usr/bin/env python3
"""VURT App Store Data — fetches live ratings from iOS App Store and Google Play."""

import json, urllib.request, urllib.parse, re

SEARCH_TERM = "VURT"


def get_ios_data():
    """Fetch iOS App Store ratings via iTunes Search API (returns JSON, reliable)."""
    result = {"platform": "iOS", "rating": None, "rating_count": None, "error": None}
    try:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(SEARCH_TERM)}&entity=software&country=us&limit=10"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())

        for app in data.get("results", []):
            name = (app.get("trackName") or "").lower()
            if "vurt" in name:
                result["name"] = app.get("trackName")
                result["rating"] = app.get("averageUserRating")
                result["rating_count"] = app.get("userRatingCount")
                result["version"] = app.get("version")
                result["bundle_id"] = app.get("bundleId")
                return result

        result["error"] = f"App not found searching '{SEARCH_TERM}'"
    except Exception as e:
        result["error"] = str(e)
    return result


def get_android_data():
    """Fetch Google Play Store ratings by parsing embedded JSON data."""
    result = {"platform": "Android", "rating": None, "rating_count": 0, "error": None}
    try:
        # Go directly to the detail page (package ID known from prior search)
        package_id = "com.vurt.mobile"
        result["package_id"] = package_id

        detail_url = f"https://play.google.com/store/apps/details?id={package_id}&hl=en&gl=us"
        req = urllib.request.Request(detail_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        detail_html = resp.read().decode("utf-8", errors="replace")

        # Google Play embeds app data in AF_initDataCallback blocks as JSON
        # The ds:5 block contains app metadata including ratings
        m = re.search(
            r"AF_initDataCallback\(\{key: 'ds:5', hash: '\d+', data:(\[.*?\]), sideChannel:",
            detail_html, re.DOTALL
        )
        if m:
            data = json.loads(m.group(1))
            s = json.dumps(data)

            # Check if the app name is in this block (verification)
            if "VURT" in s or "vurt" in s:
                # Rating data lives in the nested structure
                # When rating exists: a float like 4.7 appears before the histogram
                # When no ratings: the rating structure is empty [[[[]]]]
                rating_floats = re.findall(r'(?<=[,\[])([1-5]\.\d)(?=[,\]])', s)

                if rating_floats:
                    result["rating"] = float(rating_floats[0])
                    # Try to find rating count nearby
                    count_matches = re.findall(r'(?<=[,\[])(\d{1,7})(?=[,\]])', s)
                    # Filter for plausible rating counts (not image dimensions, timestamps, etc.)
                    for c in count_matches:
                        c_int = int(c)
                        if 1 <= c_int <= 1000000 and c_int not in (272, 10, 35, 2, 1):
                            result["rating_count"] = c_int
                            break
                else:
                    # No rating float found — app has 0 ratings
                    result["rating"] = None
                    result["rating_count"] = 0
                    result["error"] = None  # Not an error — just no ratings yet
                return result

        # Fallback: try HTML patterns
        for pattern in [
            r'"ratingValue":\s*"?(\d\.?\d?)"?',
            r'(\d\.\d)\s*star',
        ]:
            m = re.search(pattern, detail_html, re.IGNORECASE)
            if m:
                result["rating"] = float(m.group(1))
                break

        if result["rating"] is None:
            result["rating_count"] = 0  # App exists but has no ratings

    except urllib.error.HTTPError as e:
        result["error"] = f"HTTP {e.code}" if e.code != 404 else "App not found on Google Play"
    except Exception as e:
        result["error"] = str(e)
    return result


def get_app_store_data():
    """Collect ratings from both app stores. Returns dict with 'ios' and 'android' keys."""
    return {
        "ios": get_ios_data(),
        "android": get_android_data()
    }


if __name__ == "__main__":
    data = get_app_store_data()
    print(json.dumps(data, indent=2))
