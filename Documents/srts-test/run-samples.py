import requests, os, json, time

token_id = os.environ.get('VURT_MUX_TOKEN_ID','')
token_secret = os.environ.get('VURT_MUX_TOKEN_SECRET','')
aai_key = os.environ.get('ASSEMBLYAI_API_KEY','')

resp = requests.get('https://api.mux.com/video/v1/assets?limit=100', auth=(token_id, token_secret))
data = resp.json()['data']
data.sort(key=lambda a: int(a.get('passthrough','0')))

indices = [0, 25, 50, 75, 99]
samples = [data[i] for i in indices]

print("Samples:")
for s in samples:
    print(f"  PT {s['passthrough']} — {s['duration']/60:.1f}min")

results = []
for s in samples:
    pt = s['passthrough']
    asset_id = s['id']
    dur = s['duration']
    print(f"\n--- PT {pt} ---")
    
    r = requests.post(
        f'https://api.mux.com/video/v1/assets/{asset_id}/playback-ids',
        auth=(token_id, token_secret),
        json={"policy": "public"}
    )
    if r.status_code not in (200, 201):
        print(f"  FAIL playback: {r.status_code}")
        results.append({"pt": pt, "status": "error", "error": "playback creation failed"})
        continue
    
    pub_pid = r.json()['data']['id']
    mp4_url = f"https://stream.mux.com/{pub_pid}/highest.mp4"
    stream_url = f"https://stream.mux.com/{pub_pid}.m3u8"
    
    tr = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        headers={"authorization": aai_key, "content-type": "application/json"},
        json={"audio_url": mp4_url, "speech_models": ["universal-3-pro"]}
    )
    if tr.status_code != 200:
        print(f"  FAIL AAI: {tr.status_code} {tr.text[:150]}")
        requests.delete(f'https://api.mux.com/video/v1/assets/{asset_id}/playback-ids/{pub_pid}', auth=(token_id, token_secret))
        results.append({"pt": pt, "status": "error", "error": f"AAI {tr.status_code}"})
        continue
    
    tid = tr.json()['id']
    print(f"  Transcribing... (tid: {tid[:15]})")
    
    status = "queued"
    while status not in ('completed', 'error'):
        time.sleep(4)
        pr = requests.get(f'https://api.assemblyai.com/v2/transcript/{tid}', headers={"authorization": aai_key})
        pj = pr.json()
        status = pj['status']
        if status == 'processing':
            print(f"  Processing...")
    
    if status == 'completed':
        sr = requests.get(f'https://api.assemblyai.com/v2/transcript/{tid}/srt', headers={"authorization": aai_key})
        outpath = f'/home/workspace/Documents/srts-test/{pt}.srt'
        with open(outpath, 'w') as f:
            f.write(sr.text)
        
        text_preview = pj.get('text','')[:200]
        print(f"  Done -> {outpath}")
        print(f"  Preview: {text_preview}...")
        results.append({
            "pt": pt, "status": "success", "srt_path": outpath,
            "duration_min": round(dur/60, 1),
            "stream_url": stream_url, "mp4_url": mp4_url,
            "public_playback_id": pub_pid, "asset_id": asset_id,
            "text_preview": text_preview,
        })
    else:
        print(f"  FAIL: {pj.get('error','unknown')}")
        results.append({"pt": pt, "status": "error", "error": pj.get('error','')})

print("\n" + "="*60)
ok = [r for r in results if r['status'] == 'success']
fail = [r for r in results if r['status'] == 'error']
print(f"Success: {len(ok)}/5 | Failed: {len(fail)}/5\n")

for r in ok:
    print(f"PT {r['pt']} ({r['duration_min']}min)")
    print(f"  SRT:   {r['srt_path']}")
    print(f"  Watch: {r['stream_url']}")
    print(f"  MP4:   {r['mp4_url']}")
    print()

with open('/home/workspace/Documents/srts-test/sample-batch-results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Done.")
