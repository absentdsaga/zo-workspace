#!/usr/bin/env python3
"""
NFT Character to Chrono Trigger Sprite Converter
Converts 3D-rendered NFT characters to pixel art sprites in CT style
"""

import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path
import json

# Chrono Trigger Color Palettes
CT_PALETTES = {
    "warm": [
        (139, 69, 19),    # Dark Brown
        (184, 105, 43),   # Medium Brown
        (217, 132, 61),   # Light Brown
        (240, 161, 85),   # Bright Orange
        (255, 181, 112),  # Highlight Orange
        (184, 134, 11),   # Dark Gold
        (255, 215, 0),    # Gold
        (255, 237, 78),   # Bright Gold
        (62, 39, 35),     # Shadow
        (255, 255, 255),  # White
        (224, 224, 224),  # Light Gray
        (0, 0, 0),        # Black
        (33, 33, 33),     # Dark Gray
        (255, 107, 157),  # Pink accent
    ],
    "cool": [
        (74, 20, 140),    # Dark Purple
        (106, 27, 154),   # Medium Purple
        (142, 36, 170),   # Light Purple
        (171, 71, 188),   # Bright Purple
        (224, 224, 224),  # Light Gray
        (255, 255, 255),  # White
        (184, 134, 11),   # Dark Gold
        (255, 215, 0),    # Gold
        (255, 237, 78),   # Bright Gold
        (0, 230, 118),    # Glow Green
        (105, 240, 174),  # Bright Glow
        (0, 0, 0),        # Black
        (26, 26, 26),     # Dark Gray
        (232, 220, 199),  # Bone
    ],
    "tech": [
        (0, 0, 0),        # Black
        (26, 26, 26),     # Very Dark Gray
        (44, 44, 44),     # Dark Gray
        (61, 61, 61),     # Medium Dark
        (66, 66, 66),     # Medium Gray
        (97, 97, 97),     # Light Gray
        (117, 117, 117),  # Very Light Gray
        (0, 229, 255),    # Cyan Neon
        (29, 233, 182),   # Green Neon
        (255, 110, 64),   # Orange Neon
        (255, 87, 34),    # Red Eyes
        (255, 112, 67),   # Light Eyes
        (255, 215, 0),    # Gold accent
        (255, 255, 255),  # White
    ],
    "rainbow": [
        (255, 23, 68),    # Red
        (255, 111, 0),    # Orange
        (255, 235, 59),   # Yellow
        (0, 230, 118),    # Green
        (41, 121, 255),   # Blue
        (156, 39, 176),   # Purple
        (0, 0, 0),        # Black
        (255, 255, 255),  # White
        (224, 224, 224),  # Light Gray
        (255, 215, 0),    # Gold
        (33, 33, 33),     # Dark Gray
    ],
    "shiba": [
        (245, 222, 179),  # Cream
        (222, 184, 135),  # Tan
        (210, 105, 30),   # Dark Tan
        (139, 69, 19),    # Brown
        (0, 0, 0),        # Black
        (26, 26, 26),     # Dark Gray
        (44, 44, 44),     # Leather Dark
        (139, 0, 0),      # Dark Red
        (178, 34, 34),    # Medium Red
        (220, 20, 60),    # Bright Red
        (192, 192, 192),  # Silver
        (232, 232, 232),  # Light Silver
        (255, 255, 255),  # White
    ]
}


def get_dominant_colors(image, num_colors=5):
    """Extract dominant colors from image"""
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize for faster processing
    small = image.resize((50, 50))
    pixels = list(small.getdata())

    # Simple color clustering
    from collections import Counter
    color_counts = Counter(pixels)
    return [color for color, count in color_counts.most_common(num_colors)]


def select_palette(image):
    """Auto-select best CT palette based on character colors"""
    dominant = get_dominant_colors(image)

    # Analyze dominant colors
    has_purple = any(color[2] > color[0] and color[2] > color[1] for color in dominant)
    has_orange = any(color[0] > 150 and color[1] > 80 and color[2] < 100 for color in dominant)
    has_rainbow = len(set(dominant)) > 4
    is_dark = sum(sum(c) for c in dominant) / len(dominant) < 128 * 3

    if is_dark:
        return CT_PALETTES["tech"]
    elif has_purple:
        return CT_PALETTES["cool"]
    elif has_rainbow:
        return CT_PALETTES["rainbow"]
    elif has_orange:
        return CT_PALETTES["warm"]
    else:
        return CT_PALETTES["warm"]


def find_nearest_color(color, palette):
    """Find closest color in palette"""
    r, g, b = color[:3]
    min_dist = float('inf')
    nearest = palette[0]

    for p_color in palette:
        pr, pg, pb = p_color
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest = p_color

    return nearest


def apply_ct_palette(image, palette):
    """Reduce image to CT color palette"""
    if image.mode != 'RGB':
        image = image.convert('RGB')

    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if len(pixel) == 4 and pixel[3] == 0:  # Transparent
                continue
            nearest = find_nearest_color(pixel, palette)
            pixels[x, y] = nearest

    return image


def add_ct_outline(image):
    """Add black pixel outline (CT style)"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Create outline by finding edges
    alpha = image.split()[3]

    # Dilate alpha channel to create outline
    outline = alpha.filter(ImageFilter.MaxFilter(3))

    # Create black outline where dilated alpha exists but original doesn't
    result = image.copy()
    pixels = result.load()
    alpha_pixels = alpha.load()
    outline_pixels = outline.load()

    width, height = image.size
    for y in range(height):
        for x in range(width):
            if outline_pixels[x, y] > 0 and alpha_pixels[x, y] == 0:
                pixels[x, y] = (0, 0, 0, 255)

    return result


def pixelate_image(image, target_width=32, target_height=48):
    """Downscale to pixel art size with proper technique"""
    # Remove background if present
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Get bounding box of non-transparent pixels
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    # Calculate scaling to fit target while maintaining aspect ratio
    img_width, img_height = image.size
    scale = min(target_width / img_width, target_height / img_height)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    # Use NEAREST for pixel art look (no anti-aliasing)
    pixelated = image.resize((new_width, new_height), Image.NEAREST)

    # Center on target canvas
    result = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    result.paste(pixelated, (x_offset, y_offset))

    return result


def create_walk_animation(base_sprite, direction='down'):
    """Generate 4-frame walk cycle from base sprite"""
    frames = []
    width, height = base_sprite.size

    for i in range(4):
        frame = base_sprite.copy()
        pixels = frame.load()

        # Simple walk animation: alternate leg positions
        # This is a simplified version - real animation needs more work

        if i == 0:  # Left foot forward
            # Shift bottom-left pixels down slightly
            shift_legs(frame, left_forward=True)
        elif i == 1:  # Center
            # No shift
            pass
        elif i == 2:  # Right foot forward
            shift_legs(frame, left_forward=False)
        elif i == 3:  # Center
            # No shift
            pass

        frames.append(frame)

    return frames


def shift_legs(image, left_forward=True):
    """Shift leg pixels for walk animation"""
    pixels = image.load()
    width, height = image.size

    # Bottom 1/4 of sprite (legs)
    leg_start = int(height * 0.75)

    # This is simplified - would need character-specific logic
    for y in range(leg_start, height):
        for x in range(width):
            if pixels[x, y][3] > 0:  # Not transparent
                # Shift pixels slightly
                shift = 1 if left_forward else -1
                if x + shift >= 0 and x + shift < width:
                    # Simple pixel shifting (very basic animation)
                    pass

    return image


def create_sprite_sheet(frames_dict, output_path):
    """Create sprite sheet from direction frames"""
    # Assume all frames same size
    frame_width, frame_height = frames_dict['down'][0].size
    frames_per_direction = len(frames_dict['down'])

    # Layout: 4 rows (down, up, left, right), N frames per row
    sheet_width = frame_width * frames_per_direction
    sheet_height = frame_height * 4

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    directions = ['down', 'up', 'left', 'right']
    for row_idx, direction in enumerate(directions):
        if direction not in frames_dict:
            continue

        for frame_idx, frame in enumerate(frames_dict[direction]):
            x = frame_idx * frame_width
            y = row_idx * frame_height
            sheet.paste(frame, (x, y))

    sheet.save(output_path)
    print(f"✅ Saved sprite sheet: {output_path}")

    # Create JSON config
    config = {
        "frameWidth": frame_width,
        "frameHeight": frame_height,
        "startFrame": 0,
        "endFrame": frames_per_direction * 4 - 1,
        "margin": 0,
        "spacing": 0
    }

    config_path = output_path.replace('.png', '.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Saved config: {config_path}")


def convert_nft_to_sprite(input_path, output_dir, character_name, palette_name=None):
    """Main conversion function"""
    print(f"\n🎨 Converting: {character_name}")

    # Load image
    image = Image.open(input_path)
    print(f"   Loaded: {image.size} pixels")

    # Select palette
    if palette_name and palette_name in CT_PALETTES:
        palette = CT_PALETTES[palette_name]
    else:
        palette = select_palette(image)
        print(f"   Auto-selected palette")

    # Pixelate
    pixelated = pixelate_image(image, 32, 48)
    print(f"   Pixelated to: {pixelated.size}")

    # Apply CT palette
    styled = apply_ct_palette(pixelated, palette)
    print(f"   Applied CT color palette")

    # Add outline
    outlined = add_ct_outline(styled)
    print(f"   Added pixel outline")

    # Create animation frames
    frames = {
        'down': create_walk_animation(outlined, 'down'),
        'up': create_walk_animation(outlined, 'up'),
        'left': create_walk_animation(outlined, 'left'),
        'right': create_walk_animation(outlined, 'right'),
    }

    # Mirror left to create right (common pixel art technique)
    frames['right'] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames['left']]

    print(f"   Generated 4-direction animations")

    # Create output directory
    char_dir = Path(output_dir) / character_name
    char_dir.mkdir(parents=True, exist_ok=True)

    # Save individual frames
    for direction, frame_list in frames.items():
        for i, frame in enumerate(frame_list):
            frame_path = char_dir / f"{direction}-walk-{i}.png"
            frame.save(frame_path)

    # Create sprite sheet
    sheet_path = char_dir / f"{character_name}-sheet.png"
    create_sprite_sheet(frames, sheet_path)

    print(f"✨ Conversion complete!\n")
    return sheet_path


def process_character_set(set_image_path, output_dir):
    """Process a set of characters from a grid image"""
    print(f"\n📦 Processing character set: {set_image_path}")

    image = Image.open(set_image_path)
    width, height = image.size

    # Assume 3x2 grid (6 characters)
    char_width = width // 3
    char_height = height // 2

    characters = []
    for row in range(2):
        for col in range(3):
            x = col * char_width
            y = row * char_height
            char_img = image.crop((x, y, x + char_width, y + char_height))
            characters.append(char_img)

    # Process each character
    set_name = Path(set_image_path).stem.replace(' ', '-')
    for i, char_img in enumerate(characters):
        char_name = f"{set_name}-char{i+1}"

        # Save temp file
        temp_path = f"/tmp/{char_name}.png"
        char_img.save(temp_path)

        # Convert
        convert_nft_to_sprite(temp_path, output_dir, char_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nft-to-ct-sprite.py <input_image> [output_dir] [character_name] [palette]")
        print("\nPalettes: warm, cool, tech, rainbow, shiba")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    char_name = sys.argv[3] if len(sys.argv) > 3 else Path(input_path).stem
    palette = sys.argv[4] if len(sys.argv) > 4 else None

    # Check if it's a character set or single character
    if 'set' in input_path.lower():
        process_character_set(input_path, output_dir)
    else:
        convert_nft_to_sprite(input_path, output_dir, char_name, palette)

    print("\n🎉 All done! Sprites ready for spatial-worlds!")
