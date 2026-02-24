#!/usr/bin/env python3
"""
Sprite normalization - enforce consistent size, baseline, palette
"""

import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def load_config():
    config_path = Path(__file__).parent / "pipeline_config.json"
    with open(config_path) as f:
        return json.load(f)

def remove_background(img):
    """Aggressive background removal and alpha cleanup"""
    img_array = np.array(img.convert("RGBA"))

    # Threshold alpha
    alpha = img_array[:, :, 3]
    alpha = np.where(alpha < 10, 0, alpha)

    # Decontaminate edge halos (1px)
    # Find edge pixels (adjacent to transparent)
    from scipy.ndimage import binary_dilation
    transparent_mask = alpha == 0
    edge_mask = binary_dilation(transparent_mask) & (alpha > 0)

    # Reduce alpha of edge pixels slightly to remove halos
    alpha = np.where(edge_mask, alpha * 0.8, alpha)
    img_array[:, :, 3] = alpha.astype(np.uint8)

    return Image.fromarray(img_array, mode="RGBA")

def trim_transparent_margins(img):
    """Remove transparent margins"""
    img_array = np.array(img)
    alpha = img_array[:, :, 3]

    # Find bounding box
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)

    if not np.any(rows) or not np.any(cols):
        return img  # Empty image

    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    return img.crop((x_min, y_min, x_max + 1, y_max + 1))

def quantize_palette(img, max_colors):
    """Reduce to max palette colors using adaptive quantization"""
    # RGBA images require FASTOCTREE (method=2); MEDIANCUT only works on RGB
    quantized = img.quantize(colors=max_colors, method=Image.FASTOCTREE)
    return quantized.convert("RGBA")

def recenter_to_baseline(img, canvas_w, canvas_h, baseline_y, target_height):
    """
    Recenter sprite to fixed canvas with foot baseline
    Scale to target height if needed
    """
    img_array = np.array(img)
    alpha = img_array[:, :, 3]

    # Get current bounds
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)

    if not np.any(rows):
        # Empty image, return blank canvas
        return Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    y_indices = np.where(rows)[0]
    x_indices = np.where(cols)[0]

    current_height = y_indices[-1] - y_indices[0] + 1
    current_width = x_indices[-1] - x_indices[0] + 1

    # Scale to target height if needed
    if current_height != target_height:
        scale_factor = target_height / current_height
        new_width = int(current_width * scale_factor)
        new_height = target_height

        # Use NEAREST for pixel-art scaling
        img = img.resize((new_width, new_height), Image.NEAREST)
        img_array = np.array(img)
        alpha = img_array[:, :, 3]

        # Recalculate bounds
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)
        y_indices = np.where(rows)[0]
        x_indices = np.where(cols)[0]

    # Find current lowest pixel (feet)
    lowest_y = y_indices[-1]

    # Create new canvas
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    # Calculate paste position
    # Feet should be at baseline_y
    paste_y = baseline_y - lowest_y

    # Center horizontally
    sprite_width = x_indices[-1] - x_indices[0] + 1
    paste_x = (canvas_w - sprite_width) // 2 - x_indices[0]

    # Paste sprite
    canvas.paste(img, (paste_x, paste_y), img)

    return canvas

def normalize_sprite(input_path, output_path, config=None):
    """Full normalization pipeline"""
    if config is None:
        config = load_config()

    norm = config["normalization"]

    img = Image.open(input_path)

    # 1. Background removal and cleanup
    img = remove_background(img)

    # 2. Trim transparent margins
    img = trim_transparent_margins(img)

    # 3. Quantize palette
    if norm["palette_max_colors"]:
        img = quantize_palette(img, norm["palette_max_colors"])

    # 4. Recenter to canvas with baseline
    img = recenter_to_baseline(
        img,
        norm["canvas_w"],
        norm["canvas_h"],
        norm["baseline_y"],
        norm["target_char_height_px"]
    )

    # Save with full alpha
    img.save(output_path, "PNG", optimize=True)

    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: normalize_sprite.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    normalize_sprite(input_path, output_path)
    print(f"Normalized: {output_path}")

if __name__ == "__main__":
    main()
