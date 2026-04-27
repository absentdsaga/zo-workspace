#!/usr/bin/env python3
"""Retry Swahili LNJ clips with universal-2 fallback."""
import json, os, sys, time, urllib.request, subprocess

sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import get_access_token, ACCT_ID, API_BASE

AAI_KEY = os.environ["ASSEMBLYAI_API_KEY"]
AAI_BASE = "https://api.assemblyai.com/v2"
AAI_H = {"authorization": AAI_KEY, "content-type": "application/json"}

JOBS_FILE = "/home/workspace/Skills/vurt-captions/footage/aai_jobs.json"


def signed_url(file_id):
    token = get_access_token()
    r = subprocess.run(
        ["curl","-s","-H",f"Authorization: Bearer {token}","-H","x-api-version: 2",
         f"{API_BASE}/accounts/{ACCT_ID}/files/{file_id}?include=media_links.original"],
        capture_output=True, text=True, timeout=30)
    node = (json.loads(r.stdout) or {}).get("data") or {}
    return ((node.get("media_links") or {}).get("original") or {}).get("download_url")


def main():
    jobs = json.load(open(JOBS_FILE))
    retry = [(k, j) for k,j in jobs.items() if j.get("status")=="error"]
    print(f"Retrying {len(retry)} errored jobs with universal-2 fallback")
    for k, j in retry:
        url = signed_url(j["fid"])
        body = json.dumps({"audio_url": url, "speech_models":["universal-3-pro","universal-2"], "speaker_labels": True}).encode()
        req = urllib.request.Request(f"{AAI_BASE}/transcript", data=body, headers=AAI_H, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            tid = json.loads(r.read())["id"]
        jobs[k]["tid"] = tid; jobs[k]["status"] = "queued"
        print(f"SUB {j['name']} → {tid}")

    # Poll
    while True:
        pending = [k for k,j in jobs.items() if j.get("status") in ("queued","processing")]
        if not pending: break
        for k in list(pending):
            req = urllib.request.Request(f"{AAI_BASE}/transcript/{jobs[k]['tid']}", headers={"authorization": AAI_KEY})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())
            if resp["status"]=="completed":
                out = {
                    "text": resp.get("text",""),
                    "audio_duration": resp.get("audio_duration",0),
                    "utterances": resp.get("utterances",[]) or [],
                }
                with open(jobs[k]["path"], "w") as f: json.dump(out, f, indent=2)
                with open(jobs[k]["path"].replace(".json",".txt"), "w") as f: f.write(out["text"])
                jobs[k]["status"]="done"
                print(f"DONE {jobs[k]['name']}")
            elif resp["status"]=="error":
                jobs[k]["status"]="error"; jobs[k]["error"]=resp.get("error","")
                print(f"ERR {jobs[k]['name']}: {resp.get('error','')}")
            else:
                jobs[k]["status"]=resp["status"]
        with open(JOBS_FILE,"w") as f: json.dump(jobs, f, indent=2)
        if [k for k,j in jobs.items() if j.get("status") in ("queued","processing")]:
            time.sleep(10)


if __name__ == "__main__":
    main()
