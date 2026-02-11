#!/usr/bin/env python3
"""Analyze sprite positions in two screenshots to detect sync offset."""

import sys
from PIL import Image
import numpy as np

def find_sprite_center(img_path):
    """Find the brightest sprite (player) in the image."""
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)
    
    # Find all bright pixels (potential sprites)
    # Sprites are typically brighter than background
    brightness = arr.mean(axis=2)
    threshold = brightness.mean() + brightness.std()
    bright_mask = brightness > threshold
    
    # Find center of mass of bright pixels
    y_coords, x_coords = np.where(bright_mask)
    if len(x_coords) == 0:
        return None
    
    center_x = int(x_coords.mean())
    center_y = int(y_coords.mean())
    
    return (center_x, center_y)

def compare_screenshots(img1_path, img2_path):
    """Compare two screenshots and measure sprite offset."""
    pos1 = find_sprite_center(img1_path)
    pos2 = find_sprite_center(img2_path)
    
    if pos1 is None or pos2 is None:
        print("❌ Could not find sprites in images")
        return
    
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    distance = (dx**2 + dy**2)**0.5
    
    print(f"Client 1 sprite center: {pos1}")
    print(f"Client 2 sprite center: {pos2}")
    print(f"Offset: dx={dx}px, dy={dy}px")
    print(f"Distance: {distance:.1f}px")
    
    if distance < 5:
        print("✅ PERFECT SYNC (< 5px offset)")
    elif distance < 20:
        print("⚠️  Minor desync (5-20px)")
    else:
        print("❌ Major desync (> 20px)")
    
    return dx, dy, distance

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: analyze-sprite-sync.py <client1.png> <client2.png>")
        sys.exit(1)
    
    compare_screenshots(sys.argv[1], sys.argv[2])
