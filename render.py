#!/usr/bin/env python3
"""Render News 23 R2 entry.png - THE WORLD IN ONE DAY, MONDAY 23 NOVEMBER 2026.

Fresh implementation written for this round. Design follows the News 22 R9
newspaper layout: cream paper, navy header, big serif masthead, red italic
subtitle, six-fact strip, THE DAY IN UTC strip, region bar, three illustrated
heroes with red label chips and REPORTED pills, ten numbered small cards
with illustrated banners and italic captions, solid tan world map with
numbered pins, bold-prefix story list, DATE CHECK box.

All 34 stories happened, or were first reported, on Monday 23 November 2026
in some time zone. No Israel / Gaza / West Bank stories. Facts re-verified
from the R1 SOURCES.md fact list; every line below was written here, inline.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 238, 220)
CARD = (250, 245, 232)
BORDER = (198, 188, 172)
NAVY = (27, 42, 74)
NAVY2 = (36, 54, 96)
RED = (198, 38, 34)
DARKRED = (170, 30, 28)
INK = (22, 22, 22)
GRAY = (96, 90, 78)
GREEN = (46, 139, 74)
GOLD = (196, 158, 46)
MAPTAN = (206, 186, 146)
MAPDOT = (188, 166, 124)

F_SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
F_SANS_I = "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# Every text span drawn inside a card, for the gap audit:
# (x0, y0, x1, y1, card_left, card_right)
SPANS = []


def text(d, xy, s, fnt, fill, card=None):
    d.text(xy, s, font=fnt, fill=fill)
    w = d.textlength(s, font=fnt)
    if card is not None:
        SPANS.append((xy[0], xy[1], xy[0] + w, xy[1] + fnt.size, card[0], card[1]))


def fit_text(d, s, fnt, width, min_size=9):
    """Shrink the font until the single line fits (never below min_size)."""
    size = fnt.size
    while size > min_size and d.textlength(s, font=F(fnt.path, size)) > width:
        size -= 1
    return F(fnt.path, size)


# ---------------------------------------------------------------- facts ----
# Heroes: (number, chip, caption, location line, headline, body, source)
HEROES = [
    (1, "COP31: COLLAPSE", "Antalya talks end", "1 ANTALYA, TURKEY \u00b7 CLIMATE",
     "COP31 COLLAPSES: NO DEAL AS EU WALKS OUT",
     "After 49 hours of overtime, the Antalya talks end with no pact \u2014 "
     "the first failure since Copenhagen 2009. \u201cThe decisions have not "
     "been adopted.\u201d",
     "Reuters / The Hindu"),
    (2, "NATO: BRUSSELS", "North Atlantic Council", "2 BRUSSELS, BELGIUM \u00b7 DEFENCE",
     "NATO COUNCIL MEETS AS POLAND PRESSES FOR TROOPS",
     "Warsaw seeks Eastern Sentry reinforcements after three Russian Kh-101 "
     "cruise missiles fell in Poland on Friday. Rutte: the alliance \u201cwill "
     "defend every inch.\u201d",
     "Reuters"),
    (3, "TAIPEI: ROUT", "Taiex chart", "3 TAIPEI, TAIWAN \u00b7 MARKETS",
     "TAIWAN BANS SHORT SALES AFTER 17.5% ROUT",
     "The FSC bans short sales at or below the flat price from today and "
     "readies a NT$500bn stabilisation fund. Taiex closed Friday at 36,033.29.",
     "FSC / CNA"),
]

# Small cards: (number, chip, location line, headline, body, source, flag, scene)
SMALL = [
    (4, "AI FEARS", "SEOUL \u00b7 MARKETS", "KOSPI SLIDES 3\u20134% AS AI-BUBBLE FEARS MOUNT",
     "Samsung and SK Hynix lead the fall; Seoul readies a fund.",
     "Al Jazeera", "KR", "chart"),
    (5, "DAY 5", "INDIA \u00b7 CRICKET", "INDIA v NZ, DAY 5: NZ 157/4 AT LUNCH",
     "Conway 65, Ravindra 37; NZ still 195 behind India\u2019s 720/9 declared.",
     "Reuters", "IN", "cricket"),
    (6, "PORT STRIKES", "BENGHAZI \u00b7 LIBYA", "UN URGES PROBE INTO BENGHAZI ATTACKS",
     "UNSMIL seeks an independent inquiry into the strikes.",
     "UNSMIL", "LY", "port"),
    (7, "CANBERRA", "SYDNEY \u00b7 AUSTRALIA", "ALBANESE: COP31 FAILURE SHOWS \u2018DIFFICULT TIMES\u2019",
     "Australia\u2019s PM blames difficult geopolitics for the failure.",
     "AFP", "AU", "parliament"),
    (8, "BALTIC", "GULF OF FINLAND \u00b7 SHIPPING", "RUSSIAN CARGO SHIP STILL ABLAZE OFF FINLAND",
     "The vessel burns after an attack; tugs move in as the fire continues.",
     "AP", "FI", "shipfire"),
    (9, "ASEAN", "MYANMAR \u00b7 POLITICS", "MYANMAR JUNTA CALLS ASEAN DECISION \u2018UNFAIR\u2019",
     "The army-backed government hits back after ASEAN\u2019s rebuke.",
     "AFP", "MM", "asean"),
    (10, "UN ACTION", "BAHRAIN \u00b7 GULF", "BAHRAIN DEMANDS UN ACTION AFTER IRAN STRIKE",
     "Manama seeks action over the attack on a civilian facility.",
     "Arab News", "BH", "un"),
    (11, "HAUL", "LEBANON \u00b7 SECURITY", "LEBANON ARMY SEIZES 264 KG OF EXPLOSIVES",
     "Three held after the haul is found; residents sift rubble.",
     "Arab News", "LB", "blast"),
    (12, "EXAM SCANDAL", "SEOUL \u00b7 EDUCATION", "SEOUL EDUCATION CHIEF QUITS IN EXAM SCANDAL",
     "The minister resigns over an AI exam-cheating scandal.",
     "Reuters", "KR", "exam"),
    (13, "EU ENVOYS", "DENMARK \u00b7 EUROPE", "DENMARK TAKES RUSSIAN VISA CURBS TO EU",
     "Copenhagen puts its proposals to EU envoys.",
     "Reuters", "DK", "europe"),
]

# Italic-gray caption under each small-card banner, R9 style (names the scene).
CAPTIONS = {
    4: "Seoul bourse", 5: "The crease", 6: "Benghazi port", 7: "Canberra",
    8: "Gulf of Finland", 9: "ASEAN flag", 10: "UN headquarters",
    11: "The haul", 12: "Exam paper", 13: "EU stars",
}

# List items 14-34: (number, bold prefix, rest) - one line each, fitted.
LIST_ITEMS = [
    (14, "United States:", "Hawks urge Trump to strike Iran", "(23 Nov)"),
    (15, "United States:", "NYT links Nvidia\u2019s Huang to spy officer", "(NYT)"),
    (16, "South Korea:", "Samsung Securities hacked, data leaked", "(Yonhap)"),
    (17, "Europe:", "WeRide to deploy 1,000 robotaxis in Europe", "(Company)"),
    (18, "Markets:", "Gold jumps nearly 2% to $3,603 an ounce", "(Wire)"),
    (19, "China:", "Central bank injects \u00a5499.5bn overnight", "(PBoC)"),
    (20, "China:", "STAR50 down 3%; Shanghai below 3,500", "(Wire)"),
    (21, "Vietnam:", "Nghi Son refinery secures crude to January", "(Company)"),
    (22, "South Korea:", "Finance chief to explain stabilisation fund", "(Blue House)"),
    (23, "Taiwan:", "Premier to meet industry chiefs on markets", "(Govt)"),
    (24, "South Africa:", "SA v Bangladesh Test begins today", "(Cricket)"),
    (25, "United States:", "Trump speaks at Justice Dept", "(White House)"),
    (26, "Space:", "Starlink-1114 falls back over the Atlantic", "(Space-Track)"),
    (27, "South Korea:", "Cheonghae no part of a US\u2013Iran war", "(Ministry)"),
    (28, "Saudi Arabia:", "MBS meets Bulgaria\u2019s PM Radev", "(Arab News)"),
    (29, "Pakistan:", "Minister voices hope for a US\u2013Iran deal", "(Arab News)"),
    (30, "Bangladesh:", "Dhaka plans 25,000 SMEs, 2.5m jobs", "(Daily Global Nation)"),
    (31, "Philippines:", "Manila transport strike begins", "(GMA News)"),
    (32, "India:", "IFFI 2026 hosts BRICS film roundtable", "(PTI)"),
    (33, "India:", "Amit Shah stresses self-reliance in Arunachal", "(PTI)"),
    (34, "India:", "Tamil Nadu crush Bihar by 99 runs", "(SportsCraazy)"),
]

FACTS = [
    ("17.5%", "Taiex weekly rout"),
    ("4%", "Kospi falls at open"),
    ("$3,603", "gold per ounce"),
    ("264 kg", "explosives seized"),
    ("1,000", "robotaxis for Europe"),
    ("25,000", "SME entrepreneurs planned"),
]

UTC_STRIP = [
    ("00:00", "Seoul market opens"),
    ("00:21", "NZ 157/4 at lunch"),
    ("01:00", "Taiwan short-selling ban"),
    ("02:11", "Starlink re-enters"),
    ("08:00", "SA v Bangladesh Test"),
    ("21:30", "Trump speaks"),
]

REGIONS = [
    ("GLOBAL", 3, (31, 58, 95)),
    ("EUROPE", 4, (192, 57, 43)),
    ("MIDDLE EAST", 4, (125, 60, 152)),
    ("ASIA", 18 - 1, (211, 84, 0)),   # Asia 17 by this count (see SOURCES.md)
    ("AMERICAS", 3, (20, 143, 119)),
    ("OCEANIA", 1, (108, 140, 47)),
    ("AFRICA", 2, (166, 124, 82)),
]
# NOTE: region counts sum to 34: 3+4+4+17+3+1+2 = 34.

# Map pins: (number, lon, lat, label, label dx, dy)
PINS = [
    (1, 30.7, 36.9, "ANTALYA", 8, -4),
    (2, 4.35, 50.85, "BRUSSELS", 8, -4),
    (3, 121.5, 25.0, "TAIPEI", 8, -4),
    (4, 127.0, 37.5, "SEOUL", 8, -4),
    (5, 91.7, 26.1, "INDIA", -38, 8),
    (6, 20.1, 32.1, "BENGHAZI", -52, 6),
    (7, 151.2, -33.9, "SYDNEY", -48, 8),
    (8, 27.0, 60.0, "GULF OF FINLAND", 8, -12),
    (9, 96.1, 19.7, "NAYPYIDAW", 8, 8),
    (10, 50.6, 26.2, "MANAMA", 8, -4),
    (11, 35.5, 33.9, "BEIRUT", -44, -10),
    (12, 127.0, 36.4, "", 0, 0),          # second Seoul story: pin only, no label
    (13, 12.6, 55.7, "COPENHAGEN", -72, -10),
]

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60), (-55, 47),
     (-70, 42), (-75, 35), (-80, 25), (-90, 20), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20), (-50, -30),
     (-60, -38), (-70, -45), (-73, -50), (-70, -20), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28), (40, 15),
     (48, 11), (40, 0), (35, -18), (25, -30), (15, -35), (10, -20), (8, 4), (-8, 5), (-15, 12)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 58), (10, 62), (18, 70), (25, 71),
     (30, 70), (25, 60), (20, 55), (15, 55), (10, 54), (8, 57), (3, 43), (-2, 37)],
    # Asia
    [(30, 70), (40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72), (160, 70),
     (170, 66), (162, 60), (155, 55), (140, 45), (135, 35), (127, 35), (122, 30),
     (115, 22), (108, 15), (105, 8), (100, 6), (95, 15), (90, 22), (85, 20), (80, 15),
     (75, 8), (70, 20), (65, 25), (60, 25), (55, 26), (50, 28), (48, 30), (45, 35),
     (40, 38), (35, 42), (30, 45), (30, 60)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (125, -32), (130, -32), (135, -35), (140, -38),
     (145, -38), (150, -37), (153, -27), (150, -22), (146, -19), (142, -15), (135, -12),
     (130, -12), (125, -14), (120, -20), (114, -22)],
    # SE Asia islands
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -5), (135, -3), (140, -8), (130, -2), (120, 0), (110, 2), (100, 5)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (145, 44), (140, 40),
     (138, 36), (132, 33)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    # New Zealand
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -39), (174, -41), (170, -44)],
]


# ------------------------------------------------------------- drawing -----
def pill(d, x, y, w, h, fill, outline=None):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill,
                        outline=outline, width=1)


def chip(d, x, y, s, fnt, bg=RED):
    w = int(d.textlength(s, font=fnt)) + 12
    d.rectangle([x, y, x + w, y + fnt.size + 7], fill=bg)
    d.text((x + 6, y + 3), s, font=fnt, fill=(255, 255, 255))
    return w


def num_circle(d, cx, cy, n, r=10):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=2)
    f = F(F_SANS_B, 12)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 7), t, font=f, fill=(255, 255, 255))


def flag(d, x, y, code):
    """Tiny 16x11 flag, flat and simple."""
    w, h = 16, 11
    d.rectangle([x, y, x + w, y + h], outline=(120, 110, 95), width=1)
    if code == "KR":  # white, red/blue circle
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(255, 255, 255))
        d.ellipse([x + 5, y + 2, x + 11, y + 6], fill=(205, 43, 57))
        d.ellipse([x + 5, y + 5, x + 11, y + 9], fill=(0, 71, 160))
    elif code == "IN":  # saffron / white / green
        d.rectangle([x + 1, y + 1, x + w - 1, y + 4], fill=(255, 153, 51))
        d.rectangle([x + 1, y + 4, x + w - 1, y + 7], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 7, x + w - 1, y + h - 1], fill=(19, 136, 8))
    elif code == "LY":  # red / black / green
        d.rectangle([x + 1, y + 1, x + w - 1, y + 4], fill=(231, 0, 19))
        d.rectangle([x + 1, y + 4, x + w - 1, y + 7], fill=(0, 0, 0))
        d.rectangle([x + 1, y + 7, x + w - 1, y + h - 1], fill=(0, 122, 61))
    elif code == "AU":  # blue, canton cross, stars
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(0, 32, 91))
        d.rectangle([x + 1, y + 1, x + 7, y + 5], fill=(255, 255, 255))
        d.line([x + 1, y + 3, x + 7, y + 3], fill=(204, 0, 0), width=1)
        d.line([x + 4, y + 1, x + 4, y + 5], fill=(204, 0, 0), width=1)
        d.ellipse([x + 12, y + 7, x + 14, y + 9], fill=(255, 255, 255))
    elif code == "FI":  # white, blue cross
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(255, 255, 255))
        d.rectangle([x + 5, y + 1, x + 7, y + h - 1], fill=(0, 53, 128))
        d.rectangle([x + 1, y + 4, x + w - 1, y + 6], fill=(0, 53, 128))
    elif code == "MM":  # yellow / green / red, white star
        d.rectangle([x + 1, y + 1, x + w - 1, y + 4], fill=(254, 203, 0))
        d.rectangle([x + 1, y + 4, x + w - 1, y + 7], fill=(52, 140, 60))
        d.rectangle([x + 1, y + 7, x + w - 1, y + h - 1], fill=(234, 40, 57))
        d.ellipse([x + 7, y + 4, x + 9, y + 6], fill=(255, 255, 255))
    elif code == "BH":  # white + red serrated (simplified)
        d.rectangle([x + 1, y + 1, x + 6, y + h - 1], fill=(255, 255, 255))
        d.rectangle([x + 6, y + 1, x + w - 1, y + h - 1], fill=(206, 17, 38))
    elif code == "LB":  # red / white / red
        d.rectangle([x + 1, y + 1, x + w - 1, y + 3], fill=(237, 28, 36))
        d.rectangle([x + 1, y + 3, x + w - 1, y + 8], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 8, x + w - 1, y + h - 1], fill=(237, 28, 36))
        d.ellipse([x + 7, y + 4, x + 9, y + 6], fill=(0, 122, 61))
    elif code == "DK":  # red, white cross
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(198, 12, 48))
        d.rectangle([x + 5, y + 1, x + 7, y + h - 1], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 4, x + w - 1, y + 6], fill=(255, 255, 255))


def starburst(d, cx, cy, r1, r2, n, fill):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


# --------------------------------------------------------- hero scenes -----
def hero_scene(d, box, kind):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "cop31":
        # teal sky, globe, clock, summit flags, long table, delegates, sun
        for i, c in enumerate([(64, 145, 150), (52, 128, 138), (40, 110, 124)]):
            d.rectangle([x0, y0 + i * h // 3, x1, y0 + (i + 1) * h // 3], fill=c)
        # globe, lower left (below the red chip)
        gx, gy, gr = x0 + 30, y0 + 56, 20
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 190),
                  outline=(230, 225, 210), width=2)
        d.ellipse([gx - 10, gy - 12, gx + 2, gy - 2], fill=(90, 170, 100))
        d.ellipse([gx - 2, gy + 4, gx + 12, gy + 14], fill=(90, 170, 100))
        d.ellipse([gx - 14, gy - 14, gx - 4, gy - 6], fill=(235, 240, 245))
        # wall clock, upper right
        ccx, ccy, cr = x1 - 42, y0 + 26, 15
        d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(250, 246, 236),
                  outline=(40, 40, 40), width=2)
        d.line([ccx, ccy, ccx - 6, ccy - 8], fill=(40, 40, 40), width=2)
        d.line([ccx, ccy, ccx + 7, ccy - 3], fill=(40, 40, 40), width=2)
        d.ellipse([ccx - 2, ccy - 2, ccx + 2, ccy + 2], fill=(198, 38, 34))
        # row of summit flags across the middle
        cols = [(198, 38, 34), (240, 180, 40), (60, 120, 200), (80, 170, 90),
                (150, 80, 170), (230, 120, 60)]
        for i, c in enumerate(cols):
            px = x0 + 62 + i * 34
            d.line([px, y0 + 26, px, y0 + 62], fill=(230, 225, 210), width=2)
            d.polygon([(px, y0 + 26), (px + 22, y0 + 32), (px, y0 + 38)], fill=c)
        # big sun, bottom right (partly behind the table)
        d.ellipse([x1 - 62, y0 + h - 52, x1 - 6, y0 + h - 2], fill=(245, 190, 80))
        d.ellipse([x1 - 56, y0 + h - 46, x1 - 12, y0 + h - 6], fill=(250, 214, 120))
        # long table + delegates
        d.rectangle([x0, y0 + h - 26, x1, y0 + h - 14], fill=(96, 64, 40))
        d.rectangle([x0, y0 + h - 14, x1, y1], fill=(70, 46, 30))
        d.rectangle([x0, y0 + h - 26, x1, y0 + h - 22], fill=(240, 236, 224))
        for i, c in enumerate([(220, 90, 80), (240, 200, 90), (90, 160, 220),
                               (140, 200, 120), (230, 150, 90), (180, 120, 220),
                               (240, 120, 160), (120, 200, 200), (200, 200, 90)]):
            px = x0 + 12 + i * 34
            d.rectangle([px, y0 + h - 40, px + 16, y0 + h - 26], fill=c)
            d.ellipse([px + 1, y0 + h - 52, px + 15, y0 + h - 38], fill=c)
    elif kind == "nato":
        # night blue, scattered stars, moon, EU star circle, columned HQ
        # with lit windows, steps, and a flag row
        d.rectangle([x0, y0, x1, y1], fill=(28, 42, 84))
        for (sx, sy, r) in [(x0 + 140, y0 + 10, 2), (x0 + 200, y0 + 12, 1),
                            (x0 + 250, y0 + 8, 2), (x0 + 295, y0 + 20, 1),
                            (x0 + 315, y0 + 48, 2), (x0 + 14, y0 + 50, 1),
                            (x0 + 60, y0 + 52, 1)]:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(240, 240, 220))
        # crescent moon, upper right
        d.ellipse([x1 - 46, y0 + 8, x1 - 18, y0 + 36], fill=(245, 238, 200))
        d.ellipse([x1 - 40, y0 + 6, x1 - 16, y0 + 32], fill=(28, 42, 84))
        for i in range(12):
            a = 2 * math.pi * i / 12 - math.pi / 2
            sx = x0 + w // 2 + int(46 * math.cos(a))
            sy = y0 + 34 + int(20 * math.sin(a))
            starburst(d, sx, sy, 4, 2, 5, (250, 210, 60))
        d.rectangle([x0 + 60, y0 + 58, x1 - 60, y0 + 96], fill=(205, 198, 182))
        d.polygon([(x0 + 56, y0 + 58), (x0 + w // 2, y0 + 40), (x1 - 56, y0 + 58)],
                  fill=(225, 218, 200))
        d.ellipse([x0 + w // 2 - 6, y0 + 44, x0 + w // 2 + 6, y0 + 56],
                  fill=(150, 142, 126))
        for i in range(5):
            cx = x0 + 84 + i * 38
            d.rectangle([cx, y0 + 62, cx + 8, y0 + 94], fill=(150, 142, 126))
        # lit windows between the columns
        for i in range(4):
            wx = x0 + 100 + i * 38
            d.rectangle([wx, y0 + 68, wx + 12, y0 + 80], fill=(250, 210, 90))
        # steps
        d.rectangle([x0 + 48, y0 + 96, x1 - 48, y0 + 100], fill=(170, 164, 150))
        d.rectangle([x0 + 40, y0 + 100, x1 - 40, y0 + 104], fill=(150, 144, 130))
        d.rectangle([x0, y0 + 104, x1, y1], fill=(52, 58, 66))
        # row of small flags in front of the steps
        fcols = [(0, 32, 91), (198, 38, 34), (0, 90, 160), (200, 160, 40),
                 (30, 120, 60)]
        for i, c in enumerate(fcols):
            px = x0 + 96 + i * 30
            d.line([px, y0 + 88, px, y0 + 106], fill=(230, 225, 210), width=2)
            d.rectangle([px, y0 + 88, px + 16, y0 + 96], fill=c)
        for i, c in enumerate([(0, 32, 91), (198, 38, 34)]):
            px = x0 + 26 + i * 26
            d.line([px, y0 + 78, px, y0 + 104], fill=(230, 225, 210), width=2)
            d.rectangle([px, y0 + 78, px + 16, y0 + 88], fill=c)
    else:  # "taipei" - falling chart with candlesticks + volume
        d.rectangle([x0, y0, x1, y1], fill=(252, 247, 236))
        for gy in range(y0 + 18, y1 - 8, 18):
            d.line([x0 + 8, gy, x1 - 8, gy], fill=(228, 220, 204), width=1)
        for gx in range(x0 + 48, x1 - 8, 40):
            d.line([gx, y0 + 8, gx, y1 - 16], fill=(238, 231, 216), width=1)
        # candlesticks along the falling path (red down, green up)
        candles = [
            (30, 24, 12, True), (64, 30, 10, False), (98, 28, 12, True),
            (132, 40, 14, True), (166, 48, 10, False), (200, 46, 12, True),
            (234, 60, 14, True), (268, 74, 12, True),
        ]
        for (ox, oy, bh, down) in candles:
            c = (198, 38, 34) if down else (46, 139, 74)
            d.line([x0 + ox + 4, y0 + oy - 6, x0 + ox + 4, y0 + oy + bh + 6],
                   fill=c, width=1)
            d.rectangle([x0 + ox, y0 + oy, x0 + ox + 8, y0 + oy + bh], fill=c)
        pts = [(x0 + 16, y0 + 22), (x0 + 70, y0 + 30), (x0 + 120, y0 + 26),
               (x0 + 175, y0 + 46), (x0 + 225, y0 + 44), (x0 + 275, y0 + 72),
               (x0 + 310, y0 + 88)]
        d.line(pts, fill=(198, 38, 34), width=3)
        for (px, py) in pts:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(198, 38, 34))
        d.polygon([(x0 + 296, y0 + 78), (x0 + 318, y0 + 78), (x0 + 307, y0 + 100)],
                  fill=(198, 38, 34))
        # volume bars along the bottom
        for i, vh in enumerate([8, 12, 9, 14, 11, 16, 13, 18]):
            bx = x0 + 22 + i * 36
            vc = (198, 38, 34) if i % 2 == 0 else (150, 140, 125)
            d.rectangle([bx, y1 - 4 - vh, bx + 14, y1 - 4], fill=vc)
        # annotations
        f = F(F_SANS_B, 17)
        d.text((x1 - 78, y0 + 8), "-17.5%", font=f, fill=(198, 38, 34))
        af = F(F_SANS, 9)
        d.text((x0 + 120, y0 + 10), "close 36,033.29", font=af, fill=(96, 90, 78))


# -------------------------------------------------------- small scenes -----
def small_scene(d, box, kind):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w // 2, y0 + h // 2
    if kind == "chart":
        d.rectangle([x0, y0, x1, y1], fill=(24, 40, 80))
        for gx in range(x0 + 12, x1 - 4, 14):
            d.line([gx, y0 + 4, gx, y1 - 6], fill=(38, 58, 100), width=1)
        bars = [(34, (198, 38, 34)), (28, (46, 139, 74)),
                (22, (198, 38, 34)), (15, (46, 139, 74))]
        for i, (bh, c) in enumerate(bars):
            bx = x0 + 14 + i * 16
            d.rectangle([bx, y0 + h - 8 - bh, bx + 10, y0 + h - 8], fill=c)
        d.line([(x0 + 12, y0 + 12), (x0 + 72, y0 + 34)], fill=(250, 210, 60), width=2)
        d.line([x0 + 8, y0 + h - 6, x1 - 8, y0 + h - 6], fill=(120, 130, 160), width=1)
    elif kind == "cricket":
        d.rectangle([x0, y0, x1, y1], fill=(46, 125, 60))
        d.rectangle([x0 + 30, y0 + 4, x0 + 52, y1 - 4], fill=(196, 164, 120))
        # stumps at the far end
        for sx in (x0 + 36, x0 + 41, x0 + 46):
            d.line([sx, y0 + 8, sx, y0 + 18], fill=(250, 220, 80), width=2)
        d.ellipse([x0 + 66, y0 + 12, x0 + 74, y0 + 20], fill=(255, 255, 255))
        d.line([(x0 + 20, y0 + 40), (x0 + 44, y0 + 20)], fill=(120, 72, 32), width=3)
        # fielder at deep cover
        d.ellipse([x0 + 10, y0 + 28, x0 + 18, y0 + 36], fill=(255, 255, 255))
        d.rectangle([x0 + 11, y0 + 36, x0 + 17, y0 + 44], fill=(240, 240, 230))
    elif kind == "port":
        d.rectangle([x0, y0, x1, y1], fill=(30, 44, 78))
        # dock crane
        d.line([x0 + 58, y0 + 4, x0 + 58, y0 + 30], fill=(180, 170, 150), width=2)
        d.line([x0 + 58, y0 + 6, x0 + 72, y0 + 6], fill=(180, 170, 150), width=2)
        d.line([x0 + 72, y0 + 6, x0 + 68, y0 + 18], fill=(200, 190, 170), width=1)
        d.rectangle([x0 + 10, y0 + 26, x0 + 66, y0 + 40], fill=(20, 28, 52))
        d.rectangle([x0 + 18, y0 + 14, x0 + 30, y0 + 26], fill=(120, 90, 60))
        d.rectangle([x0 + 34, y0 + 18, x0 + 46, y0 + 26], fill=(90, 110, 140))
        starburst(d, x0 + 52, y0 + 16, 10, 4, 8, (245, 150, 40))
        d.rectangle([x0, y0 + 40, x1, y1], fill=(52, 84, 128))
        d.line([x0 + 6, y0 + 44, x1 - 6, y0 + 44], fill=(140, 180, 210), width=1)
    elif kind == "parliament":
        d.rectangle([x0, y0, x1, y1], fill=(126, 178, 214))
        # dome above the pediment
        d.pieslice([cx - 12, y0 + 0, cx + 12, y0 + 18], 180, 360,
                   fill=(240, 236, 224))
        d.polygon([(x0 + 12, y0 + 22), (cx, y0 + 8), (x1 - 12, y0 + 22)], fill=(240, 236, 224))
        for i in range(4):
            px = x0 + 16 + i * 14
            d.rectangle([px, y0 + 24, px + 6, y0 + 44], fill=(240, 236, 224))
        # windows on the pediment base
        d.rectangle([x0 + 20, y0 + 26, x0 + 28, y0 + 34], fill=(60, 90, 120))
        d.rectangle([x0 + 48, y0 + 26, x0 + 56, y0 + 34], fill=(60, 90, 120))
        d.rectangle([x0, y0 + 44, x1, y1], fill=(90, 120, 90))
    elif kind == "shipfire":
        d.rectangle([x0, y0, x1, y1], fill=(36, 52, 74))
        # smoke puffs
        d.ellipse([x0 + 22, y0 + 6, x0 + 36, y0 + 16], fill=(120, 120, 125))
        d.ellipse([x0 + 40, y0 + 2, x0 + 54, y0 + 12], fill=(140, 140, 145))
        d.polygon([(x0 + 10, y0 + 34), (x0 + 66, y0 + 34), (x0 + 60, y0 + 46),
                   (x0 + 16, y0 + 46)], fill=(24, 32, 48))
        starburst(d, x0 + 30, y0 + 22, 12, 5, 8, (245, 140, 30))
        starburst(d, x0 + 48, y0 + 18, 9, 4, 8, (250, 190, 60))
        d.rectangle([x0, y0 + 46, x1, y1], fill=(64, 100, 138))
        # wave crests
        for wx in (x0 + 10, x0 + 34, x0 + 58):
            d.arc([wx, y0 + 44, wx + 14, y0 + 52], 180, 360, fill=(200, 220, 240), width=1)
    elif kind == "asean":
        d.rectangle([x0, y0, x1, y1], fill=(254, 203, 0))
        d.rectangle([x0, y0 + 19, x1, y0 + 38], fill=(52, 140, 60))
        d.rectangle([x0, y0 + 38, x1, y1], fill=(234, 40, 57))
        # ten-star circle on the green band
        for i in range(10):
            a = 2 * math.pi * i / 10 - math.pi / 2
            sx = cx + int(8 * math.cos(a))
            sy = y0 + 28 + int(8 * math.sin(a))
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    elif kind == "un":
        d.rectangle([x0, y0, x1, y1], fill=(120, 170, 215))
        # UN emblem: globe with grid + olive branch arc
        d.ellipse([cx - 13, y0 + 6, cx + 13, y0 + 32], fill=(235, 232, 222))
        d.ellipse([cx - 13, y0 + 6, cx + 13, y0 + 32], outline=(90, 130, 170), width=1)
        d.line([cx, y0 + 6, cx, y0 + 32], fill=(140, 160, 180), width=1)
        d.ellipse([cx - 6, y0 + 10, cx + 6, y0 + 28], outline=(140, 160, 180), width=1)
        d.line([cx - 13, y0 + 19, cx + 13, y0 + 19], fill=(140, 160, 180), width=1)
        d.arc([cx - 20, y0 + 2, cx + 20, y0 + 40], 40, 140, fill=(90, 130, 60), width=2)
        # small HQ base below the emblem
        d.rectangle([x0 + 22, y0 + 34, x0 + 54, y0 + 46], fill=(235, 232, 222))
        for i in range(3):
            px = x0 + 28 + i * 8
            d.rectangle([px, y0 + 37, px + 4, y0 + 45], fill=(140, 150, 170))
    elif kind == "blast":
        d.rectangle([x0, y0, x1, y1], fill=(44, 40, 52))
        # orange glow behind the blast
        d.ellipse([cx - 20, cy - 16, cx + 20, cy + 12], fill=(120, 70, 40))
        starburst(d, cx, cy - 4, 16, 6, 9, (250, 150, 40))
        starburst(d, cx, cy - 4, 8, 3, 9, (250, 210, 80))
        # smoke
        d.ellipse([cx - 24, cy - 18, cx - 10, cy - 8], fill=(110, 108, 115))
        d.ellipse([cx + 10, cy - 20, cx + 24, cy - 10], fill=(130, 128, 135))
        # rubble
        d.rectangle([x0 + 12, y0 + 42, x0 + 30, y0 + 50], fill=(120, 112, 100))
        d.rectangle([x0 + 44, y0 + 44, x0 + 62, y0 + 52], fill=(100, 94, 84))
        d.rectangle([x0 + 30, y0 + 46, x0 + 40, y0 + 51], fill=(140, 132, 120))
    elif kind == "exam":
        d.rectangle([x0, y0, x1, y1], fill=(238, 232, 216))
        d.rectangle([x0 + 24, y0 + 6, x0 + 54, y0 + 50], fill=(255, 255, 255),
                    outline=(150, 140, 125), width=1)
        for i in range(4):
            ly = y0 + 14 + i * 8
            d.line([x0 + 29, ly, x0 + 49, ly], fill=(140, 135, 125), width=1)
        # pencil, lower left
        d.polygon([(x0 + 8, y0 + 44), (x0 + 16, y0 + 30), (x0 + 20, y0 + 34),
                   (x0 + 12, y0 + 48)], fill=(250, 200, 60))
        d.polygon([(x0 + 8, y0 + 44), (x0 + 12, y0 + 48), (x0 + 10, y0 + 50)],
                  fill=(198, 38, 34))
        d.line([(x0 + 56, y0 + 30), (x0 + 68, y0 + 42)], fill=(198, 38, 34), width=3)
        d.line([(x0 + 68, y0 + 30), (x0 + 56, y0 + 42)], fill=(198, 38, 34), width=3)
    else:  # "europe"
        d.rectangle([x0, y0, x1, y1], fill=(0, 32, 91))
        # small parliament silhouette at the bottom
        d.rectangle([x0 + 18, y0 + 34, x0 + 58, y0 + 50], fill=(20, 50, 110))
        d.polygon([(x0 + 14, y0 + 34), (cx, y0 + 24), (x0 + 62, y0 + 34)],
                  fill=(30, 60, 120))
        for i in range(12):
            a = 2 * math.pi * i / 12 - math.pi / 2
            sx = cx + int(26 * math.cos(a))
            sy = cy - 6 + int(16 * math.sin(a))
            starburst(d, sx, sy, 3, 1, 5, (250, 210, 60))


# ----------------------------------------------------------------- map -----
def draw_map(d, box):
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    lat_max, lat_min = 84.0, -58.0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (lat_max - lat) / (lat_max - lat_min) * mh)

    # solid tan landmass, R9 style (no stipple)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAPTAN, outline=(172, 150, 108))
    f_pin = F(F_SANS_B, 10)
    f_lab = F(F_SANS_B, 10)
    for (n, lon, lat, label, dx, dy) in PINS:
        px, py = proj(lon, lat)
        num_circle(d, px, py, n, r=9)
        if label:
            d.text((px + dx, py + dy), label, font=f_lab, fill=(60, 50, 40))


# -------------------------------------------------------------- layout -----
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 7                      # outer margin
    CW = W - 2 * MX             # 1010 content width

    # ---- navy header strip -------------------------------------------------
    d.rectangle([0, 0, W, 24], fill=NAVY)
    text(d, (MX + 3, 4), "THE WORLD IN ONE DAY", F(F_SANS_B, 15), (255, 255, 255))
    rt = "34 STORIES \u00b7 7 REGIONS"
    text(d, (W - MX - 3 - d.textlength(rt, font=F(F_SANS_B, 13)), 5), rt,
         F(F_SANS_B, 13), (255, 255, 255))

    # ---- serif masthead ----------------------------------------------------
    mast = F(F_SERIF_B, 52)
    s = "Monday 23 November 2026"
    d.text(((W - d.textlength(s, font=mast)) / 2, 28), s, font=mast, fill=INK)

    # ---- red italic subtitle ----------------------------------------------
    sub = F(F_SERIF_I, 16)
    s = ("COP31 collapses with no deal \u00b7 Taiwan bans short selling after a "
         "17.5% rout \u00b7 NATO meets in Brussels")
    d.text(((W - d.textlength(s, font=sub)) / 2, 97), s, font=sub, fill=DARKRED)

    # ---- six-fact strip -----------------------------------------------------
    fy = 114
    colw = CW / 6
    for i, (num, cap) in enumerate(FACTS):
        cx = MX + i * colw
        nf = F(F_SERIF_B, 32)
        d.text((cx + (colw - d.textlength(num, font=nf)) / 2, fy), num,
               font=nf, fill=RED)
        cf = F(F_SANS, 10)
        d.text((cx + (colw - d.textlength(cap, font=cf)) / 2, fy + 45), cap,
               font=cf, fill=GRAY)
        if i:
            d.line([cx, fy + 9, cx, fy + 58], fill=(210, 200, 182), width=1)

    # ---- THE DAY IN UTC strip ----------------------------------------------
    uy = 179
    d.rectangle([0, uy, W, uy + 16], fill=NAVY)
    x = MX + 3
    tf = F(F_SANS_B, 11)
    text(d, (x, uy + 3), "THE DAY IN UTC", tf, RED)
    x += d.textlength("THE DAY IN UTC", font=tf) + 10
    for t, label in UTC_STRIP:
        seg = f"{t} {label}"
        sf = F(F_SANS, 10)
        text(d, (x, uy + 4), t, F(F_SANS_B, 10), GOLD)
        x += d.textlength(t, font=F(F_SANS_B, 10)) + 4
        text(d, (x, uy + 4), label, sf, (235, 235, 235))
        x += d.textlength(label, font=sf) + 12
        if t != UTC_STRIP[-1][0]:
            d.text((x, uy + 4), "\u00b7", font=sf, fill=(150, 150, 160))
            x += 10

    # ---- region bar ----------------------------------------------------------
    ry = 197
    total = sum(c for _, c, _ in REGIONS)
    # every segment gets a floor width so its label always fits
    floor = 84
    widths = []
    rest = CW - floor * len(REGIONS)
    for name, count, color in REGIONS:
        widths.append(floor + rest * count / total)
    x = MX
    for (name, count, color), segw in zip(REGIONS, widths):
        d.rectangle([x, ry, x + segw, ry + 18], fill=color)
        label = f"{name} \u00b7 {count}"
        lf = F(F_SANS_B, 12)
        lw = d.textlength(label, font=lf)
        if lw <= segw - 6:
            d.text((x + (segw - lw) / 2, ry + 3), label, font=lf, fill=(255, 255, 255))
        x += segw

    # ---- heroes ---------------------------------------------------------------
    hy = 219
    hw, hh = 332, 224
    hgap = 7
    for i, (num, chp, caption, loc, headline, body, src) in enumerate(HEROES):
        x = MX + i * (hw + hgap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=BORDER, width=1)
        card = (x, x + hw)
        # illustration
        scene = ("cop31", "nato", "taipei")[i]
        hero_scene(d, (x + 1, hy + 1, x + hw - 1, hy + 105), scene)
        chip(d, x + 6, hy + 6, chp, F(F_SANS_B, 10))
        num_circle(d, x + hw - 16, hy + 105 - 12, num, r=10)
        # caption bar under the picture
        text(d, (x + 6, hy + 109), caption, F(F_SANS_I, 10), GRAY, card)
        # location line + REPORTED pill
        ly = hy + 125
        lf = F(F_SANS_B, 12)
        text(d, (x + 6, ly), loc, lf, RED, card)
        pill_txt = "REPORTED"
        pf = F(F_SANS_B, 9)
        pw = int(d.textlength(pill_txt, font=pf)) + 12
        pill(d, x + hw - 6 - pw, ly - 1, pw, 15, GREEN)
        d.text((x + hw - 6 - pw + 6, ly + 1), pill_txt, font=pf, fill=(255, 255, 255))
        # headline (serif bold, 2 lines)
        hf = F(F_SERIF_B, 19)
        lines = wrap(d, headline, hf, hw - 12)
        yy = ly + 18
        for ln in lines[:2]:
            text(d, (x + 6, yy), ln, hf, INK, card)
            yy += 20
        # body (2-3 lines) + source
        bf = F(F_SANS, 11)
        blines = wrap(d, body + f" ({src})", bf, hw - 12)
        for ln in blines[:3]:
            text(d, (x + 6, yy), ln, bf, (40, 38, 34), card)
            yy += 13

    # ---- small cards (2 rows of 5) -------------------------------------------
    sy0 = 449
    sh = 140
    sw = 198
    sgap = 5
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            num, chp, loc, headline, body, src, code, scene = SMALL[idx]
            x = MX + col * (sw + sgap)
            y = sy0 + row * (sh + 6)
            d.rectangle([x, y, x + sw, y + sh], fill=CARD, outline=BORDER, width=1)
            card = (x, x + sw)
            small_scene(d, (x + 1, y + 1, x + sw - 1, y + 52), scene)
            chip(d, x + 5, y + 5, chp, F(F_SANS_B, 9))
            num_circle(d, x + sw - 14, y + 14, num, r=9)
            text(d, (x + 6, y + 54), CAPTIONS[num], F(F_SANS_I, 9), GRAY, card)
            flag(d, x + 5, y + 68, code)
            ly = y + 66
            lf = F(F_SANS_B, 10)
            text(d, (x + 25, ly), loc, lf, RED, card)
            hf = F(F_SERIF_B, 12)
            lines = wrap(d, headline, hf, sw - 12)
            yy = y + 82
            for ln in lines[:2]:
                text(d, (x + 6, yy), ln, hf, INK, card)
                yy += 14
            bf = F(F_SANS, 10)
            blines = wrap(d, body + f" ({src})", bf, sw - 12)
            for ln in blines[:2]:
                text(d, (x + 6, yy), ln, bf, (40, 38, 34), card)
                yy += 12

    # ---- bottom: map (left) + list (right) -------------------------------------
    by = 740
    bh = 196
    # map box
    mapx, mapw = MX, 330
    d.rectangle([mapx, by, mapx + mapw, by + bh], fill=CARD, outline=BORDER, width=1)
    text(d, (mapx + 6, by + 5), "WHERE IT HAPPENED", F(F_SANS_B, 12), INK,
         (mapx, mapx + mapw))
    text(d, (mapx + 6, by + 22), "pins match story numbers", F(F_SANS, 9), GRAY,
         (mapx, mapx + mapw))
    draw_map(d, (mapx + 4, by + 36, mapx + mapw - 4, by + bh - 4))
    # list box
    lx, lw = MX + 337, 673
    d.rectangle([lx, by, lx + lw, by + bh], fill=CARD, outline=BORDER, width=1)
    text(d, (lx + 6, by + 5), "ALSO ON MONDAY \u00b7 21 MORE STORIES",
         F(F_SANS_B, 12), RED, (lx, lx + lw))
    d.line([lx + 6, by + 24, lx + lw - 6, by + 24], fill=BORDER, width=1)
    colw2 = (lw - 12 - 10) // 2
    left_items = LIST_ITEMS[:11]
    right_items = LIST_ITEMS[11:]
    for ci, items in enumerate([left_items, right_items]):
        cx = lx + 6 + ci * (colw2 + 10)
        for ri, (n, prefix, rest, src) in enumerate(items):
            yy = by + 30 + ri * 15
            num_s = f"{n} "
            pre_s = prefix + " "
            rest_s = f"{rest} {src}"
            # fit the REST in regular so the whole drawn line fits the column
            size = 10
            while size > 9:
                wsum = (d.textlength(num_s, font=F(F_SANS_B, 10))
                        + d.textlength(pre_s, font=F(F_SANS_B, 10))
                        + d.textlength(rest_s, font=F(F_SANS, size)))
                if wsum <= colw2:
                    break
                size -= 1
            fnt = F(F_SANS, size)
            text(d, (cx, yy), num_s, F(F_SANS_B, 10), RED, (lx, lx + lw))
            nx = cx + d.textlength(num_s, font=F(F_SANS_B, 10))
            text(d, (nx, yy), pre_s, F(F_SANS_B, 10), INK, (lx, lx + lw))
            nx += d.textlength(pre_s, font=F(F_SANS_B, 10))
            text(d, (nx, yy), rest_s, fnt, (40, 38, 34), (lx, lx + lw))

    # ---- DATE CHECK --------------------------------------------------------------
    dy = 942
    d.rectangle([MX, dy, W - MX, dy + 48], outline=RED, width=2)
    d.rectangle([MX + 1, dy + 1, W - MX - 1, dy + 47], fill=(252, 242, 236))
    dc = ("DATE CHECK \u2014 Every story above happened, or was first reported, "
          "on Monday 23 November 2026. Left out as other days\u2019 news: "
          "Liverpool 4-0 Man Utd (22 Nov) \u00b7 Las Vegas GP, Verstappen wins "
          "(21\u201322 Nov) \u00b7 Russian corvette Merkury sunk off Libya (22 Nov) \u00b7 "
          "Dymer apartment strike (22 Nov) \u00b7 Hormuz tanker strikes (20\u201322 Nov) "
          "\u00b7 Shuri Castle restoration \u00b7 Shenzhen summit (19 Nov) \u00b7 Kerch "
          "Bridge strikes (15\u201319 Nov) \u00b7 Peru quake (20 Nov).")
    df = F(F_SANS, 11)
    lines = wrap(d, dc, df, W - 2 * MX - 16)
    yy = dy + 4
    for ln in lines[:3]:
        # paint the leading label red+bold on the first line
        if ln.startswith("DATE CHECK"):
            lab = "DATE CHECK \u2014 "
            text(d, (MX + 8, yy), lab, F(F_SANS_B, 11), RED, (MX, W - MX))
            text(d, (MX + 8 + d.textlength(lab, font=F(F_SANS_B, 11)), yy),
                 ln[len("DATE CHECK \u2014 "):], df, (40, 38, 34), (MX, W - MX))
        else:
            text(d, (MX + 8, yy), ln, df, (40, 38, 34), (MX, W - MX))
        yy += 14

    # ---- footer ------------------------------------------------------------------
    ff = F(F_SANS, 9)
    foot = ("Rendered by an AI agent for make.fun \u00b7 news-image-20261123 \u00b7 "
            "Sources: Reuters, AP, AFP, Al Jazeera, Arab News, Yonhap, NYT, "
            "FSC / CNA, UNSMIL, Space-Track \u00b7 All facts checked 23 Nov 2026")
    d.text(((W - d.textlength(foot, font=ff)) / 2, 996), foot, font=ff, fill=GRAY)

    return img


def gap_scan(img):
    """Text-only pixel gap scan: every recorded text span must sit >=6px
    inside its card's left/right edges. Returns list of violations."""
    bad = []
    for (x0, y0, x1, y1, cl, cr) in SPANS:
        if x0 < cl + 6 - 0.5:
            bad.append(f"LEFT x0={x0:.1f} < card {cl}+6 (span to {x1:.1f})")
        if x1 > cr - 6 + 0.5:
            bad.append(f"RIGHT x1={x1:.1f} > card {cr}-6 (span from {x0:.1f})")
    return bad


def main():
    img = render()
    img.save("entry.png")
    import os
    print("saved entry.png", os.path.getsize("entry.png"), "bytes",
          img.size)
    # truncation audit: no body may wrap past its line budget
    d = ImageDraw.Draw(img)
    trunc = []
    for (num, chp, caption, loc, headline, body, src) in HEROES:
        n = len(wrap(d, headline, F(F_SERIF_B, 19), 332 - 12))
        if n > 2:
            trunc.append(f"hero {num} headline {n} lines")
        n = len(wrap(d, body + f" ({src})", F(F_SANS, 11), 332 - 12))
        if n > 3:
            trunc.append(f"hero {num} body {n} lines")
    for (num, chp, loc, headline, body, src, code, scene) in SMALL:
        n = len(wrap(d, headline, F(F_SERIF_B, 12), 198 - 12))
        if n > 2:
            trunc.append(f"card {num} headline {n} lines")
        n = len(wrap(d, body + f" ({src})", F(F_SANS, 10), 198 - 12))
        if n > 2:
            trunc.append(f"card {num} body {n} lines")
    if trunc:
        print("TRUNCATION:", trunc)
    else:
        print("truncation audit: 0 issues")
    bad = gap_scan(img)
    if bad:
        print("GAP VIOLATIONS:", len(bad))
        for b in bad[:20]:
            print(" ", b)
    else:
        print("gap scan: 0 issues")


if __name__ == "__main__":
    main()
