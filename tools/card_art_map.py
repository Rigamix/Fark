# -*- coding: utf-8 -*-
"""Which cards have NEW art, which have none, and which art file matches nothing.

The card loader still points at assets/Card_ART/<id>.png - the previous game's
deck - which is what Denis spotted on the draft screen. Repointing it needs the
mapping measured first, because two things can go wrong silently and both have
analogues in this project's history:

  * an id with no new art quietly keeps rendering the old file (the fallback
    that hides the problem)
  * an art FILE whose name matches no id renders nowhere and looks like art
    that was never drawn (the file that exists but is unreachable)

The second is the one worth the tool. Denis's filenames are not uniformly
snake_case - card_face_FairTrade.png and card_face_steadyHand.png are camel -
so a loader built on `card_face_<id>.png` will miss exactly those two and the
symptom is a blank card, not an error.
"""
import io, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = io.open(os.path.join(ROOT, 'fark_proto.html'), encoding='utf-8').read()

# ── every card the game defines, with its family where it has one ──
ids = {}
for m in re.finditer(r"\{id:'([a-z0-9_]+)'(?:,fam:'([a-z]+)')?", s):
    cid, fam = m.group(1), m.group(2)
    if cid not in ids or fam:
        ids[cid] = fam

fam_ids = {k: v for k, v in ids.items() if v}
print('cards defined: %d   of which family cards: %d' % (len(ids), len(fam_ids)))

# ── every new art file ──
files = {}
for p in glob.glob(os.path.join(ROOT, 'Art', 'Assets', 'Cards', '*', 'card_face_*.png')):
    fam = os.path.basename(os.path.dirname(p)).lower()
    stem = os.path.basename(p)[len('card_face_'):-len('.png')]
    files[stem] = (fam, os.path.relpath(p, ROOT).replace('\\', '/'))
print('new art files: %d' % len(files))

def norm(x):
    """camelCase and snake_case to one key. FairTrade -> fair_trade."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', x).lower().replace('__', '_')

by_norm = {}
for stem, (fam, path) in files.items():
    by_norm.setdefault(norm(stem), []).append((stem, fam, path))

matched, missing, orphan = [], [], []
for cid, fam in sorted(fam_ids.items()):
    hit = by_norm.get(norm(cid))
    if hit:
        matched.append((cid, fam, hit[0][1], hit[0][2], hit[0][0] != cid))
    else:
        missing.append((cid, fam))
used = {norm(c) for c, _, _, _, _ in matched}
for k, v in sorted(by_norm.items()):
    if k not in used:
        orphan.append(v[0])

print('\nMATCHED (%d):' % len(matched))
for cid, fam, afam, path, renamed in matched:
    flag = ''
    if renamed: flag += '   [FILENAME IS NOT THE ID]'
    if afam != fam: flag += '   [FAMILY FOLDER %s != card fam %s]' % (afam, fam)
    print('  %-22s %-10s %s%s' % (cid, fam, path, flag))

print('\nFAMILY CARDS WITH NO NEW ART (%d) - these are the ones that need a '
      'placeholder, NOT a fall back to the old deck:' % len(missing))
for cid, fam in missing:
    print('  %-22s %s' % (cid, fam))

print('\nART FILES MATCHING NO CARD ID (%d) - drawn but unreachable:' % len(orphan))
for stem, fam, path in orphan:
    print('  %-22s %-10s %s' % (stem, fam, path))

# ── how many cards in total would still be on the old deck ──
old = glob.glob(os.path.join(ROOT, 'assets', 'Card_ART', '*.png'))
print('\nold deck files: %d   non-family cards defined: %d'
      % (len(old), len(ids) - len(fam_ids)))
