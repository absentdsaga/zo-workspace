#!/usr/bin/env python3
"""
VURT Creator Spotlight Generator
Usage:
  python3 generate-spotlight.py --name "DIRECTOR NAME" --show "Show Title" \
    --date "April 2026" --photo /path/to/headshot.jpg --out output.png

  python3 generate-spotlight.py --help
"""
import argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import sys

LOGO_PATH = "/home/workspace/vurt_logo_hires.png"
FONT_DIR  = "/usr/share/fonts/inter"

# Brand colors
BLACK      = (11, 11, 11)
GOLD       = (212, 166, 58)
WHITE      = (242, 242, 242)
GRAY       = (154, 154, 154)

def load_fonts():
    return {
        "bold":     ImageFont.truetype(f"{FONT_DIR}/Inter-Bold.ttf", 72),
        "semibold": ImageFont.truetype(f"{FONT_DIR}/Inter-Medium.ttf", 40),
        "label":    ImageFont.truetype(f"{FONT_DIR}/Inter-Medium.ttf", 28),
        "small":    ImageFont.truetype(f"{FONT_DIR}/Inter-Medium.ttf", 24),
    }

def extract_logo():
    logo_src = Image.open(LOGO_PATH).convert("RGBA")
    # Crop the logo rectangle from the hires source
    logo_crop = logo_src.crop((490, 320, 895, 545)).convert("RGBA")
    # Replace gray background with brand black, preserve gold V and white URT text
    arr = np.array(logo_crop, dtype=float)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    is_gray = (np.abs(r - g) < 18) & (np.abs(g - b) < 18) & (r > 185) & (r < 235)
    arr[is_gray.astype(bool), 0] = 11
    arr[is_gray.astype(bool), 1] = 11
    arr[is_gray.astype(bool), 2] = 11
    arr[:,:,3] = 255
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

def build_spotlight(name, show, date, photo_path, out_path, label="CREATOR SPOTLIGHT"):
    W, H = 1080, 1350  # 4:5 IG feed

    fonts = load_fonts()
    logo_clean = extract_logo()
    logo_final = logo_clean.resize((320, int(320 * logo_clean.height / logo_clean.width)), Image.LANCZOS)

    # Load headshot — boost brightness/contrast so face reads on dark bg
    from PIL import ImageEnhance
    headshot = Image.open(photo_path).convert("RGBA")
    r, g, b, a = headshot.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(1.25)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.1)
    r2, g2, b2 = rgb.split()
    headshot = Image.merge("RGBA", (r2, g2, b2, a))
    hw, hh = headshot.size
    photo_h = int(H * 0.74)
    scale = W / hw
    headshot_resized = headshot.resize((W, int(hh * scale)), Image.LANCZOS)
    headshot_crop = headshot_resized.crop((0, 0, W, photo_h))

    # Canvas
    canvas = Image.new("RGBA", (W, H), BLACK + (255,))
    canvas.paste(headshot_crop, (0, 0), headshot_crop)

    # Gradient overlay: transparent at top ~68% of photo, full black by bottom
    grad_start = int(photo_h * 0.91)
    ov = np.zeros((H, W, 4), dtype=np.uint8)
    ov[:, :, :3] = [11, 11, 11]
    for y in range(H):
        if y < grad_start:
            alpha = 0
        elif y < photo_h:
            alpha = int(255 * (y - grad_start) / (photo_h - grad_start))
        else:
            alpha = 255
        ov[y, :, 3] = alpha
    canvas = Image.alpha_composite(canvas, Image.fromarray(ov, 'RGBA'))

    # Text
    draw = ImageDraw.Draw(canvas)
    tx = 72
    rule_y = photo_h - 32

    # Gold rule
    draw.rectangle([(tx, rule_y), (tx + 80, rule_y + 3)], fill=GOLD)

    # Label
    label_y = rule_y + 18
    draw.text((tx, label_y), label, font=fonts["label"], fill=GOLD)

    # Name
    name_y = label_y + 46
    draw.text((tx, name_y), name.upper(), font=fonts["bold"], fill=WHITE)

    # Show title
    show_y = name_y + 88
    draw.text((tx, show_y), show, font=fonts["semibold"], fill=GRAY)

    # Streaming line
    sub_y = show_y + 60
    draw.text((tx, sub_y), f"Streaming on VURT · {date}", font=fonts["small"], fill=GRAY)

    # VURT logo bottom right
    lw, lh = logo_final.size
    canvas.paste(logo_final, (W - lw - 52, H - lh - 52), logo_final)

    canvas.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Saved: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a VURT Creator Spotlight graphic")
    parser.add_argument("--name",    required=True,  help="Director/creator full name")
    parser.add_argument("--show",    required=True,  help="Show/series title")
    parser.add_argument("--date",    required=True,  help="Streaming date (e.g. 'April 2026')")
    parser.add_argument("--photo",   required=True,  help="Path to headshot image (JPG/PNG)")
    parser.add_argument("--out",     required=True,  help="Output PNG path")
    parser.add_argument("--label",   default="CREATOR SPOTLIGHT", help="Label text (default: CREATOR SPOTLIGHT)")
    args = parser.parse_args()

    if not os.path.exists(args.photo):
        print(f"Error: photo not found: {args.photo}", file=sys.stderr)
        sys.exit(1)

    build_spotlight(args.name, args.show, args.date, args.photo, args.out, args.label)

if __name__ == "__main__":
    main()
