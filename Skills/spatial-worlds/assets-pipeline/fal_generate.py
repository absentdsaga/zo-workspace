#!/usr/bin/env python3
# Run with: python3 fal_generate.py <job_file.json>
"""
fal.ai sprite generation — replaces ComfyUI for cloud GPU generation.
Uses SD 1.5 via fal.ai API, then feeds output into existing pipeline.

Usage:
    python fal_generate.py <job_file.json>
    python fal_generate.py jobs/pilot_hero.json
"""

import os
import sys
import json
import time
import urllib.request
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    import fal_client
except ImportError:
    print("ERROR: fal-client not installed. Run: pip install fal-client")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).parent

def load_config():
    with open(PIPELINE_DIR / "pipeline_config.json") as f:
        return json.load(f)

def load_job(job_path):
    with open(job_path) as f:
        return json.load(f)

def log(msg, job_id="fal"):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{ts}][{job_id}] {msg}")
    log_dir = PIPELINE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    with open(log_dir / f"{job_id}_fal.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

# ── Prompt building ───────────────────────────────────────────────────────────

def build_prompts(character_id, state, color_theme, character_type, config):
    prompts = config["prompts"]
    pose = prompts["poses"].get(state, state)
    positive = f"{prompts['global_style']}, {color_theme} {character_type}, {pose}"
    negative = prompts["negative"]
    return positive, negative

def get_seed(character_id, state, frame_num, base_seed=42):
    """Deterministic seed matching seed_strategy.py logic"""
    import hashlib
    key = f"{character_id}_{state}_{frame_num}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return (base_seed + h) % (2**32)

# ── fal.ai generation ─────────────────────────────────────────────────────────

def generate_frame_fal(character_id, state, frame_num, config, job, max_retries=3):
    """Generate a single sprite frame via fal.ai SD 1.5"""
    color_theme = job.get("color_theme", "neutral")
    character_type = job.get("character_type", "character")
    base_seed = config["comfy"].get("base_seed", 42)

    positive, negative = build_prompts(character_id, state, color_theme, character_type, config)
    seed = get_seed(character_id, state, frame_num, base_seed)
    steps = config["comfy"]["steps"]
    cfg = config["comfy"]["cfg"]
    w = config["comfy"]["gen_canvas"]["width"]
    h = config["comfy"]["gen_canvas"]["height"]

    log(f"Generating {character_id}/{state}/f{frame_num:02d} | seed={seed}", character_id)
    log(f"  Prompt: {positive[:80]}...", character_id)

    for attempt in range(1, max_retries + 1):
        try:
            # FLUX/schnell: fast, excellent prompt adherence, no negative prompt needed
            result = fal_client.run(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": positive,
                    "image_size": {"width": w, "height": h},
                    "num_inference_steps": 4,
                    "seed": seed,
                    "num_images": 1,
                    "enable_safety_checker": False,
                },
            )

            images = result.get("images", [])
            if not images:
                log(f"  Attempt {attempt}: No images returned", character_id)
                time.sleep(2 ** attempt)
                continue

            image_url = images[0]["url"]
            log(f"  Generated: {image_url[:60]}...", character_id)

            # Download to output_raw
            out_dir = PIPELINE_DIR / "output_raw" / character_id / state
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{character_id}_{state}_f{frame_num:02d}_raw.png"
            urllib.request.urlretrieve(image_url, out_path)
            log(f"  Saved: {out_path.name}", character_id)
            return True, out_path

        except Exception as e:
            log(f"  Attempt {attempt} failed: {e}", character_id)
            if attempt < max_retries:
                time.sleep(2 ** attempt)

    log(f"  FAILED after {max_retries} attempts", character_id)
    return False, None

# ── Post-processing pipeline ──────────────────────────────────────────────────

def process_frame(raw_path, character_id, state, frame_num, prev_norm_path, job_id):
    """Run raw image through cutout → normalize → QC"""
    cut_dir = PIPELINE_DIR / "output_cut" / character_id
    norm_dir = PIPELINE_DIR / "output_norm" / character_id
    qc_pass_dir = PIPELINE_DIR / "output_qc_pass" / character_id
    qc_fail_dir = PIPELINE_DIR / "output_qc_fail" / character_id

    for d in [cut_dir, norm_dir, qc_pass_dir, qc_fail_dir]:
        d.mkdir(parents=True, exist_ok=True)

    cut_path = cut_dir / f"{character_id}_{state}_f{frame_num:02d}_cut.png"
    norm_path = norm_dir / f"{character_id}_{state}_f{frame_num:02d}.png"

    # Step 1: Background removal
    log(f"  Cutout: {raw_path.name}", job_id)
    r = subprocess.run(
        [sys.executable, str(PIPELINE_DIR / "cutout_sprite.py"), str(raw_path), str(cut_path)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        log(f"  Cutout failed: {r.stderr[:100]}", job_id)
        return None

    # Step 2: Normalize
    log(f"  Normalize", job_id)
    r = subprocess.run(
        [sys.executable, str(PIPELINE_DIR / "normalize_sprite.py"), str(cut_path), str(norm_path)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        log(f"  Normalize failed: {r.stderr[:100]}", job_id)
        return None

    # Step 3: QC
    log(f"  QC check", job_id)
    args = [sys.executable, str(PIPELINE_DIR / "qc_checker.py"), str(norm_path)]
    if prev_norm_path:
        args.append(str(prev_norm_path))
    r = subprocess.run(args, capture_output=True, text=True)

    try:
        qc_data = json.loads(r.stdout)
    except json.JSONDecodeError:
        log(f"  QC parse error: {r.stdout[:100]}", job_id)
        return None

    if qc_data.get("passed"):
        pass_path = qc_pass_dir / norm_path.name
        shutil.copy(norm_path, pass_path)
        log(f"  QC PASSED", job_id)
        return pass_path
    else:
        fail_path = qc_fail_dir / norm_path.name
        shutil.copy(norm_path, fail_path)
        reason_path = qc_fail_dir / f"{norm_path.stem}_reason.json"
        with open(reason_path, "w") as f:
            json.dump(qc_data, f, indent=2)
        log(f"  QC FAILED: {qc_data.get('failures', [])}", job_id)
        return None

def generate_metadata(character_id, state, frame_paths, config):
    anim_spec = config["animation_spec"][state]
    shadow = config["shadow"]
    norm = config["normalization"]

    metadata = {
        "character_id": character_id,
        "state": state,
        "frame_rate": anim_spec["frame_rate"],
        "loop": anim_spec["loop"],
        "pivot_px": norm["pivot"],
        "baseline_y": norm["baseline_y"],
        "frames": [],
        "sort_bias": 0,
        "shadow": shadow
    }

    frame_ms = int(1000 / anim_spec["frame_rate"])
    for i, fp in enumerate(frame_paths):
        event = None
        if "events" in anim_spec:
            for ev_name, ev_frame in anim_spec["events"].items():
                if (i + 1) == ev_frame:
                    event = ev_name
        metadata["frames"].append({"file": fp.name, "duration_ms": frame_ms, "event": event})

    meta_dir = PIPELINE_DIR / "metadata" / character_id
    meta_dir.mkdir(parents=True, exist_ok=True)
    meta_path = meta_dir / f"{character_id}_{state}.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    return meta_path

# ── Main ──────────────────────────────────────────────────────────────────────

def run_job(job_path):
    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        print("ERROR: FAL_API_KEY not set. Run: source /root/.zo_secrets")
        sys.exit(1)

    os.environ["FAL_KEY"] = api_key  # fal-client reads FAL_KEY

    config = load_config()
    job = load_job(job_path)
    character_id = job["character_id"]

    log(f"Starting job: {character_id}", character_id)
    log(f"States: {job['states']}", character_id)

    results = {"character_id": character_id, "states": {}}

    for state in job["states"]:
        anim_spec = config["animation_spec"].get(state)
        if not anim_spec:
            log(f"No anim spec for '{state}', skipping", character_id)
            continue

        frame_count = anim_spec["frames"]
        log(f"\n── State: {state} ({frame_count} frames) ──", character_id)

        passed_frames = []
        prev_norm_path = None

        for frame_num in range(1, frame_count + 1):
            success, raw_path = generate_frame_fal(character_id, state, frame_num, config, job)
            if not success:
                log(f"Skipping frame {frame_num} — generation failed", character_id)
                continue

            result_path = process_frame(raw_path, character_id, state, frame_num, prev_norm_path, character_id)
            if result_path:
                passed_frames.append(result_path)
                prev_norm_path = result_path

        if passed_frames:
            meta_path = generate_metadata(character_id, state, passed_frames, config)
            log(f"Metadata: {meta_path}", character_id)
            results["states"][state] = {
                "passed": len(passed_frames),
                "total": frame_count,
                "rate": f"{len(passed_frames)}/{frame_count}",
                "metadata": str(meta_path)
            }
        else:
            log(f"WARNING: 0 frames passed for state '{state}'", character_id)
            results["states"][state] = {"passed": 0, "total": frame_count, "rate": "0/0"}

    # Summary
    log(f"\n── COMPLETE ──", character_id)
    for state, r in results["states"].items():
        log(f"  {state}: {r['rate']} frames passed QC", character_id)

    # Save results
    results_path = PIPELINE_DIR / "logs" / f"{character_id}_fal_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"Results: {results_path}", character_id)

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fal_generate.py <job_file.json>")
        print("Example: python fal_generate.py jobs/pilot_hero.json")
        sys.exit(1)
    run_job(sys.argv[1])
