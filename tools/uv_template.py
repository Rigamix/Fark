# -*- coding: utf-8 -*-
"""Write a paintable UV template PNG for the die unwrap.

No image library is installed, so this writes the PNG by hand - IHDR, one
zlib-compressed IDAT, IEND. That is the whole format for a plain truecolour
image and zlib is stdlib.

The template matches tools/glb_unwrap.py exactly: a 3x2 atlas of equal cells
ordered by PIP NUMBER, using die3d_lab.html's own convention so opposite faces
sum to seven.

    +--------+--------+--------+
    |   1    |   2    |   3    |
    +--------+--------+--------+
    |   4    |   5    |   6    |
    +--------+--------+--------+

Each cell shows two boxes:
  the OUTER cell edge  - the seam, which sits on the bevel CENTRE
  the inner SAFE AREA  - the flat face. Pips go inside this.
The band between them is the inner half of the bevel. Paint it as the face
colour continuing over the edge; anything with detail in that band will be seen
edge-on and distorted.

BLEED MATTERS. Colour must run right up to the cell edge, never stop short - a
gap there shows as a bright seam line on the ridge, which is the most visible
place on the whole die.
"""
import sys, zlib, struct

W = H = 1024
COLS, ROWS = 3, 2
CW, CH = W // COLS, H // ROWS
# from glb_unwrap: island = flat + half bevel, so the flat face is
# flat/island of the cell. Measured 0.01277/0.01336 ~ 0.956 on the tightest axis.
SAFE = 0.955

BG      = (26, 22, 18)
CELLBG  = (238, 230, 214)
SAFEBG  = (250, 246, 238)
GRID    = (120, 108, 94)
SEAM    = (198, 72, 62)
NUMCOL  = (58, 48, 40)
GUTTER  = (214, 200, 178)

px = bytearray()
for _ in range(H):
    px.extend(bytes(BG) * W)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        px[o:o+3] = bytes(c)


def rect(x0, y0, x1, y1, c):
    for y in range(max(0,int(y0)), min(H,int(y1))):
        o = (y * W + max(0,int(x0))) * 3
        n = min(W,int(x1)) - max(0,int(x0))
        if n > 0:
            px[o:o+n*3] = bytes(c) * n


def frame(x0, y0, x1, y1, c, t=2):
    rect(x0, y0, x1, y0+t, c); rect(x0, y1-t, x1, y1, c)
    rect(x0, y0, x0+t, y1, c); rect(x1-t, y0, x1, y1, c)


def dashed(x0, y0, x1, y1, c, t=3, dash=14):
    for x in range(int(x0), int(x1), dash*2):
        rect(x, y0, min(x+dash, x1), y0+t, c); rect(x, y1-t, min(x+dash, x1), y1, c)
    for y in range(int(y0), int(y1), dash*2):
        rect(x0, y, x0+t, min(y+dash, y1), c); rect(x1-t, y, x1, min(y+dash, y1), c)


# blocky 7-segment digits: (x,y,w,h) strokes in a 0..1 box
SEG = {
 1:[(.45,.05,.10,.90)],
 2:[(.10,.05,.80,.10),(.80,.05,.10,.45),(.10,.45,.80,.10),(.10,.45,.10,.50),(.10,.85,.80,.10)],
 3:[(.10,.05,.80,.10),(.80,.05,.10,.90),(.10,.45,.80,.10),(.10,.85,.80,.10)],
 4:[(.10,.05,.10,.50),(.80,.05,.10,.90),(.10,.45,.80,.10)],
 5:[(.10,.05,.80,.10),(.10,.05,.10,.45),(.10,.45,.80,.10),(.80,.45,.10,.50),(.10,.85,.80,.10)],
 6:[(.10,.05,.80,.10),(.10,.05,.10,.90),(.10,.45,.80,.10),(.80,.45,.10,.50),(.10,.85,.80,.10)],
}


def digit(n, cx, cy, size, c):
    for (sx, sy, sw, sh) in SEG[n]:
        rect(cx - size/2 + sx*size, cy - size/2 + sy*size,
             cx - size/2 + (sx+sw)*size, cy - size/2 + (sy+sh)*size, c)


CELLOF = {1:(0,0), 2:(1,0), 3:(2,0), 4:(0,1), 5:(1,1), 6:(2,1)}
for pip, (col, row) in CELLOF.items():
    x0, y0 = col*CW, row*CH
    x1, y1 = x0+CW, y0+CH
    rect(x0, y0, x1, y1, GUTTER)                       # the bevel gutter
    sw, sh = CW*SAFE, CH*SAFE
    sx, sy = x0 + (CW-sw)/2, y0 + (CH-sh)/2
    rect(sx, sy, sx+sw, sy+sh, SAFEBG)                 # the flat face
    frame(x0, y0, x1, y1, SEAM, 3)                     # the seam = bevel centre
    dashed(sx, sy, sx+sw, sy+sh, GRID, 2, 12)          # safe-area guide
    digit(pip, x0+CW*0.5, y0+CH*0.5, min(CW,CH)*0.34, NUMCOL)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw.extend(px[y*W*3:(y+1)*W*3])


def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data +
            struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))


out = sys.argv[1] if len(sys.argv) > 1 else 'die_uv_template.png'
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
       + chunk(b'IEND', b''))
open(out, 'wb').write(png)
print('wrote %s  (%dx%d, %d bytes)' % (out, W, H, len(png)))
print('  3x2 atlas by pip number; red frame = seam on the bevel centre')
print('  dashed box = safe area (the flat face); keep pips inside it')
print('  bleed colour to the red edge - a gap there reads as a bright ridge line')
