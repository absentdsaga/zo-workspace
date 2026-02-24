#!/usr/bin/env python3
"""
Slice an RPG Maker / Pipoya format sprite sheet into the game engine's format.

RPG Maker layout (per character, 4 rows down the sheet):
  Row 0: walk-down  (3 frames: L-stride, center, R-stride)
  Row 1: walk-left  (3 frames)
  Row 2: walk-right (3 frames)
  Row 3: walk-up    (3 frames)

Engine format (256x256, 4x4 grid, 64x64 per cell):
  Row 0 (frames  0-3): south (walk-down,  4 frames looped from 3)
  Row 1 (frames  4-7): north (walk-up,    4 frames looped from 3)
  Row 2 (frames  8-11): west  (walk-left,  4 frames looped from 3)
  Row 3 (frames 12-15): east  (walk-right, 4 frames looped from 3)

Usage:
  python3 slice_rpgmaker_sheet.py <sheet.png> <char_row> <output_id>

  char_row: which character in the sheet (0=first, 1=second, etc.)
  Each character occupies 4 rows in the source sheet.

Example:
  python3 slice_rpgmaker_sheet.py assets/sprites/opengameart/rpg-classes-32x32.png 0 pixel_hero
"""
import sys
from pathlib import Path
from PIL import Image

FRAME_W = 32   # source frame size
FRAME_H = 32
OUT_FRAME = 64  # output frame size (2x upscale)
SHEET_COLS = 3  # RPG Maker: 3 frames per direction
SHEET_ROWS_PER_CHAR = 4  # 4 directions per character

# RPG Maker character block size
CHAR_BLOCK_W = FRAME_W * SHEET_COLS   # 96px
CHAR_BLOCK_H = FRAME_H * SHEET_ROWS_PER_CHAR  # 128px

# RPG Maker row order within a character block → engine direction
# RPG Maker rows: 0=down, 1=left, 2=right, 3=up
# Engine rows:    0=south, 1=north, 2=west, 3=east
RPGMAKER_TO_ENGINE = {
    'south': 0,  # RPG Maker row 0 = down
    'north': 3,  # RPG Maker row 3 = up
    'west':  1,  # RPG Maker row 1 = left
    'east':  2,  # RPG Maker row 2 = right
}
ENGINE_DIR_ORDER = ['south', 'north', 'west', 'east']


def slice_character(src_path, char_index, output_id):
    src = Image.open(src_path).convert('RGBA')
    src_w, src_h = src.size

    # Characters are laid out left-to-right, top-to-bottom in 96x128 blocks
    chars_per_row = src_w // CHAR_BLOCK_W
    char_col = char_index % chars_per_row
    char_row = char_index // chars_per_row

    char_x_start = char_col * CHAR_BLOCK_W
    char_y_start = char_row * CHAR_BLOCK_H

    # Build 256x256 output sheet
    out_size = OUT_FRAME * 4
    sheet = Image.new('RGBA', (out_size, out_size), (0, 0, 0, 0))

    for engine_row, direction in enumerate(ENGINE_DIR_ORDER):
        rpgmaker_row = RPGMAKER_TO_ENGINE[direction]
        src_y = char_y_start + rpgmaker_row * FRAME_H


        # RPG Maker has 3 frames: center(idle), left-stride, right-stride
        # Frame order in RPG Maker: col 0=left-stride, col 1=center, col 2=right-stride
        # Remap to 4-frame walk cycle: center, left, center, right (smooth loop)
        rpgmaker_frames = [1, 0, 1, 2]  # center, left, center, right

        for engine_col, rm_col in enumerate(rpgmaker_frames):
            src_x = char_x_start + rm_col * FRAME_W
            frame = src.crop((src_x, src_y, src_x + FRAME_W, src_y + FRAME_H))

            # Remove magenta background (RPG Maker uses #FF00FF as transparency)
            frame_data = frame.load()
            for y in range(FRAME_H):
                for x in range(FRAME_W):
                    r, g, b, a = frame_data[x, y]
                    if r > 200 and g < 30 and b > 200:
                        frame_data[x, y] = (0, 0, 0, 0)

            # Scale up 2x with nearest-neighbor (preserve pixel art crispness)
            frame = frame.resize((OUT_FRAME, OUT_FRAME), Image.NEAREST)

            # Paste into sheet
            dest_x = engine_col * OUT_FRAME
            dest_y = engine_row * OUT_FRAME
            sheet.paste(frame, (dest_x, dest_y), frame)

        print(f"  {direction}: 4 frames sliced from RPG Maker row {rpgmaker_row}")

    # Save to game assets
    game_dir = Path(__file__).parent.parent / 'assets' / 'sprites' / 'nft-characters-xxl' / output_id
    game_dir.mkdir(parents=True, exist_ok=True)
    out_path = game_dir / f'{output_id}-sheet.png'
    sheet.save(out_path, 'PNG')
    print(f"\nSaved: {out_path}")
    print(f"Sheet: {out_size}x{out_size}, 4x4 grid, {OUT_FRAME}x{OUT_FRAME} per frame")
    return out_path


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 slice_rpgmaker_sheet.py <sheet.png> <char_row> <output_id>")
        print("Example: python3 slice_rpgmaker_sheet.py assets/sprites/opengameart/rpg-classes-32x32.png 0 pixel_hero")
        sys.exit(1)

    src = sys.argv[1]
    char_row = int(sys.argv[2])
    output_id = sys.argv[3]

    print(f"Slicing character {char_row} from {src} → {output_id}")
    slice_character(src, char_row, output_id)
