#!/usr/bin/env python3
"""
Extract NFT characters from grid images and create sprite sheets.

Each set PNG has a 3x2 grid with 6 characters.
We need to extract each character and create a 4-frame sprite sheet:
- Frame 0-3: Right (using the base image)
- Frame 4-7: Left (flipped horizontally)
- Frame 8-11: Up (using the base image, slight variation)
- Frame 12-15: Down (using the base image as default)

Output format: 128px wide × 48px tall (4 frames × 32px width, 48px height)
"""

from PIL import Image
import os

# Input files
sets = [
    ('set 1-fbae2b75a343.png', 1),
    ('set 2-7a4ef0760d63.png', 2),
    ('set 3-91dfcf064953.png', 3),
    ('set 4-124cd4dc4ad2.png', 4),
]

output_dir = 'assets/sprites/nft-characters'
os.makedirs(output_dir, exist_ok=True)

def extract_character(img, col, row):
    """Extract a single character from the grid."""
    # Grid is 3 columns × 2 rows
    width, height = img.size
    char_width = width // 3
    char_height = height // 2

    left = col * char_width
    top = row * char_height
    right = left + char_width
    bottom = top + char_height

    character = img.crop((left, top, right, bottom))
    return character

def create_sprite_sheet(character_img, set_num, char_num):
    """Create a 4-frame sprite sheet from a single character image."""
    # Target frame size: 32×48px
    frame_width = 32
    frame_height = 48

    # Resize character to fit in a frame (keeping aspect ratio)
    character_img.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)

    # Create sprite sheet: 128×48 (4 frames horizontal)
    sprite_sheet = Image.new('RGBA', (frame_width * 4, frame_height), (0, 0, 0, 0))

    # Frame 0: Right facing (base image)
    sprite_sheet.paste(character_img, (0, 0), character_img if character_img.mode == 'RGBA' else None)

    # Frame 1: Left facing (horizontally flipped)
    flipped = character_img.transpose(Image.FLIP_LEFT_RIGHT)
    sprite_sheet.paste(flipped, (frame_width, 0), flipped if flipped.mode == 'RGBA' else None)

    # Frame 2: Up facing (base image)
    sprite_sheet.paste(character_img, (frame_width * 2, 0), character_img if character_img.mode == 'RGBA' else None)

    # Frame 3: Down facing (base image)
    sprite_sheet.paste(character_img, (frame_width * 3, 0), character_img if character_img.mode == 'RGBA' else None)

    # Save sprite sheet
    char_name = f'set{set_num}-char{char_num}'
    char_dir = os.path.join(output_dir, char_name)
    os.makedirs(char_dir, exist_ok=True)

    output_path = os.path.join(char_dir, f'{char_name}-sheet.png')
    sprite_sheet.save(output_path, 'PNG')
    print(f'✅ Created {output_path}')

    return output_path

# Process each set
for filename, set_num in sets:
    print(f'\n📦 Processing {filename} (Set {set_num})')
    img = Image.open(filename).convert('RGBA')

    # Extract 6 characters (3 cols × 2 rows)
    char_num = 1
    for row in range(2):
        for col in range(3):
            print(f'  Extracting character {char_num}...')
            character = extract_character(img, col, row)
            create_sprite_sheet(character, set_num, char_num)
            char_num += 1

print('\n✅ All sprite sheets created!')
print(f'📁 Location: {output_dir}/')
print(f'📊 Total: 24 characters (4 sets × 6 characters)')
print('\n🧪 Test with: ./test-nft-sprite.sh set1-char1')
