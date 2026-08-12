# -*- coding: utf-8 -*-
"""P642: the shelf's card row lifts, and its two numbers become one.

Denis: "Move the cards and cards slot a few pixels up so they don't flirt with
the top of the dice."

71.5 -> 69.5, about 18px on the design phone.

AND IT STOPS BEING TWO NUMBERS. The row's y lived in the SLOTS array while the
tilt's pivot lived in CSS as transform-origin:50% 71.4% - a tenth of a per cent
apart, deliberately, and needing to be edited in lockstep forever. Moving the
row would have silently left the pivot behind, and a pivot off the row is the
one thing that makes the cards' CENTRES move when the plane tilts, which is what
P636 chose the origin to prevent and what _loCardFocus measures against.

So the plane's origin is now written inline from the same constant the slots are
placed from. The CSS declaration is REMOVED rather than left as a fallback: an
inline style always beats it, so it could only ever be a wrong value waiting to
be believed. One builder writes this element, and it always writes the origin.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"  var SLOTS=[[19.6,71.5],[50.5,71.5],[78.5,71.5]];",
    u"  /* P642: ONE NUMBER FOR THE ROW. It places the three slots AND the tilt's\n"
    u"     pivot (written inline on #loCardPlane below), which used to be a separate\n"
    u"     71.4% in CSS. A pivot that is not on the row makes the cards' centres\n"
    u"     move when the plane tilts - the exact thing P636 chose the origin to\n"
    u"     prevent, and what _loCardFocus measures its flight against.\n"
    u"     71.5 -> 69.5 per Denis: off the top of the dice. */\n"
    u"  var _LO_CARD_ROW_Y=69.5;\n"
    u"  var SLOTS=[[19.6,_LO_CARD_ROW_Y],[50.5,_LO_CARD_ROW_Y],[78.5,_LO_CARD_ROW_Y]];",
    'P642 one constant for the shelf row')

sub(u"      +'<div id=\"loCardPlane\">'+cHtml+'</div>'+dHtml",
    u"      +'<div id=\"loCardPlane\" style=\"transform-origin:50% '+_LO_CARD_ROW_Y+'%\">'+cHtml+'</div>'+dHtml",
    'P642 the pivot comes from the same constant')

sub(u"#loCardPlane{position:absolute;inset:0;pointer-events:none;\n"
    u"  transform-origin:50% 71.4%;transform:perspective(371px) rotateX(35deg);\n"
    u"  transition:transform .55s cubic-bezier(.3,1.35,.35,1)}",
    u"/* transform-origin is NOT here. P642 writes it inline from _LO_CARD_ROW_Y,\n"
    u"   the same constant that places the slots, so the row and its pivot cannot\n"
    u"   drift apart. A value left here could only ever be a wrong one waiting to be\n"
    u"   believed - an inline style always wins - and famLoadoutShow is the only\n"
    u"   thing that builds this element. */\n"
    u"#loCardPlane{position:absolute;inset:0;pointer-events:none;\n"
    u"  transform:perspective(371px) rotateX(35deg);\n"
    u"  transition:transform .55s cubic-bezier(.3,1.35,.35,1)}",
    'P642 drop the duplicate pivot')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
