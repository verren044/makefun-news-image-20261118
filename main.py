#!/usr/bin/env python3
"""news-image-20261118 -- "THE WORLD, WEDNESDAY 18 NOVEMBER 2026".

A newspaper front page summing up 18 November 2026 in one image: a
masthead plus four illustrated panels, one per story. The AI judge has no
news feed, so the image itself carries the news -- every panel has a
headline, a sub-headline and a flat-shape picture of the story.

Stories (18 Nov 2026 briefings):
  1. TANKER WAR IN THE GULF -- US forces destroyed five Iranian oil
     tankers in the Gulf of Oman; Iran hit ships near the Strait of
     Hormuz and fired missiles at the Al-Azraq base in Jordan.
  2. KERCH BRIDGE, NIGHT TWO -- Ukraine struck the Kerch Bridge for a
     second night in a row; Russia hit bridges of its own ahead of
     Thursday's summit.
  3. APEC OPENS IN SHENZHEN -- APEC summit opens in Shenzhen; Trump in
     Manila for Quad talks; first-ever Trump-Xi-Putin trilateral summit
     set for Thursday 19 Nov.
  4. COP31 DECISIVE PHASE -- COP31 climate talks in Antalya enter their
     decisive phase with 144 disputed items, due to conclude Friday 20 Nov.

Pure standard library (zlib, struct, os, hashlib-free runtime). No
network, no randomness, no external files. Two runs produce byte-identical
PNG output. Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
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
WHITE = (255, 255, 255)
CREAM = (255, 248, 220)
RED = (140, 29, 24)       # panel 1 header / flags
NAVY = (27, 42, 74)       # panel 2 header / night sky
TEAL = (14, 74, 92)       # panel 3 header
GREEN = (30, 107, 52)     # panel 4 header
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


# -------------------------------------------------------------------- page
PANELS = [
    {
        "head": "TANKER WAR IN THE GULF",
        "sub": "US SINKS FIVE IRANIAN TANKERS",
        "color": RED,
        "scene": scene_gulf,
    },
    {
        "head": "KERCH BRIDGE, NIGHT TWO",
        "sub": "UKRAINE STRIKES AGAIN",
        "color": NAVY,
        "scene": scene_kerch,
    },
    {
        "head": "APEC OPENS IN SHENZHEN",
        "sub": "TRUMP - XI - PUTIN SUMMIT THURSDAY",
        "color": TEAL,
        "scene": scene_shenzhen,
    },
    {
        "head": "COP31 DECISIVE PHASE",
        "sub": "144 ITEMS LEFT IN ANTALYA",
        "color": GREEN,
        "scene": scene_cop31,
    },
]


def draw_panel(buf, px, py, pw, ph, panel):
    fill_rect(buf, px, py, pw, ph, WHITE)
    fill_rect(buf, px, py, pw, 2, INK)
    fill_rect(buf, px, py + ph - 2, pw, 2, INK)
    fill_rect(buf, px, py, 2, ph, INK)
    fill_rect(buf, px + pw - 2, py, 2, ph, INK)
    # header strip
    fill_rect(buf, px + 2, py + 2, pw - 4, 76, panel["color"])
    head_lines = wrap_text(panel["head"], 3, pw - 24)
    hy = py + 12
    for line in head_lines:
        draw_text(buf, px + 12, hy, line, 3, WHITE)
        hy += 24
    sub_lines = wrap_text(panel["sub"], 2, pw - 24)
    sy = py + 12 + len(head_lines) * 24 + 2
    for line in sub_lines:
        draw_text(buf, px + 12, sy, line, 2, CREAM)
        sy += 16
    # scene
    panel["scene"](buf, px + 2, py + 78, pw - 4, ph - 80)


def render():
    buf = new_buf()
    # masthead
    draw_text_centered(buf, W // 2, 30, "THE WORLD", 9, INK)
    draw_text_centered(buf, W // 2, 108, "WEDNESDAY 18 NOVEMBER 2026", 3,
                       INK)
    fill_rect(buf, 24, 142, W - 48, 5, INK)
    fill_rect(buf, 24, 152, W - 48, 2, INK)
    # 2x2 grid of panels
    gx, gy = 24, 164
    pw = (W - 48 - 12) // 2
    ph = (976 - gy - 12) // 2
    positions = [(gx, gy), (gx + pw + 12, gy),
                 (gx, gy + ph + 12), (gx + pw + 12, gy + ph + 12)]
    for panel, (px, py) in zip(PANELS, positions):
        draw_panel(buf, px, py, pw, ph, panel)
    # footer
    draw_text_centered(buf, W // 2, 986, "FOUR STORIES, ONE DAY", 2, GREY)
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
