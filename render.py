#!/usr/bin/env python3
"""render.py — THE WORLD IN ONE DAY, MONDAY 23 NOVEMBER 2026 (News 23, round 3).

Draws entry.png (1024x1024) from the facts in SOURCES.md, using only files
bundled in this repository: fonts/ (Liberation, SIL OFL), flags/*.svg and
map_data.py. No network, no system fonts, no emoji. Deterministic: rendering
twice produces byte-identical output (verified in-process on every run).

Layout (AWS Quick Smart feedback applied on top of the News 22 R9 design
language — cream paper, navy header, serif masthead, red italic subtitle,
big red fact numbers, real world map, tiny SVG flags, green REPORTED pills,
THE DAY IN UTC timeline strip, DATE CHECK box):
  header (navy) -> lead story 1, headline ~34px -> stories 2-5, headline +
  one line -> stories 6-13, headline-only cards -> world map with a
  Europe/Middle East close-up inset -> UTC timeline 00-24h with numbered
  story dots -> list 14-34 (max 8 words each) -> DATE CHECK box.
"""
import hashlib
import io
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from map_data import LAND  # noqa: E402  (bundled local map outlines)

W, H = 1024, 1024
CREAM = (245, 238, 220)
PAPER = (255, 253, 246)
NAVY = (20, 38, 62)
NAVY2 = (28, 52, 84)
RED = (196, 42, 42)
GOLD = (201, 162, 39)
GREEN = (30, 125, 60)
SEA = (223, 233, 242)
LAND_FILL = (143, 168, 186)
LAND_LINE = (90, 120, 140)
INK = (32, 32, 32)
GREY = (96, 92, 84)
CARD_LINE = (216, 207, 184)
AXIS_BLUE = (127, 163, 200)

FDIR = os.path.join(HERE, "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = "LiberationSerif-Regular.ttf"
SERIF_B = "LiberationSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SERIF_BI = "LiberationSerif-BoldItalic.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS_I = "LiberationSans-Italic.ttf"

# ---------------------------------------------------------------- text log
# Every piece of drawn text is registered (label, x0, y0, x1, y1) so the gap
# scan can prove zero text collisions / truncations / overflows.
BOXES = []
ISSUES = []


def T(d, x, y, s, fnt, fill, anchor="la", label=None, stroke_w=0,
      stroke_fill=(255, 255, 255)):
    bbox = d.textbbox((x, y), s, font=fnt, anchor=anchor,
                      stroke_width=stroke_w)
    BOXES.append((label or s[:28], bbox[0], bbox[1], bbox[2], bbox[3]))
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor,
           stroke_width=stroke_w, stroke_fill=stroke_fill)
    return bbox


def wrap(d, s, fnt, width):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, s, fnt, fill, width, lh, label=None, anchor="la"):
    lines = wrap(d, s, fnt, width)
    for i, line in enumerate(lines):
        T(d, x, y + i * lh, line, fnt, fill, anchor=anchor,
          label=(label or "") + f" L{i+1}")
    return y + len(lines) * lh


# ------------------------------------------------------- mini SVG rasterizer
# Supports the subset used by flags/*.svg: rect, circle, ellipse, polygon.
# Renders supersampled, then downscales for crisp 20x14 flags. No network,
# no external tools: the flags really are the SVG files in this repo.
def raster_flag(path, w, h, scale=6):
    tree = ET.parse(path)
    root = tree.getroot()
    vb = [float(v) for v in root.get("viewBox", "0 0 60 42").split()]
    _, _, vbw, vbh = vb
    big = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    sx, sy = w * scale / vbw, h * scale / vbh

    def pts(attr):
        nums = [float(v) for v in attr.replace(",", " ").split()]
        return [(nums[i] * sx, nums[i + 1] * sy)
                for i in range(0, len(nums), 2)]

    for el in root:
        tag = el.tag.split("}")[-1]
        fill = el.get("fill", "#000000")
        if tag == "rect":
            x0 = float(el.get("x", 0)) * sx
            y0 = float(el.get("y", 0)) * sy
            x1 = x0 + float(el.get("width")) * sx
            y1 = y0 + float(el.get("height")) * sy
            bd.rectangle([x0, y0, x1, y1], fill=fill)
        elif tag == "circle":
            cx, cy, r = (float(el.get("cx")) * sx, float(el.get("cy")) * sy,
                         float(el.get("r")) * sx)
            bd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
        elif tag == "ellipse":
            cx, cy = float(el.get("cx")) * sx, float(el.get("cy")) * sy
            rx, ry = float(el.get("rx")) * sx, float(el.get("ry")) * sy
            bd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
        elif tag == "polygon":
            bd.polygon(pts(el.get("points")), fill=fill)
    return big.resize((w, h), Image.LANCZOS)


FLAG_CACHE = {}


def flag(name, w=20, h=14):
    if name not in FLAG_CACHE:
        FLAG_CACHE[name] = raster_flag(
            os.path.join(HERE, "flags", name + ".svg"), w, h)
    return FLAG_CACHE[name]


def paste_flag(img, x, y, name):
    img.paste(flag(name), (x, y), flag(name))
    img_draw = ImageDraw.Draw(img)
    img_draw.rectangle([x, y, x + 19, y + 13], outline=(120, 120, 120))


# ------------------------------------------------------------------- content
# Facts: SOURCES.md only. Regions: East Asia, South Asia, Southeast Asia,
# Middle East, Europe, Africa, Americas & Oceania.
LEAD = {
    "num": 1,
    "headline": ["COP31 collapses: no deal as EU walks out",
                 "over fossil fuels"],
    "body": ("Antalya talks fail \u2014 the first collapse since Copenhagen "
             "2009; the $120bn finance target falls out."),
    "meta": "Reuters \u00b7 The Hindu \u2014 ANTALYA",
}

MID = [  # stories 2-5: headline + one line
    {"num": 2, "flag": "nato",
     "headline": "NATO Council meets as Poland presses for more eastern troops",
     "body": "Warsaw presses for Eastern Sentry reinforcements."},
    {"num": 3, "flag": "taiwan",
     "headline": "Taiwan bans short selling as shares reel from 17.5% weekly rout",
     "body": "FSC measures take effect; Taiex fell 7,641.83 in a week."},
    {"num": 4, "flag": "korea",
     "headline": "Kospi slides 3\u20134% as AI-bubble fears mount",
     "body": "Samsung and SK Hynix lead the fall in Seoul."},
    {"num": 5, "flag": "india",
     "headline": "India v NZ, Day 5: NZ 157/4 at lunch",
     "body": "Conway 65, Ravindra 37; NZ still 195 behind."},
]

SMALL = [  # stories 6-13: headline-only cards
    {"num": 6, "flag": "libya",
     "headline": "UN urges probe into Benghazi attacks"},
    {"num": 7, "flag": "australia",
     "headline": "Albanese: COP31 failure shows \u2018difficult times\u2019"},
    {"num": 8, "flag": "finland",
     "headline": "Russian cargo ship still ablaze off Finland"},
    {"num": 9, "flag": "myanmar",
     "headline": "Myanmar junta calls ASEAN decision \u2018unfair\u2019"},
    {"num": 10, "flag": "bahrain",
     "headline": "Bahrain demands UN action after Iran strike"},
    {"num": 11, "flag": "lebanon",
     "headline": "Lebanon army seizes 264 kg of explosives"},
    {"num": 12, "flag": "korea",
     "headline": "Seoul education chief quits in exam scandal"},
    {"num": 13, "flag": "denmark",
     "headline": "Denmark takes Russian visa curbs to EU"},
]

# (story, bold lead, rest) — every item max 8 words, one line at 13px.
LIST = [
    (14, "Hawks urge Trump ", "to strike Iran; Trump: no rush"),
    (15, "NYT: Nvidia\u2019s Huang ", "met Chinese spy officer"),
    (16, "Samsung Securities hacked; ", "data leaked"),
    (17, "WeRide to deploy ", "1,000 robotaxis in Europe"),
    (18, "Gold jumps nearly 2% ", "to $3,603 an ounce"),
    (19, "PBoC injects \u00a5499.5bn ", "in overnight repos"),
    (20, "STAR50 down 3%; ", "Shanghai below 3,500"),
    (21, "Nghi Son refinery ", "secures crude to January"),
    (22, "Finance chief to explain ", "stabilisation fund"),
    (23, "Premier meets industry chiefs ", "on markets"),
    (24, "South Africa v Bangladesh ", "Test begins today"),
    (25, "Trump speaks on US families ", "at Justice Dept"),
    (26, "Starlink-1114 falls back ", "over the Atlantic"),
    (27, "Defence chief: Cheonghae ", "not in US\u2013Iran war"),
    (28, "MBS meets Bulgaria\u2019s PM Radev ", "in Riyadh"),
    (29, "Minister voices hope ", "for a US\u2013Iran deal"),
    (30, "Dhaka plans 25,000 entrepreneurs, ", "2.5m jobs"),
    (31, "Manila transport strike begins, ", "to Nov 24"),
    (32, "IFFI 2026 hosts ", "a BRICS film roundtable"),
    (33, "Amit Shah stresses self-reliance ", "in Arunachal"),
    (34, "Tamil Nadu crush Bihar ", "by 99 runs"),
]

# Map pins: (story, lon, lat, display x, display y, label, label offset)
# Display positions are the true projection, nudged only inside the crowded
# Europe / Middle East cluster so 18px pins never touch. Labels only for
# stories 1-13; the Europe/Middle East labels live in the close-up inset.
MAP_X0, MAP_Y0, MAP_W, MAP_H = 32, 600, 960, 138
LAT_MAX, LAT_MIN = 72, -56


def proj(lon, lat):
    return (MAP_X0 + (lon + 180) / 360 * MAP_W,
            MAP_Y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * MAP_H)


PINS = [
    (1, 30.7, 36.9, 600, 642, None, None),
    (2, 4.35, 50.85, 556, 622, None, None),
    (3, 121.5, 25.0, 836, 652, "TAIPEI", (13, -2, "la")),
    (4, 127.0, 37.5, 851, 639, None, None),
    (5, 77.2, 28.6, 718, 648, "NEW DELHI", (0, -20, "ma")),
    (6, 20.1, 32.1, 578, 652, None, None),
    (7, 149.1, -35.3, 910, 716, "CANBERRA", (0, -20, "ma")),
    (8, 24.9, 60.2, 604, 610, None, None),
    (9, 96.1, 19.8, 768, 657, "NAYPYIDAW", (0, 16, "ma")),
    (10, 50.6, 26.2, 648, 654, None, None),
    (11, 35.5, 33.9, 620, 648, None, None),
    (12, 127.0, 37.5, 871, 625, "SEOUL", (13, -6, "la")),
    (13, 12.6, 55.7, 584, 614, None, None),
]

# Inset close-up: lon -12..56, lat 22..62, box (40, 624)-(284, 734).
IN_X0, IN_Y0, IN_X1, IN_Y1 = 40, 624, 284, 734
IN_LON0, IN_LON1, IN_LAT0, IN_LAT1 = -12, 56, 22, 62


def in_proj(lon, lat):
    return (IN_X0 + (lon - IN_LON0) / (IN_LON1 - IN_LON0) * (IN_X1 - IN_X0),
            IN_Y0 + (IN_LAT1 - lat) / (IN_LAT1 - IN_LAT0) * (IN_Y1 - IN_Y0))


INSET_PINS = [  # (story, lon, lat, label, label offset)
    (2, 4.35, 50.85, "BRUSSELS", (0, 14, "ma")),
    (13, 12.6, 55.7, "COPENHAGEN", (-13, -10, "ra")),
    (8, 24.9, 60.2, "HELSINKI", (13, -2, "la")),
    (1, 30.7, 36.9, "ANTALYA", (-13, -8, "ra")),
    (11, 35.5, 33.9, "BEIRUT", (13, -6, "la")),
    (10, 50.6, 26.2, "MANAMA", (13, -6, "la")),
    (6, 20.1, 32.1, "BENGHAZI", (-13, -6, "ra")),
]

# Display-only nudges inside the close-up inset (keeps the long COPENHAGEN
# label inside the box): story -> (dx, dy) in pixels.
INSET_NUDGE = {13: (12, 0)}

# UTC timeline dots: (story, hour in UTC, short label for the legend)
UTC_EVENTS = [
    (4, 0.00, "00:00 [4] Kospi -3% at Seoul open"),
    (5, 0.35, "00:21 [5] NZ 157/4"),
    (3, 1.00, "01:00 [3] Taiwan ban in force"),
    (26, 2.18, "02:11 [26] Starlink re-enters"),
    (24, 8.00, "08:00 [24] SA v BAN Test"),
    (25, 21.50, "21:30 [25] Trump speaks"),
]


def pill(d, x, y, text, fnt, fill=GREEN):
    w = int(d.textlength(text, font=fnt)) + 14
    h = 17
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=fill)
    T(d, x + w / 2, y + 2, text, fnt, (255, 255, 255), anchor="ma",
      label="REPORTED pill")
    return w


def draw_pin(d, cx, cy, num, label=None, off=None):
    """18px pin, bold number >=11px; label offset (dx, dy, anchor) from centre."""
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
              outline=(255, 255, 255), width=1)
    T(d, cx, cy, str(num), font(SANS_B, 11), (255, 255, 255),
      anchor="mm", label=f"pin {num}")
    if label and off:
        dx, dy, anchor = off
        T(d, cx + dx, cy + dy, label, font(SANS_B, 12), NAVY,
          anchor=anchor, label=f"label {label}", stroke_w=2)


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------- header, navy
    d.rectangle([0, 0, W, 138], fill=NAVY)
    T(d, 512, 14, "THE WORLD IN ONE DAY", font(SERIF_B, 46),
      (255, 255, 255), anchor="ma", label="masthead")
    T(d, 512, 68, "MONDAY 23 NOVEMBER 2026", font(SERIF_BI, 21),
      (229, 72, 77), anchor="ma", label="subtitle")
    stats = [("34", " STORIES"), ("7", " REGIONS"), ("6", " UTC MOMENTS")]
    parts, total = [], 0
    for num, lab in stats:
        nw = d.textlength(num, font=font(SERIF_B, 32))
        lw = d.textlength(lab, font=font(SANS_B, 13))
        parts.append((num, lab, nw, lw))
        total += nw + lw
    total += 2 * 44  # gaps between the three groups
    x = 512 - total / 2
    for num, lab, nw, lw in parts:
        T(d, x, 100, num, font(SERIF_B, 32), (229, 72, 77),
          label=f"stat {num}")
        T(d, x + nw + 2, 110, lab, font(SANS_B, 13), (255, 255, 255),
          label=f"stat {lab.strip()}")
        x += nw + lw + 44
    d.rectangle([0, 136, W, 138], fill=GOLD)

    # ------------------------------------------------------- lead story 1
    d.rectangle([24, 148, 1000, 274], fill=PAPER, outline=CARD_LINE)
    T(d, 40, 156, "1", font(SERIF_B, 64), RED, label="num 1")
    T(d, 92, 152, LEAD["headline"][0], font(SERIF_B, 34), INK,
      label="lead headline 1")
    T(d, 92, 194, LEAD["headline"][1], font(SERIF_B, 34), INK,
      label="lead headline 2")
    T(d, 92, 234, LEAD["body"], font(SANS, 13), INK, label="lead body")
    T(d, 92, 256, LEAD["meta"], font(SANS, 12), GREY, label="lead meta")
    pill(d, 908, 252, "REPORTED", font(SANS_B, 10))

    # ------------------------------------------------------- stories 2-5
    mid_x = [24, 514]
    mid_y = [284, 356]
    for i, s in enumerate(MID):
        cx, cy = mid_x[i % 2], mid_y[i // 2]
        d.rectangle([cx, cy, cx + 478, cy + 68], fill=PAPER,
                    outline=CARD_LINE)
        T(d, cx + 10, cy + 9, str(s["num"]), font(SANS_B, 16), RED,
          label=f"num {s['num']}")
        paste_flag(img, cx + 34, cy + 10, s["flag"])
        draw_wrapped(d, cx + 62, cy + 8, s["headline"], font(SANS_B, 15),
                     INK, 406, 18, label=f"headline {s['num']}")
        T(d, cx + 10, cy + 47, s["body"], font(SANS, 13), INK,
          label=f"body {s['num']}")
        pill(d, cx + 408, cy + 45, "REPORTED", font(SANS_B, 9))

    # ------------------------------------------------------- stories 6-13
    sm_x = [24, 268, 512, 756]
    sm_y = [434, 502]
    for i, s in enumerate(SMALL):
        cx, cy = sm_x[i % 4], sm_y[i // 4]
        d.rectangle([cx, cy, cx + 232, cy + 64], fill=PAPER,
                    outline=CARD_LINE)
        T(d, cx + 8, cy + 7, str(s["num"]), font(SANS_B, 14), RED,
          label=f"num {s['num']}")
        paste_flag(img, cx + 30, cy + 8, s["flag"])
        draw_wrapped(d, cx + 8, cy + 27, s["headline"], font(SANS_B, 14),
                     INK, 216, 17, label=f"headline {s['num']}")

    # ------------------------------------------------------- world map
    d.rectangle([24, 576, 1000, 742], fill=SEA, outline=NAVY)
    T(d, 32, 582, "WHERE IT HAPPENED \u2014 13 PLACES", font(SANS_B, 12),
      NAVY, label="map title")
    T(d, 992, 583,
      "7 REGIONS: EAST ASIA \u00b7 SOUTH ASIA \u00b7 SOUTHEAST ASIA \u00b7 "
      "MIDDLE EAST \u00b7 EUROPE \u00b7 AFRICA \u00b7 AMERICAS & OCEANIA",
      font(SANS_B, 10), NAVY, anchor="ra", label="map regions")
    for poly in LAND:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND_FILL,
                  outline=LAND_LINE)
    # Close-up inset (its own image, so land is clipped to the box).
    inset = Image.new("RGB", (IN_X1 - IN_X0, IN_Y1 - IN_Y0), SEA)
    idr = ImageDraw.Draw(inset)
    for poly in LAND:
        idr.polygon([(x - IN_X0, y - IN_Y0)
                     for x, y in (in_proj(lon, lat) for lon, lat in poly)],
                    fill=LAND_FILL, outline=LAND_LINE)
    img.paste(inset, (IN_X0, IN_Y0))
    T(d, 40, 606, "EUROPE & MIDDLE EAST \u2014 CLOSE-UP", font(SANS_B, 10),
      NAVY, label="inset tag")
    d.rectangle([IN_X0, IN_Y0, IN_X1, IN_Y1], outline=NAVY, width=2)
    for num, lon, lat, label, off in INSET_PINS:
        cx, cy = in_proj(lon, lat)
        nx, ny = INSET_NUDGE.get(num, (0, 0))
        draw_pin(d, cx + nx, cy + ny, num, label, off)
    for num, lon, lat, dx, dy, label, off in PINS:
        draw_pin(d, dx, dy, num, label, off)

    # ------------------------------------------------------- UTC timeline
    d.rectangle([24, 750, 1000, 812], fill=NAVY)
    T(d, 36, 758, "THE DAY IN UTC", font(SANS_B, 13), (255, 255, 255),
      label="utc title")
    axis_y = 784
    d.line([(36, axis_y), (988, axis_y)], fill=AXIS_BLUE, width=2)
    for num, hour, _ in UTC_EVENTS:
        cx = 36 + hour / 24 * 952
        cy = axis_y
        if num == 5:  # 00:21 sits 14px from the 00:00 dot: stagger it below
            cy = axis_y + 12
            d.line([(cx, axis_y + 2), (cx, cy - 6)], fill=AXIS_BLUE, width=2)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        T(d, cx, cy, str(num), font(SANS_B, 10), (255, 255, 255),
          anchor="mm", label=f"utc dot {num}")
    legend = "  \u00b7  ".join(lab for _, _, lab in UTC_EVENTS)
    T(d, 512, 794, legend, font(SANS, 11), (255, 255, 255), anchor="ma",
      label="utc legend")

    # ------------------------------------------------------- list 14-34
    T(d, 24, 822, "THE REST OF THE DAY \u2014 14\u201334", font(SANS_B, 12),
      NAVY, label="list header")
    col_x = [24, 353, 682]
    for col in range(3):
        y = 842
        for num, bold, rest in LIST[col * 7:(col + 1) * 7]:
            fx, fnum = font(SANS_B, 13), font(SANS_B, 13)
            fr = font(SANS, 13)
            nx = col_x[col]
            T(d, nx, y, str(num), fnum, RED, label=f"list num {num}")
            tx = nx + d.textlength(str(num) + " ", font=fnum)
            T(d, tx, y, bold, font(SANS_B, 13), INK,
              label=f"list bold {num}")
            bx = tx + d.textlength(bold, font=font(SANS_B, 13))
            T(d, bx, y, rest, fr, INK, label=f"list rest {num}")
            # one-line fit: the whole item must end inside its column.
            end = bx + d.textlength(rest, font=fr)
            if end > col_x[col] + 317:
                ISSUES.append(
                    f"list {num} overflows column by "
                    f"{end - (col_x[col] + 317):.0f}px")
            y += 16

    # ------------------------------------------------------- DATE CHECK box
    d.rectangle([24, 963, 1000, 1016], fill=PAPER, outline=NAVY, width=2)
    T(d, 36, 970, "DATE CHECK \u2014 ", font(SANS_B, 12), NAVY,
      label="datecheck title")
    tw = d.textlength("DATE CHECK \u2014 ", font=font(SANS_B, 12))
    T(d, 36 + tw, 970,
      "Every story above happened, or was first reported, on Monday "
      "23 November 2026.", font(SANS, 12), INK, label="datecheck 1")
    T(d, 36, 986,
      "Left out: items dated 20\u201322 Nov \u2014 Democrats\u2019 House "
      "majority (22 Nov); killer-robot rules (21 Nov). No Israel / Gaza / "
      "West Bank stories.", font(SANS, 12), INK, label="datecheck 2")
    T(d, 36, 1002,
      "Sources: Reuters \u00b7 AFP \u00b7 AP \u00b7 Al Jazeera \u00b7 Arab "
      "News \u00b7 Yonhap \u00b7 NYT \u00b7 CNA \u2014 full list in "
      "SOURCES.md.", font(SANS, 12), INK, label="datecheck 3")
    return img


def gap_scan():
    # 1. pairwise text-box overlap (touching edges are fine)
    for i in range(len(BOXES)):
        li, x0, y0, x1, y1 = BOXES[i]
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            ISSUES.append(f"{li}: outside canvas "
                          f"({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
        for j in range(i + 1, len(BOXES)):
            lj, a0, b0, a1, b1 = BOXES[j]
            if x0 < a1 - 0.5 and a0 < x1 - 0.5 and y0 < b1 - 0.5 and \
                    b0 < y1 - 0.5:
                ISSUES.append(f"overlap: {li} x {lj}")
    # 2. no truncation markers anywhere
    for label, *_ in BOXES:
        if "\u2026" in label:
            ISSUES.append(f"truncation in {label}")
    # 3. story numbers 1-34 exactly once, pins 1-13 present
    seen = [int(l.split()[-1]) for l, *_ in BOXES
            if l.startswith("num ") or l.startswith("list num ")]
    if sorted(seen) != list(range(1, 35)):
        ISSUES.append(f"story numbers not 1-34 exactly once: "
                      f"{sorted(seen)}")
    pins = sorted(int(l.split()[-1]) for l, *_ in BOXES
                  if l.startswith("pin "))
    # pins appear twice (main map + inset) for the 7 close-up stories
    from collections import Counter
    c = Counter(pins)
    if sorted(c) != list(range(1, 14)):
        ISSUES.append(f"pin numbers not 1-13: {sorted(c)}")
    return ISSUES


def main():
    img1 = render()
    buf1 = io.BytesIO()
    img1.save(buf1, format="PNG")
    b1 = buf1.getvalue()
    # determinism: render a second time, bytes must match
    BOXES.clear()
    img2 = render()
    buf2 = io.BytesIO()
    img2.save(buf2, format="PNG")
    b2 = buf2.getvalue()
    if b1 != b2:
        print("DETERMINISM FAIL: second render differs")
        sys.exit(1)
    issues = gap_scan()
    out = os.path.join(HERE, "entry.png")
    with open(out, "wb") as fh:
        fh.write(b1)
    sha = hashlib.sha256(b1).hexdigest()
    print(f"entry.png: {len(b1)} bytes, sha256 {sha}")
    print(f"text boxes tracked: {len(BOXES)}")
    print(f"gap scan: {len(issues)} issue(s)")
    for it in issues:
        print("  - " + it)
    if issues:
        sys.exit(2)


if __name__ == "__main__":
    main()
