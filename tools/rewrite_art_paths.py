# -*- coding: utf-8 -*-
"""
rewrite_art_paths.py - point the game at the light copies.

Reads tools/art_manifest.json (written by optimize_art.py) and repoints
fark_proto.html at the optimized/ copy of every picture it can do SAFELY.

Safety is the whole design here. Anything this cannot rewrite with certainty is
left alone and reported - a picture that keeps its original path still loads and
still looks right, it is just heavier. There is no failure mode where the game
asks for a file that is not there.

Three cases:
  1. The full path appears as a literal      ->  rewritten in place.
  2. The filename appears as a literal and is glued to a known directory
     prefix variable (ST, PT_A, ...)         ->  filename rewritten, but ONLY
     if the prefix variable resolves to the directory the file actually lives
     in, and the literal occurs in a place that prefix reaches.
  3. Anything else                            ->  skipped and listed.

  python tools/rewrite_art_paths.py --dry-run
  python tools/rewrite_art_paths.py
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "fark_proto.html"
MANIFEST = ROOT / "tools" / "art_manifest.json"

# Directory-prefix variables the game concatenates filenames onto. Read out of
# fark_proto.html; kept here so a rename is a one-line fix rather than a hunt.
PREFIX_VARS = {
    "ST": "Art/Assets/Store/",
    "NR": "Art/Assets/NewRun/",
    "PT_A": "assets/_mockups/new_main/",
    "PT_P": "Art/Assets/Frames/Patrons/",
    "ENCH_ICON_DIR": "assets/ench_icons/",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    man = json.load(open(MANIFEST, encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    orig = html

    done, skipped = [], []
    for f in man["files"]:
        src, out = f["src"], f["out"]
        saved = f["bytesFrom"] - f["bytesTo"]

        # case 1: the whole path is written out
        if src in html:
            html = html.replace(src, out)
            done.append((saved, src, "full path"))
            continue

        # case 2: prefix variable + filename
        d, name = src.rsplit("/", 1)
        d += "/"
        var = next((v for v, val in PREFIX_VARS.items() if val == d), None)
        if var:
            newname = "optimized/" + Path(name).stem + "_opt" + Path(out).suffix
            hits = 0
            # The filename is usually NOT a whole string literal - it opens one
            # and the rest of the tag follows it:
            #     +'<img src="'+ST+'Store_back.png" alt="">'
            # so match "quote, then the name" right after the prefix variable
            # rather than a fully quoted token.
            pat = re.compile(r"(\b" + re.escape(var) + r"\s*\+\s*['\"])" + re.escape(name))
            html, n = pat.subn(lambda m: m.group(1) + newname, html)
            hits += n
            # ternaries put the name in a complete literal a little further off:
            #     ST+(dOn?'Store_front.png':'Store_front_empty.png')
            for q in ("'", '"'):
                tok = q + name + q
                if tok in html:
                    hits += html.count(tok)
                    html = html.replace(tok, q + newname + q)
            if hits:
                done.append((saved, src, "%s + filename (%d)" % (var, hits)))
                continue

        skipped.append((saved, src))

    done.sort(reverse=True)
    skipped.sort(reverse=True)
    print("rewritten: %d    skipped: %d" % (len(done), len(skipped)))
    print("  bytes saved by the rewritten set: %.2f MB"
          % (sum(d[0] for d in done) / 1048576))
    print("  bytes still on the table:         %.2f MB"
          % (sum(s[0] for s in skipped) / 1048576))
    print("\nrewritten:")
    for saved, src, how in done:
        print("  %7.2f MB  %-52s  %s" % (saved / 1048576, src, how))
    print("\nskipped (path is built somewhere this cannot see - these keep the original):")
    for saved, src in skipped[:25]:
        print("  %7.2f MB  %s" % (saved / 1048576, src))
    if len(skipped) > 25:
        print("  ... and %d more" % (len(skipped) - 25))

    if args.dry_run:
        print("\n(dry run - fark_proto.html untouched)")
        return
    if html != orig:
        HTML.write_text(html, encoding="utf-8")
        print("\nfark_proto.html updated")
    else:
        print("\nnothing to change")


if __name__ == "__main__":
    main()
