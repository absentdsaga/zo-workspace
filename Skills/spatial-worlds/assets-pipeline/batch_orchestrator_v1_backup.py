#!/usr/bin/env python3
"""
Batch orchestrator for sprite pipeline
Manages ComfyUI generation → cutout → normalize → QC → metadata
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

def load_config():
    config_path = Path(__file__).parent / "pipeline_config.json"
    with open(config_path) as f:
        return json.load(f)

def load_job(job_path):
    """Load character job specification"""
    with open(job_path) as f:
        return json.load(f)

def log(message, job_id):
    """Write to job log"""
    log_dir = Path(__file__).parent / "logs"
    log_file = log_dir / f"{job_id}.log"

    timestamp = datetime.utcnow().isoformat()
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

    print(f"[{job_id}] {message}")

def generate_comfy_prompt(character_id, state, pose, config, job):
    """Build ComfyUI prompt from config"""
    prompts = config["prompts"]

    positive_parts = [
        prompts["global_style"],
        f"{job.get('color_theme', 'neutral')} color theme",
        prompts["poses"].get(pose, pose)
    ]

    return {
        "positive": ", ".join(positive_parts),
        "negative": prompts["negative"]
    }

def run_comfy_generation(character_id, state, frame_num, seed_offset, config, job):
    """
    Run ComfyUI generation for a single frame
    """
    import requests
    import time
    import urllib.request

    log(f"Generating {character_id}/{state}/frame_{frame_num:03d}", job["character_id"])

    # Output directory
    output_dir = Path(__file__).parent / "output_raw" / character_id / state
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{character_id}_{state}_f{frame_num:02d}_raw.png"

    # Load workflow template
    workflow_path = Path(__file__).parent / "comfy" / "workflow_character_base.json"
    with open(workflow_path) as f:
        workflow = json.load(f)

    # Generate prompts
    prompts = generate_comfy_prompt(character_id, state, f"frame_{frame_num}", config, job)

    # Inject prompts into workflow
    workflow["2"]["inputs"]["text"] = prompts["positive"]
    workflow["3"]["inputs"]["text"] = prompts["negative"]

    # Set seed
    base_seed = config["comfy"].get("base_seed", 42)
    workflow["5"]["inputs"]["seed"] = base_seed + seed_offset

    # Set filename prefix
    workflow["7"]["inputs"]["filename_prefix"] = f"{character_id}_{state}_f{frame_num:02d}"

    # Submit to ComfyUI
    comfy_url = "http://localhost:8188"

    try:
        # Queue the prompt
        response = requests.post(
            f"{comfy_url}/prompt",
            json={"prompt": workflow}
        )
        response.raise_for_status()
        result = response.json()
        prompt_id = result["prompt_id"]

        log(f"ComfyUI prompt queued: {prompt_id}", job["character_id"])

        # Poll for completion
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            time.sleep(2)

            # Check history
            history_response = requests.get(f"{comfy_url}/history/{prompt_id}")
            history = history_response.json()

            if prompt_id in history:
                # Generation complete
                outputs = history[prompt_id].get("outputs", {})

                # Find the SaveImage node output (node 7)
                if "7" in outputs and "images" in outputs["7"]:
                    images = outputs["7"]["images"]
                    if images:
                        # Download the image
                        image_info = images[0]
                        image_filename = image_info["filename"]
                        image_subfolder = image_info.get("subfolder", "")
                        image_type = image_info.get("type", "output")

                        # Construct download URL
                        download_params = f"filename={image_filename}&subfolder={image_subfolder}&type={image_type}"
                        download_url = f"{comfy_url}/view?{download_params}"

                        # Download and save
                        urllib.request.urlretrieve(download_url, output_path)

                        log(f"Downloaded: {output_path.name}", job["character_id"])
                        return output_path

        log(f"ERROR: ComfyUI generation timeout for frame {frame_num}", job["character_id"])
        return output_path  # Return path even if failed

    except Exception as e:
        log(f"ERROR: ComfyUI generation failed: {e}", job["character_id"])
        return output_path  # Return path even if failed

def process_frame(raw_path, character_id, state, frame_num, prev_normalized_path, config, job):
    """Process a single frame through the pipeline"""
    job_id = job["character_id"]

    # Paths
    cut_dir = Path(__file__).parent / "output_cut" / character_id
    norm_dir = Path(__file__).parent / "output_norm" / character_id
    qc_pass_dir = Path(__file__).parent / "output_qc_pass" / character_id
    qc_fail_dir = Path(__file__).parent / "output_qc_fail" / character_id

    for d in [cut_dir, norm_dir, qc_pass_dir, qc_fail_dir]:
        d.mkdir(parents=True, exist_ok=True)

    cut_path = cut_dir / f"{character_id}_{state}_f{frame_num:02d}_cut.png"
    norm_path = norm_dir / f"{character_id}_{state}_f{frame_num:02d}.png"

    # Step 1: Cutout (background removal)
    log(f"Cutting out frame {frame_num}", job_id)
    # For now, just copy - real implementation would use rembg or similar
    if raw_path.exists():
        shutil.copy(raw_path, cut_path)
    else:
        log(f"WARNING: Raw frame not found: {raw_path}", job_id)
        return None

    # Step 2: Normalize
    log(f"Normalizing frame {frame_num}", job_id)
    pipeline_dir = Path(__file__).parent
    subprocess.run([
        sys.executable,
        str(pipeline_dir / "normalize_sprite.py"),
        str(cut_path),
        str(norm_path)
    ], check=True)

    # Step 3: QC
    log(f"QC checking frame {frame_num}", job_id)
    qc_result = subprocess.run([
        sys.executable,
        str(pipeline_dir / "qc_checker.py"),
        str(norm_path),
        str(prev_normalized_path) if prev_normalized_path else ""
    ], capture_output=True, text=True)

    qc_data = json.loads(qc_result.stdout)

    if qc_data["passed"]:
        # Move to pass directory
        pass_path = qc_pass_dir / norm_path.name
        shutil.copy(norm_path, pass_path)
        log(f"Frame {frame_num} PASSED QC", job_id)
        return pass_path
    else:
        # Move to fail directory with reason
        fail_path = qc_fail_dir / norm_path.name
        reason_path = qc_fail_dir / f"{norm_path.stem}_reason.json"

        shutil.copy(norm_path, fail_path)
        with open(reason_path, "w") as f:
            json.dump(qc_data, f, indent=2)

        log(f"Frame {frame_num} FAILED QC: {qc_data['failures']}", job_id)
        return None

def generate_metadata(character_id, state, frame_paths, config, job):
    """Generate engine-ready metadata JSON"""
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

    frame_duration_ms = int(1000 / anim_spec["frame_rate"])

    for i, frame_path in enumerate(frame_paths):
        frame_num = i + 1
        event = None

        # Check for event frames
        if "events" in anim_spec:
            for event_name, event_frame in anim_spec["events"].items():
                if frame_num == event_frame:
                    event = event_name

        metadata["frames"].append({
            "file": frame_path.name,
            "duration_ms": frame_duration_ms,
            "event": event
        })

    # Write metadata
    metadata_dir = Path(__file__).parent / "metadata" / character_id
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = metadata_dir / f"{character_id}_{state}.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata_path

def run_job(job_path):
    """Execute full pipeline for a character job"""
    config = load_config()
    job = load_job(job_path)

    job_id = job["character_id"]
    log(f"Starting job for {job_id}", job_id)

    results = {
        "character_id": job_id,
        "states": {}
    }

    # Process each animation state
    for state in job["states"]:
        log(f"Processing state: {state}", job_id)

        anim_spec = config["animation_spec"].get(state)
        if not anim_spec:
            log(f"WARNING: No animation spec for state '{state}'", job_id)
            continue

        frame_count = anim_spec["frames"]
        passed_frames = []
        prev_normalized_path = None

        # Generate and process each frame
        for frame_num in range(1, frame_count + 1):
            # Determine seed offset (deterministic per frame)
            seed_offset = frame_num * 1000

            # Generate with ComfyUI (placeholder)
            raw_path = run_comfy_generation(
                job_id,
                state,
                frame_num,
                seed_offset,
                config,
                job
            )

            # Process through pipeline
            result_path = process_frame(
                raw_path,
                job_id,
                state,
                frame_num,
                prev_normalized_path,
                config,
                job
            )

            if result_path:
                passed_frames.append(result_path)
                prev_normalized_path = result_path

        # Generate metadata for this animation
        if passed_frames:
            metadata_path = generate_metadata(
                job_id,
                state,
                passed_frames,
                config,
                job
            )
            log(f"Metadata written: {metadata_path}", job_id)

            results["states"][state] = {
                "passed_frames": len(passed_frames),
                "total_frames": frame_count,
                "metadata": str(metadata_path)
            }
        else:
            log(f"WARNING: No frames passed QC for state '{state}'", job_id)
            results["states"][state] = {
                "passed_frames": 0,
                "total_frames": frame_count,
                "metadata": None
            }

    # Write final job results
    results_dir = Path(__file__).parent / "logs"
    results_path = results_dir / f"{job_id}_results.json"

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"Job complete. Results: {results_path}", job_id)
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: batch_orchestrator.py <job_file.json>")
        sys.exit(1)

    job_path = sys.argv[1]
    results = run_job(job_path)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
