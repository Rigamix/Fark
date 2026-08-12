# -*- coding: utf-8 -*-
"""P659: the win screen - cards grey instead of vanishing, slots clear the button,
the upgrade tag moves under the name, and the offer arrives when the score does.

── TAKING A CARD NO LONGER EMPTIES THE SCREEN ──
Denis: "even I take a card don't make the other ones disappear. Just grey them
out and don't change the layout."

Both finishes replaced .res-card's innerHTML - one with a "TAKEN: NAME" line,
one with the deck alone - so the offer row vanished and everything below jumped.
There is now one _foFinish that keeps every element where it is: the wrap gets
.taken, the unpicked cards grey, the picked one stays lit, and only the deck row
is re-rendered in place. Nothing moves.

── THE SLOTS OVERLAPPED THE BUTTON ON A PHONE ──
Measured before touching it: slots bottom against button top, at three heights.
    891px   +12px   clear   <- the design shell, which is why it looked fine here
    760px   -51px   OVERLAP
    700px   -80px   OVERLAP
The offer stack is simply taller than a short phone leaves room for, so trimming
the deck's padding alone cannot fix it - at 760 the padding is only 38px of the
51px needed. The whole block lifts on short screens instead, in a media query
rather than by moving the shipped numbers, so the design shell is untouched.

── THE UPGRADE TAG ──
"remove the Upgrade tag when I'm offered a level 2 card. Write upgrade in
parenthesis under the card name." The badge is gone and famCardHtml takes a
`sub` line under the name, which is where the tier numeral used to be printed
before P646 removed it as a duplicate - so this is that slot being used for
something that is not already on the card.

── THE OFFER ARRIVES WITH THE SCORE ──
"the bottom UI still takes way too long to appear". P635 cut this from 3200 to
2400 by measuring where the coin ceremony ENDS, which was the wrong question -
Denis is not waiting for the ceremony to finish, he is waiting to be able to
act. The title, the scores and the lift are all down by 1300ms; the coins and
the count-up carry on behind the offer perfectly well. 1300 for a win.
The loss keeps a longer beat at 1800 - its heart drain is the whole content of
that screen rather than a flourish over it.
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


# ── 1. one finish that keeps the layout ──────────────────────────────────
sub(u"function _famDraftDone(o){\n"
    u"  var rc=document.querySelector('#end-ov .res-card')||document.getElementById('resCard');\n"
    u"  var d=famDef(o.id);\n"
    u"  if(rc)rc.innerHTML='<div style=\"font-family:monospace;color:#8e8;padding:30px 10px;text-align:center\">TAKEN: '\n"
    u"    +d.name.toUpperCase()+(d.fam==='tavern'?'':' '+['I','II','III'][o.tier-1])+'</div>';\n"
    u"  _famEndReady();\n"
    u"}",
    u"/* P659: THE OFFER STAYS PUT. Denis: \"even I take a card don't make the other\n"
    u"   ones disappear. Just grey them out and don't change the layout.\"\n"
    u"   Both finishes used to replace .res-card's innerHTML - one with a TAKEN line,\n"
    u"   one with the deck alone - so the row vanished and everything under it\n"
    u"   jumped. This keeps every element where it is and only re-renders the deck,\n"
    u"   which is the one thing that genuinely changed.\n"
    u"   `pick` is the index of the offer that was taken, or -1 for a decline. */\n"
    u"function _foFinish(pick,pin){\n"
    u"  var wrap=document.querySelector('#end-ov .fo-wrap');\n"
    u"  if(wrap){\n"
    u"    wrap.classList.add('taken');\n"
    u"    var cards=wrap.querySelectorAll('.fo-card');\n"
    u"    for(var i=0;i<cards.length;i++)cards[i].classList.toggle('picked',i===pick);\n"
    u"    var deck=wrap.querySelector('.fo-deck');\n"
    u"    if(deck)deck.outerHTML=_foDeckHtml(pin);\n"
    u"  }\n"
    u"  _famEndReady();\n"
    u"}\n"
    u"function _famDraftDone(o){\n"
    u"  var pick=-1;\n"
    u"  try{for(var i=0;i<(_famOffer||[]).length;i++)if(_famOffer[i]===o)pick=i;}catch(e){}\n"
    u"  _foFinish(pick,null);\n"
    u"}",
    'P659 one finish, layout kept')

sub(u"function _foDraftDoneAt(o,pos,idx){\n"
    u"  var rc=document.querySelector('#end-ov .res-card')||document.getElementById('resCard');\n"
    u"  if(rc)rc.innerHTML='<div class=\"fo-wrap\"><div class=\"fo-title\">TAKEN</div>'\n"
    u"    +_foDeckHtml({pos:pos,idx:idx})+'</div>';\n"
    u"  _famEndReady();\n"
    u"}",
    u"function _foDraftDoneAt(o,pos,idx){\n"
    u"  var pick=-1;\n"
    u"  try{for(var i=0;i<(_famOffer||[]).length;i++)if(_famOffer[i]===o)pick=i;}catch(e){}\n"
    u"  _foFinish(pick,{pos:pos,idx:idx});\n"
    u"}",
    'P659 the drag finish shares it')

sub(u".fo-card{position:relative;transition:transform .18s ease;touch-action:none}",
    u".fo-card{position:relative;transition:transform .18s ease,filter .3s ease,opacity .3s ease;touch-action:none}\n"
    u"/* P659: taken. The unpicked cards grey where they stand rather than being\n"
    u"   removed, so nothing below them moves; the picked one stays lit. Both stop\n"
    u"   taking taps, because the choice is made. */\n"
    u".fo-wrap.taken .fo-card{pointer-events:none}\n"
    u".fo-wrap.taken .fo-card:not(.picked){filter:grayscale(1) brightness(.45);opacity:.6}",
    'P659 the greying')

# ── 2. the upgrade tag moves under the name ──────────────────────────────
sub(u"      +famCardHtml(o.id,o.tier,{onclick:\"famCardSheet('\"+o.id+\"',\"+o.tier\n"
    u"        +\",{btn:'CLAIM',badge:\"+(o.upgrade?\"'UPGRADE'\":\"null\")+\",cb:'function(){\"+pickFn+\"(\"+i+\");}'})\",\n"
    u"        badge:(o.upgrade?'UPGRADE':null)})",
    u"      /* P659: no corner badge. \"Write upgrade in parenthesis under the card\n"
    u"         name\" - so it goes in famCardHtml's sub line, the slot the tier\n"
    u"         numeral used to duplicate before P646 took it out. */\n"
    u"      +famCardHtml(o.id,o.tier,{onclick:\"famCardSheet('\"+o.id+\"',\"+o.tier\n"
    u"        +\",{btn:'CLAIM',badge:\"+(o.upgrade?\"'UPGRADE'\":\"null\")+\",cb:'function(){\"+pickFn+\"(\"+i+\");}'})\",\n"
    u"        sub:(o.upgrade?'(upgrade)':null)})",
    'P659 the upgrade line')

sub(u"  var cap='<div style=\"margin-top:4px;text-align:center;font-family:\\'JMH Beda\\',serif;letter-spacing:.05em\">'\n"
    u"    +'<div style=\"font-size:12px;color:#f0e3c6\">'+d.name.toUpperCase()+'</div>'\n"
    u"    +'</div>';",
    u"  var cap='<div style=\"margin-top:4px;text-align:center;font-family:\\'JMH Beda\\',serif;letter-spacing:.05em\">'\n"
    u"    +'<div style=\"font-size:12px;color:#f0e3c6\">'+d.name.toUpperCase()+'</div>'\n"
    u"    /* P659: the sub line - \"(upgrade)\" today. Under the name, not a corner\n"
    u"       badge over the art. */\n"
    u"    +(opts.sub?'<div style=\"font-size:10px;color:'+col+';margin-top:1px\">'+opts.sub+'</div>':'')\n"
    u"    +'</div>';",
    'P659 render the sub line')

# ── 3. the offer arrives with the score ──────────────────────────────────
sub(u"  var _DRAFT_DELAY={bossWin:2400,patronWin:2400,loss:2800};",
    u"  /* P659: 2400 -> 1300 on a win. P635 measured where the coin ceremony ENDS,\n"
    u"     which was the wrong question - Denis is not waiting for the flourish to\n"
    u"     finish, he is waiting to be able to ACT. The title, the scores and the\n"
    u"     lift are all down by 1300ms and the coins carry on behind the offer\n"
    u"     perfectly well. The loss keeps a longer beat: its heart drain is the\n"
    u"     content of that screen rather than a flourish over it. */\n"
    u"  var _DRAFT_DELAY={bossWin:1300,patronWin:1300,loss:1800};",
    'P659 the offer arrives sooner')

# ── 4. short screens lift the whole block ────────────────────────────────
sub(u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5vh)}",
    u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5vh)}\n"
    u"/* P659: SHORT PHONES LIFT THE WHOLE BLOCK. Measured slots-bottom against\n"
    u"   button-top: +12px at 891 (the design shell, which is why this looked fine\n"
    u"   here), -51px at 760, -80px at 700. The stack is taller than a short screen\n"
    u"   leaves room for, so trimming the deck's padding cannot reach it - at 760\n"
    u"   that padding is 38px of the 51 needed. In a media query so the design\n"
    u"   shell's tuned numbers are untouched. */\n"
    u"@media (max-height:820px){\n"
    u"  #end-ov.win-art-on .res-card{top:41%!important}\n"
    u"  #end-ov.win-art-on .fo-deck{padding-top:2px}\n"
    u"  #end-ov.win-art-on .fo-offer{gap:6px}\n"
    u"}\n"
    u"@media (max-height:730px){\n"
    u"  #end-ov.win-art-on .res-card{top:37%!important}\n"
    u"  #end-ov.win-art-on .fo-title{margin-bottom:2px}\n"
    u"}",
    'P659 short screens lift the block')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
