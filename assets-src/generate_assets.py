#!/usr/bin/env python3
"""NiceOS asset generator — purple/blue brand art for every reskin layer.

Run from the repo root:  python3 assets-src/generate_assets.py
Writes directly into config/includes.chroot/... so the shipped tree is
always reproducible from this script. Requires Pillow.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..", "config", "includes.chroot")

PURPLE = (0x7C, 0x4D, 0xFF)
MID = (0x5B, 0x6B, 0xF9)
BLUE = (0x29, 0x79, 0xFF)
DARK_A = (0x17, 0x12, 0x30)   # deep indigo
DARK_B = (0x0E, 0x1E, 0x4E)   # deep blue

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient(w, h, top=DARK_A, bottom=DARK_B):
    """Diagonal dark indigo -> deep blue base."""
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(0, w, 4):  # stride 4, filled below for speed
            t = (x / max(1, w) + y / max(1, h)) / 2.0
            c = lerp(top, bottom, t)
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    return im


def add_glow(im, cx, cy, radius, color, alpha):
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=color + (alpha,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius / 2.2))
    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def add_grain(im, strength=6):
    noise = Image.effect_noise(im.size, strength).convert("RGB")
    return Image.blend(im, noise, 0.05)


def add_streak(im):
    """Soft diagonal light streak across the wallpaper."""
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = im.size
    d.polygon([(-w * 0.1, h), (w * 0.45, 0), (w * 0.62, 0), (w * 0.07, h)],
              fill=(255, 255, 255, 10))
    overlay = overlay.filter(ImageFilter.GaussianBlur(60))
    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def draw_orb(size, letter="N", letter_scale=0.52):
    """Circular purple->blue gradient orb with a white letter."""
    s = size * 4  # supersample
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = im.load()
    c = s / 2.0
    r = s / 2.0 - 1
    for y in range(s):
        for x in range(s):
            dx, dy = x - c, y - c
            dist = math.hypot(dx, dy)
            if dist <= r:
                t = ((x + y) / (2.0 * s))
                px[x, y] = lerp(PURPLE, BLUE, t) + (255,)
    mask = Image.new("L", (s, s), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([1, 1, s - 2, s - 2], fill=255)
    im.putalpha(mask)
    # soft top-left highlight
    hl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.ellipse([s * 0.08, s * 0.08, s * 0.62, s * 0.62],
               fill=(255, 255, 255, 46))
    hl = hl.filter(ImageFilter.GaussianBlur(s * 0.08))
    im = Image.alpha_composite(im, hl)
    if letter:
        f = ImageFont.truetype(FONT_BOLD, int(s * letter_scale))
        d = ImageDraw.Draw(im)
        bbox = d.textbbox((0, 0), letter, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((c - tw / 2 - bbox[0], c - th / 2 - bbox[1]), letter,
               font=f, fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)


def wallpaper(w, h, with_mark=True):
    im = gradient(w, h)
    im = add_glow(im, int(w * 0.22), int(h * 0.18), int(h * 0.55), PURPLE, 38)
    im = add_glow(im, int(w * 0.82), int(h * 0.86), int(h * 0.60), BLUE, 30)
    im = add_streak(im)
    im = add_grain(im)
    if with_mark:
        orb = draw_orb(int(h * 0.075), letter="N", letter_scale=0.5)
        alpha = orb.getchannel("A").point(lambda a: a * 0.85)
        orb.putalpha(alpha)
        im = im.convert("RGBA")
        im.alpha_composite(orb, (int(w * 0.94 - h * 0.075), int(h * 0.93 - h * 0.075)))
        im = im.convert("RGB")
    return im


def hero(w, h):
    """Calamares welcome hero: orb + wordmark + subtitle."""
    im = gradient(w, h)
    im = add_glow(im, int(w * 0.25), int(h * 0.5), int(h * 0.7), PURPLE, 42)
    im = add_glow(im, int(w * 0.85), int(h * 0.5), int(h * 0.7), BLUE, 34)
    im = add_grain(im)
    im = im.convert("RGBA")
    orb = draw_orb(int(h * 0.42))
    im.alpha_composite(orb, (int(w * 0.10), int(h * 0.29)))
    d = ImageDraw.Draw(im)
    f_big = ImageFont.truetype(FONT_BOLD, int(h * 0.16))
    f_sub = ImageFont.truetype(FONT_REG, int(h * 0.055))
    d.text((w * 0.36, h * 0.38), "NiceOS", font=f_big,
           fill=(255, 255, 255, 255))
    d.text((w * 0.365, h * 0.58), "A purple-blue Debian 13 desktop",
           font=f_sub, fill=(0xD8, 0xD4, 0xF2, 255))
    return im.convert("RGB")


def slide(w, h, title, lines, orb=True):
    im = gradient(w, h)
    im = add_glow(im, int(w * 0.3), int(h * 0.3), int(h * 0.5), PURPLE, 34)
    im = add_glow(im, int(w * 0.75), int(h * 0.8), int(h * 0.5), BLUE, 28)
    im = add_grain(im).convert("RGBA")
    if orb:
        o = draw_orb(int(h * 0.30))
        im.alpha_composite(o, (int(w * 0.42), int(h * 0.12)))
    d = ImageDraw.Draw(im)
    f_t = ImageFont.truetype(FONT_BOLD, int(h * 0.085))
    f_l = ImageFont.truetype(FONT_REG, int(h * 0.045))
    ty = h * 0.52
    bbox = d.textbbox((0, 0), title, font=f_t)
    d.text((w / 2 - (bbox[2] - bbox[0]) / 2, ty), title, font=f_t,
           fill=(255, 255, 255, 255))
    ty += h * 0.13
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=f_l)
        d.text((w / 2 - (bbox[2] - bbox[0]) / 2, ty), line, font=f_l,
               fill=(0xC9, 0xC4, 0xE8, 255))
        ty += h * 0.075
    return im.convert("RGB")


def write(im, path, quality=92):
    p = ensure(os.path.join(ROOT, path))
    if p.endswith(".png"):
        im.save(p, optimize=True)
    else:
        im.save(p, quality=quality, optimize=True)
    print(f"wrote {p} {im.size}")


# --- wallpapers -----------------------------------------------------------
write(wallpaper(1920, 1080), "usr/share/backgrounds/niceos/wallpaper-1920.jpg")
write(wallpaper(2560, 1440), "usr/share/backgrounds/niceos/wallpaper-2560.jpg")
write(wallpaper(1024, 768, with_mark=False),
      "usr/share/grub/themes/niceos/background.jpg", quality=88)

# --- logo / icons ---------------------------------------------------------
orb512 = draw_orb(512)
p = ensure(os.path.join(ROOT, "usr/share/niceos/niceos-logo-512.png"))
orb512.save(p, optimize=True)
print(f"wrote {p} (512)")

for size, sub in [(64, "64x64"), (48, "48x48"), (32, "32x32"), (16, "16x16")]:
    p = ensure(os.path.join(ROOT,
               f"usr/share/icons/hicolor/{sub}/apps/niceos.png"))
    draw_orb(size).save(p, optimize=True)
    print(f"wrote {p}")

# --- plymouth logo (same color orb, 256) ----------------------------------
p = ensure(os.path.join(ROOT, "usr/share/plymouth/themes/niceos/logo.png"))
draw_orb(256).save(p, optimize=True)
print(f"wrote {p}")

# --- calamares branding ---------------------------------------------------
CB = "usr/share/calamares/branding/niceos"
draw_orb(256).save(ensure(os.path.join(ROOT, CB, "niceos-logo.png")),
                   optimize=True)
draw_orb(128).save(ensure(os.path.join(ROOT, CB, "niceos-icon.png")),
                   optimize=True)
write(hero(1024, 512), f"{CB}/niceos-welcome.png")
write(slide(1200, 640, "Welcome to NiceOS",
            ["A purple-blue reskin of Debian 13 with XFCE",
             "Fast, simple, and yours."]),
      f"{CB}/slide-1.png")
write(slide(1200, 640, "Everything you need",
            ["Mac-like top panel and dock", "Calamares installer, LightDM login",
             "Plymouth splash and branded boot"], orb=False),
      f"{CB}/slide-2.png")

# --- preview for the user -------------------------------------------------
prev = wallpaper(960, 540)
prev.save("/home/z/my-project/test-infra/niceos-wallpaper-preview.png")
print("preview written")
print("ASSETS DONE")
