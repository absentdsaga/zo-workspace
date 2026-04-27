#!/usr/bin/env python3
"""Transcribe CBD EP29 and find the 'waiting for Spence' / Tatyana Ali scene."""
import json, os, sys, time, urllib.request

AAI_KEY = os.environ["ASSEMBLYAI_API_KEY"]
AAI_BASE = "https://api.assemblyai.com/v2"

FILE = "/home/workspace/Skills/vurt-captions/footage/come-back-dad/CBD_EP29_TatyanaAli.mp4"
OUT_JSON = "/home/workspace/Skills/vurt-captions/footage/come-back-dad/transcripts/CBD_EP29_TatyanaAli.json"
OUT_TXT = OUT_JSON.replace(".json", ".txt")


def upload(path):
    with open(path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(
        f"{AAI_BASE}/upload", data=data,
        headers={"authorization": AAI_KEY, "content-type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["upload_url"]


def transcribe(url):
    body = json.dumps({
        "audio_url": url,
        "speech_models": ["universal-3-pro"],
        "speaker_labels": True,
    }).encode()
    req = urllib.request.Request(
        f"{AAI_BASE}/transcript", data=body,
        headers={"authorization": AAI_KEY, "content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        tid = json.loads(r.read())["id"]
    while True:
        time.sleep(10)
        req = urllib.request.Request(f"{AAI_BASE}/transcript/{tid}", headers={"authorization": AAI_KEY})
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        if resp["status"] == "completed": return resp
        if resp["status"] == "error": raise RuntimeError(resp.get("error"))


if __name__ == "__main__":
    if os.path.exists(OUT_JSON) and os.path.getsize(OUT_JSON) > 1000:
        print("already transcribed")
        sys.exit(0)
    print("UP")
    url = upload(FILE)
    print("TRN")
    resp = transcribe(url)
    with open(OUT_JSON, "w") as f:
        json.dump({
            "text": resp.get("text", ""),
            "audio_duration": resp.get("audio_duration", 0),
            "utterances": resp.get("utterances", []),
        }, f, indent=2)
    with open(OUT_TXT, "w") as f:
        f.write(resp.get("text", ""))
    print(f"DONE dur={resp.get('audio_duration')}s utterances={len(resp.get('utterances',[]))}")
