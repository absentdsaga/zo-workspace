#!/usr/bin/env python3
"""TikTok transcript extractor — two-phase approach:
Phase 1: Extract existing auto-captions via yt-dlp (free, fast)
Phase 2: Download audio + transcribe with faster-whisper for uncaptioned videos

Usage:
  python3 transcribe_tiktok.py <tiktok_url>              # Single video
  python3 transcribe_tiktok.py --batch <urls_file>        # Batch from file
  python3 transcribe_tiktok.py --from-scan                # Process latest scan data
  python3 transcribe_tiktok.py --from-scan --top 20       # Top 20 by engagement
"""

import subprocess
import json
import os
import sys
import glob
import tempfile
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data"
TRANSCRIPT_DIR = "/home/workspace/Skills/sentiment-scanner/data/transcripts"
WHISPER_MODEL = "base"

def extract_captions_ytdlp(url: str, work_dir: str) -> str | None:
    """Phase 1: Try to get existing TikTok auto-captions via yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--write-subs", "--sub-format", "vtt", "--skip-download",
             "-o", os.path.join(work_dir, "%(id)s"), url],
            capture_output=True, text=True, timeout=30
        )
        vtt_files = glob.glob(os.path.join(work_dir, "*.vtt"))
        if vtt_files:
            import webvtt
            captions = webvtt.read(vtt_files[0])
            text = " ".join(c.text.strip() for c in captions if c.text.strip())
            for f in vtt_files:
                os.remove(f)
            return text if text else None
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        print(f"  Caption extraction failed: {e}")
    return None


def transcribe_with_whisper(url: str, work_dir: str) -> str | None:
    """Phase 2: Download audio and transcribe with faster-whisper."""
    audio_path = os.path.join(work_dir, "audio")
    try:
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3",
             "-o", audio_path + ".%(ext)s", url],
            capture_output=True, text=True, timeout=60
        )
        mp3_files = glob.glob(audio_path + ".*")
        if not mp3_files:
            return None

        audio_file = mp3_files[0]
        from faster_whisper import WhisperModel
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_file, beam_size=5)
        text = " ".join(s.text.strip() for s in segments)

        for f in mp3_files:
            os.remove(f)
        return text if text else None
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        print(f"  Whisper transcription failed: {e}")
    return None


def extract_video_id(url: str) -> str:
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)
    return url.split("/")[-1].split("?")[0]


def transcribe_video(url: str) -> dict:
    """Full two-phase transcription for a single TikTok video."""
    video_id = extract_video_id(url)
    result = {
        "url": url,
        "video_id": video_id,
        "transcript": None,
        "method": None,
        "transcribed_at": datetime.now(timezone.utc).isoformat(),
    }

    with tempfile.TemporaryDirectory() as work_dir:
        print(f"  Phase 1: Checking auto-captions for {video_id}...")
        text = extract_captions_ytdlp(url, work_dir)
        if text:
            result["transcript"] = text
            result["method"] = "auto_captions"
            print(f"  ✓ Got captions ({len(text)} chars)")
            return result

        print(f"  Phase 2: Downloading audio + whisper for {video_id}...")
        text = transcribe_with_whisper(url, work_dir)
        if text:
            result["transcript"] = text
            result["method"] = "whisper"
            print(f"  ✓ Whisper transcribed ({len(text)} chars)")
            return result

    print(f"  ✗ No transcript available for {video_id}")
    return result


def load_latest_tiktok_scan() -> dict | None:
    pattern = os.path.join(DATA_DIR, "tiktok_scan_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if files:
        with open(files[0]) as f:
            return json.load(f)
    return None


def extract_urls_from_scan(scan_data: dict, top_n: int = 50) -> list[dict]:
    """Extract video URLs from scan data, sorted by engagement."""
    signals = scan_data.get("hashtag_signals", [])
    signals.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)

    videos = []
    seen = set()
    for s in signals[:top_n]:
        url = s.get("url", s.get("video_url", ""))
        creator = s.get("creator", "")
        if url and url not in seen:
            seen.add(url)
            videos.append({
                "url": url,
                "creator": creator,
                "caption": s.get("caption", ""),
                "engagement_score": s.get("engagement_score", 0),
            })
    return videos


def run_batch(urls: list[str]) -> list[dict]:
    """Transcribe a batch of URLs."""
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    results = []

    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] {url}")
        result = transcribe_video(url)
        results.append(result)

    outfile = os.path.join(
        TRANSCRIPT_DIR,
        f"transcripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(outfile, "w") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total": len(results),
            "with_transcript": len([r for r in results if r["transcript"]]),
            "results": results,
        }, f, indent=2)

    print(f"\nSaved {len(results)} results to {outfile}")
    caption_count = len([r for r in results if r["method"] == "auto_captions"])
    whisper_count = len([r for r in results if r["method"] == "whisper"])
    failed = len([r for r in results if not r["transcript"]])
    print(f"  Auto-captions: {caption_count} | Whisper: {whisper_count} | Failed: {failed}")

    return results


def enrich_scan_with_transcripts(scan_data: dict, transcripts: list[dict]) -> dict:
    """Add transcripts back into scan data for aggregation."""
    transcript_map = {t["url"]: t for t in transcripts if t.get("transcript")}

    for signal in scan_data.get("hashtag_signals", []):
        url = signal.get("url", signal.get("video_url", ""))
        if url in transcript_map:
            signal["transcript"] = transcript_map[url]["transcript"]
            signal["transcript_method"] = transcript_map[url]["method"]

    return scan_data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--from-scan":
        top_n = 20
        if "--top" in sys.argv:
            idx = sys.argv.index("--top")
            top_n = int(sys.argv[idx + 1])

        scan = load_latest_tiktok_scan()
        if not scan:
            print("No TikTok scan data found")
            sys.exit(1)

        videos = extract_urls_from_scan(scan, top_n)
        if not videos:
            print("No video URLs found in scan data")
            sys.exit(1)

        print(f"Found {len(videos)} videos from latest scan (top {top_n} by engagement)")
        urls = [v["url"] for v in videos]
        run_batch(urls)

    elif sys.argv[1] == "--batch":
        with open(sys.argv[2]) as f:
            urls = [line.strip() for line in f if line.strip()]
        run_batch(urls)

    else:
        result = transcribe_video(sys.argv[1])
        if result["transcript"]:
            print(f"\n--- TRANSCRIPT ({result['method']}) ---")
            print(result["transcript"])
        else:
            print("\nNo transcript could be extracted.")
