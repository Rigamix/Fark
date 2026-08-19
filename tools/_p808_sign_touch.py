# -*- coding: utf-8 -*-
"""P808: Last Orders - lower text more, icons down a touch (Denis).

Derived-panel regeneration from the untouched master with the icon
centre line at y=416 (from 406); labels 57.2%, night number 68.8%,
hearts 69.6% follow. The regeneration recipe is P807's with CY=416.
"""
import io, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
im = Image.open(os.path.join(ROOT, 'Art/Assets/LastOrders/LastOrders_panel.png')).convert('RGBA')
CY = 416; SCALE = 1.25
JOBS = [((98, 294, 201, 397), 150), ((598, 296, 783, 400), 680)]
fills = []; icons = []
for (x0, y0, x1, y1), cx in JOBS:
    h = y1 - y0
    fills.append(((x0, y0), im.crop((x0, y1, x1, y1 + h)).copy()))
    icons.append((im.crop((x0, y0, x1, y1)).copy(), cx))
for pos, f in fills: im.paste(f, pos)
for icon, cx in icons:
    w2 = int(icon.width * SCALE); h2 = int(icon.height * SCALE)
    big = icon.resize((w2, h2), Image.LANCZOS)
    im.paste(big, (cx - w2 // 2, CY - h2 // 2), big)
im.save(os.path.join(ROOT, 'Art/Assets/LastOrders/optimized/LastOrders_panel_opt.webp'),
        'WEBP', quality=88, method=6)
print('derived panel regenerated (CY=416)')
