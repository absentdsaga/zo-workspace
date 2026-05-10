"""
VURT Miami DOOH billboards — 840x400px static, no QR, no motion.
Two campaigns × two variants = 4 PNGs.
Designed at 4x (3360x1600) and downsampled for crisp LED rendering.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path("/home/workspace/Documents/VURT-Billboard-Miami")
OUT.mkdir(exist_ok=True, parents=True)

SCALE = 4
W, H = 840 * SCALE, 400 * SCALE

# Brand tokens (from VURT-master.md)
BLACK = "#0B0B0B"
GOLD = "#D4A63A"
GOLD_HI = "#F5D27A"
WHITE = "#F2F2F2"
GRAY = "#9A9A9A"

INTER_BOLD = "/usr/share/fonts/inter/Inter-Bold.ttf"
INTER_DISPLAY = "/usr/share/fonts/inter/Inter.ttc"  # index 5 = Display Bold
PLEX_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def font(path, size, index=0):
    if path.endswith(".ttc"):
        return ImageFont.truetype(path, size, index=index)
    return ImageFont.truetype(path, size)

def text_w(draw, txt, fnt):
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def export(img, name):
    final = img.resize((840, 400), Image.LANCZOS)
    final.save(OUT / f"{name}.png", optimize=True)
    img.save(OUT / f"{name}@4x.png", optimize=True)
    print(f"  {name}.png  +  {name}@4x.png")

# =============================================================
# CAMPAIGN 1 — OPENING NIGHT (5/26 – 5/29)
# =============================================================

def c1_variant_a():
    """V1-A: 'VURT IS HERE' hero, date strip below, URL bottom right."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Subtle gold edge accent (top stripe)
    d.rectangle([(0, 0), (W, 6 * SCALE)], fill=GOLD)

    # Hero line — VURT IS HERE
    hero_fnt = font(INTER_BOLD, 165 * SCALE // 2)
    hero = "VURT IS HERE"
    tw, th = text_w(d, hero, hero_fnt)
    d.text(((W - tw) / 2, 80 * SCALE), hero, font=hero_fnt, fill=WHITE)

    # Divider
    div_y = 200 * SCALE
    d.line([(W * 0.32, div_y), (W * 0.68, div_y)], fill=GOLD, width=3 * SCALE // 2)

    # Date + venue strip
    sub_fnt = font(INTER_BOLD, 56 * SCALE // 2)
    sub = "5.29.26  ·  GATES HOTEL  ·  MIAMI BEACH"
    sw, sh = text_w(d, sub, sub_fnt)
    d.text(((W - sw) / 2, 220 * SCALE), sub, font=sub_fnt, fill=GOLD_HI)

    # URL — mono, bottom
    url_fnt = font(PLEX_MONO, 50 * SCALE // 2)
    url = "myvurt.com/miami"
    uw, uh = text_w(d, url, url_fnt)
    d.text(((W - uw) / 2, 310 * SCALE), url, font=url_fnt, fill=WHITE)

    export(img, "C1-A_VURT-IS-HERE")

def c1_variant_b():
    """V1-B: Date-led — huge '5.29' left, event copy stacked right."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Big date — left side
    date_fnt = font(INTER_BOLD, 280 * SCALE // 2)
    date_txt = "5.29"
    dx = 60 * SCALE
    dy = 70 * SCALE
    d.text((dx, dy), date_txt, font=date_fnt, fill=GOLD)

    # Vertical divider
    div_x = 380 * SCALE
    d.line([(div_x, 80 * SCALE), (div_x, 320 * SCALE)], fill=WHITE, width=2 * SCALE)

    # Right column copy
    rx = 410 * SCALE
    kicker_fnt = font(INTER_BOLD, 36 * SCALE // 2)
    d.text((rx, 90 * SCALE), "OPENING NIGHT", font=kicker_fnt, fill=GOLD_HI)

    brand_fnt = font(INTER_BOLD, 92 * SCALE // 2)
    d.text((rx, 130 * SCALE), "VURT", font=brand_fnt, fill=WHITE)

    venue_fnt = font(INTER_BOLD, 38 * SCALE // 2)
    d.text((rx, 215 * SCALE), "GATES HOTEL", font=venue_fnt, fill=WHITE)
    d.text((rx, 252 * SCALE), "MIAMI BEACH", font=venue_fnt, fill=GRAY)

    url_fnt = font(PLEX_MONO, 38 * SCALE // 2)
    d.text((rx, 305 * SCALE), "myvurt.com/miami", font=url_fnt, fill=GOLD)

    export(img, "C1-B_DATE-LED")

# =============================================================
# CAMPAIGN 2 — ALWAYS-ON (5/30 – 5/31)
# =============================================================

def c2_variant_a():
    """V2-A: 'BUILT FOR THE CULTURE.' hero centered, URL bottom."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Top accent
    d.rectangle([(0, 0), (W, 6 * SCALE)], fill=GOLD)

    # VURT brand mark — small, top
    brand_fnt = font(INTER_BOLD, 44 * SCALE // 2)
    bw, bh = text_w(d, "VURT", brand_fnt)
    d.text(((W - bw) / 2, 50 * SCALE), "VURT", font=brand_fnt, fill=GOLD)

    # Hero — two lines
    line1_fnt = font(INTER_BOLD, 95 * SCALE // 2)
    line2_fnt = font(INTER_BOLD, 95 * SCALE // 2)
    line1 = "VERTICAL CINEMA."
    line2 = "BUILT FOR THE CULTURE."
    l1w, l1h = text_w(d, line1, line1_fnt)
    l2w, l2h = text_w(d, line2, line2_fnt)
    d.text(((W - l1w) / 2, 110 * SCALE), line1, font=line1_fnt, fill=WHITE)
    d.text(((W - l2w) / 2, 175 * SCALE), line2, font=line2_fnt, fill=GOLD_HI)

    # Bottom strip — Always free + URL
    sub_fnt = font(INTER_BOLD, 38 * SCALE // 2)
    url_fnt = font(PLEX_MONO, 38 * SCALE // 2)
    free_txt = "ALWAYS FREE TO WATCH"
    url_txt = "myvurt.com"
    fw, _ = text_w(d, free_txt, sub_fnt)
    uw, _ = text_w(d, url_txt, url_fnt)
    sep = "   ·   "
    sw, _ = text_w(d, sep, sub_fnt)
    total = fw + sw + uw
    bx = (W - total) / 2
    by = 320 * SCALE
    d.text((bx, by), free_txt, font=sub_fnt, fill=WHITE)
    d.text((bx + fw, by), sep, font=sub_fnt, fill=GRAY)
    d.text((bx + fw + sw, by), url_txt, font=url_fnt, fill=GOLD)

    export(img, "C2-A_BUILT-FOR-THE-CULTURE")

def c2_variant_b():
    """V2-B: Logo-left poster — VURT mark dominates left, statement right."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Big VURT mark left
    mark_fnt = font(INTER_BOLD, 220 * SCALE // 2)
    d.text((40 * SCALE, 95 * SCALE), "VURT", font=mark_fnt, fill=GOLD)

    # Right column
    div_x = 410 * SCALE
    d.line([(div_x, 80 * SCALE), (div_x, 320 * SCALE)], fill=WHITE, width=2 * SCALE)

    rx = 440 * SCALE
    kicker_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d.text((rx, 95 * SCALE), "VERTICAL CINEMA", font=kicker_fnt, fill=GOLD_HI)

    statement_fnt = font(INTER_BOLD, 62 * SCALE // 2)
    d.text((rx, 135 * SCALE), "BUILT FOR", font=statement_fnt, fill=WHITE)
    d.text((rx, 178 * SCALE), "THE CULTURE.", font=statement_fnt, fill=WHITE)

    sub_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d.text((rx, 252 * SCALE), "ALWAYS FREE TO WATCH", font=sub_fnt, fill=GOLD_HI)

    url_fnt = font(PLEX_MONO, 30 * SCALE // 2)
    d.text((rx, 295 * SCALE), "myvurt.com", font=url_fnt, fill=WHITE)

    export(img, "C2-B_LOGO-LEFT")

# =============================================================
# Phone-frame device — the structural image for VURT OOH
# =============================================================

def draw_phone(d, img, x, y, w, h, poster_top_color, poster_bot_color,
               title_top, title_bot, subtitle):
    """Draw a 9:16 phone frame with a fake show poster inside.
    x, y, w, h are top-left and dimensions in 4x pixels."""
    border = 4 * SCALE
    radius = 14 * SCALE

    # Outer frame (gold)
    d.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=GOLD)
    # Inner screen (poster) — gradient
    inner_x = x + border
    inner_y = y + border
    inner_w = w - 2 * border
    inner_h = h - 2 * border
    poster = Image.new("RGB", (inner_w, inner_h), poster_top_color)
    pd = ImageDraw.Draw(poster)
    for i in range(inner_h):
        t = i / inner_h
        r = int(int(poster_top_color[1:3], 16) * (1 - t) + int(poster_bot_color[1:3], 16) * t)
        g = int(int(poster_top_color[3:5], 16) * (1 - t) + int(poster_bot_color[3:5], 16) * t)
        b = int(int(poster_top_color[5:7], 16) * (1 - t) + int(poster_bot_color[5:7], 16) * t)
        pd.line([(0, i), (inner_w, i)], fill=(r, g, b))

    # Mask for rounded corners on the poster
    mask = Image.new("L", (inner_w, inner_h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([(0, 0), (inner_w, inner_h)], radius=radius - border, fill=255)
    img.paste(poster, (inner_x, inner_y), mask)

    # Notch / dynamic island
    pd2 = ImageDraw.Draw(img)
    notch_w = inner_w * 0.3
    notch_h = 10 * SCALE
    notch_x = inner_x + (inner_w - notch_w) / 2
    notch_y = inner_y + 10 * SCALE
    pd2.rounded_rectangle(
        [(notch_x, notch_y), (notch_x + notch_w, notch_y + notch_h)],
        radius=notch_h / 2, fill=BLACK,
    )

    # Show poster type — title
    title_fnt = font(INTER_BOLD, 38 * SCALE // 2)
    tw1, th1 = text_w(pd2, title_top, title_fnt)
    tw2, th2 = text_w(pd2, title_bot, title_fnt)
    title_y = inner_y + inner_h * 0.32
    pd2.text((inner_x + (inner_w - tw1) / 2, title_y), title_top, font=title_fnt, fill=WHITE)
    pd2.text((inner_x + (inner_w - tw2) / 2, title_y + th1 + 6 * SCALE), title_bot, font=title_fnt, fill=WHITE)

    # Subtitle (e.g. "VURT ORIGINAL")
    sub_fnt = font(INTER_BOLD, 16 * SCALE // 2)
    sw, sh = text_w(pd2, subtitle, sub_fnt)
    pd2.text((inner_x + (inner_w - sw) / 2, inner_y + inner_h - sh - 14 * SCALE),
             subtitle, font=sub_fnt, fill=GOLD_HI)


# =============================================================
# CAMPAIGN 1 — Opening Night WITH IMAGERY
# =============================================================

def c1_variant_c():
    """V1-C: Phone frame left + event copy right. Tells you VURT is an app AND when the party is."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Top accent
    d.rectangle([(0, 0), (W, 5 * SCALE)], fill=GOLD)

    # Phone frame — left third
    ph_w = 170 * SCALE
    ph_h = 320 * SCALE  # ~9:16-ish at this size, slightly wider for legibility
    ph_x = 50 * SCALE
    ph_y = (H - ph_h) // 2
    draw_phone(d, img, ph_x, ph_y, ph_w, ph_h,
               "#1A1A1A", "#0B0B0B",
               "KARMA", "IN HEELS", "VURT ORIGINAL")

    # Right column copy
    d2 = ImageDraw.Draw(img)
    rx = 280 * SCALE
    kicker_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d2.text((rx, 70 * SCALE), "OPENING NIGHT", font=kicker_fnt, fill=GOLD_HI)

    hero_fnt = font(INTER_BOLD, 105 * SCALE // 2)
    d2.text((rx, 105 * SCALE), "VURT IS", font=hero_fnt, fill=WHITE)
    d2.text((rx, 165 * SCALE), "HERE.", font=hero_fnt, fill=GOLD)

    sub_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d2.text((rx, 250 * SCALE), "5.29.26  ·  GATES HOTEL", font=sub_fnt, fill=WHITE)
    d2.text((rx, 285 * SCALE), "MIAMI BEACH", font=sub_fnt, fill=GRAY)

    url_fnt = font(PLEX_MONO, 30 * SCALE // 2)
    d2.text((rx, 330 * SCALE), "myvurt.com/miami", font=url_fnt, fill=GOLD)

    export(img, "C1-C_PHONE-EVENT")


# =============================================================
# CAMPAIGN 2 — Always-on WITH IMAGERY
# =============================================================

def c2_variant_c():
    """V2-C: Phone-dominant. Tells you 'this is a vertical phone-native streaming app' in 1 second."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Phone frame — left side, dominant
    ph_w = 200 * SCALE
    ph_h = 360 * SCALE
    ph_x = 40 * SCALE
    ph_y = (H - ph_h) // 2
    draw_phone(d, img, ph_x, ph_y, ph_w, ph_h,
               "#3A1F1F", "#0B0B0B",
               "COME BACK", "DAD", "VURT ORIGINAL")

    # Right column
    d2 = ImageDraw.Draw(img)
    rx = 295 * SCALE

    # VURT mark
    brand_fnt = font(INTER_BOLD, 90 * SCALE // 2)
    d2.text((rx, 65 * SCALE), "VURT", font=brand_fnt, fill=GOLD)

    # Statement
    state_fnt = font(INTER_BOLD, 50 * SCALE // 2)
    d2.text((rx, 155 * SCALE), "VERTICAL CINEMA.", font=state_fnt, fill=WHITE)
    d2.text((rx, 200 * SCALE), "BUILT FOR THE CULTURE.", font=state_fnt, fill=GOLD_HI)

    # Free to watch
    free_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d2.text((rx, 275 * SCALE), "ALWAYS FREE TO WATCH", font=free_fnt, fill=WHITE)

    # URL
    url_fnt = font(PLEX_MONO, 32 * SCALE // 2)
    d2.text((rx, 318 * SCALE), "myvurt.com", font=url_fnt, fill=GOLD)

    export(img, "C2-C_PHONE-DOMINANT")


def c2_variant_d():
    """V2-D: Three-phone-frame triptych — proves the breadth of the platform."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Top accent
    d.rectangle([(0, 0), (W, 5 * SCALE)], fill=GOLD)

    # VURT mark — top
    brand_fnt = font(INTER_BOLD, 50 * SCALE // 2)
    bw, bh = text_w(d, "VURT", brand_fnt)
    d.text(((W - bw) / 2, 25 * SCALE), "VURT", font=brand_fnt, fill=GOLD)

    # Three phones across the middle
    ph_w = 110 * SCALE
    ph_h = 200 * SCALE
    gap = 25 * SCALE
    total_w = ph_w * 3 + gap * 2
    start_x = (W - total_w) // 2
    ph_y = 80 * SCALE

    posters = [
        ("#3A1F1F", "#0B0B0B", "COME BACK", "DAD", "DRAMA"),
        ("#1F2A3A", "#0B0B0B", "KARMA", "IN HEELS", "ROMANCE"),
        ("#3A2A1F", "#0B0B0B", "PARKING", "LOT", "COMEDY"),
    ]
    for i, (top, bot, t1, t2, sub) in enumerate(posters):
        draw_phone(d, img, start_x + i * (ph_w + gap), ph_y, ph_w, ph_h,
                   top, bot, t1, t2, sub)

    # Statement below phones
    d2 = ImageDraw.Draw(img)
    state_fnt = font(INTER_BOLD, 40 * SCALE // 2)
    state = "BUILT FOR THE CULTURE."
    sw, _ = text_w(d2, state, state_fnt)
    d2.text(((W - sw) / 2, 300 * SCALE), state, font=state_fnt, fill=WHITE)

    # Free + URL strip
    free_fnt = font(INTER_BOLD, 28 * SCALE // 2)
    url_fnt = font(PLEX_MONO, 28 * SCALE // 2)
    free_txt = "ALWAYS FREE TO WATCH"
    url_txt = "myvurt.com"
    fw, _ = text_w(d2, free_txt, free_fnt)
    uw, _ = text_w(d2, url_txt, url_fnt)
    sep = "   ·   "
    sw2, _ = text_w(d2, sep, free_fnt)
    total = fw + sw2 + uw
    bx = (W - total) / 2
    by = 348 * SCALE
    d2.text((bx, by), free_txt, font=free_fnt, fill=GOLD_HI)
    d2.text((bx + fw, by), sep, font=free_fnt, fill=GRAY)
    d2.text((bx + fw + sw2, by), url_txt, font=url_fnt, fill=WHITE)

    export(img, "C2-D_TRIPTYCH")


# =============================================================
# ROUND 2 — Tighter compositions per Dioni feedback
#   C1-D: FOMO cast listing (4 cofounders named, exclusivity stamp, no phone)
#   C2-E: Single-poster hero (one bold phone, dense right column)
#   C2-F: Triptych w/ culture tags (Hip-Hop · Romance · Faith)
# =============================================================

def c1_variant_d():
    """C1-D: FOMO cast listing. The hosts ARE the visual.
    Industry FOMO works because of who's in the room, not what's on the poster."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Top accent
    d.rectangle([(0, 0), (W, 5 * SCALE)], fill=GOLD)

    # Kicker — top center
    kicker_fnt = font(INTER_BOLD, 30 * SCALE // 2)
    kicker = "OPENING NIGHT  ·  FRI 5.29.26  ·  MIAMI BEACH"
    kw, _ = text_w(d, kicker, kicker_fnt)
    d.text(((W - kw) / 2, 30 * SCALE), kicker, font=kicker_fnt, fill=GOLD_HI)

    # Hero — VURT IS HERE (medium, makes room for cast)
    hero_fnt = font(INTER_BOLD, 110 * SCALE // 2)
    hero = "VURT IS HERE."
    hw, _ = text_w(d, hero, hero_fnt)
    d.text(((W - hw) / 2, 65 * SCALE), hero, font=hero_fnt, fill=WHITE)

    # Divider
    div_y = 175 * SCALE
    d.line([(W * 0.30, div_y), (W * 0.70, div_y)], fill=GOLD, width=2 * SCALE)

    # "HOSTED BY" small label
    hosted_fnt = font(INTER_BOLD, 22 * SCALE // 2)
    hosted = "HOSTED BY"
    h2w, _ = text_w(d, hosted, hosted_fnt)
    d.text(((W - h2w) / 2, 188 * SCALE), hosted, font=hosted_fnt, fill=GRAY)

    # 4 names — single row, large
    names_fnt = font(INTER_BOLD, 38 * SCALE // 2)
    names = "TARIK BROOKS    TED LUCAS    HILMON SOREY    ERIC TOMOSUNAS"
    nw, nh = text_w(d, names, names_fnt)
    # If too wide, render as 2 lines of 2
    if nw > W - 60 * SCALE:
        line1 = "TARIK BROOKS    ·    TED LUCAS"
        line2 = "HILMON SOREY    ·    ERIC TOMOSUNAS"
        l1w, l1h = text_w(d, line1, names_fnt)
        l2w, l2h = text_w(d, line2, names_fnt)
        d.text(((W - l1w) / 2, 220 * SCALE), line1, font=names_fnt, fill=WHITE)
        d.text(((W - l2w) / 2, 260 * SCALE), line2, font=names_fnt, fill=WHITE)
        bottom_y = 308 * SCALE
    else:
        d.text(((W - nw) / 2, 220 * SCALE), names, font=names_fnt, fill=WHITE)
        bottom_y = 280 * SCALE

    # Bottom — exclusivity stamp + URL on one strip
    excl_fnt = font(INTER_BOLD, 26 * SCALE // 2)
    url_fnt = font(PLEX_MONO, 26 * SCALE // 2)
    excl = "GATES HOTEL ROOFTOP  ·  BY INVITATION  ·  500 CAP"
    url = "myvurt.com/miami"
    ew, _ = text_w(d, excl, excl_fnt)
    uw, _ = text_w(d, url, url_fnt)
    d.text(((W - ew) / 2, bottom_y), excl, font=excl_fnt, fill=GOLD_HI)
    d.text(((W - uw) / 2, bottom_y + 38 * SCALE), url, font=url_fnt, fill=WHITE)

    export(img, "C1-D_FOMO-CAST")


def c2_variant_e():
    """C2-E: Single-poster hero. One dominant phone, denser right column.
    The 'premium product' read — versus the triptych's 'platform with range' read."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Phone frame — left, dominant. Bigger than C2-C.
    ph_w = 215 * SCALE
    ph_h = 380 * SCALE
    ph_x = 35 * SCALE
    ph_y = (H - ph_h) // 2
    draw_phone(d, img, ph_x, ph_y, ph_w, ph_h,
               "#1F2A3A", "#0B0B0B",
               "KARMA", "IN HEELS", "VURT ORIGINAL")

    # Vertical divider
    d2 = ImageDraw.Draw(img)
    div_x = 295 * SCALE
    d2.line([(div_x, 50 * SCALE), (div_x, 350 * SCALE)], fill=GOLD, width=1 * SCALE)

    # Right column anchored
    rx = 320 * SCALE

    # VURT mark — top of right col
    brand_fnt = font(INTER_BOLD, 95 * SCALE // 2)
    d2.text((rx, 55 * SCALE), "VURT", font=brand_fnt, fill=GOLD)

    # Kicker
    kicker_fnt = font(INTER_BOLD, 26 * SCALE // 2)
    d2.text((rx, 145 * SCALE), "VERTICAL CINEMA", font=kicker_fnt, fill=GOLD_HI)

    # Statement — denser, two lines tightly stacked
    state_fnt = font(INTER_BOLD, 56 * SCALE // 2)
    d2.text((rx, 178 * SCALE), "BUILT FOR", font=state_fnt, fill=WHITE)
    d2.text((rx, 222 * SCALE), "THE CULTURE.", font=state_fnt, fill=WHITE)

    # Free + URL stacked
    free_fnt = font(INTER_BOLD, 30 * SCALE // 2)
    d2.text((rx, 290 * SCALE), "ALWAYS FREE TO WATCH", font=free_fnt, fill=GOLD_HI)

    url_fnt = font(PLEX_MONO, 30 * SCALE // 2)
    d2.text((rx, 328 * SCALE), "myvurt.com", font=url_fnt, fill=WHITE)

    export(img, "C2-E_SINGLE-HERO")


def c2_variant_f():
    """C2-F: Triptych with CULTURE tags (not genre tags).
    Hip-Hop · Romance · Faith — broad-reach communities VURT credibly serves."""
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Top accent
    d.rectangle([(0, 0), (W, 5 * SCALE)], fill=GOLD)

    # VURT mark — top
    brand_fnt = font(INTER_BOLD, 50 * SCALE // 2)
    bw, _ = text_w(d, "VURT", brand_fnt)
    d.text(((W - bw) / 2, 22 * SCALE), "VURT", font=brand_fnt, fill=GOLD)

    # Three phones — slightly larger than C2-D
    ph_w = 118 * SCALE
    ph_h = 210 * SCALE
    gap = 28 * SCALE
    total_w = ph_w * 3 + gap * 2
    start_x = (W - total_w) // 2
    ph_y = 75 * SCALE

    # Posters tied to communities (palettes hint at vibe; designer can swap)
    posters = [
        ("#2A1A2A", "#0B0B0B", "TRICK", "DADDY", "HIP-HOP"),
        ("#1F2A3A", "#0B0B0B", "KARMA", "IN HEELS", "ROMANCE"),
        ("#3A2A1F", "#0B0B0B", "COME BACK", "DAD", "FAITH"),
    ]
    for i, (top, bot, t1, t2, sub) in enumerate(posters):
        draw_phone(d, img, start_x + i * (ph_w + gap), ph_y, ph_w, ph_h,
                   top, bot, t1, t2, sub)

    # Statement below phones
    d2 = ImageDraw.Draw(img)
    state_fnt = font(INTER_BOLD, 38 * SCALE // 2)
    state = "BUILT FOR THE CULTURE."
    sw, _ = text_w(d2, state, state_fnt)
    d2.text(((W - sw) / 2, 305 * SCALE), state, font=state_fnt, fill=WHITE)

    # Free + URL strip
    free_fnt = font(INTER_BOLD, 26 * SCALE // 2)
    url_fnt = font(PLEX_MONO, 26 * SCALE // 2)
    free_txt = "ALWAYS FREE TO WATCH"
    url_txt = "myvurt.com"
    fw, _ = text_w(d2, free_txt, free_fnt)
    uw, _ = text_w(d2, url_txt, url_fnt)
    sep = "   ·   "
    sw2, _ = text_w(d2, sep, free_fnt)
    total = fw + sw2 + uw
    bx = (W - total) / 2
    by = 350 * SCALE
    d2.text((bx, by), free_txt, font=free_fnt, fill=GOLD_HI)
    d2.text((bx + fw, by), sep, font=free_fnt, fill=GRAY)
    d2.text((bx + fw + sw2, by), url_txt, font=url_fnt, fill=WHITE)

    export(img, "C2-F_TRIPTYCH-CULTURE")


if __name__ == "__main__":
    print("Rendering VURT Miami billboards (840x400, 4x masters):")
    c1_variant_a()
    c1_variant_b()
    c1_variant_c()
    c2_variant_a()
    c2_variant_b()
    c2_variant_c()
    c2_variant_d()
    print("--- Round 2 ---")
    c1_variant_d()
    c2_variant_e()
    c2_variant_f()
    print(f"Output: {OUT}")
