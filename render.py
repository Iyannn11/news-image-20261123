#!/usr/bin/env python3
"""Render THE WORLD IN ONE DAY — Monday 23 November 2026 (News 23 R3b).
Fresh renderer written for entry-r3b. R1-based design (viewed R1 image
only, never read any old code) + AWS Quick maximizations (24 Nov 10:55):
- R1 layout kept exactly; new detail goes INSIDE existing elements.
- NO fact-numbers row, NO region colour bar as a band (those hurt R2).
- ONE red number per hero card; region colour only in: map land tint,
  3px top border on cards 4-13, 6px dot in list rows, map legend.
- 1024x1024. Facts from entry-r1/SOURCES.md only.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (245, 238, 220)
PAPER = (250, 244, 230)
CARD = (255, 252, 246)
NAVY = (20, 40, 75)
NAVY_DK = (24, 33, 64)
GOLD = (212, 175, 90)
RED = (192, 32, 32)
GREEN_PILL = (26, 122, 52)
GREEN_TICK = (28, 130, 60)
INK = (27, 27, 27)
GREY = (100, 100, 100)
LINE = (180, 170, 150)

# region palette (same mapping everywhere)
REGION = {
    "ASIA": (31, 122, 140),       # teal
    "EUROPE": (63, 95, 168),      # slate blue
    "MIDDLE EAST": (181, 82, 59),  # terracotta
    "AMERICAS": (201, 138, 27),   # ochre
    "AFRICA": (123, 75, 148),     # plum
    "OCEANIA": (138, 106, 61),    # brown
    "GLOBAL": (176, 71, 110),     # rose
}
REGION_ORDER = ["ASIA", "EUROPE", "MIDDLE EAST", "AMERICAS", "AFRICA",
                "OCEANIA", "GLOBAL"]

FDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    try:
        return ImageFont.truetype(FDIR + name, size)
    except OSError:
        return ImageFont.truetype(FDIR + "DejaVuSans.ttf", size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS_I = lambda s: font("DejaVuSans-Oblique.ttf", s)

VIOLATIONS = []


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_box(draw, xy, text, fnt, fill, max_w, align="left", line_h=None,
             box=None, max_lines=None):
    """Draw wrapped text. box=(x0,y0,x1,y1) is the hard limit (card bounds);
    any glyph crossing it is a gap-scan violation. Returns y below last line."""
    x, y = xy
    if line_h is None:
        line_h = int(fnt.size * 1.22)
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        tw = draw.textlength(ln, font=fnt)
        lx = x if align == "left" else x + (max_w - tw) / 2 if align == "center" else x + max_w - tw
        if box is not None:
            if lx < box[0] or lx + tw > box[2] or y < box[1] or y + fnt.size > box[3]:
                VIOLATIONS.append(
                    f"text overflow {text[:28]!r} at y={y} box={box}")
        draw.text((lx, y), ln, font=fnt, fill=fill)
        y += line_h
    return y


def text_halo(draw, xy, text, fnt, fill, halo=PAPER):
    """Text with a 1px paper halo (for map labels over dots)."""
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        draw.text((x + dx, y + dy), text, font=fnt, fill=halo)
    draw.text((x, y), text, font=fnt, fill=fill)


def pill(draw, x, y, label, fg=(255, 255, 255), bg=GREEN_PILL, fnt=None):
    fnt = fnt or SANS_B(9)
    tw = draw.textlength(label, font=fnt)
    w, h = int(tw) + 10, 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=7, fill=bg)
    draw.text((x + 5, y + 2), label, font=fnt, fill=fg)
    return w


def pin(draw, cx, cy, n, r=9, ring=False):
    if ring:
        draw.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2],
                     outline=GOLD, width=2)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=1)
    f = SANS_B(10 if r >= 9 else 8)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - 7 if r >= 9 else cy - 6), t, font=f,
              fill=(255, 255, 255))


# ---------------------------------------------------------------- heroes
def ill_cop31(draw, x, y, w, h):
    """Conference hall: big screen with globe, podium + speaker,
    delegates with tiny desk flags, stage banner."""
    draw.rectangle([x, y, x + w, y + h], fill=(28, 52, 84))
    # big screen with globe, fully inside the screen
    draw.rectangle([x + 24, y + 6, x + w - 24, y + 42], fill=(220, 228, 235))
    draw.ellipse([x + w // 2 - 15, y + 9, x + w // 2 + 15, y + 39],
                 fill=(40, 110, 190))
    draw.ellipse([x + w // 2 - 8, y + 14, x + w // 2 + 6, y + 34],
                 fill=(90, 190, 120))
    # stage banner text below the screen
    bf = SANS_B(11)
    t = "COP31 · ANTALYA"
    draw.text((x + (w - draw.textlength(t, font=bf)) / 2, y + 45), t,
              font=bf, fill=(255, 255, 255))
    # speaker at podium (centre, below the banner)
    draw.ellipse([x + w // 2 - 7, y + 58, x + w // 2 + 7, y + 72],
                 fill=(240, 220, 190))
    draw.pieslice([x + w // 2 - 12, y + 70, x + w // 2 + 12, y + 84],
                  180, 360, fill=(20, 40, 75))
    draw.rectangle([x + w // 2 - 16, y + 72, x + w // 2 + 16, y + 84],
                   fill=(120, 90, 60))
    # delegates at the sides with tiny desk flags
    cols = [(220, 60, 60), (250, 200, 60), (90, 190, 90), (240, 130, 60)]
    for i, c in enumerate(cols):
        cx = x + 26 + i * 26 if i < 2 else x + w - 78 + (i - 2) * 26
        draw.ellipse([cx - 8, y + 66, cx + 8, y + 78], fill=(240, 220, 190))
        draw.pieslice([cx - 11, y + 76, cx + 11, y + 84], 180, 360, fill=c)
        draw.rectangle([cx + 11, y + 70, cx + 19, y + 76], fill=c)


def ill_nato(draw, x, y, w, h):
    """NATO HQ at night: building outline, flagpoles, gold lit windows,
    crescent moon + stars, small sign."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 28, 66))
    draw.ellipse([x + w - 52, y + 8, x + w - 20, y + 40], fill=(245, 240, 200))
    draw.ellipse([x + w - 44, y + 4, x + w - 12, y + 36], fill=(18, 28, 66))
    for sx, sy in [(24, 12), (80, 8), (150, 14), (210, 10), (60, 28),
                   (180, 26), (250, 24)]:
        draw.regular_polygon((x + sx, y + sy, 3), 5, fill=(250, 220, 90))
    # HQ building: gold-lit window grid
    bx, by, bw, bh = x + 48, y + 34, w - 96, 44
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(214, 206, 188))
    draw.polygon([(bx - 8, by), (bx + bw / 2, by - 12), (bx + bw + 8, by)],
                 fill=(190, 182, 164))
    for r in range(2):
        for c in range(7):
            wx = bx + 12 + c * 30
            wy = by + 8 + r * 16
            draw.rectangle([wx, wy, wx + 16, wy + 9], fill=(250, 205, 80))
    for i in range(6):
        cx = bx + 12 + i * (bw - 24) / 5
        draw.rectangle([cx - 4, by + 22, cx + 4, by + bh - 2],
                       fill=(150, 142, 122))
    # flagpoles row + small sign
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 40, 60))
    for i, c in enumerate([(220, 60, 60), (60, 140, 220), (250, 200, 60),
                           (90, 190, 90), (240, 130, 60)]):
        fx = x + 26 + i * 56
        draw.line([fx, y + h - 34, fx, y + h - 12], fill=(220, 220, 220), width=2)
        draw.polygon([(fx, y + h - 34), (fx + 16, y + h - 29), (fx, y + h - 24)],
                     fill=c)
    draw.rectangle([x + w - 58, y + h - 30, x + w - 14, y + h - 14],
                   fill=(255, 255, 255), outline=(150, 150, 150), width=1)
    draw.text((x + w - 52, y + h - 28), "NATO", font=SANS_B(9), fill=NAVY)


def ill_taipei(draw, x, y, w, h):
    """Falling candlesticks on a gridded screen + ticker line."""
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for gy in range(4):
        yy = y + 12 + gy * 20
        draw.line([x + 8, yy, x + w - 8, yy], fill=(228, 228, 228), width=1)
    candles = [(24, 14, 12), (64, 26, 14), (104, 38, 12), (144, 50, 16),
               (184, 60, 12), (224, 70, 14)]
    for i, (cx, top, ch) in enumerate(candles):
        col = (200, 40, 40) if i % 2 == 0 else (60, 160, 80)
        draw.line([x + cx + 6, y + top - 6, x + cx + 6, y + top + ch + 6],
                  fill=col, width=2)
        draw.rectangle([x + cx, y + top, x + cx + 12, y + top + ch], fill=col)
    draw.line([x + 16, y + 12, x + w - 60, y + h - 30], fill=(200, 40, 40),
              width=3)
    # ticker line underneath
    draw.rectangle([x, y + h - 20, x + w, y + h], fill=(24, 33, 64))
    draw.text((x + 8, y + h - 17), "TAIEX  36,033.29", font=SANS_B(10),
              fill=(255, 255, 255))
    draw.text((x + w - 74, y + h - 17), "−17.5%", font=SANS_B(10), fill=(255, 120, 120))


# ------------------------------------------------------------ small banners
def banner(draw, x, y, w, h, kind):
    """Small coloured illustration banner (max 3 colours each)."""
    if kind == "chart":
        draw.rectangle([x, y, x + w, y + h], fill=(34, 120, 70))
        for i, bh in enumerate([10, 18, 13, 24, 17, 26]):
            bx = x + 12 + i * 28
            draw.rectangle([bx, y + h - 5 - bh, bx + 15, y + h - 5],
                           fill=(250, 210, 60))
        draw.line([x + 8, y + 8, x + w - 8, y + h - 10], fill=(255, 255, 255),
                  width=2)
    elif kind == "cricket":
        draw.rectangle([x, y, x + w, y + h], fill=(70, 160, 80))
        draw.rectangle([x + w // 2 - 12, y, x + w // 2 + 12, y + h],
                       fill=(240, 230, 200))
        for sx in (x + w // 2 - 8, x + w // 2 + 8):
            draw.line([sx, y + 5, sx, y + 15], fill=(250, 220, 90), width=3)
        draw.ellipse([x + 14, y + h - 16, x + 26, y + h - 4],
                     fill=(255, 255, 255))
    elif kind == "port":
        draw.rectangle([x, y, x + w, y + h], fill=(40, 120, 150))
        draw.rectangle([x, y + h - 12, x + w, y + h], fill=(20, 70, 100))
        draw.polygon([(x + 14, y + h - 12), (x + 46, y + 6), (x + 56, y + 6),
                      (x + 30, y + h - 12)], fill=(200, 200, 200))
        draw.rectangle([x + 88, y + h - 22, x + w - 12, y + h - 12],
                       fill=(200, 200, 200))
    elif kind == "skyline":
        draw.rectangle([x, y, x + w, y + h], fill=(140, 190, 220))
        draw.ellipse([x + w - 48, y + 3, x + w - 16, y + 24],
                     fill=(250, 240, 190))
        for bx, bh in [(10, 16), (34, 24), (64, 20), (94, 26), (124, 15)]:
            draw.rectangle([x + bx, y + h - 6 - bh, x + bx + 22, y + h - 6],
                           fill=(240, 240, 240))
    elif kind == "blast":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 44, 90))
        cx, cy = x + w // 2, y + h // 2
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            draw.line([cx, cy, cx + 20 * math.cos(a), cy + 14 * math.sin(a)],
                      fill=(250, 170, 40), width=3)
        draw.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=(250, 200, 60))
    elif kind == "asean":
        draw.rectangle([x, y, x + w, y + 8], fill=(230, 200, 40))
        draw.rectangle([x, y + 8, x + w, y + 16], fill=(40, 120, 70))
        draw.rectangle([x, y + 16, x + w, y + h], fill=(200, 50, 50))
        draw.ellipse([x + w // 2 - 10, y + 5, x + w // 2 + 10, y + 25],
                     fill=(255, 255, 255))
    elif kind == "un":
        draw.rectangle([x, y, x + w, y + h], fill=(90, 160, 220))
        draw.ellipse([x + w // 2 - 14, y + 3, x + w // 2 + 14, y + 27],
                     fill=(255, 255, 255), outline=(40, 90, 160), width=2)
        draw.ellipse([x + w // 2 - 5, y + 8, x + w // 2 + 5, y + 22],
                     fill=(120, 190, 240))
    elif kind == "haul":
        draw.rectangle([x, y, x + w, y + h], fill=(60, 40, 40))
        cx, cy = x + w // 2, y + h // 2
        for ang in range(0, 360, 24):
            a = math.radians(ang)
            draw.line([cx, cy, cx + 22 * math.cos(a), cy + 16 * math.sin(a)],
                      fill=(250, 120, 30), width=3)
        draw.ellipse([cx - 7, cy - 5, cx + 7, cy + 5], fill=(255, 220, 80))
    elif kind == "exam":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 36, 66))
        draw.rectangle([x + 46, y + 3, x + w - 46, y + h - 3],
                       fill=(255, 255, 255))
        for ly in (8, 15, 22):
            draw.line([x + 52, y + ly, x + w - 52, y + ly], fill=(180, 180, 180),
                      width=2)
        draw.line([x + w - 40, y + 6, x + w - 32, y + 16], fill=RED, width=3)
        draw.line([x + w - 32, y + 6, x + w - 40, y + 16], fill=RED, width=3)
    elif kind == "eu":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 60, 160))
        cx, cy = x + w // 2, y + h // 2
        for i in range(12):
            a = math.radians(i * 30 - 90)
            draw.regular_polygon((cx + 20 * math.cos(a), cy + 14 * math.sin(a), 3),
                                 5, fill=(250, 220, 60))


# ------------------------------------------------------------------- flags
def flag(draw, x, y, w, h, kind):
    if kind == "kr":
        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        draw.pieslice([x + w // 2 - 5, y + h // 2 - 5, x + w // 2 + 5,
                       y + h // 2 + 5], 90, 270, fill=(200, 40, 40))
        draw.pieslice([x + w // 2 - 5, y + h // 2 - 5, x + w // 2 + 5,
                       y + h // 2 + 5], 270, 90, fill=(40, 80, 200))
        draw.rectangle([x + 2, y + 2, x + 6, y + 4], fill=(30, 30, 30))
        draw.rectangle([x + w - 6, y + h - 4, x + w - 2, y + h - 2],
                       fill=(30, 30, 30))
    elif kind == "in":
        draw.rectangle([x, y, x + w, y + h // 3], fill=(255, 153, 51))
        draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3],
                       fill=(255, 255, 255))
        draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(19, 136, 8))
        draw.ellipse([x + w // 2 - 2, y + h // 2 - 2, x + w // 2 + 2,
                      y + h // 2 + 2], outline=(0, 0, 128), width=1)
    elif kind == "ly":
        draw.rectangle([x, y, x + w, y + h // 4], fill=(200, 40, 40))
        draw.rectangle([x, y + h // 4, x + w, y + 3 * h // 4], fill=(20, 20, 20))
        draw.rectangle([x, y + 3 * h // 4, x + w, y + h], fill=(0, 120, 60))
    elif kind == "au":
        draw.rectangle([x, y, x + w, y + h], fill=(0, 40, 120))
        draw.rectangle([x, y, x + 8, y + 6], fill=(200, 40, 40))
        for sx, sy in [(15, 4), (18, 9), (12, 10)]:
            draw.regular_polygon((x + sx, y + sy, 2), 5, fill=(255, 255, 255))
    elif kind == "fi":
        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        draw.rectangle([x + 6, y, x + 9, y + h], fill=(0, 80, 160))
        draw.rectangle([x, y + h // 2 - 2, x + w, y + h // 2 + 2],
                       fill=(0, 80, 160))
    elif kind == "mm":
        draw.rectangle([x, y, x + w, y + h // 3], fill=(250, 210, 40))
        draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3],
                       fill=(40, 120, 70))
        draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(200, 50, 50))
        draw.regular_polygon((x + w // 2, y + h // 2, 3), 5,
                             fill=(255, 255, 255))
    elif kind == "bh":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 40, 40))
        draw.polygon([(x, y), (x + 8, y), (x + 4, y + h // 4),
                      (x + 8, y + h // 2), (x + 4, y + 3 * h // 4),
                      (x + 8, y + h), (x, y + h)], fill=(255, 255, 255))
    elif kind == "lb":
        draw.rectangle([x, y, x + w, y + h // 4], fill=(200, 40, 40))
        draw.rectangle([x, y + h // 4, x + w, y + 3 * h // 4],
                       fill=(255, 255, 255))
        draw.rectangle([x, y + 3 * h // 4, x + w, y + h], fill=(200, 40, 40))
        draw.ellipse([x + w // 2 - 2, y + h // 2 - 3, x + w // 2 + 2,
                      y + h // 2 + 3], fill=(0, 120, 60))
    elif kind == "dk":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 40, 40))
        draw.rectangle([x + 6, y, x + 9, y + h], fill=(255, 255, 255))
        draw.rectangle([x, y + h // 2 - 2, x + w, y + h // 2 + 2],
                       fill=(255, 255, 255))
    elif kind == "us":
        for i in range(7):
            draw.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                           fill=(200, 40, 40) if i % 2 == 0 else (255, 255, 255))
        draw.rectangle([x, y, x + w // 2, y + 4 * h // 7], fill=(30, 50, 120))
        for sx, sy in [(3, 2), (8, 4), (5, 6)]:
            draw.regular_polygon((x + sx, y + sy, 1), 5, fill=(255, 255, 255))
    elif kind == "eu":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 60, 160))
        for i in range(8):
            a = math.radians(i * 45 - 90)
            draw.regular_polygon((x + w // 2 + 6 * math.cos(a),
                                  y + h // 2 + 4 * math.sin(a), 1), 5,
                                 fill=(250, 220, 60))
    elif kind == "globe":
        draw.ellipse([x, y, x + w, y + h], fill=(140, 190, 230),
                     outline=(40, 90, 160), width=1)
        draw.ellipse([x + 3, y + 2, x + w - 3, y + h - 2], outline=(40, 90, 160),
                     width=1)
        draw.line([x + 2, y + h // 2, x + w - 2, y + h // 2],
                  fill=(40, 90, 160), width=1)
    elif kind == "cn":
        draw.rectangle([x, y, x + w, y + h], fill=(220, 40, 40))
        draw.regular_polygon((x + 4, y + 4, 3), 5, fill=(250, 220, 60))
        draw.regular_polygon((x + 11, y + 3, 1), 5, fill=(250, 220, 60))
        draw.regular_polygon((x + 13, y + 7, 1), 5, fill=(250, 220, 60))
    elif kind == "vn":
        draw.rectangle([x, y, x + w, y + h], fill=(220, 40, 40))
        draw.regular_polygon((x + w // 2, y + h // 2, 4), 5,
                             fill=(250, 220, 60))
    elif kind == "tw":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 40, 40))
        draw.rectangle([x, y, x + w // 2, y + h // 2], fill=(30, 60, 160))
        draw.ellipse([x + 3, y + 2, x + 7, y + 6], fill=(255, 255, 255))
    elif kind == "za":
        draw.rectangle([x, y, x + w, y + h // 3], fill=(200, 40, 40))
        draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3],
                       fill=(255, 255, 255))
        draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(30, 60, 160))
        draw.line([x, y + h, x + w // 2, y + h // 2], fill=(0, 120, 60), width=2)
    elif kind == "sa":
        draw.rectangle([x, y, x + w, y + h], fill=(0, 110, 60))
        draw.line([x + 3, y + h // 2 - 1, x + w - 3, y + h // 2 - 1],
                  fill=(255, 255, 255), width=1)
        draw.line([x + 4, y + h - 3, x + w - 4, y + h - 3],
                  fill=(255, 255, 255), width=1)
    elif kind == "pk":
        draw.rectangle([x, y, x + w, y + h], fill=(0, 90, 50))
        draw.rectangle([x, y, x + w // 4, y + h], fill=(255, 255, 255))
        draw.ellipse([x + w // 2, y + h // 2 - 3, x + w // 2 + 6,
                      y + h // 2 + 3], fill=(255, 255, 255))
        draw.ellipse([x + w // 2 + 2, y + h // 2 - 3, x + w // 2 + 6,
                      y + h // 2 + 3], fill=(0, 90, 50))
    elif kind == "bd":
        draw.rectangle([x, y, x + w, y + h], fill=(0, 110, 60))
        draw.ellipse([x + w // 2 - 4, y + h // 2 - 4, x + w // 2 + 4,
                      y + h // 2 + 4], fill=(200, 40, 40))
    elif kind == "ph":
        draw.rectangle([x, y, x + w, y + h // 2], fill=(30, 80, 180))
        draw.rectangle([x, y + h // 2, x + w, y + h], fill=(200, 40, 40))
        draw.polygon([(x, y), (x, y + h), (x + 8, y + h // 2)],
                     fill=(255, 255, 255))
    elif kind == "tr":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 40, 40))
        draw.ellipse([x + 4, y + h // 2 - 4, x + 12, y + h // 2 + 4],
                     fill=(255, 255, 255))
        draw.ellipse([x + 6, y + h // 2 - 4, x + 12, y + h // 2 + 4],
                     fill=(200, 40, 40))
        draw.regular_polygon((x + 14, y + h // 2, 2), 5, fill=(255, 255, 255))
    elif kind == "nato":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 40, 90))
        draw.regular_polygon((x + w // 2, y + h // 2, 5), 4,
                             fill=(255, 255, 255))
    draw.rectangle([x, y, x + w, y + h], outline=(150, 150, 150), width=1)


# ------------------------------------------------------- topic icons (12px)
def topic_icon(draw, x, y, kind):
    c = NAVY
    if kind == "bars":
        for i, bh in enumerate([4, 8, 6, 11]):
            draw.rectangle([x + 1 + i * 3, y + 11 - bh, x + 3 + i * 3, y + 11],
                           fill=c)
    elif kind == "ball":
        draw.ellipse([x + 2, y + 2, x + 10, y + 10], outline=c, width=1)
        draw.line([x + 2, y + 6, x + 10, y + 6], fill=c, width=1)
    elif kind == "search":
        draw.ellipse([x + 1, y + 1, x + 8, y + 8], outline=c, width=1)
        draw.line([x + 7, y + 7, x + 11, y + 11], fill=c, width=2)
    elif kind == "box":
        draw.rectangle([x + 1, y + 3, x + 11, y + 11], outline=c, width=1)
        draw.line([x + 1, y + 3, x + 6, y + 1], fill=c, width=1)
        draw.line([x + 11, y + 3, x + 6, y + 1], fill=c, width=1)
    elif kind == "ship":
        draw.polygon([(x + 1, y + 8), (x + 11, y + 8), (x + 9, y + 11),
                      (x + 3, y + 11)], fill=c)
        draw.line([x + 6, y + 1, x + 6, y + 8], fill=c, width=1)
        draw.polygon([(x + 6, y + 2), (x + 10, y + 6), (x + 6, y + 6)], fill=c)
    elif kind == "globe":
        draw.ellipse([x + 1, y + 1, x + 11, y + 11], outline=c, width=1)
        draw.ellipse([x + 4, y + 1, x + 8, y + 11], outline=c, width=1)
        draw.line([x + 1, y + 6, x + 11, y + 6], fill=c, width=1)
    elif kind == "shield":
        draw.polygon([(x + 1, y + 1), (x + 11, y + 1), (x + 11, y + 7),
                      (x + 6, y + 11), (x + 1, y + 7)], outline=c, width=1)
    elif kind == "book":
        draw.rectangle([x + 1, y + 1, x + 11, y + 11], outline=c, width=1)
        draw.line([x + 6, y + 1, x + 6, y + 11], fill=c, width=1)
        draw.line([x + 3, y + 4, x + 5, y + 4], fill=c, width=1)
        draw.line([x + 8, y + 4, x + 10, y + 4], fill=c, width=1)
    elif kind == "stars":
        for i in range(5):
            a = math.radians(i * 72 - 90)
            draw.regular_polygon((x + 6 + 4 * math.cos(a),
                                  y + 6 + 4 * math.sin(a), 1), 5, fill=c)


# ---------------------------------------------------------------- dotted map
def _inside(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# continents in a 1004x170 space; (polygon, region) for the land tint
CONTINENTS = [
    ([(30, 30), (150, 10), (260, 25), (250, 70), (180, 85), (90, 80), (30, 55)],
     "AMERICAS"),
    ([(250, 95), (300, 90), (320, 130), (290, 165), (255, 140)], "AMERICAS"),
    ([(480, 25), (540, 12), (575, 30), (560, 55), (500, 55)], "EUROPE"),
    ([(480, 60), (540, 55), (575, 90), (550, 150), (505, 140), (480, 100)],
     "AFRICA"),
    ([(575, 20), (700, 8), (900, 15), (950, 45), (900, 75), (800, 70),
      (720, 85), (640, 70), (600, 50)], "ASIA"),
    ([(820, 95), (860, 90), (870, 110), (830, 115)], "ASIA"),
    ([(850, 120), (930, 115), (945, 140), (880, 150)], "OCEANIA"),
    # Arabian peninsula (Middle East tint over the Asia tint)
    ([(575, 62), (600, 55), (615, 65), (610, 85), (590, 90), (575, 80)],
     "MIDDLE EAST"),
]

# pins in the 1004x170 space: (number, x, y, region)
PINS = [
    (1, 556, 62, "MIDDLE EAST"), (2, 505, 42, "EUROPE"),
    (3, 860, 55, "ASIA"), (4, 830, 40, "ASIA"),
    (5, 720, 70, "ASIA"), (6, 520, 80, "AFRICA"),
    (7, 880, 135, "OCEANIA"), (8, 545, 18, "EUROPE"),
    (9, 790, 80, "ASIA"), (10, 600, 75, "MIDDLE EAST"),
    (11, 575, 62, "MIDDLE EAST"), (12, 814, 24, "ASIA"),
    (13, 520, 30, "EUROPE"), (14, 120, 55, "AMERICAS"),
    (15, 140, 45, "AMERICAS"), (16, 845, 28, "ASIA"),
    (17, 490, 50, "EUROPE"), (18, 470, 30, "GLOBAL"),
    (19, 800, 35, "ASIA"), (20, 828, 62, "ASIA"),
    (21, 815, 75, "ASIA"), (22, 844, 54, "ASIA"),
    (23, 850, 70, "ASIA"), (24, 540, 140, "AFRICA"),
    (25, 108, 68, "AMERICAS"), (26, 360, 40, "GLOBAL"),
    (27, 812, 52, "ASIA"), (28, 600, 60, "MIDDLE EAST"),
    (29, 690, 55, "ASIA"), (30, 760, 65, "ASIA"),
    (31, 880, 85, "ASIA"), (32, 700, 95, "ASIA"),
    (33, 760, 50, "ASIA"), (34, 710, 105, "ASIA"),
]

LABELS = [  # city labels only for stories 1-13: (label, pin x, pin y, dx, dy)
    ("GULF OF FINLAND", 545, 18, 12, -4),
    ("COPENHAGEN", 520, 30, -70, -12),
    ("BRUSSELS", 505, 42, -62, 0),
    ("BEIRUT", 575, 62, 12, -10),
    ("BENGHAZI", 520, 80, -64, 0),
    ("SEOUL", 830, 40, 48, -14),
    ("TAIPEI", 860, 55, 24, 41),
    ("NAYPYIDAW", 790, 80, -30, 12),
    ("NEW DELHI", 720, 70, -22, 12),
    ("SYDNEY", 880, 135, -56, -4),
]


def draw_map(img, d, x, y, w, h):
    """Dotted world map in the 1004x170 space scaled into (w, h)."""
    sx, sy = w / 1004.0, h / 170.0
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # land tint 12-15% opacity per region, dots on top
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for poly, reg in CONTINENTS:
        pts = [(px * sx, py * sy) for px, py in poly]
        od.polygon(pts, fill=REGION[reg] + (36,))
    img.paste(overlay, (x, y), overlay)
    dot = (168, 158, 138)
    scaled = [[(px * sx, py * sy) for px, py in poly] for poly, _ in CONTINENTS]
    for gy in range(3, h - 2, 8):
        for gx in range(3, w - 2, 8):
            for poly in scaled:
                if _inside(gx, gy, poly):
                    d.ellipse([x + gx - 1, y + gy - 1, x + gx + 1,
                               y + gy + 1], fill=dot)
                    break
    # faint grid every 30 deg + dotted equator (navy ~8%)
    grid = (196, 202, 214)
    for gx in (84, 167, 251, 334, 418, 502, 586, 669, 753, 837, 920):
        d.line([x + gx * sx, y, x + gx * sx, y + h], fill=grid, width=1)
    for gy in (28, 57, 85, 113, 142):
        d.line([x, y + gy * sy, x + w, y + gy * sy], fill=grid, width=1)
    for gx in range(0, w, 6):
        d.ellipse([x + gx, y + 85 * sy - 1, x + gx + 1, y + 85 * sy + 1],
                  fill=(120, 130, 160))
    # compass rose in empty South Pacific (~28px, navy line art)
    ccx, ccy = x + 200 * sx, y + 150 * sy
    d.ellipse([ccx - 13, ccy - 13, ccx + 13, ccy + 13], outline=NAVY, width=1)
    d.polygon([(ccx, ccy - 11), (ccx + 3, ccy), (ccx, ccy + 11), (ccx - 3, ccy)],
              outline=NAVY)
    d.line([ccx - 11, ccy, ccx + 11, ccy], fill=NAVY, width=1)
    d.text((ccx - 3, ccy - 23), "N", font=SANS_B(8), fill=NAVY)
    # Europe & Middle East close-up box in the empty South Atlantic
    ix0, iy0, ix1, iy1 = x + 330 * sx, y + 58 * sy, x + 480 * sx, y + 163 * sy
    d.rectangle([ix0, iy0, ix1, iy1], fill=(250, 246, 236),
                outline=NAVY, width=1)
    d.text((ix0 + 4, iy0 + 3), "EUROPE & MIDDLE EAST", font=SANS_B(8),
           fill=NAVY)
    # coverage outline on the main map
    d.rectangle([x + 470 * sx, y + 5 * sy, x + 640 * sx, y + 100 * sy],
                outline=(150, 150, 150), width=1)
    # inset dots + pins (region x 470-640, y 5-100 -> inset box)
    iw, ih = ix1 - ix0 - 4, iy1 - iy0 - 16
    for gy in range(0, int(ih), 5):
        for gx in range(0, int(iw), 5):
            ox = 470 + gx / iw * 170
            oy = 5 + gy / ih * 95
            for poly, _ in CONTINENTS:
                if _inside(ox, oy, poly):
                    d.ellipse([ix0 + 2 + gx - 1, iy0 + 14 + gy - 1,
                               ix0 + 2 + gx + 1, iy0 + 14 + gy + 1], fill=dot)
                    break
    for n, px, py, _ in PINS:
        if 470 <= px <= 640 and 5 <= py <= 100:
            pin(d, ix0 + 2 + (px - 470) / 170 * iw,
                iy0 + 14 + (py - 5) / 95 * ih, n, r=6)
    # pins: 1-3 big with gold ring, 4-13 normal, 14-34 small
    for n, px, py, _ in PINS:
        cx, cy = x + px * sx, y + py * sy
        if n <= 3:
            pin(d, cx, cy, n, r=10, ring=True)
        elif n <= 13:
            pin(d, cx, cy, n, r=9)
        else:
            pin(d, cx, cy, n, r=6)
    # city labels (1-13 only) with paper halo + grey leader lines
    lf = SANS_B(10)
    for lab, px, py, dx, dy in LABELS:
        cx, cy = x + px * sx, y + py * sy
        lx, ly = cx + dx, cy + dy
        if abs(dx) > 15 or abs(dy) > 8:
            d.line([cx, cy, lx + (4 if dx > 0 else -4), ly + 4],
                   fill=(150, 150, 150), width=1)
        text_halo(d, (lx, ly), lab, lf, INK)
    # legend: 7 region dots + names in the empty bottom-right ocean corner
    lx = x + w - 470
    ly = y + h - 14
    for reg in REGION_ORDER:
        d.ellipse([lx, ly + 1, lx + 6, ly + 7], fill=REGION[reg])
        d.text((lx + 9, ly), reg, font=SANS(10), fill=INK)
        lx += 9 + d.textlength(reg, font=SANS(10)) + 12


# ------------------------------------------------------------------ data
HEROES = [
    dict(n=1, tag="CLIMATE · MIDDLE EAST", region="MIDDLE EAST", flag="tr",
         head="COP31 collapses: no deal as EU walks out over fossil fuels",
         body="After a record 49-hour overtime, the Antalya talks end with no pact — the first failure since Copenhagen 2009. (Reuters / The Hindu)",
         num="$120bn", num_lab="climate-finance target fell out",
         ill="cop31"),
    dict(n=2, tag="DEFENCE · EUROPE", region="EUROPE", flag="nato",
         head="NATO Council meets as Poland presses for more eastern troops",
         body="Warsaw seeks Eastern Sentry reinforcements after three Russian Kh-101 cruise missiles fell in Poland on Friday. (Reuters)",
         num="3", num_lab="Russian cruise missiles fell in Poland",
         ill="nato"),
    dict(n=3, tag="MARKETS · ASIA", region="ASIA", flag="tw",
         head="Taiwan bans short selling as shares reel from 17.5% weekly rout",
         body="The FSC bans short sales at or below the flat price from today and readies a NT$500bn stabilisation fund. (FSC / CNA)",
         num="−17.5%", num_lab="Taiex weekly rout",
         ill="taipei"),
]

SMALL = [
    dict(n=4, region="ASIA", flag="kr", icon="bars",
         head="Kospi slides 3–4% as AI-bubble fears mount",
         body="Samsung and SK Hynix lead the fall; Seoul readies a fund. (Al Jazeera)",
         ill="chart"),
    dict(n=5, region="ASIA", flag="in", icon="ball",
         head="India v NZ, Day 5: NZ 157/4 at lunch",
         body="Conway 65, Ravindra 37; NZ still 195 behind. (Reuters)",
         ill="cricket"),
    dict(n=6, region="AFRICA", flag="ly", icon="search",
         head="UN urges probe into Benghazi attacks",
         body="UNSMIL calls for an independent inquiry into Sunday’s port strikes. (UNSMIL)",
         ill="port"),
    dict(n=7, region="OCEANIA", flag="au", icon="box",
         head="Albanese: COP31 failure, ‘difficult times’",
         body="Australia’s PM blames difficult geopolitics for the failure. (AFP)",
         ill="skyline"),
    dict(n=8, region="EUROPE", flag="fi", icon="ship",
         head="Russian cargo ship still ablaze off Finland",
         body="The vessel burns after an attack; tugs move in as the fire continues. (AP)",
         ill="blast"),
    dict(n=9, region="ASIA", flag="mm", icon="box",
         head="Myanmar junta calls ASEAN decision ‘unfair’",
         body="The army-backed government hits back after ASEAN’s rebuke. (AFP)",
         ill="asean"),
    dict(n=10, region="MIDDLE EAST", flag="bh", icon="globe",
         head="Bahrain demands UN action after Iran strike",
         body="Manama seeks action over the attack. (Arab News)",
         ill="un"),
    dict(n=11, region="MIDDLE EAST", flag="lb", icon="shield",
         head="Lebanon army seizes 264 kg of explosives",
         body="Three held after the haul is found; residents sift rubble. (Arab News)",
         ill="haul"),
    dict(n=12, region="ASIA", flag="kr", icon="book",
         head="Seoul minister quits in exam scandal",
         body="The minister resigns over an AI exam-cheating scandal. (Reuters)",
         ill="exam"),
    dict(n=13, region="EUROPE", flag="dk", icon="stars",
         head="Denmark takes Russian visa curbs to EU",
         body="Copenhagen puts its proposals to EU envoys. (Reuters)",
         ill="eu"),
]

# list 14-34: (number, region, flag, headline)
LIST = [
    (14, "AMERICAS", "us", "Hawks urge Trump to strike Iran again; Trump says no rush. (Reported 23 Nov)"),
    (15, "AMERICAS", "us", "NYT: Nvidia-linked Alice Huang was in contact with a Chinese spy officer. (NYT)"),
    (16, "ASIA", "kr", "Samsung Securities hacked; customers’ personal data leaked. (Yonhap)"),
    (17, "EUROPE", "eu", "WeRide to deploy 1,000 robotaxis across Europe, its CEO says. (Company)"),
    (18, "GLOBAL", "globe", "Gold jumps nearly 2% to $3,603 an ounce. (Market wire)"),
    (19, "ASIA", "cn", "Central bank injects ¥499.5bn in overnight reverse repos. (PBoC)"),
    (20, "ASIA", "cn", "STAR50 index down 3%; Shanghai Composite slips below 3,500. (Market wire)"),
    (21, "ASIA", "vn", "Nghi Son refinery secures crude supplies through January. (Company)"),
    (22, "ASIA", "kr", "Finance chief to explain the market stabilisation fund today. (Blue House)"),
    (23, "ASIA", "tw", "Premier to meet industry chiefs on market measures. (Taiwan govt)"),
    (24, "AFRICA", "za", "South Africa v Bangladesh Test begins today. (Cricket)"),
    (25, "AMERICAS", "us", "Trump to speak on US families at the Justice Dept, 16:30 EST. (White House)"),
    (26, "GLOBAL", "globe", "Starlink-1114 falls back to Earth over the Atlantic, 02:11 UTC. (Space-Track)"),
    (27, "ASIA", "kr", "Defence chief: Cheonghae extension is no part of a US–Iran war. (Defence ministry)"),
    (28, "MIDDLE EAST", "sa", "MBS meets Bulgaria’s PM Radev in Riyadh. (Arab News)"),
    (29, "ASIA", "pk", "Minister voices hope for a US–Iran deal. (Arab News)"),
    (30, "ASIA", "bd", "Dhaka plans 25,000 SME entrepreneurs and 2.5m jobs by 2031. (Daily Global Nation)"),
    (31, "ASIA", "ph", "Manila transport strike begins, running to Nov 24. (GMA News)"),
    (32, "ASIA", "in", "IFFI 2026 hosts a BRICS film roundtable. (PTI)"),
    (33, "ASIA", "in", "Amit Shah stresses self-reliance in Arunachal Pradesh. (PTI)"),
    (34, "ASIA", "in", "Tamil Nadu crush Bihar by 99 runs in the Mushtaq Ali Trophy. (SportzCraazy)"),
]

# UTC strip dots: (minutes from 00:00 UTC, story number, region)
UTC_DOTS = [
    (0, 4, "ASIA"), (21, 5, "ASIA"), (60, 3, "ASIA"), (109, 27, "ASIA"),
    (114, 15, "AMERICAS"), (120, 7, "OCEANIA"), (131, 26, "GLOBAL"),
    (480, 24, "AFRICA"), (1290, 25, "AMERICAS"),
]


def flag_headline(draw, x, y, text, fnt, max_w_full, flag_w, box, line_h):
    """Headline with a flag on its first line: line 1 is narrower
    (flag occupies the left), later lines use the full width."""
    first_w = max_w_full - flag_w - 6
    words = text.split()
    lines, cur, w_idx = [], "", 0
    for w in words:
        trial = (cur + " " + w).strip()
        lim = first_w if w_idx == 0 else max_w_full
        if draw.textlength(trial, font=fnt) <= lim:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            w_idx = 1
    if cur:
        lines.append(cur)
    yy = y
    for i, ln in enumerate(lines):
        lx = x + (flag_w + 6 if i == 0 else 0)
        tw = draw.textlength(ln, font=fnt)
        if box is not None:
            if lx < box[0] or lx + tw > box[2] or yy < box[1] or yy + fnt.size > box[3]:
                VIOLATIONS.append(f"text overflow {text[:28]!r} at y={yy}")
        draw.text((lx, yy), ln, font=fnt, fill=INK)
        yy += line_h
    return yy


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 10
    y = 0

    # ---- navy header (R1): title + gold date + stats + globe + edge labels
    d.rectangle([0, 0, W, 50], fill=NAVY)
    # globe between THE WORLD and IN ONE DAY
    t1, t2 = "THE WORLD", "IN ONE DAY"
    tf = SERIF_B(29)
    gw = 24
    total = (d.textlength(t1, font=tf) + gw + 8 +
             d.textlength(t2, font=tf))
    tx = (W - total) / 2
    d.text((tx, 3), t1, font=tf, fill=(255, 255, 255))
    gx = tx + d.textlength(t1, font=tf) + 4
    d.ellipse([gx, 8, gx + 22, 30], outline=GOLD, width=1)
    d.ellipse([gx + 7, 8, gx + 15, 30], outline=GOLD, width=1)
    d.line([gx, 19, gx + 22, 19], fill=GOLD, width=1)
    d.text((gx + gw + 4, 3), t2, font=tf, fill=(255, 255, 255))
    date = "MONDAY 23 NOVEMBER 2026"
    df = SERIF_B(13)
    d.text(((W - d.textlength(date, font=df)) / 2, 32), date, font=df, fill=GOLD)
    rt = "34 STORIES · 7 REGIONS"
    rf = SANS_B(12)
    d.text((W - M - d.textlength(rt, font=rf), 6), rt, font=rf,
           fill=(255, 255, 255))
    ef = SANS(10)
    d.text((M, 33), "No. 23", font=ef, fill=(212, 175, 90))
    er = "ALL TIMES UTC"
    d.text((W - M - d.textlength(er, font=ef), 33), er, font=ef,
           fill=(212, 175, 90))
    # thin gold rules under the navy band
    d.rectangle([0, 51, W, 52], fill=GOLD)
    d.rectangle([0, 54, W, 54], fill=GOLD)
    y = 58

    # ---- three illustrated hero cards (R1 style + AWS upgrades)
    hw = (W - 2 * M - 12) / 3
    hy = 212
    hero_y = y
    for i, s in enumerate(HEROES):
        x0 = M + i * (hw + 6)
        d.rectangle([x0, hero_y, x0 + hw, hero_y + hy], fill=CARD,
                    outline=LINE, width=1)
        ill = {"cop31": ill_cop31, "nato": ill_nato,
               "taipei": ill_taipei}[s["ill"]]
        ill(d, x0 + 1, hero_y + 1, hw - 2, 86)
        # navy number circle top-left on the illustration
        ncx, ncy = x0 + 13, hero_y + 13
        d.ellipse([ncx - 11, ncy - 11, ncx + 11, ncy + 11], fill=NAVY,
                  outline=(255, 255, 255), width=1)
        nf = SANS_B(13)
        nt = str(s["n"])
        d.text((ncx - d.textlength(nt, font=nf) / 2, ncy - 9), nt, font=nf,
               fill=(255, 255, 255))
        # label line: flag + small-caps label in region colour
        ty = hero_y + 90
        flag(d, x0 + 6, ty, 20, 14, s["flag"])
        lf2 = SANS_B(11)
        d.text((x0 + 30, ty + 1), s["tag"], font=lf2, fill=REGION[s["region"]])
        ty = ty + 16
        ty = text_box(d, (x0 + 6, ty), s["head"], SERIF_B(18), INK, hw - 12,
                      line_h=20, box=(x0, ty, x0 + hw, hero_y + hy),
                      max_lines=2)
        ty = text_box(d, (x0 + 6, ty + 2), s["body"], SANS(11), INK, hw - 12,
                      line_h=13, box=(x0, ty + 2, x0 + hw, hero_y + hy),
                      max_lines=2)
        # bottom row: ONE red number + label, REPORTED pill right
        ry = hero_y + 172
        rnf = SERIF_B(36)
        d.text((x0 + 6, ry), s["num"], font=rnf, fill=RED)
        nw = d.textlength(s["num"], font=rnf)
        text_box(d, (x0 + 12 + nw, ry + 12), s["num_lab"], SANS(10), INK,
                 hw - 74 - nw, line_h=12,
                 box=(x0 + 12 + nw, ry + 12, x0 + hw - 62, hero_y + hy),
                 max_lines=2)
        pill(d, x0 + hw - 60, ry + 12, "REPORTED")
    y = hero_y + hy + 6

    # ---- big dotted world map (R1 style + AWS upgrades)
    d.text((M, y), "WHERE IT HAPPENED — ALL 34 STORIES", font=SANS_B(12),
           fill=INK)
    y += 18
    map_h = 150
    draw_map(img, d, M, y, W - 2 * M, map_h)
    y = y + map_h + 6

    # ---- small cards 4-13: 5x2 grid, region top border + banner + flag
    cw = (W - 2 * M - 24) / 5
    chh = 104
    for row in range(2):
        for col in range(5):
            s = SMALL[row * 5 + col]
            x0 = M + col * (cw + 6)
            y0 = y + row * (chh + 6)
            d.rectangle([x0, y0, x0 + cw, y0 + chh], fill=CARD,
                        outline=LINE, width=1)
            d.rectangle([x0, y0, x0 + cw, y0 + 3], fill=REGION[s["region"]])
            banner(d, x0 + 1, y0 + 4, cw - 2, 24, s["ill"])
            # navy number circle on the banner
            ncx, ncy = x0 + 11, y0 + 16
            d.ellipse([ncx - 9, ncy - 9, ncx + 9, ncy + 9], fill=NAVY,
                      outline=(255, 255, 255), width=1)
            nf2 = SANS_B(11)
            nt = str(s["n"])
            d.text((ncx - d.textlength(nt, font=nf2) / 2, ncy - 8), nt,
                   font=nf2, fill=(255, 255, 255))
            # tiny topic icon top-right of the text area
            topic_icon(d, x0 + cw - 19, y0 + 31, s["icon"])
            ty = y0 + 31
            flag(d, x0 + 6, ty + 1, 20, 14, s["flag"])
            ty2 = flag_headline(d, x0 + 6, ty, s["head"], SERIF_B(13),
                                cw - 12, 20, box=(x0, ty, x0 + cw, y0 + chh),
                                line_h=15)
            text_box(d, (x0 + 6, ty2 + 1), s["body"], SANS(11), GREY, cw - 12,
                     line_h=12, box=(x0, ty2 + 1, x0 + cw, y0 + chh - 18),
                     max_lines=2)
            pill(d, x0 + cw - 54, y0 + chh - 17, "REPORTED")
    y = y + 2 * chh + 6 + 6

    # ---- THE DAY IN UTC: 24-hour ruler with staggered story dots
    strip_h = 28
    d.rectangle([0, y, W, y + strip_h], fill=NAVY)
    rx0, rx1 = M + 18, W - M
    ry = y + 12
    d.line([rx0, ry, rx1, ry], fill=(180, 190, 210), width=1)
    for hr in (0, 6, 12, 18, 24):
        tx = rx0 + hr / 24 * (rx1 - rx0)
        d.line([tx, ry - 3, tx, ry + 3], fill=(255, 255, 255), width=1)
        lab = f"{hr:02d}"
        d.text((tx - d.textlength(lab, font=SANS_B(7)) / 2, y + 21), lab,
               font=SANS_B(7), fill=(255, 255, 255))
    # moon at 00, sun at 12 (gold line art, clear of the 00:00 dot)
    mx = rx0 - 16
    d.ellipse([mx, ry - 4, mx + 8, ry + 4], outline=GOLD, width=1)
    d.ellipse([mx + 3, ry - 5, mx + 9, ry + 3], fill=NAVY)
    sx12 = rx0 + 12 / 24 * (rx1 - rx0)
    d.ellipse([sx12 - 4, ry - 4, sx12 + 4, ry + 4], outline=GOLD, width=1)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([sx12 + 5 * math.cos(a), ry + 5 * math.sin(a),
                sx12 + 7 * math.cos(a), ry + 7 * math.sin(a)], fill=GOLD,
               width=1)
    # story dots stagger above/below the ruler so the 00:00-02:11 cluster
    # never overlaps
    for i, (mins, n, reg) in enumerate(UTC_DOTS):
        cx = rx0 + mins / 1440 * (rx1 - rx0)
        cy = ry - 6 if i % 2 == 0 else ry + 6
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=REGION[reg],
                  outline=(255, 255, 255), width=1)
        nf3 = SANS_B(8)
        t = str(n)
        d.text((cx - d.textlength(t, font=nf3) / 2, cy - 6), t, font=nf3,
               fill=(255, 255, 255))
    y += strip_h + 6

    # ---- stories 14-34 list (R1 style + AWS: region dot, flag, pill)
    lf = SANS(12)
    lf_b = SANS_B(12)
    for n, reg, fl, body in LIST:
        # region dot
        d.ellipse([M + 1, y + 3, M + 7, y + 9], fill=REGION[reg])
        num = f"{n}."
        d.text((M + 11, y), num, font=lf_b, fill=INK)
        flag(d, M + 36, y + 1, 14, 10, fl)
        # headline (reserve room for the pill on the right)
        pw = pill(d, W - M - 56, y - 1, "REPORTED")
        text_box(d, (M + 56, y), body, lf, INK, W - M - 56 - (M + 56),
                 line_h=13, box=(M + 56, y, W - M - 62, y + 13), max_lines=1)
        # thin dotted separator
        for gx in range(M, W - M, 5):
            d.ellipse([gx, y + 12, gx + 1, y + 13], fill=(205, 195, 175))
        y += 13
    y += 4

    # ---- DATE CHECK: checklist + tear-off calendar icon
    d.rectangle([M, y, W - M, y + 40], outline=RED, width=2, fill=(255, 246, 240))
    # calendar icon MON 23 NOV (~34px)
    cx0, cy0 = M + 8, y + 3
    d.rounded_rectangle([cx0, cy0, cx0 + 34, cy0 + 34], radius=3,
                        fill=(255, 255, 255), outline=RED, width=1)
    d.rectangle([cx0, cy0, cx0 + 34, cy0 + 10], fill=RED)
    d.text((cx0 + 8, cy0 + 1), "MON", font=SANS_B(8), fill=(255, 255, 255))
    d.text((cx0 + 9, cy0 + 12), "23", font=SANS_B(14), fill=INK)
    d.text((cx0 + 7, cy0 + 26), "NOV", font=SANS_B(8), fill=GREY)
    chk = SANS(11)
    items = [
        ("All 34 stories dated Mon 23 Nov 2026 (UTC)", "7 regions covered"),
        ("34 of 34 REPORTED", "Sources: 20+ outlets"),
    ]
    for r, (a, b) in enumerate(items):
        yy = y + 6 + r * 14
        for cxx, txt in ((M + 52, a), (M + 52 + 430, b)):
            d.text((cxx, yy), "✓", font=SANS_B(11), fill=GREEN_TICK)
            d.text((cxx + 14, yy), txt, font=chk, fill=INK)
    y += 40
    print("final y:", y, "(canvas 1024)")

    # ---- very faint paper grain (2-3% opacity)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    rnd = random.Random(23)
    for _ in range(2600):
        gx, gy = rnd.randrange(W), rnd.randrange(H)
        od.point((gx, gy), fill=(60, 50, 30, 10))
    img.paste(overlay, (0, 0), overlay)

    img.save("entry.png")
    print("saved entry.png", img.size)
    if VIOLATIONS:
        print(f"GAP SCAN: {len(VIOLATIONS)} violations")
        for v in VIOLATIONS:
            print("  -", v)
    else:
        print("GAP SCAN: 0 violations (all text inside its box, left/right checked)")


if __name__ == "__main__":
    main()
