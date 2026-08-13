# -*- coding: utf-8 -*-
"""P697c: the focus scrim and panel exist BEFORE the first tap.

Measured: a scrim created and class-flipped in the same tick froze its enter
transition at currentTime 0 (opacity pinned at 0 - transitions outrank even
!important while they run), while the shelf's own scrim read 1 in the same
headless run. The shelf's scrim was created on an EARLIER open: by the time
a transition starts it owns a committed opacity:0 frame. Same contract here:
mount both pieces when the offer is injected, so every focus is a
'second open'. The lazy creation inside _foCardFocus stays as a fallback.
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
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"function _foCardFocus(el,d,tier,opts){",
    u"/* P697c: mounted at offer-injection time so the first focus transitions\n"
    u"   from a COMMITTED opacity:0 - a scrim born in the tap's own tick froze\n"
    u"   its enter transition at t=0 and the fade never ran (measured; the\n"
    u"   shelf never hits this only because its scrim outlives opens). */\n"
    u"function _foFocusPrep(){\n"
    u"  var ov=document.getElementById('end-ov');if(!ov)return;\n"
    u"  var host=ov.querySelector('.res-card')||ov;\n"
    u"  var scrim=document.getElementById('foFocusScrim');\n"
    u"  if(!scrim||!scrim.isConnected){scrim=document.createElement('div');scrim.id='foFocusScrim';host.appendChild(scrim);}\n"
    u"  scrim.onclick=_foUnfocus;\n"
    u"  if(!document.getElementById('foFocusPanel')){var pan=document.createElement('div');pan.id='foFocusPanel';ov.appendChild(pan);}\n"
    u"}\n"
    u"function _foCardFocus(el,d,tier,opts){",
    'P697c _foFocusPrep')

sub(u"    try{_foInstallDrag();}catch(e){}\n"
    u"    if(endBtns)endBtns.style.display='none';",
    u"    try{_foInstallDrag();}catch(e){}\n"
    u"    try{_foFocusPrep();}catch(e){}/* P697c */\n"
    u"    if(endBtns)endBtns.style.display='none';",
    'P697c prep at offer injection')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
