# -*- coding: utf-8 -*-
"""Does die_cube.glb wear the right number on the right face, per D3X.FACE?

WHY THIS EXISTS AS A COMMITTED CHECK. Two measurements of this same file
disagreed, and the reason was the measurement, not the model:

  attempt 1  read the UV cell and assumed slot order == value order. True of
             the current generator and NOT of the previous one, so it reported
             a broken die (1 opposite 2) that did not exist.
  attempt 2  the render showed 1 and 3 swapped. That one was real - but the
             cause was a STALE FILE: the generator wrote into the main
             checkout, a routine `cp worktree main` afterwards put the old
             build back, and the check page loaded the old build.

So: no slot assumption, no rendering, no second copy. Crop each face's UV
rectangle straight out of the atlas EMBEDDED IN THE GLB and compare it byte for
byte against the real bone_N.png. The only thing it trusts is the file itself.

Run: python3 tools/check_cube_faces.py
"""
import io, os, sys, json, struct, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GLB = os.path.join(ROOT, 'assets', 'models', 'die_cube.glb')
ART = os.path.abspath(os.path.join(ROOT, '..', '..', '..',
                                   'Art', 'Assets', 'Dice', 'Bone', 'texture'))
GAME = os.path.join(ROOT, 'fark_proto.html')

if not os.path.exists(GLB):
    print('SKIP: no die_cube.glb - run tools/make_cube_glb.py first')
    sys.exit(0)

# what the GAME expects, read from the game
g = io.open(GAME, encoding='utf-8').read()
i = g.index('  FACE:{1:')
d, j = 0, g.index('{', i)
while j < len(g):
    if g[j] == '{':
        d += 1
    elif g[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
WANT = {}
for m in re.finditer(r'(\d):\[\[-?\d+,-?\d+,-?\d+\],\[-?\d+,-?\d+,-?\d+\],'
                     r'\[(-?\d+),(-?\d+),(-?\d+)\]\]', g[i:j + 1]):
    WANT[int(m.group(1))] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
if len(WANT) != 6:
    print('FAIL: could not read D3X.FACE from the game (%d entries)' % len(WANT))
    sys.exit(1)

raw = io.open(GLB, 'rb').read()
off, chunks = 12, {}
while off < len(raw):
    ln, ty = struct.unpack_from('<I4s', raw, off)
    off += 8
    chunks[ty.decode().replace('\0', '').strip()] = raw[off:off + ln]
    off += ln
gj = json.loads(chunks['JSON'])
bin_ = chunks['BIN']


def acc(idx):
    a = gj['accessors'][idx]
    bv = gj['bufferViews'][a['bufferView']]
    o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    fmt = {5126: 'f', 5123: 'H'}[a['componentType']]
    sz = {'f': 4, 'H': 2}[fmt]
    vals = struct.unpack('<' + fmt * (a['count'] * n), bin_[o:o + a['count'] * n * sz])
    return [vals[k * n:(k + 1) * n] for k in range(a['count'])]


iv = gj['bufferViews'][gj['images'][0]['bufferView']]
atlas = Image.open(io.BytesIO(bin_[iv['byteOffset']:iv['byteOffset'] + iv['byteLength']])).convert('RGBA')
AW, AH = atlas.size
art = {}
for v in range(1, 7):
    p = os.path.join(ART, '%d.png' % v)
    if not os.path.exists(p):
        print('FAIL: missing ' + p)
        sys.exit(1)
    art[v] = Image.open(p).convert('RGB').convert('RGBA').tobytes()

prim = gj['meshes'][0]['primitives'][0]
N = acc(prim['attributes']['NORMAL'])
UV = acc(prim['attributes']['TEXCOORD_0'])
nm = {(1,0,0):'+X',(-1,0,0):'-X',(0,1,0):'+Y',(0,-1,0):'-Y',(0,0,1):'+Z',(0,0,-1):'-Z'}
want_at = {WANT[v]: v for v in WANT}

bad, seen = 0, {}
for f in range(len(N) // 4):
    n = tuple(int(round(x)) for x in N[f * 4])
    us = [UV[f * 4 + k] for k in range(4)]
    box = (round(min(u for u, _ in us) * AW), round(min(v for _, v in us) * AH),
           round(max(u for u, _ in us) * AW), round(max(v for _, v in us) * AH))
    crop = atlas.crop(box).tobytes()
    match = [v for v in art if art[v] == crop]
    got = match[0] if match else None
    exp = want_at.get(n)
    # THE PREMISE CHANGED WITH THE BLANK ART: any wear-variant may sit on any
    # face, so 'cell N wears bone_N' is meaningless now. What must still hold is
    # the face NORMAL -> atlas CELL mapping, which D3X.FACE and the brand
    # compositor both index by value.
    cell = (box[1] // 128) * 3 + (box[0] // 128)
    ok = got is not None and exp is not None and cell == exp - 1
    if not ok:
        bad += 1
    seen[n] = got
    print('  %s face %s  wears %s   D3X.FACE wants %s'
          % ('OK  ' if ok else 'FAIL', nm.get(n, str(n)).ljust(3),
             ('cell %d, variant %s' % (cell, got)) if got else 'NO MATCH',
             ('value %s' % exp) if exp else '(no entry)'))

for ax in [(1,0,0),(0,1,0),(0,0,1)]:
    a, b = want_at.get(ax), want_at.get(tuple(-c for c in ax))
    if a and b and a + b != 7:
        bad += 1
        print('  FAIL %s/%s hold %d and %d - opposite faces must sum to 7' % (nm[ax], nm[tuple(-c for c in ax)], a, b))

print(('\nFAILURES: %d' % bad) if bad
      else '\nall six faces match D3X.FACE, in the cell D3X.FACE expects; every cell is one of the six blank variants')
sys.exit(1 if bad else 0)
