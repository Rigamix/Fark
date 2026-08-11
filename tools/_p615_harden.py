# -*- coding: utf-8 -*-
"""P615: five defects the adversarial pass found in the threshold work.

Every one of them was invisible to my own verification, and the reasons are worth
keeping:

 1. REACHABILITY. I proved the gesture works by setting G.pCards myself and
    calling buildCBar by hand. In a real match G.pCards is ALWAYS empty, so
    initCardDrag is never called and there is nothing to drag. I tested the
    mechanism and never tested that a player can reach it.
 2. THE GLOW NEVER PAINTS. `.mcard.dragging` declares filter with !important and
    `.armed` is only ever set while `.dragging` is on, so the halo lost the
    cascade on every frame. Behaviour was right, paint was absent - and a
    behavioural test cannot see that.
 3. THE KNOB IS UNIT-BLIND AND FAILS OPEN. parseFloat throws the unit away, and
    calc()/clamp() give NaN -> 0 -> the line lands on the row top, where the
    fan's own lift already puts middle cards above it: armed at rest. My comment
    invites hand-tuning, which makes the trap likely rather than theoretical.
 4. A SECOND POINTER STEALS THE DRAG. _dragState is one global; a stray finger
    or a right-click orphans the airborne card in .dragging with no exit path
    that will ever run - a fourth way to end a drag, and the only one that ends
    nowhere. I asserted "one exit path" and did not test two pointers.
 5. THE PYRE'S GHOST. The burn deletes the card from G.pCards and its usedCards
    key, but never removes the .mcard. Every derived pass iterates the
    collections the burn emptied, so it is never greyed - and _cardHasUse falls
    through to its `.used` fallback and calls a destroyed card usable.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ═══ 1. REACHABILITY ══════════════════════════════════════════════════════
sub(u"  const pCards=[];/* P1 cutover: old cards retired */",
    u"  /* P615: THE PLAYER'S HAND, AT LAST. This returned [] unconditionally since\n"
    u"     the P1 cutover, so G.pCards was ALWAYS empty: #playerCards rendered no\n"
    u"     cards, initCardDrag was never called, and the entire drag-to-activate\n"
    u"     system - including the P612 threshold - was unreachable in real play.\n"
    u"     Measured 0 initCardDrag calls across match start, a roll and a resume,\n"
    u"     against a control that saw 1 on a forced build.\n"
    u"     params.pCards is what launchSeat and launchBossMatch already send and\n"
    u"     what saveMatchState/resumeMatch already round-trip, so nothing new has\n"
    u"     to be plumbed - the hand died on this one line. */\n"
    u"  const pCards=(params.pCards||[]).filter(Boolean);",
    'P615-1 pCards reaches the match')

# ═══ 2. THE ARMED GLOW ════════════════════════════════════════════════════
sub(u".mcard.armed .gcard{outline:0.22cqw solid rgba(255,226,150,.92);outline-offset:-0.22cqw}",
    u".mcard.armed .gcard{outline:0.22cqw solid rgba(255,226,150,.92);outline-offset:-0.22cqw}\n"
    u"/* P615: THE HALO HAD TO WIN THE CASCADE, and it did not. `.mcard.dragging`\n"
    u"   declares its lift shadow with !important, and `.armed` is only ever set on\n"
    u"   a card that is ALREADY dragging - onDragMove adds 'dragging' before it\n"
    u"   toggles 'armed' - so the two-stop gold halo lost on every frame of every\n"
    u"   drag and the threshold had NO visible sign at all. Behaviour was correct\n"
    u"   throughout, which is exactly why a behavioural test could not see it.\n"
    u"   Folding the drag's own shadow into this declaration lets one !important\n"
    u"   carry both, so nothing about the drag's look changes except the halo\n"
    u"   appearing. */\n"
    u".mcard.dragging.armed{\n"
    u"  filter:drop-shadow(0 8px 24px rgba(0,0,0,.7))\n"
    u"         drop-shadow(0 0 0.9cqw rgba(255,214,120,.95))\n"
    u"         drop-shadow(0 0 2.6cqw rgba(255,180,60,.55))\n"
    u"         brightness(1.16) saturate(1.12)!important}",
    'P615-2 armed glow wins the cascade')

# ═══ 3. THE KNOB, RESOLVED BY THE CSS ENGINE ══════════════════════════════
sub(u"  var lift=parseFloat(getComputedStyle(document.documentElement)\n"
    u"    .getPropertyValue('--card-arm-lift'))||0;\n"
    u"  /* the var is in cqw against the screen's width, same as the row's own\n"
    u"     sizing, so resolve it the same way rather than trusting a px read */\n"
    u"  var sc=document.getElementById('screen-match');\n"
    u"  var w=sc?sc.getBoundingClientRect().width:innerWidth;\n"
    u"  return r.top-(w*lift/100);",
    u"  /* P615: THE CSS ENGINE RESOLVES THE KNOB, not parseFloat.\n"
    u"     The old line read the NUMBER and threw the UNIT away, then treated what\n"
    u"     was left as a percentage of the shell width: '16px' became 62.4px, and\n"
    u"     any calc()/clamp()/min() parsed to NaN -> ||0 -> the threshold landed on\n"
    u"     the row top, where the fan's own --lift already puts middle cards'\n"
    u"     centres ABOVE the line. Armed at rest, first 10px of any drag fires.\n"
    u"     That mattered because the comment on --card-arm-lift invites hand-tuning\n"
    u"     and clamp(40px,16cqw,90px) is the obvious response to a small screen.\n"
    u"     A zero-width hidden strut inside the row carries the value as a HEIGHT,\n"
    u"     so every unit works and cqw resolves against the same container the\n"
    u"     row's own sizing does. */\n"
    u"  var strut=document.getElementById('armLiftStrut');\n"
    u"  if(!strut||!strut.isConnected)return r.top;/* fail CLOSED: no strut, no lift,\n"
    u"     so the line sits on the row and a card must still be lifted clear of it -\n"
    u"     never the other way round, which is what ||0 used to do */\n"
    u"  var lift=strut.getBoundingClientRect().height;\n"
    u"  if(!(lift>0))return r.top;\n"
    u"  return r.top-lift;",
    'P615-3 threshold resolved + fails closed')

sub(u"<div class=\"card-bar bot\" id=\"playerCards\">",
    u"<div class=\"card-bar bot\" id=\"playerCards\">\n"
    u"  <!-- P615: the activation threshold's height, carried as a real CSS length\n"
    u"       so the engine resolves --card-arm-lift in whatever unit it is written.\n"
    u"       Zero width, hidden, pointer-events:none - it lays out and nothing else.\n"
    u"       buildCBar only sweeps .mcard/.cchip, so it survives every rebuild. -->\n"
    u"  <div id=\"armLiftStrut\"></div>",
    'P615-3 strut markup')

sub(u"/* ═══ P613: THE THRESHOLD'S ONLY VISIBLE SIGN ═══",
    u"/* P615: the strut whose HEIGHT is the threshold lift - see _cardThresholdY */\n"
    u"#armLiftStrut{position:absolute;left:0;top:0;width:0;height:var(--card-arm-lift);\n"
    u"  visibility:hidden;pointer-events:none}\n"
    u"/* ═══ P613: THE THRESHOLD'S ONLY VISIBLE SIGN ═══",
    'P615-3 strut CSS')

# ═══ 4. ONE DRAG AT A TIME ════════════════════════════════════════════════
sub(u"    if(!_cardHasUse(cardId))return;\n",
    u"    if(!_cardHasUse(cardId))return;\n"
    u"    /* P615: A SECOND POINTER MUST NOT STEAL AN AIRBORNE DRAG. _dragState is\n"
    u"       one global and this used to overwrite it unconditionally, so a stray\n"
    u"       second finger - or a right-button press, since e.button was never\n"
    u"       checked - left the first card orphaned in `.dragging` (position:fixed,\n"
    u"       z-index 9500) with onDragEnd early-returning on it forever. That is a\n"
    u"       FOURTH way for a drag to end and the only one that ends nowhere, which\n"
    u"       contradicts the one-exit-path invariant P612 claims for itself. Worse\n"
    u"       under the threshold: the stolen card takes its delta from the other\n"
    u"       pointer's origin, so it can be carried across the line and released\n"
    u"       armed - firing a card the player never touched. */\n"
    u"    if(e&&e.button!==undefined&&e.button!==0)return;\n"
    u"    if(_dragState&&_dragState.dragging&&_dragState.el!==mcardEl)return;\n",
    'P615-4 no drag stealing')

# ═══ 5. THE PYRE'S GHOST ══════════════════════════════════════════════════
sub(u"      triggerCard('the_pyre','BURNED '+cd.name+' +500',true);\n"
    u"      setStatusMsg('BURNED '+cd.name+' → +500 BANK','gold');\n"
    u"      picker.remove();\n"
    u"      _updatePlayerCardVisuals();",
    u"      picker.remove();\n"
    u"      /* P615: THE BURNED CARD MUST LEAVE THE ROW. The two lines above have\n"
    u"         just removed it from G.pCards AND deleted its usedCards key - and\n"
    u"         every derived visual pass iterates G.pCards, so nothing could see it\n"
    u"         to grey it, while _cardHasUse fell through to its `.used` fallback\n"
    u"         and reported a card the player paid 500 points to destroy as usable.\n"
    u"         It sat in the fan as the only un-greyed card, still dragging, still\n"
    u"         arming, doing nothing. Rebuild the row - the path refundActiveCardUse\n"
    u"         already uses - and do it BEFORE triggerCard, whose floating label is\n"
    u"         parented to the bar buildCBar sweeps. */\n"
    u"      try{if(typeof buildCBar==='function')buildCBar('playerCards',G.pCards,false,'YOU');}catch(e){}\n"
    u"      triggerCard('the_pyre','BURNED '+cd.name+' +500',true);\n"
    u"      setStatusMsg('BURNED '+cd.name+' → +500 BANK','gold');\n"
    u"      _updatePlayerCardVisuals();\n"
    u"      if(typeof _updateCardGlints==='function'){try{_updateCardGlints();}catch(e){}}",
    'P615-5 pyre ghost')

sub(u"function _cardHasUse(cardId){\n"
    u"  try{\n",
    u"function _cardHasUse(cardId){\n"
    u"  /* P615: A CARD THAT IS NOT IN THE HAND HAS NO USE. The Pyre expresses\n"
    u"     \"spent\" by DELETING the usedCards key rather than zeroing it, so the\n"
    u"     absence of a flag used to fall through to the `.used` fallback and mean\n"
    u"     \"usable\". Absence now means \"not mine\", which is what a burn actually\n"
    u"     is. Fails closed. */\n"
    u"  try{if(G&&G.pCards&&G.pCards.indexOf(cardId)<0)return false;}catch(e){}\n"
    u"  try{\n",
    'P615-5 _cardHasUse fails closed')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
