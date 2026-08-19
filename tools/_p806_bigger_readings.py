# -*- coding: utf-8 -*-
"""P806: the Last Orders readings grow up - bigger icons, bigger labels,
labels clear of the row.

Denis: "make texts quite larger, move them up so they don't overlap the
icons. Make the moon and mug icons larger."

Derived-art regeneration (supersedes P805's; master untouched): the
moon and mug are cut from the master, scaled x1.25, and pasted centred
on the parchment's centre line (y~406); their original bboxes filled
with clean parchment sampled below them. Centres nudge inward (moon
cx 155, mug cx 680) so the scaled icons clear the painted corner
flourishes. Hearts grow with them (8.2 -> 9.4cqw) so the row still
reads as one; the night number grows to match (7.6 -> 8.4cqw).

Labels: 2.55 -> 3.5cqw, lifted into the band between the beam and the
icon row (top 55.2%, height 5%) - above the icons, no overlap.
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── the derived panel, regenerated from the master ──
im = Image.open(os.path.join(ROOT, 'Art/Assets/LastOrders/LastOrders_panel.png')).convert('RGBA')
CY = 406          # parchment inner centre line
SCALE = 1.25
JOBS = [          # (bbox with margin, new centre x)
    ((98, 294, 201, 397), 155),
    ((598, 296, 783, 400), 680),
]
# sample all fills first, then erase, then paste - order keeps sources clean
fills = []
icons = []
for (x0, y0, x1, y1), cx in JOBS:
    h = y1 - y0
    fills.append(((x0, y0), im.crop((x0, y1, x1, y1 + h)).copy()))
    icons.append((im.crop((x0, y0, x1, y1)).copy(), cx))
for pos, f in fills:
    im.paste(f, pos)
for icon, cx in icons:
    w2 = int(icon.width * SCALE)
    h2 = int(icon.height * SCALE)
    big = icon.resize((w2, h2), Image.LANCZOS)
    im.paste(big, (cx - w2 // 2, CY - h2 // 2), big)
im.save(os.path.join(ROOT, 'Art/Assets/LastOrders/optimized/LastOrders_panel_opt.webp'),
        'WEBP', quality=88, method=6)
print('derived panel regenerated (icons x%.2f at y%d)' % (SCALE, CY))

# ── the CSS ──
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    s = s.replace(old, new)
    edits.append(label)


sub(".lo-screen .lo-c{position:absolute;top:65.2%;height:3.6%;/* P805: the icon row is centred in the parchment now (art shifted +59px in the derived webp) */",
    ".lo-screen .lo-c{position:absolute;top:55.2%;height:5.0%;/* P806: labels in the band between beam and icon row - clear of the icons */",
    'labels above the row')

sub(".lo-screen .lo-lab{font-size:2.55cqw;letter-spacing:.08em;white-space:nowrap}",
    ".lo-screen .lo-lab{font-size:3.5cqw;letter-spacing:.08em;white-space:nowrap}",
    'labels quite larger')

sub("top:68.7%;height:14.5%;/* P805: the moon moved to the parchment centre */",
    "top:67.0%;height:14.5%;/* P806: centred on the icon row's centre line */",
    'night number recentred')

sub("font-family:'JMH Beda',serif;font-size:7.6cqw;color:#3a2812;",
    "font-family:'JMH Beda',serif;font-size:8.4cqw;color:#3a2812;",
    'night number larger')

sub("top:69.6%;height:13.0%;/* P805: centred on the moved icon row */",
    "top:67.7%;height:13.0%;/* P806: centred on the icon row's centre line */",
    'hearts recentred')

sub(".lo-screen .lo-night{position:absolute;left:23.5%;width:8.5%;",
    ".lo-screen .lo-night{position:absolute;left:26.6%;width:8.5%;/* P806: right of the GROWN moon */",
    'night number clears the bigger moon')

sub(".lo-screen .lo-heart{height:8.2cqw;width:auto;object-fit:contain;display:block}",
    ".lo-screen .lo-heart{height:9.4cqw;width:auto;object-fit:contain;display:block}/* P806: grown with the moon and mug so the row reads as one */",
    'hearts grow with the row')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
