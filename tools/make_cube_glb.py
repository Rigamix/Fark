# -*- coding: utf-8 -*-
"""Author the die as what it actually is: a hard-edged cube, 12 triangles.

WHY THIS EXISTS. The game currently has three incompatible ideas of a die:

  D3    six DOM planes, one set of 120x120 face PNGs, material = a CSS filter
  D3X   assets/models/die.glb - 298KB, 900 verts, a Sketchfab model with a 16%
        bevel and baked maps, material = a hex tint or a painted skin
  labs  two further meshes that are in neither of the above

Denis: "it's a simple not smoothed cube after all". So this builds that - 24
vertices, 6 quads, flat normals, one atlas - from the face art the CSS renderer
already uses. 900 verts and 298KB become 24 verts and a few KB, and the two
renderers can finally be looking at the same thing.

THE FACE MAPPING IS EXTRACTED, NOT INVENTED. D3.PLACE in fark_proto.html says
which face art sits on which normal, and this reads it rather than my deciding
what "face 3" means. The mapping it yields is checked for the property every
real die has - opposite faces sum to 7 - which is a control the extraction
cannot fake: a mis-parse would almost certainly break it.

NO RESAMPLING. The art is 120x120 and the atlas cells are 128x128, so each
face is placed at native size with a 4px margin that is EDGE-EXTENDED rather
than left transparent. Scaling 120 -> 128 would resample every pixel of hand-
painted art to gain nothing; a transparent margin would bleed to black in the
mip chain, which is the usual cause of dark seams on a cube.

HANDEDNESS IS ASSERTED, NOT ASSUMED. For each face, U x Vdown must equal -N.
Get this wrong and the die renders mirrored - readable, plausible, and wrong,
which is the hardest kind of wrong to notice on a dice face.
"""
import io, os, sys, json, struct, base64, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GAME = os.path.join(ROOT, 'fark_proto.html')
ART = os.path.abspath(os.path.join(ROOT, '..', '..', '..', 'Art', 'Assets', 'Dice'))
OUTDIR = os.path.abspath(os.path.join(ROOT, '..', '..', '..', 'assets', 'models'))

CELL, ART_PX = 128, 120
COLS, ROWS = 3, 2
AW, AH = CELL * COLS, CELL * ROWS

# ---- the face -> art mapping, read out of the game -----------------------
g = io.open(GAME, encoding='utf-8').read()
i = g.index('PLACE:[')
# BALANCED SCAN, not index(']'): the first ']' after PLACE:[ is the one closing
# n:[0,0,1] on the very first entry, which slices the array off mid-record and
# yields zero matches - caught by the count gate below on the first run.
_d, j = 0, g.index('[', i)
while j < len(g):
    if g[j] == '[':
        _d += 1
    elif g[j] == ']':
        _d -= 1
        if _d == 0:
            break
    j += 1
place = []
for m in re.finditer(r'\{rx:(-?\d+),ry:(-?\d+),n:\[(-?\d+),(-?\d+),(-?\d+)\],img:(\d+)\}', g[i:j]):
    rx, ry, nx, ny, nz, img = (int(x) for x in m.groups())
    place.append({'n': (nx, ny, nz), 'value': img + 1})
if len(place) != 6:
    sys.exit('GATE FAILED: PLACE did not yield 6 faces (%d)' % len(place))

# the control the extraction cannot fake
by_n = {p['n']: p['value'] for p in place}
for axis in [(0, 0, 1), (1, 0, 0), (0, 1, 0)]:
    neg = tuple(-c for c in axis)
    if axis not in by_n or neg not in by_n:
        sys.exit('GATE FAILED: missing an axis pair in PLACE')
    if by_n[axis] + by_n[neg] != 7:
        sys.exit('GATE FAILED: opposite faces %s/%s sum to %d, not 7 - the parse slid'
                 % (axis, neg, by_n[axis] + by_n[neg]))

# ---- the atlas, no resampling --------------------------------------------
atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
cells = {}
for idx, p in enumerate(place):
    val = p['value']
    src = os.path.join(ART, 'bone_%d.png' % val)
    if not os.path.exists(src):
        sys.exit('GATE FAILED: missing face art ' + src)
    im = Image.open(src).convert('RGBA')
    if im.size != (ART_PX, ART_PX):
        sys.exit('GATE FAILED: %s is %s, expected %dx%d - resampling was not wanted'
                 % (src, im.size, ART_PX, ART_PX))
    cx, cy = (idx % COLS) * CELL, (idx // COLS) * CELL
    pad = (CELL - ART_PX) // 2
    # edge-extend into the margin so mips do not pull in transparent black
    grown = Image.new('RGBA', (CELL, CELL))
    grown.paste(im.resize((CELL, CELL), Image.NEAREST), (0, 0))   # cheap dilation base
    grown.paste(im, (pad, pad))                                    # exact art on top
    atlas.paste(grown, (cx, cy))
    cells[p['n']] = (cx + pad, cy + pad)

atlas_png = io.BytesIO()
atlas.save(atlas_png, 'PNG', optimize=True)
atlas_bytes = atlas_png.getvalue()

# ---- geometry: 24 verts, flat normals, 12 tris ---------------------------
BASIS = {   # N: (U, Vdown) - U is +u across the face, Vdown is +v down it
    (0, 0, 1):  ((1, 0, 0),  (0, -1, 0)),
    (0, 0, -1): ((-1, 0, 0), (0, -1, 0)),
    (1, 0, 0):  ((0, 0, -1), (0, -1, 0)),
    (-1, 0, 0): ((0, 0, 1),  (0, -1, 0)),
    (0, 1, 0):  ((1, 0, 0),  (0, 0, 1)),
    (0, -1, 0): ((1, 0, 0),  (0, 0, -1)),
}
def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

pos, nrm, uv, idxs = [], [], [], []
H = 0.5
for p in place:
    n = p['n']
    u, vd = BASIS[n]
    if cross(u, vd) != tuple(-c for c in n):
        sys.exit('GATE FAILED: handedness for face %s - U x Vdown is %s, want %s. '
                 'A mirrored die reads as a correct one.' % (n, cross(u, vd), tuple(-c for c in n)))
    cx, cy = cells[n]
    u0, v0 = cx / AW, cy / AH
    u1, v1 = (cx + ART_PX) / AW, (cy + ART_PX) / AH
    base = len(pos)
    for su, sv, tu, tv in ((-1, -1, u0, v0), (1, -1, u1, v0), (1, 1, u1, v1), (-1, 1, u0, v1)):
        pos.append(tuple(H * (u[k]*su + vd[k]*sv + n[k]) for k in range(3)))
        nrm.append(n)
        uv.append((tu, tv))
    idxs += [base, base+1, base+2, base, base+2, base+3]

def pack(fmt, seq):
    b = bytearray()
    for t in seq:
        b += struct.pack(fmt, *t) if isinstance(t, tuple) else struct.pack(fmt, t)
    return bytes(b)

bin_pos, bin_nrm, bin_uv = pack('<3f', pos), pack('<3f', nrm), pack('<2f', uv)
bin_idx = pack('<H', idxs)
def pad4(b): return b + b'\x00' * ((4 - len(b) % 4) % 4)
blob = pad4(bin_pos) + pad4(bin_nrm) + pad4(bin_uv) + pad4(bin_idx) + pad4(atlas_bytes)
o_pos = 0
o_nrm = len(pad4(bin_pos))
o_uv = o_nrm + len(pad4(bin_nrm))
o_idx = o_uv + len(pad4(bin_uv))
o_img = o_idx + len(pad4(bin_idx))

gltf = {
  'asset': {'version': '2.0', 'generator': 'fark make_cube_glb.py - hard-edged cube, faces from D3.PLACE'},
  'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'die'}],
  'meshes': [{'name': 'die', 'primitives': [{
      'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
  'materials': [{'name': 'die', 'pbrMetallicRoughness': {
      'baseColorTexture': {'index': 0}, 'metallicFactor': 0.0, 'roughnessFactor': 0.85}}],
  'textures': [{'source': 0, 'sampler': 0}],
  'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071}],
  'images': [{'bufferView': 4, 'mimeType': 'image/png'}],
  'accessors': [
    {'bufferView': 0, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3',
     'min': [-H, -H, -H], 'max': [H, H, H]},
    {'bufferView': 1, 'componentType': 5126, 'count': len(nrm), 'type': 'VEC3'},
    {'bufferView': 2, 'componentType': 5126, 'count': len(uv), 'type': 'VEC2'},
    {'bufferView': 3, 'componentType': 5123, 'count': len(idxs), 'type': 'SCALAR'},
  ],
  'bufferViews': [
    {'buffer': 0, 'byteOffset': o_pos, 'byteLength': len(bin_pos), 'target': 34962},
    {'buffer': 0, 'byteOffset': o_nrm, 'byteLength': len(bin_nrm), 'target': 34962},
    {'buffer': 0, 'byteOffset': o_uv,  'byteLength': len(bin_uv),  'target': 34962},
    {'buffer': 0, 'byteOffset': o_idx, 'byteLength': len(bin_idx), 'target': 34963},
    {'buffer': 0, 'byteOffset': o_img, 'byteLength': len(atlas_bytes)},
  ],
  'buffers': [{'byteLength': len(blob)}],
}
js = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
js += b' ' * ((4 - len(js) % 4) % 4)
glb = (b'glTF' + struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(blob))
       + struct.pack('<I', len(js)) + b'JSON' + js
       + struct.pack('<I', len(blob)) + b'BIN\x00' + blob)

os.makedirs(OUTDIR, exist_ok=True)
open(os.path.join(OUTDIR, 'die_cube.glb'), 'wb').write(glb)
open(os.path.join(OUTDIR, 'die_cube_atlas.png'), 'wb').write(atlas_bytes)

print('die_cube.glb   %6d bytes   %d verts, %d tris' % (len(glb), len(pos), len(idxs) // 3))
print('atlas          %6d bytes   %dx%d, %d cells of %d with %dpx art, no resampling'
      % (len(atlas_bytes), AW, AH, COLS * ROWS, CELL, ART_PX))
print('faces (from D3.PLACE):', ', '.join('%s=%d' % (p['n'], p['value']) for p in place))
print('opposite pairs sum to 7: checked')
print('handedness U x Vdown == -N: checked on all six')
