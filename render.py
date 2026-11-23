#!/usr/bin/env python3
"""Render News 23 (Monday 23 November 2026) front page, 1024x1024 PNG.
Fresh build from the News 22 R9 design spec. Deterministic, no network.
Story data is inline in this file. Run: python3 render.py
Writes entry.png next to this script, renders twice, checks byte-identity,
then runs a text-only pixel gap scan on every card.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (245, 238, 220)
NAVY = (18, 32, 62)
NAVY2 = (26, 44, 80)
INK = (28, 28, 28)
MUTED = (96, 90, 78)
RED = (196, 30, 30)
GREEN = (34, 139, 34)
BORDER = (190, 180, 165)
CARD = (255, 253, 247)
GOLD = (212, 175, 105)
MAPDOT = (198, 188, 162)
MAPLAND = (232, 222, 196)

FD = "/usr/share/fonts/truetype/dejavu"

def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)

# ---------------------------------------------------------------- stories
# heroes: chip, title, body, caption, source
HEROES = [
    dict(chip="CLIMATE  ·  ANTALYA", kind="cop31",
         title="COP31 collapses: no deal as EU walks out over fossil fuels",
         body=("After a record 49-hour overtime, the Antalya talks end with no "
               "pact \u2014 the first failure since Copenhagen 2009."),
         caption="COP31 president: \u201cthe decisions have not been adopted.\u201d",
         source="Reuters / The Hindu"),
    dict(chip="EUROPE  ·  BRUSSELS", kind="nato",
         title="NATO Council meets as Poland presses for more eastern troops",
         body=("Warsaw seeks Eastern Sentry reinforcements after three Russian "
               "Kh-101 cruise missiles fell in Poland on Friday."),
         caption="Rutte: the alliance \u201cwill defend every inch.\u201d",
         source="Reuters"),
    dict(chip="ASIA  ·  TAIPEI", kind="taiwan",
         title="Taiwan bans short selling as shares reel from 17.5% weekly rout",
         body=("The FSC bans short sales at or below the flat price from today "
               "and readies a NT$500bn stabilisation fund."),
         caption="Taiex closed Friday at 36,033.29.",
         source="FSC / CNA"),
]

# small cards: flag code, headline, body, source
SMALL = [
    dict(flag="KR", head="Kospi slides 3\u20134% as AI-bubble fears mount",
         body="Samsung and SK Hynix lead the fall; Seoul readies a stabilisation fund.",
         source="Al Jazeera"),
    dict(flag="IN", head="India v NZ, Day 5: NZ 157/4 at lunch",
         body="Conway 65, Ravindra 37; NZ still 195 behind India\u2019s 720/9 declared.",
         source="Reuters"),
    dict(flag="LY", head="UN urges probe into Benghazi attacks",
         body="UNSMIL calls for an independent inquiry after Sunday\u2019s port strikes.",
         source="UNSMIL"),
    dict(flag="AU", head="Albanese: COP31 failure shows \u2018difficult times\u2019",
         body="Australia\u2019s PM blames geopolitics as the Antalya talks end with no deal.",
         source="AFP"),
    dict(flag="FI", head="Russian cargo ship still ablaze off Finland",
         body="The vessel burns after an attack; tugs move in as the fire continues.",
         source="AP"),
    dict(flag="MM", head="Myanmar junta calls ASEAN decision \u2018unfair\u2019",
         body="The army-backed government hits back after ASEAN\u2019s rebuke.",
         source="AFP"),
    dict(flag="BH", head="Bahrain demands UN action after Iran strike",
         body="Manama seeks action over the attack on a civilian facility.",
         source="Arab News"),
    dict(flag="LB", head="Lebanon army seizes 264 kg of explosives",
         body="Three arrested after the haul is found; residents sift rubble nearby.",
         source="Arab News"),
    dict(flag="KR", head="Seoul education chief quits in exam scandal",
         body="The minister resigns over an AI cheating scandal in national exams.",
         source="Reuters"),
    dict(flag="DK", head="Denmark takes Russian visa curbs to EU",
         body="Copenhagen puts its proposals to EU envoys after the rapper-plot case.",
         source="Reuters"),
]

# list items 14-34: prefix, body, source
LIST = [
    ("UNITED STATES", "Hawks urge Trump to strike Iran again; Trump says no rush.", "Reported 23 Nov"),
    ("UNITED STATES", "NYT: Nvidia-linked Alice Huang was in contact with a Chinese spy officer.", "NYT"),
    ("SOUTH KOREA", "Samsung Securities hacked; customers\u2019 personal data leaked.", "Yonhap"),
    ("EUROPE", "WeRide to deploy 1,000 robotaxis across Europe, its CEO says.", "Company"),
    ("MARKETS", "Gold jumps nearly 2% to $3,603 an ounce.", "Market wire"),
    ("CHINA", "Central bank injects \u00a5499.5bn in overnight reverse repos.", "PBoC"),
    ("CHINA", "STAR50 index down 3%; Shanghai Composite slips below 3,500.", "Market wire"),
    ("VIETNAM", "Nghi Son refinery secures crude supplies through January.", "Company"),
    ("SOUTH KOREA", "Finance chief to explain the market stabilisation fund today.", "Blue House"),
    ("TAIWAN", "Premier to meet industry chiefs on market measures.", "Taiwan govt"),
    ("SOUTH AFRICA", "South Africa v Bangladesh Test begins today.", "Cricket"),
    ("UNITED STATES", "Trump to speak on US families at the Justice Dept, 16:30 EST.", "White House"),
    ("SPACE", "Starlink-1114 falls back to Earth over the Atlantic, 02:11 UTC.", "Space-Track"),
    ("SOUTH KOREA", "Defence chief: Cheonghae extension is no part of a US\u2013Iran war.", "Defence ministry"),
    ("SAUDI ARABIA", "MBS meets Bulgaria\u2019s PM Radev in Riyadh.", "Arab News"),
    ("PAKISTAN", "Minister voices hope for a US\u2013Iran deal.", "Arab News"),
    ("BANGLADESH", "Dhaka plans 25,000 SME entrepreneurs and 2.5m jobs by 2031.", "Daily Global Nation"),
    ("PHILIPPINES", "Manila transport strike begins, running to Nov 24.", "GMA News"),
    ("INDIA", "IFFI 2026 hosts a BRICS film roundtable.", "IFFI"),
    ("INDIA", "Amit Shah stresses self-reliance in Arunachal Pradesh.", "PTI"),
    ("INDIA", "Tamil Nadu crush Bihar by 99 runs in the Mushtaq Ali Trophy.", "SportzCraazy"),
]

UTC_STRIP = [
    ("00:00 UTC", "Kospi \u22123% at open"),
    ("00:21 UTC", "NZ 157/4 at lunch"),
    ("01:00 UTC", "Taiwan short-sale ban"),
    ("02:11 UTC", "Starlink-1114 re-enters"),
    ("08:00 UTC", "SA v Bangladesh begins"),
    ("21:30 UTC", "Trump at Justice Dept"),
]

# map pins: (lon, lat, label, side, dy) -- side R: label right of pin,
# L: label left of pin; dy shifts the label row (0 = centred on pin)
PINS = [
    (30.7, 36.9, "ANTALYA", "L", -5), (4.35, 50.85, "BRUSSELS", "R", -5),
    (121.56, 25.03, "TAIPEI", "R", -5), (126.98, 37.57, "SEOUL", "R", -5),
    (20.07, 32.12, "BENGHAZI", "L", -5), (151.21, -33.87, "SYDNEY", "L", -5),
    (24.0, 59.8, "GULF OF FINLAND", "R", -5), (50.59, 26.23, "MANAMA", "R", -15),
    (35.50, 33.89, "BEIRUT", "L", 9), (96.08, 19.75, "NAYPYIDAW", "R", 9),
    (46.68, 24.71, "RIYADH", "L", 9), (120.98, 14.60, "MANILA", "R", 9),
    (90.41, 23.81, "DHAKA", "L", -15),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Every story above happened, or was first reported, on Monday 23 November 2026. "
    "Left out as other days\u2019 news: Liverpool 4-0 Man Utd (22 Nov) \u00b7 Las Vegas GP, Verstappen wins "
    "(21\u201322 Nov) \u00b7 Russian corvette Merkury sunk off Libya (22 Nov) \u00b7 Dymer apartment strike "
    "(22 Nov) \u00b7 Hormuz tanker strikes (20\u201322 Nov) \u00b7 Shuri Castle restoration (22 Nov) \u00b7 "
    "Cikande candy-factory fire (22 Nov) \u00b7 Lahore AQI 538 (22 Nov) \u00b7 BepiColombo enters Mercury "
    "orbit (21 Nov) \u00b7 Kerch Bridge strikes (15\u201319 Nov) \u00b7 Peru quake (20 Nov) \u00b7 Shenzhen "
    "summit (19 Nov)."
)

N_STORIES = 3 + len(SMALL) + len(LIST)

# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def wrap_mixed(draw, parts, width):
    """Wrap a line made of (text, font) parts; returns list of part-lists."""
    # flatten to words with their font
    words = []
    for text, fnt in parts:
        for w in text.split(" "):
            words.append((w, fnt))
    lines, cur, cur_w = [], [], 0.0
    space_w = draw.textlength(" ", font=parts[0][1])
    for w, fnt in words:
        ww = draw.textlength(w, font=fnt)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [(w, fnt)], ww
        else:
            cur.append((w, fnt))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines

def draw_parts_line(draw, x, y, parts_line, space_w=None):
    """Draw one mixed-font line; returns width used."""
    cx = x
    for i, (w, fnt) in enumerate(parts_line):
        if i:
            cx += draw.textlength(" ", font=fnt)
        draw.text((cx, y), w, font=fnt, fill=INK)
        cx += draw.textlength(w, font=fnt)
    return cx - x

# ---------------------------------------------------------------- flags
def draw_flag(d, x, y, w, h, code):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(120, 115, 100), width=1)
    if code == "KR":  # white, red-over-blue taegeuk
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=(255, 255, 255))
        cx, cy, r = x + w // 2, y + h // 2, h // 3
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(205, 50, 60))
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 180, fill=(40, 70, 160))
    elif code == "IN":  # saffron / white / green + navy wheel dot
        d.rectangle([x + 1, y + 1, x + w - 2, y + h // 3], fill=(255, 153, 51))
        d.rectangle([x + 1, y + h // 3, x + w - 2, y + 2 * h // 3], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 2 * h // 3, x + w - 2, y + h - 2], fill=(19, 136, 8))
        d.ellipse([x + w // 2 - 2, y + h // 2 - 2, x + w // 2 + 2, y + h // 2 + 2],
                  fill=(0, 0, 128))
    elif code == "LY":  # red / black / green + white crescent dot
        d.rectangle([x + 1, y + 1, x + w - 2, y + h // 3], fill=(200, 30, 30))
        d.rectangle([x + 1, y + h // 3, x + w - 2, y + 2 * h // 3], fill=(20, 20, 20))
        d.rectangle([x + 1, y + 2 * h // 3, x + w - 2, y + h - 2], fill=(0, 120, 40))
        d.ellipse([x + w // 2 - 2, y + h // 2 - 2, x + w // 2 + 2, y + h // 2 + 2],
                  fill=(255, 255, 255))
    elif code == "AU":  # blue + stars
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=(0, 40, 120))
        for sx, sy in [(0.30, 0.30), (0.70, 0.25), (0.55, 0.55), (0.80, 0.65), (0.35, 0.70)]:
            d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                      fill=(255, 255, 255))
    elif code == "FI":  # white + blue nordic cross
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=(255, 255, 255))
        d.rectangle([x + int(w * 0.30), y + 1, x + int(w * 0.45), y + h - 2], fill=(40, 90, 170))
        d.rectangle([x + 1, y + int(h * 0.38), x + w - 2, y + int(h * 0.62)], fill=(40, 90, 170))
    elif code == "MM":  # yellow / green / red + white star dot
        d.rectangle([x + 1, y + 1, x + w - 2, y + h // 3], fill=(250, 210, 60))
        d.rectangle([x + 1, y + h // 3, x + w - 2, y + 2 * h // 3], fill=(0, 130, 60))
        d.rectangle([x + 1, y + 2 * h // 3, x + w - 2, y + h - 2], fill=(210, 40, 40))
        d.ellipse([x + w // 2 - 2, y + h // 2 - 2, x + w // 2 + 2, y + h // 2 + 2],
                  fill=(255, 255, 255))
    elif code == "BH":  # white + red serrated
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=(255, 255, 255))
        zx = x + int(w * 0.30)
        pts = [(zx, y + 1)]
        for i in range(5):
            yy = y + 1 + i * (h - 2) // 4
            pts.append((x + w - 2 if i % 2 == 0 else zx, yy))
        pts.append((x + w - 2, y + h - 2))
        pts.append((zx, y + h - 2))
        d.polygon(pts, fill=(200, 30, 50))
    elif code == "LB":  # red / white / red + green cedar dot
        d.rectangle([x + 1, y + 1, x + w - 2, y + h // 4], fill=(200, 30, 30))
        d.rectangle([x + 1, y + h // 4, x + w - 2, y + 3 * h // 4], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 3 * h // 4, x + w - 2, y + h - 2], fill=(200, 30, 30))
        d.ellipse([x + w // 2 - 2, y + h // 2 - 3, x + w // 2 + 2, y + h // 2 + 3],
                  fill=(0, 120, 50))
    elif code == "DK":  # red + white cross
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=(200, 30, 50))
        d.rectangle([x + int(w * 0.30), y + 1, x + int(w * 0.44), y + h - 2], fill=(255, 255, 255))
        d.rectangle([x + 1, y + int(h * 0.36), x + w - 2, y + int(h * 0.64)], fill=(255, 255, 255))

# ---------------------------------------------------------------- hero illustrations
def draw_hero_art(d, x, y, w, h, kind):
    if kind == "cop31":
        # teal sky, globe with a crack, red NO DEAL ribbon
        for i in range(h):
            t = i / max(1, h - 1)
            d.line([x, y + i, x + w - 1, y + i],
                   fill=(int(120 + 90 * t), int(190 + 40 * t), int(200 - 30 * t)))
        cx, cy, r = x + w - 70, y + 22, 22
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 120, 180),
                  outline=(20, 60, 90), width=2)
        d.ellipse([cx - 15, cy - 10, cx - 3, cy + 2], fill=(90, 170, 90))
        d.ellipse([cx + 2, cy + 5, cx + 15, cy + 15], fill=(90, 170, 90))
        d.line([cx - 9, cy - 19, cx + 2, cy - 5, cx - 5, cy + 6, cx + 9, cy + 19],
               fill=(255, 255, 255), width=2)
        d.polygon([(x, y + h - 18), (x + w, y + h - 28), (x + w, y + h - 12), (x, y + h - 2)],
                  fill=RED)
        d.text((x + 10, y + h - 16), "NO DEAL", font=F_SANS_B(13), fill=(255, 255, 255))
    elif kind == "nato":
        # navy hall, columns, ring of gold stars
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=(36, 58, 110))
        d.polygon([(x + 16, y + 22), (x + w // 2, y + 2), (x + w - 16, y + 22)],
                  fill=(212, 175, 105))
        d.rectangle([x + 14, y + 22, x + w - 14, y + 28], fill=(232, 226, 210))
        for i in range(5):
            cx = x + 32 + i * 56
            d.rectangle([cx, y + 30, cx + 14, y + h - 14], fill=(232, 226, 210))
        d.rectangle([x + 16, y + h - 14, x + w - 16, y + h - 8], fill=(232, 226, 210))
        cx, cy = x + w - 42, y + 30
        for k in range(12):
            import math
            a = math.pi * 2 * k / 12 - math.pi / 2
            sx, sy = cx + 19 * math.cos(a), cy + 19 * math.sin(a)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    else:  # taiwan: falling market chart
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=(252, 250, 244))
        for gy in range(y + 12, y + h - 8, 14):
            d.line([x + 6, gy, x + w - 6, gy], fill=(228, 222, 208))
        pts = [(x + 14, y + 14), (x + 70, y + 24), (x + 120, y + 20), (x + 175, y + 38),
               (x + 225, y + 34), (x + 275, y + 58), (x + w - 14, y + h - 16)]
        d.line(pts, fill=RED, width=3, joint="curve")
        for px, py in pts[1:-1]:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        d.polygon([(x + w - 30, y + h - 34), (x + w - 14, y + h - 34), (x + w - 22, y + h - 12)],
                  fill=RED)
        d.text((x + 10, y + h - 24), "\u221217.5% IN A WEEK", font=F_SANS_B(12), fill=RED)

# ---------------------------------------------------------------- world map
# Simplified continent outlines in (lon, lat). Dotted render, equirectangular.
NA = [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-125, 49), (-124, 42),
      (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 15),
      (-86, 12), (-83, 9), (-79, 9), (-80, 13), (-84, 16), (-88, 18), (-90, 21),
      (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32), (-76, 35),
      (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52),
      (-65, 58), (-68, 55), (-75, 62), (-85, 66), (-95, 69), (-110, 68), (-125, 70),
      (-140, 70), (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
             (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-60, 70)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23),
      (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54), (-66, -55),
      (-68, -50), (-65, -45), (-62, -40), (-58, -34), (-52, -32), (-48, -28),
      (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
      (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-75, 10)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11), (-12, 8),
          (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5), (13, -10),
          (12, -17), (14, -22), (16, -28), (19, -34), (26, -34), (32, -29), (35, -24),
          (40, -16), (40, -10), (42, -4), (46, 0), (51, 2), (51, 11), (48, 11),
          (44, 11), (43, 12), (40, 15), (39, 18), (37, 20), (35, 23), (34, 27),
          (32, 31), (30, 31), (25, 32), (20, 32), (15, 32), (11, 34), (10, 37),
          (5, 37), (-1, 35)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
           (0, 51), (3, 53), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64),
           (13, 68), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 68),
           (50, 69), (55, 68), (60, 69), (65, 69), (70, 72), (75, 73), (80, 73),
           (85, 74), (90, 75), (95, 76), (100, 77), (105, 77), (110, 74), (115, 73),
           (120, 73), (125, 72), (130, 71), (135, 71), (140, 72), (145, 72),
           (150, 70), (155, 69), (160, 69), (165, 66), (170, 66), (178, 65),
           (178, 62), (170, 60), (162, 60), (158, 56), (156, 51), (150, 59),
           (142, 59), (140, 54), (138, 46), (135, 43), (132, 43), (128, 38),
           (127, 35), (122, 38), (120, 34), (122, 30), (120, 28), (118, 25),
           (114, 22), (110, 20), (108, 18), (106, 10), (104, 9), (101, 7),
           (99, 7), (98, 10), (100, 13), (98, 16), (97, 16), (94, 17), (92, 21),
           (91, 22), (89, 22), (88, 22), (86, 20), (84, 19), (82, 17), (80, 15),
           (80, 13), (77, 8), (76, 10), (74, 13), (72, 20), (70, 21), (68, 23),
           (66, 25), (62, 25), (58, 25), (56, 26), (54, 26), (52, 28), (50, 29),
           (48, 30), (48, 26), (52, 26), (56, 26), (59, 22), (58, 20), (55, 17),
           (52, 15), (48, 14), (44, 13), (43, 12), (42, 15), (41, 18), (39, 21),
           (37, 24), (35, 28), (34, 29), (36, 36), (33, 36), (30, 36), (27, 37),
           (23, 36), (22, 37), (19, 40), (23, 40), (26, 38), (26, 40), (22, 40),
           (19, 42), (15, 44), (12, 44), (8, 44), (3, 43), (-1, 44), (-2, 47),
           (-5, 48), (-9, 43), (-10, 36)]
AUSTRALIA = [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
             (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
             (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38), (141, 40),
         (142, 42), (144, 44), (142, 44), (140, 42), (139, 39), (137, 37), (135, 35),
         (132, 33)]
NEWGUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
             (141, -8), (136, -6), (132, -4)]
LAND = [NA, GREENLAND, SA, AFRICA, EURASIA, AUSTRALIA, UK, JAPAN, NEWGUINEA]

def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside

def on_land(lon, lat):
    return any(point_in_poly(lon, lat, p) for p in LAND)

# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header band (0-66)
    d.rectangle([0, 0, W - 1, 66], fill=NAVY)
    d.rectangle([0, 66, W - 1, 67], fill=GOLD)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=F_SERIF_B(30))) / 2, 6),
           title, font=F_SERIF_B(30), fill=(255, 255, 255))
    sub = "MONDAY  23  NOVEMBER  2026"
    d.text(((W - d.textlength(sub, font=F_SERIF(15))) / 2, 40),
           sub, font=F_SERIF(15), fill=GOLD)
    strip = "%d STORIES  \u00b7  7 REGIONS" % N_STORIES
    d.text((W - 8 - d.textlength(strip, font=F_SANS_B(11)), 26),
           strip, font=F_SANS_B(11), fill=(255, 255, 255))

    # ---- heroes (74-250), 3 cards of 330 wide
    hy, hh = 74, 176
    for i, hero in enumerate(HEROES):
        x = 8 + i * 339
        w = 330
        d.rectangle([x, hy, x + w - 1, hy + hh - 1], fill=CARD, outline=BORDER, width=1)
        # illustration (x+6 .. x+w-7, hy+6 .. hy+74)
        ix, iy, iw, ih = x + 6, hy + 6, w - 12, 68
        d.rectangle([ix, iy, ix + iw - 1, iy + ih - 1], outline=BORDER, width=1)
        draw_hero_art(d, ix + 1, iy + 1, iw - 2, ih - 2, hero["kind"])
        # red label chip over illustration top-left
        chip = hero["chip"]
        cw = d.textlength(chip, font=F_SANS_B(10)) + 12
        d.rectangle([ix + 4, iy + 4, ix + 4 + cw, iy + 20], fill=RED)
        d.text((ix + 10, iy + 7), chip, font=F_SANS_B(10), fill=(255, 255, 255))
        # green REPORTED pill, bottom-right of illustration
        pill = "REPORTED"
        pw = d.textlength(pill, font=F_SANS_B(9)) + 12
        d.rounded_rectangle([ix + iw - 6 - pw, iy + ih - 22, ix + iw - 6, iy + ih - 6],
                            radius=7, fill=GREEN)
        d.text((ix + iw - pw, iy + ih - 20), pill, font=F_SANS_B(9), fill=(255, 255, 255))
        # title (serif bold 14px, 2 lines max), body (10px, 2 lines),
        # caption, source -- each on its own band, no overlaps
        tx = x + 6
        tw = w - 18
        ty = hy + 78
        for li, line in enumerate(wrap(d, hero["title"], F_SERIF_B(14), tw)[:2]):
            d.text((tx, ty + li * 17), line, font=F_SERIF_B(14), fill=INK)
        by = hy + 114
        for li, line in enumerate(wrap(d, hero["body"], F_SANS(10), tw)[:2]):
            d.text((tx, by + li * 12), line, font=F_SANS(10), fill=INK)
        cy = hy + 144
        d.text((tx, cy), hero["caption"], font=F_SERIF(10), fill=MUTED)
        sy = hy + 158
        d.text((tx, sy), hero["source"], font=F_SANS_B(8), fill=MUTED)

    # ---- map panel (258-556): title + dotted world + pins
    my, mh = 258, 298
    d.rectangle([8, my, W - 9, my + mh - 1], fill=CARD, outline=BORDER, width=1)
    d.text((14, my + 5), "WHERE IT HAPPENED \u2014 13 PLACES",
           font=F_SANS_B(11), fill=NAVY)
    mx0, my0, mx1, my1 = 14, my + 24, W - 14, my + mh - 6
    mw, mhgt = mx1 - mx0, my1 - my0
    LON0, LON1, LAT0, LAT1 = -180.0, 180.0, -36.0, 62.0
    def to_xy(lon, lat):
        return (mx0 + (lon - LON0) / (LON1 - LON0) * mw,
                my0 + (LAT1 - lat) / (LAT1 - LAT0) * mhgt)
    step = 4
    for gy in range(my0, my1, step):
        lat = LAT1 - (gy - my0) / mhgt * (LAT1 - LAT0)
        for gx in range(mx0, mx1, step):
            lon = LON0 + (gx - mx0) / mw * (LON1 - LON0)
            if on_land(lon, lat):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=MAPDOT)
    # pins with labels (label side chosen to stay inside the panel)
    for n, (lon, lat, label, side, dy) in enumerate(PINS, 1):
        px, py = to_xy(lon, lat)
        px, py = int(px), int(py)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        num = str(n)
        d.text((px - d.textlength(num, font=F_SANS_B(9)) / 2, py - 7),
               num, font=F_SANS_B(9), fill=(255, 255, 255))
        lw = d.textlength(label, font=F_SANS_B(9))
        lx = px + 11 if side == "R" else px - 11 - lw
        ly = py + dy
        d.text((lx + 1, ly + 1), label, font=F_SANS_B(9), fill=(255, 255, 255))
        d.text((lx, ly), label, font=F_SANS_B(9), fill=INK)

    # ---- small cards (564-696): 5 cols x 2 rows, 195x64
    sy0 = 564
    cw, chh, gap = 195, 64, 8
    for i, card in enumerate(SMALL):
        r, c = divmod(i, 5)
        x = 8 + c * (cw + gap)
        y = sy0 + r * (chh + 4)
        d.rectangle([x, y, x + cw - 1, y + chh - 1], fill=CARD, outline=BORDER, width=1)
        fx, fy = x + 6, y + 5
        draw_flag(d, fx, fy, 26, 16, card["flag"])
        hx = fx + 32
        hw = cw - 38 - 12
        for li, line in enumerate(wrap(d, card["head"], F_SANS_B(10), hw)[:2]):
            d.text((hx, fy + li * 11), line, font=F_SANS_B(10), fill=INK)
        byy = y + 30
        for li, line in enumerate(wrap(d, card["body"], F_SANS(9), cw - 18)[:2]):
            d.text((x + 6, byy + li * 11), line, font=F_SANS(9), fill=INK)
        d.text((x + 6, y + 53), card["source"], font=F_SANS_B(8), fill=MUTED)

    # ---- UTC strip (704-728)
    uy = 704
    d.rectangle([8, uy, W - 9, uy + 24], fill=NAVY)
    seg = (W - 16) / 6
    for i, (t, ev) in enumerate(UTC_STRIP):
        cx = 8 + seg * i + seg / 2
        fnt = F_SANS_B(9)
        txt = t + "  \u00b7  " + ev
        while d.textlength(txt, font=fnt) > seg - 8 and fnt.size > 7:
            fnt = F_SANS_B(fnt.size - 1)
        d.text((cx - d.textlength(txt, font=fnt) / 2, uy + 7), txt,
               font=fnt, fill=(255, 255, 255))
        if i:
            d.line([8 + seg * i, uy + 5, 8 + seg * i, uy + 19], fill=(90, 110, 150))

    # ---- list 14-34 (736-936): one line each, prefix bold, numbers red
    ly = 736
    lh = 200 / len(LIST)
    for i, (prefix, body, source) in enumerate(LIST):
        y = ly + i * lh
        num = "%d." % (14 + i)
        x = 8 + 6
        d.text((x, y), num, font=F_SANS_B(10), fill=RED)
        x += d.textlength(num + " ", font=F_SANS_B(10))
        d.text((x, y), prefix, font=F_SANS_B(10), fill=INK)
        x += d.textlength(prefix, font=F_SANS_B(10))
        rest = " \u2014 " + body
        d.text((x, y), rest, font=F_SANS(10), fill=INK)
        x += d.textlength(rest, font=F_SANS(10))
        d.text((x + 4, y), "(" + source + ")", font=F_SANS(9), fill=MUTED)

    # ---- DATE CHECK box (944-1016)
    dy = 944
    d.rectangle([8, dy, W - 9, 1016], fill=(255, 251, 235), outline=BORDER, width=1)
    for li, line in enumerate(wrap(d, DATE_CHECK, F_SANS(11), W - 16 - 24)):
        d.text((8 + 12, dy + 6 + li * 14), line, font=F_SANS(11), fill=INK)

    return img

# ---------------------------------------------------------------- gap scan
def is_text(px):
    r, g, b = px
    return (r < 140 and g < 140 and b < 140) or (max(px) - min(px) > 60)

def scan(img):
    px = img.load()
    d = ImageDraw.Draw(img)
    print("--- GAP SCAN (text-only pixel scan) ---")
    bad = 0
    # hero text zones: title band and body band (caption/source excluded)
    for i in range(3):
        x = 8 + i * 339
        for name, zone, x0, x1 in [
                ("title", (x + 6, 74 + 78, x + 330 - 12, 74 + 112), x, x + 330 - 1),
                ("body", (x + 6, 74 + 114, x + 330 - 12, 74 + 138), x, x + 330 - 1)]:
            xs, ys = [], []
            for yy in range(zone[1], zone[3]):
                for xx in range(zone[0], zone[2]):
                    if is_text(px[xx, yy]):
                        xs.append(xx)
                        ys.append(yy)
            lg = min(xs) - x if xs else 99
            rg = x1 - max(xs) if xs else 99
            flag = "OK " if (6 <= lg <= 8 and rg >= 10) else "FIX"
            if flag == "FIX":
                bad += 1
            print("hero %d %s: left=%d right=%d %s" % (i + 1, name, lg, rg, flag))
    # small card text zones: headline band (right of flag) and body band
    for i in range(10):
        r, c = divmod(i, 5)
        x = 8 + c * (195 + 8)
        y = 564 + r * (64 + 4)
        for name, zone, x0, x1 in [
                ("head", (x + 38, y + 5, x + 195 - 12, y + 27), x + 32, x + 195 - 1),
                ("body", (x + 6, y + 30, x + 195 - 12, y + 52), x, x + 195 - 1)]:
            xs = []
            for yy in range(zone[1], zone[3]):
                for xx in range(zone[0], zone[2]):
                    if is_text(px[xx, yy]):
                        xs.append(xx)
            lg = min(xs) - x0 if xs else 99
            rg = x1 - max(xs) if xs else 99
            flag = "OK " if (6 <= lg <= 8 and rg >= 10) else "FIX"
            if flag == "FIX":
                bad += 1
            print("small %2d %s: left=%d right=%d %s" % (i + 1, name, lg, rg, flag))
    # list lines: each line band, text must start at x=14 and end before right edge
    for i in range(len(LIST)):
        y0 = int(736 + i * (200 / len(LIST)))
        y1 = int(736 + (i + 1) * (200 / len(LIST)))
        xs = []
        for yy in range(y0, min(y1, 936)):
            for xx in range(8, W - 8):
                if is_text(px[xx, yy]):
                    xs.append(xx)
        if not xs:
            print("list %2d: NO TEXT  FIX" % (14 + i))
            bad += 1
            continue
        lg = min(xs) - 8
        rg = (W - 9) - max(xs)
        flag = "OK " if (lg >= 5 and rg >= 4) else "FIX"
        if flag == "FIX":
            bad += 1
        print("list %2d: left=%d right=%d %s" % (14 + i, lg, rg, flag))
    print("scan issues:", bad)
    return bad

if __name__ == "__main__":
    img1 = render()
    img1.save(OUT, optimize=True)
    h1 = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    img2 = render()
    tmp = OUT + ".tmp"
    img2.save(tmp, format="PNG", optimize=True)
    h2 = hashlib.sha256(open(tmp, "rb").read()).hexdigest()
    os.remove(tmp)
    print("size:", os.path.getsize(OUT), "bytes; sha256:", h1)
    print("deterministic:", "YES" if h1 == h2 else "NO")
    print("stories:", N_STORIES, "(heroes 3 + small %d + list %d)" % (len(SMALL), len(LIST)))
    scan(img1)
