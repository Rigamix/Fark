# -*- coding: utf-8 -*-
u"""P864b: the spoils tiles stop overflowing the phone.

The brief's section 9 asks to "confirm it still reads at 430x900 and that no
tile is clipped". Measured at 430 logical px, it does not - and it did not
before P864 either. Driven against a control built from the previous commit:

    pre-P864 : the tile row is 501px inside a 344px card  (clipped 157px)
    post-P864: 536px inside 344px                          (clipped 192px)

so this is a pre-existing defect that P864's longer card text made about 35px
worse. On screen GROG'S FLASK reads as "G'S FLASK" and HIS PURSE runs off the
right edge.

THE MECHANISM, because the numbers alone do not say what to change. The tiles
carry `aspect-ratio:2/3` and the columns are `1fr`, which is
`minmax(auto, 1fr)` - and its MINIMUM is the item's min-content size. So a
narrow column makes the text wrap tall, aspect-ratio computes the item's WIDTH
back from that height (260px tall -> 173px wide, exactly the measured number),
and the auto minimum lets the track grow to accommodate it. Each tile is sized
by its own height and the row ends up as wide as its tallest tile demands.

Two changes, both needed - either alone leaves the loop intact:
  minmax(0,1fr) removes the auto minimum, so a track can no longer grow to fit
    an item.
  min-height replaces aspect-ratio, so a tile's width is never derived from its
    height at all.
overflow:hidden is the backstop: with the width fixed, a long description clips
inside its own tile rather than pushing anything.

SCOPED, NOT GLOBAL. `grid-template-columns:1fr 1fr 1fr` appears on eight lines
and `aspect-ratio:2/3` on twenty-three - both are house idiom used by screens
nobody measured here. The grid edit is anchored to the SPOILS header line, and
the tile edit to `cursor:pointer;aspect-ratio:2/3;display:flex`, which occurs
exactly three times and only on these three tiles.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]


GRID_OLD = ("""IT IS FINAL</div>'
      +'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">';""")
GRID_NEW = ("""IT IS FINAL</div>'
      +'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px">';""")
sub(GRID_OLD, GRID_NEW, 'spoils grid')

TILE_OLD = ("cursor:pointer;aspect-ratio:2/3;display:flex;flex-direction:column;"
            "background:#191919;border:2px solid")
TILE_NEW = ("cursor:pointer;min-height:186px;overflow:hidden;display:flex;flex-direction:column;"
            "background:#191919;border:2px solid")
n = s.count(TILE_OLD)
if n != 3:
    sys.exit('TILE ANCHOR x%d, expected exactly the 3 spoils tiles (nothing written)' % n)
s = s.replace(TILE_OLD, TILE_NEW)

# 2px of padding back from each side, bought to keep the text legible once the
# columns are ~105px rather than 173px.
for ink in ('#dc5', '#6bc', '#8e8'):
    a = "border:2px solid %s;padding:7px\">" % ink
    if s.count(a) != 1:
        sys.exit('PAD ANCHOR %s x%d (nothing written)' % (ink, s.count(a)))
    s = s.replace(a, "border:2px solid %s;padding:5px\">" % ink)

if s.count(TILE_NEW) != 3:
    sys.exit('TILES NOT REFITTED (nothing written)')
# assert the SPOILS grid specifically, not the token: minmax(0,1fr) is already
# used elsewhere in the file, so a global count says nothing about this edit.
if 'grid-template-columns:repeat(3,minmax(0,1fr));gap:6px' not in s:
    sys.exit('SPOILS GRID NOT REWRITTEN (nothing written)')
# NO global "old grid is gone" guard. Three other screens legitimately keep
# `grid-template-columns:1fr 1fr 1fr;gap:8px`, so testing for its absence
# file-wide asserts against the wrong thing - it would fail on code this patch
# deliberately did not touch. sub() already proved the SPOILS anchor was
# unique before rewriting it, which is the claim that matters.

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: spoils grid + 3 tiles refitted')
