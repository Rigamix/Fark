# -*- coding: utf-8 -*-
"""Read the pixels around a held card and say whether a glow was painted.

getComputedStyle said the glow was there three times while Denis saw
nothing, so this reads the composited screenshot instead. No dependency
on any imaging library - a PNG is IHDR + zlib(IDAT) + per-row filters,
and decoding it here is cheaper than adding a package.

The test: walk outward from the card's edge and measure how WARM each
ring is (R-B, which separates gold from the dark wood underneath).
A painted halo falls off smoothly over its blur radius. No halo is a
flat reading at the table's own warmth from the first ring out.

    python tools/glow_pixels.py shot.png X Y W H DPR
"""
import sys, zlib, struct


def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', 'not a png'
    pos, idat, w, h, depth, ctype = 8, b'', 0, 0, 0, 0
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        body = d[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, depth, ctype = struct.unpack('>IIBB', body[:10])
        elif typ == b'IDAT':
            idat += body
        elif typ == b'IEND':
            break
        pos += 12 + ln
    assert depth == 8, 'depth %d unsupported' % depth
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * nch
    out, prev = bytearray(w * h * nch), bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for i in range(stride):
            a = line[i - nch] if i >= nch else 0
            b = prev[i]
            c = prev[i - nch] if i >= nch else 0
            if f == 1:   line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, nch, out


def main():
    path, X, Y, W, H, DPR = sys.argv[1], *[float(a) for a in sys.argv[2:7]]
    w, h, nch, px = read_png(path)
    X, Y, W, H = X * DPR, Y * DPR, W * DPR, H * DPR

    def at(x, y):
        x, y = int(x), int(y)
        if x < 0 or y < 0 or x >= w or y >= h:
            return None
        i = (y * w + x) * nch
        return px[i], px[i + 1], px[i + 2]

    print('image %dx%d  card @%d,%d %dx%d (device px)' % (w, h, X, Y, W, H))
    # rings outward from the card's left, right and top edges
    print('\n dist |  left        right       top      | warmth(R-B)')
    print(' -----+-----------------------------------+------------')
    for dist in (2, 5, 9, 14, 20, 28, 40, 60):
        cy = Y + H * 0.5
        cx = X + W * 0.5
        samples = [at(X - dist, cy), at(X + W + dist, cy), at(cx, Y - dist)]
        good = [s for s in samples if s]
        if not good:
            continue
        warm = sum(s[0] - s[2] for s in good) / len(good)
        txt = '  '.join('%3d,%3d,%3d' % s if s else '   -,  -,  -' for s in samples)
        print(' %4d | %s | %6.1f' % (dist, txt, warm))

    # the table's own warmth, far from any card
    far = [at(X - 160, Y + H * 0.5), at(X + W + 160, Y + H * 0.5)]
    far = [s for s in far if s]
    if far:
        base = sum(s[0] - s[2] for s in far) / len(far)
        print('\n table baseline warmth (160px away): %.1f' % base)
        near = at(X - 3, Y + H * 0.5)
        if near:
            print(' at the card edge:                   %.1f' % (near[0] - near[2]))
            print('\n VERDICT: %s' % ('GLOW PAINTED' if (near[0] - near[2]) - base > 12
                                      else 'NO GLOW - the edge reads as bare table'))


main()
