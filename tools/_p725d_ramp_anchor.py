# -*- coding: utf-8 -*-
"""P725d: flight and settled agree on what phys.t MEANS.

The flight ramp ends AT the die's settle moment (P720: the shadow lands
WITH the die) - k=1 when now reaches _lt. _settleDim still carried the
pre-P720 catch-up semantic: k=0 AT phys.t, ramping for 350ms after. For
early settlers the difference is invisible (350ms have long passed by
the handoff), but a die settling within 350ms of the tape's end is
REWOUND to partial dim at handoff and re-ramps - the subtle residual
flicker, always on the last dice to land. A dim->lighter-dim swap is not
a bright restore, which is how it hid from the setter trap's filter.
One-line fix: the settled ramp ends at phys.t too, same curve, same
anchor, so the two formulas agree at every moment a handoff can happen.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"    var self=this,_R=this.SIDEDIM_RAMP;\n"
    u"    var _k=(performance.now()-(d.phys.t||0)-_R.delay)/_R.dur;",
    u"    var self=this,_R=this.SIDEDIM_RAMP;\n"
    u"    /* P725d: phys.t is the ramp's END, exactly as the flight formula\n"
    u"       treats the settle moment (P720: the shadow lands WITH the die) -\n"
    u"       treating it as the START rewound any die that settled within\n"
    u"       350ms of the tape's end to partial dim at the handoff. */\n"
    u"    var _k=(performance.now()-((d.phys.t||0)-_R.dur)-_R.delay)/_R.dur;",
    'settled ramp ends at phys.t')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
