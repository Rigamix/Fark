# -*- coding: utf-8 -*-
"""P451 - Hair of the Dog's live stake, on screen for the first time.

RULED: the stake stays visible for as long as it is live. Measured, only ONE of
the three cards without a chip was actually missing anything:

  High Table    had no pending window at all - it changes a number the seat
                sheet already shows, and that number was WRONG (P449/P450).
  Cursed Table  already surfaces at the decision point; its marker was there
                and wrong, not missing (P449).
  Hair of the Dog  a real live wager, armed across a match boundary, with
                nothing on screen. This one.

IT IS A STATUS INDICATOR, NOT A CHIP, AND THAT DISTINCTION IS THE RULING. The
three cards that already render in the chip row do so because they are
CONTROLS - arm Double Stakes, pay the tab, arm For Keeps. Every one takes a
tap. Hair of the Dog takes no input: it armed itself when you lost and it
resolves on its own at your next first bank. Giving it a chip would put a
tappable-looking thing in a row of tappable things and have it do nothing.

So it renders in the same row, from the same absorption point, with a
deliberately different treatment: no onclick, no pointer cursor, and it states
BOTH sides of the wager because P447 gave it a downside. A marker that showed
only the doubled bank would be advertising the pure-upside card that no longer
exists - the same mismatch the seat sheet had.

BOTH ROOM VIEWS, because the chip row is hand-written twice - _gbRenderRoom and
_ptRoom. Absorbing that duplication is a bigger job than this patch and is
noted rather than attempted; adding to one and not the other would make the
marker appear or vanish depending on which screen the player came through.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the gbx Room view ──
A = (u"  if(famOwnTier('the_tab')>0&&!S.run._tabOwed)chips+='<div class=\"gbx-box sub\" "
     u"onclick=\"famTabTake()\"")
assert s.count(A) == 1, 'gbx anchor matched %d' % s.count(A)
s = s.replace(A,
  u"""  /* HAIR OF THE DOG: a STATUS, not a control. No onclick and no pointer -
     the player armed nothing and can do nothing about it; it fired when they
     lost and pays at their next first bank. It sits in the chip row because
     that is where run-scoped state is read, but it must not look tappable in a
     row where everything else is.
     BOTH SIDES, because P447 gave this card a downside: showing only the
     doubled bank would advertise the pure-upside version that no longer
     exists. */
  if(S.run._hotdNext)chips+='<div class="gbx-box sub" style="height:30px;padding:0 10px;'
    +'font-size:12px;cursor:default;border:2px solid #6b4a7a;opacity:.92">'
    +'HUNGOVER \\u2014 first bank doubled, bust before it and a circle goes</div>';
""" + A)

# ── the patron-table Room view ──
B = (u"  if(famOwnTier('the_tab')>0&&!S.run._tabOwed)chips+='<div onclick=\"famTabTake()\">"
     u"the tab \\u2014 ")
n = s.count(B)
if n != 1:
    # the em-dash may be a literal character rather than an escape in source
    B = u"  if(famOwnTier('the_tab')>0&&!S.run._tabOwed)chips+='<div onclick=\"famTabTake()\">the tab "
    n = s.count(B)
assert n == 1, 'ptRoom anchor matched %d' % n
s = s.replace(B,
  u"""  /* same status, same rules, second view - see the note in _gbRenderRoom.
     Rendered in both because this row is written out twice; adding it to one
     would make the marker depend on which screen the player arrived through. */
  if(S.run._hotdNext)chips+='<div style="cursor:default;border-color:#6b4a7a">'
    +'hungover \\u2014 first bank doubled, bust first and a circle goes</div>';
""" + B)

assert s != orig, 'nothing changed'
assert s.count("if(S.run._hotdNext)chips+=") == 2, \
    'marker sites %d (want 2 - both Room views)' % s.count("if(S.run._hotdNext)chips+=")
# it must not be tappable in either view
import re
# BOUNDED TO THE MARKER'S OWN STATEMENT. A fixed 320-char window ran past the
# end of it into the NEXT chip in the row - the tab chip, which does have an
# onclick, correctly - so the check was reading a neighbour and blaming this
# patch. Same too-wide-a-window mistake as the three-line adjacency scan that
# undercounted co-located clears in the doBust trace.
for m in re.finditer(r"if\(S\.run\._hotdNext\)chips\+=(.*?</div>';)", s, re.S):
    assert 'onclick' not in m.group(1), 'the status marker has an onclick'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P451 applied: hangover status marker, both Room views, no onclick')
