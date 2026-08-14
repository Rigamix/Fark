# -*- coding: utf-8 -*-
"""P725c: the tape-end frame no longer flashes the dim off.

The setter-trap probe caught the surviving flicker at exactly the frame
the tape ends: the rolling branch calls _physPose first, which detects
the tape is done and settles the die MID-FRAME (d.roll=null, d.phys set)
- then the flight-dim IIFE below it reads R2=d.roll, finds null, computes
k=0 and restores the authored bright map. One full bright frame on every
still-dimmed die, timed to the LAST die's settle, re-dimmed only by the
next frame's settled branch. P725's backdate fixed the ramp restart and
P725b the rebuild flash; this was the third writer, hiding inside the
same frame. A die whose tape just ended now goes straight to _settleDim
- the one settled-dim path - which computes k=1 from the backdated
phys.t, so the map never leaves dim.
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


sub(u"          (function(){\n"
    u"            var R2=d.roll,_lt=0;\n",
    u"          (function(){\n"
    u"            var R2=d.roll;\n"
    u"            /* P725c: _physPose above may have ENDED the tape THIS frame -\n"
    u"               d.roll is already null and d.phys exists. The flight formula\n"
    u"               below would read _lt=0 and restore the authored map: one\n"
    u"               full bright frame before the settled branch re-dims (the\n"
    u"               flicker's third writer, caught by the setter trap at the\n"
    u"               tape-end frame). Hand the die to the ONE settled-dim path. */\n"
    u"            if(!R2){if(d.phys)D3X._settleDim(d);return;}\n"
    u"            var _lt=0;\n",
    'tape-end frame goes to _settleDim')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
