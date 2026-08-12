# -*- coding: utf-8 -*-
"""P658: the drag stops lagging, shows its glow, and fires with the game's own FX.

Denis: "I can drag it although it's laggy. And there is no FX around, no glow to
let me know I can activate it, no fx when I release and actually activate."

THE GLOW WAS BEING CLOBBERED, not missing. #famRowP .fcv.armed already carries
the gold drop-shadow - P633 widened it to both rows - but P657's .fcv-drag rule
set `filter` too, and a filter REPLACES rather than adds. Same specificity, later
in the sheet, so the drag's shadow won every time the card was in hand, which is
the only time the armed state can happen. .fcv-drag no longer touches filter, so
.armed shows exactly when it applies.

THE LAG WAS THREE FORCED LAYOUTS PER MOVE. Every touchmove read
getBoundingClientRect() on the card and then _famThresholdY() read two more - the
row and the strut - and each read after a style write flushes layout. On a finger
producing 60 events a second that is 180 synchronous layouts.
  * the threshold is measured ONCE, at drag start. It cannot move during a drag:
    the row is not being relaid out and the strut's height is a CSS constant.
  * the card's centre is computed from its start rect plus the drag delta rather
    than re-read - the same number, without asking the engine for it.
  * the transform is written in a rAF, so a burst of moves between frames
    collapses into one write instead of one each.
  * will-change:transform, so the compositor keeps it on its own layer.

AND THE RELEASE USES THE GAME'S OWN FX, not new ones: SFX.cardFire(), the
_haptic pattern, spawnCardBurst() for the plume in the card's colour, and the
cardFired keyframes - all four already written for the legacy row's activation
in P617/P619. The keyframes were bound to .mcard only; they now cover .fcv too,
which is one selector rather than a second animation.
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


# ── 1. the gesture: measure once, write in a frame ───────────────────────
sub(u"  function start(e){\n"
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
    u"  }",
    u"  function start(e){\n"
    u"    if(!_famCanPlay(i))return;\n"
    u"    if(e&&e.button!==undefined&&e.button!==0)return;\n"
    u"    /* one drag at a time - a second finger must not steal an airborne card,\n"
    u"       the same rule P615 had to add to the legacy row */\n"
    u"    if(_famDrag&&_famDrag.live&&_famDrag.el!==el)return;\n"
    u"    var t=e.touches?e.touches[0]:e;\n"
    u"    /* P658: EVERYTHING THAT NEEDS LAYOUT IS READ ONCE, HERE. Reading the\n"
    u"       card's rect and the threshold on every move meant three forced layouts\n"
    u"       per event - the card, the row and the strut - and a finger produces\n"
    u"       sixty events a second. Neither number can change mid-drag: the row is\n"
    u"       not being relaid out and the strut's height is a CSS constant. */\n"
    u"    var r0=el.getBoundingClientRect();\n"
    u"    _famDrag={el:el,i:i,x0:t.clientX,y0:t.clientY,live:false,\n"
    u"              cy0:r0.top+r0.height/2,line:_famThresholdY(),\n"
    u"              dx:0,dy:0,raf:0,armed:false};\n"
    u"  }\n"
    u"  function paint(){\n"
    u"    var d=_famDrag;if(!d||d.el!==el)return;d.raf=0;\n"
    u"    el.style.transform='translate('+d.dx.toFixed(1)+'px,'+d.dy.toFixed(1)+'px)';\n"
    u"    /* the centre from the start rect plus the delta - the same number the\n"
    u"       engine would give back, without asking it */\n"
    u"    var armed=(d.cy0+d.dy)<d.line;\n"
    u"    if(armed!==d.armed){d.armed=armed;el.classList.toggle('armed',armed);}\n"
    u"  }\n"
    u"  function move(e){\n"
    u"    if(!_famDrag||_famDrag.el!==el)return;\n"
    u"    var t=e.touches?e.touches[0]:e;\n"
    u"    var dx=t.clientX-_famDrag.x0,dy=t.clientY-_famDrag.y0;\n"
    u"    if(!_famDrag.live&&Math.hypot(dx,dy)<10)return;\n"
    u"    if(!_famDrag.live){_famDrag.live=true;el.classList.add('fcv-drag');}\n"
    u"    /* `transform` and not `translate`: .fcv's rotate and translate carry the\n"
    u"       fan, and the standalone properties compose rather than replace, so the\n"
    u"       card keeps its angle while it lifts.\n"
    u"       Written in a FRAME, so a burst of moves between paints collapses into\n"
    u"       one write instead of one each. */\n"
    u"    _famDrag.dx=dx;_famDrag.dy=dy;\n"
    u"    if(!_famDrag.raf)_famDrag.raf=requestAnimationFrame(paint);\n"
    u"    if(e.cancelable)e.preventDefault();\n"
    u"  }",
    'P658 measure once, paint in a frame')

# ── 2. the release: the game's own FX ────────────────────────────────────
sub(u"  function end(){\n"
    u"    if(!_famDrag||_famDrag.el!==el)return;\n"
    u"    var live=_famDrag.live,idx=_famDrag.i;_famDrag=null;\n"
    u"    var armed=el.classList.contains('armed');\n"
    u"    el.classList.remove('fcv-drag','armed');\n"
    u"    el.style.transform='';\n"
    u"    if(!live)return;/* a tap - famCardTap's onclick still has it */\n"
    u"    if(armed)try{famUse(idx);}catch(err){}\n"
    u"  }",
    u"  function end(){\n"
    u"    if(!_famDrag||_famDrag.el!==el)return;\n"
    u"    var live=_famDrag.live,idx=_famDrag.i,raf=_famDrag.raf;_famDrag=null;\n"
    u"    if(raf)cancelAnimationFrame(raf);\n"
    u"    var armed=el.classList.contains('armed');\n"
    u"    el.classList.remove('fcv-drag','armed');\n"
    u"    el.style.transform='';\n"
    u"    if(!live)return;/* a tap - famCardTap's onclick still has it */\n"
    u"    if(!armed)return;/* released short of the line - it just goes home */\n"
    u"    /* P658: THE GAME'S OWN FIRE, not new effects. All four of these were\n"
    u"       written for the legacy row's activation in P617/P619 and none of them\n"
    u"       knows or cares which row the card came from. The plume goes BEFORE the\n"
    u"       effect for the same reason it does there: a card that rebuilds the row\n"
    u"       as part of its own effect still gets its beat off the element the\n"
    u"       player was holding. */\n"
    u"    try{SFX.cardFire();}catch(err){try{SFX.nav();}catch(e2){}}\n"
    u"    try{_haptic([12,30,12]);}catch(err){}\n"
    u"    try{spawnCardBurst(el);}catch(err){}\n"
    u"    el.classList.add('card-fired');\n"
    u"    setTimeout(function(){el.classList.remove('card-fired');},420);\n"
    u"    try{famUse(idx);}catch(err){}\n"
    u"  }",
    'P658 fire with the existing FX')

# ── 3. the drag must not eat the armed glow ──────────────────────────────
sub(u"/* P657: the card in hand. No transition while dragging - the transform is set\n"
    u"   every move and an easing curve on it lags the finger - and above the rest\n"
    u"   of the table so it is never dragged behind the dice or the controls. */\n"
    u"#famRowP .fcv.fcv-drag{transition:none;z-index:9500;pointer-events:none;\n"
    u"  filter:drop-shadow(0 1cqw 1.4cqw rgba(10,6,2,.6))}\n"
    u"#famRowP .fcv.fcv-drag .fcvIn{animation:none}",
    u"/* P657/P658: the card in hand. No transition while dragging - the transform is\n"
    u"   set every frame and an easing curve on it lags the finger - and above the\n"
    u"   rest of the table so it is never dragged behind the dice or the controls.\n"
    u"   NO `filter` HERE, and that is the fix for \"no glow\": .fcv.armed carries the\n"
    u"   gold drop-shadow, a filter REPLACES rather than adds, and this rule has the\n"
    u"   same specificity but comes later - so the drag's own shadow won every time\n"
    u"   the card was in hand, which is the only time armed can happen.\n"
    u"   will-change so the compositor keeps the moving card on its own layer. */\n"
    u"#famRowP .fcv.fcv-drag{transition:none;z-index:9500;pointer-events:none;\n"
    u"  will-change:transform}\n"
    u"#famRowP .fcv.fcv-drag .fcvIn{animation:none}\n"
    u"/* the fire flash, on the family card too - one selector rather than a second\n"
    u"   set of keyframes */\n"
    u".fcv.card-fired{animation:cardFired .42s ease-out}",
    'P658 stop clobbering the glow')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
