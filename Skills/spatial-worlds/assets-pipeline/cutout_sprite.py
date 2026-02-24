#!/usr/bin/env python3
"""
Background removal using rembg
Converts RGB images to RGBA with transparent background
"""

import sys
from pathlib import Path
from PIL import Image
from rembg import remove

def remove_background(input_path, output_path):
    """Remove background and output RGBA PNG"""
    print(f"Removing background: {input_path.name}")
    
    # Open input image
    input_img = Image.open(input_path)
    
    # Remove background
    output_img = remove(input_img)
    
    # Ensure RGBA mode
    if output_img.mode != 'RGBA':
        output_img = output_img.convert('RGBA')
    
    # Save with transparency
    output_img.save(output_path, 'PNG')
    
    print(f"  ✓ Saved: {output_path.name}")
    
    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: cutout_sprite.py <input_image> <output_image>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    remove_background(input_path, output_path)

if __name__ == "__main__":
    main()
