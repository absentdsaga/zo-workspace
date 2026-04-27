#!/usr/bin/env python3
"""Download approved Come Back Dad social clips + OTR clips from Frame.io."""
import json
import os
import subprocess
import sys
import urllib.parse

sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import get_access_token, ACCT_ID, API_BASE  # noqa

OUT_DIR = "/home/workspace/Skills/vurt-captions/footage/come-back-dad"

CLIPS = [
    ("966ffd71-9fd4-4242-980a-fb3279acd280", "CBD_Social_01.mp4"),
    ("e9be066c-a4e7-4972-9c09-128bf1df6248", "CBD_Social_02.mp4"),
    ("8cca91fc-abc5-492b-9985-2523840cb0d9", "CBD_Social_03.mp4"),
    ("9baaaee8-84ff-4933-b040-649c881794c1", "CBD_Social_04.mp4"),
    ("2ca1673a-accb-4b41-8398-9bd4e4ae2b15", "CBD_Social_05.mp4"),
    ("ad9ed1ea-c236-4797-ad55-48f83bd1d47c", "CBD_OTR_Comeback-1.mp4"),
    ("f37eb0e5-945f-4fa0-bba6-9b684e2ef867", "CBD_OTR_ComeBack-2.mp4"),
]


def get_signed_url(file_id):
    token = get_access_token()
    url = f"{API_BASE}/accounts/{ACCT_ID}/files/{file_id}?include=media_links.original"
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}",
         "-H", "x-api-version: 2", url],
        capture_output=True, text=True, timeout=30,
    )
    data = json.loads(r.stdout)
    node = data.get("data") or {}
    media_links = node.get("media_links") or {}
    original = media_links.get("original") or {}
    # fallback: some responses put download_url on the asset itself
    return original.get("download_url") or node.get("download_url")


def download(file_id, filename):
    dest = os.path.join(OUT_DIR, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"SKIP {filename} (exists, {os.path.getsize(dest)/1e6:.1f}MB)")
        return
    url = get_signed_url(file_id)
    if not url:
        print(f"FAIL {filename} — no signed URL returned")
        return
    print(f"GET  {filename}")
    r = subprocess.run(
        ["curl", "-sL", "-o", dest, url],
        capture_output=True, text=True, timeout=600,
    )
    if r.returncode != 0:
        print(f"FAIL {filename} — curl rc={r.returncode}: {r.stderr[:200]}")
        return
    size = os.path.getsize(dest) if os.path.exists(dest) else 0
    print(f"DONE {filename} ({size/1e6:.1f}MB)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for fid, name in CLIPS:
        download(fid, name)
