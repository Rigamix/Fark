# -*- coding: utf-8 -*-
"""P427b - Steeped pays out through _ruleActive, not off G._tell.

Parking Steeped exposed a split that was invisible while Mabel wore it: the
bonus ACCRUES through `_ruleActive('steeped', ...)`, which sees a badge, a
sleeve and a sealed seat alike - but it PAYS OUT, DISPLAYS and RESETS through
`G._tell.id === 'steeped'`, which only ever sees the boss's own badge.

While Mabel carried it the two agreed and nothing showed. With no boss wearing
it, a cursed seat rolling Steeped would have accrued a bonus every roll and
paid none of it, forever. That is the exact bug P427 just fixed for Zero Hour -
shipping it for Steeped in the same commit would have been a poor trade.

Four sites, all the same one-line change.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

EDITS = [
    # the running turn-total display
    (u"      if(G._tell.id==='steeped'&&G._tellState&&G._tellState.bonus>0)t+=G._tellState.bonus;",
     u"      if(_ruleActive('steeped','p')&&G._tellState&&G._tellState.bonus>0)t+=G._tellState.bonus;",
     'turn total display'),
    # reset when the turn hands over
    (u"    if(G._tell.id==='steeped'&&G._tellState){G._tellState.bonus=0;_updateTellHUD();}",
     u"    if(_ruleActive('steeped','p')&&G._tellState){G._tellState.bonus=0;_updateTellHUD();}",
     'turn handover reset'),
    # reset on bust - it spills, that is the whole rule
    (u"  if(G._tell&&G._tell.id==='steeped'&&G._tellState){G._tellState.bonus=0;_updateTellHUD();}",
     u"  if(_ruleActive('steeped','p')&&G._tellState){G._tellState.bonus=0;_updateTellHUD();}",
     'bust reset'),
    # THE PAYOUT
    (u"    if(G._tell.id==='steeped'&&G._tellState&&G._tellState.bonus>0){",
     u"    if(_ruleActive('steeped','p')&&G._tellState&&G._tellState.bonus>0){",
     'bank payout'),
]

for old, new, what in EDITS:
    n = s.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    s = s.replace(old, new)

# The accrual sites already read _ruleActive; leave them. Prove the split is
# gone rather than asserting it from the edits above.
assert u"G._tell.id==='steeped'" not in s, 'a direct read survives'
assert s.count(u"_ruleActive('steeped'") == 6, \
    "expected 6 _ruleActive('steeped') sites, found %d" % s.count(u"_ruleActive('steeped'")

assert s != orig, 'nothing changed'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P427b applied. 4 direct reads -> _ruleActive')
