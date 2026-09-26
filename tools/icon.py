#!/usr/bin/env python3
"""Draws the Keel & Cloud pixel-art icon (a 64x64 master) and writes the PNGs used by the pack:
   assets/icon-64.png (server list), assets/icon-256.png (launcher), assets/banner.png (README).
No dependencies: pixels are drawn by hand and written with zlib."""
import math, os, struct, zlib

W = H = 64
ROOT = os.path.join(os.path.dirname(__file__), '..')


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


SKY_TOP, SKY_LOW = hexc('#1d3a5f'), hexc('#f2b880')
SUN, SUN_GLOW = hexc('#ffe7a8'), hexc('#f7c98b')
CLOUD, CLOUD_SHADE = hexc('#fdf6ec'), hexc('#d9c9d6')
SEA_TOP, SEA_DEEP, FOAM = hexc('#2f6f86'), hexc('#0b2233'), hexc('#8fd0d8')
ENVELOPE, ENVELOPE_SHADE, ENVELOPE_LIGHT = hexc('#e9dcc0'), hexc('#b9a585'), hexc('#fff6e0')
BRASS, BRASS_DARK = hexc('#d9a441'), hexc('#8a5d1d')
WOOD, WOOD_DARK, WOOD_LIGHT = hexc('#8b5a2b'), hexc('#4e2f16'), hexc('#b07a44')
ROPE = hexc('#5b4630')
SUB, SUB_LIGHT = hexc('#1f5a70'), hexc('#6fb3c2')
OUTLINE = hexc('#1a1410')

px = [[None] * W for _ in range(H)]
layer = [[0] * W for _ in range(H)]  # 0 = scenery, 1 = ship (gets an outline)


def put(x, y, c, lay=0):
    if 0 <= x < W and 0 <= y < H:
        px[y][x] = c
        layer[y][x] = lay


HORIZON = 44
# Sky: dusk gradient with dithered bands, pixel-art style.
for y in range(HORIZON):
    t = y / (HORIZON - 1)
    for x in range(W):
        d = ((x + y) % 2) * 0.03
        put(x, y, mix(SKY_TOP, SKY_LOW, min(1, t ** 1.4 + d)))
# Sun low on the horizon, behind everything.
for y in range(HORIZON - 12, HORIZON):
    for x in range(40, 62):
        r = math.hypot(x - 51, y - (HORIZON - 1))
        if r < 7:
            put(x, y, SUN)
        elif r < 9 and (x + y) % 2 == 0:
            put(x, y, SUN_GLOW)
# Sea: gradient into the deep, with foam lines.
for y in range(HORIZON, H):
    t = (y - HORIZON) / (H - HORIZON - 1)
    for x in range(W):
        put(x, y, mix(SEA_TOP, SEA_DEEP, t ** 0.8))
for y, xs in ((HORIZON, range(0, 64, 1)), (HORIZON + 2, range(3, 30, 1)), (HORIZON + 4, range(34, 60, 1))):
    for x in xs:
        if (x // 3 + y) % 3 == 0:
            put(x, y, FOAM)
# Sun glitter on the water.
for y, x0, x1 in ((HORIZON + 1, 46, 56), (HORIZON + 3, 48, 54), (HORIZON + 5, 49, 53), (HORIZON + 7, 50, 52)):
    for x in range(x0, x1 + 1):
        if (x + y) % 3:
            put(x, y, SUN_GLOW)
# A submarine in the deep: the other half of the pack.
for y in range(55, 59):
    for x in range(9, 25):
        if ((x - 16.5) / 8) ** 2 + ((y - 56.8) / 2) ** 2 <= 1:
            put(x, y, SUB)
for x, y in ((14, 54), (15, 54), (16, 54), (15, 53), (15, 52)):
    put(x, y, SUB)
for x in (11, 13, 18, 20, 22):
    put(x, 56, SUB_LIGHT)
put(24, 57, SUB_LIGHT)


def blob(cx, cy, rx, ry, c, shade=None):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                put(x, y, shade if shade and y > cy + ry * 0.35 else c)


# Clouds, one behind the ship and one small one to the left.
for cx, cy, rx, ry in ((44, 22, 9, 4), (37, 24, 7, 3.2), (52, 24, 6, 3)):
    blob(cx, cy, rx, ry, CLOUD, CLOUD_SHADE)
for cx, cy, rx, ry in ((9, 12, 5, 2.2), (14, 13, 4, 1.8)):
    blob(cx, cy, rx, ry, CLOUD, CLOUD_SHADE)

# The airship. Envelope: an elongated ellipse with brass bands and a highlight.
ECX, ECY, ERX, ERY = 27, 17, 17, 7.5
for y in range(int(ECY - ERY) - 1, int(ECY + ERY) + 2):
    for x in range(int(ECX - ERX) - 1, int(ECX + ERX) + 2):
        v = ((x - ECX) / ERX) ** 2 + ((y - ECY) / ERY) ** 2
        if v <= 1:
            c = ENVELOPE
            if y > ECY + ERY * 0.3:
                c = ENVELOPE_SHADE
            elif y < ECY - ERY * 0.45 and ECX - 10 < x < ECX + 4:
                c = ENVELOPE_LIGHT
            if x in (17, 27, 37):
                c = BRASS_DARK if y > ECY + ERY * 0.3 else BRASS
            put(x, y, c, 1)
# Tail fins.
for x, y in ((9, 13), (10, 13), (9, 12), (8, 12), (9, 21), (10, 21), (9, 22), (8, 22)):
    put(x, y, ENVELOPE_SHADE, 1)
# Rigging from envelope to hull.
for x0, x1 in ((18, 20), (27, 27), (36, 34)):
    for y in range(25, 30):
        x = round(x0 + (x1 - x0) * (y - 25) / 4)
        put(x, y, ROPE, 1)
# Hull: a boat with a proper keel, planks, a brass rail and portholes.
HULL_TOP = 30
for y in range(HULL_TOP, HULL_TOP + 7):
    inset = (y - HULL_TOP) ** 2 // 4
    for x in range(16 + inset, 40 - inset // 2):
        c = WOOD if (y - HULL_TOP) % 2 == 0 else WOOD_DARK if y > HULL_TOP + 3 else WOOD_LIGHT
        put(x, y, c, 1)
for x in range(15, 41):
    put(x, HULL_TOP - 1, BRASS, 1)
for x in (21, 26, 31):
    put(x, HULL_TOP + 2, BRASS, 1)
put(40, HULL_TOP, WOOD, 1)
put(41, HULL_TOP - 1, WOOD, 1)
put(42, HULL_TOP - 2, WOOD, 1)
# Keel line under the hull.
for x in range(24, 35):
    put(x, HULL_TOP + 7, WOOD_DARK, 1)
# Propeller at the stern.
for x, y in ((12, 29), (12, 30), (12, 31), (13, 30), (14, 30), (11, 28), (11, 32)):
    put(x, y, BRASS if (x, y) != (13, 30) else BRASS_DARK, 1)

# One-pixel dark outline around the ship, so it reads at 16-32 px.
outline = []
for y in range(H):
    for x in range(W):
        if layer[y][x] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and layer[ny][nx] == 1:
                    outline.append((x, y))
                    break
for x, y in outline:
    px[y][x] = mix(px[y][x], OUTLINE, 0.75)


def write_png(path, pixels, scale=1):
    h, w = len(pixels) * scale, len(pixels[0]) * scale
    raw = bytearray()
    for row in pixels:
        line = bytearray([0])
        for c in row:
            line += bytes(c) * scale
        raw += bytes(line) * scale
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(png)


# README banner: the scene widened by extending sky and sea, icon art centred.
def banner():
    bw = 192
    rows = []
    for y in range(H):
        base = px[y][0] if y < HORIZON else px[y][2]
        row = []
        for x in range(bw):
            ix = x - (bw - W) // 2
            if 0 <= ix < W:
                row.append(px[y][ix])
            elif y < HORIZON:
                t = y / (HORIZON - 1)
                row.append(mix(SKY_TOP, SKY_LOW, min(1, t ** 1.4 + ((x + y) % 2) * 0.03)))
            else:
                t = (y - HORIZON) / (H - HORIZON - 1)
                c = mix(SEA_TOP, SEA_DEEP, t ** 0.8)
                if y in (HORIZON, HORIZON + 3) and (x // 3 + y) % 3 == 0:
                    c = FOAM
                row.append(c)
        rows.append(row)
    for cx, cy, rx, ry in ((22, 14, 7, 2.5), (160, 10, 8, 2.8), (170, 12, 5, 2)):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if 0 <= x < bw and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    rows[y][x] = CLOUD_SHADE if y > cy + ry * 0.35 else CLOUD
    return rows


write_png(os.path.join(ROOT, 'assets/icon-64.png'), px)
write_png(os.path.join(ROOT, 'assets/icon-256.png'), px, 4)
write_png(os.path.join(ROOT, 'assets/banner.png'), banner(), 5)
print('wrote assets/icon-64.png, assets/icon-256.png, assets/banner.png')
