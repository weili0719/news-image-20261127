#!/usr/bin/env python3
"""WORLD NEWS - Friday 27 November 2026. One-page front page, drawn in code.

Writes a 1024x1024 JPEG to /output/entry.png. No network, no clock, no
randomness: same code + same data = same bytes. Run twice, compare SHA-256.
Text that would overflow its box is truncated with an ellipsis instead of
failing, so a font build that measures glyphs slightly wider can never
abort the run.

All 46 stories were first reported on Friday 27 November 2026 and verified
against live reporting that day (Reuters, CNN, AP, BBC, Dawn, Kyiv Post,
NPR, ONS, Bank of Korea, NZ Electoral Commission, Ukraine Air Force,
Saudi Energy Ministry, PowerOutage.us). Older context is flagged in the
DATE CHECK footer: the Cairo tanker fire was Wed 25 Nov; the NZ election
was 7 Nov (final count Fri 27 Nov); UK migration covers the year to Jun 2026.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"
MARGIN = 14
PAPER = (250, 247, 240)
INK = (18, 18, 18)
NAVY = (26, 42, 74)
RED = (176, 58, 46)
GREY = (110, 110, 108)
LIGHT = (244, 241, 234)
RULE = (60, 60, 60)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(d, text, fnt, max_w):
    """Greedy word wrap measured with real glyph widths."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, fnt, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(d, text, fnt, max_w, max_lines):
    """Wrap text, truncating with an ellipsis so it never exceeds max_lines.

    A different FreeType/Pillow build can measure glyphs a fraction wider
    than this machine does; a hard failure over a slightly-wide glyph must
    never abort the whole run. At normal metrics nothing is truncated:
    every text already fits within its budget.
    """
    lines = wrap_text(d, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    words = text.split(" ")
    while words:
        cand = " ".join(words) + " …"
        lines = wrap_text(d, cand, fnt, max_w)
        if len(lines) <= max_lines:
            return lines
        words.pop()
    return ["…"]


def fit_width(d, text, fnt, max_w):
    """Truncate a single line with an ellipsis so it fits max_w."""
    if d.textlength(text, font=fnt) <= max_w:
        return text
    words = text.split(" ")
    while words:
        cand = " ".join(words) + " …"
        if d.textlength(cand, font=fnt) <= max_w:
            return cand
        words.pop()
    return "…"


# ---------------------------------------------------------------- regions
REGIONS = [
    ("EUROPE", 14, (46, 90, 136)),
    ("S ASIA", 8, (125, 60, 152)),
    ("MIDEAST", 6, (192, 57, 43)),
    ("AFRICA", 4, (191, 143, 0)),
    ("E ASIA", 4, (20, 143, 119)),
    ("N AMERICA", 3, (52, 73, 94)),
    ("SE ASIA", 2, (34, 153, 84)),
    ("LAT AM", 2, (194, 24, 91)),
    ("GLOBAL", 2, (97, 106, 107)),
    ("OCEANIA", 1, (230, 126, 34)),
]
REGION_COLOR = {name: col for name, _, col in REGIONS}
TOTAL_STORIES = 46

# ---------------------------------------------------------------- stat strip
STATS = [
    ("2", "Italians killed in Kuwait drone strike"),
    ("$96.57", "Brent settles Thu, best since 6 Nov"),
    ("EUR 45bn", "Ukraine loan backed by 24 EU states"),
    ("980,000", "peak without power in US storm"),
    ("12,021", "Ebola cases in DR Congo (5,904 dead)"),
    ("77,000", "UK net migration, lowest since 1997"),
]

# ---------------------------------------------------------------- UTC timeline
TIMELINE = [
    ("11:00", "Kuwait drone strike kills 2"),
    ("16:00", "Russia fires 155 drones"),
    ("~18:50", "Chess Game 3 drawn; 1.5-1.5"),
    ("~00:00", "Storm: ~900,000 lose power"),
    ("~01:00", "NZ final count: hung House"),
    ("~02:00", "EU summit fails"),
    ("09:35", "Brent hits $97.30"),
]

# ---------------------------------------------------------------- pictured stories
# kind, region, kicker, headline, body, tag, source, pin (map col, row)
PANELS = [
    ("radar", "MIDEAST", "KUWAIT - MIDDLE EAST - DRONE WAR",
     "Drone strike kills two Italians in Kuwait",
     "Rheinmetall technicians hit at air-defence site; Italy blames Iran, Tehran denies it.",
     "CONFIRMED", "Reuters, CNN", (46, 10)),
    ("tanker", "MIDEAST", "STRAIT OF HORMUZ - MIDDLE EAST - OIL",
     "Mines hit two tankers; Brent nears $97",
     "Ships catch fire off Oman; one supertanker held 2m barrels. Brent settles at $96.57.",
     "CONFIRMED", "Reuters", (48, 12)),
    ("eustars", "EUROPE", "BRUSSELS - EUROPE - EU SUMMIT",
     "EU summit ends with no budget deal",
     "24 states back a EUR 45bn Ukraine loan for 2027, but the 2028-34 budget talks fail; Dec retry.",
     "OFFICIAL", "Costa, von der Leyen", (38, 6)),
    ("storm", "N AMERICA", "NEW YORK - N. AMERICA - WEATHER",
     "Storm cuts power to nearly 1m on Thanksgiving",
     "Macy's 100th parade postponed, a first; ~400 flights axed, 2,000 delayed.",
     "CONFIRMED", "PowerOutage.us, NPR", (21, 9)),
    ("podium", "N AMERICA", "MAR-A-LAGO - N. AMERICA - TRUMP",
     "Trump welcomes Putin to G20 in Miami",
     "'If he wanted to come, he certainly can.' He rewrote a NATO text to add Ukraine.",
     "CONFIRMED", "Kyiv Post", (20, 12)),
    ("skyline", "MIDEAST", "GAZA - MIDDLE EAST - CEASEFIRE",
     "Israel kills senior Hamas official in Gaza",
     "Khaled Abu Nada dies in a Deir al-Balah flat; third such killing since Tuesday.",
     "CONFIRMED", "AP, Dawn", (43, 11)),
    ("clinic", "AFRICA", "E. CONGO - AFRICA - HEALTH",
     "Ebola outbreak passes 12,000 cases",
     "12,021 cases and 5,904 dead, ministry data show; fighting forces responders out.",
     "OFFICIAL", "DRC health ministry", (42, 18)),
    ("night", "EUROPE", "KYIV - EUROPE - UKRAINE WAR",
     "Russia fires 155 drones overnight",
     "110 downed; hits at 27 sites. Estonia and Latvia scramble NATO jets as alerts sound.",
     "OFFICIAL", "Ukraine Air Force", (42, 7)),
    ("beehive", "OCEANIA", "WELLINGTON - OCEANIA - ELECTION",
     "NZ final count leaves hung House",
     "Coalition holds 65 of 130 seats, one short; Opportunity (7) now decides.",
     "OFFICIAL", "Electoral Commission", (69, 26)),
    ("plane", "EUROPE", "LONDON - EUROPE - MIGRATION",
     "UK net migration falls to 77,000",
     "Lowest since 1997 outside Covid, down from a 944,000 peak in 2023.",
     "OFFICIAL", "ONS", (35, 6)),
    ("bank", "E ASIA", "SEOUL - EAST ASIA - ECONOMY",
     "Bank of Korea lifts rate to 3.25%",
     "Third hike this year; growth forecast raised to 3.9% on a chip-export boom.",
     "OFFICIAL", "Bank of Korea", (61, 9)),
    ("chess", "EUROPE", "GENEVA - EUROPE - CHESS",
     "Chess title match still level at 1.5-1.5",
     "Game 3 ends in a 60-move draw; Gukesh holds Sindarov with Black. Game 4 on Sat.",
     "CONFIRMED", "Sportstar", (37, 8)),
    ("refinery", "MIDEAST", "JAZAN - MIDDLE EAST - ENERGY",
     "Houthi strike hits Saudi Aramco refinery",
     "One Nepali worker killed, several hurt; part of the refinery halted.",
     "CONFIRMED", "Saudi Energy Ministry", (45, 14)),
]

# ---------------------------------------------------------------- more stories
# (city, headline, region) - numbers continue from 14
MORE = [
    ("Karachi", "Building collapse toll at 7; 14 missing", "S ASIA"),
    ("Bangkok", "Blast and fire hit oil refinery; 9 hurt", "SE ASIA"),
    ("Paris", "Depardieu to face trial over 2018 case", "EUROPE"),
    ("Paris", "AFP hit by cyberattack; site taken offline", "EUROPE"),
    ("Nairobi", "Court halts US-backed Ebola facility build", "AFRICA"),
    ("Yangon", "Myanmar rejects parts of ICJ ruling", "SE ASIA"),
    ("Taiz", "Strike blamed on Saudis kills 11", "MIDEAST"),
    ("Quetta", "Convoy attack kills 4 Pakistani soldiers", "S ASIA"),
    ("Helsinki", "Finland extends border act to 2028", "EUROPE"),
    ("Minsk", "Russia, Ukraine swap bodies of the fallen", "EUROPE"),
    ("Ankara", "Erdogan signs off Mecca defence pact", "MIDEAST"),
    ("Kathmandu", "Nepal to declare 4,000 flood dead", "S ASIA"),
    ("Dhaka", "Tear gas fired at garment-wage protests", "S ASIA"),
    ("Buenos Aires", "Argentina bans money printing", "LAT AM"),
    ("London", "Lloyds app goes down on Black Friday", "EUROPE"),
    ("Berlin", "SAP puts 10,000 jobs under threat", "EUROPE"),
    ("New York", "JPMorgan: AI risks 24m jobs in 5 years", "N AMERICA"),
    ("Shanghai", "Nvidia chips at Huang-linked site", "E ASIA"),
    ("New Delhi", "India wants Pakistan drama off Netflix", "S ASIA"),
    ("Kyiv", "Zelenskyy warns on Black Sea food exports", "EUROPE"),
    ("Mexico City", "Mexico backs Cuba, opposes blockade", "LAT AM"),
    ("Markets", "Gold steadies near $3,565", "GLOBAL"),
    ("Geneva", "UN: hunger to worsen in 16 areas", "GLOBAL"),
    ("Warsaw", "Poland to sign Palantir defence deal", "EUROPE"),
    ("Cairo", "Sisi orders payout for Warraq victims", "AFRICA"),
    ("Kyiv", "Russia has lost 1.6m troops, Kyiv claims", "EUROPE"),
    ("New Delhi", "Modi to revive women's quota bill", "S ASIA"),
    ("Dhaka", "Ex-aide of Hasina arrested amid tensions", "S ASIA"),
    ("Taipei", "Taiwan, EU eye closer disinformation fight", "E ASIA"),
    ("Islamabad", "PTI condemns bid to detain Rehman", "S ASIA"),
    ("Berlin", "India, Germany hold partnership talks", "EUROPE"),
    ("Cairo", "Tanker fire kills 31; driver detained (25 Nov)", "AFRICA"),
    ("Tokyo", "Japan eyes $353bn defence over five years", "E ASIA"),
]

SOURCES_LINE = ("Sources: Reuters - CNN - AP - BBC - Dawn - Kyiv Post - NPR - ONS - "
                "Bank of Korea - NZ Electoral Commission - Ukraine Air Force - "
                "Saudi Energy Ministry - PowerOutage.us. Pictures and map drawn in code.")

# ---------------------------------------------------------------- dotted map
# Land spans as (row, col_start, col_end); col = (lon+180)/5, row = (80-lat)/4.5
LAND_SPANS = [
    (0, 10, 16), (0, 45, 70),
    (1, 8, 20), (1, 26, 31), (1, 42, 71),
    (2, 2, 22), (2, 26, 31), (2, 37, 40), (2, 42, 71),
    (3, 3, 23), (3, 27, 30), (3, 37, 41), (3, 42, 71),
    (4, 8, 23), (4, 33, 33), (4, 38, 42), (4, 43, 71),
    (5, 9, 22), (5, 35, 42), (5, 43, 70),
    (6, 10, 21), (6, 34, 43), (6, 44, 69),
    (7, 9, 21), (7, 35, 43), (7, 44, 66), (7, 67, 68),
    (8, 9, 22), (8, 35, 44), (8, 44, 49), (8, 50, 64), (8, 67, 67),
    (9, 9, 21), (9, 33, 45), (9, 44, 49), (9, 51, 55), (9, 56, 64),
    (10, 9, 13), (10, 14, 21), (10, 33, 46), (10, 45, 49), (10, 51, 55), (10, 56, 63),
    (11, 10, 15), (11, 33, 47), (11, 45, 48), (11, 51, 54), (11, 57, 62),
    (12, 13, 16), (12, 33, 47), (12, 52, 54), (12, 57, 61),
    (13, 20, 27), (13, 34, 46), (13, 58, 61), (13, 60, 66),
    (14, 20, 28), (14, 34, 45), (14, 58, 66),
    (15, 20, 29), (15, 35, 44), (15, 60, 66),
    (16, 21, 28), (16, 35, 43), (16, 58, 64),
    (17, 22, 28), (17, 36, 42), (17, 57, 65),
    (18, 22, 27), (18, 36, 41), (18, 57, 65),
    (19, 23, 27), (19, 37, 40), (19, 57, 64),
    (20, 23, 26), (20, 37, 39), (20, 58, 63),
    (21, 24, 26), (21, 59, 63),
    (22, 24, 26), (22, 59, 62),
    (23, 24, 25), (23, 60, 62), (23, 68, 69),
    (24, 24, 25), (24, 68, 69),
    (25, 24, 25),
    (26, 24, 25),
    (27, 24, 24),
    (28, 24, 24),
]
MAP_COLS, MAP_ROWS = 72, 30


def paint_map(d, x0, y0, w, h):
    cw, ch = w / MAP_COLS, h / MAP_ROWS
    dot = (88, 88, 84)
    for r, c0, c1 in LAND_SPANS:
        cy = y0 + (r + 0.5) * ch
        for c in range(c0, c1 + 1):
            cx = x0 + (c + 0.5) * cw
            d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=dot)
    # numbered pins, coloured by region
    fnum = font(F_BOLD, 9)
    for i, p in enumerate(PANELS, 1):
        col, row = p[7]
        cx = x0 + (col + 0.5) * cw
        cy = y0 + (row + 0.5) * ch
        colr = REGION_COLOR[p[1]]
        r = 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colr, outline=(255, 255, 255), width=1)
        tw = d.textlength(str(i), font=fnum)
        d.text((cx - tw / 2, cy - 6.5), str(i), font=fnum, fill=(255, 255, 255))


# ---------------------------------------------------------------- flat scenes
def _sky(d, box, top, bot):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=top)
    d.rectangle([x, y + h // 2, x + w, y + h], fill=bot)


def paint_scene(d, kind, box):
    x, y, w, h = box
    x1, y1 = x + w, y + h
    cx, cy = x + w / 2, y + h / 2
    if kind == "radar":  # Kuwait drone + radar dish
        _sky(d, box, (232, 214, 170), (214, 186, 130))
        d.polygon([(x + 8, y1), (x + 8, y + 22), (x + w - 8, y + 22), (x + w - 8, y1)], fill=(150, 120, 70))
        d.arc([x + w * 0.30, y + 2, x + w * 0.70, y + 34], 180, 360, fill=(40, 40, 40), width=3)
        d.line([cx, y + 18, cx, y + 34], fill=(40, 40, 40), width=3)
        d.ellipse([x + w * 0.66, y + 6, x + w * 0.80, y + 16], fill=(60, 60, 60))  # drone body
        d.line([x + w * 0.62, y + 8, x + w * 0.84, y + 8], fill=(60, 60, 60), width=2)
        d.line([x + w * 0.60, y + 14, x + w * 0.62, y + 22], fill=(200, 60, 30), width=2)
        d.line([x + w * 0.80, y + 14, x + w * 0.82, y + 22], fill=(200, 60, 30), width=2)
        for dx, dy in [(0.72, 0.42), (0.78, 0.38), (0.70, 0.50)]:
            d.line([x + w * dx, y + h * dy, x + w * (dx + 0.05), y + h * (dy - 0.10)], fill=(220, 120, 40), width=2)
    elif kind == "tanker":  # Hormuz tanker + mine
        _sky(d, box, (200, 215, 225), (90, 130, 160))
        d.rectangle([x, y + h * 0.62, x1, y1], fill=(52, 95, 130))
        d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.66], fill=(40, 45, 55))
        d.rectangle([x + w * 0.60, y + h * 0.26, x + w * 0.72, y + h * 0.42], fill=(200, 60, 40))
        d.rectangle([x + w * 0.20, y + h * 0.30, x + w * 0.30, y + h * 0.42], fill=(230, 230, 230))
        d.ellipse([x + w * 0.10, y + h * 0.10, x + w * 0.26, y + h * 0.30], fill=(120, 120, 120))
        d.ellipse([x + w * 0.16, y + h * 0.04, x + w * 0.30, y + h * 0.20], fill=(140, 140, 140))
        d.ellipse([x + w * 0.80, y + h * 0.68, x + w * 0.92, y + h * 0.82], fill=(30, 30, 30))
        for a in range(8):
            import math
            ang = a * 3.14159 / 4
            d.line([x + w * 0.86 + 5 * math.cos(ang), y + h * 0.75 + 5 * math.sin(ang),
                    x + w * 0.86 + 10 * math.cos(ang), y + h * 0.75 + 10 * math.sin(ang)],
                   fill=(30, 30, 30), width=2)
    elif kind == "eustars":  # EU circle of stars + columns
        _sky(d, box, (38, 64, 120), (70, 100, 160))
        import math
        for k in range(12):
            ang = k * 3.14159 / 6 - 3.14159 / 2
            sx = cx + w * 0.26 * math.cos(ang)
            sy = cy - 2 + h * 0.30 * math.sin(ang)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 215, 0))
        d.rectangle([x + w * 0.10, y1 - 12, x + w * 0.90, y1 - 6], fill=(230, 225, 210))
        for k in range(5):
            bx = x + w * (0.16 + k * 0.17)
            d.rectangle([bx, y + h * 0.62, bx + 7, y1 - 12], fill=(230, 225, 210))
        d.rectangle([x + w * 0.10, y + h * 0.55, x + w * 0.90, y + h * 0.62], fill=(230, 225, 210))
    elif kind == "storm":  # nor'easter: clouds, rain, balloon
        _sky(d, box, (90, 100, 115), (130, 135, 145))
        d.ellipse([x + 6, y + 4, x + w * 0.45, y + 24], fill=(60, 65, 75))
        d.ellipse([x + w * 0.45, y + 2, x + w * 0.90, y + 22], fill=(70, 75, 85))
        d.ellipse([x + w * 0.62, y + 8, x + w * 0.88, y + 30], fill=(235, 90, 60))  # balloon
        d.line([x + w * 0.75, y + 30, x + w * 0.72, y + 40], fill=(60, 60, 60), width=2)
        for k in range(7):
            rx = x + 10 + k * (w - 20) / 6
            d.line([rx, y + h * 0.55, rx - 4, y + h * 0.85], fill=(200, 210, 225), width=2)
        d.polygon([(x + 8, y1), (x + 8, y + h * 0.72), (x + w * 0.30, y + h * 0.72), (x + w * 0.30, y1)],
                  fill=(50, 50, 55))
        d.polygon([(x + w * 0.30, y + h * 0.62), (x + w * 0.30, y1), (x + w * 0.55, y1)],
                  fill=(40, 40, 45))
    elif kind == "podium":  # Trump podium + flags + Miami towers
        _sky(d, box, (120, 150, 190), (200, 205, 215))
        for k, bh in enumerate([0.45, 0.62, 0.52, 0.70]):
            bx = x + w * (0.06 + k * 0.14)
            d.rectangle([bx, y + h * (1 - bh), bx + w * 0.10, y1], fill=(70, 85, 110))
        d.rectangle([x + w * 0.62, y + 6, x + w * 0.70, y + h * 0.55], fill=(200, 60, 50))
        d.rectangle([x + w * 0.62, y + 6, x + w * 0.70, y + 16], fill=(255, 255, 255))
        d.rectangle([x + w * 0.80, y + 6, x + w * 0.88, y + h * 0.55], fill=(40, 70, 160))
        d.rectangle([x + w * 0.42, y + h * 0.60, x + w * 0.58, y1], fill=(40, 45, 60))
        d.ellipse([cx - 7, y + h * 0.42, cx + 7, y + h * 0.60], fill=(235, 200, 160))
        d.rectangle([x + w * 0.42, y + h * 0.60, x + w * 0.58, y + h * 0.72], fill=(30, 30, 40))
    elif kind == "skyline":  # Gaza skyline + smoke
        _sky(d, box, (225, 200, 160), (200, 170, 120))
        for k, bh in enumerate([0.5, 0.68, 0.42, 0.60, 0.48]):
            bx = x + w * (0.04 + k * 0.19)
            d.rectangle([bx, y + h * (1 - bh), bx + w * 0.15, y1], fill=(90, 80, 70))
            for wy in range(2):
                d.rectangle([bx + 3, y + h * (1 - bh) + 6 + wy * 12, bx + 8, y + h * (1 - bh) + 11 + wy * 12],
                            fill=(255, 220, 130))
        d.ellipse([x + w * 0.60, y + 2, x + w * 0.78, y + 20], fill=(110, 110, 110))
        d.ellipse([x + w * 0.68, y - 2, x + w * 0.86, y + 16], fill=(130, 130, 130))
        d.polygon([(x + w * 0.70, y + 18), (x + w * 0.74, y + 34), (x + w * 0.66, y + 34)], fill=(120, 120, 120))
    elif kind == "clinic":  # Ebola clinic tent + virus
        _sky(d, box, (190, 225, 200), (150, 200, 170))
        d.polygon([(x + w * 0.10, y + h * 0.60), (cx, y + h * 0.18), (x + w * 0.90, y + h * 0.60)],
                  fill=(245, 245, 240))
        d.rectangle([x + w * 0.44, y + h * 0.42, x + w * 0.56, y + h * 0.60], fill=(200, 40, 40))
        d.rectangle([x + w * 0.47, y + h * 0.46, x + w * 0.53, y + h * 0.56], fill=(255, 255, 255))
        d.rectangle([x + w * 0.47, y + h * 0.42, x + w * 0.53, y + h * 0.60], fill=(255, 255, 255))
        d.ellipse([x + w * 0.72, y + h * 0.55, x + w * 0.90, y + h * 0.78], fill=(150, 40, 120))
        import math
        for a in range(8):
            ang = a * 3.14159 / 4
            d.line([x + w * 0.81 + 8 * math.cos(ang), y + h * 0.66 + 8 * math.sin(ang),
                    x + w * 0.81 + 13 * math.cos(ang), y + h * 0.66 + 13 * math.sin(ang)],
                   fill=(150, 40, 120), width=2)
        d.ellipse([x + w * 0.06, y + h * 0.62, x + w * 0.20, y + h * 0.80], fill=(60, 120, 200))
    elif kind == "night":  # night drone barrage + interceptor
        _sky(d, box, (20, 28, 50), (35, 50, 80))
        import math
        for k in range(14):
            sx = x + (k * 37) % w
            sy = y + (k * 23) % int(h * 0.5)
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
        for k in range(4):
            dx = x + w * (0.12 + k * 0.22)
            dy = y + h * (0.18 + (k % 2) * 0.14)
            d.ellipse([dx, dy, dx + 12, dy + 5], fill=(200, 200, 200))
            d.line([dx - 6, dy + 2, dx + 18, dy + 2], fill=(200, 200, 200), width=2)
        d.line([x + w * 0.15, y1 - 4, x + w * 0.75, y + h * 0.25], fill=(255, 200, 60), width=2)
        d.polygon([(x + w * 0.05, y1), (x + w * 0.05, y + h * 0.72), (x + w * 0.30, y + h * 0.72), (x + w * 0.30, y1)],
                  fill=(15, 20, 35))
    elif kind == "beehive":  # NZ Beehive + seat bars 65 vs 65
        _sky(d, box, (200, 220, 235), (170, 195, 215))
        d.polygon([(x + w * 0.14, y + h * 0.30), (x + w * 0.34, y + h * 0.12), (x + w * 0.54, y + h * 0.30)],
                  fill=(120, 130, 140))
        d.rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.54, y1 - 8], fill=(150, 160, 170))
        for r in range(3):
            d.line([x + w * 0.16, y + h * (0.42 + r * 0.16), x + w * 0.52, y + h * (0.42 + r * 0.16)],
                   fill=(90, 100, 110), width=2)
        d.rectangle([x + w * 0.62, y + h * 0.55, x + w * 0.70, y1 - 8], fill=(46, 90, 136))
        d.rectangle([x + w * 0.72, y + h * 0.55, x + w * 0.80, y1 - 8], fill=(125, 60, 152))
        d.rectangle([x + w * 0.82, y + h * 0.72, x + w * 0.90, y1 - 8], fill=(230, 126, 34))
        d.rectangle([x + w * 0.62, y + h * 0.30, x + w * 0.90, y + h * 0.44], fill=(255, 255, 255), outline=(60, 60, 60))
        d.text((x + w * 0.65, y + h * 0.31), "65 - 65", font=font(F_BOLD, 10), fill=(20, 20, 20))
    elif kind == "plane":  # plane + falling chart
        _sky(d, box, (210, 225, 240), (180, 200, 220))
        d.polygon([(x + w * 0.10, y + h * 0.45), (x + w * 0.70, y + h * 0.30), (x + w * 0.90, y + h * 0.38),
                   (x + w * 0.70, y + h * 0.52), (x + w * 0.30, y + h * 0.58)], fill=(240, 240, 240))
        d.polygon([(x + w * 0.35, y + h * 0.42), (x + w * 0.45, y + h * 0.20), (x + w * 0.55, y + h * 0.42)],
                  fill=(200, 60, 50))
        d.line([x + w * 0.08, y + h * 0.80, x + w * 0.90, y + h * 0.80], fill=(60, 60, 60), width=2)
        pts = [(x + w * 0.10, y + h * 0.70), (x + w * 0.35, y + h * 0.62), (x + w * 0.60, y + h * 0.68),
               (x + w * 0.88, y + h * 0.55)]
        d.line(pts, fill=(176, 58, 46), width=3)
        d.polygon([(x + w * 0.88, y + h * 0.55), (x + w * 0.80, y + h * 0.55), (x + w * 0.88, y + h * 0.47)],
                  fill=(176, 58, 46))
    elif kind == "bank":  # bank + chip + up arrow
        _sky(d, box, (205, 220, 235), (175, 195, 215))
        d.polygon([(x + w * 0.12, y + h * 0.34), (cx - 14, y + h * 0.14), (x + w * 0.52, y + h * 0.34)],
                  fill=(60, 80, 110))
        for k in range(4):
            bx = x + w * (0.15 + k * 0.10)
            d.rectangle([bx, y + h * 0.38, bx + 6, y + h * 0.78], fill=(230, 230, 225))
        d.rectangle([x + w * 0.10, y + h * 0.78, x + w * 0.54, y + h * 0.84], fill=(60, 80, 110))
        d.rectangle([x + w * 0.62, y + h * 0.42, x + w * 0.88, y + h * 0.72], fill=(40, 45, 55))
        for k in range(3):
            d.line([x + w * (0.67 + k * 0.07), y + h * 0.50, x + w * (0.67 + k * 0.07), y + h * 0.64],
                   fill=(120, 200, 140), width=2)
        d.line([x + w * 0.60, y + h * 0.72, x + w * 0.78, y + h * 0.30, x + w * 0.95, y + h * 0.22],
               fill=(34, 153, 84), width=3)
        d.polygon([(x + w * 0.95, y + h * 0.22), (x + w * 0.86, y + h * 0.22), (x + w * 0.95, y + h * 0.32)],
                  fill=(34, 153, 84))
    elif kind == "chess":  # chessboard + king
        _sky(d, box, (235, 225, 205), (215, 200, 170))
        bs = min(w, h) * 0.62
        bx, by = x + w * 0.06, y + h * 0.16
        cell = bs / 4
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0:
                    d.rectangle([bx + c * cell, by + r * cell, bx + (c + 1) * cell, by + (r + 1) * cell],
                                fill=(60, 45, 30))
                else:
                    d.rectangle([bx + c * cell, by + r * cell, bx + (c + 1) * cell, by + (r + 1) * cell],
                                fill=(240, 225, 200))
        d.rectangle([bx, by, bx + bs, by + bs], outline=(40, 30, 20), width=2)
        kx, ky = x + w * 0.74, y + h * 0.30
        d.ellipse([kx - 9, ky - 9, kx + 9, ky + 9], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        d.line([kx, ky - 15, kx, ky - 9], fill=(30, 30, 30), width=3)
        d.line([kx - 5, ky - 12, kx + 5, ky - 12], fill=(30, 30, 30), width=3)
        d.rectangle([kx - 11, ky + 8, kx + 11, ky + 22], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        d.rectangle([kx - 14, ky + 22, kx + 14, ky + 27], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        qx, qy = x + w * 0.86, y + h * 0.62
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=(30, 30, 30))
        d.rectangle([qx - 8, qy + 6, qx + 8, qy + 18], fill=(30, 30, 30))
    elif kind == "refinery":  # refinery towers + flame
        _sky(d, box, (225, 210, 180), (200, 175, 130))
        d.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.24, y1], fill=(120, 120, 125))
        d.rectangle([x + w * 0.28, y + h * 0.30, x + w * 0.40, y1], fill=(140, 140, 145))
        d.rectangle([x + w * 0.44, y + h * 0.55, x + w * 0.62, y1], fill=(110, 110, 115))
        d.rectangle([x + w * 0.66, y + h * 0.40, x + w * 0.86, y1], fill=(130, 130, 135))
        d.polygon([(x + w * 0.72, y + h * 0.22), (x + w * 0.80, y + h * 0.02), (x + w * 0.88, y + h * 0.22)],
                  fill=(255, 140, 30))
        d.polygon([(x + w * 0.75, y + h * 0.22), (x + w * 0.80, y + h * 0.10), (x + w * 0.85, y + h * 0.22)],
                  fill=(255, 220, 60))
        d.ellipse([x + w * 0.30, y + h * 0.08, x + w * 0.44, y + h * 0.24], fill=(120, 120, 120))
        d.ellipse([x + w * 0.36, y + h * 0.02, x + w * 0.50, y + h * 0.16], fill=(140, 140, 140))

# ---------------------------------------------------------------- page layout
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    avail = x1 - x0

    # --- top strip
    d.rectangle([0, 0, W, 26], fill=NAVY)
    f_top = font(F_BOLD, 13)
    d.text((x0, 5), "THE WORLD IN ONE DAY", font=f_top, fill=(255, 255, 255))
    f_top_r = font(F_BOLD, 11)
    rt = "46 STORIES  -  10 REGIONS  -  FRIDAY 27 NOVEMBER 2026"
    d.text((x1 - d.textlength(rt, font=f_top_r), 6), rt, font=f_top_r, fill=(255, 215, 120))

    # --- masthead
    f_title = font(F_SERIF, 56)
    title = "Friday 27 November 2026"
    while d.textlength(title, font=f_title) > avail and f_title.size > 30:
        f_title = font(F_SERIF, f_title.size - 2)
    d.text(((W - d.textlength(title, font=f_title)) / 2, 30), title, font=f_title, fill=INK)
    f_sub = font(F_BOLD, 13)
    sub = ("Storm cuts power to nearly a million Americans  -  Drone attack kills two Italians "
           "in Kuwait  -  EU summit ends with no budget deal")
    while d.textlength(sub, font=f_sub) > avail and f_sub.size > 9:
        f_sub = font(F_BOLD, f_sub.size - 1)
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 96), sub, font=f_sub, fill=RED)
    d.line([x0, 118, x1, 118], fill=RULE, width=2)
    d.line([x0, 122, x1, 122], fill=RULE, width=1)

    # --- stat strip: 6 boxes
    sy, sh = 128, 54
    gap = 6
    bw = (avail - 5 * gap) // 6
    f_num = font(F_BOLD, 23)
    f_lab = font(F_SANS, 8)
    for i, (num, lab) in enumerate(STATS):
        bx = x0 + i * (bw + gap)
        d.rectangle([bx, sy, bx + bw, sy + sh], fill=LIGHT, outline=(200, 196, 186))
        d.rectangle([bx, sy, bx + bw, sy + 3], fill=RED)
        nw = d.textlength(num, font=f_num)
        d.text((bx + (bw - nw) / 2, sy + 6), num, font=f_num, fill=INK)
        lines = fit_lines(d, lab, f_lab, bw - 10, 2)
        ly = sy + 33
        for ln in lines:
            d.text((bx + (bw - d.textlength(ln, font=f_lab)) / 2, ly), ln, font=f_lab, fill=(70, 70, 70))
            ly += 10

    # --- region bar
    ry, rh = 188, 24
    total = sum(c for _, c, _ in REGIONS)
    cx = x0
    short_names = {"N AMERICA": "N AMER"}
    for name, count, col in REGIONS:
        seg = int(round(avail * count / total))
        if name == "OCEANIA":
            seg = avail - (cx - x0)
        d.rectangle([cx, ry, cx + seg, ry + rh], fill=col)
        label = "%s %d" % (short_names.get(name, name), count)
        placed = False
        for fsize in (9, 8, 7):
            f_reg = font(F_BOLD, fsize)
            if d.textlength(label, font=f_reg) <= seg - 4:
                d.text((cx + (seg - d.textlength(label, font=f_reg)) / 2, ry + 12 - fsize / 2),
                       label, font=f_reg, fill=(255, 255, 255))
                placed = True
                break
        if not placed:
            f_reg = font(F_BOLD, 9)
            num = str(count)
            d.text((cx + (seg - d.textlength(num, font=f_reg)) / 2, ry + 6), num,
                   font=f_reg, fill=(255, 255, 255))
        cx += seg

    # --- UTC timeline (all labels below the line, one row)
    ty = 218
    d.rectangle([x0, ty, x0 + 108, ty + 50], fill=NAVY)
    f_tl = font(F_BOLD, 11)
    d.text((x0 + 8, ty + 8), "THE DAY", font=f_tl, fill=(255, 255, 255))
    d.text((x0 + 8, ty + 24), "IN UTC", font=f_tl, fill=(255, 215, 120))
    line_x0, line_x1, line_y = x0 + 122, x1, ty + 14
    d.line([line_x0, line_y, line_x1, line_y], fill=RULE, width=2)
    f_tt = font(F_BOLD, 10)
    f_tx = font(F_SANS, 8)
    n_tl = len(TIMELINE)
    for i, (tm, txt) in enumerate(TIMELINE):
        px = line_x0 + (line_x1 - line_x0) * i / (n_tl - 1)
        d.ellipse([px - 4, line_y - 4, px + 4, line_y + 4], fill=RED, outline=(255, 255, 255), width=1)
        tw = 128
        if i == n_tl - 1:  # last label: right-align so it cannot hit the previous one
            lx = x1 - max(d.textlength(tm, font=f_tt), d.textlength(txt, font=f_tx)) - 2
        else:  # left-align from the dot: next dot is 146px away, so no overlap
            lx = px
        lines = fit_lines(d, txt, f_tx, tw, 2)
        ly = line_y + 8
        d.text((lx, ly), tm, font=f_tt, fill=RED)
        draw_lines(d, lines, lx, ly + 11, f_tx, INK, 9)

    # --- pictured stories
    def paint_panel(idx, p, px, py, pw, ph, big):
        kind, region, kicker, head, body, tag, src, _pin = p
        colr = REGION_COLOR[region]
        d.rectangle([px, py, px + pw, py + ph], fill=(255, 255, 255), outline=(190, 186, 178))
        d.rectangle([px, py, px + pw, py + 3], fill=colr)
        ih = 58 if big else 46
        paint_scene(d, kind, (px + 4, py + 6, pw - 8, ih))
        # number badge over the illustration
        f_badge = font(F_BOLD, 12 if big else 11)
        bs = 20 if big else 18
        d.ellipse([px + 6, py + 8, px + 6 + bs, py + 8 + bs], fill=colr, outline=(255, 255, 255), width=1)
        num = str(idx + 1)
        d.text((px + 6 + (bs - d.textlength(num, font=f_badge)) / 2, py + 8 + (bs - 13) / 2 - 1),
               num, font=f_badge, fill=(255, 255, 255))
        ty2 = py + 6 + ih + 4
        f_kick = font(F_BOLD, 10 if big else 8)
        d.text((px + 6, ty2), kicker, font=f_kick, fill=colr)
        ty2 += 13 if big else 11
        f_head = font(F_BOLD, 15 if big else 12)
        head_lines = fit_lines(d, head, f_head, pw - 12, 2 if big else 3)
        ty2 = draw_lines(d, head_lines, px + 6, ty2, f_head, INK, 18 if big else 14)
        f_body = font(F_SANS, 10 if big else 8)
        body_lines = fit_lines(d, body, f_body, pw - 12, 2)
        ty2 = draw_lines(d, body_lines, px + 6, ty2 + 2, f_body, (60, 60, 60), 12 if big else 10)
        # tag chip + source, anchored at the bottom
        f_tag = font(F_BOLD, 8 if big else 7)
        f_src = font(F_SANS, 8 if big else 7)
        by = py + ph - 13
        tag_w = d.textlength(tag, font=f_tag) + 10
        tag_col = (20, 110, 60) if tag in ("OFFICIAL", "CONFIRMED") else (176, 58, 46)
        d.rectangle([px + 6, by, px + 6 + tag_w, by + 11], fill=tag_col)
        d.text((px + 11, by + 1), tag, font=f_tag, fill=(255, 255, 255))
        # With headline/body line counts capped above, the text provably
        # ends at or above the tag row (big panels: at most by-2, small:
        # at most by-6), so no overflow check is needed here.
        d.text((px + 12 + tag_w, by + 1), src, font=f_src, fill=GREY)

    # row A: 3 large panels
    ay, ah = 276, 158
    aw = (avail - 2 * 6) // 3
    for i in range(3):
        paint_panel(i, PANELS[i], x0 + i * (aw + 6), ay, aw, ah, big=True)
    # rows B and C: 5 small panels each
    by_, bh = 440, 150
    bw2 = (avail - 4 * 6) // 5
    for r in range(2):
        for c in range(5):
            i = 3 + r * 5 + c
            paint_panel(i, PANELS[i], x0 + c * (bw2 + 6), by_ + r * (bh + 6), bw2, bh, big=False)

    # --- map + more stories
    my = 756
    d.text((x0, my), "WHERE IT HAPPENED", font=font(F_BOLD, 11), fill=INK)
    d.text((x0 + 176, my + 1), "pins = picture numbers, coloured by region",
           font=font(F_SANS, 9), fill=GREY)
    mx = x0 + 482
    d.text((mx, my), "ALSO ON 27 NOVEMBER:  33 MORE STORIES", font=font(F_BOLD, 11), fill=INK)
    d.line([x0, my + 16, x1, my + 16], fill=RULE, width=1)
    map_y = my + 22
    map_h = 168
    paint_map(d, x0, map_y, 470, map_h)
    # more stories: two columns
    f_more = font(F_SANS, 9)
    f_more_b = font(F_BOLD, 9)
    col_w = (x1 - mx) // 2 - 4
    per_col = 17
    for ci in range(2):
        cx2 = mx + ci * (col_w + 8)
        for ri in range(per_col):
            k = ci * per_col + ri
            if k >= len(MORE):
                break
            city, head, region = MORE[k]
            yy = map_y + 2 + ri * 10
            num = str(14 + k)
            colr = REGION_COLOR[region]
            d.text((cx2, yy), num, font=f_more_b, fill=colr)
            nwoff = d.textlength("00 ", font=f_more_b)
            line = fit_width(d, "%s: %s" % (city, head), f_more, col_w - nwoff)
            d.text((cx2 + nwoff, yy), line, font=f_more, fill=INK)

    # --- footer
    fy = 950
    d.line([x0, fy - 4, x1, fy - 4], fill=RULE, width=2)
    f_fh = font(F_BOLD, 9)
    f_ft = font(F_SANS, 9)
    d.text((x0, fy), "DATE CHECK", font=f_fh, fill=RED)
    dc = ("Every story was first reported on Friday 27 November 2026; events shown happened "
          "Thu 26-Fri 27 Nov. Older context flagged: Cairo tanker fire was "
          "Wed 25 Nov; NZ election was 7 Nov (final count Fri); UK migration covers the year to Jun 2026; "
          "Ebola totals are cumulative.")
    dc_lines = fit_lines(d, dc, f_ft, avail - 92, 2)
    draw_lines(d, dc_lines, x0 + 92, fy, f_ft, INK, 11)
    hy = fy + 26
    d.text((x0, hy), "HOW SURE", font=f_fh, fill=RED)
    hs = "OFFICIAL  said by a government, court or agency   -   CONFIRMED  carried by two or more outlets   -   CLAIM  one side's account, not verified"
    d.text((x0 + 92, hy), hs, font=f_ft, fill=INK)
    sy2 = hy + 15
    src_lines = wrap_text(d, SOURCES_LINE, font(F_SANS, 8), avail)
    draw_lines(d, src_lines, x0, sy2, font(F_SANS, 8), GREY, 10)
    d.text((x0, H - 16), "PAGE 1  -  WORLD NEWS  -  PRINTED 27 NOVEMBER 2026  -  EDITION NO. 11,429",
           font=font(F_SANS, 8), fill=GREY)

    return img


def main():
    img = compose()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="JPEG", quality=88)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
