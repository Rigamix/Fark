# -*- coding: utf-8 -*-
"""Bake Denis's enchant icons into a file:// safe JS asset.

Reads Art/Assets/Enchants/*.png (his originals, never modified), normalises
each to a 512x512 face tile with the art fitted inside the 432px FLAT area of
the die's UV island, and emits base64 PNGs into assets/models/dice/ench_icons.js
- the same pattern skins.js uses, because external images are cross-origin
over file:// in Firefox and WebGL refuses them.

The die sheet is 1536x1024: a 3x2 grid of 512 cells, 8px margin, 496px island,
and the bevel puts 87% of that island on the flat face.
"""
import base64, io, os, glob
from PIL import Image

ROOT = r"C:/Users/Rigam/OneDrive/Documents/Work/Gambit"
SRC  = os.path.join(ROOT, "Art/Assets/Enchants")
OUT  = os.path.join(ROOT, ".claude/worktrees/zen-chatterjee-f04c42/assets/models/dice/ench_icons.js")

CELL, MARGIN = 256, 4  # the shipped skin sheet is 960x640, so a face island
                       # is only ~310px - a 512 tile was pure oversampling
ISL  = CELL - 2 * MARGIN          # 496
FLAT = 0.870
FLATPX = ISL * FLAT               # 432
FILL = 0.80                       # how much of the flat face the art may use

out, report = {}, []
for f in sorted(glob.glob(os.path.join(SRC, "*.png"))):
    name = os.path.splitext(os.path.basename(f))[0].lower()
    im = Image.open(f).convert("RGBA")
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    w, h = im.size
    box = FLATPX * FILL
    k = min(box / w, box / h)
    nw, nh = max(1, int(round(w * k))), max(1, int(round(h * k)))
    im = im.resize((nw, nh), Image.LANCZOS)

    tile = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    tile.paste(im, ((CELL - nw) // 2, (CELL - nh) // 2), im)

    b = io.BytesIO()
    # quantise: these are flat inked shapes, not photographs
    q = tile.quantize(colors=64, method=Image.FASTOCTREE).convert("RGBA")
    q.putalpha(tile.split()[-1])
    q.save(b, "PNG", optimize=True)
    out[name] = base64.b64encode(b.getvalue()).decode("ascii")
    report.append((name, (w, h), (nw, nh), len(b.getvalue()) // 1024))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("/* Enchant icon faces - baked from Art/Assets/Enchants by a build step.\n")
    fh.write("   Each is a 512x512 face tile, art fitted inside the 432px FLAT area of\n")
    fh.write("   the die's UV island so nothing important bends over the bevel.\n")
    fh.write("   Embedded because an external image is cross-origin over file:// and\n")
    fh.write("   WebGL refuses it - same reason skins.js is embedded. */\n")
    fh.write("window.FK_ENCH_ICONS={\n")
    for k in sorted(out):
        fh.write('  %s:"data:image/png;base64,%s",\n' % (k, out[k]))
    fh.write("};\n")

print("baked %d icons -> %s" % (len(out), OUT))
for n, src, dst, kb in report:
    print("  %-14s %sx%s -> %sx%s in a 512 tile   %dKB" % (n, src[0], src[1], dst[0], dst[1], kb))
print("\nflat face %d px, art fitted to %d px" % (round(FLATPX), round(FLATPX * FILL)))
missing = [x for x in ["tithe","ward","snare","break","trade","snuff","fog"] if x not in out]
if missing:
    print("MISSING (still placeholder): " + ", ".join(missing))
extra = [x for x in out if x not in ["tithe","ward","snare","break","trade","snuff","fog"]]
if extra:
    print("EXTRA (no face to sit on, usable as a shop glyph): " + ", ".join(extra))
