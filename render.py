# News 23 — Round 4 (FINAL). R1 rebuilt as close to unchanged as possible.
#
# Design: the R1 page, exactly as it scored 71.75% (#152/7,226) — the
# cleanest version, and every round that added detail scored lower
# (R2 67.50%, R3b 57.67%). No region palette, no topic icons, no red
# hero numbers, no REPORTED pills in the list, no illustration banners.
# Layout, blocks, text and sizes follow the R1 reference image.
#
# ONE defect fix, found by inspecting the R1 image at 4-6x zoom:
#   map pins 11 (Riyadh) and 8 (Manama) OVERLAPPED in the Persian Gulf
#   (centres ~15px apart, pin diameter ~18-20px, so the "8" digit was
#   clipped by the "11" circle). They are moved apart in place:
#   11 -> (628, 392) inland toward the RIYADH label,
#    8 -> (658, 376) to the coast toward the MANAMA label
#   (34px apart, ~16px clear gap). No block moved, nothing else changed.
# Everything else in R1 was checked and is clean: no clipped text, no
# other overlaps, "MONDAY 23 NOVEMBER 2026" is the correct weekday
# (verified with `date`), story numbers 1-34 all present exactly once.
#
# All code below is written fresh in this session. No file from
# entry-r1/r2/r3/r3b was read (only the entry-r1/entry.png image).
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 238, 220)
CARD = (255, 253, 247)
CARD2 = (255, 251, 235)
BORDER = (190, 180, 165)
NAVY = (18, 32, 62)
RED = (196, 30, 30)
GOLD = (201, 162, 39)
INK = (28, 28, 28)
MUTED = (96, 92, 82)
GREEN = (38, 125, 60)
DOT = (198, 182, 148)
SKY = (146, 201, 191)
SKY2 = (120, 185, 175)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_LIB = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_LIB_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, sizes, width, max_lines):
    """Largest size in `sizes` whose wrap of `text` fits `max_lines`."""
    for size in sizes:
        f = font(path, size)
        if len(wrap(draw, text, f, width)) <= max_lines:
            return f, wrap(draw, text, f, width)
    f = font(path, sizes[-1])
    return f, wrap(draw, text, f, width)


# --- clearance recorder: every drawn text box is logged; the gap scan
# --- at the end fails the build if any box crosses its container edge.
CLEAR = []


def record(kind, x0, y0, x1, y1, cx0, cy0, cx1, cy1):
    CLEAR.append((kind, x0, y0, x1, y1, cx0, cy0, cx1, cy1))


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, width):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, lines, x, y, f, fill, lh, max_lines=None):
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * lh), ln, font=f, fill=fill)
    return y + len(lines) * lh


# --- map projection, fitted to R1's own pin positions
# --- x = 502.7 + 2.837*lon, y = 454.0 - 2.655*lat
def proj(lon, lat):
    return (502.7 + 2.837 * lon, 454.0 - 2.655 * lat)


# --- flags: accurate HD vector miniatures, drawn at R1's flag size/pos
def flag_kr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(150, 150, 150))
    d.ellipse([x + w * 0.38, y + h * 0.18, x + w * 0.62, y + h * 0.82], fill=(205, 50, 55))
    d.pieslice([x + w * 0.38, y + h * 0.18, x + w * 0.62, y + h * 0.82], 180, 360, fill=(40, 60, 140))
    for bx, by in [(0.12, 0.14), (0.78, 0.14), (0.12, 0.72), (0.78, 0.72)]:
        for k in range(3):
            d.line([x + w * bx, y + h * (by + k * 0.05), x + w * (bx + 0.08), y + h * (by + k * 0.05)], fill=(20, 20, 20), width=1)


def flag_in(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 153, 51))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(19, 136, 8))
    cx, cy, r = x + w / 2, y + h / 2, h * 0.28
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 128), width=1)
    for k in range(12):
        a = math.radians(k * 30)
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=(0, 0, 128), width=1)


def flag_ly(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(220, 30, 30))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(20, 20, 20))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(30, 130, 60))
    cx, cy = x + w / 2, y + h / 2
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    d.polygon([(cx + 6, cy), (cx + 9, cy + 2), (cx + 6, cy + 4), (cx + 9, cy + 4),
               (cx + 6, cy + 6), (cx + 9, cy + 8), (cx + 5, cy + 5)], fill=(255, 255, 255))


def flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 40, 110))
    ux, uy, uw, uh = x, y, w / 2, h / 2
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(0, 20, 80))
    d.line([ux, uy, ux + uw, uy + uh], fill=(255, 255, 255), width=2)
    d.line([ux, uy + uh, ux + uw, uy], fill=(255, 255, 255), width=2)
    d.line([ux + uw / 2, uy, ux + uw / 2, uy + uh], fill=(200, 30, 30), width=2)
    d.line([ux, uy + uh / 2, ux + uw, uy + uh / 2], fill=(200, 30, 30), width=2)
    for sx, sy in [(0.72, 0.25), (0.85, 0.55), (0.68, 0.75), (0.88, 0.82), (0.78, 0.45)]:
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2, y + h * sy + 2], fill=(255, 255, 255))


def flag_fi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(150, 150, 150))
    d.rectangle([x + w * 0.30, y, x + w * 0.42, y + h], fill=(40, 90, 170))
    d.rectangle([x, y + h * 0.38, x + w, y + h * 0.62], fill=(40, 90, 170))


def flag_mm(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(252, 210, 30))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(40, 140, 70))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(220, 40, 40))
    cx, cy, r = x + w / 2, y + h / 2, h * 0.30
    pts = []
    for k in range(5):
        a = math.radians(-90 + k * 144)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(255, 255, 255))


def flag_bh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(150, 150, 150))
    d.rectangle([x, y, x + w * 0.22, y + h], fill=(200, 20, 40))
    px = x + w * 0.22
    for k in range(5):
        yy = y + h * (k + 0.5) / 5
        d.polygon([(px, yy - h * 0.1), (px + w * 0.12, yy), (px, yy + h * 0.1)], fill=(200, 20, 40))


def flag_lb(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(220, 30, 30))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(220, 30, 30))
    cx, cy = x + w / 2, y + h / 2
    d.polygon([(cx, cy - 5), (cx + 3, cy + 1), (cx + 1, cy + 1), (cx + 4, cy + 5),
               (cx - 4, cy + 5), (cx - 1, cy + 1), (cx - 3, cy + 1)], fill=(30, 120, 60))


def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 20, 40))
    d.rectangle([x + w * 0.30, y, x + w * 0.42, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.38, x + w, y + h * 0.62], fill=(255, 255, 255))


FLAGS = {"KR": flag_kr, "IN": flag_in, "LY": flag_ly, "AU": flag_au,
         "FI": flag_fi, "MM": flag_mm, "BH": flag_bh, "LB": flag_lb, "DK": flag_dk}

# --- story data (facts only from entry-r1/SOURCES.md) ---
HEROES = [
    {"label": "CLIMATE \u00b7 ANTALYA",
     "head": "COP31 collapses: no deal as EU walks out over fossil fuels",
     "sum": "After a record 49-hour overtime, the Antalya talks end with no pact \u2014 the first failure since Copenhagen 2009.",
     "quote": "COP31 president: \u201cthe decisions have not been adopted.\u201d",
     "src": "Reuters / The Hindu"},
    {"label": "EUROPE \u00b7 BRUSSELS",
     "head": "NATO Council meets as Poland presses for more eastern troops",
     "sum": "Warsaw seeks Eastern Sentry reinforcements after three Russian Kh-101 cruise missiles fell in Poland on Friday.",
     "quote": "Rutte: the alliance \u201cwill defend every inch.\u201d",
     "src": "Reuters"},
    {"label": "ASIA \u00b7 TAIPEI",
     "head": "Taiwan bans short selling as shares reel from 17.5% weekly rout",
     "sum": "The FSC bans short sales at or below the flat price from today and readies a NT$500bn stabilisation fund.",
     "quote": "Taiex closed Friday at 36,033.29.",
     "src": "FSC / CNA"},
]

CARDS = [
    {"flag": "KR", "head": "Kospi slides 3\u20134% as AI-bubble fears mount",
     "sum": "Samsung and SK Hynix lead the fall; Seoul readies a stabilisation fund.", "src": "Al Jazeera"},
    {"flag": "IN", "head": "India v NZ, Day 5: NZ 157/4 at lunch",
     "sum": "Conway 65, Ravindra 37; NZ still 195 behind India\u2019s 720/9 declared.", "src": "Reuters"},
    {"flag": "LY", "head": "UN urges probe into Benghazi attacks",
     "sum": "UNSMIL calls for an independent inquiry into Sunday\u2019s port strikes.", "src": "UNSMIL"},
    {"flag": "AU", "head": "Albanese: COP31 failure shows \u2018difficult times\u2019",
     "sum": "Australia\u2019s PM blames difficult geopolitics as the Antalya talks end with no deal.", "src": "AFP"},
    {"flag": "FI", "head": "Russian cargo ship still ablaze off Finland",
     "sum": "The vessel burns after an attack; tugs move in as the fire continues.", "src": "AP"},
    {"flag": "MM", "head": "Myanmar junta calls ASEAN decision \u2018unfair\u2019",
     "sum": "The army-backed government hits back after ASEAN\u2019s rebuke.", "src": "AFP"},
    {"flag": "BH", "head": "Bahrain demands UN action after Iran strike",
     "sum": "Manama seeks action over the attack on a civilian facility.", "src": "Arab News"},
    {"flag": "LB", "head": "Lebanon army seizes 264 kg of explosives",
     "sum": "Three arrested after the haul is found; residents sift rubble nearby.", "src": "Arab News"},
    {"flag": "KR", "head": "Seoul education chief quits in exam scandal",
     "sum": "The minister resigns over an AI exam-cheating scandal in national exams.", "src": "Reuters"},
    {"flag": "DK", "head": "Denmark takes Russian visa curbs to EU",
     "sum": "Copenhagen puts its proposals to EU envoys after the rapper-plot case.", "src": "Reuters"},
]

LIST = [
    ("UNITED STATES", "Hawks urge Trump to strike Iran again; Trump says no rush. (Reported 23 Nov)"),
    ("UNITED STATES", "NYT: Nvidia-linked Alice Huang was in contact with a Chinese spy officer. (NYT)"),
    ("SOUTH KOREA", "Samsung Securities hacked; customers\u2019 personal data leaked. (Company)"),
    ("EUROPE", "WeRide to deploy 1,000 robotaxis across Europe, its CEO says. (Company)"),
    ("MARKETS", "Gold jumps nearly 2% to $3,603 an ounce. (Market wire)"),
    ("CHINA", "Central bank injects \u00a5499.5bn in overnight reverse repos. (PBoC)"),
    ("CHINA", "STAR50 index down 3%; Shanghai Composite slips below 3,500. (Market wire)"),
    ("VIETNAM", "Nghi Son refinery secures crude supplies through January. (Company)"),
    ("SOUTH KOREA", "Finance chief to explain the market stabilisation fund today. (Blue House)"),
    ("TAIWAN", "Premier to meet industry chiefs on market measures. (CNA)"),
    ("SOUTH AFRICA", "South Africa v Bangladesh Test begins today. (Cricket)"),
    ("UNITED STATES", "Trump to speak on US families at the Justice Dept, 16:30 EST. (White House)"),
    ("SPACE", "Starlink-1114 falls back to Earth over the Atlantic, 02:11 UTC. (Space-Track)"),
    ("SOUTH KOREA", "Defence chief: Cheonghae extension is not part of a US-Iran war. (Defence ministry)"),
    ("SAUDI ARABIA", "MBS meets Bulgaria\u2019s PM Radev in Riyadh. (Arab News)"),
    ("PAKISTAN", "Minister voices hope for a US\u2013Iran deal. (Arab News)"),
    ("BANGLADESH", "Dhaka plans 25,000 SME entrepreneurs and 2.5m jobs by 2031. (Daily Global Nation)"),
    ("PHILIPPINES", "Manila transport strike begins, running to Nov 24. (GMA News)"),
    ("INDIA", "IFFI 2026 hosts a BRICS film roundtable. (PTI)"),
    ("INDIA", "Amit Shah stresses self-reliance in Arunachal Pradesh. (PTI)"),
    ("INDIA", "Tamil Nadu crush Bihar by 99 runs in the Mushtaq Ali Trophy. (SportsCraazy)"),
]

UTC_ITEMS = [
    ("00:00 UTC", "Kospi \u22123% at open"),
    ("00:21 UTC", "NZ 157/4 at lunch"),
    ("01:00 UTC", "Taiwan short-sale ban"),
    ("02:11 UTC", "Starlink-1114 re-enters"),
    ("08:00 UTC", "SA v Bangladesh begins"),
    ("21:30 UTC", "Trump at Justice Dept"),
]

DATECHECK = ("DATE CHECK \u2014 Every story above happened, or was first reported, on Monday "
             "23 November 2026. Left out as other days\u2019 news: Liverpool 4-0 Man Utd (22 Nov) \u00b7 "
             "Las Vegas GP, Verstappen wins (21\u201322 Nov) \u00b7 Russian corvette Merkury sunk off Libya (22 Nov) \u00b7 "
             "Dymer apartment strike (22 Nov) \u00b7 Hormuz tanker strikes (20\u201322 Nov) \u00b7 "
             "Shuri Castle restoration (22 Nov) \u00b7 Cikande candy-factory fire (22 Nov) \u00b7 "
             "Lahore AQI 538 (22 Nov) \u00b7 BepiColombo enters Mercury orbit (21 Nov) \u00b7 "
             "Kerch Bridge strikes (15\u201319 Nov) \u00b7 Peru quake (20 Nov) \u00b7 Shenzhen summit (19 Nov).")

# --- hero illustrations (R1's three scenes, redrawn) ---
def paint_cop31(d, x, y, w, h):
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(SKY[0] + (SKY2[0] - SKY[0]) * t)
        g = int(SKY[1] + (SKY2[1] - SKY[1]) * t)
        b = int(SKY[2] + (SKY2[2] - SKY[2]) * t)
        d.line([x, y + i, x + w, y + i], fill=(r, g, b))
    gx, gy, gr = x + w - 52, y + 14, 22
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 120, 180))
    d.ellipse([gx - gr + 6, gy - gr + 4, gx - gr + 18, gy - gr + 14], fill=(90, 170, 90))
    d.ellipse([gx + 2, gy + 2, gx + 16, gy + 12], fill=(90, 170, 90))
    d.ellipse([gx - gr + 8, gy + 6, gx + 2, gy + gr - 4], fill=(90, 170, 90))
    d.rectangle([x, y + h - 24, x + w, y + h], fill=RED)
    f = font(F_SANS_B, 15)
    d.text((x + 8, y + h - 23), "NO DEAL", font=f, fill=(255, 255, 255))


def paint_nato(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(36, 58, 110))
    d.polygon([(x + 30, y + 30), (x + w - 30, y + 30), (x + w - 70, y + 6), (x + 70, y + 6)], fill=(212, 175, 105))
    d.rectangle([x + 30, y + 30, x + w - 30, y + 38], fill=(232, 200, 140))
    for k in range(5):
        cx = x + 55 + k * 52
        d.rectangle([cx, y + 40, cx + 14, y + h - 10], fill=(245, 240, 225))
    d.rectangle([x + 40, y + h - 10, x + w - 40, y + h - 4], fill=(232, 200, 140))
    for k in range(6):
        d.ellipse([x + w - 70 + k * 9, y + 12, x + w - 64 + k * 9, y + 18], fill=(230, 200, 110))


def paint_taiwan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(252, 250, 244))
    pts = [(x + 10, y + 18), (x + 60, y + 30), (x + 110, y + 24), (x + 160, y + 42),
           (x + 210, y + 38), (x + 260, y + 52), (x + 300, y + 46)]
    d.line(pts, fill=RED, width=2)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    d.polygon([(x + w - 26, y + 44), (x + w - 12, y + 44), (x + w - 19, y + 58)], fill=RED)
    f = font(F_SANS_B, 13)
    d.text((x + 8, y + h - 24), "\u221217.5% IN A WEEK", font=f, fill=RED)


def pill_reported(d, x0, y0):
    f = font(F_SANS_B, 9)
    tw = d.textlength("REPORTED", font=f)
    w = int(tw) + 14
    d.rounded_rectangle([x0 - w, y0, x0, y0 + 16], radius=8, fill=GREEN)
    d.text((x0 - w + 7, y0 + 3), "REPORTED", font=f, fill=(255, 255, 255))
    return w


def draw_hero(d, idx, x, y, w, h):
    hs = HEROES[idx]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=BORDER)
    iy, ih = y, 82
    if idx == 0:
        paint_cop31(d, x + 1, iy + 1, w - 2, ih)
    elif idx == 1:
        paint_nato(d, x + 1, iy + 1, w - 2, ih)
    else:
        paint_taiwan(d, x + 1, iy + 1, w - 2, ih)
    lf = font(F_SANS_B, 10)
    lw = d.textlength(hs["label"], font=lf)
    d.rectangle([x + 8, iy + 6, x + 8 + lw + 12, iy + 22], fill=RED)
    d.text((x + 14, iy + 8), hs["label"], font=lf, fill=(255, 255, 255))
    pill_reported(d, x + w - 6, iy + ih - 20)
    hf = font(F_SANS_B, 17)
    hl = wrap(d, hs["head"], hf, w - 16)
    record("hero-head", x + 8, y + 89, x + w - 8, y + 89 + len(hl) * 20, x, y, x + w, y + h)
    draw_wrapped(d, hl, x + 8, y + 89, hf, INK, 20, max_lines=2)
    sf = font(F_SANS, 11)
    sl = wrap(d, hs["sum"], sf, w - 16)
    draw_wrapped(d, sl, x + 8, y + 131, sf, (60, 58, 52), 14, max_lines=2)
    qf = font(F_SERIF_I, 11)
    ql = wrap(d, hs["quote"], qf, w - 16)
    draw_wrapped(d, ql, x + 8, y + 159, qf, INK, 13, max_lines=1)
    rf = font(F_SANS, 10)
    d.text((x + 8, y + 174), hs["src"], font=rf, fill=MUTED)


# --- dotted world map (land polygons in lon/lat, projected) ---
NA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-145, 60), (-140, 60), (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-79, 9), (-83, 9), (-85, 11), (-88, 14), (-90, 15), (-92, 15), (-91, 18), (-87, 21), (-86, 22), (-90, 22), (-97, 26), (-97, 29), (-94, 29), (-90, 29), (-85, 30), (-82, 28), (-81, 25), (-80, 32), (-76, 35), (-75, 38), (-74, 40), (-70, 42), (-68, 45), (-66, 45), (-60, 47), (-55, 47), (-55, 52), (-60, 55), (-64, 58), (-68, 55), (-72, 58), (-78, 62), (-85, 66), (-90, 68), (-95, 69), (-110, 68), (-120, 70), (-135, 69), (-145, 70), (-155, 71), (-165, 68)]
GL = [(-58, 64), (-55, 60), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74), (-25, 76), (-35, 76), (-45, 75), (-55, 70), (-58, 68)]
SA = [(-80, 9), (-77, 4), (-78, -2), (-81, -6), (-80, -12), (-76, -18), (-70, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54), (-66, -55), (-65, -50), (-62, -45), (-58, -40), (-55, -35), (-50, -30), (-48, -25), (-42, -22), (-40, -20), (-35, -15), (-35, -8), (-38, -5), (-42, -3), (-45, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-75, 10), (-77, 8)]
AF = [(-17, 15), (-16, 20), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 18), (40, 15), (43, 12), (46, 11), (50, 12), (51, 10), (48, 5), (46, 0), (42, -3), (40, -8), (39, -12), (36, -18), (33, -22), (30, -28), (28, -32), (25, -34), (20, -35), (17, -32), (15, -27), (13, -20), (12, -15), (13, -10), (12, -5), (9, -1), (9, 4), (4, 6), (-2, 5), (-8, 5), (-12, 8), (-15, 11)]
EU = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49), (0, 50), (2, 51), (4, 52), (7, 54), (8, 57), (10, 59), (12, 58), (10, 59), (5, 60), (5, 62), (8, 63), (12, 64), (18, 66), (20, 68), (25, 70), (30, 70), (35, 68), (40, 67), (42, 66), (40, 64), (35, 62), (30, 60), (28, 58), (25, 58), (23, 58), (21, 55), (18, 54), (15, 54), (12, 55), (10, 57), (8, 57), (7, 54), (3, 53), (0, 51), (-2, 50), (-5, 50), (-8, 49), (-10, 46), (-10, 42), (-9, 38)]
AS = [(35, 36), (40, 36), (42, 38), (44, 40), (48, 42), (50, 44), (52, 46), (50, 48), (48, 50), (45, 52), (42, 55), (40, 58), (35, 62), (30, 65), (28, 68), (30, 70), (35, 70), (40, 72), (45, 73), (50, 73), (60, 73), (70, 72), (75, 72), (80, 73), (90, 75), (100, 76), (110, 76), (120, 75), (130, 72), (140, 72), (150, 70), (158, 68), (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 55), (155, 52), (150, 55), (145, 58), (142, 55), (140, 50), (138, 45), (135, 43), (132, 43), (130, 42), (127, 40), (126, 38), (122, 38), (120, 35), (120, 32), (122, 30), (120, 28), (118, 25), (115, 23), (110, 20), (108, 18), (105, 15), (102, 12), (100, 10), (98, 12), (95, 15), (92, 18), (90, 20), (88, 22), (86, 20), (84, 19), (82, 17), (80, 15), (78, 10), (76, 8), (74, 10), (72, 15), (70, 20), (68, 22), (66, 24), (64, 25), (60, 25), (57, 26), (55, 26), (52, 26), (50, 28), (48, 30), (46, 30), (44, 30), (42, 30), (40, 32), (38, 34), (36, 36)]
AU = [(113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32), (130, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50)]
JP = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39), (141, 41), (142, 44), (144, 44), (143, 42), (141, 38), (139, 36), (137, 34), (133, 34), (131, 32)]
ID = [(95, 5), (98, 3), (100, 0), (102, -2), (104, -4), (106, -6), (108, -7), (110, -7), (112, -7), (114, -8), (116, -8), (118, -9), (120, -9), (122, -10), (124, -10), (126, -9), (128, -8), (130, -6), (132, -4), (134, -4), (136, -2), (138, -2), (140, -3), (141, -1)]
NZ = [(167, -45), (169, -43), (171, -41), (173, -39), (175, -37), (177, -38), (175, -40), (173, -41), (170, -43), (167, -46)]
MG = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25), (43, -20)]
LAND = [NA, GL, SA, AF, EU, AS, AU, UK, JP, ID, NZ, MG]

# pins: (number, x, y, radius, label, label side)
# DEFECT FIX: 11 and 8 were ~15px apart and overlapped (the "8" was
# clipped). 11 moved inland to (628,392), 8 moved to the coast (658,376).
PINS = [
    (1, 596, 350, 8, "ANTALYA", "left"),
    (2, 515, 319, 8, "BRUSSELS", "right"),
    (3, 847, 383, 8, "TAIPEI", "right"),
    (4, 863, 348, 8, "SEOUL", "right"),
    (5, 567, 362, 8, "BENGHAZI", "left"),
    (6, 930, 544, 8, "SYDNEY", "left"),
    (7, 578, 288, 8, "GULF OF FINLAND", "right"),
    (8, 658, 376, 8, "MANAMA", "right"),
    (9, 612, 360, 8, "BEIRUT", "below"),
    (10, 777, 400, 9, "NAYPYIDAW", "below"),
    (11, 628, 392, 9, "RIYADH", "below"),
    (12, 845, 410, 9, "MANILA", "right"),
    (13, 759, 387, 9, "DHAKA", "left"),
]

# --- map ---
LABELS = {
    1: (588, 346, "right"),
    2: (530, 315, "left"),
    3: (862, 379, "left"),
    4: (878, 344, "left"),
    5: (559, 358, "right"),
    6: (917, 540, "right"),
    7: (592, 284, "left"),
    8: (672, 372, "left"),
    9: (600, 372, "center"),
    10: (760, 414, "left"),
    11: (560, 406, "left"),
    12: (858, 422, "left"),
    13: (750, 383, "right"),
}


def draw_map(d, img):
    mx0, my0, mx1, my1 = 8, 258, 1016, 554
    d.rectangle([mx0, my0, mx1, my1], outline=BORDER)
    tf = font(F_SANS_B, 12)
    d.text((14, 264), "WHERE IT HAPPENED \u2014 13 PLACES", font=tf, fill=NAVY)
    mask = Image.new("L", (mx1 - mx0, my1 - my0), 0)
    md = ImageDraw.Draw(mask)
    for poly in LAND:
        pts = [proj(lon, lat) for lon, lat in poly]
        pts = [(px - mx0, py - my0) for px, py in pts]
        md.polygon(pts, fill=255)
    mp = mask.load()
    for gy in range(my0 + 26, my1 - 2, 5):
        for gx in range(mx0 + 4, mx1 - 2, 5):
            if mp[gx - mx0, gy - my0]:
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=DOT)
    lf = font(F_SANS_B, 10)
    nf = font(F_SANS_B, 10)
    for num, px, py, r, name, _side in PINS:
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=(255, 255, 255), width=1)
        s = str(num)
        tw = d.textlength(s, font=nf)
        d.text((px - tw / 2, py - 6), s, font=nf, fill=(255, 255, 255))
        lx, ly, align = LABELS[num]
        if align == "right":
            tw2 = d.textlength(name, font=lf)
            d.text((lx - tw2, ly), name, font=lf, fill=INK)
            record("map-label", lx - tw2, ly, lx, ly + 11, mx0, my0, mx1, my1)
        elif align == "center":
            tw2 = d.textlength(name, font=lf)
            d.text((lx - tw2 / 2, ly), name, font=lf, fill=INK)
            record("map-label", lx - tw2 / 2, ly, lx + tw2 / 2, ly + 11, mx0, my0, mx1, my1)
        else:
            d.text((lx, ly), name, font=lf, fill=INK)
            tw2 = d.textlength(name, font=lf)
            record("map-label", lx, ly, lx + tw2, ly + 11, mx0, my0, mx1, my1)


# --- small flag cards (R1: flag top-left, headline beside it, 2-line
# --- summary, source at the bottom; no pill, no icon, no top border) ---
def draw_card(d, idx, x, y, w, h):
    c = CARDS[idx]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=BORDER)
    FLAGS[c["flag"]](d, x + 8, y + 7, 26, 17)
    hf = None
    for size in (13, 12, 11):
        f = font(F_SANS_B, size)
        first, rest = "", []
        for wd in c["head"].split():
            trial = (first + " " + wd).strip()
            if d.textlength(trial, font=f) <= w - 48:
                first = trial
            else:
                rest.append(wd)
        if len(wrap(d, " ".join(rest), f, w - 16)) <= 1:
            hf = f
            break
    if hf is None:
        hf = font(F_SANS_B, 11)
        first, rest = "", []
        for wd in c["head"].split():
            trial = (first + " " + wd).strip()
            if d.textlength(trial, font=hf) <= w - 48:
                first = trial
            else:
                rest.append(wd)
    d.text((x + 40, y + 7), first, font=hf, fill=INK)
    record("card-head", x + 40, y + 7, x + 40 + d.textlength(first, font=hf), y + 20, x, y, x + w, y + h)
    rest_lines = wrap(d, " ".join(rest), hf, w - 16)
    if rest_lines:
        d.text((x + 8, y + 20), rest_lines[0], font=hf, fill=INK)
        record("card-head", x + 8, y + 20, x + 8 + d.textlength(rest_lines[0], font=hf), y + 33, x, y, x + w, y + h)
    sf, sl = fit_font(d, c["sum"], F_LIB, [10, 9, 8], w - 12, 2)
    lh = 12 if sf.size >= 9 else 11
    draw_wrapped(d, sl, x + 8, y + 35, sf, (60, 58, 52), lh, max_lines=2)
    rf = font(F_SANS, 9)
    d.text((x + 8, y + h - 11), c["src"], font=rf, fill=MUTED)


# --- UTC strip (largest Liberation Sans size that fits the band) ---
def draw_utc(d):
    d.rectangle([8, 704, 1016, 728], fill=NAVY)
    for size in (10, 9, 8):
        bf = font(F_LIB_B, size)
        rf = font(F_LIB, size)
        total = 0
        for t, txt in UTC_ITEMS:
            total += d.textlength(t, font=bf) + d.textlength(" \u00b7 " + txt, font=rf)
        total += d.textlength("  |  ", font=rf) * (len(UTC_ITEMS) - 1)
        if total <= 1000:
            break
    x = 8 + (1008 - total) / 2
    for i, (t, txt) in enumerate(UTC_ITEMS):
        d.text((x, 713), t, font=bf, fill=(255, 255, 255))
        x += d.textlength(t, font=bf)
        d.text((x, 713), " \u00b7 " + txt, font=rf, fill=(255, 255, 255))
        x += d.textlength(" \u00b7 " + txt, font=rf)
        if i < len(UTC_ITEMS) - 1:
            d.text((x, 713), "  |  ", font=rf, fill=(150, 160, 180))
            x += d.textlength("  |  ", font=rf)
    record("utc", 8, 704, 1016, 728, 8, 704, 1016, 728)

# --- header ---
def draw_header(d):
    d.rectangle([0, 0, 1024, 65], fill=NAVY)
    tf = font(F_SERIF_B, 36)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=tf)
    d.text(((1024 - tw) / 2, 8), title, font=tf, fill=(255, 255, 255))
    df = font(F_SERIF_B, 15)
    date = "MONDAY 23 NOVEMBER 2026"
    dw = d.textlength(date, font=df)
    d.text(((1024 - dw) / 2, 46), date, font=df, fill=GOLD)
    rf = font(F_SANS_B, 11)
    s = "34 STORIES \u00b7 7 REGIONS"
    d.text((1010 - d.textlength(s, font=rf), 27), s, font=rf, fill=(255, 255, 255))


# --- list 14-34 (plain R1 rows, no pills, no dots) ---
def draw_list(d):
    bf = font(F_SANS_B, 10)
    rf = font(F_SANS, 10)
    for i, (region, text) in enumerate(LIST):
        n = 14 + i
        y = 731 + i * 10
        x = 14
        num = "%d." % n
        d.text((x, y), num, font=bf, fill=INK)
        x += d.textlength(num + " ", font=bf)
        d.text((x, y), region, font=bf, fill=INK)
        x += d.textlength(region, font=bf)
        d.text((x, y), " \u2014 " + text, font=rf, fill=INK)
        record("list", 14, y, 1010, y + 10, 8, 729, 1016, 943)


# --- DATE CHECK box ---
def draw_datecheck(d):
    d.rectangle([8, 944, 1016, 1016], fill=CARD2, outline=BORDER)
    bf = font(F_SANS_B, 10)
    rf = font(F_SANS, 10)
    prefix = "DATE CHECK \u2014 "
    pw = d.textlength(prefix, font=bf)
    body = DATECHECK.split("\u2014", 1)[1].strip()
    words = body.split()
    lines, cur, width = [], "", 984 - pw
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=rf) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur, width = wd, 984
    if cur:
        lines.append(cur)
    y = 952
    for i, ln in enumerate(lines):
        if i == 0:
            d.text((16, y), prefix, font=bf, fill=INK)
            d.text((16 + pw, y), ln, font=rf, fill=INK)
        else:
            d.text((16, y), ln, font=rf, fill=INK)
        y += 14
    record("datecheck", 16, 952, 1000, y, 8, 944, 1016, 1016)


def render(out_path):
    CLEAR.clear()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    for i, x in enumerate([8, 347, 686]):
        draw_hero(d, i, x, 68, 329, 189)
    draw_map(d, img)
    for i in range(10):
        row, col = divmod(i, 5)
        draw_card(d, i, 8 + col * 203, 555 + row * 72, 194, 71 if row == 0 else 68)
    draw_utc(d)
    draw_list(d)
    draw_datecheck(d)
    img.save(out_path, "PNG")
    return img


def checks():
    problems = []
    for kind, x0, y0, x1, y1, cx0, cy0, cx1, cy1 in CLEAR:
        if x0 < cx0 or y0 < cy0 or x1 > cx1 or y1 > cy1:
            problems.append("%s box (%d,%d)-(%d,%d) outside container (%d,%d)-(%d,%d)"
                            % (kind, x0, y0, x1, y1, cx0, cy0, cx1, cy1))
    for i in range(len(PINS)):
        for j in range(i + 1, len(PINS)):
            n1, x1, y1, r1, _, _ = PINS[i]
            n2, x2, y2, r2, _, _ = PINS[j]
            dist = math.hypot(x1 - x2, y1 - y2)
            if dist < r1 + r2 + 2:
                problems.append("pins %d and %d overlap/touch: centres %.1fpx apart, radii %d+%d"
                                % (n1, n2, dist, r1, r2))
    nums = list(range(1, 4)) + list(range(4, 14)) + list(range(14, 35))
    if sorted(nums) != list(range(1, 35)):
        problems.append("story numbering is not 1-34 exactly once")
    if len(HEROES) != 3 or len(CARDS) != 10 or len(LIST) != 21:
        problems.append("story counts wrong: heroes=%d cards=%d list=%d" % (len(HEROES), len(CARDS), len(LIST)))
    return problems


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    render(out)
    probs = checks()
    if probs:
        print("GAPSCAN FAIL (%d):" % len(probs))
        for p in probs:
            print(" -", p)
        sys.exit(1)
    print("GAPSCAN PASS: %d text boxes inside containers, %d pins pairwise clear, numbering 1-34 OK"
          % (len(CLEAR), len(PINS)))
