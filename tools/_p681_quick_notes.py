# -*- coding: utf-8 -*-
"""P681: the quick items from Denis's seventeen notes.

1. WIN SCREEN - "when I pick a card that card should disappear from the
   offering." The picked card is in the deck row now, so it leaves the offer;
   the unpicked stay greyed exactly as before (his earlier ruling).
2. START DICE - "make it that I can choose one even as they are animating in."
   The tap handler refused until _floatDone (set 1.6-2s after the deal). A tap
   mid-float now lands: it stops the float where it is and proceeds.
3. "PATRON HOLDS 50" - removed; the number sits right beneath it already.
4. "AMBER JOINS YOUR SIX" - the buy toast goes; the tray already shows the new
   die. (Denis: any message like this can be removed.)
5. CARD FOCUS - tap anywhere else dismisses it; while it is open the two
   status strips fade so the tip never overlaps score/rolling text; and the
   'their card' caption goes - he knows.
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


# ── 1. the picked card leaves the offer ─────────────────────────────────
sub(u".fo-wrap.taken .fo-card:not(.picked){filter:grayscale(1) brightness(.45);opacity:.6}",
    u".fo-wrap.taken .fo-card:not(.picked){filter:grayscale(1) brightness(.45);opacity:.6}\n"
    u"/* P681: the picked card is in the deck row now, so it LEAVES the offer -\n"
    u"   the unpicked stay greyed in place, per the earlier ruling */\n"
    u".fo-wrap.taken .fo-card.picked{opacity:0;scale:.55;\n"
    u"  transition:opacity .35s ease,scale .35s ease;pointer-events:none}",
    'P681 picked card leaves')

# ── 2. pick a die mid-float ─────────────────────────────────────────────
sub(u"  var die=ov.querySelectorAll('.nrdie')[i];if(!die||!die._floatDone)return;",
    u"  var die=ov.querySelectorAll('.nrdie')[i];if(!die)return;\n"
    u"  /* P681: a tap mid-float lands - stop the deal animation where it is and\n"
    u"     proceed, instead of refusing until the settle (Denis: \"I don't want to\n"
    u"     have to wait for their settle to select when I know what I want\"). */\n"
    u"  if(!die._floatDone){die.style.animation='none';die._floatDone=true;}",
    'P681 tap mid-float')

# ── 3. the HOLDS line goes ──────────────────────────────────────────────
sub(u"      oppBank+=total;setStatusMsg((G.rung?G.rung.name:'RIVAL')+' HOLDS '+oppBank.toLocaleString(),'active');",
    u"      oppBank+=total;/* P681: no 'HOLDS n' line - the number sits right\n"
    u"        beneath it already, and a display can vouch for a bug */",
    'P681 HOLDS goes')

# ── 4. the buy toast goes ───────────────────────────────────────────────
sub(u"  famLog(getDie(mat).name.toUpperCase()+' JOINS YOUR SIX \\u2014 '+getDie(out).name.toUpperCase()+' TRADED OUT');\n",
    u"  /* P681: no 'JOINS YOUR SIX' toast - the tray shows the new die (Denis:\n"
    u"     any message like this can be removed) */\n",
    'P681 buy toast goes')

# ── 5. focus: tap-away, strips fade, caption goes ───────────────────────
sub(u"var _cardFocusEl=null;\n"
    u"function _cardFocusClose(){\n"
    u"  var t=document.getElementById('cardFocusTip');if(t)t.remove();\n"
    u"  if(_cardFocusEl){try{_cardFocusEl.classList.remove('focus');}catch(e){}}\n"
    u"  _cardFocusEl=null;\n"
    u"}",
    u"var _cardFocusEl=null;\n"
    u"function _cardFocusClose(){\n"
    u"  var t=document.getElementById('cardFocusTip');if(t)t.remove();\n"
    u"  if(_cardFocusEl){try{_cardFocusEl.classList.remove('focus');}catch(e){}}\n"
    u"  _cardFocusEl=null;\n"
    u"  try{var ms=document.getElementById('screen-match');if(ms)ms.classList.remove('tip-open');}catch(e){}\n"
    u"}\n"
    u"/* P681: TAP ANYWHERE ELSE DISMISSES. One document-level listener, installed\n"
    u"   once; taps on a card route through the toggle (switch or close) and taps\n"
    u"   on the tip itself are inert, so only genuine elsewhere-taps close. */\n"
    u"(function(){\n"
    u"  function away(e){\n"
    u"    if(!_cardFocusEl)return;\n"
    u"    var t=e.target;\n"
    u"    if(t&&t.closest&&(t.closest('.fcv')||t.closest('#cardFocusTip')))return;\n"
    u"    _cardFocusClose();\n"
    u"  }\n"
    u"  document.addEventListener('pointerdown',away,true);\n"
    u"  document.addEventListener('touchstart',away,true);\n"
    u"})();",
    'P681 tap-away closes')

sub(u"  var ms=document.getElementById('screen-match')||document.body;\n"
    u"  var tip=document.createElement('div');tip.id='cardFocusTip';",
    u"  var ms=document.getElementById('screen-match')||document.body;\n"
    u"  /* P681: while a tip is open the status strips fade, so it never overlaps\n"
    u"     the score or the 'X IS ROLLING' line */\n"
    u"  try{ms.classList.add('tip-open');}catch(e){}\n"
    u"  var tip=document.createElement('div');tip.id='cardFocusTip';",
    'P681 strips fade while open')

sub(u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;",
    u"/* P681: the strips give way to an open tip */\n"
    u"#screen-match.tip-open .status-strip{opacity:0;transition:opacity .18s ease}\n"
    u"#screen-match .status-strip{transition:opacity .18s ease}\n"
    u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;",
    'P681 the strip CSS')

sub(u"    title:c.name,\n"
    u"    sub:spent?'spent — used up for this match':'their card',\n"
    u"    body:(c.desc||_sentenceCase(c.eff||'')),below:true});\n"
    u"}\n"
    u"function famOppTap(i){",
    u"    title:c.name,\n"
    u"    /* P681: no 'their card' caption - Denis knows whose it is */\n"
    u"    sub:spent?'spent — used up for this match':'',\n"
    u"    body:(c.desc||_sentenceCase(c.eff||'')),below:true});\n"
    u"}\n"
    u"function famOppTap(i){",
    'P681 npc caption goes')

sub(u"    sub:inst.broken?'BROKEN — tampered for the night'\n"
    u"       :(_tg?'ARMED — it fires after your next roll':'their card'),",
    u"    sub:inst.broken?'BROKEN — tampered for the night'\n"
    u"       :(_tg?'ARMED — it fires after your next roll':''),",
    'P681 fam caption goes')

sub(u"  if(_npcHandHidden()&&!_npcCardRevealed(cid)){\n"
    u"    _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"      title:'HIDDEN',sub:'their card',",
    u"  if(_npcHandHidden()&&!_npcCardRevealed(cid)){\n"
    u"    _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"      title:'HIDDEN',sub:'',",
    'P681 hidden caption goes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
