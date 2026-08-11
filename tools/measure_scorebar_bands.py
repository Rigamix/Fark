# -*- coding: utf-8 -*-
"""Where is the frame's channel, and where is the fill's ink?

P589 nudged the fill up 1cqw on the strength of "the two files are separate
masters and their bands do not have to agree to the pixel". Denis has since
rebuilt ScoreBar_new_fill.png to match the frame exactly, so the honest move is
to MEASURE the two bands rather than keep hand-tuning an offset - and to delete
the offset only if the measurement says it is now zero.

WHAT COUNTS AS THE BAND. The frame's channel is the transparent/dark trough the
fill is meant to sit in; the fill's band is simply where its ink is. Both are
read as ALPHA runs down a column, at several x positions, because a single
column can land on a rivet or a highlight and give a band nobody would draw.

READ AT MATCHED x. The frame and the fill are stretched to the same box, so a
column at x in one is the same screen column as x in the other. Columns are
picked inside the left half's fill travel (the fill grows from the outer edge),
away from the centre badge and away from the flags.
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'Art', 'Assets', 'Match')

frame = Image.open(os.path.join(M, 'ScoreBar_new.png')).convert('RGBA')
fill  = Image.open(os.path.join(M, 'ScoreBar_new_fill.png')).convert('RGBA')
print('frame %s   fill %s   %s' % (frame.size, fill.size,
      'SAME CANVAS' if frame.size == fill.size else '*** DIFFERENT CANVAS ***'))

W, H = frame.size
fa, la = frame.load(), fill.load()

# columns inside the left bar's travel: the flags end ~15.9% and the badge
# starts 43.5%, so sample between.
COLS = [int(W * p) for p in (0.19, 0.24, 0.29, 0.34, 0.39)]

def alpha_run(px, x, thresh=40):
    """first and last row at x whose alpha clears thresh"""
    top = bot = None
    for y in range(H):
        if px[x, y][3] > thresh:
            if top is None:
                top = y
            bot = y
    return top, bot

def opaque_run(px, x, thresh=215):
    """first/last row at x that is essentially solid - the frame's own plate,
       whose INNER edges bound the channel the fill sits in"""
    rows = [y for y in range(H) if px[x, y][3] > thresh]
    return (rows[0], rows[-1]) if rows else (None, None)

def channel(px, x):
    """The trough: inside the frame's silhouette, the LONGEST CONTIGUOUS dark
       run.

       CONTIGUITY IS THE WHOLE CORRECTION. The first version took the first and
       last row below the cut without requiring them to be connected, so it
       swallowed the dark outer OUTLINES at both extremes and returned the whole
       plank silhouette (rows 93..380) while calling it the channel - the trough
       is rows ~137..333. It happened not to change the verdict, because the two
       light rims are near-identical thicknesses (35 and 36 rows) and the
       silhouette's centre therefore lands within 2 rows of the trough's. That is
       luck, not method: an asymmetric frame would have been certified centred
       while visibly sitting high."""
    top, bot = alpha_run(px, x)
    if top is None:
        return None, None
    lum = [(y, sum(px[x, y][:3]) / 3.0) for y in range(top, bot + 1)]
    if not lum:
        return None, None
    dark = min(v for _, v in lum)
    light = max(v for _, v in lum)
    cut = dark + (light - dark) * 0.45
    best, run = None, None
    for y, v in lum:
        if v <= cut:
            run = [y, y] if run is None else [run[0], y]
            if best is None or run[1] - run[0] > best[1] - best[0]:
                best = list(run)
        else:
            run = None
    return (best[0], best[1]) if best else (None, None)

print('\n%-7s | %-21s | %-21s | delta' % ('x', 'FRAME channel (rows)', 'FILL ink (rows)'))
print('-' * 74)
deltas_top, deltas_bot = [], []
for x in COLS:
    ct, cb = channel(fa, x)
    it, ib = alpha_run(la, x)
    if None in (ct, cb, it, ib):
        print('%-7d | %-21s | %-21s |' % (x, (ct, cb), (it, ib)))
        continue
    dt, db = it - ct, ib - cb
    deltas_top.append(dt); deltas_bot.append(db)
    print('%-7d | %4d..%-4d  (%5.2f%%..%5.2f%%) | %4d..%-4d  (%5.2f%%..%5.2f%%) | top %+d  bot %+d'
          % (x, ct, cb, 100.0*ct/H, 100.0*cb/H, it, ib, 100.0*it/H, 100.0*ib/H, dt, db))

if deltas_top:
    mt = sum(deltas_top) / len(deltas_top)
    mb = sum(deltas_bot) / len(deltas_bot)
    ctr = (mt + mb) / 2.0
    print('\nmean top delta %+.1f px   mean bottom delta %+.1f px   centre drift %+.1f px'
          % (mt, mb, ctr))
    print('centre drift as %% of bar height: %+.3f%%' % (100.0 * ctr / H))
    # the bar renders ~430 CSS px wide at the design width; height = 430*933/3795
    css_h = 430.0 * H / W
    print('at the 430px design width the bar is %.1f css px tall, so that drift is %+.2f css px'
          % (css_h, css_h * ctr / H))
    print('\nVERDICT: %s' % ('bands coincide - the fill needs NO offset (top:0)'
                             if abs(ctr) <= 2 else
                             'bands still differ - an offset of %+.3f%% of height is warranted' % (100.0*ctr/H)))
