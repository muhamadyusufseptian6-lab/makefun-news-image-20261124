#!/usr/bin/env python3
"""news-image-20261124: sum up Tuesday 24 November 2026 in one image.

Draws a 1024x1024 newspaper front page with six of the day's biggest
stories, using only the Python standard library. No network, no files
read, fully deterministic: two runs write byte-identical PNGs.

Stories (all as reported on 24 November 2026):
  1. Iran vows to defy the US naval blockade of the Strait of Hormuz.
  2. Ukraine says its sea drones sank the Russian corvette Merkury
     at Benghazi, Libya, and hit a second ship; Sparta II hit in
     the Baltic.
  3. COP31 climate talks in Antalya collapse with no deal and no
     fossil-fuel language.
  4. A candy-factory fire in Cikande, Banten, Indonesia kills 24,
     with about 30 missing.
  5. Game 1 of the World Chess Championship begins in Geneva:
     Gukesh vs Sindarov, both 20, the youngest final ever.
  6. Asian regulators step in to calm the AI-stock sell-off.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes: $MAKEFUN_OUTPUT_DIR/entry.png
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (20, 39, 61)
NAVY = (18, 50, 79)
GOLD = (201, 162, 39)
GREY = (110, 110, 105)
LIGHT_LINE = (205, 198, 184)
WHITE = (255, 255, 255)

ACCENTS = [
    (142, 43, 37),    # Hormuz: deep red
    (46, 74, 107),    # war at sea: slate blue
    (46, 107, 79),    # climate: green
    (180, 85, 31),    # factory fire: burnt orange
    (31, 92, 92),     # chess: teal
    (51, 62, 77),     # markets: charcoal
]

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits, written from scratch for this entry.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for ty in range(thickness):
                for tx in range(thickness):
                    self.set(x0 + tx, y0 + ty, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color, thickness=1):
        for a, b in zip(points, points[1:]):
            self.line(a[0], a[1], b[0], b[1], color, thickness)

    def fill_poly(self, points, color):
        """Scanline fill for a simple polygon given as [(x, y), ...]."""
        if not points:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, color)

    def circle(self, cx, cy, r, color):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r:
                    self.set(cx + x, cy + y, color)

    def ring(self, cx, cy, r, color, thickness=2):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = (x * x + y * y) ** 0.5
                if r - thickness < d <= r:
                    self.set(cx + x, cy + y, color)

    # ------------------------------------------------------------ text
    def draw_text(self, x, y, text, scale, color):
        # The bitmap font covers capitals only; render everything in
        # capitals so no character falls back to "?".
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale,
                            scale, scale, color,
                        )
            cx += 6 * scale
        return cx - x

    def draw_text_centered(self, y, text, scale, color):
        w = text_width(text, scale)
        self.draw_text((self.w - w) // 2, y, text, scale, color)


# ------------------------------------------------------------------- icons
# Each icon is drawn inside a 116x116 box at (x, y) on a story colour.

def icon_hormuz(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    # sea
    c.fill_rect(x, y + 78, 116, 38, (24, 68, 96))
    c.polyline([(x + 6, y + 86), (x + 30, y + 82), (x + 54, y + 86),
                (x + 78, y + 82), (x + 110, y + 86)], (140, 190, 220), 2)
    c.polyline([(x + 6, y + 98), (x + 30, y + 94), (x + 54, y + 98),
                (x + 78, y + 94), (x + 110, y + 98)], (140, 190, 220), 2)
    # tanker hull
    c.fill_poly([(x + 12, y + 62), (x + 104, y + 62), (x + 96, y + 80),
                 (x + 20, y + 80)], (30, 30, 34))
    # containers
    c.fill_rect(x + 22, y + 40, 18, 22, (201, 162, 39))
    c.fill_rect(x + 42, y + 40, 18, 22, (220, 220, 215))
    c.fill_rect(x + 62, y + 40, 18, 22, (178, 84, 52))
    # bridge tower
    c.fill_rect(x + 84, y + 30, 14, 32, (235, 235, 230))
    c.fill_rect(x + 87, y + 34, 8, 5, (18, 50, 79))
    # blockade chain: a row of white links across the top
    for lx in range(x + 10, x + 108, 12):
        c.ring(lx, y + 14, 4, (255, 255, 255), 2)


def icon_warship(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    c.fill_rect(x, y + 80, 116, 36, (20, 52, 74))
    c.polyline([(x + 6, y + 88), (x + 30, y + 84), (x + 54, y + 88),
                (x + 78, y + 84), (x + 110, y + 88)], (150, 180, 205), 2)
    # explosion starburst
    cx, cy = x + 58, y + 34
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 10, 26
        a = math.radians(ang)
        b = math.radians(ang + 15)
        c.fill_poly([(cx, cy),
                     (cx + int(r2 * math.cos(a)), cy + int(r2 * math.sin(a))),
                     (cx + int(r1 * math.cos(b)), cy + int(r1 * math.sin(b)))],
                    (240, 180, 40))
    c.circle(cx, cy, 9, (255, 220, 90))
    # listing warship hull
    c.fill_poly([(x + 14, y + 66), (x + 96, y + 58), (x + 100, y + 72),
                 (x + 88, y + 80), (x + 22, y + 80)], (38, 40, 44))
    # superstructure and mast, tilted
    c.fill_rect(x + 44, y + 48, 26, 14, (60, 62, 66))
    c.line(x + 58, y + 48, x + 52, y + 26, (200, 200, 195), 3)
    c.line(x + 52, y + 26, x + 66, y + 30, (200, 200, 195), 2)


def icon_climate(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    cx, cy = x + 58, y + 58
    # globe
    c.circle(cx, cy, 40, (120, 180, 215))
    c.circle(cx - 12, cy - 8, 12, (90, 160, 90))
    c.circle(cx + 14, cy + 10, 14, (90, 160, 90))
    c.circle(cx + 16, cy - 16, 8, (90, 160, 90))
    c.ring(cx, cy, 40, (235, 235, 230), 3)
    # crack: a dark zigzag splitting the globe
    c.polyline([(cx - 30, cy - 34), (cx - 12, cy - 14), (cx - 22, cy + 2),
                (cx - 2, cy + 18), (cx - 10, cy + 36)], (40, 30, 26), 3)
    # small sun, half-hidden
    c.circle(x + 92, y + 22, 10, (240, 180, 40))
    for dx, dy in ((0, -16), (11, -11), (16, 0), (11, 11)):
        c.line(x + 92 + dx, y + 22 + dy, x + 92 + dx * 2 // 3,
               y + 22 + dy * 2 // 3, (240, 180, 40), 2)


def icon_fire(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    # factory
    c.fill_rect(x + 16, y + 62, 84, 40, (52, 48, 44))
    c.fill_poly([(x + 16, y + 62), (x + 30, y + 46), (x + 44, y + 62),
                 (x + 58, y + 46), (x + 72, y + 62), (x + 86, y + 46),
                 (x + 100, y + 62)], (52, 48, 44))
    c.fill_rect(x + 84, y + 30, 10, 34, (52, 48, 44))
    # windows
    for wx in (26, 46, 66):
        c.fill_rect(x + wx, y + 74, 10, 10, (240, 200, 90))
    # flame
    c.fill_poly([(x + 34, y + 52), (x + 46, y + 20), (x + 52, y + 38),
                 (x + 62, y + 14), (x + 70, y + 40), (x + 82, y + 52)],
                (245, 160, 30))
    c.fill_poly([(x + 46, y + 52), (x + 54, y + 32), (x + 60, y + 44),
                 (x + 68, y + 52)], (255, 220, 80))
    # smoke
    c.circle(x + 92, y + 20, 7, (180, 180, 175))
    c.circle(x + 100, y + 12, 5, (200, 200, 195))


def icon_chess(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    # 4x4 board
    bx, by, s = x + 12, y + 26, 23
    for row in range(4):
        for col in range(4):
            colr = (240, 235, 220) if (row + col) % 2 == 0 else (30, 34, 40)
            c.fill_rect(bx + col * s, by + row * s, s, s, colr)
    c.rect(bx, by, 4 * s, 4 * s, (240, 235, 220), 2)
    # white king on a dark square, black queen on a light square,
    # so each piece contrasts with the square it stands on;
    # a thin outline ring sharpens each piece against its square
    kx, ky = bx + 2 * s + s // 2, by + 1 * s + s // 2
    c.ring(kx, ky, 11, (30, 34, 40), 1)
    c.circle(kx, ky, 9, (250, 248, 240))
    c.fill_rect(kx - 6, ky - 2, 12, 4, (250, 248, 240))
    c.fill_rect(kx - 2, ky - 6, 4, 12, (250, 248, 240))
    # black queen on a light square
    qx, qy = bx + 1 * s + s // 2, by + 1 * s + s // 2
    c.ring(qx, qy, 11, (240, 235, 220), 1)
    c.circle(qx, qy, 9, (25, 28, 32))
    c.fill_rect(qx - 6, qy - 2, 12, 4, (25, 28, 32))
    c.fill_rect(qx - 2, qy - 6, 4, 12, (25, 28, 32))


def icon_markets(c, x, y, bg):
    c.fill_rect(x, y, 116, 116, bg)
    # bars
    heights = [26, 44, 34, 58, 48, 70]
    for i, hgt in enumerate(heights):
        bx = x + 14 + i * 15
        colr = (120, 130, 145) if i < 4 else (205, 70, 55)
        c.fill_rect(bx, y + 92 - hgt, 11, hgt, colr)
    # falling line
    c.polyline([(x + 12, y + 22), (x + 34, y + 30), (x + 52, y + 26),
                (x + 72, y + 48), (x + 92, y + 40), (x + 104, y + 58)],
               (220, 60, 45), 3)
    # down arrow
    c.fill_poly([(x + 96, y + 52), (x + 108, y + 52), (x + 102, y + 66)],
                (220, 60, 45))


ICONS = [icon_hormuz, icon_warship, icon_climate,
         icon_fire, icon_chess, icon_markets]

# ----------------------------------------------------------------- stories
STORIES = [
    {
        "cat": "MIDDLE EAST",
        "headline": "IRAN VOWS TO DEFY US BLOCKADE",
        "body": "Tehran says it will use every means to break the US naval "
                "blockade of the Strait of Hormuz. Trump warns ships that "
                "try it will be sunk.",
        "source": "REUTERS / WSJ",
    },
    {
        "cat": "WAR AT SEA",
        "headline": "UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA",
        "body": "Kyiv says seven sea drones sank the corvette Merkury at "
                "Benghazi and hit a second ship. A Russian freighter was "
                "also hit in the Baltic.",
        "source": "WSJ / REUTERS",
    },
    {
        "cat": "CLIMATE",
        "headline": "COP31 CLIMATE TALKS COLLAPSE",
        "body": "UN climate talks in Antalya end with no deal and no mention "
                "of fossil fuels. The longest COP ever, and the first "
                "collapse since 2009.",
        "source": "CNN / UN NEWS",
    },
    {
        "cat": "DISASTER",
        "headline": "24 DEAD IN INDONESIA FACTORY FIRE",
        "body": "A blaze at a candy factory in Cikande, Banten, kills 24 "
                "with about 30 still missing. Rescuers search the "
                "burned-out building.",
        "source": "REUTERS",
    },
    {
        "cat": "SPORT",
        "headline": "CHESS CROWN ON THE LINE IN GENEVA",
        "body": "Game 1 begins today: champion Gukesh, 20, defends his title "
                "against Sindarov, 20, in the youngest World Championship "
                "final ever.",
        "source": "CHESS.COM / FIDE",
    },
    {
        "cat": "MARKETS",
        "headline": "ASIA MOVES TO CALM AI STOCK ROUT",
        "body": "Regulators in China, South Korea and Taiwan roll out "
                "emergency measures as the global sell-off in AI shares "
                "rattles markets.",
        "source": "DOW JONES",
    },
]

# ------------------------------------------------------------------ layout
def draw_card(c, x, y, w, h, story, accent, icon_fn):
    c.fill_rect(x, y, w, h, CARD)
    c.rect(x, y, w, h, INK, 2)
    c.fill_rect(x, y, w, 8, accent)
    # category label
    c.draw_text(x + 16, y + 18, story["cat"], 2, accent)
    # icon
    icon_fn(c, x + 16, y + 44, accent)
    # headline to the right of the icon
    hx = x + 144
    hw = w - 144 - 16
    lines = wrap_text(story["headline"], hw, 3)
    hy = y + 48
    for line in lines[:3]:
        c.draw_text(hx, hy, line, 3, INK)
        hy += 26
    # body text, full width under the icon
    by = y + 168
    for line in wrap_text(story["body"], w - 32, 2)[:4]:
        c.draw_text(x + 16, by, line, 2, (52, 52, 48))
        by += 16
    # source line at the bottom
    c.fill_rect(x + 16, y + h - 24, w - 32, 1, LIGHT_LINE)
    c.draw_text(x + 16, y + h - 18, "SOURCE: " + story["source"], 1, GREY)


def build_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    # ---- masthead
    c.fill_rect(20, 20, WIDTH - 40, 132, NAVY)
    c.rect(20, 20, WIDTH - 40, 132, INK, 2)
    c.draw_text_centered(34, "THE WORLD IN ONE DAY", 2, GOLD)
    c.draw_text_centered(58, "24 NOVEMBER 2026", 7, WHITE)
    c.fill_rect(212, 122, 200, 2, GOLD)
    c.fill_rect(612, 122, 200, 2, GOLD)
    c.draw_text_centered(130, "TUESDAY - SIX STORIES FROM AROUND THE GLOBE",
                         2, (200, 205, 215))
    # ---- story grid: 2 columns x 3 rows
    gx, gy = 20, 166
    cw, ch = 484, 264
    gapx, gapy = 16, 14
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        draw_card(c, gx + col * (cw + gapx), gy + row * (ch + gapy),
                  cw, ch, story, ACCENTS[i], ICONS[i])
    # ---- footer
    c.draw_text_centered(
        986,
        "SOURCES: REUTERS, WSJ, CNN, UN NEWS, CHESS.COM, DOW JONES",
        2, GREY)
    return c


# -------------------------------------------------------------- PNG writer
def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)  # filter: none
        start = y * WIDTH * 3
        raw += canvas.px[start:start + WIDTH * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat)
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    # Resolve the repo dir from this script's own location, never cwd.
    _here = os.path.dirname(os.path.abspath(__file__))
    _ = _here  # the image is drawn in-memory; nothing is read from disk.
    data = png_bytes(build_image())
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
