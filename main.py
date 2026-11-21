# Sums up the world's news of Saturday 21 November 2026 in one image, drawn entirely by this program
# (Python 3.13, standard library only, no network): a newspaper front page with the day's date in
# large type and six stories, each with a small drawn picture and a short label, plus a strip of
# three more. It writes the image to /output/entry.png (MAKEFUN_OUTPUT_DIR outside the grader's
# container). The drawing is fixed: two runs write the same bytes.
#
# The stories, each reported on 21 November 2026 by more than one outlet (checked 21 November):
#   - Russia's overnight barrage on Ukraine (400+ drones, 110 missiles) and Russian missiles and a
#     suspected drone coming down in Poland, whose prime minister called it a deliberate provocation
#     (AP via the day's briefs; TBS/JNN; South China Morning Post).
#   - An AI-sector sell-off pushing the S&P 500 and Dow into correction, the index down 3.7%, and
#     Anthropic stumbling days after its stock-market debut at about $2 trillion (the day's briefs;
#     The Japan Times).
#   - The International Court of Justice finding Myanmar responsible for genocide against the
#     Rohingya (the day's briefs; The Japan Times analysis).
#   - An Anthropic researcher saying Claude had solved the Riemann Hypothesis, mathematics'
#     longest-standing riddle (The Japan Times; South China Morning Post).
#   - The COP31 climate talks in Antalya, Turkey, running past their deadline, nearly 200 nations
#     deadlocked over fossil fuels (the day's briefs).
#   - A pancreatic-cancer pill, daraxonrasib, making tumours undetectable in one in 12 patients in
#     a trial (the day's briefs).
#   In the strip: the UK and EU signing their biggest post-Brexit agreements; student (Gen Z)
#   protests across 25 European countries; hackers breaching the FBI and the US Agriculture
#   Department (the day's briefs; Kyodo; The Japan Times).

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- canvas

PAPER = (250, 247, 240)
INK = (22, 22, 26)
WHITE = (255, 255, 255)
RED = (178, 34, 44)
BLUE = (29, 78, 137)
GOLD = (198, 138, 26)
GREEN = (34, 116, 71)
TEAL = (14, 116, 128)
PURPLE = (94, 58, 140)
GREY = (96, 96, 104)
LIGHT = (233, 228, 216)

img = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = c[0]
        img[i + 1] = c[1]
        img[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            i = base + xx * 3
            img[i] = c[0]
            img[i + 1] = c[1]
            img[i + 2] = c[2]


def line(x0, y0, x1, y1, c, t=3):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    r = t // 2
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        rect(x - r, y - r, t, t, c)


def circle(cx, cy, rad, c, fill=True):
    for yy in range(cy - rad, cy + rad + 1):
        for xx in range(cx - rad, cx + rad + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if d2 <= rad * rad and (fill or d2 > (rad - 4) ** 2):
                px(xx, yy, c)


def poly(points, c):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) // (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            rect(xs[i], y, xs[i + 1] - xs[i] + 1, 1, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, top row first.
FONT = {
    'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11], 'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E], 'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F], 'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F], 'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E], 'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11], 'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11], 'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E], 'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D], 'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E], 'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E], 'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11], 'X': [0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11],
    'Y': [0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04], 'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E], '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F], '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02], '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E], '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E], '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ' ': [0, 0, 0, 0, 0, 0, 0], '.': [0, 0, 0, 0, 0, 0x0C, 0x0C], ',': [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    ':': [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0], ';': [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0], '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    '?': [0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04], '-': [0, 0, 0, 0x1F, 0, 0, 0],
    '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D], '$': [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    '%': [0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03], '+': [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0],
    '/': [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10], '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08], '*': [0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0],
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (0x10 >> col):
                    rect(x + col * scale, y + row * scale, scale, scale, c)
        x += 6 * scale
    return x


def draw_centered(y, s, scale, c):
    return draw_text((W - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    words = s.split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons (drawn in a 120x120 box at x, y)

def icon_missile(x, y):
    # city skyline, a missile coming down, a burst
    rect(x + 4, y + 88, 26, 28, INK)
    rect(x + 34, y + 76, 22, 40, INK)
    rect(x + 60, y + 92, 30, 24, INK)
    rect(x + 94, y + 82, 22, 34, INK)
    rect(x + 40, y + 82, 4, 6, GOLD)
    rect(x + 48, y + 96, 4, 6, GOLD)
    rect(x + 12, y + 96, 4, 6, GOLD)
    poly([(x + 78, y + 8), (x + 90, y + 20), (x + 62, y + 46), (x + 50, y + 34)], RED)
    poly([(x + 50, y + 34), (x + 62, y + 46), (x + 44, y + 52), (x + 38, y + 40)], GOLD)
    for dx, dy in [(0, -12), (10, -8), (-10, -8), (12, 4), (-12, 4)]:
        line(x + 24, y + 62, x + 24 + dx, y + 62 + dy, GOLD, 4)
    circle(x + 24, y + 62, 7, RED)


def icon_chart(x, y):
    line(x + 10, y + 10, x + 10, y + 104, INK, 4)
    line(x + 10, y + 104, x + 114, y + 104, INK, 4)
    pts = [(x + 14, y + 34), (x + 40, y + 26), (x + 58, y + 44), (x + 76, y + 40), (x + 108, y + 88)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 6)
    poly([(x + 108, y + 88), (x + 92, y + 86), (x + 102, y + 72)], RED)
    rect(x + 24, y + 62, 10, 42, BLUE)
    rect(x + 44, y + 74, 10, 30, BLUE)
    rect(x + 64, y + 86, 10, 18, BLUE)


def icon_scales(x, y):
    line(x + 60, y + 14, x + 60, y + 92, INK, 6)
    line(x + 22, y + 26, x + 98, y + 26, INK, 6)
    circle(x + 60, y + 14, 6, GOLD)
    for cx in (x + 26, x + 94):
        line(cx - 4, y + 26, cx, y + 52, INK, 3)
        line(cx + 4, y + 26, cx, y + 52, INK, 3)
        poly([(cx - 18, y + 52), (cx + 18, y + 52), (cx + 10, y + 68), (cx - 10, y + 68)], GOLD)
    rect(x + 40, y + 92, 40, 8, INK)
    rect(x + 30, y + 100, 60, 8, INK)


def icon_math(x, y):
    line(x + 10, y + 104, x + 114, y + 104, INK, 4)
    line(x + 16, y + 108, x + 16, y + 12, INK, 4)
    prev = None
    for i in range(0, 97, 4):
        xx = x + 18 + i
        yy = y + 66 - int(34 * ((i / 96.0) ** 2) + 12 * ((i % 24) / 24.0 - 0.5))
        if prev is not None:
            line(prev[0], prev[1], xx, yy, TEAL, 5)
        prev = (xx, yy)
    for gx in range(3):
        for gy in range(3):
            circle(x + 78 + gx * 14, y + 22 + gy * 14, 3, PURPLE)
    draw_text(x + 92, y + 76, '?', 3, RED)


def icon_climate(x, y):
    circle(x + 48, y + 60, 38, BLUE, fill=False)
    # meridians as vertical ellipses approximated by lines
    for dx in (-20, 0, 20):
        line(x + 48 + dx // 2, y + 28, x + 48 + dx, y + 60, TEAL, 3)
        line(x + 48 + dx, y + 60, x + 48 + dx // 2, y + 92, TEAL, 3)
    line(x + 14, y + 48, x + 82, y + 48, TEAL, 3)
    line(x + 18, y + 74, x + 78, y + 74, TEAL, 3)
    # thermometer
    rect(x + 98, y + 18, 10, 62, INK)
    rect(x + 100, y + 44, 6, 34, RED)
    circle(x + 103, y + 90, 12, RED)
    rect(x + 100, y + 84, 6, 8, RED)


def icon_pill(x, y):
    # capsule
    poly([(x + 22, y + 78), (x + 62, y + 38), (x + 76, y + 52), (x + 36, y + 92)], TEAL)
    poly([(x + 62, y + 38), (x + 84, y + 16), (x + 98, y + 30), (x + 76, y + 52)], RED)
    line(x + 62, y + 38, x + 76, y + 52, WHITE, 4)
    # cross badge
    circle(x + 88, y + 88, 20, GREEN)
    rect(x + 84, y + 74, 8, 28, WHITE)
    rect(x + 74, y + 84, 28, 8, WHITE)
    # small round tablets
    circle(x + 26, y + 26, 12, GOLD)
    line(x + 16, y + 26, x + 36, y + 26, WHITE, 3)


# ---------------------------------------------------------------- page

rect(0, 0, W, H, PAPER)
rect(24, 24, W - 48, 4, INK)
draw_centered(44, 'THE WORLD IN ONE DAY', 3, INK)
rect(24, 78, W - 48, 2, INK)
draw_centered(96, 'SATURDAY', 7, INK)
draw_centered(152, '21 NOVEMBER 2026', 8, RED)
rect(24, 224, W - 48, 4, INK)

PANELS = [
    ('EUROPE - WAR', RED, icon_missile,
     'RUSSIA BARRAGES KYIV; MISSILES LAND IN POLAND',
     '400+ DRONES AND 110 MISSILES IN ONE NIGHT. POLAND CALLS IT A DELIBERATE PROVOCATION'),
    ('MARKETS', BLUE, icon_chart,
     'AI SELL-OFF PUSHES WALL ST INTO CORRECTION',
     'THE S&P 500 FALLS 3.7% AS ANTHROPIC STUMBLES DAYS AFTER ITS $2 TRILLION STOCK MARKET DEBUT'),
    ('WORLD COURT', GOLD, icon_scales,
     'ICJ: MYANMAR RESPONSIBLE FOR ROHINGYA GENOCIDE',
     'THE HAGUE RULES ON THE 2017 CRACKDOWN ON THE ROHINGYA MINORITY'),
    ('SCIENCE', PURPLE, icon_math,
     "RESEARCHER: AI SOLVES MATH'S GREATEST RIDDLE",
     'AN ANTHROPIC RESEARCHER SAYS CLAUDE HAS SOLVED THE RIEMANN HYPOTHESIS, UNSOLVED FOR 160 YEARS'),
    ('CLIMATE', GREEN, icon_climate,
     'COP31 TALKS RUN INTO OVERTIME IN ANTALYA',
     'NEARLY 200 NATIONS DEADLOCKED OVER FOSSIL FUELS AS THE UN SUMMIT PASSES ITS DEADLINE'),
    ('HEALTH', TEAL, icon_pill,
     'CANCER PILL ERASES TUMOURS IN TRIAL',
     'PANCREATIC CANCER DRUG DARAXONRASIB: TUMOURS UNDETECTABLE IN 1 IN 12 PATIENTS'),
]

PX = [28, 524]
PY = [244, 476, 708]
PW = 472
PH = 216
for idx, (tag, color, icon, head, sub) in enumerate(PANELS):
    x = PX[idx % 2]
    y = PY[idx // 2]
    rect(x, y, PW, PH, WHITE)
    rect(x, y, PW, 4, color)
    rect(x, y + PH - 4, PW, 4, INK)
    rect(x, y, 4, PH, INK)
    rect(x + PW - 4, y, 4, PH, INK)
    icon(x + 14, y + 52)
    tx = x + 148
    tw = PW - 148 - 14
    rect(tx, y + 16, text_w(tag, 2) + 12, 20, color)
    draw_text(tx + 6, y + 19, tag, 2, WHITE)
    ly = y + 46
    for ln in wrap(head, 3, tw):
        draw_text(tx, ly, ln, 3, INK)
        ly += 25
    ly += 3
    for ln in wrap(sub, 2, tw):
        draw_text(tx, ly, ln, 2, GREY)
        ly += 16

rect(24, 940, W - 48, 3, INK)
also = ('ALSO TODAY: UK AND EU SIGN THEIR BIGGEST POST-BREXIT DEALS - STUDENT PROTESTS SWEEP 25 EUROPEAN '
        'COUNTRIES - HACKERS BREACH THE FBI AND THE US AGRICULTURE DEPARTMENT')
ly = 952
for ln in wrap(also, 2, W - 56):
    draw_centered(ly, ln, 2, INK)
    ly += 17

# ---------------------------------------------------------------- PNG out

raw = b''
for yy in range(H):
    raw += b'\x00' + bytes(img[yy * W * 3:(yy + 1) * W * 3])


def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(raw, 9))
       + chunk(b'IEND', b''))

out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'entry.png'), 'wb') as f:
    f.write(png)
