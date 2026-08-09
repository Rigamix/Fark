# -*- coding: utf-8 -*-
"""Write two PNGs for the die unwrap: a paintable template, and a wireframe guide.

  die_uv_template.png  what to paint over
  die_uv_layout.png    the actual UV islands, drawn from the GLB's real UVs

No image library is installed, so both are written by hand - IHDR, one
zlib-compressed IDAT, IEND. That is the whole format for a truecolour PNG and
zlib is stdlib.

WHY THE TEMPLATE CHANGED. The first version drew a distinct gutter band and a
red frame at every cell edge. On the die that read as "thin areas of texture on
the bevels" - because a bevel is spanned by the outer strip of TWO neighbouring
cells, so two half-gutters plus two frame lines met on the ridge and showed as a
band. The unwrap was right; the template was drawing furniture onto it.

So now: each face's colour FILLS ITS WHOLE CELL, right to the edge. Two faces
meet exactly on the ridge line and there is nothing in between. The only guide
is a dashed line marking where the flat face ends, and that is a guide to paint
over, not a thing to keep.

Each face gets a slightly different tint. That is deliberate - it makes the seam
visible on the model while checking, without putting a band there. Paint over
the tints and the seams become invisible, which is the point.

BLEED STILL MATTERS. Colour must reach the cell edge. A gap there shows as a
bright line along the ridge, the most visible place on the die.
"""
import sys, zlib, struct, json, os

# 2048x1024 with a 4x2 grid: cells of exactly 512x512. A 3x2 grid in a square
# image gave 341x512 cells and stretched every face 1.5x vertically. Both
# dimensions stay powers of two so mipmapping is safe on WebGL1 as well as 2.
W, H = 2048, 1024
COLS, ROWS = 4, 2
CW, CH = W // COLS, H // ROWS
SAFE = 0.955     # the flat face as a fraction of the cell - from glb_unwrap

CELLOF = {1:(0,0), 2:(1,0), 3:(2,0), 4:(0,1), 5:(1,1), 6:(2,1)}
# six parchment tints, distinguishable but all in the deck's range
TINT = {1:(238,231,216), 2:(233,225,208), 3:(228,219,200),
        4:(223,213,192), 5:(218,207,184), 6:(213,201,176)}
GUIDE  = (150, 136, 118)
NUMCOL = (176, 160, 138)
INK    = (58, 48, 40)


def blank(w, h, c):
    return bytearray(bytes(c) * w * h)


def rect(px, w, h, x0, y0, x1, y1, c):
    x0 = max(0, int(x0)); x1 = min(w, int(x1))
    for y in range(max(0, int(y0)), min(h, int(y1))):
        o = (y * w + x0) * 3
        n = x1 - x0
        if n > 0:
            px[o:o+n*3] = bytes(c) * n


def dashed(px, w, h, x0, y0, x1, y1, c, t=2, dash=13):
    for x in range(int(x0), int(x1), dash*2):
        rect(px, w, h, x, y0, min(x+dash, x1), y0+t, c)
        rect(px, w, h, x, y1-t, min(x+dash, x1), y1, c)
    for y in range(int(y0), int(y1), dash*2):
        rect(px, w, h, x0, y, x0+t, min(y+dash, y1), c)
        rect(px, w, h, x1-t, y, x1, min(y+dash, y1), c)


def line(px, w, h, x0, y0, x1, y1, c):
    dx, dy = abs(x1-x0), abs(y1-y0)
    n = max(int(dx), int(dy), 1)
    for i in range(n+1):
        x = int(round(x0 + (x1-x0)*i/n)); y = int(round(y0 + (y1-y0)*i/n))
        if 0 <= x < w and 0 <= y < h:
            o = (y*w + x)*3
            px[o:o+3] = bytes(c)


SEG = {
 1:[(.42,.06,.16,.88)],
 2:[(.08,.06,.84,.15),(.77,.06,.15,.44),(.08,.43,.84,.15),(.08,.43,.15,.48),(.08,.85,.84,.15)],
 3:[(.08,.06,.84,.15),(.77,.06,.15,.88),(.08,.43,.84,.15),(.08,.85,.84,.15)],
 4:[(.08,.06,.15,.52),(.77,.06,.15,.88),(.08,.43,.84,.15)],
 5:[(.08,.06,.84,.15),(.08,.06,.15,.44),(.08,.43,.84,.15),(.77,.43,.15,.48),(.08,.85,.84,.15)],
 6:[(.08,.06,.84,.15),(.08,.06,.15,.88),(.08,.43,.84,.15),(.77,.43,.15,.48),(.08,.85,.84,.15)],
}


def digit(px, w, h, n, cx, cy, size, c):
    for (sx, sy, sw, sh) in SEG[n]:
        rect(px, w, h, cx-size/2+sx*size, cy-size/2+sy*size,
             cx-size/2+(sx+sw)*size, cy-size/2+(sy+sh)*size, c)


def write_png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0); raw.extend(px[y*w*3:(y+1)*w*3])
    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag+data) & 0xffffffff))
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    open(path, 'wb').write(png)
    return len(png)


# ---------- 1. the paintable template ------------------------------------
px = blank(W, H, (20, 17, 14))
for pip, (col, row) in CELLOF.items():
    x0, y0 = col*CW, row*CH
    # the face colour FILLS THE CELL - no frame, no gutter band. Two faces meet
    # exactly on the ridge and there is nothing between them.
    rect(px, W, H, x0, y0, x0+CW, y0+CH, TINT[pip])
    sw, sh = CW*SAFE, CH*SAFE
    sx, sy = x0+(CW-sw)/2, y0+(CH-sh)/2
    dashed(px, W, H, sx, sy, sx+sw, sy+sh, GUIDE, 2, 13)
    digit(px, W, H, pip, x0+CW*0.5, y0+CH*0.5, min(CW, CH)*0.30, NUMCOL)
n1 = write_png(sys.argv[1] if len(sys.argv) > 1 else 'die_uv_template.png', W, H, px)

# ---------- 2. the wireframe layout guide, from the real UVs --------------
glb = sys.argv[3] if len(sys.argv) > 3 else 'out3d/die_new_uv.glb'
out2 = sys.argv[2] if len(sys.argv) > 2 else 'die_uv_layout.png'
if os.path.exists(glb):
    raw = open(glb, 'rb').read()
    js = binc = None; off = 12
    while off < len(raw):
        clen, ctype = struct.unpack('<II', raw[off:off+8])
        body = raw[off+8:off+8+clen]
        if ctype == 0x4E4F534A: js = json.loads(body.decode('utf-8').rstrip('\x00 '))
        elif ctype == 0x004E4942: binc = body
        off += 8 + clen + ((4 - (clen % 4)) % 4 if clen % 4 else 0)
    prim = js['meshes'][0]['primitives'][0]

    def rd(i, n, fmt, size):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
        base = bv.get('byteOffset',0)+a.get('byteOffset',0)
        stride = bv.get('byteStride') or size*n
        return [struct.unpack_from('<'+fmt*n, binc, base+k*stride) for k in range(a['count'])]

    uv = rd(prim['attributes']['TEXCOORD_0'], 2, 'f', 4)
    ia = js['accessors'][prim['indices']]
    idx = [t[0] for t in rd(prim['indices'], 1, 'I' if ia['componentType']==5125 else 'H',
                            4 if ia['componentType']==5125 else 2)]

    g = blank(W, H, (250, 247, 241))
    # the cell grid, so the islands can be read against the atlas
    for c in range(1, COLS): rect(g, W, H, c*CW-1, 0, c*CW+1, H, (214,206,192))
    for r in range(1, ROWS): rect(g, W, H, 0, r*CH-1, W, r*CH+1, (214,206,192))
    # every triangle edge, exactly as the file stores it
    for t in range(0, len(idx), 3):
        a, b, c = idx[t], idx[t+1], idx[t+2]
        for (p, q) in ((a,b), (b,c), (c,a)):
            line(g, W, H, uv[p][0]*W, uv[p][1]*H, uv[q][0]*W, uv[q][1]*H, (70,60,52))
    for pip, (col, row) in CELLOF.items():
        digit(g, W, H, pip, col*CW+CW*0.5, row*CH+CH*0.5, min(CW,CH)*0.22, (198,120,96))
    n2 = write_png(out2, W, H, g)
    print('wrote %s  (%dx%d, %d bytes)  - paint over this' % (sys.argv[1] if len(sys.argv)>1 else 'die_uv_template.png', W, H, n1))
    print('wrote %s  (%dx%d, %d bytes)  - the real UV islands from the GLB' % (out2, W, H, n2))
    print('  %d triangles drawn' % (len(idx)//3))
else:
    print('wrote template only - %s not found for the wireframe' % glb)
print()
print('  face colour fills each cell to the edge: two faces meet ON the ridge,')
print('  with nothing in between. The dashed box is where the flat face ends.')
print('  Tints differ per face so the seam is visible while checking; paint over')
print('  them and the seams disappear, which is the point.')
