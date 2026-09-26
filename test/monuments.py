#!/usr/bin/env python3
"""Measures how far YUNG's ocean monuments sit above the Tectonic sea floor.

Needs the test server running (test/server-test.sh --keep-running). Finds monuments over RCON,
force-loads them so they generate, then reads the region files directly.
Gap = water between a monument column's lowest block and the floor under it. A monument fails when more than
a quarter of its columns float by more than 3 blocks, more than 30% are embedded in terrain, or it reaches
sea level. A few overhanging or embedded edges on slopes are normal; vanilla monuments do the same.
"""
import gzip, io, math, os, statistics, struct, sys, time, zlib

sys.path.insert(0, os.path.dirname(__file__))
from rcon import Rcon

ROOT = os.path.join(os.path.dirname(__file__), '..')
WORLD = os.path.join(ROOT, 'build/server/world')
STRUCTURE = 'betteroceanmonuments:ocean_monument'
RADIUS = 48
SEA_LEVEL = 63
FLUID = ('minecraft:water', 'minecraft:air', 'minecraft:cave_air', 'minecraft:seagrass', 'minecraft:tall_seagrass',
         'minecraft:kelp', 'minecraft:kelp_plant', 'minecraft:bubble_column')


def monument_block(name):
    return 'prismarine' in name or name == 'minecraft:sea_lantern'


# --- minimal NBT reader -----------------------------------------------------------------------
def nbt(buf):
    def payload(t):
        if t == 1: return struct.unpack('>b', buf.read(1))[0]
        if t == 2: return struct.unpack('>h', buf.read(2))[0]
        if t == 3: return struct.unpack('>i', buf.read(4))[0]
        if t == 4: return struct.unpack('>q', buf.read(8))[0]
        if t == 5: return struct.unpack('>f', buf.read(4))[0]
        if t == 6: return struct.unpack('>d', buf.read(8))[0]
        if t == 7: return buf.read(struct.unpack('>i', buf.read(4))[0])
        if t == 8: return buf.read(struct.unpack('>H', buf.read(2))[0]).decode('utf-8', 'replace')
        if t == 9:
            et, n = struct.unpack('>bi', buf.read(5))
            return [payload(et) for _ in range(n)]
        if t == 10:
            out = {}
            while (ct := buf.read(1)[0]) != 0:
                name = buf.read(struct.unpack('>H', buf.read(2))[0]).decode('utf-8', 'replace')
                out[name] = payload(ct)
            return out
        if t == 11: n = struct.unpack('>i', buf.read(4))[0]; return struct.unpack(f'>{n}i', buf.read(4 * n))
        if t == 12: n = struct.unpack('>i', buf.read(4))[0]; return struct.unpack(f'>{n}q', buf.read(8 * n))
        raise ValueError(f'bad tag {t}')
    t = buf.read(1)[0]
    buf.read(struct.unpack('>H', buf.read(2))[0])
    return payload(t)


_chunks = {}
def chunk(cx, cz):
    if (cx, cz) in _chunks:
        return _chunks[(cx, cz)]
    path = os.path.join(WORLD, 'region', f'r.{cx >> 5}.{cz >> 5}.mca')
    sections = None
    with open(path, 'rb') as f:
        f.seek(4 * ((cx & 31) + (cz & 31) * 32))
        loc = struct.unpack('>I', f.read(4))[0]
        if loc:
            f.seek((loc >> 8) * 4096)
            length, comp = struct.unpack('>IB', f.read(5))
            raw = f.read(length - 1)
            data = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw)
            sections = {s['Y']: s.get('block_states') for s in nbt(io.BytesIO(data))['sections']}
    _chunks[(cx, cz)] = sections
    return sections


def block(x, y, z):
    sections = chunk(x >> 4, z >> 4)
    states = sections.get(y >> 4) if sections else None
    if not states:
        return 'minecraft:air'
    palette = states['palette']
    if len(palette) == 1:
        return palette[0]['Name']
    bits = max(4, math.ceil(math.log2(len(palette))))
    per_long = 64 // bits
    i = ((y & 15) * 16 + (z & 15)) * 16 + (x & 15)
    value = (states['data'][i // per_long] >> ((i % per_long) * bits)) & ((1 << bits) - 1)
    return palette[value]['Name']


def measure(cx, cz):
    """Returns (gaps, highest monument block, share of columns embedded in terrain)."""
    gaps, top, embedded = [], -64, 0
    for x in range(cx - RADIUS, cx + RADIUS + 1, 4):
        for z in range(cz - RADIUS, cz + RADIUS + 1, 4):
            lowest = next((y for y in range(-64, 100) if monument_block(block(x, y, z))), None)
            if lowest is None:
                continue
            highest = next(y for y in range(100, lowest - 1, -1) if monument_block(block(x, y, z)))
            top = max(top, highest)
            inside = sum(1 for y in range(lowest, highest + 1) if block(x, y, z) not in FLUID and not monument_block(block(x, y, z)))
            covered = sum(1 for y in range(highest + 1, highest + 6) if block(x, y, z) not in FLUID)
            embedded += inside > 3 or covered >= 3
            floor = next((y for y in range(lowest - 1, -65, -1) if block(x, y, z) not in FLUID), -65)
            gaps.append(lowest - floor - 1)
    return gaps, top, embedded / max(len(gaps), 1)


def main():
    r = Rcon(open(os.path.join(ROOT, 'build/server/.rcon-pass')).read().strip())
    found = set()
    for ox in range(-4000, 4001, 4000):
        for oz in range(-4000, 4001, 4000):
            t = time.time()
            out = r.run(f'execute positioned {ox} 64 {oz} run locate structure {STRUCTURE}')
            print(f'locate from [{ox}, {oz}] took {time.time() - t:.1f}s')
            if 'is at [' in out:
                x, _, z = out.split('[')[1].split(']')[0].split(', ')
                found.add((int(x), int(z)))
    print(f'{len(found)} monuments found')
    for x, z in sorted(found):
        r.run(f'forceload add {x - RADIUS} {z - RADIUS} {x + RADIUS} {z + RADIUS}')
    time.sleep(20)
    r.run('save-all flush')
    time.sleep(5)
    for x, z in sorted(found):
        r.run(f'forceload remove {x - RADIUS} {z - RADIUS} {x + RADIUS} {z + RADIUS}')
    floating = 0
    for x, z in sorted(found):
        gaps, top, embedded = measure(x, z)
        if not gaps:
            print(f'[{x}, {z}] no monument blocks found (not generated?)')
            continue
        share = sum(g > 3 for g in gaps) / len(gaps)
        bad = share > 0.25 or top >= SEA_LEVEL or embedded > 0.3
        floating += bad
        print(f'[{x}, {z}] columns={len(gaps)} median gap={statistics.median(gaps)} max={max(gaps)} '
              f'floating={share:.0%} embedded={embedded:.0%} top y={top}' + ('  <-- FAIL' if bad else ''))
    print(f'FAIL: {floating} monuments floating, buried or breaching the surface' if floating else 'PASS')
    sys.exit(1 if floating else 0)


if __name__ == '__main__':
    main()
