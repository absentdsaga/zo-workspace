#!/usr/bin/env python3
"""
Atlas assembler - pack sprites into texture atlas with metadata
"""

import json
import sys
from pathlib import Path
from PIL import Image
import math

def load_config():
    config_path = Path(__file__).parent / "pipeline_config.json"
    with open(config_path) as f:
        return json.load(f)

def pack_sprites(sprite_paths, padding=2):
    """
    Simple bin-packing algorithm for sprite atlas
    Returns: (atlas_image, frame_positions)
    """
    if not sprite_paths:
        return None, {}

    # Load all sprites to get dimensions
    sprites = []
    for path in sprite_paths:
        img = Image.open(path)
        sprites.append({
            "path": path,
            "image": img,
            "width": img.width,
            "height": img.height
        })

    # Simple grid layout (can be optimized with better bin packing)
    # Calculate grid dimensions
    frame_count = len(sprites)
    cols = math.ceil(math.sqrt(frame_count))
    rows = math.ceil(frame_count / cols)

    # Assume all sprites are same size (normalized)
    sprite_w = sprites[0]["width"]
    sprite_h = sprites[0]["height"]

    atlas_w = cols * (sprite_w + padding) - padding
    atlas_h = rows * (sprite_h + padding) - padding

    # Create atlas
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))

    frame_positions = {}

    for i, sprite_data in enumerate(sprites):
        col = i % cols
        row = i // cols

        x = col * (sprite_w + padding)
        y = row * (sprite_h + padding)

        atlas.paste(sprite_data["image"], (x, y))

        frame_positions[sprite_data["path"].name] = {
            "x": x,
            "y": y,
            "width": sprite_w,
            "height": sprite_h
        }

    return atlas, frame_positions

def build_atlas(character_id, state=None):
    """Build atlas for character (all states or specific state)"""
    config = load_config()
    pipeline_dir = Path(__file__).parent

    qc_pass_dir = pipeline_dir / "output_qc_pass" / character_id
    atlas_dir = pipeline_dir / "atlas"
    atlas_dir.mkdir(parents=True, exist_ok=True)

    if not qc_pass_dir.exists():
        print(f"No QC pass directory found for {character_id}")
        return None

    # Collect sprites
    if state:
        pattern = f"{character_id}_{state}_*.png"
    else:
        pattern = f"{character_id}_*.png"

    sprite_paths = sorted(qc_pass_dir.glob(pattern))

    if not sprite_paths:
        print(f"No sprites found for {character_id} (state: {state})")
        return None

    print(f"Building atlas from {len(sprite_paths)} sprites...")

    # Pack into atlas
    atlas_image, frame_positions = pack_sprites(sprite_paths)

    if not atlas_image:
        print("Failed to pack sprites")
        return None

    # Save atlas image
    atlas_name = f"{character_id}_{state}" if state else character_id
    atlas_path = atlas_dir / f"{atlas_name}_atlas.png"
    atlas_image.save(atlas_path, "PNG", optimize=True)

    # Save atlas metadata
    atlas_meta = {
        "character_id": character_id,
        "state": state,
        "atlas_image": atlas_path.name,
        "frame_count": len(sprite_paths),
        "frames": frame_positions
    }

    atlas_meta_path = atlas_dir / f"{atlas_name}_atlas.json"
    with open(atlas_meta_path, "w") as f:
        json.dump(atlas_meta, f, indent=2)

    print(f"Atlas created: {atlas_path}")
    print(f"Metadata: {atlas_meta_path}")

    return {
        "atlas_image": str(atlas_path),
        "metadata": str(atlas_meta_path),
        "frame_count": len(sprite_paths)
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: atlas_assembler.py <character_id> [state]")
        sys.exit(1)

    character_id = sys.argv[1]
    state = sys.argv[2] if len(sys.argv) > 2 else None

    result = build_atlas(character_id, state)

    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
