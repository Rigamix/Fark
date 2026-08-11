# -*- coding: utf-8 -*-
"""P611: a refunded card can be dragged again.

THE BUG, proven at runtime by the card-activation recon before any of this was
written: refundActiveCardUse restores usedCards[cardId] and strips `.used`, so
canActivateCard(cardId) returns TRUE - but the card is still parked in the
activation zone wearing `.in-zone`, and initCardDrag's onDragStart returns early
on that class. The card reads as usable and cannot be picked up. Measured: uses
1, canActivate true, className "mcard mcard-active in-zone", drag refused.

WHY NOT JUST REMOVE THE CLASS. placeCardInZone does `mcardEl.style.cssText=''`,
which destroys the fan-slot custom properties (--rot, --cx, --lift, --wobble-d)
and reparents the element into #activateZone. Stripping `.in-zone` alone would
leave a draggable card sitting in the zone with no resting slot to go home to.
The row has to be REBUILT from state - which is exactly what resume already does
at 34293-34295, and which the recon verified restores the card to its original
slot with its slot properties and a `.used` derived from the flag.

AND THE THREE BAIL-OUTS ROUTE THROUGH THE SAME FUNCTION NOW. frozen_die,
double_down and the_pyre each hand-rolled "give the use back": bump the counter,
querySelector the chip, remove `.used`. Three copies of one intent, none of them
aware of `.in-zone` either - the same shape as the two rank ladders and the four
position-inferred gates found earlier tonight. One function owns it.

SCOPE: this does not touch canActivateCard's gating, any card's effect, or when
effects resolve. It is the redesign brief's own out-of-scope line, respected -
the threshold redesign will delete `.in-zone` as a concept, and this is the
minimum that stops a live card getting stranded before then.
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


sub(u"function refundActiveCardUse(cardId){\n"
    u"  if(!G||!G.activeCardState||!G.activeCardState.usedCards)return;\n"
    u"  G.activeCardState.usedCards[cardId]=(G.activeCardState.usedCards[cardId]||0)+1;\n"
    u"  /* Remove .used from all card representations (chip in activation zone + base mcard) */\n"
    u"  document.querySelectorAll('[data-cid=\"'+cardId+'\"]').forEach(function(el){el.classList.remove('used');});\n"
    u"  /* Refresh card visuals so any chip that was greyed gets restored */\n"
    u"  if(typeof _updatePlayerCardVisuals==='function')_updatePlayerCardVisuals();\n"
    u"  _refreshCardUsesDisplay(cardId);\n"
    u"}",
    u"function refundActiveCardUse(cardId){\n"
    u"  if(!G||!G.activeCardState||!G.activeCardState.usedCards)return;\n"
    u"  G.activeCardState.usedCards[cardId]=(G.activeCardState.usedCards[cardId]||0)+1;\n"
    u"  /* P611: THE ROW IS REBUILT, not patched class by class.\n"
    u"     Stripping `.used` restored the LOGICAL state and left the POSITIONAL one\n"
    u"     stuck: a refunded card sat in the activation zone still wearing\n"
    u"     `.in-zone`, and initCardDrag's onDragStart returns early on that class -\n"
    u"     so canActivateCard said yes and the card could not be picked up. Removing\n"
    u"     the class alone is not the fix either: placeCardInZone has already done\n"
    u"     `style.cssText=''` and destroyed the fan-slot properties (--rot, --cx,\n"
    u"     --lift), so the card would be draggable with no resting slot to return\n"
    u"     to. Rebuilding from G.pCards is the path resume already uses, and it puts\n"
    u"     the card back in its own slot with `.used` derived from the flag. */\n"
    u"  try{\n"
    u"    if(typeof buildCBar==='function')buildCBar('playerCards',G.pCards,false,'YOU');\n"
    u"  }catch(e){}\n"
    u"  /* belt and braces for any representation outside the player's row */\n"
    u"  document.querySelectorAll('[data-cid=\"'+cardId+'\"]').forEach(function(el){\n"
    u"    el.classList.remove('used');el.classList.remove('in-zone');\n"
    u"  });\n"
    u"  if(typeof _updatePlayerCardVisuals==='function')_updatePlayerCardVisuals();\n"
    u"  if(typeof _updateCardGlints==='function'){try{_updateCardGlints();}catch(e){}}\n"
    u"  _refreshCardUsesDisplay(cardId);\n"
    u"}",
    'P611 refundActiveCardUse rebuilds')

for cid, label in ((u'frozen_die', 'frozen_die'),
                   (u'double_down', 'double_down'),
                   (u'the_pyre', 'the_pyre')):
    sub(u"    G.activeCardState.usedCards['%s']=(G.activeCardState.usedCards['%s']||0)+1;\n"
        u"    var _chip=document.querySelector('.mcard-active[data-cid=\"%s\"]');if(_chip)_chip.classList.remove('used');"
        % (cid, cid, cid),
        u"    /* P611: through the one function that owns a refund. This used to\n"
        u"       hand-roll it - bump the counter, find the chip, strip `.used` - which\n"
        u"       is three copies of an intent that all forgot `.in-zone` in the same\n"
        u"       way, and stranded the card exactly as the main refund path did. */\n"
        u"    refundActiveCardUse('%s');" % cid,
        'P611 bail-out ' + label)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
