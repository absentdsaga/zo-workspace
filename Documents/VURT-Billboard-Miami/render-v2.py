"""
VURT Miami DOOH billboards — research-backed v2 concepts.
Two NEW concepts: C1-E (By Invitation) + C2-G (Single Hero rotation).
840x400px static, designed at 4x (3360x1600) for crisp LED rendering.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

OUT = Path("/home/workspace/Documents/VURT-Billboard-Miami")

SCALE = 4
W, H = 840 * SCALE, 400 * SCALE

# Brand tokens
BLACK = "#0B0B0B"
GOLD = "#D4A63A"
GOLD_HI = "#F5D27A"
WHITE = "#EBEBEB"      # NOT pure white — research: #FFFFFF blooms on LED
GRAY = "#999999"
DIM = "#666666"
ACCENT_RED = "#E63946"  # VURT brand red, optional A/B accent

INTER_BOLD = "/usr/share/fonts/inter/Inter-Bold.ttf"
INTER_REGULAR = "/usr/share/fonts/inter/Inter-Regular.ttf"
INTER_MEDIUM = "/usr/share/fonts/inter/Inter-Medium.ttf"
PLEX_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def tw(draw, txt, fnt):
    b = draw.textbbox((0, 0), txt, font=fnt)
    return b[2] - b[0], b[3] - b[1]

def export(img, name):
    final = img.resize((840, 400), Image.LANCZOS)
    final.save(OUT / f"{name}.png", optimize=True)
    img.save(OUT / f"{name}@4x.png", optimize=True)
    print(f"  {name}.png  +  {name}@4x.png")


# =============================================================
# C1-E — "BY INVITATION" (Opening Night, 5/26-5/29)
# =============================================================
def c1_e_by_invitation():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    PAD_L = 56 * SCALE
    PAD_R = 56 * SCALE

    # VURT logo (top right) — wordmark in Inter Bold caps
    logo_fnt = font(INTER_BOLD, 64 * SCALE // 2)
    logo = "VURT"
    lw, lh = tw(d, logo, logo_fnt)
    d.text((W - PAD_R - lw, 32 * SCALE), logo, font=logo_fnt, fill=WHITE)

    # Hero line 1 — "BY INVITATION."
    hero_fnt = font(INTER_BOLD, 120 * SCALE // 2)
    hero1 = "BY INVITATION."
    h1w, h1h = tw(d, hero1, hero_fnt)
    d.text((PAD_L, 70 * SCALE), hero1, font=hero_fnt, fill=WHITE)

    # Hero line 2 — "ROOFTOP. 5.29." in accent
    hero2 = "ROOFTOP. 5.29."
    h2w, h2h = tw(d, hero2, hero_fnt)
    d.text((PAD_L, 70 * SCALE + h1h + 8 * SCALE), hero2, font=hero_fnt, fill=GOLD_HI)

    # Vertical divider line (left of support block)
    div_y_start = 240 * SCALE
    d.line([(PAD_L, div_y_start), (PAD_L + 60 * SCALE, div_y_start)],
           fill=GOLD, width=2 * SCALE)

    # Event meta line
    meta_fnt = font(INTER_MEDIUM, 28 * SCALE // 2)
    meta = "Opening Night  ·  Gates Hotel South Beach  ·  Miami"
    d.text((PAD_L, 252 * SCALE), meta, font=meta_fnt, fill=WHITE)

    # Hosted by line — small, dim
    host_fnt = font(INTER_REGULAR, 22 * SCALE // 2)
    host = "Hosted by Tarik Brooks  ·  Ted Lucas  ·  Hilmon Sorey  ·  Eric Tomosunas"
    d.text((PAD_L, 282 * SCALE), host, font=host_fnt, fill=GRAY)

    # CTA — bottom right
    cta_fnt = font(PLEX_MONO, 32 * SCALE // 2)
    cta = "myvurt.com/abff →"
    cw, ch = tw(d, cta, cta_fnt)
    d.text((W - PAD_R - cw, H - 56 * SCALE - ch), cta, font=cta_fnt, fill=GOLD_HI)

    export(img, "C1-E_BY-INVITATION")


# =============================================================
# C2-G — "SINGLE HERO" (Always-On 5/30-5/31)
# Three variants — same layout, different "talent" placeholder.
# Real photos to be supplied by gfx guy from Frame.io masters.
# =============================================================
def c2_g_single_hero(variant_name, talent_label, accent=GOLD_HI):
    """
    Concept-grade mockup. Left half = talent placeholder (cinematic gradient
    + name plate showing where the photo goes). Right half = type column.
    Real production: gfx guy drops in talent photo at full bleed left half.
    """
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # ---- Left half: photo placeholder area ----
    PHOTO_W = int(W * 0.55)
    photo = Image.new("RGB", (PHOTO_W, H), "#1a1a1a")
    pd = ImageDraw.Draw(photo)

    # Cinematic gradient backdrop (radial-ish — darker corners)
    for i in range(20):
        alpha_band = 255 - int(i * 6)
        rect_inset = i * 12
        pd.rectangle([(rect_inset, rect_inset), (PHOTO_W - rect_inset, H - rect_inset)],
                     outline=(int(20 + i * 2), int(20 + i * 1.5), int(20 + i * 1.5)),
                     width=2)

    # Photo placeholder label (so user knows this is where talent goes)
    ph_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    ph_label = f"[ {talent_label} ]"
    plw, plh = tw(pd, ph_label, ph_fnt)
    pd.text(((PHOTO_W - plw) // 2, (H - plh) // 2 - 30 * SCALE),
            ph_label, font=ph_fnt, fill=DIM)

    sub_fnt = font(INTER_REGULAR, 18 * SCALE // 2)
    sub = "talent photo · full-bleed · single face"
    slw, slh = tw(pd, sub, sub_fnt)
    pd.text(((PHOTO_W - slw) // 2, (H - plh) // 2 + 20 * SCALE),
            sub, font=sub_fnt, fill=DIM)

    # Soft fade on right edge of photo into black background
    fade = Image.new("L", (PHOTO_W, H), 255)
    fd = ImageDraw.Draw(fade)
    for x in range(PHOTO_W - 80 * SCALE, PHOTO_W):
        ratio = (x - (PHOTO_W - 80 * SCALE)) / (80 * SCALE)
        fd.line([(x, 0), (x, H)], fill=int(255 * (1 - ratio)))
    img.paste(photo, (0, 0), fade)

    # ---- Right half: type column ----
    R_LEFT = int(W * 0.58)
    R_PAD_R = 56 * SCALE

    # VURT logo
    logo_fnt = font(INTER_BOLD, 76 * SCALE // 2)
    d.text((R_LEFT, 60 * SCALE), "VURT", font=logo_fnt, fill=WHITE)

    # Tagline 2 lines
    tag_fnt = font(INTER_BOLD, 56 * SCALE // 2)
    d.text((R_LEFT, 140 * SCALE), "Vertical Cinema.", font=tag_fnt, fill=WHITE)
    d.text((R_LEFT, 140 * SCALE + 60 * SCALE), "Built for the Culture.", font=tag_fnt, fill=WHITE)

    # Divider
    d.line([(R_LEFT, 280 * SCALE), (R_LEFT + 60 * SCALE, 280 * SCALE)],
           fill=accent, width=2 * SCALE)

    # Value prop
    vp_fnt = font(INTER_BOLD, 32 * SCALE // 2)
    d.text((R_LEFT, 295 * SCALE), "ALWAYS FREE TO WATCH", font=vp_fnt, fill=accent)

    # CTA
    cta_fnt = font(PLEX_MONO, 32 * SCALE // 2)
    d.text((R_LEFT, 340 * SCALE), "myvurt.com →", font=cta_fnt, fill=WHITE)

    export(img, variant_name)


if __name__ == "__main__":
    print("Rendering research-backed v2 concepts:")
    print()
    c1_e_by_invitation()
    c2_g_single_hero("C2-G-1_HERO-DRAMA", "ROTIMI")
    c2_g_single_hero("C2-G-2_HERO-LEGACY", "VIVICA A. FOX")
    c2_g_single_hero("C2-G-3_HERO-ROMANCE", "MEAGAN GOOD")
    print()
    print("Done. Concepts saved to /home/workspace/Documents/VURT-Billboard-Miami/")
