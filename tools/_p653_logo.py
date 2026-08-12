# -*- coding: utf-8 -*-
"""P653: the new logo becomes the app icon, the favicon and an optimized copy.

Denis: "C:\\...\\Art\\Assets in there use logo.png. Optimize and update it"

Art/Assets/Logo.png is 745x771 - a red die wearing an F, on a gold glow. Nearly
square, so it takes a 13px centre crop off the top and bottom to reach 745x745;
the die sits centred with margin on every side, so nothing of the artwork is in
those rows. P630's source needed a real crop (1010x1001) and P631's was already
square; this is the small case between them.

THREE OUTPUTS, which is what "update it" means here - the logo has three jobs:
  assets/Menu_Art/iOS icon.png   512x512, the manifest's icon for both its 192
                                 and 512 entries
  favicon.png                    64x64, the tab icon
  Art/Assets/optimized/logo_opt.webp
                                 the pipeline copy every art folder here keeps,
                                 at source size

LANCZOS on the way down, and the icons stay PNG because the manifest declares
image/png for them. The webp is the light copy, not a replacement for either.

WHY BOTH ICON FILES AND NOT ONE: they are different sizes for different jobs and
the 64px one is not a scaled-down 512 at request time - it is a separate encode,
which is the point of having it. P630's note records the older bug in the same
place: one 360px file served both manifest entries, so the OS was upscaling at
the 512 slot.
"""
import io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'Art', 'Assets', 'Logo.png')
if not os.path.exists(SRC):
    sys.exit('no Art/Assets/Logo.png')

im = Image.open(SRC).convert('RGB')
w, h = im.size
print('source %dx%d' % (w, h))

side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
sq = im.crop((left, top, left + side, top + side))
print('centre crop -> %dx%d  (took %d off the width, %d off the height)'
      % (sq.size[0], sq.size[1], w - side, h - side))

jobs = [
    (os.path.join(ROOT, 'assets', 'Menu_Art', 'iOS icon.png'), 512),
    (os.path.join(ROOT, 'favicon.png'), 64),
]
for path, size in jobs:
    before = os.path.getsize(path) if os.path.exists(path) else 0
    out = sq.resize((size, size), Image.LANCZOS)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    out.save(path, 'PNG', optimize=True)
    print('  %-40s %dx%d  %d -> %d bytes'
          % (os.path.relpath(path, ROOT), size, size, before, os.path.getsize(path)))

opt_dir = os.path.join(ROOT, 'Art', 'Assets', 'optimized')
os.makedirs(opt_dir, exist_ok=True)
opt = os.path.join(opt_dir, 'logo_opt.webp')
im.save(opt, 'WEBP', quality=90, method=6)
print('  %-40s %dx%d  %d -> %d bytes'
      % (os.path.relpath(opt, ROOT), w, h, os.path.getsize(SRC), os.path.getsize(opt)))
