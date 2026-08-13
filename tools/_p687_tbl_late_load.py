# -*- coding: utf-8 -*-
"""P687: dice shadows survive a slow table image.

Found by the lifecycle probe on a fresh boss match: canvas sized, light on,
dice settled - and BLANK. _drawDiceShadows bails when _tblImg (the table art
it masks against) has not finished loading, and nothing repaints when it
does; the settle marks have already passed, so a fresh match on a slow load
shows no shadows until some unrelated dirty event. The prop-shadow painter
paid for this exact trap already (it re-queues itself once on the image's
load, line ~19859); the dice painter just never got the same fix. Mirrored.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"  x.clearRect(0,0,W,H);\n"
       u"  /* already cleared above, so this one may simply leave */\n"
       u"  if(!_tblImg.complete||!_tblImg.naturalWidth)return;")
new = (u"  x.clearRect(0,0,W,H);\n"
       u"  /* already cleared above, so this one may simply leave */\n"
       u"  /* P687: ...but not silently forever. The settle marks have already\n"
       u"     passed by the time a slow table image arrives, so a fresh match\n"
       u"     painted NO dice shadows until some unrelated dirty event. The prop\n"
       u"     painter re-queues itself on the image's load (its own copy of this\n"
       u"     exact trap); the dice painter now does the same, through the one\n"
       u"     dirty mark. */\n"
       u"  if(!_tblImg.complete||!_tblImg.naturalWidth){\n"
       u"    if(!_tblImg.complete)_tblImg.addEventListener('load',function(){_dsDirty();},{once:true});\n"
       u"    return;\n"
       u"  }")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P687 late table image marks dirty')
