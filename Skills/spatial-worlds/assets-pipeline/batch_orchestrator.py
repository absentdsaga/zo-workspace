#!/usr/bin/env python3
"""
Batch orchestrator V2 - Full ComfyUI API integration
Adds: deterministic seeds, retry logic, timeout handling, traceability

Only use this AFTER workflow_freeze_test.py passes 3/3
"""

import json
import sys
import subprocess
import time
import urllib.request
from pathlib import Path
from datetime import datetime
import shutil
import requests
from seed_strategy import get_seed

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

def build_workflow(character_id, state, frame_num, seed, config, job):
    """
    Build ComfyUI workflow JSON for a specific frame
    
    Uses locked workflow template and injects:
    - Character-specific positive/negative prompts
    - Deterministic seed
    - Output filename prefix
    """
    # Load locked workflow
    workflow_path = Path(__file__).parent / "comfy" / "workflow_locked_v1.json"
    if not workflow_path.exists():
        # Fallback to base workflow if not locked yet
        workflow_path = Path(__file__).parent / "comfy" / "workflow_character_base.json"
    
    with open(workflow_path) as f:
        workflow = json.load(f)
    
    # Build prompts
    prompts = config["prompts"]
    
    # Character-specific details from job
    color_theme = job.get("color_theme", "neutral")
    character_type = job.get("character_type", "character")
    
    # State-specific pose
    pose_description = prompts["poses"].get(state, state)
    
    # Construct positive prompt
    positive_parts = [
        prompts["global_style"],
        f"{color_theme} {character_type}",
        pose_description
    ]
    positive_prompt = ", ".join(positive_parts)
    
    # Inject into workflow
    workflow["2"]["inputs"]["text"] = positive_prompt
    workflow["3"]["inputs"]["text"] = prompts["negative"]
    workflow["5"]["inputs"]["seed"] = seed
    workflow["7"]["inputs"]["filename_prefix"] = f"{character_id}_{state}_f{frame_num:02d}"
    
    return workflow

def submit_prompt(workflow, comfy_url="http://localhost:8188"):
    """
    Submit workflow to ComfyUI and get prompt ID
    
    Returns:
        prompt_id (str) or None on failure
    """
    try:
        response = requests.post(
            f"{comfy_url}/prompt",
            json={"prompt": workflow},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result.get("prompt_id")
    except Exception as e:
        print(f"   ERROR: Failed to submit prompt: {e}")
        return None

def poll_until_done(prompt_id, timeout=300, comfy_url="http://localhost:8188"):
    """
    Poll ComfyUI history until prompt completes
    
    Returns:
        (status, history_payload)
        status: "success" | "timeout" | "error"
        history_payload: dict with outputs if success, None otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        time.sleep(2)
        
        try:
            history_response = requests.get(
                f"{comfy_url}/history/{prompt_id}",
                timeout=5
            )
            history = history_response.json()
            
            if prompt_id in history:
                return ("success", history[prompt_id])
        
        except Exception as e:
            print(f"   WARNING: Poll error: {e}")
            time.sleep(1)
            continue
    
    return ("timeout", None)

def collect_output_files(history_payload, comfy_url="http://localhost:8188"):
    """
    Extract output image info from history payload
    
    Returns:
        List of dicts with {filename, subfolder, type, download_url}
    """
    outputs = history_payload.get("outputs", {})
    
    # Find SaveImage node output (node 7 in our workflow)
    if "7" not in outputs or "images" not in outputs["7"]:
        return []
    
    images = outputs["7"]["images"]
    result = []
    
    for img_info in images:
        filename = img_info["filename"]
        subfolder = img_info.get("subfolder", "")
        img_type = img_info.get("type", "output")
        
        download_params = f"filename={filename}&subfolder={subfolder}&type={img_type}"
        download_url = f"{comfy_url}/view?{download_params}"
        
        result.append({
            "filename": filename,
            "subfolder": subfolder,
            "type": img_type,
            "download_url": download_url
        })
    
    return result

def copy_to_output_raw(download_url, character_id, state, frame_num):
    """
    Download generated image to output_raw directory
    
    Returns:
        Path to saved file
    """
    output_dir = Path(__file__).parent / "output_raw" / character_id / state
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{character_id}_{state}_f{frame_num:02d}_raw.png"
    
    urllib.request.urlretrieve(download_url, output_path)
    
    return output_path

def run_comfy_generation_with_retry(
    character_id, 
    state, 
    frame_num, 
    seed, 
    config, 
    job,
    max_retries=3,
    comfy_url="http://localhost:8188"
):
    """
    Run ComfyUI generation with exponential backoff retry
    
    Returns:
        (success: bool, output_path: Path or None, reason: str)
    """
    log(f"Generating {character_id}/{state}/frame_{frame_num:03d} (seed: {seed})", job["character_id"])
    
    workflow = build_workflow(character_id, state, frame_num, seed, config, job)
    
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            wait_time = 2 ** (attempt - 1)  # Exponential backoff: 2, 4, 8 seconds
            log(f"  Retry {attempt}/{max_retries} after {wait_time}s...", job["character_id"])
            time.sleep(wait_time)
        
        # Submit prompt
        prompt_id = submit_prompt(workflow, comfy_url)
        if not prompt_id:
            continue
        
        log(f"  Queued: {prompt_id} (attempt {attempt}/{max_retries})", job["character_id"])
        
        # Poll for completion
        status, history_payload = poll_until_done(prompt_id, timeout=300, comfy_url=comfy_url)
        
        if status == "timeout":
            log(f"  Timeout waiting for {prompt_id}", job["character_id"])
            continue
        
        if status == "error":
            log(f"  Error in generation for {prompt_id}", job["character_id"])
            continue
        
        # Collect outputs
        output_files = collect_output_files(history_payload, comfy_url)
        
        if not output_files:
            log(f"  No output files from {prompt_id}", job["character_id"])
            continue
        
        # Download first output
        download_url = output_files[0]["download_url"]
        output_path = copy_to_output_raw(download_url, character_id, state, frame_num)
        
        log(f"  Downloaded: {output_path.name}", job["character_id"])
        
        return (True, output_path, f"success_on_attempt_{attempt}")
    
    # All retries exhausted
    reason = f"failed_after_{max_retries}_attempts"
    log(f"  FAILED: {reason}", job["character_id"])
    
    # Create placeholder to track failure
    output_dir = Path(__file__).parent / "output_raw" / character_id / state
    output_dir.mkdir(parents=True, exist_ok=True)
    failed_marker = output_dir / f"{character_id}_{state}_f{frame_num:02d}_FAILED.json"
    
    with open(failed_marker, "w") as f:
        json.dump({
            "character_id": character_id,
            "state": state,
            "frame_num": frame_num,
            "seed": seed,
            "reason": reason,
            "attempts": max_retries
        }, f, indent=2)
    
    return (False, None, reason)

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
    if raw_path and raw_path.exists():
        subprocess.run([sys.executable, str(pipeline_dir / "cutout_sprite.py"), str(raw_path), str(cut_path)], check=True)
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

    base_seed = config["comfy"].get("base_seed", 42)

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
            # Deterministic seed
            seed = get_seed(job_id, state, frame_num, base_seed)

            # Generate with ComfyUI (with retry)
            success, raw_path, reason = run_comfy_generation_with_retry(
                job_id,
                state,
                frame_num,
                seed,
                config,
                job
            )

            if not success:
                log(f"Skipping frame {frame_num} - generation failed: {reason}", job_id)
                continue

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
                "pass_rate": f"{len(passed_frames)}/{frame_count}",
                "metadata": str(metadata_path)
            }
        else:
            log(f"WARNING: No frames passed QC for state '{state}'", job_id)
            results["states"][state] = {
                "passed_frames": 0,
                "total_frames": frame_count,
                "pass_rate": "0/0",
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
        print("Usage: batch_orchestrator_v2.py <job_file.json>")
        sys.exit(1)

    job_path = sys.argv[1]
    results = run_job(job_path)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
