# -*- coding: utf-8 -*-
"""P647: the deck slots tuck into each other again, now that they arch.

Denis: "more overlap on card slots on win screen" - an instruction, not a
report, which is how I first read it. "no they aren't touching."

THE HISTORY, because the two asks look contradictory until the arch is in it:
  -5%   the original. "spread them out horizontally a bit so they don't overlap
        as much" - too much overlap.
  +1.5% P641. At 4deg the rotated corners still encroached 6.3px into a 5.2px
        gap, so they touched - but as three near-level rectangles, which reads
        as a collision rather than a hand.
  +4%   P646, with the arch at 8deg. Now genuinely clear by 7.6px, and too far
        apart: "no they aren't touching".
The arch is what changed the answer. Overlap between three tilted, arched cards
reads as a fan tucked together; the same overlap between three level ones read
as a mistake. So the spread goes back negative, but nowhere near the original.

-1% is -3.44px of the 344px column, and each 8deg outer slot's box already
reaches 6.16px toward its neighbour, so the corners tuck by about 9.6px - a
third of the original overlap, on cards that now sit on a curve.

THE MIDDLE STAYS ON TOP. .fo-slot:nth-child(2) already carries z-index:2 and it
was doing nothing while they were apart; with them overlapping it is what makes
the row read as an arch with its outer cards tucked behind, rather than as a
left-to-right shingle.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"/* P646: ARCHED, AND NO LONGER TOUCHING. A slot is 19% of a 344px column =\n"
       u"   65.4 x 93.2px. Rotating by theta grows its bounding box by\n"
       u"   (h*sin + w*cos - w)/2 per side, so the old 4deg took 3.17px from each of\n"
       u"   two neighbours - 6.3px of encroachment into a 5.2px gap, which is the\n"
       u"   overlap Denis is looking at. 8deg needs 6.16px per side; 4% is 13.8px.\n"
       u"   The arch is the 14px of vertical differential (was 5px) - that is the part\n"
       u"   that reads as a curve rather than as three tilted rectangles. */\n"
       u".fo-slot+.fo-slot{margin-left:4%}")

new = (u"/* ARCHED, AND TUCKED. A slot is 19% of a 344px column = 65.4 x 93.2px, and\n"
       u"   rotating by theta grows its box by (h*sin + w*cos - w)/2 per side - 6.16px\n"
       u"   at the 8deg below.\n"
       u"   P646 opened the spread to +4% and Denis's answer was \"no they aren't\n"
       u"   touching\": the ARCH changed what the right amount is. Three near-level\n"
       u"   rectangles touching read as a collision, which is why the original -5%\n"
       u"   and the +1.5% that followed were both wrong; three tilted cards on a\n"
       u"   curve overlapping read as a hand. So P647 goes back negative, at a third\n"
       u"   of the original: -1% is -3.44px, and with the 6.16px each outer slot\n"
       u"   already reaches, the corners tuck by about 9.6px.\n"
       u"   The 14px of vertical differential is the arch itself - that is the part\n"
       u"   that makes it a curve rather than three tilted rectangles. */\n"
       u".fo-slot+.fo-slot{margin-left:-1%}")

c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)\n  %r' % (c, old[:140]))
s = s.replace(old, new)

# the middle already carries z-index:2 - say why it matters now that it does
old2 = u".fo-slot:nth-child(2){transform:translateY(-6px);z-index:2}"
new2 = (u"/* z-index:2 was inert while they were apart. Overlapping, it is what makes\n"
        u"   the row an arch with its outer cards tucked BEHIND the middle, instead\n"
        u"   of a left-to-right shingle. */\n"
        u".fo-slot:nth-child(2){transform:translateY(-6px);z-index:2}")
if s.count(old2) != 1:
    sys.exit('ANCHOR x%d for the middle slot' % s.count(old2))
s = s.replace(old2, new2)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('  ok  P647 the slots tuck again (+4% -> -1%)')
