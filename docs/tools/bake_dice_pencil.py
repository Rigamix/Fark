# -*- coding: utf-8 -*-
"""Bake a pencil wobble into dice face textures.

The 3D dice outline is a colored drop-shadow of each face's ALPHA
silhouette, so grain baked into the alpha edge shows up in the outline on
every engine (iOS WebKit drops SVG url() filters, so runtime grain is
desktop-only). This tool:
  1. keeps pristine faces in Art/Assets/Dice/src/<name>.png (created on
     first run from the live files),
  2. shrinks the art ~7% onto a transparent margin,
  3. displaces the whole image with two noise fields (low-freq wobble +
     fine grain) so the alpha edge - and the pips - wobble like pencil,
  4. writes the baked result back to Art/Assets/Dice/<name>.png at 240px.

Future material sets: drop <mat>_1..6.png into Art/Assets/Dice/ (or src/)
and rerun:  python docs/tools/bake_dice_pencil.py
"""
import os, shutil
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
DICE = os.path.normpath(os.path.join(ROOT, 'Art', 'Assets', 'Dice'))
SRC  = os.path.join(DICE, 'src')

W       = 240    # work + output size
CONTENT = 0.93   # art scale inside the canvas (margin = wobble headroom)
WOBBLE  = 0.020  # low-freq amplitude, fraction of W  (~4.8px @240)
GRAIN   = 0.007  # high-freq amplitude                (~1.7px @240)
SEED    = 11

def noise_field(shape_small, amp, rng):
    small = rng.random(shape_small).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W, W), Image.BICUBIC)
    return (np.asarray(im).astype(np.float32) / 255.0 - 0.5) * 2.0 * amp

def bake(path_src, path_out, rng):
    im = Image.open(path_src).convert('RGBA').resize((W, W), Image.LANCZOS)
    # shrink onto transparent margin
    cw = int(W * CONTENT)
    canvas = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    canvas.paste(im.resize((cw, cw), Image.LANCZOS), ((W - cw) // 2, (W - cw) // 2))
    a = np.asarray(canvas).astype(np.float32)

    dx = noise_field((7, 7),   W * WOBBLE, rng) + noise_field((56, 56), W * GRAIN, rng)
    dy = noise_field((7, 7),   W * WOBBLE, rng) + noise_field((56, 56), W * GRAIN, rng)

    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    sx = np.clip(xx + dx, 0, W - 1).astype(np.int32)
    sy = np.clip(yy + dy, 0, W - 1).astype(np.int32)
    out = a[sy, sx]
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(path_out)

def main():
    os.makedirs(SRC, exist_ok=True)
    names = [f for f in os.listdir(DICE) if f.lower().endswith('.png')]
    rng = np.random.default_rng(SEED)
    for f in sorted(names):
        src = os.path.join(SRC, f)
        if not os.path.exists(src):                    # first run: archive pristine
            shutil.copy2(os.path.join(DICE, f), src)
        bake(src, os.path.join(DICE, f), rng)
        print('baked', f)

if __name__ == '__main__':
    main()
