# -*- coding: utf-8 -*-
"""P609: the shelf's card reader becomes the die reader.

Denis: "Card tooltip should be the same everywhere, and it should be like the die
tooltip: full focus screen effect with a subtle hover animation, darkening the bg
and blurring. all the EXACT same." Scope: NOT the match screen - he has a
different plan for in-match card tooltips.

WHAT "THE DIE TOOLTIP" IS. Not .die-tooltip / attachDieTooltipTap - that is a
legacy 200px anchored popup with no scrim. It is the FOCUS treatment: a blurred,
darkened scrim, the subject zoomed and floating, and a panel of text. It already
exists four times over ONE shared CSS block (_loFocus shelf, _stFocus store,
_ptDieFocus patron, _nrFocus first-night offer).

AND ONLY ONE CARD SURFACE OUTSIDE THE MATCH IS STILL WRONG. _ptCardFocus already
wears the die treatment - it is the reference implementation copied below. The
.mcard-tooltip family is dead on every non-match screen (their hosts were
superseded by the painted gb*/pt* layer). famCardSheet is SHARED with in-match
famCardTap/famOppTap and is deliberately untouched. That leaves the shelf, where
the SAME pointerdown delegate sends a die tap to the full focus treatment and a
card tap to _loTip, a 100px box with the room fully lit.

THE NON-OBVIOUS HALF IS THE DICE. #gbLoadout.lo-focus lifts the whole WebGL
canvas to z-index 60 so a zoomed die clears the scrim, and D3X only hides the
other dice when one of ITS OWN chips carries .zoom. Focus a CARD and `zoomed`
stays null, so the prototype's first screenshot was six fully-lit sharp dice
sitting on top of a darkened, blurred room. The .loDie rule below is what fixes
that, by the same route the patron panel already uses: D3X's visibility test
reads getComputedStyle(chip).opacity.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1. the float, unscoped so a focused card bobs the way a focused die does.
#    .zoom is added by five call sites, all focus openers; no in-match .fcv
#    ever receives it, so this cannot leak into the match.
sub(u"#ptvFan .fcv.zoom .fcvIn{animation:fcvFloat 4.4s ease-in-out .55s infinite}",
    u"/* P609: unscoped from #ptvFan - the same bob now serves the shelf's card\n"
    u"   focus. `.zoom` is only ever set by the focus openers, never in-match. */\n"
    u".fcv.zoom .fcvIn{animation:fcvFloat 4.4s ease-in-out .55s infinite}",
    'P609 float unscoped')

# 2. the shelf's focus rules, including the load-bearing dice one
sub(u".loFeat.unpinned{opacity:0;pointer-events:none;transition:opacity .35s}",
    u".loFeat.unpinned{opacity:0;pointer-events:none;transition:opacity .35s}\n"
    u"/* P609: the shelf's CARD focus, matching its die focus. */\n"
    u"#loStage .loCard{transition:opacity .3s}\n"
    u"#loStage .loCard.zoom{z-index:60}\n"
    u"#gbLoadout.lo-focus #loStage .loCard:not(.zoom){opacity:0;pointer-events:none}\n"
    u"/* THIS ONE IS LOAD-BEARING. #gbLoadout.lo-focus lifts #d3xCanvas to z-index\n"
    u"   60 so a zoomed DIE clears the scrim, and D3X only hides the other dice\n"
    u"   when one of its own chips carries .zoom. With a CARD zoomed nothing tells\n"
    u"   it to stand down, so six fully-lit sharp dice sat on top of the blurred\n"
    u"   room. D3X's visibility test reads computed opacity, which is exactly how\n"
    u"   the patron panel already solves this. */\n"
    u"#gbLoadout.lo-focus #loStage .loDie:not(.zoom){opacity:0;pointer-events:none}",
    'P609 shelf focus CSS')

# 3. route the shelf's card taps at the focus opener instead of the small box
sub(u"    else if(cd){\n"
    u"      var cdd=famDef(cd.getAttribute('data-cid'));\n"
    u"      var own=(S.run.fcards||[]).filter(function(c){return famDef(c.id)===cdd;})[0];\n"
    u"      var t=(own&&own.tier)||1;\n"
    u"      if(cdd)_loTip(cd,cdd.name+(cdd.fam==='tavern'?'':' '+['I','II','III'][t-1]),cdd.text[t-1]);\n"
    u"    }\n",
    u"    else if(cd){\n"
    u"      /* P609: the full focus treatment, not _loTip's small anchored box.\n"
    u"         The die branch two lines up has always opened _loFocus; this is the\n"
    u"         same delegate finally treating both taps alike. */\n"
    u"      var own=(S.run.fcards||[]).filter(function(c){return c.id===cd.getAttribute('data-cid');})[0];\n"
    u"      _loCardFocus(cd,(own&&own.tier)||1);\n"
    u"    }\n",
    'P609 shelf delegate')

# 4. the opener itself, modelled line-for-line on _ptCardFocus
sub(u"/* small anchored tooltip: name + one-liner, tap-away dismiss */",
    u"/* P609: the shelf's card focus - the die treatment, for a card.\n"
    u"   Deliberately a near-copy of _ptCardFocus rather than a generalisation of\n"
    u"   it: the two panels differ in which screen root and scrim they mount on,\n"
    u"   and folding them together would mean a parameterised opener serving four\n"
    u"   surfaces whose only shared part is already shared - the CSS block.\n"
    u"   _loUnfocus needs no change: .loCard's resting transform is CSS-only, so\n"
    u"   clearing the inline one restores it, and its chip._d3 guard no-ops here. */\n"
    u"function _loCardFocus(el,tier){\n"
    u"  var ov=document.getElementById('gbLoadout');\n"
    u"  if(!ov||ov.classList.contains('lo-focus'))return;\n"
    u"  var d=famDef(el.getAttribute('data-cid'));if(!d)return;\n"
    u"  tier=tier||1;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#ffd98a';\n"
    u"  _loTipHide();\n"
    u"  var stage=document.getElementById('loStage');\n"
    u"  var scrim=document.getElementById('loFocusScrim');\n"
    u"  if(!scrim){scrim=document.createElement('div');scrim.id='loFocusScrim';(stage||ov).appendChild(scrim);}\n"
    u"  scrim.onclick=_loUnfocus;\n"
    u"  var pan=document.getElementById('loFocusPanel');\n"
    u"  if(!pan){pan=document.createElement('div');pan.id='loFocusPanel';ov.appendChild(pan);}\n"
    u"  pan.innerHTML='<div class=\"fname\" style=\"color:'+col+';--fnoc:'+_fkDarker(col)+'\">'+_fkSheen(d.name)+'</div>'\n"
    u"    +'<div class=\"ffaces\" style=\"font-size:2cqh\"><span style=\"color:'+col+'\">'+FAMILIES[d.fam].name+'</span>'\n"
    u"      +'<span style=\"color:#cfc0a8\"> \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE')+'</span></div>'\n"
    u"    +'<div class=\"fdesc\">'+_accG(d.text[tier-1])+'</div>'\n"
    u"    +'<div id=\"loFBack\" onclick=\"_loUnfocus()\"><img src=\"Art/Assets/Icons/optimized/close_opt.webp\" alt=\"close\"></div>';\n"
    u"  var gr=ov.getBoundingClientRect(),nr=el.getBoundingClientRect();\n"
    u"  /* K is 2.05, not the die's 2.3: a card is already the taller subject and\n"
    u"     2.3 pushed its head under the panel's name line. */\n"
    u"  var K=2.05;\n"
    u"  var wr=(Math.random()<0.5?-1:1)*(0.6+Math.random()*1.0);\n"
    u"  var ncx=nr.left+nr.width/2,ncy=nr.top+nr.height/2;\n"
    u"  var dx=(gr.left+gr.width/2)-ncx,dy=(gr.top+gr.height*0.365)-ncy;\n"
    u"  el.style.transition='transform .55s cubic-bezier(.3,1.35,.35,1)';\n"
    u"  el.style.transform='translate(calc(-50% + '+dx.toFixed(1)+'px), calc(-50% + '+dy.toFixed(1)+'px)) rotate('+wr.toFixed(1)+'deg) scale('+K+')';\n"
    u"  el.classList.add('zoom');\n"
    u"  ov.classList.add('lo-focus');\n"
    u"  window._loFocSp=el;\n"
    u"}\n"
    u"/* small anchored tooltip: name + one-liner, tap-away dismiss */",
    'P609 _loCardFocus')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
