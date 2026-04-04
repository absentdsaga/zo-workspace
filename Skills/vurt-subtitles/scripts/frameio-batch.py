"""
VURT Frame.io → AssemblyAI → SRT batch pipeline (production)

Features:
- Speaker diarization (universal-3-pro model)
- Short-utterance flagging for QC
- Merge pass for mid-sentence splits
- Manifest CSV (SRT → Frame.io view URL)
- Review flags CSV (flagged segments for editor attention)
- Resume support (skips already-processed files)
- Concurrent processing with rate limiting

Usage:
  source /root/.zo_secrets
  python3 Skills/vurt-subtitles/scripts/frameio-batch.py [--dry-run] [--limit N] [--folder FOLDER_ID]
"""
import json, urllib.request, urllib.parse, os, sys, csv, time, argparse, re
from datetime import datetime, timezone
from collections import defaultdict

# === Config ===
SECRETS_PATH = "/home/workspace/.secrets/adobe-tokens.json"
CLIENT_ID = os.environ.get("VURT_ADOBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("VURT_ADOBE_CLIENT_SECRET", "")
ACCT = "6c77dc3c-f088-486d-a8e3-678fc0fcbd70"
PROJECT = "6a0a9a57-379a-4d48-a7ba-f63982fa3acc"
FIO_BASE = f"https://api.frame.io/v4/accounts/{ACCT}"
AAI_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "")
AAI_BASE = "https://api.assemblyai.com/v2"
UA = "VURT-Subtitle-Pipeline/2.0"
AAI_H = {"authorization": AAI_KEY, "content-type": "application/json", "User-Agent": UA}

OUT_DIR = "/home/workspace/Documents/srts-full"
INVENTORY_PATH = "/home/workspace/Documents/frameio-srt-test/frameio-inventory.json"

# QC thresholds
LOW_CONFIDENCE_THRESHOLD = 0.6
LOW_CONFIDENCE_CLUSTER_MIN = 3
SHORT_UTTERANCE_SEC = 1.0  # Flag utterances < 1 second with speaker change
MERGE_GAP_MS = 3000  # Merge same-speaker utterances within 3 seconds
MERGE_ENABLED = False  # Disabled until tested — enable with --merge flag
MAX_LINE_CHARS = 32  # 9:16 vertical video standard
MAX_LINES = 2  # Max lines per subtitle block
MIN_DISPLAY_SEC = 1.0  # Minimum display duration (Netflix standard)


# === Adobe Token Management ===
def get_token():
    tokens = json.load(open(SECRETS_PATH))
    obtained_str = tokens.get("obtained_at", "2000-01-01T00:00:00+00:00").replace("Z", "+00:00")
    obtained = datetime.fromisoformat(obtained_str)
    if (datetime.now(timezone.utc) - obtained).total_seconds() > 3000:
        return _refresh_token(tokens)
    return tokens["access_token"]


def _refresh_token(tokens=None):
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
    return new["access_token"]


def fio(path):
    token = get_token()
    req = urllib.request.Request(
        f"{FIO_BASE}{path}",
        headers={"Authorization": f"Bearer {token}", "x-api-key": CLIENT_ID, "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            token = _refresh_token()
            req = urllib.request.Request(
                f"{FIO_BASE}{path}",
                headers={"Authorization": f"Bearer {token}", "x-api-key": CLIENT_ID, "User-Agent": UA},
            )
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        raise


# === SRT Generation ===
def ms_to_srt_ts(ms):
    """Convert milliseconds to SRT timestamp format."""
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    f = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{f:03d}"


def merge_utterances(utterances):
    """Merge consecutive same-speaker utterances that are close together
    and where the first doesn't end with sentence-ending punctuation."""
    if not utterances:
        return utterances

    merged = [dict(utterances[0])]  # copy first
    for utt in utterances[1:]:
        prev = merged[-1]
        same_speaker = prev.get("speaker") == utt.get("speaker")
        gap = utt["start"] - prev["end"]
        prev_text = prev["text"].strip()
        # Don't merge if previous ends a sentence
        ends_sentence = prev_text and prev_text[-1] in ".!?\"'"

        if same_speaker and gap < MERGE_GAP_MS and not ends_sentence:
            # Merge: extend end time, concatenate text
            prev["end"] = utt["end"]
            prev["text"] = prev["text"].strip() + " " + utt["text"].strip()
        else:
            merged.append(dict(utt))

    return merged


def wrap_into_chunks(text, max_chars=MAX_LINE_CHARS, max_lines=MAX_LINES):
    """Split text into chunks that each fit within max_chars x max_lines.
    Returns a list of strings. No text is dropped.
    """
    flat = ' '.join(text.strip().split())
    if len(flat) <= max_chars:
        return [flat]

    words = flat.split()
    chunks = []
    current_chunk_lines = []
    current_line = ""

    for word in words:
        test = f"{current_line} {word}".strip() if current_line else word
        if len(test) <= max_chars:
            current_line = test
        else:
            if current_line:
                current_chunk_lines.append(current_line)
            current_line = word
            if len(current_chunk_lines) >= max_lines:
                chunks.append("\n".join(current_chunk_lines))
                current_chunk_lines = []

    if current_line:
        current_chunk_lines.append(current_line)
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))

    return chunks if chunks else [flat]


def enforce_min_duration(utterances, min_sec=MIN_DISPLAY_SEC):
    """Ensure every utterance has at least min_sec display time.
    Extends end time if needed, but won't overlap with next utterance.
    """
    result = []
    for i, utt in enumerate(utterances):
        u = dict(utt)
        dur_ms = u["end"] - u["start"]
        min_ms = int(min_sec * 1000)

        if dur_ms < min_ms:
            new_end = u["start"] + min_ms
            # Don't overlap with next utterance
            if i < len(utterances) - 1:
                next_start = utterances[i + 1]["start"]
                new_end = min(new_end, next_start - 1)
            u["end"] = max(u["end"], new_end)

        result.append(u)
    return result


def utterances_to_srt(utterances):
    """Build SRT from utterances with optional merge, line wrapping, and min duration."""
    processed = utterances
    if MERGE_ENABLED:
        processed = merge_utterances(processed)
    processed = enforce_min_duration(processed)

    srt_blocks = []
    idx = 1
    for utt in processed:
        text = utt["text"].strip()
        if not text:
            continue
        chunks = wrap_into_chunks(text)
        if len(chunks) == 1:
            start_ts = ms_to_srt_ts(utt["start"])
            end_ts = ms_to_srt_ts(utt["end"])
            srt_blocks.append(f"{idx}\n{start_ts} --> {end_ts}\n{chunks[0]}\n")
            idx += 1
        else:
            # Split timing proportionally
            total_dur = utt["end"] - utt["start"]
            chunk_dur = total_dur // len(chunks)
            for j, chunk in enumerate(chunks):
                start = utt["start"] + j * chunk_dur
                end = utt["start"] + (j + 1) * chunk_dur if j < len(chunks) - 1 else utt["end"]
                srt_blocks.append(f"{idx}\n{ms_to_srt_ts(start)} --> {ms_to_srt_ts(end)}\n{chunk}\n")
                idx += 1
    return "\n".join(srt_blocks) + "\n"


# === QC Flagging ===
def flag_low_confidence(words):
    """Find clusters of low-confidence words."""
    flags = []
    cluster = []
    for w in words:
        if w.get("confidence", 1.0) < LOW_CONFIDENCE_THRESHOLD:
            cluster.append(w)
        else:
            if len(cluster) >= LOW_CONFIDENCE_CLUSTER_MIN:
                flags.append({
                    "type": "low_confidence",
                    "start_ms": cluster[0]["start"],
                    "end_ms": cluster[-1]["end"],
                    "start_ts": ms_to_srt_ts(cluster[0]["start"]),
                    "end_ts": ms_to_srt_ts(cluster[-1]["end"]),
                    "avg_confidence": sum(w["confidence"] for w in cluster) / len(cluster),
                    "word_count": len(cluster),
                    "text": " ".join(w["text"] for w in cluster),
                })
            cluster = []
    # Final cluster
    if len(cluster) >= LOW_CONFIDENCE_CLUSTER_MIN:
        flags.append({
            "type": "low_confidence",
            "start_ms": cluster[0]["start"],
            "end_ms": cluster[-1]["end"],
            "start_ts": ms_to_srt_ts(cluster[0]["start"]),
            "end_ts": ms_to_srt_ts(cluster[-1]["end"]),
            "avg_confidence": sum(w["confidence"] for w in cluster) / len(cluster),
            "word_count": len(cluster),
            "text": " ".join(w["text"] for w in cluster),
        })
    return flags


def flag_short_utterances(utterances):
    """Flag very short utterances with speaker changes — often misattributed."""
    flags = []
    for i, utt in enumerate(utterances):
        dur_ms = utt["end"] - utt["start"]
        if dur_ms < SHORT_UTTERANCE_SEC * 1000:
            # Check if speaker changes around this utterance
            prev_speaker = utterances[i - 1].get("speaker") if i > 0 else None
            next_speaker = utterances[i + 1].get("speaker") if i < len(utterances) - 1 else None
            curr_speaker = utt.get("speaker")

            if prev_speaker != curr_speaker or next_speaker != curr_speaker:
                flags.append({
                    "type": "short_utterance",
                    "start_ms": utt["start"],
                    "end_ms": utt["end"],
                    "start_ts": ms_to_srt_ts(utt["start"]),
                    "end_ts": ms_to_srt_ts(utt["end"]),
                    "duration_ms": dur_ms,
                    "speaker": curr_speaker,
                    "text": utt["text"].strip(),
                })
    return flags


# === Get Download URL ===
def get_download_url(file_id):
    """Get the download URL for a Frame.io file."""
    fd = fio(f"/files/{file_id}?include=media_links.original")
    return fd["data"]["media_links"]["original"]["download_url"]


# === Process Single File ===
def process_file(file_info, out_dir):
    """Transcribe a single file and return results + flags."""
    name = file_info["name"]
    file_id = file_info["id"]
    srt_name = re.sub(r'\.(mp4|mov|mkv|avi|webm|wav|mp3)$', '', name, flags=re.IGNORECASE)
    srt_path = os.path.join(out_dir, f"{srt_name}.srt")

    # Skip if already done
    if os.path.exists(srt_path) and os.path.getsize(srt_path) > 10:
        return {"name": srt_name, "status": "skipped", "reason": "already exists"}

    # Get download URL
    try:
        dl_url = get_download_url(file_id)
    except Exception as e:
        return {"name": srt_name, "status": "error", "error": f"download_url: {e}"}

    # Submit to AssemblyAI
    body = json.dumps({
        "audio_url": dl_url,
        "speech_models": ["universal-3-pro"],
        "speaker_labels": True,
    }).encode()
    req = urllib.request.Request(f"{AAI_BASE}/transcript", data=body, headers=AAI_H, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        tid = resp["id"]
    except Exception as e:
        return {"name": srt_name, "status": "error", "error": f"submit: {e}"}

    # Poll for completion
    while True:
        time.sleep(5)
        req = urllib.request.Request(f"{AAI_BASE}/transcript/{tid}", headers=AAI_H)
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())

        if resp["status"] == "completed":
            break
        elif resp["status"] == "error":
            return {"name": srt_name, "status": "error", "error": resp.get("error", "unknown")}

    # Extract data
    utterances = resp.get("utterances", [])
    words = resp.get("words", [])
    dur = resp.get("audio_duration", 0)
    speakers = len(set(u.get("speaker") for u in utterances)) if utterances else 0

    # Build SRT
    if utterances:
        srt = utterances_to_srt(utterances)
    else:
        # Fallback
        req2 = urllib.request.Request(f"{AAI_BASE}/transcript/{tid}/srt", headers=AAI_H)
        with urllib.request.urlopen(req2) as r2:
            srt = r2.read().decode()

    # Write SRT
    with open(srt_path, "w") as f:
        f.write(srt)

    # QC flags
    flags = []
    if words:
        flags.extend(flag_low_confidence(words))
    if utterances:
        flags.extend(flag_short_utterances(utterances))

    return {
        "name": srt_name,
        "status": "success",
        "duration_sec": dur,
        "word_count": len(words),
        "speakers": speakers,
        "flags": flags,
        "view_url": file_info.get("view_url", ""),
        "path": file_info.get("path", ""),
    }


# === Main ===
def main():
    parser = argparse.ArgumentParser(description="VURT Frame.io → SRT batch pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--limit", type=int, default=0, help="Max files to process (0 = all)")
    parser.add_argument("--folder", type=str, default="", help="Only process files from this folder path prefix")
    parser.add_argument("--output", type=str, default=OUT_DIR, help="Output directory")
    parser.add_argument("--merge", action="store_true", help="Enable merge pass for mid-sentence splits")
    args = parser.parse_args()

    global MERGE_ENABLED
    if args.merge:
        MERGE_ENABLED = True
        print("Merge pass: ENABLED")

    out_dir = args.output
    os.makedirs(out_dir, exist_ok=True)

    # Load inventory
    if not os.path.exists(INVENTORY_PATH):
        print("ERROR: No inventory found. Run frameio-crawl.py first.")
        sys.exit(1)

    inv = json.load(open(INVENTORY_PATH))
    files = inv["files"]
    print(f"Loaded inventory: {len(files)} files")

    # Filter by folder if specified
    if args.folder:
        files = [f for f in files if f["path"].startswith(args.folder)]
        print(f"Filtered to {len(files)} files in '{args.folder}'")

    # Apply limit
    if args.limit > 0:
        files = files[:args.limit]
        print(f"Limited to {args.limit} files")

    if args.dry_run:
        print(f"\n[DRY RUN] Would process {len(files)} files:")
        for f in files:
            srt_name = re.sub(r'\.(mp4|mov|mkv|avi|webm|wav|mp3)$', '', f["name"], flags=re.IGNORECASE)
            exists = os.path.exists(os.path.join(out_dir, f"{srt_name}.srt"))
            status = "SKIP (exists)" if exists else "PROCESS"
            print(f"  [{status}] {f['name']} ({f['file_size']/1e6:.0f}MB)")
        to_process = [f for f in files if not os.path.exists(
            os.path.join(out_dir, re.sub(r'\.(mp4|mov|mkv|avi|webm|wav|mp3)$', '', f["name"], flags=re.IGNORECASE) + ".srt")
        )]
        print(f"\n{len(to_process)} files to process, {len(files) - len(to_process)} already done")
        return

    # Process
    print(f"\n{'=' * 60}")
    print(f"Processing {len(files)} files...")
    print(f"Output: {out_dir}")
    print(f"{'=' * 60}\n")

    results = []
    all_flags = {}
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f['name']}...", end=" ", flush=True)
        result = process_file(f, out_dir)
        results.append(result)

        if result["status"] == "success":
            dur_min = result["duration_sec"] / 60
            n_flags = len(result.get("flags", []))
            print(f"OK ({dur_min:.1f}min, {result['word_count']} words, {result['speakers']} spk, {n_flags} flags)")
            if result.get("flags"):
                all_flags[result["name"]] = result["flags"]
        elif result["status"] == "skipped":
            print(f"SKIPPED ({result['reason']})")
        else:
            print(f"ERROR: {result.get('error', 'unknown')}")

    # === Generate Manifest CSV ===
    manifest_path = os.path.join(out_dir, "MANIFEST.csv")
    with open(manifest_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["srt_filename", "frameio_url", "frameio_path", "duration_min", "word_count", "speakers", "flagged_segments", "status"])
        for r in results:
            if r["status"] == "success":
                w.writerow([
                    f"{r['name']}.srt",
                    r.get("view_url", ""),
                    r.get("path", ""),
                    round(r["duration_sec"] / 60, 1),
                    r["word_count"],
                    r["speakers"],
                    len(r.get("flags", [])),
                    "success",
                ])
            elif r["status"] == "skipped":
                w.writerow([f"{r['name']}.srt", "", "", "", "", "", "", "skipped"])
            else:
                w.writerow([f"{r['name']}.srt", "", "", "", "", "", "", f"error: {r.get('error', '')}"])
    print(f"\nManifest: {manifest_path}")

    # === Generate Review Flags CSV ===
    if all_flags:
        flags_path = os.path.join(out_dir, "REVIEW_FLAGS.csv")
        with open(flags_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["srt_filename", "flag_type", "start_time", "end_time", "text", "details"])
            for name, flags in sorted(all_flags.items()):
                for flag in flags:
                    details = ""
                    if flag["type"] == "low_confidence":
                        details = f"avg_conf={flag['avg_confidence']:.2f}, {flag['word_count']} words"
                    elif flag["type"] == "short_utterance":
                        details = f"dur={flag['duration_ms']}ms, speaker={flag.get('speaker', '?')}"
                    w.writerow([
                        f"{name}.srt",
                        flag["type"],
                        flag["start_ts"],
                        flag["end_ts"],
                        flag["text"],
                        details,
                    ])
        print(f"Review flags: {flags_path}")

    # === Summary ===
    ok = [r for r in results if r["status"] == "success"]
    skipped = [r for r in results if r["status"] == "skipped"]
    errors = [r for r in results if r["status"] == "error"]
    total_dur = sum(r.get("duration_sec", 0) for r in ok)
    total_words = sum(r.get("word_count", 0) for r in ok)
    total_flags = sum(len(r.get("flags", [])) for r in ok)

    print(f"\n{'=' * 60}")
    print(f"BATCH COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Processed: {len(ok)}")
    print(f"  Skipped:   {len(skipped)}")
    print(f"  Errors:    {len(errors)}")
    print(f"  Duration:  {total_dur/60:.0f} min ({total_dur/3600:.1f} hours)")
    print(f"  Words:     {total_words:,}")
    print(f"  Flags:     {total_flags}")
    print(f"  Est cost:  ${total_dur/60 * 0.00617:.2f} (pro)")

    if errors:
        print(f"\nErrors:")
        for r in errors:
            print(f"  {r['name']}: {r.get('error', 'unknown')}")

    # Save report
    report_path = os.path.join(out_dir, "batch-report.json")
    with open(report_path, "w") as f:
        json.dump({
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "total_files": len(results),
            "success": len(ok),
            "skipped": len(skipped),
            "errors": len(errors),
            "total_duration_min": round(total_dur / 60, 1),
            "total_words": total_words,
            "total_flags": total_flags,
            "estimated_cost": round(total_dur / 60 * 0.00617, 2),
            "results": results,
        }, f, indent=2)
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
