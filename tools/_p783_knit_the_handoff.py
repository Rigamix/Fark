# -*- coding: utf-8 -*-
"""P783: the glow's body joins the core canvas - the trough between
blend modes goes.

Denis (2026-08-19): "still there. Somehow your 'core' is darker than
the glow around." Right diagnosis, inverted labels: the scanline shows
bloom peak L205 over the rim, a TROUGH of L153 just outside it, then
the screened spill's L180. The core's blur dies within ~3px, and the
screen-blended spill that takes over CANNOT match the normal-blended
core's luminance over dark wood - screen only brightens toward its
source colour and caps low on a dark backdrop. Two compositing modes,
a valley at the handoff.

The body octave (the gold r8) moves to the CORE canvas as r12: one
continuous NORMAL-blend gradient now runs from the rim bloom down to
nothing over ~12px - visible on any backdrop, grain still showing
through its low-alpha tail - while the screened canvas keeps only the
faint wide pool (r24) that brightens the table underneath it all. No
handoff happens at any brightness the eye can catch.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = """    octaves:[{r:6,col:'#ffe08a',passes:2,core:true},{r:8,col:'#ffd24a'},{r:24,col:'#ff9e30',deep:true}]},"""
new = """    octaves:[{r:6,col:'#ffe08a',passes:2,core:true},{r:12,col:'#ffd24a',core:true},{r:24,col:'#ff9e30',deep:true}]},"""
if s.count(old) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(old))
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the body joins the core canvas')
