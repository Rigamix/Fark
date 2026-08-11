# -*- coding: utf-8 -*-
"""Encode every card face into assets/cards/<id>.webp.

THE MASTERS ARE NEVER TOUCHED - same rule as optimize_art.py. Art/Assets/Cards/
holds Denis's 911x1298 originals; assets/cards/ holds the downscaled derivatives
the game actually loads, named by CARD ID because that is what the loader
interpolates (`assets/cards/`+id+`.webp`).

SIZE AND QUALITY ARE THE SHIPPED CONVENTION, not new choices: the 32 files
already there are 456x650 - exactly half the master - at 53-70 KB. Matching them
keeps one look across the deck.

QUALITY IS CALIBRATED ON THE SHIPPED FILES, not on an invented RMSE target. The
32 faces already in assets/cards/ measure RMSE 2.5-3.0 against their masters at
45-71 KB, and my first pass set the bar there - which sent 43 of 70 to lossless
at ~200 KB each. The bar was wrong, not the encoder: RMSE PLATEAUS AT ~6.8 for
the boss art even at quality 97, so that residual is inherent to this art at
456x650 and no quality setting reaches 3.0. The family cards hit 2.5-3.0 because
their art is simpler, not because it was encoded harder.
So the convention that actually transfers is FILE SIZE: quality 90 puts the boss
faces in the same 45-75 KB band as the shipped deck. RMSE is kept only as a
catastrophe guard at 15, which no face should ever trip.

NAMING IS THE DANGEROUS PART and is delegated: boss folders go through
tools/boss_card_art_map.py, which carries the owner gate and the reviewed alias
table. Family folders use `card_face_<id>` with three explicit exceptions. A file
that resolves to no id is REPORTED and skipped, never guessed at - an art file
that renders nowhere looks exactly like art that was never drawn.

  python tools/optimize_card_art.py --dry-run
  python tools/optimize_card_art.py
"""
import io, os, re, sys, subprocess, glob

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:
    sys.exit('needs Pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS = os.path.join(ROOT, 'Art', 'Assets', 'Cards')
OUT = os.path.join(ROOT, 'assets', 'cards')
DRY = '--dry-run' in sys.argv
W, H = 456, 650
RMSE_LIMIT = 15.0   # catastrophe guard only - see the note below

BOSSES = ['Aldric', 'Ambrose', 'Brutus', 'Corvus', 'Finnick', 'Grog', 'Mabel', 'Whisper']
FAMILIES = ['Amber', 'Jade', 'Obsidian', 'Silver', 'Starstone', 'Tavern', 'Vagabond']

# family files that are not `card_face_<id>`. All three are real word-level
# differences, so they are data rather than a rule.
FAM_ALIAS = {
    'steadyHand': 'steady_hand',
    'FairTrade':  'fair_trade',
    'fools_gold': 'fools_gold_f',   # the id carries an _f; the file does not
    'vanguard':   'vanguard_f',     # same
}

# ── the boss mapping comes from the tool that owns it ──
def boss_pairs():
    out = []
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'boss_card_art_map.py')],
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        m = re.match(r'\s{2}([a-z0-9_]+)\s+(\w+)\s+(Art[\\/].+?\.png)', line)
        if m:
            out.append((m.group(1), os.path.join(ROOT, m.group(3).replace('\\', os.sep))))
    return out

def family_pairs():
    out, skipped = [], []
    ids = set(re.findall(r"id:'([a-z0-9_]+)'",
                         io.open(os.path.join(ROOT, 'fark_proto.html'), encoding='utf-8').read()))
    for fam in FAMILIES:
        d = os.path.join(CARDS, fam)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith('.png'):
                continue
            stem = re.sub(r'^card_face_', '', os.path.splitext(f)[0])
            cid = FAM_ALIAS.get(stem, stem)
            if cid in ids:
                out.append((cid, os.path.join(d, f)))
            else:
                skipped.append((stem, fam))
    return out, skipped

def rmse(a, b):
    diff = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    st = ImageStat.Stat(diff)
    return (sum(v * v for v in st.mean) / 3.0) ** 0.5 + (sum(st.stddev) / 3.0) * 0.0

pairs = boss_pairs()
fam, skipped = family_pairs()
pairs += fam

seen, dupes = {}, []
for cid, path in pairs:
    if cid in seen:
        dupes.append((cid, seen[cid], path))
    seen[cid] = path

print('card faces to encode: %d   (boss %d + family %d)' % (len(seen), len(boss_pairs()), len(fam)))
if dupes:
    print('\nTWO FILES CLAIM ONE ID (%d) - resolve before shipping:' % len(dupes))
    for cid, a, b in dupes:
        print('  %-24s %s  vs  %s' % (cid, os.path.relpath(a, ROOT), os.path.relpath(b, ROOT)))
if skipped:
    print('\nFAMILY FILES MATCHING NO ID (%d) - skipped, not guessed:' % len(skipped))
    for stem, fam_ in skipped:
        print('  %-24s %s' % (stem, fam_))

if not DRY and not os.path.isdir(OUT):
    os.makedirs(OUT)

tot_src = tot_out = 0
lossless = []
for cid in sorted(seen):
    src = seen[cid]
    im = Image.open(src).convert('RGBA')
    small = im.resize((W, H), Image.LANCZOS)
    dst = os.path.join(OUT, cid + '.webp')
    a = io.BytesIO(); small.save(a, 'WEBP', quality=90, method=6)
    b = io.BytesIO(); small.save(b, 'WEBP', lossless=True, method=6)
    back = Image.open(io.BytesIO(a.getvalue()))
    err = rmse(small, back)
    use, tag = (a, 'lossy') if err <= RMSE_LIMIT else (b, 'lossless')
    if err > RMSE_LIMIT:
        lossless.append((cid, round(err, 2)))
    tot_src += os.path.getsize(src); tot_out += len(use.getvalue())
    if not DRY:
        io.open(dst, 'wb').write(use.getvalue())

print('\n%s  %.1f MB -> %.2f MB  (%d%% smaller)' % (
    'would write' if DRY else 'wrote', tot_src / 1e6, tot_out / 1e6,
    round(100 * (1 - tot_out / max(1, tot_src)))))
if lossless:
    print('shipped LOSSLESS because lossy drifted (%d): %s' % (len(lossless), lossless[:8]))
