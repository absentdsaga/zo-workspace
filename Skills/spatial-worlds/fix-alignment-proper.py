#!/usr/bin/env python3
"""
Properly fix sprite alignment by finding the lowest pixel in each frame
and ensuring all frames have feet at the exact same Y position.
"""

from PIL import Image
import os
import glob

def find_lowest_pixel(img):
    """Find the Y coordinate of the lowest non-transparent pixel."""
    pixels = img.load()
    width, height = img.size

    # Scan from bottom up
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if len(pixels[x, y]) == 4:  # RGBA
                if pixels[x, y][3] > 0:  # Has alpha
                    return y
            else:  # RGB
                if pixels[x, y] != (0, 0, 0):  # Not black
                    return y
    return height - 1

def align_sprite_frames(frames):
    """Align all frames so feet are at same Y position."""
    if not frames:
        return

    # Load all images
    images = [(f, Image.open(f).convert('RGBA')) for f in frames]

    # Find lowest pixel in each frame
    lowest_points = [(f, find_lowest_pixel(img), img) for f, img in images]

    # Find the maximum lowest point (most bottom)
    max_lowest = max(lp[1] for lp in lowest_points)

    print(f"  Lowest pixels: {[lp[1] for lp in lowest_points]}")
    print(f"  Target alignment: {max_lowest}")

    # Align each frame
    for filepath, lowest, img in lowest_points:
        if lowest == max_lowest:
            continue  # Already aligned

        # Calculate how much to shift down
        shift = max_lowest - lowest

        # Create new image with same size
        new_img = Image.new('RGBA', img.size, (0, 0, 0, 0))

        # Paste old image shifted down
        new_img.paste(img, (0, shift))

        # Save
        new_img.save(filepath)
        print(f"    Shifted {os.path.basename(filepath)} down by {shift}px")

def process_character_set(char_dir):
    """Process all frames for one character set."""
    print(f"\nProcessing: {os.path.basename(char_dir)}")

    # Get all animation directions
    directions = ['down-walk', 'up-walk', 'left-walk', 'right-walk']

    for direction in directions:
        frames = sorted(glob.glob(os.path.join(char_dir, f"{direction}-*.png")))
        if frames:
            print(f"  Aligning {direction}...")
            align_sprite_frames(frames)

    # Regenerate sprite sheet
    print(f"  Regenerating sprite sheet...")
    from subprocess import run
    char_name = os.path.basename(char_dir)

    run([
        'montage',
        *glob.glob(os.path.join(char_dir, 'right-walk-*.png')),
        *glob.glob(os.path.join(char_dir, 'left-walk-*.png')),
        *glob.glob(os.path.join(char_dir, 'up-walk-*.png')),
        *glob.glob(os.path.join(char_dir, 'down-walk-*.png')),
        '-tile', '4x4',
        '-geometry', '32x48+0+0',
        '-background', 'none',
        os.path.join(char_dir, f'{char_name}-sheet.png')
    ], check=True)

    print(f"  ✓ Fixed {char_name}")

def main():
    sprite_dir = "/home/workspace/Skills/spatial-worlds/assets/sprites/nft-characters"

    print("Fixing sprite alignment by measuring actual pixel positions...")

    # Process all character directories
    for char_dir in sorted(glob.glob(os.path.join(sprite_dir, "set*-char*"))):
        if os.path.isdir(char_dir):
            process_character_set(char_dir)

    print("\n✓ All sprites fixed!")

if __name__ == '__main__':
    main()
