#!/usr/bin/env python3
"""Submit every clip in inventory.json to AssemblyAI via signed Frame.io URL.
Poll until all complete. Write transcripts to footage/<show>/transcripts/<id>.json."""
import json, os, re, sys, time, urllib.request, subprocess

sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import get_access_token, ACCT_ID, API_BASE

AAI_KEY = os.environ["ASSEMBLYAI_API_KEY"]
AAI_BASE = "https://api.assemblyai.com/v2"
AAI_H = {"authorization": AAI_KEY, "content-type": "application/json"}

INV = "/home/workspace/Skills/vurt-captions/footage/inventory.json"
FOOTAGE = "/home/workspace/Skills/vurt-captions/footage"
JOBS_FILE = "/home/workspace/Skills/vurt-captions/footage/aai_jobs.json"


def show_slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def signed_url(file_id):
    token = get_access_token()
    r = subprocess.run(
        ["curl","-s","-H",f"Authorization: Bearer {token}","-H","x-api-version: 2",
         f"{API_BASE}/accounts/{ACCT_ID}/files/{file_id}?include=media_links.original"],
        capture_output=True, text=True, timeout=30)
    node = (json.loads(r.stdout) or {}).get("data") or {}
    ml = node.get("media_links") or {}
    return (ml.get("original") or {}).get("download_url")


def submit(audio_url):
    body = json.dumps({"audio_url": audio_url, "speech_models":["universal-3-pro"], "speaker_labels": True}).encode()
    req = urllib.request.Request(f"{AAI_BASE}/transcript", data=body, headers=AAI_H, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["id"]


def status(tid):
    req = urllib.request.Request(f"{AAI_BASE}/transcript/{tid}", headers={"authorization": AAI_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    inv = json.load(open(INV))
    jobs = {}
    if os.path.exists(JOBS_FILE):
        jobs = json.load(open(JOBS_FILE))

    # Submit
    for show, meta in inv.items():
        slug = show_slug(show)
        tdir = f"{FOOTAGE}/{slug}/transcripts"
        os.makedirs(tdir, exist_ok=True)
        for clip in meta["clips"]:
            fid = clip.get("file_id") or clip.get("id")
            if not fid: continue
            key = f"{slug}/{fid}"
            # Already transcribed?
            target = f"{tdir}/{fid}.json"
            if os.path.exists(target) and os.path.getsize(target) > 100:
                continue
            if key in jobs and jobs[key].get("status") in ("queued","processing","completed"):
                continue
            url = signed_url(fid)
            if not url:
                print(f"NO URL {show}/{clip['name']}"); continue
            try:
                tid = submit(url)
                jobs[key] = {"tid": tid, "status": "queued", "show": show, "name": clip["name"], "fid": fid, "path": target}
                print(f"SUB  {show}/{clip['name']} → {tid}")
            except Exception as e:
                print(f"ERR  {show}/{clip['name']}: {e}")
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=2)

    # Poll
    print(f"\n--- Polling {sum(1 for j in jobs.values() if j['status'] != 'done')} jobs ---")
    while True:
        pending = [k for k,j in jobs.items() if j.get("status") != "done"]
        if not pending: break
        for k in list(pending):
            j = jobs[k]
            try:
                resp = status(j["tid"])
            except Exception as e:
                print(f"POLL ERR {k}: {e}"); continue
            st = resp.get("status")
            if st == "completed":
                out = {
                    "text": resp.get("text",""),
                    "audio_duration": resp.get("audio_duration",0),
                    "utterances": resp.get("utterances",[]) or [],
                }
                with open(j["path"],"w") as f:
                    json.dump(out, f, indent=2)
                with open(j["path"].replace(".json",".txt"),"w") as f:
                    f.write(out["text"])
                j["status"] = "done"
                print(f"DONE {j['show']}/{j['name']} ({out['audio_duration']}s)")
            elif st == "error":
                j["status"] = "error"; j["error"] = resp.get("error","")
                print(f"AAI ERR {k}: {resp.get('error','')}")
            else:
                j["status"] = st
        with open(JOBS_FILE,"w") as f:
            json.dump(jobs, f, indent=2)
        remaining = [k for k,j in jobs.items() if j.get("status") not in ("done","error")]
        if not remaining: break
        print(f"  ... {len(remaining)} remaining")
        time.sleep(15)

    done = sum(1 for j in jobs.values() if j["status"]=="done")
    err = sum(1 for j in jobs.values() if j["status"]=="error")
    print(f"\nFinal: {done} done, {err} errors")


if __name__ == "__main__":
    main()
