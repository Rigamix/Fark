# -*- coding: utf-8 -*-
"""
optimize_art.py - make a light copy of every picture the game ships.

THE RULE (Denis, 2026-07-28): whenever a new picture goes into the game, a
downscaled, re-encoded copy goes beside it in an `optimized/` subfolder. The
high-res original is NEVER touched and NEVER replaced - it stays as the master
to re-derive from when a size changes.

  Art/Assets/Store/Store_front.png          <- master, left alone
  Art/Assets/Store/optimized/Store_front_opt.webp   <- what the game loads

WHAT "MINIMUM SIZE" MEANS HERE
An image only needs enough pixels for the largest box it ever paints into,
times the device pixel ratio. tools/art_targets.json holds those box widths in
CSS pixels, measured off the running game rather than guessed - see
`--report-missing` for anything not yet measured.

FORMAT
WebP keeps alpha and is smaller than PNG at the same perceived quality, so it
is the default. But lossy WebP smears flat colour and hard ink lines, which is
most of this game's art, so every image is encoded BOTH ways and the choice is
made by measurement: if lossy is visibly different from the master (RMSE over
the threshold) the lossless copy ships instead, even though it is bigger.
Anything that still comes out heavier than the source PNG keeps the PNG.

USAGE
  python tools/optimize_art.py --dry-run            # what would change, and by how much
  python tools/optimize_art.py                      # write the optimized/ copies
  python tools/optimize_art.py --only Store,Icons   # just those subdirectories
  python tools/optimize_art.py --report-missing     # images with no measured target
  python tools/optimize_art.py --manifest out.json  # machine-readable result

The manifest is what rewrite_art_paths.py reads to point the game at the light
copies; anything absent from it keeps its original path and still works.
"""
import argparse, json, math, os, sys, io
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:
    sys.exit("Pillow is required:  python -m pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
TARGETS_FILE = ROOT / "tools" / "art_targets.json"
OUT_DIRNAME = "optimized"
OUT_SUFFIX = "_opt"

# How much bigger than its CSS box an image is rendered. Phones the game
# targets are DPR 3, but 2x of painterly art is indistinguishable from 3x at
# arm's length and is roughly half the bytes. Text-heavy art wants more.
DEFAULT_DPR = 2.0
# Above this VISIBLE difference (0-255 per channel, measured over the picture
# composited onto a flat background so fully-transparent pixels cannot count)
# the lossy copy is judged to have changed the picture and the lossless copy
# ships instead. Calibrated by measurement across backdrops, cut-outs and small
# ink icons: at q92 they land between 1.5 and 3.2, so 3.5 passes everything
# that is honest and would still catch a real smear.
RMSE_LIMIT = 3.5
# WebP stores alpha losslessly even in lossy mode, so any movement here means
# the encoder has actually reshaped the cut-out.
ALPHA_LIMIT = 1.0
LOSSY_Q = 92


def png_size(path):
    """Dimensions without decoding the pixels: IHDR is at a fixed offset."""
    with open(path, "rb") as f:
        head = f.read(26)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big"))


def visible_rmse(a, b):
    """How different the two pictures LOOK, and how different their cut-outs are.

    Comparing RGBA directly is wrong and was the first thing this got wrong:
    where alpha is 0 the colour channels are invisible, and a lossy encoder is
    free to put anything there. Measured that way a mostly-transparent cut-out
    scored 73 - not because it looked different but because nobody can see the
    pixels that differed. Compositing both over the same flat background first
    weights every pixel by how visible it actually is.
    """
    if a.size != b.size:
        return 999.0, 999.0
    bg = Image.new("RGBA", a.size, (128, 128, 128, 255))
    ca = Image.alpha_composite(bg, a).convert("RGB")
    cb = Image.alpha_composite(bg, b).convert("RGB")
    st = ImageStat.Stat(ImageChops.difference(ca, cb))
    rgb = math.sqrt(sum(st.sum2) / (3.0 * a.size[0] * a.size[1]))
    sa = ImageStat.Stat(ImageChops.difference(a.getchannel("A"), b.getchannel("A")))
    alpha = math.sqrt(sa.sum2[0] / float(a.size[0] * a.size[1]))
    return rgb, alpha


def load_targets():
    if not TARGETS_FILE.exists():
        return {"default_css_px": None, "dpr": DEFAULT_DPR, "targets": {}}
    with open(TARGETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def target_for(rel, cfg):
    """Longest CSS-pixel width this image ever paints at.

    Keys are matched longest-first, so a specific file beats its directory:
       "Art/Assets/Icons/close.png"  beats  "Art/Assets/Icons/"
    """
    best = None
    for key, val in cfg.get("targets", {}).items():
        if rel.replace("\\", "/").startswith(key) and (best is None or len(key) > len(best[0])):
            best = (key, val)
    if best:
        return best[1]
    return cfg.get("default_css_px")


def _enc(im, fmt, **kw):
    buf = io.BytesIO()
    im.save(buf, fmt, **kw)
    return buf.getvalue()


def process(src, cfg, args):
    rel = str(src.relative_to(ROOT)).replace("\\", "/")
    dims = png_size(src)
    if dims is None:
        try:
            with Image.open(src) as probe:
                dims = probe.size
        except Exception as e:
            return {"src": rel, "skipped": "unreadable: %s" % e}
    src_bytes = src.stat().st_size

    css_px = target_for(rel, cfg)
    if css_px is None:
        return {"src": rel, "skipped": "no measured target", "w": dims[0], "h": dims[1],
                "bytes": src_bytes}

    dpr = cfg.get("dpr", DEFAULT_DPR)
    # headroom covers states the measuring sweep could not reach - a zoom, a
    # drag scale - without having to guess a bigger box for every picture
    want_w = int(math.ceil(css_px * dpr * cfg.get("headroom", 1.0)))

    with Image.open(src) as im:
        im = im.convert("RGBA")
        if im.width > want_w:
            new_h = max(1, int(round(im.height * want_w / im.width)))
            small = im.resize((want_w, new_h), Image.LANCZOS)
        else:
            small = im.copy()  # already small enough; re-encode only

        # Lossy first, and the fallbacks only if it fails the gate - lossless
        # WebP at method 6 costs seconds on a big image and almost never wins.
        lossy = (".webp", _enc(small, "WEBP", quality=LOSSY_Q, method=6), "lossy")
        with Image.open(io.BytesIO(lossy[1])) as dec:
            err, aerr = visible_rmse(small, dec.convert("RGBA"))

        if err <= RMSE_LIMIT and aerr <= ALPHA_LIMIT:
            pick = lossy
            if len(pick[1]) >= src_bytes and small.size == im.size:
                return {"src": rel, "skipped": "master already smaller", "w": dims[0],
                        "h": dims[1], "bytes": src_bytes}
        else:
            lossless = (".webp", _enc(small, "WEBP", lossless=True, method=6), "lossless")
            png = (".png", _enc(small, "PNG", optimize=True), "png")
            pick = lossless if len(lossless[1]) <= len(png[1]) else png
            # never ship something heavier than the master
            if len(pick[1]) >= src_bytes and small.size == im.size:
                return {"src": rel, "skipped": "master already smaller", "w": dims[0],
                        "h": dims[1], "bytes": src_bytes}

        out_dir = src.parent / OUT_DIRNAME
        out_path = out_dir / (src.stem + OUT_SUFFIX + pick[0])
        result = {
            "src": rel,
            "out": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "from": [dims[0], dims[1]], "to": list(small.size),
            "cssPx": css_px, "dpr": dpr,
            "bytesFrom": src_bytes, "bytesTo": len(pick[1]),
            "encoding": pick[2], "rmse": round(err, 2), "alphaErr": round(aerr, 2),
        }
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(pick[1])
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="Art/Assets",
                    help="subtree to walk (default Art/Assets)")
    ap.add_argument("--only", default="", help="comma-separated subdirectory filter")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report-missing", action="store_true",
                    help="list images with no measured target and exit")
    ap.add_argument("--manifest", default="tools/art_manifest.json")
    args = ap.parse_args()

    cfg = load_targets()
    base = ROOT / args.root
    if not base.exists():
        sys.exit("no such tree: %s" % base)

    only = [o.strip() for o in args.only.split(",") if o.strip()]
    files = []
    for p in sorted(base.rglob("*")):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        if OUT_DIRNAME in p.parts:
            continue                      # never re-optimize our own output
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if only and not any(("/" + o + "/") in ("/" + rel) or rel.startswith(o) or ("/" + o) in rel for o in only):
            continue
        files.append(p)

    if args.report_missing:
        missing = []
        for p in files:
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            if target_for(rel, cfg) is None:
                missing.append((p.stat().st_size, rel))
        missing.sort(reverse=True)
        print("%d image(s) with no measured target:" % len(missing))
        for b, rel in missing:
            print("  %8.2f MB  %s" % (b / 1048576, rel))
        return

    results, before, after, skipped = [], 0, 0, 0
    for p in files:
        r = process(p, cfg, args)
        results.append(r)
        if "skipped" in r:
            skipped += 1
            continue
        before += r["bytesFrom"]
        after += r["bytesTo"]

    print("%d file(s): %d optimized, %d skipped" % (len(results), len(results) - skipped, skipped))
    print("  %.1f MB -> %.1f MB  (%.0f%% smaller)"
          % (before / 1048576, after / 1048576,
             100 * (1 - after / before) if before else 0))
    if args.dry_run:
        print("  (dry run - nothing written)")
    else:
        man = ROOT / args.manifest
        man.parent.mkdir(parents=True, exist_ok=True)
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"generated_by": "tools/optimize_art.py",
                       "dpr": cfg.get("dpr", DEFAULT_DPR),
                       "files": [r for r in results if "out" in r]}, f, indent=1)
        print("  manifest: %s" % args.manifest)

    worst = sorted([r for r in results if "out" in r],
                   key=lambda r: r["bytesFrom"] - r["bytesTo"], reverse=True)[:12]
    if worst:
        print("\nbiggest savings:")
        for r in worst:
            print("  %7.2f -> %6.2f MB  %sx%s -> %sx%s  %-8s %s"
                  % (r["bytesFrom"] / 1048576, r["bytesTo"] / 1048576,
                     r["from"][0], r["from"][1], r["to"][0], r["to"][1],
                     r["encoding"], r["src"]))


if __name__ == "__main__":
    main()
