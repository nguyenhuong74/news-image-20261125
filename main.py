#!/usr/bin/env python3
"""The World in One Page -- Tuesday 25 November 2026.

Draws a 1024x1024 newspaper front page summing up the world news of
Tuesday 25 November 2026. Python 3.13 standard library only: no network,
no files read at run time, no pip installs. Writes /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).

Everything here -- the 5x7 bitmap font and the PNG encoder -- is written
from scratch for this entry.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (20, 28, 38)
NAVY = (18, 32, 54)
GOLD = (198, 156, 60)
CARD = (255, 255, 255)
BORDER = (180, 172, 152)
MUTED = (90, 86, 76)
RED = (176, 42, 42)
BLUE = (36, 84, 140)
TEAL = (0, 120, 110)
PURPLE = (96, 64, 140)
GREEN = (40, 110, 60)
ORANGE = (190, 100, 20)

# ------------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, '1' = ink.
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
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01110", "10001", "10001", "01110", "01000", "01100"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00010", "01100"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ';': ("00000", "00000", "01100", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "00000", "00000", "01100", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    return len(text) * 6 * scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[base:base + 3] = bytes(color)
                base += 3

    def hline(self, x0, x1, y, color, thick=1):
        for yy in range(y, y + thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, color)

    def vline(self, x, y0, y1, color, thick=1):
        for xx in range(x, x + thick):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, color)
                elif not fill and abs(d - r * r) <= r:
                    self.set(xx, yy, color)

    def poly(self, points, color):
        """Scanline-filled polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    nodes.append(x)
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                for x in range(int(nodes[i]), int(nodes[i + 1]) + 1):
                    self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        """Draw text; returns the x just past the last glyph."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)


# ------------------------------------------------------------------- icons
def icon_ship(cv, x, y, color):
    # tanker hull
    cv.poly([(x + 2, y + 34), (x + 54, y + 34), (x + 48, y + 48),
             (x + 8, y + 48)], color)
    cv.rect(x + 34, y + 20, 14, 14, color)
    cv.rect(x + 10, y + 26, 8, 8, color)
    # waves
    cv.hline(x, x + 56, y + 52, color, 2)
    # spiky mine above the ship
    mx, my = x + 18, y + 10
    cv.circle(mx, my, 7, color)
    for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9), (-6, -6), (6, -6),
                   (-6, 6), (6, 6)):
        cv.line(mx, my, mx + dx, my + dy, color)


def icon_jet(cv, x, y, color):
    cv.poly([(x + 4, y + 30), (x + 44, y + 22), (x + 54, y + 26),
             (x + 44, y + 30), (x + 20, y + 34)], color)
    cv.poly([(x + 22, y + 30), (x + 30, y + 12), (x + 34, y + 12),
             (x + 34, y + 30)], color)
    cv.poly([(x + 14, y + 34), (x + 22, y + 46), (x + 26, y + 46),
             (x + 26, y + 34)], color)
    cv.line(x + 4, y + 30, x + 52, y + 26, color)


def icon_building(cv, x, y, color):
    cv.rect(x + 8, y + 10, 40, 42, color)
    cv.poly([(x + 8, y + 10), (x + 28, y + 2), (x + 48, y + 10)], color)
    for wx in (x + 14, x + 26, x + 38):
        for wy in (y + 18, y + 30, y + 42):
            cv.rect(wx, wy, 5, 5, PAPER)


def icon_rocket(cv, x, y, color):
    cv.poly([(x + 28, y + 2), (x + 38, y + 22), (x + 34, y + 40),
             (x + 22, y + 40), (x + 18, y + 22)], color)
    cv.circle(x + 28, y + 20, 5, PAPER)
    cv.circle(x + 28, y + 20, 3, color)
    cv.poly([(x + 18, y + 34), (x + 10, y + 48), (x + 20, y + 42)], color)
    cv.poly([(x + 38, y + 34), (x + 46, y + 48), (x + 36, y + 42)], color)
    cv.poly([(x + 24, y + 40), (x + 32, y + 40), (x + 28, y + 54)], GOLD)


def icon_flags(cv, x, y, color):
    cv.vline(x + 14, y + 8, y + 52, color, 2)
    cv.vline(x + 40, y + 8, y + 52, color, 2)
    cv.poly([(x + 16, y + 8), (x + 38, y + 8), (x + 32, y + 18),
             (x + 16, y + 18)], BLUE)
    cv.poly([(x + 42, y + 8), (x + 54, y + 8), (x + 54, y + 18),
             (x + 42, y + 18)], GREEN)
    cv.rect(x + 4, y + 52, 48, 3, color)


def icon_drone(cv, x, y, color):
    cx, cy = x + 28, y + 28
    cv.rect(cx - 9, cy - 6, 18, 12, color)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cv.line(cx, cy, cx + dx * 18, cy + dy * 16, color)
        cv.circle(cx + dx * 18, cy + dy * 16, 7, color, fill=False)
        cv.hline(cx + dx * 18 - 8, cx + dx * 18 + 8, cy + dy * 16, color, 2)


ICONS = {
    "ship": icon_ship,
    "jet": icon_jet,
    "building": icon_building,
    "rocket": icon_rocket,
    "flags": icon_flags,
    "drone": icon_drone,
}

# ------------------------------------------------------------------ content
# Six main stories of Tuesday 25 November 2026, each verified against
# reporting published that day (Reuters, BBC, AP, Xinhua, Just Security).
STORIES = [
    {
        "kicker": "MIDDLE EAST - HORMUZ",
        "accent": RED,
        "icon": "ship",
        "headline": "Tankers hit by mines in Strait of Hormuz",
        "body": ("Iran's Revolutionary Guard said oil tankers struck naval "
                 "mines in the strait and caught fire. Washington is "
                 "probing possible Iranian links."),
    },
    {
        "kicker": "EUROPE - UKRAINE",
        "accent": BLUE,
        "icon": "jet",
        "headline": "Kyiv says it hit five Russian warplanes",
        "body": ("Ukraine's General Staff said its forces struck three "
                 "MiG-31s and two Su-34s at Savasleyka airbase, and hit "
                 "two oil refineries in Samara."),
    },
    {
        "kicker": "MIDDLE EAST - GAZA",
        "accent": TEAL,
        "icon": "building",
        "headline": "Israeli strike kills Hamas security chief",
        "body": ("Mohammed Abu al-Ouf, head of Hamas's internal security in "
                 "northern Gaza, was killed with his wife and two daughters "
                 "in Gaza City, medics said."),
    },
    {
        "kicker": "SPACE - CHINA",
        "accent": PURPLE,
        "icon": "rocket",
        "headline": "First Pakistani in orbit on Shenzhou-24",
        "body": ("China's Shenzhou-24 docked with the Tiangong station. "
                 "Muhammad Zeeshan Ali is the first foreign astronaut to "
                 "visit Tiangong."),
    },
    {
        "kicker": "PACIFIC",
        "accent": GREEN,
        "icon": "flags",
        "headline": "Solomon Islands signs Australia pact",
        "body": ("The two countries signed a treaty that would bar any "
                 "foreign military or security base on Solomon Islands."),
    },
    {
        "kicker": "AFRICA - SUDAN",
        "accent": ORANGE,
        "icon": "drone",
        "headline": "RSF drone strikes kill 19 civilians",
        "body": ("Sudan's Emergency Lawyers said paramilitary drone strikes "
                 "killed 19 people and wounded 20 in two cities, as the "
                 "civil war grinds on."),
    },
]

BRIEFS = [
    ("EGYPT", "Fuel tanker crash near Cairo kills at least 31."),
    ("BANGLADESH", "Garment wage up 36% to $139 a month."),
    ("CLIMATE", "Pope Leo XIV warns COP31 ended with no deal."),
    ("POLAND", "No-fly zone planned on Ukraine border."),
]


# -------------------------------------------------------------------- draw
def draw_card(cv, x, y, w, h, story):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 3, story["accent"])
    # border
    cv.hline(x, x + w - 1, y + h - 1, BORDER)
    cv.vline(x, y, y + h - 1, BORDER)
    cv.vline(x + w - 1, y, y + h - 1, BORDER)
    pad = 16
    # kicker tag
    tag = story["kicker"]
    tw = text_width(tag, 2)
    cv.rect(x + pad, y + 16, tw + 12, 22, story["accent"])
    cv.text(x + pad + 6, y + 19, tag, 2, CARD)
    # icon, top right
    ICONS[story["icon"]](cv, x + w - 74, y + 14, story["accent"])
    # headline, two lines max, left of the icon
    lines = wrap_text(story["headline"], w - pad * 2 - 66, 3)
    hy = y + 52
    for line in lines[:2]:
        cv.text(x + pad, hy, line, 3, INK)
        hy += 24
    cv.hline(x + pad, x + w - pad - 1, hy + 2, BORDER)
    # body
    blines = wrap_text(story["body"], w - pad * 2, 2)
    by = hy + 14
    for line in blines[:4]:
        cv.text(x + pad, by, line, 2, INK)
        by += 18


def draw(cv):
    cv.rect(0, 0, W, H, PAPER)
    # ---- masthead
    cv.rect(0, 0, W, 128, NAVY)
    cv.rect(0, 128, W, 4, GOLD)
    cv.text_centered(16, "THE WORLD IN ONE PAGE", 5, CARD)
    cv.text_centered(60, "TUESDAY, 25 NOVEMBER 2026", 3, GOLD)
    cv.text_centered(94, "Six stories that defined the day - from the Strait of "
                         "Hormuz to Tiangong", 2, (200, 205, 215))
    # ---- story grid: 2 columns x 3 rows
    margin, gap = 16, 14
    cw = (W - margin * 2 - gap) // 2
    ch = 222
    top = 146
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cw + gap)
        cy = top + (i // 2) * (ch + gap)
        draw_card(cv, cx, cy, cw, ch, story)
    # ---- briefs strip
    by = top + 3 * ch + 2 * gap + 12
    bh = 116
    cv.rect(0, by, W, bh, NAVY)
    cv.rect(0, by, W, 3, GOLD)
    cv.text(16, by + 12, "IN BRIEF", 2, GOLD)
    col_w = (W - 32) // 4
    for i, (label, text) in enumerate(BRIEFS):
        bx = 16 + i * col_w
        if i:
            cv.vline(bx - 8, by + 36, by + bh - 12, (70, 84, 108))
        cv.text(bx, by + 36, label, 2, GOLD)
        for j, line in enumerate(wrap_text(text, col_w - 16, 2)[:3]):
            cv.text(bx, by + 58 + j * 17, line, 2, CARD)
    # ---- footer
    fy = by + bh + 10
    cv.text_centered(fy, "Sources: Reuters, BBC, AP, Xinhua, Just Security - "
                         "events of 25 November 2026", 1, MUTED)


# --------------------------------------------------------------------- png
def png_bytes(cv):
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw(cv)
    data = png_bytes(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
