#!/usr/bin/env python3
"""Round 10: one-image summary of world news, Friday 27 November 2026.

Fresh rebuild of the front page. Design changes vs round 9: the top-3 hero
pictures are much taller and brighter (pale skies, big simple subjects),
every hero carries a WHY IT MATTERS line, the masthead date is drawn in a
single navy colour with the red kicker on its own clear band below it, the
dark night scenes are re-lit as bright dusk, the world map uses leader-line
pins so Europe and the Gulf no longer crowd, and the 39 extra stories move
to two wider columns beside the map. All 52 stories, stats, timeline and
footers are kept from the verified round-9 set.

Facts were checked against live reporting on 27 November 2026 (Reuters,
AP, BBC, CNN, Dawn, Kyiv Post, NPR, ONS, Bank of Korea, NZ Electoral
Commission, DRC health ministry, Ukraine Air Force, Saudi Energy
Ministry). Every picture and the map are drawn in code; nothing is pasted
in. Deterministic: same code gives the same bytes.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
INK = (22, 22, 22)
NAVY = (11, 31, 75)
NAVY2 = (30, 58, 138)
RED = (185, 28, 28)
RED2 = (153, 27, 27)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
SKY = (191, 227, 242)
GOLD = (245, 176, 65)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REGION = {
    "EUROPE": (29, 78, 216),
    "MIDEAST": (192, 57, 43),
    "AFRICA": (30, 122, 52),
    "S ASIA": (124, 58, 237),
    "E ASIA": (217, 119, 6),
    "SE ASIA": (14, 116, 144),
    "N AMER": (15, 118, 110),
    "OCEANIA": (67, 56, 202),
    "LATAM": (180, 83, 9),
    "GLOBAL": (107, 114, 128),
}

TAG_FILL = {"OFFICIAL": (30, 58, 138), "CONFIRMED": (22, 101, 52),
            "CLAIM": (180, 83, 9), "REPORTED": (120, 53, 15)}


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, line_h, align="left", width=None):
    for line in lines:
        lx = x
        if align == "center" and width is not None:
            lx = x + (width - text_w(draw, line, fnt)) / 2
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def shrink_to_fit(draw, text, path, size, max_w, min_size=7):
    """Largest font size at which `text` fits `max_w` (single line)."""
    while size > min_size and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


# ---------------------------------------------------------------- stories
# (num, region, kicker, headline, body, why, tag, source)
HEROES = [
    (1, "MIDEAST", "KUWAIT \u00b7 MIDEAST \u00b7 DRONE WAR",
     "Drone strike kills two Italians in Kuwait",
     "Rheinmetall Italia technicians hit at an air-defence site; "
     "Italy blames Iran, Tehran denies it.",
     "First deadly strike on Italians in the Gulf crisis.",
     "CONFIRMED", "Reuters, CNN"),
    (2, "MIDEAST", "STRAIT OF HORMUZ \u00b7 MIDEAST \u00b7 OIL",
     "Mines hit two tankers; Brent nears $97",
     "Ships catch fire off Oman; Brent climbed to $97.71, highest "
     "since 9 November.",
     "Oil at a three-week high; Strait fears grow.",
     "CONFIRMED", "Reuters"),
    (3, "EUROPE", "BRUSSELS \u00b7 EUROPE \u00b7 EU SUMMIT",
     "EU summit ends with no budget deal",
     "24 states back a EUR 45bn Ukraine loan for 2027, but the "
     "2028-34 budget talks fail. Dec retry.",
     "2027 funding is safe; the budget fight is not.",
     "OFFICIAL", "Costa, von der Leyen"),
]

CARDS = [
    (4, "N AMER", "NEW YORK \u00b7 N AMER \u00b7 WEATHER",
     "Storm cuts power to nearly 1m in US",
     "Macy's 100th parade postponed, a first; 2,400+ flights delayed.",
     "", "CONFIRMED", "PowerOutage.us, NPR"),
    (5, "N AMER", "MAR-A-LAGO \u00b7 N AMER \u00b7 TRUMP",
     "Trump welcomes Putin to G20 in Miami",
     "Trump says Putin \u201cwould like to make a deal\u201d on Ukraine.",
     "", "CONFIRMED", "Kyiv Post"),
    (6, "MIDEAST", "GAZA \u00b7 MIDEAST \u00b7 CEASEFIRE",
     "Israel kills senior Hamas official in Gaza",
     "Hamas official Abu Nada killed in Gaza, third since Tue.",
     "", "CONFIRMED", "AP, Dawn"),
    (7, "AFRICA", "E. CONGO \u00b7 AFRICA \u00b7 HEALTH",
     "Ebola outbreak passes 12,000 cases",
     "12,021 cases, 5,304 dead; fighting forces responders out.",
     "", "OFFICIAL", "DRC health ministry"),
    (8, "EUROPE", "KYIV \u00b7 EUROPE \u00b7 UKRAINE WAR",
     "Russia fires 155 drones overnight",
     "110 downed, hits at 27 sites; Estonia scrambles jets.",
     "", "OFFICIAL", "Ukraine Air Force"),
    (9, "OCEANIA", "WELLINGTON \u00b7 OCEANIA \u00b7 ELECTION",
     "NZ final count leaves hung House",
     "Coalition holds 65 of 130, one short; Opportunity (7) now decides.",
     "", "OFFICIAL", "Electoral Commission"),
    (10, "EUROPE", "LONDON \u00b7 EUROPE \u00b7 MIGRATION",
     "UK net migration falls to 77,000",
     "Lowest since 1997 outside Covid; 661,000 out in year to June.",
     "", "OFFICIAL", "ONS"),
    (11, "E ASIA", "SEOUL \u00b7 E ASIA \u00b7 ECONOMY",
     "Bank of Korea lifts rate to 3.25%",
     "Third hike since July, 5-2; 2027 growth lifted to 4.1% on chips.",
     "", "OFFICIAL", "Bank of Korea"),
    (12, "EUROPE", "GENEVA \u00b7 EUROPE \u00b7 CHESS",
     "Chess title match still level at 1.5-1.5",
     "Game 3 ends in a 60-move draw; Gukesh holds Black. Game 4 Sat.",
     "", "CONFIRMED", "Chess.com"),
    (13, "MIDEAST", "JAZAN \u00b7 MIDEAST \u00b7 ENERGY",
     "Houthi strike hits Saudi Aramco refinery",
     "One Nepali worker killed, several hurt; part of the refinery "
     "halted.",
     "", "CONFIRMED", "Saudi Energy Ministry"),
]

MORE = [
    (14, "Karachi", "Building toll now 8; 13 missing"),
    (15, "Bangkok", "Fire at Bangchak refinery; units shut"),
    (16, "Paris", "Depardieu to face trial over 2018 case"),
    (17, "Nairobi", "Court halts US-backed Ebola facility"),
    (18, "Yangon", "Myanmar rejects parts of ICJ ruling"),
    (19, "Taiz", "Strike blamed on Saudis kills 11"),
    (20, "Quetta", "Convoy attack kills 7 soldiers"),
    (21, "Helsinki", "Finland extends border act to 2028"),
    (22, "Minsk", "Russia, Ukraine swap bodies of fallen"),
    (23, "Cairo", "AFP hit by cyberattack; site offline"),
    (24, "Kathmandu", "Nepal to declare 4,000 flood dead"),
    (25, "Dhaka", "Tear gas fired at garment protests"),
    (26, "Buenos Aires", "Argentina bans money printing"),
    (27, "Jakarta", "Candy factory fire toll rises to 26"),
    (28, "Berlin", "SAP weighs cutting 10,000 jobs"),
    (29, "Shanghai", "Nvidia chips at Huang-linked site"),
    (30, "New Delhi", "India wants Pakistan drama off Netflix"),
    (31, "Kyiv", "Zelenskyy warns on Black Sea exports"),
    (32, "Markets", "Gold steadies near $3,565"),
    (33, "Geneva", "UN: hunger to worsen in 16 areas"),
    (34, "Warsaw", "Poland to sign Palantir defence deal"),
    (35, "Kyiv", "Russia has lost 1.6m troops, Kyiv claims"),
    (36, "New Delhi", "Modi to revive women's quota bill"),
    (37, "Taipei", "Taiwan, EU eye closer defence ties"),
    (38, "Berlin", "India, Germany hold partnership talks"),
    (39, "Islamabad", "PTI condemns bid to detain Rehman"),
    (40, "Tokyo", "Japan eyes JPY 35bn defence over 5 years"),
    (41, "Cairo", "Tanker fire kills 31; driver detained"),
    (42, "Kuwait", "Kuwait summons Iran envoy over attacks"),
    (43, "Tallinn", "Estonia scrambles NATO jets"),
    (44, "New Delhi", "Building collapse kills 2; 8 rescued"),
    (45, "Seoul", "Samsung pays KRW 30tn dividend"),
    (46, "Riyadh", "Houthis claimed Ras Tanura strikes"),
    (47, "Brussels", "Costa gets 3 weeks for budget deal"),
    (48, "Beijing", "Trump plays down China-Iran intel row"),
    (49, "Budapest", "3 states sit out Ukraine loan"),
    (50, "London", "UK condemns Kuwait drone strike"),
    (51, "Kinshasa", "WHO unveils $1.58bn Ebola plan"),
    (52, "Seoul", "Finance chiefs hold fire after hike"),
]

STATS = [
    ("2", "Italians killed in Kuwait strike"),
    ("$97.71", "Brent intraday, top since 9 Nov"),
    ("EUR 45bn", "Ukraine loan backed by 24 states"),
    ("980,000", "Peak without power in US storm"),
    ("12,021", "Ebola cases in DR Congo"),
    ("77,000", "UK net migration at 29-year low"),
]

REGION_BAR = [("EUROPE", 16, REGION["EUROPE"]),
              ("S ASIA", 8, REGION["S ASIA"]),
              ("E ASIA", 7, REGION["E ASIA"]),
              ("MIDEAST", 7, REGION["MIDEAST"]),
              ("AFRICA", 5, REGION["AFRICA"]),
              ("SE ASIA", 3, REGION["SE ASIA"]),
              ("N AMER", 2, REGION["N AMER"]),
              ("GLOBAL", 2, REGION["GLOBAL"]),
              ("LATAM", 1, REGION["LATAM"]),
              ("OCEANIA", 1, REGION["OCEANIA"])]

TIMELINE = [
    ("00:00", "Storm peak: ~980k out"),
    ("01:00", "NZ final count: hung House"),
    ("02:00", "EU summit ends, no deal"),
    ("07:45", "Brent hits $97.71"),
    ("11:00", "Kuwait strike kills 2"),
    ("16:00", "Russia fires 155 drones"),
    ("18:50", "Chess Game 3 drawn 1.5-1.5"),
]

# (num, lon, lat, nudge dx, dy) for the map pins, coloured by region
PINS = [
    (1, 47.5, 29.3, 16, 12), (2, 56.5, 26.5, 20, -8),
    (3, 4.35, 50.85, 12, -16), (4, -74.0, 40.7, -16, -10),
    (5, -80.0, 26.7, -18, 10), (6, 34.45, 31.5, -16, -14),
    (7, 29.2, -1.7, 14, 10), (8, 30.5, 50.45, 20, 6),
    (9, 174.8, -41.3, 12, -12), (10, -0.12, 51.5, -16, -16),
    (11, 127.0, 37.5, 16, -8), (12, 6.14, 46.2, -18, 12),
    (13, 42.55, 16.9, -18, 12),
]
PIN_REGION = {1: "MIDEAST", 2: "MIDEAST", 3: "EUROPE", 4: "N AMER",
              5: "N AMER", 6: "MIDEAST", 7: "AFRICA", 8: "EUROPE",
              9: "OCEANIA", 10: "EUROPE", 11: "E ASIA", 12: "EUROPE",
              13: "MIDEAST"}


# ------------------------------------------------------- illustrations
def _sky(d, x, y, w, h, top, bottom):
    """Vertical gradient sky, bright at the horizon."""
    for i in range(h):
        t = i / max(1, h - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=col)


def _sun(d, cx, cy, r, core=(255, 214, 90), ring=(255, 170, 40)):
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=ring)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=core)


def _cloud(d, x, y, s, fill=(255, 255, 255)):
    d.ellipse([x, y, x + 3 * s, y + 2 * s], fill=fill)
    d.ellipse([x + s, y - s, x + 3 * s, y + s], fill=fill)


def illo_kuwait(d, x, y, w, h):
    _sky(d, x, y, w, h, (168, 214, 240), (252, 222, 160))
    _sun(d, x + w - 42, y + 30, 20)
    _cloud(d, x + 18, y + 16, 12)
    gy = y + h - 26
    d.rectangle([x, gy, x + w, y + h], fill=(214, 178, 120))
    d.rectangle([x, gy - 14, x + 70, gy], fill=(120, 120, 118))
    d.rectangle([x + 8, gy - 26, x + 62, gy - 14], fill=(150, 150, 148))
    for i in range(4):
        d.rectangle([x + 12 + i * 13, gy - 22, x + 20 + i * 13, gy - 16],
                    fill=(70, 70, 70))
    # radar dish
    cx, cy = x + w - 105, gy - 34
    d.line([(cx, cy + 30), (cx, cy)], fill=(60, 60, 60), width=5)
    d.pieslice([cx - 34, cy - 34, cx + 34, cy + 6], 180, 360, fill=(240, 240, 240),
               outline=(60, 60, 60), width=2)
    d.line([(cx, cy), (cx + 26, cy - 26)], fill=(60, 60, 60), width=3)
    # drone, big and central
    dx, dy = x + 118, y + 32
    d.line([(dx - 52, dy - 8), (dx + 52, dy - 8)], fill=(40, 40, 40), width=5)
    d.ellipse([dx - 18, dy - 7, dx + 18, dy + 10], fill=(40, 40, 40))
    d.ellipse([dx - 60, dy - 13, dx - 42, dy - 3], fill=(90, 90, 90))
    d.ellipse([dx + 42, dy - 13, dx + 60, dy - 3], fill=(90, 90, 90))
    # small orange burst on the building roof
    bx, by = x + 46, gy - 30
    for k in range(8):
        ang = k * 3.14159 / 4
        ex = bx + int(13 * math.cos(ang))
        ey = by + int(13 * math.sin(ang))
        d.line([(bx, by), (ex, ey)], fill=(255, 140, 0), width=3)
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(255, 200, 40))
    # second low block to fill the ground line
    d.rectangle([x + w - 78, gy - 12, x + w - 18, gy], fill=(150, 150, 148))


def illo_hormuz(d, x, y, w, h):
    _sky(d, x, y, w, h * 3 // 5, (150, 205, 238), (255, 236, 190))
    _sun(d, x + 52, y + 26, 18)
    _cloud(d, x + w - 120, y + 14, 11)
    sy = y + h * 3 // 5
    d.rectangle([x, sy, x + w, y + h], fill=(28, 110, 180))
    d.rectangle([x, sy, x + w, sy + 5], fill=(120, 200, 240))
    for i in range(5):
        wx = x + 20 + i * 62
        d.arc([wx, sy + 12, wx + 44, sy + 26], 0, 180, fill=(190, 230, 250),
              width=3)
    # big red tanker
    tx, ty = x + 28, sy - 34
    d.rectangle([tx, ty, tx + 210, ty + 34], fill=(178, 34, 34))
    d.rectangle([tx, ty - 16, tx + 210, ty], fill=(120, 40, 40))
    for i, c in enumerate([(255, 200, 60), (60, 180, 90), (255, 255, 255),
                           (255, 140, 40)]):
        d.rectangle([tx + 12 + i * 50, ty - 14, tx + 52 + i * 50, ty - 2],
                    fill=c)
    d.rectangle([tx + 218, ty - 26, tx + 236, ty + 34], fill=(90, 90, 90))
    # flame + smoke on the far tanker, kept inside the frame
    fx, fy = x + w - 52, sy - 26
    d.polygon([(fx - 16, fy + 18), (fx, fy - 26), (fx + 16, fy + 18)],
              fill=(255, 140, 0))
    d.polygon([(fx - 8, fy + 18), (fx, fy - 10), (fx + 8, fy + 18)],
              fill=(255, 210, 60))
    d.ellipse([fx - 24, fy - 36, fx - 4, fy - 18], fill=(120, 120, 120))
    d.ellipse([fx - 12, fy - 38, fx + 6, fy - 22], fill=(150, 150, 150))
    # mine in the water
    mx, my = x + w - 130, sy + 26
    d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(40, 40, 40))
    for k in range(6):
        ang = k * 3.14159 / 3
        ex = mx + int(15 * math.cos(ang))
        ey = my + int(15 * math.sin(ang))
        d.line([(mx, my), (ex, ey)], fill=(40, 40, 40), width=3)


def illo_eu(d, x, y, w, h):
    _sky(d, x, y, w, h, (190, 216, 245), (240, 244, 250))
    _cloud(d, x + 16, y + 12, 10)
    _cloud(d, x + w - 130, y + 20, 9)
    # parliament building, bright navy with gold windows
    bx, by, bw, bh = x + 18, y + h - 62, w - 36, 62
    d.rectangle([bx, by, bx + bw, by + bh], fill=(30, 58, 138))
    d.rectangle([bx, by - 10, bx + bw, by], fill=(20, 40, 100))
    for i in range(9):
        wx = bx + 12 + i * (bw - 24) // 9
        d.rectangle([wx, by + 10, wx + 14, by + 26], fill=(255, 214, 90))
        d.rectangle([wx, by + 34, wx + 14, by + 50], fill=(255, 214, 90))
    # gold star circle
    cx, cy, r = x + w // 2, y + 34, 26
    for k in range(12):
        ang = -3.14159 / 2 + k * 3.14159 / 6
        sx = cx + int(r * math.cos(ang))
        sy = cy + int(r * math.sin(ang))
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 214, 90))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 214, 90))


def illo_storm(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 222, 235), (245, 240, 225))
    # bright rain cloud, light grey with white belly
    d.ellipse([x + 12, y + 8, x + 130, y + 34], fill=(120, 130, 145))
    d.ellipse([x + 60, y + 2, x + 190, y + 30], fill=(100, 112, 130))
    d.ellipse([x + 40, y + 22, x + 160, y + 40], fill=(210, 218, 228))
    # rain streaks
    for i in range(14):
        rx = x + 14 + i * 15
        d.line([(rx, y + 42), (rx - 6, y + 58)], fill=(90, 130, 180), width=2)
    # yellow lightning
    lx = x + w - 60
    d.polygon([(lx, y + 8), (lx - 14, y + 38), (lx - 2, y + 38),
               (lx - 16, y + 66), (lx + 8, y + 32), (lx - 4, y + 32)],
              fill=(255, 214, 0), outline=(200, 150, 0))
    # house + sagging wire
    gy = y + h - 18
    d.rectangle([x, gy, x + w, y + h], fill=(150, 190, 130))
    d.polygon([(x + 30, gy - 26), (x + 52, gy - 44), (x + 74, gy - 26)],
              fill=(178, 60, 40))
    d.rectangle([x + 34, gy - 26, x + 70, gy], fill=(245, 235, 210))
    d.rectangle([x + 48, gy - 14, x + 56, gy], fill=(90, 60, 40))
    d.line([(x + 90, y + 30), (x + 150, y + 52), (x + w - 8, y + 34)],
           fill=(60, 60, 60), width=3)
    d.line([(x + 150, y + 52), (x + 150, y + 66)], fill=(60, 60, 60), width=2)


def illo_mar(d, x, y, w, h):
    _sky(d, x, y, w, h, (170, 215, 240), (255, 240, 200))
    _sun(d, x + w - 36, y + 24, 16)
    _cloud(d, x + 14, y + 12, 10)
    gy = y + h - 16
    d.rectangle([x, gy, x + w, y + h], fill=(120, 185, 110))
    # white building, red roof
    d.rectangle([x + 60, gy - 40, x + 170, gy], fill=(250, 248, 240))
    d.polygon([(x + 52, gy - 40), (x + 115, gy - 54), (x + 178, gy - 40)],
              fill=(178, 60, 40))
    for i in range(5):
        d.rectangle([x + 68 + i * 20, gy - 30, x + 80 + i * 20, gy - 12],
                    fill=(60, 120, 180))
    # palms
    for px in (x + 26, x + w - 30):
        d.line([(px, gy), (px, gy - 34)], fill=(120, 90, 50), width=4)
        for k in range(5):
            ang = -3.14159 + k * 3.14159 / 4
            ex = px + int(18 * math.cos(ang))
            ey = gy - 34 + int(10 * math.sin(ang))
            d.line([(px, gy - 34), (ex, ey)], fill=(30, 140, 70), width=3)
    # two flags
    for fx, cols in ((x + 190, [(200, 30, 30), (255, 255, 255), (30, 60, 160)]),
                     (x + 214, [(255, 255, 255), (30, 60, 160), (200, 30, 30)])):
        d.line([(fx, gy - 52), (fx, gy - 14)], fill=(80, 80, 80), width=2)
        for i, c in enumerate(cols):
            d.rectangle([fx, gy - 52 + i * 8, fx + 20, gy - 44 + i * 8], fill=c)


def illo_gaza(d, x, y, w, h):
    _sky(d, x, y, w, h, (190, 220, 238), (255, 238, 200))
    _sun(d, x + 30, y + 22, 15)
    _cloud(d, x + w - 110, y + 12, 9)
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(215, 200, 160))
    # beige blocks, daylight
    for bx, bw, bh in ((x + 14, 56, 42), (x + 78, 64, 52), (x + 150, 56, 36)):
        d.rectangle([bx, gy - bh, bx + bw, gy], fill=(232, 214, 175),
                    outline=(160, 140, 110), width=2)
        for wy in range(2):
            for wx in range(3):
                d.rectangle([bx + 8 + wx * 17, gy - bh + 8 + wy * 16,
                             bx + 16 + wx * 17, gy - bh + 18 + wy * 16],
                            fill=(90, 110, 140))
    # pale smoke plume, kept inside the frame
    sx = x + 110
    d.ellipse([sx - 22, y + 12, sx + 10, y + 36], fill=(200, 200, 200))
    d.ellipse([sx - 10, y + 4, sx + 24, y + 26], fill=(220, 220, 220))
    d.ellipse([sx - 28, y + 26, sx - 2, y + 46], fill=(185, 185, 185))


def illo_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 248, 245))
    # three red virus shapes, sized to stay inside the picture
    for cx, cy, r in ((x + 52, y + 24, 13), (x + 148, y + 18, 10),
                      (x + 108, y + 48, 15)):
        for k in range(10):
            ang = k * 3.14159 / 5
            ex = cx + int((r + 6) * math.cos(ang))
            ey = cy + int((r + 6) * math.sin(ang))
            d.line([(cx, cy), (ex, ey)], fill=(200, 40, 40), width=2)
            d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(200, 40, 40))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 60, 60))
        d.ellipse([cx - r // 2, cy - r // 2, cx, cy], fill=(255, 150, 150))
    # white cross badge, bottom right
    bx, by = x + w - 26, y + h - 22
    d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=(255, 255, 255),
              outline=(30, 122, 52), width=3)
    d.rectangle([bx - 2, by - 9, bx + 2, by + 9], fill=(200, 40, 40))
    d.rectangle([bx - 9, by - 2, bx + 9, by + 2], fill=(200, 40, 40))


def illo_kyiv(d, x, y, w, h):
    # bright dusk, not night: orange horizon rising to violet
    _sky(d, x, y, w, h, (90, 70, 140), (255, 170, 90))
    _sun(d, x + w - 40, y + h - 34, 13, core=(255, 230, 150),
         ring=(255, 180, 80))
    # skyline silhouette, dark blue, with lit windows
    gy = y + h - 12
    d.rectangle([x, gy, x + w, y + h], fill=(60, 50, 90))
    for bx, bw, bh in ((x + 8, 44, 34), (x + 58, 36, 48), (x + 100, 52, 30),
                       (x + 158, 40, 44)):
        d.rectangle([bx, gy - bh, bx + bw, gy], fill=(40, 36, 70))
        for wy in range(bh // 14):
            for wx in range(bw // 14):
                if (wx + wy) % 2 == 0:
                    d.rectangle([bx + 5 + wx * 14, gy - bh + 6 + wy * 14,
                                 bx + 10 + wx * 14, gy - bh + 11 + wy * 14],
                                fill=(255, 214, 90))
    # bright drone trails
    for tx, ty, ln in ((x + 30, y + 14, 70), (x + 120, y + 26, 84),
                       (x + 180, y + 10, 60)):
        d.line([(tx, ty), (tx + ln, ty + 18)], fill=(255, 214, 0), width=3)
        d.ellipse([tx + ln - 4, ty + 14, tx + ln + 4, ty + 22],
                  fill=(255, 240, 150))
    # orange blast, kept inside the frame
    bx, by = x + 130, gy - 38
    for k in range(8):
        ang = k * 3.14159 / 4
        ex = bx + int(12 * math.cos(ang))
        ey = by + int(12 * math.sin(ang))
        d.line([(bx, by), (ex, ey)], fill=(255, 120, 0), width=3)
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(255, 210, 60))


def illo_nz(d, x, y, w, h):
    _sky(d, x, y, w, h, (175, 218, 242), (250, 244, 220))
    _sun(d, x + 32, y + 22, 15)
    _cloud(d, x + w - 120, y + 12, 10)
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(110, 180, 110))
    # beehive: stacked light-grey tiers, inside the frame
    cx = x + w // 2
    for i, tw in enumerate((110, 92, 74, 56)):
        ty = gy - 12 - i * 10
        d.rectangle([cx - tw // 2, ty, cx + tw // 2, ty + 10],
                    fill=(225, 225, 220), outline=(150, 150, 145), width=1)
    d.rectangle([cx - 16, gy - 54, cx + 16, gy - 44], fill=(200, 200, 195))
    # flag
    d.line([(cx + 66, gy - 44), (cx + 66, gy - 6)], fill=(80, 80, 80), width=2)
    d.rectangle([cx + 66, gy - 44, cx + 96, gy - 30], fill=(30, 60, 160))
    d.line([(cx + 66, gy - 44), (cx + 96, gy - 30)], fill=(255, 255, 255),
           width=2)
    d.line([(cx + 96, gy - 44), (cx + 66, gy - 30)], fill=(255, 255, 255),
           width=2)


def illo_london(d, x, y, w, h):
    _sky(d, x, y, w, h, (180, 220, 242), (255, 240, 205))
    _sun(d, x + w - 34, y + 22, 15)
    _cloud(d, x + 12, y + 10, 10)
    _cloud(d, x + 120, y + 26, 8)
    gy = y + h - 12
    d.rectangle([x, gy, x + w, y + h], fill=(140, 170, 120))
    # Big Ben tower, scaled to the small frame
    tx = x + w // 2 - 16
    d.rectangle([tx, gy - 34, tx + 32, gy], fill=(190, 165, 110))
    d.rectangle([tx - 3, gy - 38, tx + 35, gy - 34], fill=(150, 125, 80))
    d.polygon([(tx + 4, gy - 38), (tx + 16, gy - 48), (tx + 28, gy - 38)],
              fill=(60, 90, 60))
    d.ellipse([tx + 6, gy - 30, tx + 26, gy - 12], fill=(255, 250, 230),
              outline=(90, 70, 40), width=2)
    d.line([(tx + 16, gy - 21), (tx + 16, gy - 27)], fill=(40, 40, 40),
           width=2)
    d.line([(tx + 16, gy - 21), (tx + 22, gy - 19)], fill=(40, 40, 40),
           width=2)
    # houses
    for hx in (x + 12, x + w - 52):
        d.rectangle([hx, gy - 16, hx + 40, gy], fill=(220, 200, 170))
        d.polygon([(hx - 3, gy - 16), (hx + 20, gy - 26), (hx + 43, gy - 16)],
                  fill=(178, 60, 40))


def illo_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 242, 250))
    _cloud(d, x + 12, y + 10, 9)
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(190, 205, 215))
    # bank building, scaled to the small frame
    d.rectangle([x + 16, gy - 30, x + 96, gy], fill=(245, 245, 240),
                outline=(120, 120, 120), width=2)
    d.polygon([(x + 12, gy - 30), (x + 56, gy - 42), (x + 100, gy - 30)],
              fill=(30, 58, 138))
    for i in range(3):
        d.rectangle([x + 26 + i * 24, gy - 24, x + 38 + i * 24, gy - 6],
                    fill=(60, 120, 180))
    # rising green chart, kept inside the frame
    pts = [(x + 112, gy - 6), (x + 140, gy - 18), (x + 168, gy - 14),
           (x + 196, gy - 30), (x + 218, gy - 40)]
    d.line(pts, fill=(22, 101, 52), width=4)
    d.polygon([(x + 206, gy - 44), (x + 222, gy - 40), (x + 212, gy - 28)],
              fill=(22, 101, 52))
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(22, 101, 52))


def illo_chess(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 230, 205))
    # board, scaled to fill the small frame: 8 columns, 6 rows
    sq = 10
    bx, by = x + (w - sq * 8) // 2, y + 4
    for r in range(6):
        for c in range(8):
            fill = (240, 217, 181) if (r + c) % 2 == 0 else (181, 136, 99)
            d.rectangle([bx + c * sq, by + r * sq, bx + (c + 1) * sq,
                         by + (r + 1) * sq], fill=fill)
    d.rectangle([bx, by, bx + 8 * sq, by + 6 * sq], outline=(90, 60, 30),
                width=2)
    # pieces: white king, black queen, sized to the squares
    pr = 4
    kx, ky = bx + sq, by + sq
    d.ellipse([kx - pr, ky - pr, kx + pr, ky + pr], fill=(255, 255, 255),
              outline=(60, 60, 60), width=1)
    kf = font(SANS_B, 9)
    d.text((kx - 3, ky - 6), "K", font=kf, fill=(40, 40, 40))
    qx, qy = bx + 5 * sq, by + 3 * sq
    d.ellipse([qx - pr, qy - pr, qx + pr, qy + pr], fill=(40, 40, 40))
    d.text((qx - 3, qy - 6), "Q", font=kf, fill=(255, 255, 255))
    # score badge
    d.rounded_rectangle([x + w - 62, y + h - 24, x + w - 6, y + h - 6],
                        radius=4, fill=(11, 31, 75))
    d.text((x + w - 54, y + h - 23), "1.5-1.5", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def illo_refinery(d, x, y, w, h):
    _sky(d, x, y, w, h, (175, 216, 240), (255, 236, 190))
    _sun(d, x + 30, y + 22, 15)
    _cloud(d, x + w - 110, y + 12, 9)
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(205, 190, 160))
    # towers and tanks, scaled to the small frame
    for tx, tw, th in ((x + 14, 26, 28), (x + 46, 20, 36), (x + 72, 30, 24)):
        d.rectangle([tx, gy - th, tx + tw, gy], fill=(180, 180, 175),
                    outline=(110, 110, 110), width=1)
        d.rectangle([tx + 4, gy - th - 6, tx + tw - 4, gy - th],
                    fill=(140, 140, 135))
    d.ellipse([x + 120, gy - 22, x + 170, gy], fill=(220, 220, 215),
              outline=(110, 110, 110), width=1)
    d.rectangle([x + 120, gy - 22, x + 170, gy - 10], fill=(220, 220, 215))
    # flame, kept inside the frame
    fx, fy = x + 56, gy - 30
    d.polygon([(fx - 12, fy + 12), (fx, fy - 14), (fx + 12, fy + 12)],
              fill=(255, 140, 0))
    d.polygon([(fx - 6, fy + 12), (fx, fy - 4), (fx + 6, fy + 12)],
              fill=(255, 210, 60))

ILLOS = {1: illo_kuwait, 2: illo_hormuz, 3: illo_eu, 4: illo_storm,
         5: illo_mar, 6: illo_gaza, 7: illo_ebola, 8: illo_kyiv,
         9: illo_nz, 10: illo_london, 11: illo_seoul, 12: illo_chess,
         13: illo_refinery}


# ------------------------------------------------------- dotted world map
# Rough continent outlines in (lon, lat); dots are sampled inside them.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60),
     (-160, 58)],
    [(-55, 60), (-40, 65), (-30, 70), (-20, 76), (-35, 80), (-55, 76)],
    [(-78, 8), (-60, 10), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -52), (-73, -40), (-72, -20),
     (-77, -12), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -30), (12, -18), (9, -1), (9, 4), (-8, 5), (-15, 11)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (40, 68), (55, 68), (70, 72),
     (90, 75), (110, 74), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (135, 35),
     (130, 33), (127, 35), (122, 30), (120, 25), (110, 20), (105, 10),
     (100, 8), (97, 15), (90, 22), (88, 22), (80, 15), (77, 8), (75, 12),
     (70, 20), (66, 25), (60, 25), (57, 26), (52, 26), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (30, 36), (26, 38), (22, 37), (18, 40),
     (12, 44), (8, 44), (3, 43), (-1, 38), (-9, 37)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (100, -5), (95, 0)],
    [(109, 1), (116, 4), (119, -2), (114, -4), (109, -2)],
    [(105, -7), (114, -8), (114, -7), (105, -6)],
    [(131, -1), (138, -3), (146, -6), (150, -9), (141, -8), (132, -4)],
    [(120, 18), (122, 14), (121, 10), (120, 14)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (136, -35), (140, -38), (146, -39),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (174, -41), (170, -44)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 40),
     (142, 43), (144, 44), (142, 41), (139, 38), (136, 35), (132, 32)],
    [(43, -12), (47, -15), (50, -17), (48, -22), (45, -25), (43, -20)],
]


def _inside(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def draw_map(d, x0, y0, w, h):
    """Dotted world map with numbered leader-line pins."""
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=(150, 145, 135), width=1)
    sx = w / 360.0
    sy = h / 132.0
    s = min(sx, sy)
    ox = x0 + (w - 360 * s) / 2
    oy = y0 + (h - 132 * s) / 2
    step = 2.4
    lon = -168.0
    while lon <= 192:
        lat = 76.0
        while lat >= -56:
            if any(_inside(lon, lat, poly) for poly in CONTINENTS):
                px = ox + (lon + 168) * s
                py = oy + (76 - lat) * s
                d.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4],
                          fill=(140, 135, 125))
            lat -= step
        lon += step
    for num, lo, la, ndx, ndy in PINS:
        tx = ox + (lo + 168) * s
        ty = oy + (76 - la) * s
        px, py = tx + ndx, ty + ndy
        d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(40, 40, 40))
        d.line([(tx, ty), (px, py)], fill=(120, 120, 120), width=1)
        col = REGION[PIN_REGION[num]]
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=col,
                  outline=(255, 255, 255), width=2)
        fnt = font(SANS_B, 11 if num < 10 else 9)
        tw = text_w(d, str(num), fnt)
        d.text((px - tw / 2, py - 7 if num < 10 else py - 6), str(num),
               font=fnt, fill=(255, 255, 255))


# ------------------------------------------------------- story cards
def draw_card(d, x, y, w, h, story, hero=False):
    num, region, kicker, headline, body, why, tag, source = story
    col = REGION[region]
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=(180, 175, 165), width=1)
    d.rectangle([x, y, x + w, y + 3], fill=col)
    illo_h = 112 if hero else (70 if h > 180 else 60)
    ILLOS[num](d, x + 1, y + 4, w - 2, illo_h)
    # number badge over the picture
    bx, by = x + 12, y + 12
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=RED,
              outline=(255, 255, 255), width=2)
    nf = font(SANS_B, 12 if num < 10 else 10)
    tw = text_w(d, str(num), nf)
    d.text((bx - tw / 2, by - 8 if num < 10 else by - 7), str(num), font=nf,
           fill=(255, 255, 255))
    ty = y + 4 + illo_h + 6
    kf = font(SANS_B, 9 if hero else 8)
    d.text((x + 8, ty), kicker, font=kf, fill=col)
    ty += 13 if hero else 12
    hf = font(SANS_B, 17 if hero else 13)
    hl = wrap(d, headline, hf, w - 16)
    if len(hl) > 2:
        hf = font(SANS_B, 15 if hero else 12)
        hl = wrap(d, headline, hf, w - 16)
    ty = draw_lines(d, x + 8, ty, hl[:2], hf, INK, 19 if hero else 15)
    ty += 2
    bf = font(SANS, 11 if hero else 10)
    bl = wrap(d, body, bf, w - 16)
    ty = draw_lines(d, x + 8, ty, bl[:2], bf, (50, 50, 50), 12)
    if hero and why:
        wf = shrink_to_fit(d, "WHY IT MATTERS \u2014 " + why, SANS_B, 10,
                           w - 16)
        d.text((x + 8, ty + 2), "WHY IT MATTERS \u2014 ", font=wf, fill=RED)
        pre = text_w(d, "WHY IT MATTERS \u2014 ", wf)
        rest = why
        while rest and text_w(d, rest, wf) > w - 16 - pre:
            rest = rest[:-1]
        if rest != why:
            rest = rest[:-3].rstrip() + "\u2026" if len(rest) > 3 else rest
        d.text((x + 8 + pre, ty + 2), rest, font=wf, fill=(60, 60, 60))
        ty += 14
    # tag + source, pinned to the card bottom
    tf = font(SANS_B, 8)
    tag_w = text_w(d, tag, tf) + 10
    tag_y = y + h - 15
    d.rectangle([x + 8, tag_y, x + 8 + tag_w, tag_y + 11],
                fill=TAG_FILL[tag])
    d.text((x + 13, tag_y + 1), tag, font=tf, fill=(255, 255, 255))
    sf = font(SANS, 8)
    d.text((x + 8 + tag_w + 6, tag_y + 1), source, font=sf, fill=GREY)


# ------------------------------------------------------- page build
def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((10, 4), "THE WORLD IN ONE DAY", font=font(SANS_B, 12),
           fill=(255, 255, 255))
    right = "52 STORIES  \u00b7  10 REGIONS  \u00b7  FRIDAY 27 NOVEMBER 2026"
    rf = font(SANS_B, 11)
    d.text((W - 10 - text_w(d, right, rf), 5), right, font=rf,
           fill=(255, 214, 90))
    # masthead: one colour, one line, measured and centred
    title = "Friday 27 November 2026"
    tf = shrink_to_fit(d, title, SERIF_B, 60, W - 40)
    tw = text_w(d, title, tf)
    d.text(((W - tw) / 2, 24), title, font=tf, fill=NAVY)
    # red kicker on its own band, clear of the masthead
    kick = ("Storm cuts power to nearly a million Americans  \u00b7  Drone "
            "attack kills two Italians in Kuwait  \u00b7  EU summit ends "
            "with no budget deal")
    kf = shrink_to_fit(d, kick, SANS_B, 14, W - 30)
    kw = text_w(d, kick, kf)
    d.text(((W - kw) / 2, 88), kick, font=kf, fill=RED)
    d.line([(8, 104), (W - 8, 104)], fill=NAVY, width=2)
    # stats strip
    y0, y1 = 108, 150
    bw = (W - 16) / 6
    for i, (val, lab) in enumerate(STATS):
        x = 8 + i * bw
        d.rectangle([x + 1, y0, x + bw - 1, y1], outline=(150, 145, 135),
                    width=1)
        vf = shrink_to_fit(d, val, SANS_B, 24, bw - 14)
        vw = text_w(d, val, vf)
        d.text((x + (bw - vw) / 2, y0 + 2), val, font=vf, fill=NAVY)
        lf = font(SANS, 9)
        ll = wrap(d, lab, lf, bw - 12)
        draw_lines(d, x + 6, y0 + 27, ll[:2], lf, (60, 60, 60), 10,
                   align="center", width=bw - 12)
    # region bar
    ry = 154
    total = sum(n for _, n, _ in REGION_BAR)
    x = 8
    for name, n, col in REGION_BAR:
        seg = (W - 16) * n / total
        d.rectangle([x, ry, x + seg, ry + 14], fill=col)
        if seg >= 56:
            lf = font(SANS_B, 8)
            lab = "%s %d" % (name, n)
            d.text((x + (seg - text_w(d, lab, lf)) / 2, ry + 3), lab,
                   font=lf, fill=(255, 255, 255))
        elif seg >= 30:
            lf = font(SANS_B, 8)
            lab = str(n)
            d.text((x + (seg - text_w(d, lab, lf)) / 2, ry + 3), lab,
                   font=lf, fill=(255, 255, 255))
        x += seg
    # timeline
    ty = 172
    d.rectangle([8, ty, 116, ty + 34], fill=NAVY)
    d.text((14, ty + 4), "THE DAY", font=font(SANS_B, 12),
           fill=(255, 255, 255))
    d.text((14, ty + 18), "IN UTC", font=font(SANS_B, 12),
           fill=(255, 214, 90))
    line_y = ty + 17
    d.line([(124, line_y), (W - 10, line_y)], fill=(90, 90, 86), width=2)
    span = (W - 10 - 124)
    for i, (t, lab) in enumerate(TIMELINE):
        ex = 124 + span * (i + 0.5) / len(TIMELINE)
        d.ellipse([ex - 3, line_y - 3, ex + 3, line_y + 3], fill=RED)
        tf2 = font(SANS_B, 10)
        d.text((ex - text_w(d, t, tf2) / 2, ty - 1), t, font=tf2, fill=RED)
        lf = font(SANS, 8)
        ll = wrap(d, lab, lf, 118)
        draw_lines(d, ex - 59, line_y + 5, ll[:2], lf, (50, 50, 50), 9,
                   align="center", width=118)
    # hero row: three tall, bright pictures
    hy = 210
    hw = (W - 16 - 18) / 3
    for i, story in enumerate(HEROES):
        draw_card(d, 8 + i * (hw + 9), hy, hw, 228, story, hero=True)
    # rows 2 and 3: five cards each
    cw = (W - 16 - 36) / 5
    for i, story in enumerate(CARDS[:5]):
        draw_card(d, 8 + i * (cw + 9), 442, cw, 178, story)
    for i, story in enumerate(CARDS[5:]):
        draw_card(d, 8 + i * (cw + 9), 624, cw, 164, story)
    # bottom headers
    d.text((8, 792), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=INK)
    d.text((330, 792), "ALSO ON 27 NOVEMBER:  39 MORE STORIES",
           font=font(SANS_B, 12), fill=INK)
    d.text((8, 806), "pins = picture numbers, coloured by region; leader "
           "lines spread the crowded Europe and Gulf pins",
           font=font(SANS, 8), fill=GREY)
    d.line([(8, 788), (W - 8, 788)], fill=NAVY, width=1)
    # map, left
    draw_map(d, 8, 820, 314, 172)
    # more-stories list, right, two columns
    lf = font(SANS_B, 8)
    bf = font(SANS, 8)
    col_w = (W - 330 - 8) / 2
    for j, (num, city, text) in enumerate(MORE):
        col = j // 20
        row = j % 20
        lx = 330 + col * col_w
        ly = 820 + row * 8.6
        d.text((lx, ly), "%d" % num, font=lf, fill=NAVY)
        cx = lx + 20
        line = "%s: %s" % (city, text)
        while text_w(d, line, bf) > col_w - 24 and len(line) > 10:
            line = line[:-1]
        d.text((cx, ly), line, font=bf, fill=INK)
    # footer
    d.line([(8, 993), (W - 8, 993)], fill=NAVY, width=2)
    ff = font(SANS, 8)
    d.text((8, 996), "DATE CHECK", font=font(SANS_B, 8), fill=RED)
    d.text((74, 996),
           "Every story was first reported on Friday 27 November 2026; "
           "older context flagged: NZ election 7 Nov, UK migration year "
           "to Jun 2026, Ebola totals cumulative.",
           font=ff, fill=INK)
    d.text((8, 1005), "HOW SURE", font=font(SANS_B, 8), fill=RED)
    d.text((74, 1005),
           "OFFICIAL = said by a government, court or agency  \u00b7  "
           "CONFIRMED = carried by two or more outlets  \u00b7  CLAIM = "
           "one side's account, not verified",
           font=ff, fill=INK)
    d.text((8, 1013),
           "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 Dawn "
           "\u00b7 Kyiv Post \u00b7 NPR \u00b7 ONS \u00b7 Bank of Korea "
           "\u00b7 NZ Electoral Commission \u00b7 Ukraine Air Force "
           "\u00b7 Saudi Energy Ministry \u00b7 PowerOutage.us. Pictures "
           "and map drawn in code.",
           font=ff, fill=GREY)
    page = "PAGE 1 \u00b7 WORLD NEWS \u00b7 PRINTED 27 NOV 2026 \u00b7 52 STORIES"
    pf = font(SANS_B, 8)
    d.text((W - 8 - text_w(d, page, pf), 1005), page, font=pf, fill=INK)
    img.save(out_path, "JPEG", quality=88, optimize=True)
    return out_path


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.jpg")
    build(path)
    data = open(path, "rb").read()
    print("wrote", path, len(data), "bytes",
          "sha256", hashlib.sha256(data).hexdigest())
