# -*- coding: utf-8 -*-
"""P805: the Last Orders icons centre in the parchment.

Denis: "center the icons in the panel.. they're too high.." The moon
and the mug are PAINTED into LastOrders_panel.png near the parchment's
top (icon row centre y~347) while the parchment's inner area spans
y~293..520 (centre ~406). Centring is therefore art surgery, done on
the DERIVED copy only - the master is untouched, per the art process:

  For each icon bbox (+6px margin): moon (98,294,201,397), mug
  (598,296,783,400) - cut the icon, paste it 59px lower, and fill the
  vacated strip with the clean parchment sampled directly below the
  original bbox. Output: optimized/LastOrders_panel_opt.webp (q88/m6).

The CSS overlays follow by the same 59/547 = 10.8%: labels 54.4% ->
65.2%, night number 57.9% -> 68.7%, hearts 58.8% -> 69.6%.

Rerunnable: this script regenerates the derived webp from the master
and re-pins the CSS (idempotent on the CSS via anchor checks).
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── the derived panel ──
im = Image.open(os.path.join(ROOT, 'Art/Assets/LastOrders/LastOrders_panel.png')).convert('RGBA')
SH = 59
for (x0, y0, x1, y1) in [(98, 294, 201, 397), (598, 296, 783, 400)]:
    icon = im.crop((x0, y0, x1, y1)).copy()
    fill = im.crop((x0, y1, x1, y1 + SH)).copy()
    im.paste(fill, (x0, y0))
    im.paste(icon, (x0, y0 + SH))
im.save(os.path.join(ROOT, 'Art/Assets/LastOrders/optimized/LastOrders_panel_opt.webp'),
        'WEBP', quality=88, method=6)
print('derived panel regenerated (+%dpx)' % SH)

# ── the CSS pins (no-op if already applied) ──
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
pairs = [
    (".lo-screen .lo-c{position:absolute;top:54.4%;height:3.6%;",
     ".lo-screen .lo-c{position:absolute;top:65.2%;height:3.6%;/* P805: the icon row is centred in the parchment now (art shifted +59px in the derived webp) */"),
    ("top:57.9%;height:14.5%;/* P804: centred on the painted moon */",
     "top:68.7%;height:14.5%;/* P805: the moon moved to the parchment centre */"),
    ("top:58.8%;height:13.0%;/* P804: centred on the painted icon row */",
     "top:69.6%;height:13.0%;/* P805: centred on the moved icon row */"),
]
changed = 0
for o, n in pairs:
    if s.count(o) == 1:
        s = s.replace(o, n)
        changed += 1
    elif s.count(n) != 1:
        sys.exit('ANCHOR lost for %r' % o[:40])
if changed:
    io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('css pins: %d applied (rest already in place)' % changed)
