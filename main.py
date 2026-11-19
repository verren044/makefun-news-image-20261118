"""THE WORLD, WEDNESDAY 18 NOVEMBER 2026 - the day's world news in one image.

Pure stdlib Python (math, os, struct, zlib). Deterministic: no network,
no randomness, no clock. Renders output.png (1024x1024) in the cwd.
52 stories: 13 anchors (4 illustrated scenes, 1 big card, 8 small cards)
+ 39 briefs, plus a world map and a UTC timeline.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (244, 238, 222)
PAPER2 = (250, 246, 232)
INK = (22, 22, 22)
GREY = (110, 106, 94)
RED = (176, 32, 32)
DARKRED = (140, 20, 20)
BLUE = (38, 78, 150)
DARKBLUE = (24, 44, 96)
SKY = (168, 200, 232)
PALESKY = (208, 224, 240)
SEA = (28, 68, 128)
DEEPSEA = (18, 48, 96)
GREEN = (46, 120, 66)
LAND = (198, 188, 148)
GOLD = (212, 160, 40)
ORANGE = (232, 110, 20)
YELLOW = (240, 200, 60)
WHITE = (255, 255, 255)
BLACK = (8, 8, 8)
NIGHT = (16, 24, 56)
MOON = (235, 232, 210)
SMOKE = (150, 148, 142)

FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", "     ", "     ", "     ", "     ", "     "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
}

ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ., -':!?/")


def check_text(s):
    bad = [c for c in s if c not in ALLOWED]
    if bad:
        raise ValueError("bad chars %r in %r" % (bad, s))


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return (self.buf[i], self.buf[i + 1], self.buf[i + 2])

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def border(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / float(y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def starburst(self, cx, cy, r, c, n=16):
        for i in range(n):
            a = 2.0 * math.pi * i / n
            self.line(cx, cy, cx + int(math.cos(a) * r), cy + int(math.sin(a) * r), c)

    def text(self, x, y, s, scale, c):
        check_text(s)
        for i, ch in enumerate(s):
            g = FONT[ch]
            cx = x + i * 6 * scale
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "#":
                        self.fill_rect(cx + col * scale, y + r * scale, scale, scale, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)


def panel(cv, x, y, w, h, title, head=INK):
    cv.fill_rect(x, y, w, h, PAPER2)
    cv.border(x, y, w, h, INK)
    cv.fill_rect(x + 1, y + 1, w - 2, 18, head)
    cv.text(x + 7, y + 6, title, 1, WHITE)
    return (x + 1, y + 20, w - 2, h - 21)


def scene_gulf(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, PALESKY)
    cv.fill_circle(x + w - 30, y + 22, 14, GOLD)
    cv.fill_rect(x, y + int(h * 0.55), w, h - int(h * 0.55), SEA)
    cv.fill_rect(x, y + int(h * 0.55), w, 2, WHITE)
    cv.fill_rect(x + 12, y + int(h * 0.62), w - 24, 12, BLACK)
    cv.fill_rect(x + w // 2 - 14, y + int(h * 0.62) - 12, 28, 12, WHITE)
    cv.fill_rect(x + w // 2 + 16, y + int(h * 0.62) - 18, 6, 18, RED)
    cv.starburst(x + int(w * 0.72), y + int(h * 0.38), 26, ORANGE)
    cv.starburst(x + int(w * 0.72), y + int(h * 0.38), 14, YELLOW)
    cv.fill_circle(x + int(w * 0.72), y + int(h * 0.38), 7, YELLOW)
    cv.fill_circle(x + int(w * 0.30), y + int(h * 0.30), 9, SMOKE)
    cv.fill_circle(x + int(w * 0.36), y + int(h * 0.24), 12, SMOKE)
    cv.fill_circle(x + int(w * 0.42), y + int(h * 0.30), 8, SMOKE)


def scene_kerch(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, NIGHT)
    for sx, sy in ((12, 10), (30, 26), (55, 8), (80, 20), (110, 12), (140, 28),
                   (170, 8), (200, 18), (40, 44), (150, 40), (95, 34), (210, 34)):
        cv.set(x + sx, y + sy, WHITE)
    cv.fill_circle(x + w - 32, y + 26, 13, MOON)
    cv.fill_circle(x + w - 36, y + 22, 11, NIGHT)
    cv.fill_rect(x, y + int(h * 0.68), w, h - int(h * 0.68), DEEPSEA)
    cv.line(x, y + int(h * 0.62), x + w, y + int(h * 0.62), WHITE)
    for tx in (int(w * 0.25), int(w * 0.70)):
        cv.line(x + tx, y + int(h * 0.62), x + tx, y + int(h * 0.34), WHITE)
        cv.line(x + tx, y + int(h * 0.34), x + w // 2, y + int(h * 0.62), WHITE)
    cv.fill_circle(x + w // 2, y + int(h * 0.56), 10, ORANGE)
    cv.fill_circle(x + w // 2, y + int(h * 0.56), 5, YELLOW)
    cv.starburst(x + w // 2, y + int(h * 0.56), 18, ORANGE, 10)
    cv.fill_circle(x + w // 2 + 26, y + int(h * 0.50), 6, SMOKE)
    cv.fill_circle(x + w // 2 + 34, y + int(h * 0.44), 8, SMOKE)


def scene_shenzhen(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, PALESKY)
    cv.fill_circle(x + 26, y + 20, 12, GOLD)
    base = y + h
    towers = ((0, 0.55), (0.14, 0.78), (0.28, 0.62), (0.42, 0.92),
              (0.56, 0.70), (0.70, 0.85), (0.84, 0.60))
    for fx, fh in towers:
        tw = int(w * 0.13)
        th = int(h * fh)
        cv.fill_rect(x + int(w * fx), base - th, tw, th, DARKBLUE)
        for wy in range(base - th + 8, base - 6, 12):
            for wx in range(x + int(w * fx) + 4, x + int(w * fx) + tw - 4, 8):
                cv.set(wx, wy, GOLD)
    cv.fill_rect(x, base - int(h * 0.92) - 6, 3, int(h * 0.92) + 6, INK)
    cv.fill_rect(x, y + int(h * 0.06), w, 2, INK)
    flags = ((0.30, RED, None), (0.50, None, "US"), (0.72, None, "RU"))
    for fx, solid, kind in flags:
        px = x + int(w * fx)
        cv.line(px, y + int(h * 0.10), px, y + int(h * 0.38), INK)
        if kind is None:
            cv.fill_rect(px + 1, y + int(h * 0.10), 20, 12, solid)
        elif kind == "US":
            for i in range(4):
                cv.fill_rect(px + 1, y + int(h * 0.10) + i * 3, 20, 2,
                             RED if i % 2 == 0 else WHITE)
            cv.fill_rect(px + 1, y + int(h * 0.10), 9, 6, BLUE)
        else:
            cv.fill_rect(px + 1, y + int(h * 0.10), 20, 4, WHITE)
            cv.fill_rect(px + 1, y + int(h * 0.10) + 4, 20, 4, BLUE)
            cv.fill_rect(px + 1, y + int(h * 0.10) + 8, 20, 4, RED)


def scene_cop31(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (188, 214, 234))
    cv.fill_circle(x + 24, y + 20, 12, GOLD)
    cv.fill_poly(((x, y + h), (x, y + int(h * 0.62)),
                  (x + int(w * 0.45), y + int(h * 0.48)),
                  (x + int(w * 0.75), y + int(h * 0.66)), (x + w, y + h)), GREEN)
    cv.fill_poly(((x, y + h), (x + int(w * 0.35), y + int(h * 0.70)),
                  (x + int(w * 0.70), y + int(h * 0.58)), (x + w, y + h)), (34, 96, 52))
    gx, gy, gr = x + int(w * 0.68), y + int(h * 0.30), 26
    cv.fill_circle(gx, gy, gr, SEA)
    cv.fill_circle(gx - 8, gy - 6, 7, GREEN)
    cv.fill_circle(gx + 9, gy + 7, 6, GREEN)
    cv.fill_circle(gx + 4, gy - 12, 5, GREEN)
    cv.fill_circle(x + w - 26, y + 26, 19, RED)
    cv.text_c(x + w - 26, y + 18, "144", 2, WHITE)
    cv.text_c(x + w - 26, y + 34, "ITEMS", 1, WHITE)


CONTINENTS = [
    [(-170, 70), (-140, 70), (-120, 70), (-95, 70), (-80, 70), (-75, 60),
     (-80, 45), (-75, 35), (-80, 25), (-90, 20), (-95, 15), (-105, 20),
     (-115, 30), (-125, 40), (-125, 50), (-140, 60), (-165, 60)],
    [(-80, 10), (-75, 0), (-70, -10), (-60, -20), (-55, -30), (-65, -45),
     (-70, -55), (-75, -40), (-75, -20), (-80, -5)],
    [(-10, 36), (0, 40), (10, 44), (20, 45), (30, 46), (30, 55), (20, 60),
     (10, 60), (5, 58), (0, 50), (-5, 45), (-10, 40)],
    [(-15, 35), (-5, 35), (10, 37), (20, 32), (30, 30), (35, 25), (40, 15),
     (50, 10), (45, 0), (40, -10), (35, -20), (30, -30), (20, -35),
     (15, -25), (10, -15), (5, -5), (0, 5), (-10, 15)],
    [(40, 70), (60, 70), (80, 70), (100, 75), (120, 75), (140, 70),
     (160, 65), (170, 60), (160, 50), (150, 45), (140, 40), (130, 35),
     (120, 30), (110, 20), (100, 10), (95, 5), (90, 15), (80, 20),
     (70, 25), (60, 25), (50, 30), (40, 40)],
    [(115, -20), (125, -15), (135, -12), (145, -15), (150, -25),
     (145, -35), (135, -38), (125, -35), (115, -30)],
]

MARKERS = [
    (-150, 65, "ALASKA"), (55, 26, "GULF"), (36, 45, "KERCH"),
    (114, 22, "SHENZHEN"), (30, 37, "ANTALYA"), (15, -2, "CONGO"),
    (178, -17, "FIJI"), (-160, -21, "COOK IS."),
]


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (172, 206, 236))
    for poly in CONTINENTS:
        pts = []
        for lon, lat in poly:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((90 - lat) / 180.0 * h)
            pts.append((px, py))
        cv.fill_poly(pts, LAND)
    for i, (lon, lat, name) in enumerate(MARKERS, 1):
        px = x + int((lon + 180) / 360.0 * w)
        py = y + int((90 - lat) / 180.0 * h)
        cv.fill_circle(px, py, 5, RED)
        cv.fill_circle(px, py, 2, WHITE)
        cv.text(px + 7, py - 3, str(i), 1, RED)
        cv.text(px + 7, py + 5, name, 1, INK)


CARDS = [
    ("NVIDIA 115.8 BN", ["DATA CENTRE SALES BEAT FORECASTS.",
                          "BOARD RULES OUT HUANG RETURN."]),
    ("WALL ST FALLS AGAIN", ["STOCKS DROP FOR A SECOND DAY",
                             "AS YIELDS RISE."]),
    ("EBOLA DOUBLES", ["CASES DOUBLE IN CONGO IN THREE MONTHS.",
                        "TWO VACCINE CANDIDATES IN TRIALS."]),
    ("CYCLONE XAVIER", ["FIJI BRACES AS STORM STRENGTHENS",
                         "OFFSHORE."]),
    ("DIRTY BOMB REPORT", ["CAPITALS ALARMED BY NEW",
                           "INTELLIGENCE."]),
    ("GAZA TRUCE AT RISK", ["BOARD OF PEACE WARNS TRUCE",
                            "COULD COLLAPSE."]),
    ("COURT RULES ON MYANMAR", ["ASEAN TERMS SET FOR THE",
                                "GENERALS RETURN."]),
    ("US TECH OUTAGES", ["CLOUD SERVICES DOWN ACROSS",
                         "THE STATES."]),
]

TIMELINE = [
    ("00", "KERCH BRIDGE STRUCK"), ("03", "GULF TANKERS SUNK"),
    ("08", "APEC OPENS"), ("09", "COP31 DECISIVE PHASE"),
    ("15", "WALL ST FALLS"), ("21", "GAZA TRUCE WARNING"),
]

BRIEFS = [
    ("KAHANA ELECTED KNESSET SPEAKER", "NEW SPEAKER TAKES THE CHAIR IN JERUSALEM"),
    ("CARNEY MEETS TRUMP AT APEC", "CANADA AND US TALK TRADE IN SHENZHEN"),
    ("PATTINSON IS THE NEW JAMES BOND", "007 ROLE GOES TO THE BATMAN STAR"),
    ("PAKISTAN CUTS PETROL PRICE", "PETROL DOWN RS3 TO RS325 A LITRE"),
    ("UN WARNS OF COLD DEATHS IN GAZA", "1.7 MILLION DISPLACED FACE WINTER"),
    ("BAHRAIN INTERCEPTS IRAN ATTACKS", "GULF DEFENCES STOP DRONES OVERNIGHT"),
    ("SAUDI INTERCEPTS HOUTHI MISSILE", "RIYADH SAYS NO DAMAGE FROM STRIKE"),
    ("ADNOC SHIP HIT IN HORMUZ", "TANKER DAMAGED AS GULF SHIPPING HALTS"),
    ("AUSTRALIA SANCTIONS SETTLERS", "CANBERRA ACTS OVER WEST BANK VIOLENCE"),
    ("IRAQ TELLS MILITIA TO LEAVE", "BAGHDAD ORDERS GROUPS OUT OF CITIES"),
    ("SUDAN ARMY GAINS IN KORDOFAN", "KHARTOUM PUSHES BACK RSF ADVANCE"),
    ("NIGERIA STATES GET OWN POLICE", "ABUJA APPROVES STATE POLICE FORCES"),
    ("WAYMO HALTS FREEWAY ROBOTAXIS", "SELF DRIVING FLEET PULLED AFTER CRASH"),
    ("NZ TSUNAMI WARNING LIFTED", "ALL CLEAR AFTER PACIFIC QUAKE SCARE"),
    ("EU ACTS AGAINST TEMU", "BRUSSELS OPENS NEW PROBE INTO MARKETPLACE"),
    ("NATO PLANS NEW COMMS STRATEGY", "ALLIANCE REBUILDS SECURE NETWORKS"),
    ("XI AND PUTIN MEET IN SHENZHEN", "TRILATERAL WITH TRUMP SET FOR THURSDAY"),
    ("TRUMP LANDS IN SHENZHEN", "XI GREETS HIM AT THE AIRPORT"),
    ("LEE USES APEC TO DEEPEN TIES", "SEOUL AND BEIJING TALK TRADE"),
    ("RUSSIAN BOMBERS NEAR JAPAN", "TOKYO PROTESTS AIRSPACE VIOLATION CLAIM"),
    ("UKRAINE SEEKS MORE FIGHTERS", "KYIV ASKS ALLIES FOR JETS AND DEFENCES"),
    ("RUSSIA HITS KYIV BRIDGES", "KERCH SPAN FALLS AFTER SECOND STRIKE"),
    ("IRAN FIRES AT US SITES IN KUWAIT", "ALI AL SALEM BASE TARGETED"),
    ("THIRD US CARRIER REACHES GULF", "WASHINGTON BOLSTERS NAVAL PRESENCE"),
    ("ARAMCO TOWER DAMAGED IN RIYADH", "DEBRIS FROM ATTACK HITS SKYSCRAPER"),
    ("HERZOG TAPS EISENKOT TO LEAD", "ISRAEL PRESIDENT NAMES NEW PM CHOICE"),
    ("ASEAN SETS TERMS FOR MYANMAR", "BLOC LAYS OUT PATH BACK TO THE TABLE"),
    ("RUSSIA AND UKRAINE AGREE SWAP", "LARGEST POW EXCHANGE SINCE 2022"),
    ("GERMANY FUNDS PATRIOT MISSILES", "BERLIN PUTS 300M INTO UKRAINE DEFENCE"),
    ("TURKEY TAKES OPPOSITION TV", "ANKARA SEIZES CONTROL OF BROADCASTER"),
    ("PAKISTAN EDGE INDIA IN THRILLER", "BLIND CRICKET ASIA CUP FINAL SEALED"),
    ("US JAILS MAN FOR 27 YEARS", "PLOT TO KILL TRUMP ENDS IN PRISON"),
    ("UN WARNS ON EU RETURN HUB PLAN", "RIGHTS RISKS SEEN IN RWANDA SCHEME"),
    ("LEONID METEORS PEAK OVERNIGHT", "ANNUAL SHOWER LIGHTS UP THE SKY"),
    ("TRAINS COLLIDE NEAR PRAGUE", "46 HURT, 4 CRITICAL AFTER CRASH"),
    ("POPE CALLS FOR LESS WAR", "PONTIFF SPEAKS AFTER US MIDTERMS"),
    ("STUDENTS MARCH IN BRUSSELS", "THOUSANDS MARK STUDENTS DAY"),
    ("DEUTSCHE BANK LEAK SURFACES", "FILES LINK OLIGARCHS AND EPSTEIN"),
    ("SENATOR DEMANDS CHIP ACTION", "US SEEKS LOOPHOLE FIX ON AI EXPORTS"),
]


def draw_small_card(cv, x, y, w, h, title, lines):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK)
    cv.fill_rect(x + 1, y + 1, w - 2, 14, RED)
    cv.text(x + 6, y + 4, title, 1, WHITE)
    cv.text(x + 6, y + 20, lines[0], 1, INK)
    cv.text(x + 6, y + 30, lines[1], 1, INK)


def png_bytes(buf, w, h):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, data):
        out = struct.pack(">I", len(data)) + t + data
        out += struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def render():
    cv = Canvas(W, H, PAPER)
    cv.text_c(W // 2, 12, "THE WORLD", 7, INK)
    cv.text_c(W // 2, 66, "WEDNESDAY 18 NOVEMBER 2026", 2, INK)
    cv.text_c(W // 2, 86, "TANKER WAR IN THE GULF. KERCH STRUCK AGAIN. APEC OPENS IN SHENZHEN.", 1, GREY)
    cv.fill_rect(24, 100, W - 48, 3, INK)

    scenes = (("GULF TANKER WAR", scene_gulf), ("KERCH BRIDGE", scene_kerch),
              ("APEC SHENZHEN", scene_shenzhen), ("COP31 ANTALYA", scene_cop31))
    for i, (title, fn) in enumerate(scenes):
        x = 24 + i * 246
        sx, sy, sw, sh = panel(cv, x, 112, 238, 172, title)
        fn(cv, sx, sy, sw, sh)

    mx, my, mw, mh = panel(cv, 24, 292, 500, 170, "WORLD MAP", DARKBLUE)
    draw_map(cv, mx, my, mw, mh)

    px, py, pw, ph = panel(cv, 532, 292, 232, 170, "PELTOLA WINS", RED)
    cv.text(px + 8, py + 10, "PELTOLA WINS", 2, INK)
    cv.text(px + 8, py + 28, "ALASKA", 2, INK)
    cv.text(px + 8, py + 52, "DEMOCRATS TAKE SENATE 56-44", 1, RED)
    cv.text(px + 8, py + 68, "MARY PELTOLA BEATS DAN SULLIVAN.", 1, INK)
    cv.text(px + 8, py + 79, "AP CALLS THE RACE FOR ALASKA.", 1, INK)
    cv.fill_rect(px + 8, py + 98, pw - 16, 2, INK)
    cv.text(px + 8, py + 108, "FIRST DEMOCRAT TO WIN THE SEAT", 1, GREY)
    cv.text(px + 8, py + 119, "IN 50 YEARS.", 1, GREY)

    nx, ny, nw, nh = panel(cv, 772, 292, 228, 170, "BY THE NUMBERS", INK)
    stats = [("144", "COP31 ITEMS DISPUTED"), ("56-44", "SENATE SPLIT"),
             ("115.8", "NVIDIA BN REVENUE"), ("5", "TANKERS SUNK")]
    for i, (num, lab) in enumerate(stats):
        yy = ny + 8 + i * 34
        cv.text(nx + 8, yy, num, 2, RED)
        cv.text(nx + 8 + cv.text_w(num, 2) + 10, yy + 4, lab, 1, INK)

    cv.text(24, 470, "THE DAY IN TIME", 1, INK)
    cv.fill_rect(24, 488, W - 48, 2, INK)
    for i, (hh, ev) in enumerate(TIMELINE):
        tx = 60 + i * 162
        cv.fill_rect(tx, 480, 2, 18, RED)
        cv.text_c(tx + 1, 500, hh, 1, RED)
        cv.text_c(tx + 1, 510, ev, 1, INK)

    for i, (title, lines) in enumerate(CARDS):
        row, col = divmod(i, 3)
        x = 24 + col * 328
        y = 536 + row * 60
        draw_small_card(cv, x, y, 320, 54, title, lines)

    cv.text(24, 724, "THE DAY IN BRIEF", 2, INK)
    cv.text(24, 744, "7 REGIONS: N. AMERICA, S. AMERICA, EUROPE, AFRICA, MIDDLE EAST, ASIA, OCEANIA", 1, GREY)
    for i, (head, cap) in enumerate(BRIEFS):
        if len(head) > 52 or len(cap) > 52:
            raise ValueError("brief too long: %r / %r" % (head, cap))
        col, row = divmod(i, 13)
        bx = 24 + col * 328
        by = 758 + row * 18
        cv.text(bx, by, head, 1, INK)
        cv.text(bx, by + 8, cap, 1, (70, 68, 60))
    cv.fill_rect(24, 996, W - 48, 1, INK)
    cv.text_c(W // 2, 1002, "52 STORIES, ONE DAY", 2, INK)
    return cv


def main():
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    if len(BRIEFS) != 39 or len(CARDS) != 8 or len(TIMELINE) != 6:
        raise ValueError("story counts wrong: %d briefs, %d cards, %d timeline"
                         % (len(BRIEFS), len(CARDS), len(TIMELINE)))
    cv = render()
    data = png_bytes(cv.buf, W, H)
    with open(out, "wb") as f:
        f.write(data)
    import hashlib
    print("wrote %s %d bytes sha256 %s" % (out, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
