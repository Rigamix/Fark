#!/usr/bin/env python3
"""Bake the enchant SHOP-PLAQUE icons.

Not to be confused with build_ench_icons.py next door - that one bakes the
same art onto die FACES as base64 for the 3D layer. This one is for the
wooden plaques on the shop's ENCHANTS tab.

Denis's sources are 330-430px and the plaques render them at roughly 40 CSS
px. A browser does that downscale in ONE bilinear pass with no mipmapping,
which is what made them look soft. This resamples once, offline, with LANCZOS.

The dark ring is baked into the alpha here rather than done in CSS because
four chained drop-shadows on an <img> that sits inside a will-change layer
which ITSELF carries a drop-shadow get rasterised at the layer's resolution
rather than the device's - so they came out blurry anyway, and cost four
filters per icon on every frame of the plaque's sway.

Re-run after changing any source icon:
    python tools/build_ench_store_icons.py

Writes assets/ench_icons/*.png. Art/ is never modified.
"""
import glob
import os
import sys

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("needs Pillow:  pip install Pillow")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "Art", "Assets", "Enchants", "storeIcons")
OUT = os.path.join(ROOT, "assets", "ench_icons")

# 160 is about 1:1 on a dpr-3 phone and a clean 4x step on dpr-1. Larger just
# buys file size; smaller and the dpr-3 case has to upscale.
WIDTH = 160
RING = 4              # bake px; reads as ~1 CSS px at display size
DARK = (26, 16, 8)    # the rim colour the plaques already use

SKIP = {"enchants_panel.png"}   # the plaque itself, not an icon


def main():
    if not os.path.isdir(SRC):
        sys.exit("no source dir: " + SRC)
    os.makedirs(OUT, exist_ok=True)
    total = made = 0
    for path in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        name = os.path.basename(path)
        if name in SKIP:
            continue
        im = Image.open(path).convert("RGBA")
        sw, sh = im.size
        im = im.resize((WIDTH, max(1, round(sh * WIDTH / sw))), Image.LANCZOS)

        # pad, or the ring is clipped wherever the art touches an edge
        pad = RING + 2
        canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad))

        # grow the silhouette, soften the stair-step, harden back to a clean
        # edge - a plain MaxFilter on its own leaves visible corners
        ring = canvas.split()[3].filter(ImageFilter.MaxFilter(RING * 2 + 1))
        ring = ring.filter(ImageFilter.GaussianBlur(0.4))
        ring = ring.point(lambda v: 255 if v > 110 else 0)

        outline = Image.new("RGBA", canvas.size, DARK + (255,))
        outline.putalpha(ring)
        Image.alpha_composite(outline, canvas).save(os.path.join(OUT, name), optimize=True)

        size = os.path.getsize(os.path.join(OUT, name))
        total += size
        made += 1
        print("  %-18s -> %dx%d  %5.1fKB" % (name, canvas.width, canvas.height, size / 1024))
    print("%d icons, %.0fKB total" % (made, total / 1024))


if __name__ == "__main__":
    main()
