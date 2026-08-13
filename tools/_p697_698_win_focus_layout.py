# -*- coding: utf-8 -*-
"""P697+P698: the win screen reads cards the table's way, and its block
stops floating high.

P697 (Denis: "the card focus panel on win screen is still the old one"):
offer and deck taps stop opening the bottom sheet. They use the same
grow + word-stagger focus the table uses - _cardFocusToggle learns to mount
its tip inside #end-ov (the overlay outstacks #screen-match's 9001s, so a
tip mounted below it could never be seen) and carries the one button the
focus will ever hold: CLAIM, on offer cards only. The tavern-floor peek and
the TRADE OUT decision modal keep the sheet - those are different surfaces.

P698 (Denis: "the cards and card slots are a bit too high"): the block gets
a floor as well as a ceiling. On tall phones the safe-area pushed the
painted plaque lower while the block's 47% anchor stayed, so PICK A CARD
sat ON the parchment and an 11%-of-screen dead band opened above SKIP.
Now .res-card spans top 49.5% -> just above the SKIP pill, .fo-wrap flexes
across that span, and .fo-deck's margin-top:auto pins the slots to the
bottom of it - the dead band is spent, on every device, without a per-height
special case.
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


# ── P697.1: the focus mounts where the card lives ──
sub(u"  var ms=document.getElementById('screen-match')||document.body;\n"
    u"  /* P681: while a tip is open the status strips fade, so it never overlaps\n"
    u"     the score or the 'X IS ROLLING' line */\n"
    u"  try{ms.classList.add('tip-open');}catch(e){}",
    u"  /* P697: a card inside the WON overlay mounts its tip THERE - #end-ov is\n"
    u"     a stacking context above the tip's 9001, so a tip left in\n"
    u"     #screen-match would paint underneath the overlay it serves. The rect\n"
    u"     math below is container-relative either way; both boxes are the\n"
    u"     whole screen. */\n"
    u"  var ms=(el.closest&&el.closest('#end-ov'))||document.getElementById('screen-match')||document.body;\n"
    u"  /* P681: while a tip is open the status strips fade, so it never overlaps\n"
    u"     the score or the 'X IS ROLLING' line */\n"
    u"  try{document.getElementById('screen-match').classList.add('tip-open');}catch(e){}",
    'P697 focus mounts in #end-ov when the card is there')

# ── P697.2: the tip can carry CLAIM ──
sub(u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>';\n"
    u"  ms.appendChild(tip);",
    u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>'\n"
    u"    /* P697: the one button the focus ever carries - the win screen's\n"
    u"       CLAIM. At the table nobody passes btn and the focus stays a pure\n"
    u"       reading surface. */\n"
    u"    +(o.btn?'<div class=\"cft-btn\">'+o.btn+'</div>':'');\n"
    u"  ms.appendChild(tip);\n"
    u"  if(o.btn){var _bt=tip.querySelector('.cft-btn');if(_bt)_bt.onclick=function(ev){\n"
    u"    try{ev.stopPropagation();}catch(e){}\n"
    u"    var cb=o.cb;_cardFocusClose();if(cb)try{cb();}catch(e){}\n"
    u"  };}",
    'P697 CLAIM button in the tip')

# ── P697.3: the win-screen tap wrappers ──
sub(u"function famUse(i){",
    u"/* P697: the win screen reads cards the same way the table does. The offer\n"
    u"   card's focus carries CLAIM; the drag-to-slot gesture stays the other\n"
    u"   door, untouched. The deck row reads without a button. */\n"
    u"function _foOfferTap(i){\n"
    u"  var o=_famOffer&&_famOffer[i];if(!o)return;\n"
    u"  var d=famDef(o.id);if(!d)return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  _cardFocusToggle(document.querySelectorAll('#end-ov .fo-offer .fcv')[i],{\n"
    u"    title:d.name.toUpperCase(),\n"
    u"    sub:FAMILIES[d.fam].name+' \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE')\n"
    u"       +(d.consumable||d.id==='for_keeps'?' \\u00b7 BURNS ON USE':'')\n"
    u"       +(o.upgrade?' \\u00b7 UPGRADE':''),\n"
    u"    body:d.text[o.tier-1],col:col,below:true,\n"
    u"    btn:'CLAIM',cb:function(){famDraftPick(i);}});\n"
    u"}\n"
    u"function _foDeckTap(ci){\n"
    u"  _getS();var c=S.run&&S.run.fcards&&S.run.fcards[ci];if(!c)return;\n"
    u"  var d=famDef(c.id);if(!d)return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  _cardFocusToggle(document.querySelector('#end-ov .fo-slot[data-ci=\"'+ci+'\"] .fcv'),{\n"
    u"    title:d.name.toUpperCase(),\n"
    u"    sub:FAMILIES[d.fam].name+' \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE'),\n"
    u"    body:d.text[c.tier-1],col:col});\n"
    u"}\n"
    u"function famUse(i){",
    'P697 _foOfferTap/_foDeckTap')

# ── P697.4: the offer stops calling the sheet ──
sub(u"      +famCardHtml(o.id,o.tier,{onclick:\"famCardSheet('\"+o.id+\"',\"+o.tier\n"
    u"        +\",{btn:'CLAIM',badge:\"+(o.upgrade?\"'UPGRADE'\":\"null\")+\",cb:'function(){\"+pickFn+\"(\"+i+\");}'})\",\n"
    u"        sub:(o.upgrade?'(upgrade)':null)})",
    u"      /* P697: the sheet gives way to the table's own focus. pickFn stays\n"
    u"         in the signature for the one caller; the tap wrapper reads\n"
    u"         _famOffer directly and CLAIM lives in the tip now. */\n"
    u"      +famCardHtml(o.id,o.tier,{onclick:\"_foOfferTap(\"+i+\")\",\n"
    u"        sub:(o.upgrade?'(upgrade)':null)})",
    'P697 offer onclick -> focus')

# ── P697.5: the deck row too ──
sub(u"        +' onclick=\"famCardSheet(\\''+_c.id+'\\','+_c.tier+')\">'",
    u"        +' onclick=\"_foDeckTap('+_ci+')\">'/* P697 */",
    'P697 deck onclick -> focus')

# ── P697.6: no stale tip rides into the overlay ──
sub(u"  /* Show animated end overlay */\n"
    u"  var ov=document.getElementById('end-ov');",
    u"  /* Show animated end overlay */\n"
    u"  try{_cardFocusClose();}catch(e){}/* P697: enter focus-clean */\n"
    u"  var ov=document.getElementById('end-ov');",
    'P697 overlay entry closes any focus')

# ── P697.7: the CSS ──
sub(u"@keyframes cftWord{\n"
    u"  0%{opacity:0;translate:0 0.9cqw;filter:blur(2px)}\n"
    u"  100%{opacity:1;translate:0 0;filter:none}}",
    u"@keyframes cftWord{\n"
    u"  0%{opacity:0;translate:0 0.9cqw;filter:blur(2px)}\n"
    u"  100%{opacity:1;translate:0 0;filter:none}}\n"
    u"/* P697: the focus serves the WON overlay too. Its tip mounts in #end-ov,\n"
    u"   where the #end-ov>* reset (position:relative;z-index:1) would win the\n"
    u"   cascade tie on specificity-equal #cardFocusTip - the id-qualified rule\n"
    u"   puts absolute back. cqw still resolves against #screen-match, the\n"
    u"   nearest size container, same as at the table. */\n"
    u"#end-ov>#cardFocusTip{position:absolute;z-index:9001}\n"
    u"/* the CLAIM plaque: P671b's gold, ink darker than trim; the tip itself\n"
    u"   is pointer-events:none, so the button re-arms its own */\n"
    u"#cardFocusTip .cft-btn{display:inline-block;pointer-events:auto;\n"
    u"  cursor:pointer;margin-top:2.2cqw;padding:1.6cqw 7cqw;\n"
    u"  font-family:'JMH Beda',serif;font-size:3.6cqw;letter-spacing:.1em;\n"
    u"  color:#241505;background:#c9a24a;border:2px solid #7a5a1c;\n"
    u"  border-radius:1.6cqw;box-shadow:0 2px 6px rgba(0,0,0,.5)}\n"
    u"#cardFocusTip .cft-btn:active{transform:translateY(1px)}",
    'P697 tip CSS in #end-ov + CLAIM plaque')

# ── P698.1: floor and ceiling ──
sub(u"#end-ov.win-art-on .res-card{top:47%!important;width:80%!important}",
    u"/* P698: a FLOOR as well as a ceiling. Top pins under the plaque - 49.5\n"
    u"   clears it on tall phones, where the safe-area pushed the painted\n"
    u"   panel lower and PICK A CARD sat ON the parchment; bottom stops above\n"
    u"   the SKIP pill wherever the device anchors it. The wrap flexes across\n"
    u"   the span and the deck's margin-top:auto (below) pins the slots to\n"
    u"   the floor, so the dead band above SKIP is spent, not left over. */\n"
    u"#end-ov.win-art-on .res-card{top:49.5%!important;\n"
    u"  bottom:calc(28px + env(safe-area-inset-bottom,0px) + 8.5vh);\n"
    u"  width:80%!important}\n"
    u"#end-ov.win-art-on .fo-wrap{display:flex;flex-direction:column;\n"
    u"  align-self:stretch;flex:1 1 auto;min-height:0}",
    'P698 res-card floor+ceiling, fo-wrap flexes')

# ── P698.2: the counterweight retires ──
sub(u"/* P643: vh, NOT %. A percentage padding resolves against the containing\n"
    u"   block's WIDTH - .res-card is 80% of 430px, so 5% bought 17px against a\n"
    u"   44.5px move and the slots came up with the cards anyway. #end-ov is fixed\n"
    u"   inset:0, so 1vh is one per cent of the overlay's height: the same unit the\n"
    u"   52%->47% move was made in, and therefore an exact cancellation. */\n"
    u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5vh)}",
    u"/* P643 held the slots still with vh padding while P641 lifted the cards;\n"
    u"   P698 retires the counterweight - the wrap flexes between plaque and\n"
    u"   SKIP now, and margin-top:auto is what pins the slots to the bottom of\n"
    u"   that span on any screen. */\n"
    u"#end-ov.win-art-on .fo-deck{padding-top:6px;margin-top:auto}",
    'P698 deck pins to the floor')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
