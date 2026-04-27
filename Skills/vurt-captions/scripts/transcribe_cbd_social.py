#!/usr/bin/env python3
"""Transcribe CBD social clips via AssemblyAI, write JSON + plain-text transcripts."""
import json
import os
import time
import urllib.request

AAI_KEY = os.environ["ASSEMBLYAI_API_KEY"]
AAI_BASE = "https://api.assemblyai.com/v2"
AAI_H = {"authorization": AAI_KEY, "content-type": "application/json"}

FOOTAGE_DIR = "/home/workspace/Skills/vurt-captions/footage/come-back-dad"
OUT_DIR = "/home/workspace/Skills/vurt-captions/footage/come-back-dad/transcripts"


def upload_local(path):
    with open(path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(
        f"{AAI_BASE}/upload",
        data=data,
        headers={"authorization": AAI_KEY, "content-type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["upload_url"]


def transcribe(audio_url):
    body = json.dumps({
        "audio_url": audio_url,
        "speech_models": ["universal-3-pro"],
        "speaker_labels": True,
    }).encode()
    req = urllib.request.Request(f"{AAI_BASE}/transcript", data=body, headers=AAI_H, method="POST")
    with urllib.request.urlopen(req) as r:
        tid = json.loads(r.read())["id"]
    while True:
        time.sleep(5)
        req = urllib.request.Request(f"{AAI_BASE}/transcript/{tid}", headers=AAI_H)
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        if resp["status"] == "completed":
            return resp
        if resp["status"] == "error":
            raise RuntimeError(resp.get("error", "unknown"))


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(FOOTAGE_DIR) if f.lower().endswith(".mp4"))
    for name in files:
        base = os.path.splitext(name)[0]
        out_json = os.path.join(OUT_DIR, f"{base}.json")
        out_txt = os.path.join(OUT_DIR, f"{base}.txt")
        if os.path.exists(out_json) and os.path.getsize(out_json) > 100:
            print(f"SKIP {name}")
            continue
        path = os.path.join(FOOTAGE_DIR, name)
        print(f"UP   {name}")
        audio_url = upload_local(path)
        print(f"TRN  {name}")
        resp = transcribe(audio_url)
        with open(out_json, "w") as f:
            json.dump({
                "text": resp.get("text", ""),
                "audio_duration": resp.get("audio_duration", 0),
                "utterances": resp.get("utterances", []),
            }, f, indent=2)
        with open(out_txt, "w") as f:
            f.write(resp.get("text", ""))
        print(f"DONE {name} ({resp.get('audio_duration', 0)}s)")


if __name__ == "__main__":
    run()
