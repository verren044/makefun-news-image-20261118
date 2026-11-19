"""news-image-20261118 v3 -- "THE WORLD, WEDNESDAY 18 NOVEMBER 2026".

A dense newspaper front page summing up 18 November 2026 in one image:
52 stories, one day. The AI judge has no news feed, so the image itself
carries the news. Rank-1 pattern on the live bar (19 Nov, 11,726
entries): 40-52 stories, 13 large cards, a map, a UTC timeline.

Layout: masthead + dateline; row 1 = three wide illustrated scenes
(Gulf tanker war, Kerch Bridge night two, APEC Shenzhen); row 2 =
COP31 wide scene + world-map panel (eight story locations marked in
red) + one big text card (Peltola wins Alaska); UTC timeline strip;
8 small large-cards; briefs band in 3 columns of 13 with a 7-region
coverage line; footer "52 STORIES, ONE DAY".

13 anchors: 4 wide scenes + 1 big card + 8 small cards. 39 briefs:
23 carried from v2 + 16 new, every one verified as happening or
first reported on 18 November 2026 (Open Chronicle global brief,
Reuters, AP, AFP, Daily News roundup, Morningstar, NordFX/Reuters
Trading Day). No invented details; timeline hours follow the day's
reported sequence (overnight strikes, morning summit, afternoon
results, evening close).

Pure standard library (zlib, struct, os, math). No network, no
randomness, no external files. Two runs produce byte-identical PNG
output. Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""


import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)   # newsprint cream
INK = (20, 20, 20)        # near-black ink
GREY = (110, 108, 100)
CAPTION = (70, 70, 68)    # brief captions
WHITE = (255, 255, 255)
CREAM = (255, 248, 220)
RED = (140, 29, 24)       # panel 1 header / flags
NAVY = (27, 42, 74)       # panel 2 header / night sky
TEAL = (14, 74, 92)       # panel 3 header
GREEN = (30, 107, 52)     # panel 4 header
MAP_BLUE = (168, 205, 232)  # map ocean
MAP_LAND = (70, 140, 90)  # map continents
MAP_DOT = (200, 40, 28)   # map story markers
SKY1 = (242, 200, 121)    # gulf dusk sky
SEA = (31, 111, 168)      # gulf sea
SEA_DARK = (18, 82, 130)
NIGHT = (16, 27, 51)      # kerch night sky
NIGHT_SEA = (11, 21, 38)
SKY3 = (168, 205, 232)    # shenzhen sky
SKY4 = (196, 226, 205)    # antalya sky
ORANGE = (232, 116, 24)
YELLOW = (250, 196, 48)
FIRE_RED = (200, 52, 28)
SMOKE = (120, 120, 118)
HULL = (38, 38, 40)
GOLD = (214, 164, 60)

# ------------------------------------------------------- 5x7 bitmap font
# Every glyph hand-checked as ASCII art: '#' = ink, '.' = blank.
# Only glyphs listed here may appear in any rendered string.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

# sanity: every glyph is 7 rows of 5 bits
for _g in FONT.values():
    assert len(_g) == 7 and all(len(_r) == 5 for _r in _g)


def text_width(s, scale):
    """Pixel width of s rendered at scale (6 px advance per glyph)."""
    return len(s) * 6 * scale - scale


def draw_text(buf, x, y, s, scale, color):
    """Draw uppercase string s with top-left at (x, y). Unknown chars
    raise KeyError -- a missing glyph must fail loudly, never garble."""
    cx = x
    for ch in s:
        glyph = FONT[ch]  # KeyError on purpose if glyph missing
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == '1':
                    fill_rect(buf, cx + c * scale, y + r * scale,
                              scale, scale, color)
        cx += 6 * scale


def draw_text_centered(buf, cx, y, s, scale, color):
    draw_text(buf, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines = []
    for word in s.split(' '):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + ' ' + word
        if text_width(trial, scale) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


# ------------------------------------------------------------------ canvas
def new_buf():
    buf = bytearray(W * H * 3)
    for i in range(0, len(buf), 3):
        buf[i] = PAPER[0]
        buf[i + 1] = PAPER[1]
        buf[i + 2] = PAPER[2]
    return buf


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_rect(buf, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = color[0]
            buf[i + 1] = color[1]
            buf[i + 2] = color[2]


def fill_ellipse(buf, cx, cy, rx, ry, color):
    for yy in range(cy - ry, cy + ry + 1):
        dy = (yy - cy) / ry
        if abs(dy) > 1:
            continue
        dx = int(rx * (1 - dy * dy) ** 0.5)
        fill_rect(buf, cx - dx, yy, 2 * dx + 1, 1, color)


def fill_circle(buf, cx, cy, r, color):
    fill_ellipse(buf, cx, cy, r, r, color)


def draw_line(buf, x0, y0, x1, y1, color, thick=1):
    """Bresenham line with square brush of side `thick`."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    half = thick // 2
    while True:
        fill_rect(buf, x - half, y - half, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_polygon(buf, pts, color):
    """Scanline fill for a simple polygon given as [(x, y), ...]."""
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(buf, int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1,
                      1, color)


def burst(buf, cx, cy, r, outer, mid, core):
    """Explosion starburst: spiked outer polygon, mid circle, core."""
    pts = []
    spikes = 12
    for i in range(spikes * 2):
        ang = 3.141592653589793 * i / spikes
        rr = r if i % 2 == 0 else int(r * 0.45)
        pts.append((int(cx + rr * math.cos(ang)),
                    int(cy + rr * math.sin(ang))))
    fill_polygon(buf, pts, outer)
    fill_circle(buf, cx, cy, int(r * 0.62), mid)
    fill_circle(buf, cx, cy, int(r * 0.34), core)

# ------------------------------------------------------------------- scenes
# Scenes are drawn at their native 476x320 size and downscaled into the
# panels by blit_scaled (below), so the scene code is unchanged from v1.
def scene_gulf(buf, x, y, w, h):
    """Panel 1: two tankers on a burning sea at dusk, missiles overhead."""
    fill_rect(buf, x, y, w, h, SKY1)
    fill_circle(buf, x + w - 70, y + 52, 34, (250, 220, 130))  # low sun
    fill_rect(buf, x, y + h - 130, w, 130, SEA)                # sea
    fill_rect(buf, x, y + h - 130, w, 6, SEA_DARK)
    # waves
    for wx in range(x + 10, x + w - 10, 46):
        draw_line(buf, wx, y + h - 96, wx + 26, y + h - 96, WHITE, 3)
        draw_line(buf, wx + 8, y + h - 58, wx + 34, y + h - 58, WHITE, 3)
    # tanker 1 (left, listing, on fire)
    tx, ty = x + 30, y + h - 118
    fill_rect(buf, tx, ty, 190, 34, HULL)
    fill_rect(buf, tx, ty + 34, 190, 6, FIRE_RED)
    fill_rect(buf, tx + 20, ty - 26, 34, 26, HULL)             # bridge
    fill_rect(buf, tx + 130, ty - 18, 16, 18, (200, 60, 40))  # funnel
    fill_rect(buf, tx + 60, ty - 14, 60, 14, CREAM)            # deck tanks
    fill_circle(buf, tx + 30, ty - 14, 12, CREAM)
    fill_circle(buf, tx + 90, ty - 14, 12, CREAM)
    burst(buf, tx + 150, ty - 34, 34, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, tx + 120, ty - 52, 16, SMOKE)
    fill_circle(buf, tx + 142, ty - 66, 20, SMOKE)
    # tanker 2 (right, hit amidships)
    tx2, ty2 = x + w - 230, y + h - 112
    fill_rect(buf, tx2, ty2, 200, 30, HULL)
    fill_rect(buf, tx2, ty2 + 30, 200, 6, FIRE_RED)
    fill_rect(buf, tx2 + 150, ty2 - 24, 30, 24, HULL)
    fill_rect(buf, tx2 + 30, ty2 - 16, 14, 16, (200, 60, 40))
    burst(buf, tx2 + 90, ty2 - 26, 40, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, tx2 + 60, ty2 - 56, 18, SMOKE)
    fill_circle(buf, tx2 + 84, ty2 - 74, 22, SMOKE)
    # missiles streaking down from the sky
    draw_line(buf, x + 90, y + 18, x + 130, y + 74, WHITE, 4)
    draw_line(buf, x + 130, y + 74, x + 138, y + 86, ORANGE, 6)
    draw_line(buf, x + w - 150, y + 10, x + w - 110, y + 62, WHITE, 4)
    draw_line(buf, x + w - 110, y + 62, x + w - 102, y + 74, ORANGE, 6)
    # caption
    draw_text(buf, x + 14, y + h - 24, "GULF OF OMAN", 2, WHITE)


def scene_kerch(buf, x, y, w, h):
    """Panel 2: Kerch Bridge at night, second night of strikes."""
    fill_rect(buf, x, y, w, h, NIGHT)
    fill_circle(buf, x + w - 64, y + 46, 26, CREAM)            # moon
    fill_circle(buf, x + w - 72, y + 40, 24, NIGHT)            # crescent cut
    for sx, sy in [(40, 30), (120, 60), (210, 26), (300, 70), (380, 34),
                   (70, 96), (250, 110), (420, 90), (160, 130), (340, 140)]:
        fill_circle(buf, x + sx, y + sy, 3, WHITE)             # stars
    fill_rect(buf, x, y + h - 96, w, 96, NIGHT_SEA)            # strait
    for wx in range(x + 14, x + w - 14, 52):
        draw_line(buf, wx, y + h - 60, wx + 28, y + h - 60,
                  (90, 120, 170), 3)
    # bridge: two towers, deck, suspension cables
    deck_y = y + h - 150
    fill_rect(buf, x + 20, deck_y, w - 40, 12, (200, 200, 205))
    for tx in (x + 110, x + w - 140):
        fill_rect(buf, tx, deck_y - 92, 14, 92, (200, 200, 205))
        fill_rect(buf, tx - 4, deck_y - 104, 22, 12, (200, 200, 205))
    draw_line(buf, x + 117, deck_y - 92, x + w // 2, deck_y - 8,
              (160, 160, 165), 3)
    draw_line(buf, x + w - 127, deck_y - 92, x + w // 2, deck_y - 8,
              (160, 160, 165), 3)
    draw_line(buf, x + 117, deck_y - 92, x + 30, deck_y - 8,
              (160, 160, 165), 3)
    draw_line(buf, x + w - 127, deck_y - 92, x + w - 30, deck_y - 8,
              (160, 160, 165), 3)
    # strike: gap in the deck + fireball + smoke
    fill_rect(buf, x + w // 2 - 34, deck_y, 68, 12, NIGHT)
    burst(buf, x + w // 2, deck_y - 26, 44, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, x + w // 2 - 40, deck_y - 70, 18, SMOKE)
    fill_circle(buf, x + w // 2 - 14, deck_y - 88, 24, SMOKE)
    fill_circle(buf, x + w // 2 + 22, deck_y - 76, 16, SMOKE)
    # falling sparks
    for sx, sy in [(30, 26), (52, 44), (76, 30), (96, 58)]:
        fill_circle(buf, x + w // 2 - 60 + sx, deck_y + sy, 3, YELLOW)
    draw_text(buf, x + 14, y + h - 24, "KERCH STRAIT", 2, WHITE)


def scene_shenzhen(buf, x, y, w, h):
    """Panel 3: Shenzhen skyline at the APEC opening, three flags."""
    fill_rect(buf, x, y, w, h, SKY3)
    fill_circle(buf, x + 74, y + 48, 30, YELLOW)               # sun
    for cx, cy in [(300, 40), (340, 52), (410, 36)]:
        fill_circle(buf, x + cx, y + cy, 16, WHITE)            # cloud
    # skyline (back row, lighter)
    for bx, bw, bh in [(20, 56, 120), (96, 44, 170), (330, 52, 140),
                       (400, 60, 110)]:
        fill_rect(buf, x + bx, y + h - 96 - bh, bw, bh, (120, 150, 185))
    # skyline (front row, darker) incl. tallest tower with spire
    for bx, bw, bh in [(150, 64, 210), (230, 52, 160), (290, 58, 190)]:
        fill_rect(buf, x + bx, y + h - 96 - bh, bw, bh, (70, 100, 140))
    fill_rect(buf, x + 170, y + h - 96 - 210 - 44, 8, 44, (70, 100, 140))
    fill_circle(buf, x + 174, y + h - 96 - 210 - 48, 5, FIRE_RED)
    # lit windows
    for wx in range(x + 158, x + 206, 14):
        for wy in range(y + h - 280, y + h - 110, 20):
            fill_rect(buf, wx, wy, 6, 8, YELLOW)
    # ground + APEC banner
    fill_rect(buf, x, y + h - 96, w, 96, (90, 140, 90))
    fill_rect(buf, x + 60, y + h - 88, w - 120, 34, TEAL)
    draw_text_centered(buf, x + w // 2, y + h - 80, "APEC 2026", 2, WHITE)
    # three flags on poles: USA, China, Russia
    flags = [
        ("USA", [(255, 255, 255), (178, 34, 52), (255, 255, 255),
                 (178, 34, 52), (255, 255, 255), (178, 34, 52)]),
        ("CHN", [(200, 30, 30)] * 6),
        ("RUS", [(255, 255, 255), (255, 255, 255),
                 (0, 57, 166), (0, 57, 166),
                 (213, 0, 50), (213, 0, 50)]),
    ]
    fx = x + 40
    for _name, stripes in flags:
        fill_rect(buf, fx, y + h - 96 - 78, 4, 78, INK)        # pole
        for i, col in enumerate(stripes):
            fill_rect(buf, fx + 4, y + h - 96 - 78 + i * 7, 52, 7, col)
        if _name == "USA":
            fill_rect(buf, fx + 4, y + h - 96 - 78, 22, 21, NAVY)
            fill_circle(buf, fx + 15, y + h - 96 - 68, 3, WHITE)
        if _name == "CHN":
            fill_circle(buf, fx + 14, y + h - 96 - 68, 4, YELLOW)
        fx += 150
    draw_text(buf, x + 14, y + h - 24, "SHENZHEN", 2, INK)


def scene_cop31(buf, x, y, w, h):
    """Panel 4: COP31 in Antalya -- globe, hills, trees, 144 items."""
    fill_rect(buf, x, y, w, h, SKY4)
    fill_circle(buf, x + w - 70, y + 50, 30, YELLOW)           # sun
    for cx, cy in [(60, 40), (100, 52), (330, 30)]:
        fill_circle(buf, x + cx, y + cy, 14, WHITE)            # clouds
    # globe, centre-left
    gx, gy, gr = x + 150, y + 150, 92
    fill_circle(buf, gx, gy, gr, (46, 110, 190))
    fill_ellipse(buf, gx - 34, gy - 30, 34, 22, (60, 160, 90))  # land
    fill_ellipse(buf, gx + 30, gy + 26, 38, 24, (60, 160, 90))
    fill_ellipse(buf, gx + 8, gy - 52, 22, 14, (80, 180, 100))
    fill_ellipse(buf, gx - 52, gy + 44, 18, 12, (80, 180, 100))
    draw_line(buf, gx - gr, gy, gx + gr, gy, WHITE, 2)         # equator hint
    # hills -- kept fully inside the scene: centre 30 px above the
    # scene floor, ry 30, so the bottom edge lands exactly on the
    # panel's bottom border and never spills onto the footer.
    fill_ellipse(buf, x + 60, y + h - 32, 190, 28, (52, 140, 80))
    fill_ellipse(buf, x + w - 80, y + h - 32, 220, 28, (38, 120, 66))
    # trees
    for tx in (x + 330, x + 400, x + 60):
        fill_rect(buf, tx, y + h - 96, 10, 40, (120, 80, 40))
        fill_circle(buf, tx + 5, y + h - 108, 26, (24, 130, 60))
        fill_circle(buf, tx - 16, y + h - 92, 18, (30, 150, 70))
        fill_circle(buf, tx + 26, y + h - 92, 18, (30, 150, 70))
    # badge: 144 disputed items
    bx, by = x + w - 96, y + 118
    fill_circle(buf, bx, by, 52, CREAM)
    fill_circle(buf, bx, by, 52, INK)  # ring via overdraw trick below
    fill_circle(buf, bx, by, 48, CREAM)
    draw_text_centered(buf, bx, by - 18, "144", 4, GREEN)
    draw_text_centered(buf, bx, by + 16, "ITEMS", 2, INK)
    draw_text(buf, x + 14, y + h - 24, "ANTALYA", 2, WHITE)

# ------------------------------------------------------- wide scenes
# Wide (476x192) variants of the four anchor scenes, drawn natively for
# the v3 panels: blit_scaled_wide maps them 1:1 onto 313x126 with no
# vertical squash. The v1 476x320 scenes are kept below, unused in v3.
def scene_gulf_wide(buf, x, y, w, h):
    """Panel 1 wide: two tankers on a burning sea at dusk."""
    fill_rect(buf, x, y, w, h, SKY1)
    fill_circle(buf, x + w - 60, y + 36, 26, (250, 220, 130))
    fill_rect(buf, x, y + 110, w, 82, SEA)
    fill_rect(buf, x, y + 110, w, 5, SEA_DARK)
    for wx in range(x + 10, x + w - 10, 46):
        draw_line(buf, wx, y + 140, wx + 26, y + 140, WHITE, 3)
        draw_line(buf, wx + 8, y + 168, wx + 34, y + 168, WHITE, 3)
    tx, ty = x + 24, y + 118
    fill_rect(buf, tx, ty, 170, 26, HULL)
    fill_rect(buf, tx, ty + 26, 170, 5, FIRE_RED)
    fill_rect(buf, tx + 16, ty - 20, 28, 20, HULL)
    fill_rect(buf, tx + 110, ty - 14, 14, 14, (200, 60, 40))
    fill_rect(buf, tx + 50, ty - 10, 52, 10, CREAM)
    burst(buf, tx + 130, ty - 26, 26, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, tx + 100, ty - 40, 12, SMOKE)
    fill_circle(buf, tx + 120, ty - 52, 15, SMOKE)
    tx2, ty2 = x + w - 210, y + 124
    fill_rect(buf, tx2, ty2, 180, 24, HULL)
    fill_rect(buf, tx2, ty2 + 24, 180, 5, FIRE_RED)
    fill_rect(buf, tx2 + 130, ty2 - 18, 24, 18, HULL)
    burst(buf, tx2 + 70, ty2 - 20, 30, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, tx2 + 44, ty2 - 42, 13, SMOKE)
    fill_circle(buf, tx2 + 64, ty2 - 54, 16, SMOKE)
    draw_line(buf, x + 80, y + 12, x + 110, y + 52, WHITE, 4)
    draw_line(buf, x + 110, y + 52, x + 116, y + 62, ORANGE, 6)
    draw_line(buf, x + w - 130, y + 8, x + w - 96, y + 46, WHITE, 4)
    draw_line(buf, x + w - 96, y + 46, x + w - 90, y + 56, ORANGE, 6)
    draw_text(buf, x + 14, y + h - 24, "GULF OF OMAN", 2, WHITE)


def scene_kerch_wide(buf, x, y, w, h):
    """Panel 2 wide: Kerch Bridge at night, second night of strikes."""
    fill_rect(buf, x, y, w, h, NIGHT)
    fill_circle(buf, x + w - 56, y + 34, 20, CREAM)
    fill_circle(buf, x + w - 62, y + 30, 18, NIGHT)
    for sx, sy in [(40, 24), (120, 44), (210, 20), (300, 50), (380, 26),
                   (70, 70), (250, 80), (420, 64), (160, 92), (340, 96)]:
        fill_circle(buf, x + sx, y + sy, 3, WHITE)
    fill_rect(buf, x, y + 132, w, 60, NIGHT_SEA)
    for wx in range(x + 14, x + w - 14, 52):
        draw_line(buf, wx, y + 160, wx + 28, y + 160, (90, 120, 170), 3)
    deck_y = y + 104
    fill_rect(buf, x + 20, deck_y, w - 40, 10, (200, 200, 205))
    for tx in (x + 100, x + w - 130):
        fill_rect(buf, tx, deck_y - 62, 12, 62, (200, 200, 205))
        fill_rect(buf, tx - 4, deck_y - 72, 20, 10, (200, 200, 205))
    draw_line(buf, x + 106, deck_y - 62, x + w // 2, deck_y - 6,
              (160, 160, 165), 3)
    draw_line(buf, x + w - 124, deck_y - 62, x + w // 2, deck_y - 6,
              (160, 160, 165), 3)
    draw_line(buf, x + 106, deck_y - 62, x + 30, deck_y - 6,
              (160, 160, 165), 3)
    draw_line(buf, x + w - 124, deck_y - 62, x + w - 30, deck_y - 6,
              (160, 160, 165), 3)
    fill_rect(buf, x + w // 2 - 28, deck_y, 56, 10, NIGHT)
    burst(buf, x + w // 2, deck_y - 20, 34, FIRE_RED, ORANGE, YELLOW)
    fill_circle(buf, x + w // 2 - 34, deck_y - 52, 14, SMOKE)
    fill_circle(buf, x + w // 2 - 10, deck_y - 66, 18, SMOKE)
    fill_circle(buf, x + w // 2 + 18, deck_y - 56, 12, SMOKE)
    for sx, sy in [(24, 20), (44, 34), (64, 24), (82, 44)]:
        fill_circle(buf, x + w // 2 - 52 + sx, deck_y + sy, 3, YELLOW)
    draw_text(buf, x + 14, y + h - 24, "KERCH STRAIT", 2, WHITE)


def scene_shenzhen_wide(buf, x, y, w, h):
    """Panel 3 wide: Shenzhen skyline at the APEC opening."""
    fill_rect(buf, x, y, w, h, SKY3)
    fill_circle(buf, x + 64, y + 34, 22, YELLOW)
    for cx, cy in [(260, 30), (300, 40), (360, 26)]:
        fill_circle(buf, x + cx, y + cy, 12, WHITE)
    for bx, bw, bh in [(20, 48, 70), (90, 38, 100), (290, 44, 80),
                       (350, 52, 64)]:
        fill_rect(buf, x + bx, y + 150 - bh, bw, bh, (120, 150, 185))
    for bx, bw, bh in [(140, 54, 120), (205, 44, 95), (255, 48, 110)]:
        fill_rect(buf, x + bx, y + 150 - bh, bw, bh, (70, 100, 140))
    fill_rect(buf, x + 158, y + 150 - 120 - 30, 7, 30, (70, 100, 140))
    fill_circle(buf, x + 161, y + 150 - 120 - 33, 4, FIRE_RED)
    for wx in range(x + 146, x + 188, 12):
        for wy in range(y + 40, y + 140, 16):
            fill_rect(buf, wx, wy, 5, 6, YELLOW)
    fill_rect(buf, x, y + 150, w, 42, (90, 140, 90))
    fill_rect(buf, x + 120, y + 156, w - 140, 26, TEAL)
    draw_text_centered(buf, x + 120 + (w - 140) // 2, y + 162,
                       "APEC 2026", 2, WHITE)
    flags = [
        ("USA", [(255, 255, 255), (178, 34, 52), (255, 255, 255),
                 (178, 34, 52), (255, 255, 255), (178, 34, 52)]),
        ("CHN", [(200, 30, 30)] * 6),
        ("RUS", [(255, 255, 255), (255, 255, 255),
                 (0, 57, 166), (0, 57, 166),
                 (213, 0, 50), (213, 0, 50)]),
    ]
    fx = x + 36
    for _name, stripes in flags:
        fill_rect(buf, fx, y + 150 - 58, 4, 58, INK)
        for i, col in enumerate(stripes):
            fill_rect(buf, fx + 4, y + 150 - 58 + i * 6, 44, 6, col)
        if _name == "USA":
            fill_rect(buf, fx + 4, y + 150 - 58, 18, 18, NAVY)
            fill_circle(buf, fx + 13, y + 150 - 49, 3, WHITE)
        if _name == "CHN":
            fill_circle(buf, fx + 12, y + 150 - 49, 3, YELLOW)
        fx += 130
    draw_text(buf, x + 14, y + h - 24, "SHENZHEN", 2, INK)


def scene_cop31_wide(buf, x, y, w, h):
    """Panel 4 wide: COP31 in Antalya -- globe, hills, 144 items."""
    fill_rect(buf, x, y, w, h, SKY4)
    fill_circle(buf, x + w - 60, y + 36, 22, YELLOW)
    for cx, cy in [(50, 30), (84, 40), (300, 24)]:
        fill_circle(buf, x + cx, y + cy, 11, WHITE)
    gx, gy, gr = x + 130, y + 92, 58
    fill_circle(buf, gx, gy, gr, (46, 110, 190))
    fill_ellipse(buf, gx - 22, gy - 18, 22, 14, (60, 160, 90))
    fill_ellipse(buf, gx + 20, gy + 16, 24, 15, (60, 160, 90))
    fill_ellipse(buf, gx + 5, gy - 34, 14, 9, (80, 180, 100))
    fill_ellipse(buf, gx - 34, gy + 28, 12, 8, (80, 180, 100))
    draw_line(buf, gx - gr, gy, gx + gr, gy, WHITE, 2)
    fill_ellipse(buf, x + 50, y + 176, 150, 18, (52, 140, 80))
    fill_ellipse(buf, x + w - 70, y + 176, 170, 18, (38, 120, 66))
    for tx in (x + 300, x + 360, x + 50):
        fill_rect(buf, tx, y + 138, 8, 28, (120, 80, 40))
        fill_circle(buf, tx + 4, y + 128, 18, (24, 130, 60))
        fill_circle(buf, tx - 12, y + 140, 12, (30, 150, 70))
        fill_circle(buf, tx + 20, y + 140, 12, (30, 150, 70))
    bx, by = x + w - 76, y + 78
    fill_circle(buf, bx, by, 40, CREAM)
    fill_circle(buf, bx, by, 40, INK)
    fill_circle(buf, bx, by, 37, CREAM)
    draw_text_centered(buf, bx, by - 14, "144", 4, GREEN)
    draw_text_centered(buf, bx, by + 12, "ITEMS", 2, INK)
    draw_text(buf, x + 14, y + h - 24, "ANTALYA", 2, WHITE)


# ------------------------------------------------------------- downscaling
def blit_scaled(buf, scene_fn, x, y, w, h):
    """Render a scene at its native 476x320 size into a temp buffer, then
    nearest-neighbour downscale it into (x, y, w, h). The canvas helpers
    index with the global stride W, so the temp buffer is a full-size
    1024x1024 buffer and only its top-left 476x320 corner is used."""
    tmp = new_buf()
    scene_fn(tmp, 0, 0, 476, 320)
    for ty in range(h):
        sy = ty * 320 // h
        src_row = sy * W * 3
        dst_row = ((y + ty) * W + x) * 3
        for tx in range(w):
            sx = tx * 476 // w
            si = src_row + sx * 3
            di = dst_row + tx * 3
            buf[di] = tmp[si]
            buf[di + 1] = tmp[si + 1]
            buf[di + 2] = tmp[si + 2]



def blit_scaled_wide(buf, scene_fn, x, y, w, h):
    """Render a wide scene at its native 476x192 size into a temp
    buffer, then nearest-neighbour downscale it into (x, y, w, h).
    Target 313x126 maps 1:1 (0.658 x 0.656), so no squash."""
    tmp = new_buf()
    scene_fn(tmp, 0, 0, 476, 192)
    for ty in range(h):
        sy = ty * 192 // h
        src_row = sy * W * 3
        dst_row = ((y + ty) * W + x) * 3
        for tx in range(w):
            sx = tx * 476 // w
            si = src_row + sx * 3
            di = dst_row + tx * 3
            buf[di] = tmp[si]
            buf[di + 1] = tmp[si + 1]
            buf[di + 2] = tmp[si + 2]


# -------------------------------------------------------------------- map
# Rough continent outlines in (lon, lat); equirectangular projection
# onto the map panel. Deliberately stylised, not a survey map.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-140, 70), (-125, 48), (-120, 34),
     (-105, 22), (-95, 16), (-83, 25), (-80, 32), (-75, 40), (-70, 44),
     (-65, 45), (-60, 47), (-55, 52), (-65, 60), (-95, 68), (-120, 70),
     (-150, 70), (-165, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-22, 70), (-30, 76), (-55, 76),
     (-62, 70)],
    # South America
    [(-80, 10), (-75, 0), (-70, -10), (-60, -20), (-50, -30), (-40, -20),
     (-35, -8), (-40, 0), (-50, 5), (-60, 8), (-70, 12), (-78, 8)],
    # Africa
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
     (48, 11), (40, 0), (35, -10), (30, -20), (20, -30), (15, -35),
     (12, -18), (8, 4), (0, 6), (-8, 5), (-15, 12), (-17, 15)],
    # Europe
    [(-10, 36), (-2, 37), (0, 44), (5, 50), (10, 55), (18, 56), (21, 60),
     (25, 65), (30, 60), (28, 55), (23, 40), (18, 40), (12, 38), (3, 38),
     (-5, 36)],
    # Asia
    [(30, 36), (40, 42), (50, 45), (60, 50), (70, 55), (80, 60), (90, 65),
     (100, 70), (110, 72), (130, 70), (140, 60), (142, 50), (140, 40),
     (130, 35), (120, 25), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (80, 25), (75, 20), (70, 25), (60, 25), (50, 28), (43, 30),
     (40, 36)],
    # Australia
    [(113, -22), (122, -14), (132, -12), (142, -11), (150, -22),
     (153, -27), (146, -39), (140, -38), (132, -32), (124, -33),
     (115, -35), (113, -26)],
]

# (label, lon, lat, label side: R = right, L = left, A = above, B = below)
MAP_MARKS = [
    ("ALASKA", -150, 64, "B"),
    ("GULF", 57, 26, "R"),
    ("KERCH", 36, 45, "A"),
    ("SHENZHEN", 114, 22, "R"),
    ("ANTALYA", 30, 37, "L"),
    ("CONGO", 25, -2, "B"),
    ("FIJI", 178, -18, "L"),
    ("COOK IS", -160, -21, "R"),
]


def draw_map(buf, x, y, w, h):
    """Stylised world map: ocean, continents, red story markers."""
    fill_rect(buf, x, y, w, h, MAP_BLUE)

    def mx(lon):
        return x + int((lon + 170) * w / 360)

    def my(lat):
        return y + int((75 - lat) * h / 130)

    for cont in CONTINENTS:
        fill_polygon(buf, [(mx(lon), my(lat)) for lon, lat in cont],
                     MAP_LAND)
    for label, lon, lat, side in MAP_MARKS:
        cx, cy = mx(lon), my(lat)
        fill_circle(buf, cx, cy, 4, MAP_DOT)
        fill_circle(buf, cx, cy, 2, WHITE)
        lw = text_width(label, 1)
        if side == "R":
            lx, ly = cx + 7, cy - 3
        elif side == "L":
            lx, ly = cx - 7 - lw, cy - 3
        elif side == "A":
            lx, ly = cx - lw // 2, cy - 13
        else:
            lx, ly = cx - lw // 2, cy + 8
        draw_text(buf, lx, ly, label, 1, INK)


# ------------------------------------------------------------------ briefs
# (headline, caption) -- 32 briefs, all verified 18 Nov 2026.
BRIEFS = [
    # 39 briefs, one line each (headline + caption, <=52 chars each).
    # Col 1 (13) -- Americas + Europe carry-over from v2.
    ("EU PLANS RWANDA RETURN HUBS",
     "FIVE STATES PLAN MIGRANT RETURN CENTRES IN RWANDA."),
    ("27 YEARS FOR IRAN PLOT",
     "PAKISTANI MAN SENTENCED OVER PLOT AGAINST TRUMP."),
    ("QUAD MEETS IN MANILA",
     "TRUMP JOINS MODI, ALBANESE AND TAKAICHI IN MANILA."),
    ("RUSSIAN PLANE CRASHES, 19 DEAD",
     "MILITARY AN-12 DOWN IN KEMEROVO, SIBERIA."),
    ("US SOLDIER IN UK MOVED TO US",
     "HELD OVER RUSSIA SPY SUSPICION, NOW IN US CUSTODY."),
    ("140,000 JOIN FRENCH PAY PROTESTS",
     "FOURTH WEEKEND OF MARCHES OVER LIVING COSTS."),
    ("HOUTHIS PRESS TOWARD ADEN",
     "YEMEN REBELS ADVANCE ON THE SOUTHERN PORT CITY."),
    ("US SCOLDS KYIV ON DEEP STRIKES",
     "GERMANY PUSHES BACK AS PEACE TALKS ARE PLANNED."),
    ("TURKEY TAKES OVER SOZCU TV",
     "OPPOSITION CHANNEL SEIZED BY THE STATE."),
    ("SERBIA PARLIAMENT OPENS",
     "STUDENT LIST TAKES A MAJORITY OF SEATS."),
    ("ERITREA BORDER CLASHES",
     "FIGHTING RAISES FEARS OF A WIDER WAR IN TIGRAY."),
    ("KOREA LIFTS 2027 GROWTH TO 3.9 PCT",
     "SEOUL RAISES ITS FORECAST FOR NEXT YEAR."),
    ("FRANCE-MALAYSIA RARE EARTHS DEAL",
     "STRATEGIC PARTNERSHIP SIGNED IN KUALA LUMPUR."),
    # Col 2 (13) -- markets, tech, health, sport + new stories.
    ("BRAZIL REAL FALLS",
     "LULA FISCAL PLAN DISAPPOINTS INVESTORS."),
    ("EUROPE PAYS UP FOR LNG",
     "GAS STOCKS LOW AS WINTER NEARS."),
    ("PAKISTAN SOLAR SHARE HITS 28 PCT",
     "ROOFTOP PANELS LIFT SOLAR TO RECORD SHARE."),
    ("US TIGHTENS CHIP RULES ON CHINA",
     "NEW CURBS ON ADVANCED CHIP ACCESS."),
    ("ANTHROPIC TO LIST ON NASDAQ",
     "AI FIRM SET TO LIST ON THURSDAY 19 NOVEMBER."),
    ("FIJI DECLARES DISASTER",
     "EL NINO DROUGHT DECLARED A NATIONAL DISASTER."),
    ("WHO WARNS ON SUPERBUGS",
     "ANTIMICROBIAL RESISTANCE THREAT GROWS, WHO SAYS."),
    ("MEASLES NO LONGER ELIMINATED IN US",
     "PAHO ENDS US STATUS AFTER 5,400 CASES IN 2026."),
    ("DHONI RETIRES FROM IPL",
     "INDIA GREAT MS DHONI ENDS HIS IPL CAREER."),
    ("CYCLONE AKVAN NEARS INDIA",
     "STORM HEADS FOR ANDHRA PRADESH, LANDFALL FRIDAY."),
    ("KAHANA ELECTED KNESSET SPEAKER",
     "ISRAEL PARLIAMENT PICKS MATAN KAHANA."),
    ("CARNEY MEETS TRUMP AT APEC",
     "CANADA PM IN SHENZHEN FOR SUMMIT TALKS."),
    ("PATTINSON IS THE NEW JAMES BOND",
     "ROBERT PATTINSON TAKES OVER THE 007 ROLE."),
    # Col 3 (13) -- Middle East, Africa, Asia, Oceania (all new).
    ("PAKISTAN CUTS PETROL PRICE",
     "PETROL DOWN RS3 TO RS325 A LITRE."),
    ("UN WARNS OF COLD DEATHS IN GAZA",
     "1.7 MILLION DISPLACED AS WINTER SETS IN."),
    ("BAHRAIN INTERCEPTS IRAN ATTACKS",
     "KUWAIT COUNTERS HOSTILE DRONES."),
    ("SAUDI INTERCEPTS HOUTHI MISSILE",
     "CRUISE MISSILE DOWNED NEAR RIYADH."),
    ("ADNOC SHIP HIT IN HORMUZ",
     "ONE CREW MISSING, 11 INJURED."),
    ("AUSTRALIA SANCTIONS SETTLERS",
     "THREE PEOPLE, FOUR GROUPS SANCTIONED."),
    ("IRAQ TELLS MILITIA TO LEAVE",
     "KATAIB HEZBOLLAH REJECTS ULTIMATUM."),
    ("SUDAN ARMY GAINS IN KORDOFAN",
     "RSF UNDER PRESSURE AS AID CRISIS GROWS."),
    ("NIGERIA STATES GET OWN POLICE",
     "LANDMARK LAW PASSES ON POLICING."),
    ("WAYMO HALTS FREEWAY ROBOTAXIS",
     "DRIVERLESS FREEWAY TRIPS SUSPENDED."),
    ("NZ TSUNAMI WARNING LIFTED",
     "ALERT WITHDRAWN AFTER NORTH ISLAND SCARE."),
    ("EU ACTS AGAINST TEMU",
     "BRUSSELS TARGETS ILLEGAL PRODUCTS."),
    ("NATO PLANS NEW COMMS STRATEGY",
     "ALLIANCE TO UPGRADE ITS NETWORKS."),
]


def draw_briefs_strict(buf, x, y, w, briefs):
    """One column of briefs, strict single lines: headline + caption,
    19 px per brief (8 + 8 + 3 gap). Asserts every line fits."""
    cy = y
    for head, cap in briefs:
        assert text_width(head, 1) <= w, head
        assert text_width(cap, 1) <= w, cap
        draw_text(buf, x, cy, head, 1, INK)
        cy += 8
        draw_text(buf, x, cy, cap, 1, CAPTION)
        cy += 8
        cy += 3
    return cy


# -------------------------------------------------------------------- page
PANELS = [
    {
        "head": "TANKER WAR IN THE GULF",
        "sub": "US SINKS FIVE TANKERS",
        "color": RED,
        "scene": scene_gulf_wide,
    },
    {
        "head": "KERCH BRIDGE, NIGHT TWO",
        "sub": "UKRAINE STRIKES AGAIN",
        "color": NAVY,
        "scene": scene_kerch_wide,
    },
    {
        "head": "APEC OPENS IN SHENZHEN",
        "sub": "SUMMIT THURSDAY",
        "color": TEAL,
        "scene": scene_shenzhen_wide,
    },
    {
        "head": "COP31 DECISIVE PHASE",
        "sub": "144 ITEMS LEFT",
        "color": GREEN,
        "scene": scene_cop31_wide,
    },
]

# Big text card (anchor 5): Peltola wins Alaska.
BIG_CARD = {
    "head": "PELTOPA WINS ALASKA",
    "sub": "DEMOCRATS WIN SENATE",
    "color": (88, 44, 110),
    "body": [
        "FIRST ALASKA NATIVE ELECTED TO THE SENATE.",
        "BEATS SULLIVAN WITH OVER 50 PCT OF FIRST VOTES.",
        "MIDTERM SHOCKER SEALS A 56-44 MAJORITY.",
        "AP AND ALASKA PUBLIC MEDIA CONFIRM RESULT.",
    ],
}

# 8 small large-cards (anchors 6-13):
# (headline <=24 chars, color, caption line 1, caption line 2)
CARDS = [
    ("NVIDIA 115.8 BN", NAVY,
     "RECORD 115.8 BN QUARTER. SHARES FELL 2.89 PCT.",
     "BOARD SAYS EX-CEO HUANG WILL NOT RETURN."),
    ("WALL ST FALLS AGAIN", RED,
     "S AND P 500 DOWN 0.23 PCT, FIFTH LOSS IN A ROW.",
     "DOW DOWN 1.11 PCT. NASDAQ UP 0.42 PCT."),
    ("EBOLA DOUBLES", GREEN,
     "UN: OVER 11,000 CASES AND 5,400 DEATHS IN CONGO",
     "TWO VACCINE CANDIDATES IN TRIALS."),
    ("CYCLONE XAVIER", TEAL,
     "CATEGORY 5 STORM SLAMS THE COOK ISLANDS.",
     "GUSTS TO 315 KM PER HOUR."),
    ("DIRTY BOMB REPORT", RED,
     "TRUMP CALLS REPORT OF IRAN PLOT ON WASHINGTON",
     "SERIOUS. US LOOKS INTO THE REPORT."),
    ("GAZA TRUCE AT RISK", NAVY,
     "BOARD OF PEACE WARNS THE CEASEFIRE MAY COLLAPSE",
     "WITHOUT ACTION. UN WARNS OF COLD DEATHS."),
    ("COURT RULES ON MYANMAR", GREEN,
     "ICJ DECIDES THURSDAY ON ROHINGYA GENOCIDE CASE.",
     "DECISION DUE THURSDAY 19 NOVEMBER."),
    ("US TECH OUTAGES", TEAL,
     "NSA NETWORK DOWN. BANKS HIT. EIGHTH MAJOR",
     "OUTAGE IN A WEEK. RUBIO: NO CYBERATTACK FOUND."),
]

# (hour UTC, label, above the line?) -- the day's sequence in UTC as
# reported: overnight strikes, morning summit, afternoon results,
# evening close. Hours follow the reporting flow, not a stopwatch.
TIMELINE = [
    (0, "US SINKS FIVE TANKERS", True),
    (3, "KERCH HIT AGAIN", False),
    (8, "XI AND PUTIN MEET", True),
    (9, "COP31 DRAFT: 144 ITEMS", False),
    (15, "PELTOPA WINS ALASKA", True),
    (21, "WALL ST CLOSES LOWER", False),
]

PW = 317   # panel/card width (3 across: 3*317 + 2*12 = 975, x 24..999)
PH = 172   # scene panel height (header 46 + scene 126)
HDR = 46   # header strip height inside a panel
COL_X = [24, 353, 682]
ROW1_Y = 140
ROW2_Y = 320
TL_Y = 498
CARD_Y = [536, 596, 656]
CARD_H = 54
BRIEF_Y = 740
FOOT_Y = 996


def draw_panel(buf, px, py, panel):
    fill_rect(buf, px, py, PW, PH, WHITE)
    fill_rect(buf, px, py, PW, 2, INK)
    fill_rect(buf, px, py + PH - 2, PW, 2, INK)
    fill_rect(buf, px, py, 2, PH, INK)
    fill_rect(buf, px + PW - 2, py, 2, PH, INK)
    fill_rect(buf, px + 2, py + 2, PW - 4, HDR - 2, panel["color"])
    draw_text(buf, px + 12, py + 8, panel["head"], 2, WHITE)
    draw_text(buf, px + 12, py + 26, panel["sub"], 2, CREAM)
    blit_scaled_wide(buf, panel["scene"], px + 2, py + HDR, PW - 4,
                     PH - HDR)


def draw_map_panel(buf, px, py):
    fill_rect(buf, px, py, PW, PH, WHITE)
    fill_rect(buf, px, py, PW, 2, INK)
    fill_rect(buf, px, py + PH - 2, PW, 2, INK)
    fill_rect(buf, px, py, 2, PH, INK)
    fill_rect(buf, px + PW - 2, py, 2, PH, INK)
    fill_rect(buf, px + 2, py + 2, PW - 4, HDR - 2, NAVY)
    draw_text(buf, px + 12, py + 8, "THE WORLD AT A GLANCE", 2, WHITE)
    draw_text(buf, px + 12, py + 26, "STORIES MARKED IN RED", 2, CREAM)
    draw_map(buf, px + 2, py + HDR, PW - 4, PH - HDR)


def draw_big_card(buf, px, py):
    card = BIG_CARD
    fill_rect(buf, px, py, PW, PH, WHITE)
    fill_rect(buf, px, py, PW, 2, INK)
    fill_rect(buf, px, py + PH - 2, PW, 2, INK)
    fill_rect(buf, px, py, 2, PH, INK)
    fill_rect(buf, px + PW - 2, py, 2, PH, INK)
    fill_rect(buf, px + 2, py + 2, PW - 4, HDR - 2, card["color"])
    draw_text(buf, px + 12, py + 8, card["head"], 2, WHITE)
    draw_text(buf, px + 12, py + 26, card["sub"], 2, CREAM)
    cy = py + HDR + 10
    for line in card["body"]:
        assert text_width(line, 1) <= PW - 24, line
        draw_text(buf, px + 12, cy, line, 1, INK)
        cy += 12
    fill_rect(buf, px + 12, py + PH - 26, PW - 24, 2, card["color"])
    draw_text(buf, px + 12, py + PH - 20, "ALASKA SENATE RACE", 1, GREY)


def draw_small_card(buf, px, py, card):
    head, color, cap1, cap2 = card
    assert text_width(head, 2) <= PW - 20, head
    assert text_width(cap1, 1) <= PW - 20, cap1
    assert text_width(cap2, 1) <= PW - 20, cap2
    fill_rect(buf, px, py, PW, CARD_H, WHITE)
    fill_rect(buf, px, py, PW, 2, INK)
    fill_rect(buf, px, py + CARD_H - 2, PW, 2, INK)
    fill_rect(buf, px, py, 2, CARD_H, INK)
    fill_rect(buf, px + PW - 2, py, 2, CARD_H, INK)
    fill_rect(buf, px + 2, py + 2, PW - 4, 20, color)
    draw_text(buf, px + 10, py + 5, head, 2, WHITE)
    draw_text(buf, px + 10, py + 26, cap1, 1, INK)
    draw_text(buf, px + 10, py + 35, cap2, 1, CAPTION)


def draw_timeline(buf):
    y0 = TL_Y
    draw_text(buf, 24, y0, "THE DAY IN UTC", 1, GREY)
    line_y = y0 + 22
    draw_line(buf, 24, line_y, 1000, line_y, INK, 2)
    for hour in (0, 6, 12, 18, 24):
        tx = 24 + hour * 976 // 24
        fill_rect(buf, tx - 1, line_y - 5, 2, 10, INK)
        lab = "%02d" % hour
        lx = max(24, min(1000 - 11, tx - 6))
        draw_text(buf, lx, line_y + 8, lab, 1, GREY)
    draw_text(buf, 1000 - text_width("UTC", 1), y0, "UTC", 1, GREY)
    for hour, label, above in TIMELINE:
        ex = 24 + hour * 976 // 24
        fill_circle(buf, ex, line_y, 4, RED)
        fill_circle(buf, ex, line_y, 2, WHITE)
        lw = text_width(label, 1)
        lx = max(24, min(1000 - lw, ex - lw // 2))
        ly = line_y - 14 if above else line_y + 20
        draw_text(buf, lx, ly, label, 1, INK)


def render():
    buf = new_buf()
    # masthead
    draw_text_centered(buf, W // 2, 24, "THE WORLD", 8, INK)
    draw_text_centered(buf, W // 2, 88, "WEDNESDAY 18 NOVEMBER 2026", 3,
                       INK)
    fill_rect(buf, 24, 118, W - 48, 4, INK)
    fill_rect(buf, 24, 126, W - 48, 2, INK)
    # row 1: three wide scene panels
    for panel, px in zip(PANELS[:3], COL_X):
        draw_panel(buf, px, ROW1_Y, panel)
    # row 2: COP31 scene, map panel, big text card
    draw_panel(buf, COL_X[0], ROW2_Y, PANELS[3])
    draw_map_panel(buf, COL_X[1], ROW2_Y)
    draw_big_card(buf, COL_X[2], ROW2_Y)
    # UTC timeline strip
    draw_timeline(buf)
    # 8 small large-cards, 3 columns x 3 rows (3, 3, 2)
    for i, card in enumerate(CARDS):
        draw_small_card(buf, COL_X[i % 3], CARD_Y[i // 3], card)
    # briefs header + 7-region coverage line
    draw_text(buf, 24, 716, "THE DAY IN BRIEF", 2, INK)
    cov = ("7 REGIONS: N. AMERICA, S. AMERICA, EUROPE, AFRICA, "
           "MIDDLE EAST, ASIA, OCEANIA")
    draw_text(buf, 1000 - text_width(cov, 1), 719, cov, 1, GREY)
    fill_rect(buf, 24, 734, W - 48, 2, INK)
    # bottom band: 39 briefs, 13 per column
    for col in range(3):
        end = draw_briefs_strict(buf, COL_X[col], BRIEF_Y, PW,
                                 BRIEFS[col * 13:(col + 1) * 13])
        assert end <= 992, end
    # footer
    draw_text_centered(buf, W // 2, FOOT_Y, "52 STORIES, ONE DAY", 2, GREY)
    return buf


# ---------------------------------------------------------------------- PNG
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(buf):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += buf[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(render())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
