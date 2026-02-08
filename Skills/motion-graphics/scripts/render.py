#!/usr/bin/env python3
"""Render a Remotion composition to video."""

import argparse
import subprocess
import sys
import os
from pathlib import Path

STUDIO_PATH = "/home/workspace/motion-graphics-studio"

def main():
    parser = argparse.ArgumentParser(description="Render a Remotion composition")
    parser.add_argument("composition", help="Composition ID to render")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: out/<composition>.mp4)")
    parser.add_argument("--codec", "-c", default="h264", choices=["h264", "h265", "vp8", "vp9", "gif", "png"], help="Output codec")
    parser.add_argument("--quality", "-q", type=int, default=80, help="Quality (0-100, for lossy codecs)")
    parser.add_argument("--scale", "-s", type=float, default=1.0, help="Scale factor (0.5 = half size)")
    
    args = parser.parse_args()
    
    if not os.path.exists(STUDIO_PATH):
        print(f"Error: Studio not found at {STUDIO_PATH}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output = args.output
    else:
        ext = "gif" if args.codec == "gif" else "png" if args.codec == "png" else "mp4" if args.codec in ["h264", "h265"] else "webm"
        output = f"out/{args.composition}.{ext}"
    
    # Ensure output directory exists
    output_path = Path(STUDIO_PATH) / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = [
        "bun", "run", "render",
        args.composition,
        "--output", output,
        "--codec", args.codec,
    ]
    
    if args.codec not in ["png"]:
        cmd.extend(["--crf", str(100 - args.quality)])  # CRF is inverse of quality
    
    if args.scale != 1.0:
        cmd.extend(["--scale", str(args.scale)])
    
    print(f"Rendering {args.composition} to {output}...")
    print(f"Codec: {args.codec}, Quality: {args.quality}, Scale: {args.scale}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=STUDIO_PATH,
            check=True
        )
        print()
        print(f"✅ Rendered to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
