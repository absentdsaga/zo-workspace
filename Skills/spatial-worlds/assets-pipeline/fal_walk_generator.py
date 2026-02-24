#!/usr/bin/env python3
"""
Walk animation generator for 2.5D isometric chibi sprites.

Generates 4 directions × 4 frames = 16 images per character,
then assembles into a 256×256 sprite sheet for the game engine.

Sheet layout (matches IsoGame-NFT-TEST.ts):
  Row 0 (frames  0- 3): south (walking toward viewer)
  Row 1 (frames  4- 7): north (walking away)
  Row 2 (frames  8-11): west  (walking left)
  Row 3 (frames 12-15): east  (walking right)

Each frame is 64×64 px.

Usage:
    python3 fal_walk_generator.py jobs/hero_orange_walk.json
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    import fal_client
except ImportError:
    print("ERROR: fal-client not installed. Run: pip install fal-client --break-system-packages")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow --break-system-packages")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).parent
GAME_SPRITES_DIR = PIPELINE_DIR.parent / "assets" / "sprites" / "nft-characters-xxl"

# Direction → game engine direction name mapping
DIR_MAP = {
    "south": "south",   # frames 0-3
    "north": "north",   # frames 4-7
    "west":  "west",    # frames 8-11
    "east":  "east",    # frames 12-15
}

FRAME_SIZE = 64  # Each cell in the sheet is 64×64
SHEET_COLS = 4
SHEET_ROWS = 4   # 4 directions

def log(msg, job_id="walk"):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{ts}][{job_id}] {msg}")


def load_config():
    with open(PIPELINE_DIR / "pipeline_config.json") as f:
        return json.load(f)


def load_job(job_path):
    with open(job_path) as f:
        return json.load(f)


def get_seed(character_id, direction, frame_num, base_seed=42):
    key = f"{character_id}_walk_{direction}_{frame_num}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return (base_seed + h) % (2**32)


# ── Prompt building ──────────────────────────────────────────────────────────

DIRECTION_PROMPTS = {
    "south": {
        "view": "front-facing three-quarter view, character walking toward viewer, feet visible, slight downward angle as if seen from above",
        "frames": [
            "left leg forward and right leg back mid-stride",
            "both legs centered upright transition step",
            "right leg forward and left leg back mid-stride",
            "both legs centered balanced neutral step",
        ]
    },
    "north": {
        "view": "back-facing three-quarter view, character walking away from viewer, back of armor visible, slight downward angle as if seen from above",
        "frames": [
            "left leg forward and right leg back mid-stride from behind",
            "both legs centered upright transition step from behind",
            "right leg forward and left leg back mid-stride from behind",
            "both legs centered balanced neutral step from behind",
        ]
    },
    "east": {
        "view": "side-profile view facing right, character walking rightward, slight downward angle as if seen from above",
        "frames": [
            "front foot planted forward right stride",
            "feet passing center transition right walk",
            "back foot pushing off ground right stride",
            "feet close together weight transfer right walk",
        ]
    },
    "west": {
        "view": "side-profile view facing left, character walking leftward, slight downward angle as if seen from above",
        "frames": [
            "front foot planted forward left stride",
            "feet passing center transition left walk",
            "back foot pushing off ground left stride",
            "feet close together weight transfer left walk",
        ]
    }
}


def build_walk_prompt(color_theme, character_type, direction, frame_idx, config):
    global_style = config["prompts"]["global_style"]
    negative = config["prompts"]["negative"]

    dir_info = DIRECTION_PROMPTS[direction]
    view = dir_info["view"]
    frame_desc = dir_info["frames"][frame_idx]

    positive = (
        f"{global_style}, "
        f"{color_theme} {character_type}, "
        f"{view}, "
        f"walk animation frame: {frame_desc}, "
        f"transparent background, isolated character only"
    )
    return positive, negative


# ── fal.ai generation ────────────────────────────────────────────────────────

def image_to_data_uri(path):
    """Convert local image file to base64 data URI for fal.ai img2img."""
    import base64
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"data:{mime};base64,{b64}"


def generate_frame(character_id, direction, frame_idx, config, job, ref_frame_path=None, max_retries=3):
    """
    Generate a single walk frame.
    - frame_idx == 0: text-to-image (establishes reference character design)
    - frame_idx > 0:  img2img from ref_frame_path (maintains character consistency)
    """
    color_theme = job.get("color_theme", "colorful")
    character_type = job.get("character_type", "character")
    base_seed = config["comfy"].get("base_seed", 42)

    positive, _ = build_walk_prompt(color_theme, character_type, direction, frame_idx, config)
    seed = get_seed(character_id, direction, frame_idx, base_seed)
    w = config["comfy"]["gen_canvas"]["width"]
    h = config["comfy"]["gen_canvas"]["height"]

    use_img2img = (frame_idx > 0 and ref_frame_path is not None)
    mode = "img2img" if use_img2img else "txt2img"
    log(f"  Generating {direction}/f{frame_idx} [{mode}] | seed={seed}", character_id)

    for attempt in range(1, max_retries + 1):
        try:
            if use_img2img:
                # Use the reference frame (frame 0) to lock in character appearance
                # strength 0.60 = keep 40% of original, change pose
                image_data_uri = image_to_data_uri(ref_frame_path)
                result = fal_client.run(
                    "fal-ai/flux/dev/image-to-image",
                    arguments={
                        "image_url": image_data_uri,
                        "prompt": positive,
                        "strength": 0.60,
                        "num_inference_steps": 28,
                        "seed": seed,
                        "num_images": 1,
                        "enable_safety_checker": False,
                    },
                )
            else:
                # Frame 0: text-to-image to establish the character design
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

            # Save to output_raw
            out_dir = PIPELINE_DIR / "output_raw" / character_id / f"walk_{direction}"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{character_id}_walk_{direction}_f{frame_idx:02d}_raw.png"
            urllib.request.urlretrieve(image_url, out_path)
            log(f"  Saved raw: {out_path.name}", character_id)
            return True, out_path

        except Exception as e:
            log(f"  Attempt {attempt} failed: {e}", character_id)
            if attempt < max_retries:
                time.sleep(2 ** attempt)

    return False, None


def process_frame(raw_path, character_id, direction, frame_idx, job_id):
    """Run cutout → normalize (64×64 for sheet)"""
    cut_dir = PIPELINE_DIR / "output_cut" / character_id / f"walk_{direction}"
    norm_dir = PIPELINE_DIR / "output_norm_walk" / character_id / f"walk_{direction}"

    for d in [cut_dir, norm_dir]:
        d.mkdir(parents=True, exist_ok=True)

    cut_path = cut_dir / f"{character_id}_walk_{direction}_f{frame_idx:02d}_cut.png"
    norm_path = norm_dir / f"{character_id}_walk_{direction}_f{frame_idx:02d}.png"

    # Step 1: Background removal
    r = subprocess.run(
        [sys.executable, str(PIPELINE_DIR / "cutout_sprite.py"), str(raw_path), str(cut_path)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        log(f"  Cutout failed: {r.stderr[:200]}", job_id)
        return None

    # Step 2: Normalize to 64×64
    normalize_to_64(cut_path, norm_path)
    log(f"  Normalized: {norm_path.name}", job_id)
    return norm_path


def normalize_to_64(input_path, output_path):
    """Normalize cutout to 64×64 transparent canvas, character centered with feet at bottom."""
    import numpy as np
    img = Image.open(input_path).convert("RGBA")
    arr = __import__("numpy").array(img)
    alpha = arr[:, :, 3]

    rows = __import__("numpy").any(alpha > 10, axis=1)
    cols = __import__("numpy").any(alpha > 10, axis=0)

    if not __import__("numpy").any(rows):
        canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        canvas.save(output_path, "PNG")
        return

    y_indices = __import__("numpy").where(rows)[0]
    x_indices = __import__("numpy").where(cols)[0]
    y_min, y_max = int(y_indices[0]), int(y_indices[-1])
    x_min, x_max = int(x_indices[0]), int(x_indices[-1])

    char = img.crop((x_min, y_min, x_max + 1, y_max + 1))
    char_h = y_max - y_min + 1
    char_w = x_max - x_min + 1

    # Scale to fit in 60×60 (leave 2px margin)
    target = 56
    scale = target / max(char_h, char_w)
    new_w = max(1, int(char_w * scale))
    new_h = max(1, int(char_h * scale))
    char = char.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    # Center horizontally, bottom-align (feet at y=62)
    paste_x = (64 - new_w) // 2
    paste_y = 62 - new_h
    canvas.paste(char, (paste_x, paste_y), char)
    canvas.save(output_path, "PNG")


# ── Sprite sheet assembly ────────────────────────────────────────────────────

DIRECTION_ORDER = ["south", "north", "west", "east"]  # matches engine frame layout

def assemble_sheet(character_id, frame_paths_by_dir, output_dir):
    """Assemble 4×4 grid of 64×64 frames into 256×256 sprite sheet."""
    sheet = Image.new("RGBA", (FRAME_SIZE * SHEET_COLS, FRAME_SIZE * SHEET_ROWS), (0, 0, 0, 0))

    for row_idx, direction in enumerate(DIRECTION_ORDER):
        frames = frame_paths_by_dir.get(direction, [])
        for col_idx in range(SHEET_COLS):
            if col_idx < len(frames) and frames[col_idx] is not None:
                frame_img = Image.open(frames[col_idx]).convert("RGBA")
                if frame_img.size != (FRAME_SIZE, FRAME_SIZE):
                    frame_img = frame_img.resize((FRAME_SIZE, FRAME_SIZE), Image.LANCZOS)
                sheet.paste(frame_img, (col_idx * FRAME_SIZE, row_idx * FRAME_SIZE), frame_img)
            else:
                # Fill with a placeholder (magenta) if frame missing
                log(f"  WARNING: Missing {direction}/f{col_idx}, using placeholder", character_id)
                placeholder = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (255, 0, 255, 128))
                sheet.paste(placeholder, (col_idx * FRAME_SIZE, row_idx * FRAME_SIZE))

    output_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = output_dir / f"{character_id}-sheet.png"
    sheet.save(sheet_path, "PNG")
    log(f"  Sheet saved: {sheet_path}", character_id)
    return sheet_path


def copy_to_game(character_id, sheet_path, frame_paths_by_dir):
    """Copy sprite sheet into game assets directory."""
    game_char_dir = GAME_SPRITES_DIR / character_id
    game_char_dir.mkdir(parents=True, exist_ok=True)

    # Copy sheet
    dest_sheet = game_char_dir / f"{character_id}-sheet.png"
    shutil.copy(sheet_path, dest_sheet)
    log(f"  Copied sheet to game: {dest_sheet}", character_id)

    # Copy individual frames with proper names for reference
    for dir_name, frames in frame_paths_by_dir.items():
        for i, fp in enumerate(frames):
            if fp is not None:
                dest = game_char_dir / f"{dir_name}-walk-{i}.png"
                shutil.copy(fp, dest)

    log(f"  Game assets updated: {game_char_dir}", character_id)
    return dest_sheet


# ── Main ─────────────────────────────────────────────────────────────────────

def run_job(job_path):
    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        print("ERROR: FAL_API_KEY not set. Run: source /root/.zo_secrets")
        sys.exit(1)
    os.environ["FAL_KEY"] = api_key

    config = load_config()
    job = load_job(job_path)
    character_id = job["character_id"]
    directions = job.get("walk_directions", ["south", "north", "east", "west"])
    frames_per_dir = job.get("frames_per_direction", 4)

    log(f"Starting walk job: {character_id}", character_id)
    log(f"Directions: {directions}, Frames: {frames_per_dir}", character_id)

    frame_paths_by_dir = {}

    for direction in directions:
        log(f"\n── Direction: {direction} ──", character_id)
        frames = []

        ref_frame_path = None  # frame 0 raw path used as img2img reference

        for frame_idx in range(frames_per_dir):
            success, raw_path = generate_frame(
                character_id, direction, frame_idx, config, job,
                ref_frame_path=ref_frame_path
            )
            if not success:
                log(f"  Frame {frame_idx} generation failed, using None", character_id)
                frames.append(None)
                continue

            # Frame 0 becomes the reference for all subsequent frames in this direction
            if frame_idx == 0:
                ref_frame_path = raw_path

            norm_path = process_frame(raw_path, character_id, direction, frame_idx, character_id)
            frames.append(norm_path)

        frame_paths_by_dir[direction] = frames
        passed = sum(1 for f in frames if f is not None)
        log(f"  {direction}: {passed}/{frames_per_dir} frames ready", character_id)

    # Assemble sprite sheet
    log(f"\n── Assembling sprite sheet ──", character_id)
    sheet_dir = PIPELINE_DIR / "output_sheets" / character_id
    sheet_path = assemble_sheet(character_id, frame_paths_by_dir, sheet_dir)

    # Copy to game
    log(f"\n── Copying to game assets ──", character_id)
    game_path = copy_to_game(character_id, sheet_path, frame_paths_by_dir)

    log(f"\n── COMPLETE ──", character_id)
    log(f"  Sheet: {sheet_path}", character_id)
    log(f"  Game:  {game_path}", character_id)

    return {"character_id": character_id, "sheet_path": str(sheet_path), "game_path": str(game_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fal_walk_generator.py <job_file.json>")
        print("Example: python3 fal_walk_generator.py jobs/hero_orange_walk.json")
        sys.exit(1)
    run_job(sys.argv[1])
