#!/usr/bin/env python3
"""VURT Mux → AssemblyAI Batch Subtitle Generator

For each Mux asset:
1. Create temporary public playback ID
2. Send audio URL to AssemblyAI for transcription
3. Poll until done, download SRT
4. Remove public playback ID (cleanup)
"""
import os, sys, json, time, argparse, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

MUX_TOKEN_ID = os.environ.get("VURT_MUX_TOKEN_ID", "")
MUX_TOKEN_SECRET = os.environ.get("VURT_MUX_TOKEN_SECRET", "")
ASSEMBLYAI_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "")
MUX_BASE = "https://api.mux.com/video/v1"
AAI_BASE = "https://api.assemblyai.com/v2"

def mux_get(path):
    r = requests.get(f"{MUX_BASE}/{path}", auth=(MUX_TOKEN_ID, MUX_TOKEN_SECRET))
    r.raise_for_status()
    return r.json()

def mux_post(path, data=None):
    r = requests.post(f"{MUX_BASE}/{path}", json=data or {}, auth=(MUX_TOKEN_ID, MUX_TOKEN_SECRET))
    r.raise_for_status()
    return r.json()

def mux_delete(path):
    r = requests.delete(f"{MUX_BASE}/{path}", auth=(MUX_TOKEN_ID, MUX_TOKEN_SECRET))
    r.raise_for_status()

def list_all_assets():
    assets = []
    cursor = None
    while True:
        url = "assets?limit=100"
        if cursor:
            url += f"&page={cursor}"
        try:
            d = mux_get(url)
        except Exception:
            break
        batch = d.get("data", [])
        if not batch:
            break
        assets.extend(batch)
        cursor = d.get("next_cursor")
        if not cursor:
            break
    return assets

def transcribe(audio_url):
    h = {"authorization": ASSEMBLYAI_KEY, "content-type": "application/json"}
    r = requests.post(f"{AAI_BASE}/transcript", json={"audio_url": audio_url, "speech_models": ["universal-2"]}, headers=h)
    if not r.ok:
        raise Exception(f"Transcript request failed ({r.status_code}): {r.text}")

    tid = r.json()["id"]
    while True:
        r = requests.get(f"{AAI_BASE}/transcript/{tid}", headers=h)
        d = r.json()
        if d["status"] == "completed":
            return tid, d
        if d["status"] == "error":
            raise Exception(f"Transcription error: {d.get('error')}")
        time.sleep(3)

def get_srt(transcript_id):
    h = {"authorization": ASSEMBLYAI_KEY}
    r = requests.get(f"{AAI_BASE}/transcript/{transcript_id}/srt", headers=h)
    r.raise_for_status()
    return r.text

CONFIDENCE_THRESHOLD = 0.6
MIN_CLUSTER_WORDS = 3

def flag_low_confidence(transcript, name):
    words = transcript.get("words", [])
    if not words:
        return []
    flags = []
    cluster = []
    for w in words:
        if w.get("confidence", 1.0) < CONFIDENCE_THRESHOLD:
            cluster.append(w)
        else:
            if len(cluster) >= MIN_CLUSTER_WORDS:
                flags.append({
                    "name": name,
                    "start": format_ts(cluster[0]["start"]),
                    "end": format_ts(cluster[-1]["end"]),
                    "start_ms": cluster[0]["start"],
                    "end_ms": cluster[-1]["end"],
                    "avg_confidence": round(sum(c["confidence"] for c in cluster) / len(cluster), 3),
                    "word_count": len(cluster),
                    "text": " ".join(c["text"] for c in cluster),
                })
            cluster = []
    if len(cluster) >= MIN_CLUSTER_WORDS:
        flags.append({
            "name": name,
            "start": format_ts(cluster[0]["start"]),
            "end": format_ts(cluster[-1]["end"]),
            "start_ms": cluster[0]["start"],
            "end_ms": cluster[-1]["end"],
            "avg_confidence": round(sum(c["confidence"] for c in cluster) / len(cluster), 3),
            "word_count": len(cluster),
            "text": " ".join(c["text"] for c in cluster),
        })
    return flags

def format_ts(ms):
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def process_asset(asset, index, total, output_dir):
    aid = asset["id"]
    passthrough = asset.get("passthrough", "")
    dur_min = round(asset.get("duration", 0) / 60, 1)
    tag = f"[{index+1}/{total}]"
    name = passthrough or aid[:16]
    public_pid = None

    try:
        has_audio = any(t.get("type") == "audio" for t in asset.get("tracks", []))
        if not has_audio:
            print(f"{tag} SKIP (no audio): {name}")
            return {"name": name, "status": "skipped", "reason": "no audio"}

        print(f"{tag} {name} ({dur_min}min) — creating public URL...")
        resp = mux_post(f"assets/{aid}/playback-ids", {"policy": "public"})
        public_pid = resp["data"]["id"]
        audio_url = f"https://stream.mux.com/{public_pid}/highest.mp4"

        print(f"{tag} {name} — transcribing...")
        tid, transcript = transcribe(audio_url)

        print(f"{tag} {name} — fetching SRT...")
        srt = get_srt(tid)

        srt_path = output_dir / f"{name}.srt"
        srt_path.write_text(srt, encoding="utf-8")

        flags = flag_low_confidence(transcript, name)
        if flags:
            print(f"{tag} {name} — {len(flags)} segment(s) flagged for review")

        audio_dur = transcript.get("audio_duration", 0)
        print(f"{tag} {name} — done ({round(audio_dur/60,1)}min audio) → {srt_path}")

        return {"name": name, "status": "success", "srt_path": str(srt_path),
                "audio_duration": audio_dur, "asset_id": aid, "flags": flags}

    except Exception as e:
        print(f"{tag} {name} — FAILED: {e}")
        return {"name": name, "status": "error", "error": str(e), "asset_id": aid}

    finally:
        if public_pid:
            try:
                mux_delete(f"assets/{aid}/playback-ids/{public_pid}")
                print(f"{tag} {name} — cleaned up public playback ID")
            except:
                print(f"{tag} {name} — WARNING: failed to remove public playback ID {public_pid}")

def main():
    parser = argparse.ArgumentParser(description="VURT Mux → AssemblyAI Batch SRT")
    parser.add_argument("-o", "--output", default="./srts", help="Output directory")
    parser.add_argument("-n", "--limit", type=int, default=0, help="Max assets to process (0=all)")
    parser.add_argument("-c", "--concurrency", type=int, default=3, help="Parallel jobs")
    parser.add_argument("--dry-run", action="store_true", help="List assets without processing")
    args = parser.parse_args()

    if not all([MUX_TOKEN_ID, MUX_TOKEN_SECRET, ASSEMBLYAI_KEY]):
        print("ERROR: Set VURT_MUX_TOKEN_ID, VURT_MUX_TOKEN_SECRET, ASSEMBLYAI_API_KEY")
        sys.exit(1)

    print("VURT Batch Subtitle Generator (Mux → AssemblyAI)\n")
    print("Fetching asset list...")
    assets = list_all_assets()
    audio_assets = [a for a in assets if any(t.get("type") == "audio" for t in a.get("tracks", []))]
    print(f"Found {len(assets)} total assets, {len(audio_assets)} with audio\n")

    if args.limit:
        audio_assets = audio_assets[:args.limit]

    if args.dry_run:
        for i, a in enumerate(audio_assets):
            name = a.get("passthrough", "") or a["id"][:16]
            dur = round(a.get("duration", 0) / 60, 1)
            print(f"  {i+1}. {name} — {dur}min")
        print(f"\n{len(audio_assets)} assets would be processed.")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(process_asset, a, i, len(audio_assets), output_dir): a
            for i, a in enumerate(audio_assets)
        }
        for f in as_completed(futures):
            results.append(f.result())

    elapsed = round((time.time() - start) / 60, 1)
    succeeded = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    total_audio = sum(r.get("audio_duration", 0) for r in succeeded) / 60
    cost = total_audio * 0.0025

    all_flags = []
    for r in succeeded:
        all_flags.extend(r.get("flags", []))

    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Processed:  {len(audio_assets)}")
    print(f"Succeeded:  {len(succeeded)}")
    print(f"Failed:     {len(failed)}")
    print(f"Audio:      {total_audio:.1f} minutes")
    print(f"Est. cost:  ${cost:.2f}")
    print(f"Wall time:  {elapsed} minutes")
    print(f"Flagged:    {len(all_flags)} segment(s) across {len(set(f['name'] for f in all_flags))} file(s)")

    if failed:
        print(f"\nFailed:")
        for f in failed:
            print(f"  - {f['name']}: {f['error']}")

    if all_flags:
        print(f"\nSegments needing review:")
        for f in sorted(all_flags, key=lambda x: x["avg_confidence"]):
            print(f"  - {f['name']} [{f['start']}–{f['end']}] conf={f['avg_confidence']} \"{f['text'][:60]}...\"" if len(f['text']) > 60 else f"  - {f['name']} [{f['start']}–{f['end']}] conf={f['avg_confidence']} \"{f['text']}\"")

    report = output_dir / "subtitle-report.json"
    report.write_text(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
        "summary": {"total": len(audio_assets), "succeeded": len(succeeded),
                     "failed": len(failed), "audio_minutes": round(total_audio, 1),
                     "estimated_cost": round(cost, 2)}
    }, indent=2))
    print(f"\nReport: {report}")

    if all_flags:
        flags_path = output_dir / "review-flags.json"
        flags_path.write_text(json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "threshold": CONFIDENCE_THRESHOLD,
            "min_cluster_words": MIN_CLUSTER_WORDS,
            "total_flags": len(all_flags),
            "flagged_files": len(set(f["name"] for f in all_flags)),
            "flags": sorted(all_flags, key=lambda x: x["avg_confidence"])
        }, indent=2))
        print(f"Review flags: {flags_path}")

if __name__ == "__main__":
    main()
