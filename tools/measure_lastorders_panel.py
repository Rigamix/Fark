# -*- coding: utf-8 -*-
"""Where does the Last Orders sign actually put its parchment and its icons?

TWO QUESTIONS, and they have different answers.

  1. "texts and symbols are way too high on the panel" - the labels and hearts
     are DOM and can move; the moon and the mug are PAINTED INTO the sign. If
     the painted icons sit high in the parchment then no CSS can lower the row,
     because moving the hearts alone would break the three-icon line. P573's
     note asserts exactly that. It is an assertion, so it gets measured.

  2. "panel is still too high" - P573 pinned .lo-sign at top:8% on the reasoning
     that the panel's dark ceiling/rope portion must overlap the BACKGROUND's
     dark ceiling or a seam opens, and put that limit at 8.7%. That number
     decides whether "lower the panel" is free or costs a seam, so it is
     re-derived here from the two images rather than quoted.

Bands are read as row statistics over OPAQUE pixels only - the sign is a cutout
and counting transparent rows as "dark" would put the ceiling everywhere.
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LO = os.path.join(ROOT, 'Art', 'Assets', 'LastOrders')

panel = Image.open(os.path.join(LO, 'LastOrders_panel.png')).convert('RGBA')
bg    = Image.open(os.path.join(LO, 'LastOrders.png')).convert('RGBA')
PW, PH = panel.size
BW, BH = bg.size
print('panel %s   background %s' % (panel.size, bg.size))

pp = panel.load()

def row_stats(y):
    """over opaque pixels in row y: coverage, mean brightness, dark fraction"""
    op = [pp[x, y] for x in range(PW) if pp[x, y][3] > 40]
    if not op:
        return 0.0, None, None
    lum = [sum(c[:3]) / 3.0 for c in op]
    return (len(op) / float(PW), sum(lum) / len(lum),
            sum(1 for v in lum if v < 110) / float(len(lum)))

print('\n── the sign, row by row (%% of its own height) ──')
print(' y      %h     cover  meanLum  dark%   read')
prev = None
for y in range(0, PH, max(1, PH // 46)):
    cov, lum, dk = row_stats(y)
    if lum is None:
        continue
    tag = ''
    if lum < 90:  tag = 'dark (ceiling/beam/rope)'
    elif lum > 165 and dk < 0.06: tag = 'CLEAR PARCHMENT'
    elif lum > 150: tag = 'parchment + ink'
    print(' %-6d %5.1f%%  %5.2f  %6.1f  %5.1f%%  %s' % (y, 100.0*y/PH, cov, lum, 100*dk, tag))

# ── the parchment band and where its ink actually is ──
# threshold set FROM the row dump, not guessed: the parchment reads 129..138
# mean and the frame either side reads 41..77, so 110 separates them with room
# on both sides. The first version used >150 and matched NOTHING, which printed
# as a silently missing section rather than as an error - the parchment is not
# as bright as "parchment" suggests.
parch = [y for y in range(PH) if (lambda s: s[1] is not None and s[1] > 110 and s[0] > 0.5)(row_stats(y))]
if parch:
    p0, p1 = parch[0], parch[-1]
    print('\nparchment rows %d..%d  (%.1f%%..%.1f%% of the sign)' % (p0, p1, 100.0*p0/PH, 100.0*p1/PH))
    # THE BASELINE IS THE PARCHMENT ITSELF. A flat "dark > 4.5%" threshold
    # called almost the whole parchment inked, because the aged texture alone
    # runs 4.3-4.8% dark - that measured the paper, not the drawing. Take the
    # parchment's own median as zero and only count rows well above it.
    dks = sorted(row_stats(y)[2] for y in range(p0, p1 + 1))
    base = dks[len(dks) // 2]
    cut = base + 0.045
    print('parchment grain baseline %.1f%% dark; counting ink above %.1f%%'
          % (100 * base, 100 * cut))
    bands, run = [], None
    for y in range(p0, p1 + 1):
        if row_stats(y)[2] > cut:
            run = [y, y] if run is None else [run[0], y]
        elif run is not None:
            if run[1] - run[0] > PH * 0.01:
                bands.append(tuple(run))
            run = None
    if run is not None and run[1] - run[0] > PH * 0.01:
        bands.append(tuple(run))
    span = float(p1 - p0)
    for (i0, i1) in bands:
        print('  INK BAND rows %d..%d = %.1f%%..%.1f%% of the sign, %.1f%%..%.1f%% OF THE PARCHMENT'
              % (i0, i1, 100.0*i0/PH, 100.0*i1/PH, 100.0*(i0-p0)/span, 100.0*(i1-p0)/span))
    if bands:
        # the ICON band is the topmost one - the lower band is the painted
        # corner flourishes, which are decoration and are meant to stay put.
        i0, i1 = bands[0]
        above, below = (i0 - p0) / span, (p1 - i1) / span
        print('  -> icon band: clear parchment ABOVE %.1f%%, BELOW %.1f%% (of the parchment)'
              % (100*above, 100*below))
        drop = (below - above) / 2.0
        print('  -> centring it needs it %.1f%% of the parchment lower = %.2f%% OF THE SIGN'
              % (100 * drop, 100 * drop * span / PH))

# ── the seam: how far down does the background stay dark? ──
bl = bg.load()
print('\n── background: how far down the ceiling stays dark ──')
lastdark = None
for y in range(0, BH, max(1, BH // 60)):
    row = [bl[x, y] for x in range(0, BW, max(1, BW // 60))]
    lum = sum(sum(c[:3]) / 3.0 for c in row) / len(row)
    if lum < 60:
        lastdark = y
    if y < BH * 0.42:
        print('  %5.1f%%  meanLum %6.1f%s' % (100.0*y/BH, lum, '   <- dark' if lum < 60 else ''))
if lastdark is not None:
    print('background stays dark to %.1f%% of its height' % (100.0*lastdark/BH))

# how much of the sign image is its dark top (ceiling + ropes)?
darktop = 0
for y in range(PH):
    cov, lum, dk = row_stats(y)
    if lum is None or lum < 95:
        darktop = y
    else:
        break
print('sign: dark top runs to row %d (%.1f%% of the sign image)' % (darktop, 100.0*darktop/PH))
