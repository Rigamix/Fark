# -*- coding: utf-8 -*-
"""P807: Last Orders sign tune, per Denis.

"lower text, larger. Move NIGHTS to the right a bit and NEW ROSTER to
the left a bit. Move moon icon and number to the left. You scaled up
the hearts which I didn't ask."

- Labels: 3.5 -> 4.0cqw, band lowered (55.2 -> 55.9%) toward the row.
- NIGHTS column +2.5% right; NEW ROSTER column -2.5% left.
- Moon: cx 155 -> 150 in the derived art - the painted left flourish
  ends at x=85 and the x1.25 moon's edge lands exactly there, so five
  master-pixels is ALL the leftward room that exists without covering
  the flourish. The night number follows further (26.6 -> 25.3%).
- Hearts: back to 8.2cqw - the P806 scale-up was not asked for.

Regenerates the derived panel from the untouched master.
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── the derived panel (moon cx 150, mug unchanged at 680) ──
im = Image.open(os.path.join(ROOT, 'Art/Assets/LastOrders/LastOrders_panel.png')).convert('RGBA')
CY = 406
SCALE = 1.25
JOBS = [((98, 294, 201, 397), 150), ((598, 296, 783, 400), 680)]
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
print('derived panel regenerated (moon cx 150)')

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


sub(".lo-screen .lo-c{position:absolute;top:55.2%;height:5.0%;/* P806: labels in the band between beam and icon row - clear of the icons */",
    ".lo-screen .lo-c{position:absolute;top:55.9%;height:4.4%;/* P807: lower, still clear of the icons */",
    'labels lower')

sub(".lo-screen .lo-lab{font-size:3.5cqw;letter-spacing:.08em;white-space:nowrap}",
    ".lo-screen .lo-lab{font-size:4.0cqw;letter-spacing:.08em;white-space:nowrap}",
    'labels larger')

sub(".lo-screen .lo-c-moon {left:4.0%;width:26.8%}",
    ".lo-screen .lo-c-moon {left:6.5%;width:26.8%}/* P807: NIGHTS a bit right */",
    'NIGHTS right')

sub(".lo-screen .lo-c-mug  {left:67.7%;width:28.0%}",
    ".lo-screen .lo-c-mug  {left:65.2%;width:28.0%}/* P807: NEW ROSTER a bit left */",
    'NEW ROSTER left')

sub(".lo-screen .lo-night{position:absolute;left:26.6%;width:8.5%;/* P806: right of the GROWN moon */",
    ".lo-screen .lo-night{position:absolute;left:25.3%;width:8.5%;/* P807: left with the moon */",
    'number left')

sub(".lo-screen .lo-heart{height:9.4cqw;width:auto;object-fit:contain;display:block}/* P806: grown with the moon and mug so the row reads as one */",
    ".lo-screen .lo-heart{height:8.2cqw;width:auto;object-fit:contain;display:block}/* P807: back to authored - the grow was not asked for */",
    'hearts back to authored')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
