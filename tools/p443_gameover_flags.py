# -*- coding: utf-8 -*-
"""P443 - the game-over stat flags, which have been 404ing.

WHAT WAS BROKEN. The four stat flags on the game-over screen load from
`assets/GameOver_Art/gameover_flag<N>.webp`. That directory does not exist -
not the files, the DIRECTORY - so all four 404. `.golo-flag img` is the thing
that gives the flag its height, so with no image the flag collapses and the
labels land directly on the painted street: NIGHTS, MATCHES, PEAK GOLD and
FEATS in dark bronze on dark stone, at 16px, effectively unreadable.

It looked like font damage. It is not - the same screen measured identically
before and after the face swap. The face swap only made it easier to notice.

THE ART ALREADY EXISTS. Denis drew GameOver_stat01..04 and they are already
optimized alongside GameOver_bg and GameOver_banner - which this same screen
loads from the current tree, correctly, two lines apart in the markup. Only the
flags were left pointing at the old tree.

AND THIS IS THE RULING, not scope I chose: nothing links to old art, and where
final art is not ready a new-style placeholder stands in rather than a fallback
to the previous game's file. Here the final art is ready and unreferenced.

REACHABILITY CHECKED FIRST, because it decides whether this matters at all: the
draft screen turned out to be dead this same session and its old-art cards were
only ever visible because a probe forced the screen open. showScreen('gameover')
has ten call sites - death by coins, death mid-gauntlet, the run-out-of-tiers
ending. This one a player sees.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── registry entry, next to the other current-tree directories ──
ANCHOR = u"  winPlates:    'Art/Assets/Icons/Wins/optimized/',"
assert s.count(ANCHOR) == 1, 'registry anchor %d' % s.count(ANCHOR)
s = s.replace(ANCHOR, ANCHOR + u"""
  /* the four stat flags. Were `assets/GameOver_Art/`, a directory that does
     not exist, so all four 404'd and the labels fell onto the background. The
     bg and banner on the same screen were already on the current tree. */
  gameOver:     'Art/Assets/GameOver/optimized/',""")

# ── the flag src ──
OLD = u"""      +'<img src="assets/GameOver_Art/gameover_flag'+(i+1)+'.webp" alt="">'"""
assert s.count(OLD) == 1, 'flag img matched %d' % s.count(OLD)
s = s.replace(OLD,
  u"""      /* FK_ART, not a literal - this src is exactly the kind that got picked
         out of the old tree in the first place. 01..04, zero-padded, matching
         the filenames Denis exported. */
      +'<img src="'+FK_ART.gameOver+'GameOver_stat0'+(i+1)+'_opt.webp" alt="">'""")

assert s != orig, 'nothing changed'
# STRIP COMMENTS BEFORE ASSERTING, because the comments explaining a removal
# quote the thing removed. This is the FOURTH check today tripped by its own
# prose - the --font-px declaration, the @font-face rules, and twice here. The
# instance-by-instance fix (reword the comment) keeps losing to the habit, so
# the check changes instead: asserts about what the CODE references must be
# made against code.
import re
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert 'assets/GameOver_Art' not in code, 'a reference to the dead directory survives'
# THE FILES MUST ACTUALLY BE THERE. A patch that swaps one 404 for another
# looks identical in the diff and identical on screen.
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for n in range(1, 5):
    p = os.path.join(here, 'Art', 'Assets', 'GameOver', 'optimized',
                     'GameOver_stat0%d_opt.webp' % n)
    assert os.path.exists(p), 'missing art: %s' % p
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P443 applied: four stat flags moved to the current tree')
