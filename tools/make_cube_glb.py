# -*- coding: utf-8 -*-
"""Author the die as what it is: a hard-edged cube, 6 planes, 12 triangles.

BUILT AGAINST D3X.FACE, WHICH IS THE WHOLE POINT. The game's 3D renderer already
holds a table saying, for every value, that value's [right, up, normal] basis in
mesh space - measured off the old 298KB Sketchfab model. Authoring the cube to
that table makes it a DROP-IN: no code change, no new constant, and the existing
orientation maths keeps working. Authoring it to anything else would mean
shipping a model AND editing a table, and getting either wrong shows the wrong
number on a die.

THE TWO RENDERERS DISAGREE ABOUT WHICH FACE HOLDS WHICH NUMBER, AND NOT BY A
COORDINATE CONVENTION. Converting D3.PLACE from CSS space (Y down) into three
space and comparing:

    value 1   D3X -X    D3 +Z     differ
    value 2   D3X +Y    D3 +Y     same
    value 3   D3X -Z    D3 +X     differ
    value 4   D3X +Z    D3 -X     differ
    value 5   D3X -Y    D3 -Y     same
    value 6   D3X +X    D3 -Z     differ

The map taking one to the other is [[0,0,-1],[0,1,0],[-1,0,0]], whose
determinant is -1. That is a REFLECTION, not a rotation: the DOM die and the
WebGL die are mirror-image dice, opposite chirality. Both satisfy
opposite-faces-sum-to-7, so neither looks wrong on its own and no single-sided
check could ever have caught it. Reported, not silently reconciled - which of
the two chiralities Denis wants is a design call, not mine.

NO RESAMPLING. Art is 120x120, atlas cells are 128x128, so each face sits at
native size with an edge-extended margin. Upscaling would resample hand-painted
art to gain nothing; a transparent margin bleeds to black in the mip chain,
which is the usual cause of dark seams on a cube.

EVERY ORIENTATION CLAIM IS ASSERTED, NOT ASSUMED: R x U == N per face (a
mirrored face reads as a correct one), opposite faces sum to 7, and the winding
is CCW seen from outside so no face is inside-out.
"""
import io, os, sys, json, struct, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GAME = os.path.join(ROOT, 'fark_proto.html')
ART = os.path.abspath(os.path.join(ROOT, '..', '..', '..', 'Art', 'Assets', 'Dice'))
# WRITE INTO THE WORKTREE, NOT THE MAIN CHECKOUT. The generator used to emit
# into ..\..\..ssets\models, i.e. the main checkout, while the git work
# happens here - so a routine `cp worktree main` afterwards silently
# overwrote the FRESH build with the STALE one, and the check page then
# rendered a model built from the wrong face table. Two copies of one asset,
# same bug shape as everything else this audit has removed. One location; the
# merge to main carries it, no manual copy.
OUTDIR = os.path.join(ROOT, 'assets', 'models')

CELL, ART_PX, COLS, ROWS = 128, 120, 3, 2
AW, AH = CELL * COLS, CELL * ROWS
H = 0.5

g = io.open(GAME, encoding='utf-8').read()


def balanced(src, start_tok, open_c, close_c):
    i = src.index(start_tok)
    d, j = 0, src.index(open_c, i)
    while j < len(src):
        if src[j] == open_c:
            d += 1
        elif src[j] == close_c:
            d -= 1
            if d == 0:
                return src[i:j + 1]
        j += 1
    sys.exit('GATE FAILED: unbalanced block at ' + start_tok)


# ---- the authority: D3X.FACE ---------------------------------------------
face_src = balanced(g, '  FACE:{1:', '{', '}')
FACE = {}
for m in re.finditer(r'(\d):\[\[(-?\d+),(-?\d+),(-?\d+)\],\[(-?\d+),(-?\d+),(-?\d+)\],'
                     r'\[(-?\d+),(-?\d+),(-?\d+)\]\]', face_src):
    v = int(m.group(1))
    gs = [int(x) for x in m.groups()[1:]]
    FACE[v] = (tuple(gs[0:3]), tuple(gs[3:6]), tuple(gs[6:9]))   # right, up, normal
if sorted(FACE) != [1, 2, 3, 4, 5, 6]:
    sys.exit('GATE FAILED: D3X.FACE did not yield values 1-6 (%s)' % sorted(FACE))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def neg(a):
    return tuple(-c for c in a)


# controls
for v, (R, U, N) in FACE.items():
    if cross(R, U) != N:
        sys.exit('GATE FAILED: value %d has R x U = %s, want N = %s. A mirrored face '
                 'renders as a correct one.' % (v, cross(R, U), N))
by_n = {N: v for v, (R, U, N) in FACE.items()}
for ax in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
    if by_n[ax] + by_n[neg(ax)] != 7:
        sys.exit('GATE FAILED: %s/%s hold %d and %d, which do not sum to 7'
                 % (ax, neg(ax), by_n[ax], by_n[neg(ax)]))

# ---- the chirality comparison, reported not enforced ---------------------
place_src = balanced(g, 'PLACE:[', '[', ']')
D3 = {}
for m in re.finditer(r'\{rx:-?\d+,ry:-?\d+,n:\[(-?\d+),(-?\d+),(-?\d+)\],img:(\d+)\}', place_src):
    n = (int(m.group(1)), -int(m.group(2)), int(m.group(3)))   # CSS Y is DOWN
    D3[int(m.group(4)) + 1] = n
mismatch = [v for v in sorted(FACE) if D3.get(v) != FACE[v][2]]

# ---- atlas, no resampling -------------------------------------------------
atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
cells = {}
for slot, v in enumerate(sorted(FACE)):
    src = os.path.join(ART, 'bone_%d.png' % v)
    if not os.path.exists(src):
        sys.exit('GATE FAILED: missing face art ' + src)
    im = Image.open(src).convert('RGBA')
    if im.size != (ART_PX, ART_PX):
        sys.exit('GATE FAILED: %s is %s, expected %dx%d' % (src, im.size, ART_PX, ART_PX))
    cx, cy = (slot % COLS) * CELL, (slot // COLS) * CELL
    pad = (CELL - ART_PX) // 2
    grown = Image.new('RGBA', (CELL, CELL))
    grown.paste(im.resize((CELL, CELL), Image.NEAREST), (0, 0))   # edge-extend base
    grown.paste(im, (pad, pad))                                    # exact art on top
    atlas.paste(grown, (cx, cy))
    cells[v] = (cx + pad, cy + pad)

buf = io.BytesIO()
atlas.save(buf, 'PNG', optimize=True)
atlas_bytes = buf.getvalue()

# ---- geometry -------------------------------------------------------------
pos, nrm, uv, idxs = [], [], [], []
for v in sorted(FACE):
    R, U, N = FACE[v]
    cx, cy = cells[v]
    u0, v0 = cx / AW, cy / AH
    u1, v1 = (cx + ART_PX) / AW, (cy + ART_PX) / AH
    base = len(pos)
    # BL, BR, TR, TL as seen from OUTSIDE, so the winding below is CCW from +N
    corners = [(-1, -1, u0, v1), (1, -1, u1, v1), (1, 1, u1, v0), (-1, 1, u0, v0)]
    for sr, su, tu, tv in corners:
        pos.append(tuple(H * (R[k] * sr + U[k] * su + N[k]) for k in range(3)))
        nrm.append(N)
        uv.append((tu, tv))
    idxs += [base, base + 1, base + 2, base, base + 2, base + 3]

# winding control: the geometric normal of the first triangle must equal N
for f, v in enumerate(sorted(FACE)):
    a, b, c = pos[f * 4], pos[f * 4 + 1], pos[f * 4 + 2]
    e1 = tuple(b[k] - a[k] for k in range(3))
    e2 = tuple(c[k] - a[k] for k in range(3))
    gn = cross(e1, e2)
    N = FACE[v][2]
    if not all((gn[k] > 0) == (N[k] > 0) and (gn[k] < 0) == (N[k] < 0) for k in range(3)):
        sys.exit('GATE FAILED: value %d winds inside-out (geometric normal %s vs %s)'
                 % (v, gn, N))


def pack(fmt, seq):
    out = bytearray()
    for t in seq:
        out += struct.pack(fmt, *t) if isinstance(t, tuple) else struct.pack(fmt, t)
    return bytes(out)


bp, bn, bu, bi = pack('<3f', pos), pack('<3f', nrm), pack('<2f', uv), pack('<H', idxs)
pad4 = lambda b: b + b'\x00' * ((4 - len(b) % 4) % 4)
blob = pad4(bp) + pad4(bn) + pad4(bu) + pad4(bi) + pad4(atlas_bytes)
o_n = len(pad4(bp)); o_u = o_n + len(pad4(bn)); o_i = o_u + len(pad4(bu)); o_img = o_i + len(pad4(bi))

gltf = {
  'asset': {'version': '2.0',
            'generator': 'fark make_cube_glb.py - hard cube, orientation from D3X.FACE'},
  'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'die'}],
  'meshes': [{'name': 'die', 'primitives': [{
      'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
  'materials': [{'name': 'die', 'doubleSided': False, 'pbrMetallicRoughness': {
      'baseColorTexture': {'index': 0}, 'metallicFactor': 0.0, 'roughnessFactor': 0.85}}],
  'textures': [{'source': 0, 'sampler': 0}],
  'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071}],
  'images': [{'bufferView': 4, 'mimeType': 'image/png'}],
  'accessors': [
    {'bufferView': 0, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3',
     'min': [-H, -H, -H], 'max': [H, H, H]},
    {'bufferView': 1, 'componentType': 5126, 'count': len(nrm), 'type': 'VEC3'},
    {'bufferView': 2, 'componentType': 5126, 'count': len(uv), 'type': 'VEC2'},
    {'bufferView': 3, 'componentType': 5123, 'count': len(idxs), 'type': 'SCALAR'}],
  'bufferViews': [
    {'buffer': 0, 'byteOffset': 0, 'byteLength': len(bp), 'target': 34962},
    {'buffer': 0, 'byteOffset': o_n, 'byteLength': len(bn), 'target': 34962},
    {'buffer': 0, 'byteOffset': o_u, 'byteLength': len(bu), 'target': 34962},
    {'buffer': 0, 'byteOffset': o_i, 'byteLength': len(bi), 'target': 34963},
    {'buffer': 0, 'byteOffset': o_img, 'byteLength': len(atlas_bytes)}],
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

nm = {(1,0,0):'+X',(-1,0,0):'-X',(0,1,0):'+Y',(0,-1,0):'-Y',(0,0,1):'+Z',(0,0,-1):'-Z'}
print('die_cube.glb   %6d bytes   %d verts, %d tris  (mesh alone %d bytes)'
      % (len(glb), len(pos), len(idxs) // 3, len(bp) + len(bn) + len(bu) + len(bi)))
print('atlas          %6d bytes   %dx%d, %d cells of %d holding %dpx art, no resampling'
      % (len(atlas_bytes), AW, AH, COLS * ROWS, CELL, ART_PX))
print('orientation from D3X.FACE:', ', '.join('%d=%s' % (v, nm[FACE[v][2]]) for v in sorted(FACE)))
print('  R x U == N on all six          : checked')
print('  opposite faces sum to 7        : checked')
print('  winding CCW from outside       : checked')
if mismatch:
    print('\nNOTE - the DOM renderer disagrees on %d of 6 values: %s'
          % (len(mismatch), ', '.join(str(v) for v in mismatch)))
    print('  D3.PLACE (converted to three space) puts them at: '
          + ', '.join('%d=%s' % (v, nm[D3[v]]) for v in mismatch))
    print('  The map between the two tables has determinant -1: they are MIRROR-IMAGE')
    print('  dice, not a coordinate convention. This cube follows D3X so it drops into')
    print('  the 3D renderer unchanged; matching the DOM die instead is a design call.')
