# -*- coding: utf-8 -*-
"""P672: the rival's arch mirrors the player's, and the match-screen card focus
becomes grow-plus-text instead of a sheet.

Denis: "npc cards should have the same spread as mine, meaning an arch (just
flipped) and not chaos like what you show me." And: "tapping on a card should
make it grow a bit bigger (smoothly) and above it have a nice text appearing
animation with the title and description of that card. Touch it again and it
disappears. Since you now can drag and drop to activate it should be the only
way to do so, rather than having a play button."

── THE ARCH ──
The player's fan is a real arch: outer cards rotate outward AND droop 0.55cqw,
so the hand bulges upward, with a separate two-card case (±4.5, 0.3). The
rival's row had rotations only, in the order -7/+7/0 - the middle card tilted
right and the third sat straight, which is the "chaos" in Denis's screenshot -
and no translates at all. It now carries the player's arch mirrored (rotation
signs flipped, droop upward) with count-aware cases for two to five cards,
five being a late boss night's 3 family + 2 npc.

── THE FOCUS ──
famCardTap opened the bottom sheet with a PLAY button; famOppTap/npcOppTap the
same sheet without one. On the match screen all three now toggle _cardFocus:
the card grows on the standalone `scale` property (which composes with the fan's
`rotate`/`translate` instead of replacing them - the same reason P580 put the
fan on `rotate`), and the title and rules text appear word by word beside it -
above the player's card, below the rival's, since their row hangs from the top.
Second tap, tapping another card, starting a drag, or the row rebuilding all
dismiss it - the drag hook matters because drag is now the ONLY way to play a
card, so the focus must never eat the gesture.

The text reuses the game's own voice: JMH Beda over the wood with the
status-line's shadow, _accG for the number/keyword accents, _noOrphan for the
line breaks, and the family colour on the title - printed as ink two steps
darker than the accent, per the standing rule.

famCardSheet itself is untouched: the win-screen draft, the deck row and the
patron peek still open the parchment sheet. Only the match screen changes, and
the PLAY path dies with it - famUse through the drag threshold is the one way
to play a card now.
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


# ── 1. the arch ─────────────────────────────────────────────────────────
sub(u"#screen-match #famRowO .fcv:nth-child(1){rotate:-7deg}\n"
    u"#screen-match #famRowO .fcv:nth-child(2){rotate:7deg}\n"
    u"#screen-match #famRowO .fcv:nth-child(3){rotate:0deg}\n"
    u"/* P670: the row can hold five now (up to 3 family + 2 npc on a late boss\n"
    u"   night) - the fan pattern covered three and children past it sat dead\n"
    u"   straight. */\n"
    u"#screen-match #famRowO .fcv:nth-child(4){rotate:-4deg}\n"
    u"#screen-match #famRowO .fcv:nth-child(5){rotate:4deg}\n"
    u"/* P586: same for the rival - a lone card sits straight. */\n"
    u"#screen-match #famRowO .fcv:only-child{rotate:0deg}",
    u"/* P672: THE PLAYER'S ARCH, MIRRORED. The old angles were -7/+7/0 - the\n"
    u"   middle card tilted right and the third sat straight, which is the \"chaos\"\n"
    u"   Denis photographed - and the row had no translates at all, so it was\n"
    u"   never an arch. These are the player row's own numbers with the rotation\n"
    u"   signs flipped and the droop turned upward: their hand hangs from the top,\n"
    u"   so the bulge points at the table the way the player's points at them.\n"
    u"   Count-aware like the player's two-card case, up to the five a late boss\n"
    u"   night can hold (3 family + 2 npc). */\n"
    u"/* three (the default pattern, same shape as #famRowP's 1/2/3) */\n"
    u"#screen-match #famRowO .fcv:nth-child(1){rotate:6.5deg;translate:0 -0.55cqw}\n"
    u"#screen-match #famRowO .fcv:nth-child(2){rotate:0deg;translate:none}\n"
    u"#screen-match #famRowO .fcv:nth-child(3){rotate:-6.5deg;translate:0 -0.55cqw}\n"
    u"/* two */\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(2){rotate:4.5deg;translate:0 -0.3cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(2) ~ .fcv{rotate:-4.5deg;translate:0 -0.3cqw}\n"
    u"/* four */\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(4){rotate:7deg;translate:0 -0.6cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(4) ~ .fcv:nth-child(2){rotate:2.5deg;translate:0 -0.15cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(4) ~ .fcv:nth-child(3){rotate:-2.5deg;translate:0 -0.15cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(4) ~ .fcv:nth-child(4){rotate:-7deg;translate:0 -0.6cqw}\n"
    u"/* five */\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(5){rotate:8deg;translate:0 -0.8cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(5) ~ .fcv:nth-child(2){rotate:4deg;translate:0 -0.3cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(5) ~ .fcv:nth-child(3){rotate:0deg;translate:none}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(5) ~ .fcv:nth-child(4){rotate:-4deg;translate:0 -0.3cqw}\n"
    u"#screen-match #famRowO .fcv:first-child:nth-last-child(5) ~ .fcv:nth-child(5){rotate:-8deg;translate:0 -0.8cqw}\n"
    u"/* P586: same for the rival - a lone card sits straight. */\n"
    u"#screen-match #famRowO .fcv:only-child{rotate:0deg;translate:none}",
    'P672 the mirrored arch')

# ── 2. the focus machinery ──────────────────────────────────────────────
sub(u"function famCardTap(i){\n"
    u"  if(!G||!G.pF||!G.pF[i])return;\n"
    u"  var inst=G.pF[i],d=famDef(inst.id);if(!d)return;\n"
    u"  /* Confession's card-seal is retired - Still Waters hushes a die's family\n"
    u"     and never touches cards - and G._fSealIdx was never assigned by anything,\n"
    u"     so the seal branch here was unreachable as well as wrong. */\n"
    u"  var usable=d.kind==='active'&&inst.charges>0&&CFX[inst.id]&&CFX[inst.id].use;\n"
    u"  var sub=(d.kind==='active'?(inst.charges>0?'uses left: '+inst.charges:'spent for this match'):'');\n"
    u"  famCardSheet(inst.id,inst.tier,{sub:sub,\n"
    u"    btn:usable?'PLAY':null,cb:usable?('function(){famUse('+i+');}'):null});\n"
    u"}",
    u"/* ═══════ P672: THE MATCH-SCREEN CARD FOCUS ═══════\n"
    u"   Tap a card at the table: it grows a little and its title and rules text\n"
    u"   appear word by word beside it - above the player's card, below the\n"
    u"   rival's, since their row hangs from the top. Tap it again (or tap\n"
    u"   another card, start a drag, or let the row rebuild) and it goes. The\n"
    u"   bottom sheet is a win-screen and peek surface now; at the table there is\n"
    u"   no PLAY button anywhere - dragging past the threshold is the one way to\n"
    u"   play a card, so the focus must never eat that gesture, which is why the\n"
    u"   drag's own live-flip closes it.\n"
    u"   The grow rides the standalone `scale` property for the same reason P580\n"
    u"   put the fan on `rotate`: standalone properties compose, so the fan angle\n"
    u"   and the arch droop hold while the card scales. */\n"
    u"var _cardFocusEl=null;\n"
    u"function _cardFocusClose(){\n"
    u"  var t=document.getElementById('cardFocusTip');if(t)t.remove();\n"
    u"  if(_cardFocusEl){try{_cardFocusEl.classList.remove('focus');}catch(e){}}\n"
    u"  _cardFocusEl=null;\n"
    u"}\n"
    u"/* words wrapped for the stagger; delay written inline so the CSS stays one\n"
    u"   keyframe. _noOrphan first, so the widow rule holds here too. */\n"
    u"function _cftWords(txt,t0){\n"
    u"  var i=0;\n"
    u"  return String(txt).split(' ').map(function(w){\n"
    u"    return '<span class=\"w\" style=\"animation-delay:'+(t0+(i++)*38)+'ms\">'+w+'</span>';\n"
    u"  }).join(' ');\n"
    u"}\n"
    u"function _cardFocusToggle(el,o){\n"
    u"  if(!el)return;\n"
    u"  if(_cardFocusEl===el){_cardFocusClose();return;}\n"
    u"  _cardFocusClose();\n"
    u"  _cardFocusEl=el;el.classList.add('focus');\n"
    u"  var ms=document.getElementById('screen-match')||document.body;\n"
    u"  var tip=document.createElement('div');tip.id='cardFocusTip';\n"
    u"  /* the accent travels as a variable, NOT as inline color - an inline color\n"
    u"     outranks every stylesheet rule, so the darkening step below it could\n"
    u"     never have applied */\n"
    u"  tip.innerHTML='<div class=\"cft-name\" style=\"--cft-a:'+(o.col||'#f0c860')+'\">'+_cftWords(o.title,0)+'</div>'\n"
    u"    +(o.sub?'<div class=\"cft-sub\">'+_cftWords(o.sub,140)+'</div>':'')\n"
    u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>';\n"
    u"  ms.appendChild(tip);\n"
    u"  /* placed off the CARD's box, clamped to the screen; the tip is\n"
    u"     position:absolute in #screen-match, so rects convert through its box */\n"
    u"  var cr=el.getBoundingClientRect(),sr=ms.getBoundingClientRect();\n"
    u"  var cx=cr.left+cr.width/2-sr.left;\n"
    u"  tip.style.left=Math.max(sr.width*0.04,Math.min(sr.width*0.96-tip.offsetWidth,cx-tip.offsetWidth/2))+'px';\n"
    u"  if(o.below){tip.style.top=(cr.bottom-sr.top+sr.width*0.045)+'px';}\n"
    u"  else{tip.style.top=(cr.top-sr.top-tip.offsetHeight-sr.width*0.045)+'px';}\n"
    u"}\n"
    u"function famCardTap(i){\n"
    u"  if(!G||!G.pF||!G.pF[i])return;\n"
    u"  var inst=G.pF[i],d=famDef(inst.id);if(!d)return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  var sub=(d.kind==='active'?(inst.charges>0?'uses left: '+inst.charges+' — drag past the line to play'\n"
    u"                                            :'spent for this match'):'passive — always on');\n"
    u"  _cardFocusToggle(document.querySelectorAll('#famRowP .fcv')[i],{\n"
    u"    title:d.name.toUpperCase()+(inst.tier>1?' '+['','II','III'][inst.tier-1]:''),\n"
    u"    sub:sub,body:d.text[inst.tier-1],col:col});\n"
    u"}",
    'P672 famCardTap becomes the focus')

sub(u"  var spent=_npcCardSpent(cid);\n"
    u"  var h='<div style=\"text-align:center;padding:6px 4px 14px\">'\n"
    u"    +famCardArt(cid,1,{style:'width:38%;max-width:170px;margin:0 auto;display:inline-block'})\n"
    u"    +'<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:19px;color:#2a1808;margin-top:8px\">'+c.name+'</div>'\n"
    u"    +'<div style=\"font-size:12px;color:#6a5238;margin-top:2px\">'+(spent?'SPENT — used up for this match':'their card — read the table')+'</div>'\n"
    u"    +'<div style=\"font-size:14px;line-height:1.5;color:#3a2812;margin:10px auto 4px;max-width:88%\">'+_accG(c.desc||_sentenceCase(c.eff||''))+'</div>'\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h,'fam-sheet');/* P671: same parchment as famCardSheet */\n"
    u"}",
    u"  var spent=_npcCardSpent(cid);\n"
    u"  /* P672: grow-and-read, like every other card at the table */\n"
    u"  _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"    title:c.name,\n"
    u"    sub:spent?'spent — used up for this match':'their card',\n"
    u"    body:(c.desc||_sentenceCase(c.eff||'')),below:true});\n"
    u"}",
    'P672 npcOppTap joins the focus')

sub(u"function famOppTap(i){\n"
    u"  if(!G||!G.oF||!G.oF[i])return;\n"
    u"  var inst=G.oF[i],d=famDef(inst.id);if(!d)return;\n"
    u"  var _tg=(inst.id==='tar_pit'&&G._oTarPit)||(inst.id==='sleight'&&G._oSleight)||(inst.id==='ill_omen'&&G._oIllOmen);\n"
    u"  famCardSheet(inst.id,inst.tier,{sub:inst.broken?'BROKEN — Tampered for the night'\n"
    u"    :(_tg?'ARMED — it fires after your next roll':'their card — read the table')});\n"
    u"}",
    u"function famOppTap(i){\n"
    u"  if(!G||!G.oF||!G.oF[i])return;\n"
    u"  var inst=G.oF[i],d=famDef(inst.id);if(!d)return;\n"
    u"  var _tg=(inst.id==='tar_pit'&&G._oTarPit)||(inst.id==='sleight'&&G._oSleight)||(inst.id==='ill_omen'&&G._oIllOmen);\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  /* P672: grow-and-read replaces the sheet at the table */\n"
    u"  _cardFocusToggle(document.querySelectorAll('#famRowO .fcv')[i],{\n"
    u"    title:d.name.toUpperCase()+(inst.tier>1?' '+['','II','III'][inst.tier-1]:''),\n"
    u"    sub:inst.broken?'BROKEN — tampered for the night'\n"
    u"       :(_tg?'ARMED — it fires after your next roll':'their card'),\n"
    u"    body:d.text[inst.tier-1],col:col,below:true});\n"
    u"}",
    'P672 famOppTap joins the focus')

# ── 3. the dismissals ───────────────────────────────────────────────────
sub(u"    if(!_famDrag.live){_famDrag.live=true;el.classList.add('fcv-drag');}",
    u"    if(!_famDrag.live){_famDrag.live=true;el.classList.add('fcv-drag');\n"
    u"      /* P672: a drag is the one way to play a card - the focus must never\n"
    u"         sit on top of the gesture */\n"
    u"      try{_cardFocusClose();}catch(e){}}",
    'P672 drag dismisses the focus')

sub(u"  var hostO=document.getElementById('famRowO');",
    u"  /* P672: the rebuild replaces every element the focus could be holding */\n"
    u"  try{_cardFocusClose();}catch(e){}\n"
    u"  var hostO=document.getElementById('famRowO');",
    'P672 rebuild dismisses the focus')

# ── 4. the CSS ──────────────────────────────────────────────────────────
sub(u"/* the fire flash, on the family card too - one selector rather than a second\n"
    u"   set of keyframes */\n"
    u".fcv.card-fired{animation:cardFired .42s ease-out}",
    u"/* the fire flash, on the family card too - one selector rather than a second\n"
    u"   set of keyframes */\n"
    u".fcv.card-fired{animation:cardFired .42s ease-out}\n"
    u"/* ── P672: THE CARD FOCUS ──\n"
    u"   The grow is standalone `scale`, so the fan's rotate and the arch's\n"
    u"   translate hold underneath it; its transition lives here because the\n"
    u"   rows' base transition lists only transform and filter. */\n"
    u"#screen-match .fcv{transition:transform .18s ease,filter .18s ease,\n"
    u"  scale .24s cubic-bezier(.3,1.45,.4,1)}\n"
    u"#screen-match .fcv.focus{scale:1.3;z-index:9000}\n"
    u"#screen-match #famRowO .fcv.focus{scale:1.24}\n"
    u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;\n"
    u"  max-width:74cqw;text-align:center}\n"
    u"#cardFocusTip .cft-name{font-family:'JMH Beda',serif;font-size:5cqw;\n"
    u"  letter-spacing:.04em;\n"
    u"  /* the title prints two steps darker than the family accent it is handed -\n"
    u"     never AT the accent (the standing rule) */\n"
    u"  color:color-mix(in srgb,var(--cft-a,#f0c860) 80%,#140c04)}\n"
    u"#cardFocusTip .cft-sub{font-family:'JMH Beda',serif;font-size:2.9cqw;\n"
    u"  color:#c9b490;opacity:.9;margin-top:0.4cqw}\n"
    u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.7cqw;\n"
    u"  color:#efe2c4;line-height:1.35;margin-top:1.2cqw}\n"
    u"#cardFocusTip .cft-name,#cardFocusTip .cft-sub,#cardFocusTip .cft-body{\n"
    u"  text-shadow:0 1px 0 rgba(20,12,4,.85),0 0 6px rgba(20,12,4,.7)}\n"
    u"/* the words arrive one after another - delay is written inline per word */\n"
    u"#cardFocusTip span.w{display:inline-block;opacity:0;\n"
    u"  animation:cftWord .32s ease-out forwards}\n"
    u"@keyframes cftWord{\n"
    u"  0%{opacity:0;translate:0 0.9cqw;filter:blur(2px)}\n"
    u"  100%{opacity:1;translate:0 0;filter:none}}",
    'P672 the focus CSS')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
