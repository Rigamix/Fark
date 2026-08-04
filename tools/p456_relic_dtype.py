# -*- coding: utf-8 -*-
"""P456 - the eight relics had no 2D die styling at all.

apv_table_totality's last red. Its own header said "0 of 8 relics" and it was
right: asking the CSSOM directly, the sixteen .dtype- selectors are all
MATERIALS, and not one of the eight relic ids has a block. A relic on the 2D
path renders with whatever --d* vars are inherited - the trophy for beating a
boss looks like an ordinary die.

(I briefly believed it was 6 of 8, because my own console formatter printed
`missing[:6]` and I read the truncation as the data. The probe was right the
whole time. Same shape as everything else this session: a display treated as
the thing it displays.)

DERIVED, NOT INVENTED. Each block is built from that relic's existing MATCOL
tint - the 3D colour already chosen for it - so the two renderers agree about
what a relic looks like. The MATCOL entries are themselves marked "PLACEHOLDER
TINTS until the dice art lands", so these are placeholders derived from
placeholders, and they say so. This is consistency work, not art direction:
when the dice art arrives both tables change together.

WHY NOT REUSE THE FAMILY'S BLOCK, which is the obvious shortcut: the MATCOL
comment records that the relic tints USED to be copies of their family colour -
"six of the eight byte-identical" - so a relic was indistinguishable from the
ordinary die it is a trophy of. That was fixed once in 3D. Copying family
blocks here would reintroduce it in 2D.

The pip colours stay light-on-dark or dark-on-light by luminance rather than by
a fixed choice, because grogs_tooth (pale bone) and corvus_ledger_d (deep blue)
cannot take the same pips.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# the tints already chosen for 3D, read from MATCOL rather than restated
RELICS = [
    ('grogs_tooth',     0xefe4b0), ('mabels_thimble', 0x8a5a18),
    ('finnicks_palm',   0xff9a70), ('corvus_ledger_d', 0x2b4a8f),
    ('brutus_shield',   0x6e7d8c), ('aldrics_square', 0x0d5c34),
    ('whispers_fang',   0x9b2226), ('ambrose_weight', 0xb89a3c),
]
for rid, col in RELICS:
    assert re.search(re.escape(rid) + r'\s*:\s*0x%06x' % col, s), \
        'MATCOL tint for %s is not 0x%06x - re-read it rather than trusting this list' % (rid, col)

def rgb(c):
    return ((c >> 16) & 255, (c >> 8) & 255, c & 255)
def hx(t):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(v))) for v in t)
def scale(c, f):
    return tuple(v * f for v in rgb(c))
def lum(c):
    r, g, b = rgb(c)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0

blocks = []
for rid, col in RELICS:
    light = lum(col) > 0.55            # pale face -> dark pips, and the reverse
    blocks.append(
        '.dtype-%s{--dborder:%s;--dborder2:%s;--dface:%s;--dface2:%s;'
        '--dface3:%s;--dhigh:%s;--dpip:%s;--dpip2:%s;--dglow:rgba(%d,%d,%d,.42);'
        '--ddither:rgba(%d,%d,%d,.18)}'
        % (rid, hx(scale(col, .78)), hx(scale(col, .95)),
           hx(scale(col, .40)), hx(scale(col, .55)), hx(scale(col, .26)),
           hx(scale(col, 1.0)),
           '#2a2118' if light else hx(scale(col, 1.35)),
           '#4a3d2c' if light else hx(scale(col, 1.1)),
           rgb(col)[0], rgb(col)[1], rgb(col)[2],
           rgb(col)[0], rgb(col)[1], rgb(col)[2]))

ANCHOR = u".dtype-gold{"
n = s.count(ANCHOR)
assert n >= 1, '.dtype-gold anchor matched %d' % n
NOTE = (u"/* RELIC DIE FACES, 2D. Added 2026-08-03: the eight relics had no\n"
        u"   .dtype- block at all, so a boss trophy rendered with inherited die\n"
        u"   vars - indistinguishable from an ordinary die on the 2D path.\n"
        u"   Each is DERIVED from that relic's MATCOL tint so 3D and 2D agree;\n"
        u"   those tints are themselves placeholders until the dice art lands,\n"
        u"   and these move when they do. Deliberately NOT copies of the family\n"
        u"   blocks - that is the exact mistake MATCOL already had to be fixed\n"
        u"   for, where six of eight relics were byte-identical to their\n"
        u"   family and read as ordinary dice. */\n")
# EVERY copy of the material block gets them - the .dtype- set is written twice
# and a relic styled in one and not the other is the same half-fixed state this
# patch exists to remove.
s = s.replace(ANCHOR, NOTE + '\n'.join(blocks) + '\n' + ANCHOR)

assert s != orig, 'nothing changed'
for rid, _ in RELICS:
    assert s.count('.dtype-%s{' % rid) == n, \
        '%s written %d times, expected %d (one per material block copy)' \
        % (rid, s.count('.dtype-%s{' % rid), n)
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P456 applied: 8 relic .dtype- blocks x %d copies of the material block' % n)
