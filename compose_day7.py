#!/usr/bin/env python3
"""Round 7 front-page renderer for make.fun bounty news-image-20261127.

Draws a 1024x1024 code-drawn newspaper front page summing up world news
for Friday 27 November 2026. Pure Pillow, no network, no clock, no random
input: the same data literals always produce the same JPEG bytes.

Layout (top to bottom): navy nameplate band, serif masthead date, red
kicker line, six-box stat strip, region colour bar, UTC timeline, three
large pictured stories, ten small pictured stories, dotted world map with
numbered pins, 39 more one-line stories, date-check / confidence footer.

Run:  python3 compose_day7.py
Writes entry.jpg next to this file and /output/entry.png (same bytes).
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 26, 40)
NAVY = (15, 31, 64)
NAVY_SOFT = (38, 58, 96)
RED = (176, 32, 32)
GOLD = (214, 164, 32)
GREY = (96, 100, 108)
LIGHT_LINE = (205, 198, 182)
WHITE = (255, 255, 255)
GREEN_TAG = (22, 110, 58)
BLUE_TAG = (18, 74, 138)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

# ---------------------------------------------------------------- data
# Region colours (used for kickers, pins, region bar).
REGION_COLOUR = {
    "EUROPE": (26, 74, 158),
    "MIDEAST": (178, 32, 32),
    "N AMER": (16, 110, 110),
    "AFRICA": (196, 116, 0),
    "E ASIA": (122, 44, 150),
    "S ASIA": (190, 60, 120),
    "SE ASIA": (40, 130, 60),
    "LAT AM": (150, 90, 20),
    "OCEANIA": (90, 90, 160),
    "GLOBAL": (90, 96, 104),
}

# Pictured stories: number, city, region, kicker topic, headline, body,
# verification tag, source, scene key, map lon/lat, pin nudge (dx, dy).
PICTURED = [
    (1, "KUWAIT", "MIDEAST", "DRONE WAR",
     "Drone strike kills two Italians in Kuwait",
     "Rheinmetall Italia technicians hit at an air-defence site; Italy "
     "blames Iran. Tehran denies it.",
     "CONFIRMED", "Reuters, CNN", "kuwait", 47.5, 29.4, (9, -7)),
    (2, "STRAIT OF HORMUZ", "MIDEAST", "OIL",
     "Mines hit two tankers; Brent nears $97",
     "Ships catch fire off Oman; Brent climbed to $97.71, its highest "
     "since 9 November.",
     "CONFIRMED", "Reuters", "hormuz", 56.5, 26.5, (11, 5)),
    (3, "BRUSSELS", "EUROPE", "EU SUMMIT",
     "EU summit ends with no budget deal",
     "24 states back a EUR 45bn Ukraine loan for 2027, but the 2028-34 "
     "budget talks fail. Dec retry.",
     "OFFICIAL", "Costa, von der Leyen", "brussels", 4.35, 50.85, (5, -9)),
    (4, "NEW YORK", "N AMER", "WEATHER",
     "Storm cuts power to nearly 1m on Thanksgiving",
     "Macy's 100th parade postponed, a first; 2,400+ flights delayed.",
     "CONFIRMED", "PowerOutage.us, NPR", "storm", -74.0, 40.7, (0, 0)),
    (5, "MAR-A-LAGO", "N AMER", "TRUMP",
     "Trump welcomes Putin to G20 in Miami",
     "Trump says Putin \"would like to make a deal\" to end the Ukraine war.",
     "CONFIRMED", "Kyiv Post", "maralago", -80.05, 26.47, (0, 0)),
    (6, "GAZA", "MIDEAST", "CEASEFIRE",
     "Israel kills senior Hamas official in Gaza",
     "Khaled Abu Nada dies in a Deir al-Balah flat, third such killing "
     "since Tue.",
     "CONFIRMED", "AP, Dawn", "gaza", 34.45, 31.5, (-9, 3)),
    (7, "E. CONGO", "AFRICA", "HEALTH",
     "Ebola outbreak passes 12,000 cases",
     "12,021 cases, 5,904 dead, ministry data show; fighting forces "
     "responders out.",
     "OFFICIAL", "DRC health ministry", "ebola", 29.5, 0.5, (0, 0)),
    (8, "KYIV", "EUROPE", "UKRAINE WAR",
     "Russia fires 155 drones overnight",
     "110 downed; hits at 27 sites. Estonia scrambles NATO jets as "
     "alerts sound.",
     "OFFICIAL", "Ukraine Air Force", "kyiv", 30.5, 50.45, (3, 0)),
    (9, "WELLINGTON", "OCEANIA", "ELECTION",
     "NZ final count leaves hung House",
     "Coalition holds 65 of 130 seats, one short; Opportunity (7) now "
     "decides.",
     "OFFICIAL", "Electoral Commission", "wellington", 174.8, -41.3, (-14, 0)),
    (10, "LONDON", "EUROPE", "MIGRATION",
     "UK net migration falls to 77,000",
     "Lowest since 1997 outside Covid; 738,000 in, 661,000 out in year "
     "to June.",
     "OFFICIAL", "ONS", "london", -0.1, 51.5, (-7, -5)),
    (11, "SEOUL", "E ASIA", "ECONOMY",
     "Bank of Korea lifts rate to 3.25%",
     "Third hike since July, 5-2 vote; 2027 growth forecast lifted to "
     "4.1% on chips.",
     "OFFICIAL", "Bank of Korea", "seoul", 127.0, 37.55, (0, 0)),
    (12, "GENEVA", "EUROPE", "CHESS",
     "Chess title match still level at 1.5-1.5",
     "Game 3 ends in a 60-move draw; Gukesh holds Sindarov with Black. "
     "Game 4 on Sat.",
     "CONFIRMED", "Chess.com", "chess", 6.14, 46.2, (-3, 9)),
    (13, "JAZAN", "MIDEAST", "ENERGY",
     "Houthi strike hits Saudi Aramco refinery",
     "One Nepali worker killed, several hurt; part of the refinery "
     "halted.",
     "CONFIRMED", "Saudi Energy Ministry", "jazan", 42.55, 16.9, (5, 11)),
]

# One-line stories 14-52: (city, region, text). Regions must sum with the
# pictured stories to: EUROPE 16, S ASIA 8, E ASIA 7, MIDEAST 7,
# AFRICA 5, SE ASIA 3, N AMER 2, GLOBAL 2, LAT AM 1, OCEANIA 1 = 52.
MORE = [
    ("Karachi", "S ASIA", "Building toll now 8; 13 missing"),
    ("Bangkok", "SE ASIA", "Fire at Bangchak refinery; units shut"),
    ("Paris", "EUROPE", "Depardieu to face trial over 2018 case"),
    ("Nairobi", "AFRICA", "Court halts US-backed Ebola facility"),
    ("Yangon", "SE ASIA", "Myanmar rejects parts of ICJ ruling"),
    ("Taiz", "MIDEAST", "Strike blamed on Saudis kills 11"),
    ("Quetta", "S ASIA", "Convoy attack kills 7 soldiers"),
    ("Helsinki", "EUROPE", "Finland extends border act to 2028"),
    ("Minsk", "EUROPE", "Russia, Ukraine swap bodies of fallen"),
    ("Cairo", "AFRICA", "AFP hit by cyberattack; site offline"),
    ("Kathmandu", "S ASIA", "Nepal to declare 4,000 flood dead"),
    ("Dhaka", "S ASIA", "Tear gas fired at garment protests"),
    ("Buenos Aires", "LAT AM", "Argentina bans money printing"),
    ("Jakarta", "SE ASIA", "Candy factory fire toll rises to 26"),
    ("Berlin", "EUROPE", "SAP weighs cutting 10,000 jobs"),
    ("Shanghai", "E ASIA", "Nvidia chips at Huang-linked site"),
    ("New Delhi", "S ASIA", "India wants Pakistan drama off Netflix"),
    ("Kyiv", "EUROPE", "Zelenskyy warns on Black Sea exports"),
    ("Markets", "GLOBAL", "Gold steadies near $3,565"),
    ("Geneva", "GLOBAL", "UN: hunger to worsen in 16 areas"),
    ("Warsaw", "EUROPE", "Poland to sign Palantir defence deal"),
    ("Kyiv", "EUROPE", "Russia has lost 1.6m troops, Kyiv claims"),
    ("New Delhi", "S ASIA", "Modi to revive women's quota bill"),
    ("Taipei", "E ASIA", "Taiwan, EU eye closer defence ties"),
    ("Berlin", "EUROPE", "India, Germany hold partnership talks"),
    ("Islamabad", "S ASIA", "PTI condemns bid to detain Rehman"),
    ("Tokyo", "E ASIA", "Japan eyes JPY 35bn defence over 5 years"),
    ("Cairo", "AFRICA", "Tanker fire kills 31; driver detained*"),
    ("Kuwait", "MIDEAST", "Kuwait summons Iran envoy over attacks"),
    ("Tallinn", "EUROPE", "Estonia scrambles NATO jets"),
    ("New Delhi", "S ASIA", "Building collapse kills 2; 8 rescued"),
    ("Seoul", "E ASIA", "Samsung pays KRW 30tn dividend"),
    ("Riyadh", "MIDEAST", "Houthis claimed Ras Tanura strikes"),
    ("Brussels", "EUROPE", "Costa gets 3 weeks for budget deal"),
    ("Beijing", "E ASIA", "Trump plays down China-Iran intel row"),
    ("Budapest", "EUROPE", "3 states sit out Ukraine loan"),
    ("London", "EUROPE", "UK condemns Kuwait drone strike"),
    ("Kinshasa", "AFRICA", "WHO unveils $1.58bn Ebola plan"),
    ("Seoul", "E ASIA", "Finance chiefs hold fire after hike"),
]

STATS = [
    ("2", "Italians killed in Kuwait strike"),
    ("$97.71", "Brent intraday, top since 9 Nov"),
    ("EUR 45bn", "Ukraine loan backed by 24 states"),
    ("980,000", "Peak without power in US storm"),
    ("12,021", "Ebola cases in DR Congo"),
    ("77,000", "UK net migration at 29-year low"),
]

REGION_ORDER = [
    ("EUROPE", 16), ("S ASIA", 8), ("E ASIA", 7), ("MIDEAST", 7),
    ("AFRICA", 5), ("SE ASIA", 3), ("N AMER", 2), ("GLOBAL", 2),
    ("LAT AM", 1), ("OCEANIA", 1),
]

TIMELINE = [
    ("00:00", "Storm peak:\n~980,000 lose power"),
    ("01:00", "NZ final count:\nhung House"),
    ("02:00", "EU summit ends,\nno deal"),
    ("07:45", "Brent hits\n$97.71"),
    ("11:00", "Kuwait strike\nkills 2"),
    ("16:00", "Russia fires\n155 drones"),
    ("18:50", "Chess Game 3\ndrawn: 1.5-1.5"),
]

# Dotted world map: landmass ranges per row, 60 columns x 26 rows.
# Columns map lon -180..180, rows map lat 90..-90 (equirectangular).
LAND_ROWS = [
    [(6, 13), (44, 57)],
    [(4, 15), (21, 27), (40, 58)],
    [(3, 16), (21, 27), (36, 58)],
    [(2, 18), (21, 26), (35, 58)],
    [(2, 19), (29, 37), (38, 58)],
    [(3, 20), (29, 38), (39, 58)],
    [(4, 20), (29, 38), (40, 58)],
    [(5, 19), (29, 36), (37, 55)],
    [(6, 17), (29, 33), (36, 54)],
    [(7, 15), (28, 34), (36, 52)],
    [(9, 14), (28, 36), (37, 51)],
    [(11, 14), (19, 23), (28, 37), (38, 49)],
    [(18, 24), (29, 36), (39, 48)],
    [(18, 24), (29, 36), (39, 47)],
    [(18, 24), (30, 35), (40, 45)],
    [(18, 23), (30, 35), (49, 55)],
    [(19, 23), (30, 34), (49, 55)],
    [(19, 22), (30, 33), (49, 54), (58, 59)],
    [(19, 21), (50, 53), (58, 59)],
    [(19, 20), (58, 58)],
    [(20, 20)],
    [], [], [], [], [],
]

TOTAL_STORIES = 13 + len(MORE)
assert TOTAL_STORIES == 52, TOTAL_STORIES
assert sum(c for _, c in REGION_ORDER) == 52

# ---------------------------------------------------------------- helpers

def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap_text(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, font, width, max_lines, min_size, fname):
    """Wrap text; if it needs more than max_lines, shrink the font until
    it fits, then truncate the last line with an ellipsis if still long."""
    size = font.size
    while size >= min_size:
        f = load(fname, size) if size != font.size else font
        lines = wrap_text(draw, text, f, width)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
    lines = wrap_text(draw, text, load(fname, min_size), width)
    while len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while text_w(draw, last + " ...", load(fname, min_size)) > width \
                and len(last) > 4:
            last = last[:-1]
        lines[-1] = last + " ..."
    return lines, load(fname, min_size)


def chip(draw, x, y, text, bg, fg=WHITE):
    """Small rounded verification tag; returns its right edge."""
    f = load(SANS_B, 8)
    w = int(text_w(draw, text, f)) + 8
    draw.rounded_rectangle([x, y, x + w, y + 11], radius=2, fill=bg)
    draw.text((x + 4, y + 1), text, font=f, fill=fg)
    return x + w


def badge(draw, cx, cy, num, colour):
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=colour,
                 outline=WHITE, width=1)
    f = load(SANS_B, 10)
    t = str(num)
    draw.text((cx - text_w(draw, t, f) / 2, cy - 6), t, font=f, fill=WHITE)


# ---------------------------------------------------------------- scenes
# Each scene draws a flat illustration inside the box (x, y, w, h).

def _sky(d, x, y, w, h, top, bottom):
    for i in range(h):
        r = top[0] + (bottom[0] - top[0]) * i // h
        g = top[1] + (bottom[1] - top[1]) * i // h
        b = top[2] + (bottom[2] - top[2]) * i // h
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))


def _burst(d, cx, cy, r, colour):
    pts = []
    for k in range(16):
        ang = 3.14159 * k / 8
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * __import__("math").cos(ang),
                    cy + rr * __import__("math").sin(ang)))
    d.polygon(pts, fill=colour)


def scene_kuwait(d, x, y, w, h):
    _sky(d, x, y, w, h, (232, 148, 74), (122, 62, 40))
    gy = y + h - 16
    d.rectangle([x, gy, x + w, y + h], fill=(196, 158, 104))
    d.rectangle([x, gy, x + w, gy + 2], fill=(150, 110, 66))
    # radar mast and dish
    mx = x + w * 0.30
    d.line([(mx, gy), (mx, y + 12)], fill=(40, 40, 40), width=3)
    d.pieslice([mx - 16, y + 6, mx + 16, y + 30], 180, 360, fill=(60, 60, 60))
    d.line([(mx, y + 18), (mx + 20, y + 4)], fill=(40, 40, 40), width=2)
    # low building
    d.rectangle([x + w * 0.55, gy - 12, x + w * 0.92, gy], fill=(90, 78, 66))
    for i in range(4):
        d.rectangle([x + w * 0.58 + i * 12, gy - 9, x + w * 0.58 + i * 12 + 6,
                     gy - 3], fill=(232, 200, 120))
    # drone silhouette
    dx, dy = x + w * 0.68, y + 14
    d.ellipse([dx - 12, dy - 3, dx + 12, dy + 3], fill=(30, 30, 30))
    d.ellipse([dx - 20, dy - 6, dx - 10, dy - 2], fill=(30, 30, 30))
    d.ellipse([dx + 10, dy - 6, dx + 20, dy - 2], fill=(30, 30, 30))
    d.line([(dx - 16, dy + 8), (dx - 8, dy + 2)], fill=(30, 30, 30), width=2)
    d.line([(dx + 16, dy + 8), (dx + 8, dy + 2)], fill=(30, 30, 30), width=2)
    # explosion burst
    _burst(d, x + w * 0.86, y + h - 26, 11, (255, 190, 40))
    _burst(d, x + w * 0.86, y + h - 26, 6, (255, 120, 20))


def scene_hormuz(d, x, y, w, h):
    _sky(d, x, y, w, int(h * 0.55), (168, 205, 228), (214, 232, 240))
    d.ellipse([x + w * 0.78, y + 4, x + w * 0.94, y + 20], fill=(255, 214, 120))
    sy = y + int(h * 0.55)
    d.rectangle([x, sy, x + w, y + h], fill=(24, 88, 138))
    d.rectangle([x, sy, x + w, sy + 3], fill=(120, 180, 215))
    for i in range(5):
        wx = x + 8 + i * (w // 5)
        d.arc([wx, sy + 6, wx + 22, sy + 14], 0, 180, fill=(150, 200, 230))
    # tanker hull and deck
    hx, hy = x + w * 0.10, sy + 8
    d.polygon([(hx, hy), (hx + w * 0.62, hy), (hx + w * 0.58, hy + 16),
               (hx + 4, hy + 16)], fill=(28, 32, 40))
    d.rectangle([hx + 6, hy - 14, hx + w * 0.62, hy], fill=(140, 40, 36))
    for i, c in enumerate([(200, 60, 40), (40, 90, 160), (220, 170, 40),
                           (40, 130, 80)]):
        d.rectangle([hx + 10 + i * 26, hy - 13, hx + 32 + i * 26, hy - 2],
                    fill=c)
    # bridge tower
    d.rectangle([hx + w * 0.52, hy - 26, hx + w * 0.60, hy - 13],
                fill=(240, 240, 240))
    # mine with spikes, splash
    mx, my = x + w * 0.84, sy + 12
    for k in range(8):
        ang = 3.14159 * k / 4
        d.line([(mx, my), (mx + 11 * __import__("math").cos(ang),
                            my + 11 * __import__("math").sin(ang))],
               fill=(20, 20, 20), width=2)
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 20))
    d.arc([mx - 14, my - 2, mx - 2, my + 12], 90, 270, fill=WHITE)
    d.arc([mx + 2, my - 2, mx + 14, my + 12], 270, 90, fill=WHITE)
    # smoke
    for cx, cy, r in [(hx + 30, hy - 22, 6), (hx + 38, hy - 30, 8),
                      (hx + 48, hy - 38, 6)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 120))


def scene_brussels(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 160, 210), (190, 210, 235))
    bx, by = x + w * 0.14, y + h - 34
    d.rectangle([bx, by, bx + w * 0.72, y + h], fill=(30, 52, 96))
    d.rectangle([bx, by - 6, bx + w * 0.72, by], fill=(22, 40, 78))
    for r in range(2):
        for c in range(7):
            wx = bx + 8 + c * 22
            wy = by + 7 + r * 13
            d.rectangle([wx, wy, wx + 12, wy + 8], fill=(255, 214, 90))
    # circle of gold stars
    cx, cy = x + w * 0.5, y + 16
    for k in range(12):
        ang = 3.14159 * 2 * k / 12 - 1.5708
        sx = cx + 13 * __import__("math").cos(ang)
        sy = cy + 10 * __import__("math").sin(ang)
        d.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=GOLD)
    # flags
    for fx in (x + 8, x + w - 12):
        d.line([(fx, y + h - 26), (fx, y + h - 6)], fill=(60, 60, 60), width=2)
        d.rectangle([fx, y + h - 26, fx + 12, y + h - 18], fill=(26, 74, 158))


def scene_storm(d, x, y, w, h):
    _sky(d, x, y, w, h, (58, 64, 78), (110, 118, 132))
    for cx, cy, rx, ry in [(0.25, 0.22, 34, 13), (0.55, 0.14, 40, 14),
                           (0.82, 0.26, 32, 12)]:
        d.ellipse([x + w * cx - rx, y + h * cy - ry, x + w * cx + rx,
                   y + h * cy + ry], fill=(44, 48, 62))
    # lightning
    lx, ly = x + w * 0.72, y + 8
    d.polygon([(lx, ly), (lx - 6, ly + 18), (lx - 1, ly + 18),
               (lx - 8, ly + 34), (lx + 4, ly + 16), (lx - 1, ly + 16)],
              fill=(255, 214, 60))
    # rain
    for i in range(14):
        rx = x + 6 + i * (w // 14)
        d.line([(rx, y + h * 0.42), (rx - 4, y + h * 0.58)],
               fill=(190, 200, 215), width=1)
    # tilted power pole and sagging wires
    px = x + w * 0.22
    d.line([(px, y + h - 4), (px + 8, y + h * 0.45)], fill=(30, 26, 22),
           width=4)
    d.line([(px - 12, y + h * 0.55), (px + 22, y + h * 0.50)],
           fill=(30, 26, 22), width=3)
    d.arc([px - 30, y + h * 0.42, px + 60, y + h * 0.75], 20, 160,
          fill=(30, 26, 22))
    # fallen branch / debris
    d.line([(x + w * 0.6, y + h - 2), (x + w * 0.72, y + h - 12)],
           fill=(50, 40, 28), width=3)


def scene_maralago(d, x, y, w, h):
    _sky(d, x, y, w, h, (140, 195, 230), (225, 240, 248))
    d.ellipse([x + w * 0.80, y + 4, x + w * 0.93, y + 17], fill=(255, 214, 110))
    gy = y + h - 10
    d.rectangle([x, gy, x + w, y + h], fill=(120, 170, 90))
    # white building with red roof
    bx = x + w * 0.30
    d.polygon([(bx - 4, gy - 22), (bx + w * 0.44, gy - 22),
               (bx + w * 0.40, gy - 32), (bx, gy - 32)], fill=(178, 40, 40))
    d.rectangle([bx, gy - 22, bx + w * 0.44, gy], fill=(248, 246, 240))
    for i in range(4):
        d.rectangle([bx + 8 + i * 24, gy - 17, bx + 18 + i * 24, gy - 6],
                    fill=(90, 120, 150))
    d.rectangle([bx + w * 0.20, gy - 12, bx + w * 0.26, gy], fill=(120, 80, 40))
    # palm trees
    for tx in (x + w * 0.12, x + w * 0.88):
        d.line([(tx, gy), (tx + 4, gy - 26)], fill=(110, 80, 40), width=3)
        for k in range(5):
            ang = 3.14159 * (0.15 + 0.18 * k)
            d.arc([tx - 12, gy - 38, tx + 16, gy - 16], 180 + k * 36,
                  180 + k * 36 + 70, fill=(40, 120, 60))
    # US flag on a pole
    fx = x + w * 0.62
    d.line([(fx, gy - 34), (fx, gy)], fill=(60, 60, 60), width=2)
    for i in range(4):
        d.rectangle([fx, gy - 34 + i * 4, fx + 18, gy - 31 + i * 4],
                    fill=(178, 40, 40) if i % 2 == 0 else WHITE)
    d.rectangle([fx, gy - 34, fx + 8, gy - 26], fill=(26, 60, 130))


def scene_gaza(d, x, y, w, h):
    _sky(d, x, y, w, h, (214, 196, 164), (238, 226, 200))
    gy = y + h - 8
    d.rectangle([x, gy, x + w, y + h], fill=(170, 150, 120))
    # buildings
    for bx, bw, bh in [(0.06, 0.26, 34), (0.36, 0.22, 44), (0.62, 0.30, 28)]:
        bx0 = x + w * bx
        d.rectangle([bx0, gy - bh, bx0 + w * bw, gy], fill=(196, 178, 146))
        for r in range(3):
            for c in range(3):
                wx = bx0 + 5 + c * 14
                wy = gy - bh + 6 + r * 11
                d.rectangle([wx, wy, wx + 7, wy + 6], fill=(90, 78, 60))
    # damaged building with smoke
    dx = x + w * 0.62
    d.polygon([(dx, gy - 28), (dx + w * 0.30, gy - 28), (dx + w * 0.26, gy),
               (dx + 4, gy)], fill=(150, 132, 104))
    for cx, cy, r in [(0.72, 0.30, 9), (0.76, 0.18, 12), (0.70, 0.08, 8)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(110, 108, 104))
    # rubble
    for tx in (0.10, 0.45):
        d.polygon([(x + w * tx, gy), (x + w * tx + 12, gy - 9),
                   (x + w * tx + 24, gy)], fill=(120, 104, 82))


def scene_ebola(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 90, 96), (34, 140, 132))
    # virus shapes: spiky circles
    for cx, cy, r, col in [(0.24, 0.42, 13, (190, 60, 60)),
                           (0.55, 0.60, 16, (220, 80, 70)),
                           (0.82, 0.34, 11, (190, 60, 60))]:
        vx, vy = x + w * cx, y + h * cy
        for k in range(10):
            ang = 3.14159 * 2 * k / 10
            d.line([(vx, vy), (vx + (r + 6) * __import__("math").cos(ang),
                                vy + (r + 6) * __import__("math").sin(ang))],
                   fill=col, width=2)
            ex = vx + (r + 7) * __import__("math").cos(ang)
            ey = vy + (r + 7) * __import__("math").sin(ang)
            d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=col)
        d.ellipse([vx - r, vy - r, vx + r, vy + r], fill=col)
        d.ellipse([vx - r * 0.45, vy - r * 0.45, vx + r * 0.2, vy + r * 0.2],
                  fill=(255, 140, 130))
    # red cross badge
    cx, cy = x + w * 0.86, y + h - 12
    d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=WHITE)
    d.rectangle([cx - 3, cy - 9, cx + 3, cy + 9], fill=WHITE)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=WHITE, width=1)


def scene_kyiv(d, x, y, w, h):
    _sky(d, x, y, w, h, (14, 22, 48), (40, 58, 96))
    for sx, sy in [(0.1, 0.15), (0.3, 0.08), (0.55, 0.2), (0.8, 0.1),
                   (0.92, 0.28)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * sx + 2, y + h * sy + 2],
                  fill=(220, 225, 240))
    gy = y + h - 6
    d.rectangle([x, gy, x + w, y + h], fill=(10, 14, 28))
    # skyline with lit windows
    for bx, bw, bh in [(0.04, 0.16, 26), (0.24, 0.12, 36), (0.40, 0.18, 22),
                       (0.62, 0.14, 32), (0.80, 0.16, 24)]:
        bx0 = x + w * bx
        d.rectangle([bx0, gy - bh, bx0 + w * bw, gy], fill=(22, 30, 54))
        for r in range(2):
            for c in range(3):
                if (r + c) % 2 == 0:
                    wx = bx0 + 4 + c * 10
                    wy = gy - bh + 5 + r * 10
                    d.rectangle([wx, wy, wx + 5, wy + 5], fill=(255, 210, 90))
    # drones with red lights and trails
    for dx, dy in [(0.30, 0.22), (0.62, 0.30), (0.85, 0.18)]:
        px, py = x + w * dx, y + h * dy
        d.line([(px - 26, py + 10), (px, py)], fill=(150, 160, 190), width=1)
        d.ellipse([px - 7, py - 2, px + 7, py + 2], fill=(200, 205, 215))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 60, 50))
    # defence flash
    _burst(d, x + w * 0.48, y + h * 0.42, 8, (255, 210, 80))

def scene_wellington(d, x, y, w, h):
    _sky(d, x, y, w, h, (150, 190, 220), (215, 232, 240))
    d.ellipse([x + w * 0.82, y + 5, x + w * 0.94, y + 17], fill=(255, 214, 110))
    gy = y + h - 8
    d.rectangle([x, gy, x + w, y + h], fill=(110, 150, 90))
    # beehive parliament: stacked rounded tiers
    cx = x + w * 0.30
    for i, (tw, th) in enumerate([(52, 8), (44, 8), (36, 8), (26, 8)]):
        ty = gy - 8 - i * 8
        d.rectangle([cx - tw / 2, ty, cx + tw / 2, ty + 8],
                    fill=(150, 140, 120) if i % 2 == 0 else (170, 160, 140))
    d.rectangle([cx - 3, gy - 40, cx + 3, gy - 32], fill=(120, 110, 95))
    # parliament block with flag
    bx = x + w * 0.58
    d.rectangle([bx, gy - 26, bx + w * 0.30, gy], fill=(200, 190, 170))
    d.rectangle([bx, gy - 30, bx + w * 0.30, gy - 26], fill=(140, 30, 30))
    d.line([(bx + w * 0.15, gy - 44), (bx + w * 0.15, gy - 30)],
           fill=(60, 60, 60), width=2)
    d.rectangle([bx + w * 0.15, gy - 44, bx + w * 0.15 + 14, gy - 37],
                fill=(26, 60, 130))
    # seat bars: 65 vs 65 deadlock
    for i, (bh, col) in enumerate([(16, (26, 74, 158)), (16, (178, 32, 32))]):
        bx0 = x + 8 + i * 22
        d.rectangle([bx0, gy - 4 - bh, bx0 + 16, gy - 4], fill=col)
    d.text((x + 8, gy - 26), "65-65", font=load(SANS_B, 9), fill=INK)


def scene_london(d, x, y, w, h):
    _sky(d, x, y, w, h, (170, 185, 205), (225, 230, 238))
    gy = y + h - 8
    d.rectangle([x, gy, x + w, y + h], fill=(120, 125, 135))
    # clock tower
    tx = x + w * 0.14
    d.rectangle([tx, y + 12, tx + 18, gy], fill=(150, 130, 90))
    d.polygon([(tx - 2, y + 12), (tx + 20, y + 12), (tx + 9, y + 2)],
              fill=(60, 70, 60))
    d.ellipse([tx + 2, y + 16, tx + 16, y + 30], fill=(245, 242, 230))
    d.line([(tx + 9, y + 23), (tx + 9, y + 18)], fill=INK, width=1)
    d.line([(tx + 9, y + 23), (tx + 13, y + 23)], fill=INK, width=1)
    # arrivals board
    bx = x + w * 0.44
    d.rectangle([bx, y + 16, bx + w * 0.46, y + 40], fill=(20, 26, 36))
    for i in range(3):
        d.rectangle([bx + 4, y + 20 + i * 7, bx + w * 0.46 - 4, y + 24 + i * 7],
                    fill=(255, 210, 90) if i == 0 else (140, 170, 200))
    # plane silhouette
    px, py = x + w * 0.70, y + h * 0.62
    d.ellipse([px - 22, py - 3, px + 22, py + 3], fill=(240, 242, 245))
    d.polygon([(px + 18, py), (px + 30, py - 8), (px + 30, py + 2)],
              fill=(240, 242, 245))
    d.polygon([(px - 2, py - 2), (px + 8, py - 14), (px + 14, py - 2)],
              fill=(210, 215, 222))
    d.line([(px - 24, py + 8), (px - 30, py + 14)], fill=(210, 215, 222),
           width=2)


def scene_seoul(d, x, y, w, h):
    _sky(d, x, y, w, h, (150, 180, 220), (220, 232, 244))
    gy = y + h - 8
    d.rectangle([x, gy, x + w, y + h], fill=(140, 145, 155))
    # bank building with columns
    bx = x + w * 0.10
    d.polygon([(bx, y + 22), (bx + w * 0.42, y + 22), (bx + w * 0.36, y + 12),
               (bx + w * 0.06, y + 12)], fill=(90, 100, 118))
    d.rectangle([bx, y + 22, bx + w * 0.42, gy], fill=(200, 205, 215))
    for i in range(5):
        cx = bx + 8 + i * 16
        d.rectangle([cx, y + 26, cx + 7, gy - 4], fill=(120, 128, 142))
    # rising arrow chart
    pts = [(x + w * 0.58, y + h - 22), (x + w * 0.68, y + h - 34),
           (x + w * 0.74, y + h - 28), (x + w * 0.88, y + h - 44)]
    d.line(pts, fill=(22, 130, 70), width=3)
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 10, ay + 2), (ax - 2, ay + 10)], fill=(22, 130, 70))
    # chip
    cx, cy = x + w * 0.86, y + 14
    d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(30, 36, 48))
    d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 210, 90))
    for k in range(3):
        d.line([(cx - 8, cy - 5 + k * 5), (cx - 12, cy - 5 + k * 5)],
               fill=(30, 36, 48), width=1)
        d.line([(cx + 8, cy - 5 + k * 5), (cx + 12, cy - 5 + k * 5)],
               fill=(30, 36, 48), width=1)


def scene_chess(d, x, y, w, h):
    _sky(d, x, y, w, h, (96, 74, 58), (150, 122, 96))
    # board 4x4
    bs = min(w * 0.52, h - 12)
    bx, by = x + w * 0.08, y + 6
    sq = bs / 4
    for r in range(4):
        for c in range(4):
            col = (240, 232, 214) if (r + c) % 2 == 0 else (52, 44, 38)
            d.rectangle([bx + c * sq, by + r * sq, bx + (c + 1) * sq,
                         by + (r + 1) * sq], fill=col)
    d.rectangle([bx, by, bx + bs, by + bs], outline=(30, 24, 18), width=2)
    # pieces: K white, Q black, N white, P black
    f = load(SANS_B, int(sq * 0.62))
    for (r, c, letter, col) in [(0, 1, "K", (20, 20, 20)),
                                (1, 2, "Q", (245, 240, 228)),
                                (2, 0, "N", (20, 20, 20)),
                                (3, 3, "P", (245, 240, 228))]:
        px, py = bx + c * sq, by + r * sq
        d.ellipse([px + 1, py + 1, px + sq - 1, py + sq - 1],
                  fill=(250, 246, 236) if col == (20, 20, 20) else (30, 26, 22))
        tw = text_w(d, letter, f)
        d.text((px + (sq - tw) / 2, py + sq * 0.16), letter, font=f, fill=col)
    # clock
    cx = x + w * 0.72
    d.rectangle([cx, y + 12, cx + w * 0.22, y + 34], fill=(20, 22, 28))
    d.text((cx + 4, y + 15), "1.5-1.5", font=load(SANS_B, 11), fill=(255, 210, 90))
    d.text((cx + 2, y + 40), "GAME 3", font=load(SANS_B, 8), fill=INK)
    d.text((cx + 2, y + 50), "60 MOVES", font=load(SANS_B, 8), fill=INK)


def scene_jazan(d, x, y, w, h):
    _sky(d, x, y, w, h, (210, 130, 70), (90, 60, 52))
    gy = y + h - 8
    d.rectangle([x, gy, x + w, y + h], fill=(70, 58, 48))
    # refinery towers and tanks
    for tx, tw, th in [(0.08, 0.10, 34), (0.22, 0.08, 44), (0.34, 0.12, 28)]:
        tx0 = x + w * tx
        d.rectangle([tx0, gy - th, tx0 + w * tw, gy], fill=(120, 118, 116))
        d.rectangle([tx0 - 2, gy - th - 6, tx0 + w * tw + 2, gy - th],
                    fill=(90, 88, 86))
    for tx in (0.52, 0.68):
        tx0 = x + w * tx
        d.ellipse([tx0, gy - 16, tx0 + w * 0.14, gy], fill=(150, 148, 144))
    # pipes
    d.line([(x + w * 0.10, gy - 10), (x + w * 0.85, gy - 10)],
           fill=(90, 88, 86), width=3)
    # flame
    fx, fy = x + w * 0.24, gy - 46
    d.polygon([(fx - 8, fy + 8), (fx - 2, fy - 10), (fx + 3, fy - 2),
               (fx + 8, fy - 12), (fx + 10, fy + 8)], fill=(255, 150, 30))
    d.polygon([(fx - 4, fy + 8), (fx, fy - 2), (fx + 5, fy + 8)],
              fill=(255, 220, 80))
    # smoke
    for cx, cy, r in [(0.24, 0.28, 8), (0.28, 0.16, 10), (0.22, 0.06, 7)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(100, 96, 92))


SCENES = {
    "kuwait": scene_kuwait, "hormuz": scene_hormuz,
    "brussels": scene_brussels, "storm": scene_storm,
    "maralago": scene_maralago, "gaza": scene_gaza,
    "ebola": scene_ebola, "kyiv": scene_kyiv,
    "wellington": scene_wellington, "london": scene_london,
    "seoul": scene_seoul, "chess": scene_chess, "jazan": scene_jazan,
}


# ---------------------------------------------------------------- layout

def draw_panel(d, story, x, y, w, h, large):
    (num, city, region, topic, headline, body, tag, source, scene,
     _lon, _lat, _nudge) = story
    colour = REGION_COLOUR[region]
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=LIGHT_LINE, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=colour)
    ih = 56 if large else 46
    SCENES[scene](d, x + 1, y + 4, w - 2, ih)
    badge(d, x + 13, y + 15, num, colour)
    ty = y + ih + 7
    kicker = "%s - %s - %s" % (city, region, topic)
    kf = load(SANS_B, 9 if large else 8)
    d.text((x + 6, ty), kicker, font=kf, fill=colour)
    ty += 13 if large else 12
    hsize = 15 if large else 13
    hlines, hf = fit_block(d, headline, load(SANS_B, hsize), w - 12, 2, 11,
                           SANS_B)
    for ln in hlines:
        d.text((x + 6, ty), ln, font=hf, fill=INK)
        ty += hf.size + 2
    ty += 1
    bsize = 10 if large else 9
    blines, bf = fit_block(d, body, load(SANS, bsize), w - 12, 2, 8, SANS)
    for ln in blines:
        d.text((x + 6, ty), ln, font=bf, fill=(52, 56, 64))
        ty += bf.size + 3
    # tag row pinned to the panel bottom
    tag_y = y + h - 15
    tag_bg = GREEN_TAG if tag in ("CONFIRMED", "OFFICIAL") else (150, 90, 20)
    end = chip(d, x + 6, tag_y, tag, tag_bg)
    sf = load(SANS, 8)
    d.text((end + 5, tag_y + 1), source, font=sf, fill=GREY)


def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 234, 222),
                outline=LIGHT_LINE, width=1)
    cols, rows = 60, 26
    dx, dy = w / cols, h / rows
    for r, ranges in enumerate(LAND_ROWS):
        for a, b in ranges:
            for c in range(a, b + 1):
                cx = x0 + (c + 0.5) * dx
                cy = y0 + (r + 0.5) * dy
                d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5],
                          fill=(120, 116, 104))
    for story in PICTURED:
        (num, _c, region, _t, _h, _b, _tag, _s, _sc, lon, lat, (nx, ny)) = story
        px = x0 + (lon + 180) / 360 * w + nx
        py = y0 + (90 - lat) / 180 * h + ny
        badge(d, px, py, num, REGION_COLOUR[region])


def draw_more(d, x0, y0, col_w, items, start_num):
    f10, f9, f85 = load(SANS, 9), load(SANS, 8), load(SANS, 8)
    fb = load(SANS_B, 9)
    row_h = 10
    for i, (city, region, text) in enumerate(items):
        n = start_num + i
        yy = y0 + i * row_h
        head = "%d %s: " % (n, city)
        for f in (f10, f9, f85):
            if text_w(d, head, fb) + text_w(d, text, f) <= col_w:
                break
        else:
            f = f85
            while text_w(d, head, fb) + text_w(d, text + " ...", f) > col_w \
                    and len(text) > 8:
                text = text[:-1]
            text += " ..."
        d.text((x0, yy), head, font=fb, fill=INK)
        d.text((x0 + text_w(d, head, fb), yy), text, font=f,
               fill=(52, 56, 64))


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14
    CW = W - 2 * M  # 996

    # nameplate band
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((M, 5), "THE WORLD IN ONE DAY", font=load(SANS_B, 13), fill=WHITE)
    right = "52 STORIES  -  10 REGIONS  -  FRIDAY 27 NOVEMBER 2026"
    rf = load(SANS_B, 11)
    d.text((W - M - text_w(d, right, rf), 6), right, font=rf, fill=GOLD)

    # masthead
    mast = "Friday 27 November 2026"
    mf = load(SERIF, 64)
    d.text(((W - text_w(d, mast, mf)) / 2, 28), mast, font=mf, fill=NAVY)
    kick = ("Storm cuts power to nearly a million Americans  -  Drone attack "
            "kills two Italians in Kuwait  -  EU summit ends with no budget deal")
    ksize = 14
    while ksize > 10:
        kf = load(SANS_B, ksize)
        if text_w(d, kick, kf) <= CW:
            break
        ksize -= 1
    d.text(((W - text_w(d, kick, kf)) / 2, 94), kick, font=kf, fill=RED)
    d.rectangle([M, 110, W - M, 112], fill=NAVY)
    d.rectangle([M, 114, W - M, 115], fill=RED)

    # stat strip
    sy, sh = 118, 44
    bw = (CW - 5 * 3) // 6
    for i, (num, label) in enumerate(STATS):
        bx = M + i * (bw + 3)
        d.rectangle([bx, sy, bx + bw, sy + sh], fill=WHITE,
                    outline=LIGHT_LINE, width=1)
        d.rectangle([bx, sy, bx + bw, sy + 2], fill=RED)
        nf = load(SANS_B, 22)
        d.text((bx + (bw - text_w(d, num, nf)) / 2, sy + 3), num, font=nf,
               fill=NAVY)
        lf = load(SANS, 9)
        lab_lines = wrap_text(d, label, lf, bw - 8)
        for j, ln in enumerate(lab_lines[:1]):
            d.text((bx + (bw - text_w(d, ln, lf)) / 2, sy + 29), ln,
                   font=lf, fill=GREY)

    # region bar
    ry = 166
    total = sum(c for _, c in REGION_ORDER)
    rx = M
    small_note = []
    for name, count in REGION_ORDER:
        seg_w = int(round(count / total * CW))
        if rx + seg_w > W - M:
            seg_w = W - M - rx
        col = REGION_COLOUR[name]
        d.rectangle([rx, ry, rx + seg_w, ry + 15], fill=col)
        lab = "%s %d" % (name, count)
        lf = load(SANS_B, 9)
        if seg_w >= 52 and text_w(d, lab, lf) <= seg_w - 4:
            d.text((rx + (seg_w - text_w(d, lab, lf)) / 2, ry + 3), lab,
                   font=lf, fill=WHITE)
        else:
            small_note.append(lab)
        rx += seg_w
    note = "  -  ".join(small_note)
    nf = load(SANS, 8)
    d.text((M, ry + 18), note, font=nf, fill=GREY)

    # UTC timeline
    ty = 200
    d.rectangle([M, ty, M + 116, ty + 30], fill=NAVY)
    d.text((M + 10, ty + 3), "THE DAY", font=load(SANS_B, 12), fill=WHITE)
    d.text((M + 10, ty + 16), "IN UTC", font=load(SANS_B, 12), fill=GOLD)
    lx0, lx1, ly = M + 132, W - M - 8, ty + 18
    d.line([(lx0, ly), (lx1, ly)], fill=NAVY, width=2)
    n = len(TIMELINE)
    for i, (tm, lab) in enumerate(TIMELINE):
        cx = lx0 + (lx1 - lx0) * i / (n - 1)
        d.ellipse([cx - 4, ly - 4, cx + 4, ly + 4], fill=RED, outline=WHITE,
                  width=1)
        tf = load(SANS_B, 11)
        tw = text_w(d, tm, tf)
        d.text((min(max(cx - tw / 2, lx0), W - M - tw), ty + 2), tm,
               font=tf, fill=RED)
        lf = load(SANS, 9)
        for j, ln in enumerate(lab.split("\n")):
            lw = text_w(d, ln, lf)
            lx = min(max(cx - lw / 2, M), W - M - lw)
            d.text((lx, ly + 7 + j * 10), ln, font=lf, fill=(52, 56, 64))

    # pictured stories: 3 large, then 5 + 5 small
    py = 252
    lw = (CW - 2 * 9) // 3
    for i in range(3):
        draw_panel(d, PICTURED[i], M + i * (lw + 9), py, lw, 148, True)
    py = 408
    sw = (CW - 4 * 8) // 5
    for row in range(2):
        for col in range(5):
            idx = 3 + row * 5 + col
            draw_panel(d, PICTURED[idx], M + col * (sw + 8), py, sw, 136,
                       False)
        py += 144

    # bottom headings
    hy = 694
    d.text((M, hy), "WHERE IT HAPPENED", font=load(SANS_B, 13), fill=INK)
    sub = "pins = picture numbers, coloured by region"
    d.text((M + 168, hy + 2), sub, font=load(SANS, 9), fill=GREY)
    d.text((520, hy), "ALSO ON 27 NOVEMBER: 39 MORE STORIES",
           font=load(SANS_B, 13), fill=INK)

    # map and more-stories list
    draw_map(d, M, 712, 494, 120)
    cap = ("Dotted map: pins are pictured stories 1-13; Europe and the "
           "Gulf are crowded.")
    cf = load(SANS, 9)
    d.text((M, 838), cap, font=cf, fill=GREY)
    draw_more(d, 520, 712, 238, MORE[:20], 14)
    draw_more(d, 772, 712, 238, MORE[20:], 34)

    # footer
    fy = 918
    d.line([(M, fy), (W - M, fy)], fill=NAVY, width=2)
    lab_f = load(SANS_B, 10)
    body_f = load(SANS, 10)
    d.text((M, fy + 6), "DATE CHECK", font=lab_f, fill=RED)
    dc = ("Every story was first reported on Friday 27 November 2026; events "
          "shown happened Thu 26-Fri 27 Nov. Older context flagged: NZ election "
          "was 7 Nov (final count Fri); UK migration covers the year to Jun 2026; "
          "Ebola totals are cumulative; *Cairo tanker fire and Karachi building "
          "collapse were Wed 25 Nov.")
    for j, ln in enumerate(wrap_text(d, dc, body_f, CW - 92)):
        d.text((M + 92, fy + 6 + j * 12), ln, font=body_f, fill=INK)
    hy2 = fy + 34
    d.text((M, hy2), "HOW SURE", font=lab_f, fill=RED)
    hs = ("OFFICIAL = said by a government, court or agency  -  CONFIRMED = "
          "carried by two or more outlets  -  CLAIM = one side's account, "
          "not verified")
    d.text((M + 92, hy2), hs, font=body_f, fill=INK)
    sy2 = hy2 + 16
    src = ("Sources: Reuters - AP - BBC - CNN - Dawn - Kyiv Post - NPR - ONS - "
           "Bank of Korea - NZ Electoral Commission - Ukraine Air Force - "
           "Saudi Energy Ministry - PowerOutage.us. Pictures and map drawn "
           "in code.")
    for j, ln in enumerate(wrap_text(d, src, load(SANS, 9), CW)):
        d.text((M, sy2 + j * 11), ln, font=load(SANS, 9), fill=GREY)
    by = H - 16
    d.text((M, by), "PAGE 1  -  WORLD NEWS  -  PRINTED 27 NOVEMBER 2026  -  "
                    "EDITION NO. 11,429", font=load(SANS, 9), fill=GREY)
    tail = "52 STORIES  -  ALL VERIFIED 27 NOV 2026"
    tf = load(SANS_B, 9)
    d.text((W - M - text_w(d, tail, tf), by), tail, font=tf, fill=NAVY)
    return img


def main():
    img = render()
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    data = buf.getvalue()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.jpg"), "wb") as f:
        f.write(data)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("stories: %d" % TOTAL_STORIES)
    print("bytes: %d" % len(data))
    print("sha256: %s" % digest)


if __name__ == "__main__":
    main()
