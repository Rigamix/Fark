# -*- coding: utf-8 -*-
"""P724: the side shadow fades in PER DIE, at each die's own landing.

Denis: "sometimes a die might settle quite earlier than another. Can the
game recognize this and start the shadow fade per die?" It can: the tape
is shared but each die's track inside it goes still at its own frame. The
ramp keyed on the tape's END (the slowest die), so the whole row dimmed
together. Now each die's settle frame is found once - a backward scan of
its own positions AND orientation (a die can spin in place) with the
solver's own stillness epsilon - cached on its roll, and that moment ends
its ramp. An early settler starts dimming while its neighbours tumble.
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
    u"            var R2=d.roll,_lt=(R2&&R2.sol&&R2.sol.frames)?R2.t0+R2.sol.frames.length*(D3X.PHYS.dt*1000):0;\n",
    u"          (function(){\n"
    u"            var R2=d.roll,_lt=0;\n"
    u"            if(R2&&R2.sol&&R2.sol.frames){\n"
    u"              /* P724: THIS die's own settle frame, not the tape's end -\n"
    u"                 found once by walking its track backward until position\n"
    u"                 or orientation moved (the solver's stillness epsilon),\n"
    u"                 cached on the roll. Early settlers dim while their\n"
    u"                 neighbours are still in the air. */\n"
    u"              if(R2._setF===undefined){\n"
    u"                var _fr=R2.sol.frames,_i0=R2.i,_li=_fr.length-1;\n"
    u"                while(_li>1){\n"
    u"                  var _a=_fr[_li-1][_i0],_b=_fr[_li][_i0];\n"
    u"                  if(Math.abs(_b.x-_a.x)+Math.abs(_b.y-_a.y)+Math.abs(_b.z-_a.z)\n"
    u"                    +Math.abs(_b.qx-_a.qx)+Math.abs(_b.qy-_a.qy)+Math.abs(_b.qz-_a.qz)>0.006)break;\n"
    u"                  _li--;\n"
    u"                }\n"
    u"                R2._setF=_li;\n"
    u"              }\n"
    u"              _lt=R2.t0+R2._setF*(D3X.PHYS.dt*1000);\n"
    u"            }\n",
    'P724 per-die settle moment ends the ramp')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
