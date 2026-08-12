# -*- coding: utf-8 -*-
"""P657: the activation drag moves to the row the player's cards are actually in.

Denis, twice: "The card activation new mechanic doesn't work at all? Can't drag
anything in match." P656 made #playerCards hit-testable and he still could not
drag, which is the answer: the touch was never the problem, because THERE IS
NOTHING IN THAT ROW.

MEASURED (tools/apv_which_row.js), taking a card through the draft's own
famApplyPick and then launching a seat:
    draft wrote to the legacy loadout   false
    draft wrote to the family cards     true
    in match  G.pCards []   G.pF ['transmute']
    #playerCards .mcard  0        <- what initCardDrag is bound to
    #famRowP .fcv        1        <- what the player is holding
The draft writes S.run.fcards. #playerCards is built from G.pCards, which comes
from S.run.cards - the legacy four-slot loadout the draft never touches. So the
drag has been bound to a row that is empty in every real run.

AND MY OWN VERIFICATION OF IT WAS THE REASON THIS SURVIVED. P615's probe seeded
S.run.cards by hand before launching, so it proved the gesture works on cards
the player never has. The lesson is already in this project's notes - a harness
that supplies its own input cannot tell you the game supplies it - and this is
the same mistake one level further out: the row was right, the row's CONTENTS
were mine.

WHAT THIS DOES: binds the same gesture to the family cards. The threshold, the
strut, the armed look and the fire-on-release-above-the-line are the existing
mechanics; only the row and the fire call change. Firing goes through famUse,
which already owns the guards - active kind, a CFX use handler, charges left,
and the card's own canUse - so nothing about what a card may do is
re-implemented here.

The legacy row keeps its own drag. It is empty today, but it is not this
patch's business to remove a layer, and leaving both means nothing regresses if
S.run.cards is ever filled again.
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


# ── 1. the threshold learns which row it is measuring ────────────────────
sub(u"function _cardThresholdY(){\n"
    u"  var row=document.getElementById('playerCards');\n"
    u"  if(!row)return -1e9;/* no row: nothing can be above the line */",
    u"/* P657: takes the ROW now. The lift is the same knob and the same strut for\n"
    u"   both hands; what differs is which row's top the line sits above. Defaults\n"
    u"   to the legacy row so every existing caller is unchanged. */\n"
    u"function _cardThresholdY(rowEl){\n"
    u"  var row=rowEl||document.getElementById('playerCards');\n"
    u"  if(!row)return -1e9;/* no row: nothing can be above the line */",
    'P657 the threshold takes a row')

sub(u"function _cardIsArmed(el){",
    u"/* P657: the family hand's own line - same strut, same lift, measured from\n"
    u"   #famRowP because that is the row those cards leave. */\n"
    u"function _famThresholdY(){\n"
    u"  return _cardThresholdY(document.getElementById('famRowP'));\n"
    u"}\n"
    u"function _cardIsArmed(el){",
    'P657 the family threshold')

# ── 2. the gesture, on the cards the player holds ────────────────────────
sub(u"/* tap a card at the table: the painted sheet; PLAY when usable */\n"
    u"function famCardTap(i){",
    u"/* P657: DRAG A FAMILY CARD UP TO PLAY IT. The same gesture P612 built for the\n"
    u"   legacy row, on the row that actually holds the player's cards - see the\n"
    u"   note in tools/_p657_family_card_drag.py for how it came to be on the wrong\n"
    u"   one.\n"
    u"   A TAP IS STILL A TAP: nothing happens under 10px of travel, so famCardTap\n"
    u"   still opens the sheet and its PLAY button still works. Two ways in, and the\n"
    u"   drag is the fast one.\n"
    u"   THE GUARDS ARE famUse'S, NOT COPIES OF THEM. Whether a card can be played -\n"
    u"   active kind, a use handler, charges left, its own canUse - is decided in\n"
    u"   exactly one place, and this only asks whether it is worth starting a drag. */\n"
    u"var _famDrag=null;\n"
    u"function _famCanPlay(i){\n"
    u"  if(!G||!G.pF||!G.pF[i])return false;\n"
    u"  var inst=G.pF[i],d=famDef(inst.id),fx=CFX[inst.id];\n"
    u"  if(!d||d.kind!=='active'||!fx||!fx.use)return false;\n"
    u"  return inst.charges>0;\n"
    u"}\n"
    u"function _famDragInit(el,i){\n"
    u"  if(!el||el._famDrag)return;el._famDrag=1;\n"
    u"  function start(e){\n"
    u"    if(!_famCanPlay(i))return;\n"
    u"    if(e&&e.button!==undefined&&e.button!==0)return;\n"
    u"    /* one drag at a time - a second finger must not steal an airborne card,\n"
    u"       the same rule P615 had to add to the legacy row */\n"
    u"    if(_famDrag&&_famDrag.live&&_famDrag.el!==el)return;\n"
    u"    var t=e.touches?e.touches[0]:e;\n"
    u"    _famDrag={el:el,i:i,x0:t.clientX,y0:t.clientY,live:false};\n"
    u"  }\n"
    u"  function move(e){\n"
    u"    if(!_famDrag||_famDrag.el!==el)return;\n"
    u"    var t=e.touches?e.touches[0]:e;\n"
    u"    var dx=t.clientX-_famDrag.x0,dy=t.clientY-_famDrag.y0;\n"
    u"    if(!_famDrag.live&&Math.hypot(dx,dy)<10)return;\n"
    u"    if(!_famDrag.live){_famDrag.live=true;el.classList.add('fcv-drag');}\n"
    u"    /* `transform` and not `translate`: .fcv's rotate and translate carry the\n"
    u"       fan, and the standalone properties compose rather than replace, so the\n"
    u"       card keeps its angle while it lifts */\n"
    u"    el.style.transform='translate('+dx.toFixed(1)+'px,'+dy.toFixed(1)+'px)';\n"
    u"    var r=el.getBoundingClientRect();\n"
    u"    el.classList.toggle('armed',(r.top+r.height/2)<_famThresholdY());\n"
    u"    if(e.cancelable)e.preventDefault();\n"
    u"  }\n"
    u"  function end(){\n"
    u"    if(!_famDrag||_famDrag.el!==el)return;\n"
    u"    var live=_famDrag.live,idx=_famDrag.i;_famDrag=null;\n"
    u"    var armed=el.classList.contains('armed');\n"
    u"    el.classList.remove('fcv-drag','armed');\n"
    u"    el.style.transform='';\n"
    u"    if(!live)return;/* a tap - famCardTap's onclick still has it */\n"
    u"    if(armed)try{famUse(idx);}catch(err){}\n"
    u"  }\n"
    u"  el.addEventListener('mousedown',start);\n"
    u"  el.addEventListener('touchstart',start,{passive:true});\n"
    u"  document.addEventListener('mousemove',move);\n"
    u"  document.addEventListener('touchmove',move,{passive:false});\n"
    u"  document.addEventListener('mouseup',end);\n"
    u"  document.addEventListener('touchend',end);\n"
    u"  document.addEventListener('touchcancel',end);\n"
    u"}\n"
    u"/* tap a card at the table: the painted sheet; PLAY when usable */\n"
    u"function famCardTap(i){",
    'P657 the family drag')

# ── 3. bind it wherever the row is built ─────────────────────────────────
sub(u"  hostP.innerHTML=hp;",
    u"  hostP.innerHTML=hp;\n"
    u"  /* P657: the row is rebuilt on every change, so the gesture is bound here\n"
    u"     rather than once - _famDragInit is idempotent per element. */\n"
    u"  try{[].forEach.call(hostP.querySelectorAll('.fcv'),function(el,ix){_famDragInit(el,ix);});}catch(e){}",
    'P657 bind on every render')

# ── 4. the dragged card rides above everything ───────────────────────────
sub(u"#famRowP .fcv .fcvIn{animation:famBob 4.6s ease-in-out infinite;will-change:transform}",
    u"#famRowP .fcv .fcvIn{animation:famBob 4.6s ease-in-out infinite;will-change:transform}\n"
    u"/* P657: the card in hand. No transition while dragging - the transform is set\n"
    u"   every move and an easing curve on it lags the finger - and above the rest\n"
    u"   of the table so it is never dragged behind the dice or the controls. */\n"
    u"#famRowP .fcv.fcv-drag{transition:none;z-index:9500;pointer-events:none;\n"
    u"  filter:drop-shadow(0 1cqw 1.4cqw rgba(10,6,2,.6))}\n"
    u"#famRowP .fcv.fcv-drag .fcvIn{animation:none}",
    'P657 the dragging look')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
