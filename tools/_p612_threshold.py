# -*- coding: utf-8 -*-
"""P612: the card activation threshold replaces the activation zone.

Denis's brief. Drag a card up; past an invisible line it glows; RELEASE above it
and the card fires and comes back to its own slot, greyed. Release below and it
just goes home. No permanent zone, no space reserved before or after, and the
resting slot is the only position that ever matters.

SCOPE, as the brief states it: this changes how a card is TRIGGERED and how that
is shown. It does not touch what any card does, when effects resolve, targeting,
or canActivateCard's gating. Nothing below goes near those.

--- what the recon established, and what it changes here -------------------

usedCards[cardId] IS the source of truth (uses remaining, correct across resume).
`.in-zone` was the ONLY piece of state that existed purely as DOM position, and
it was a HARD GATE: onDragStart refused on it, so a card whose uses had been
refunded read as usable and could not be picked up. It is deleted outright here,
which is the redesign and the bug fix in one move.

ONE EXIT PATH. snapCardBack assumed the element never moved; placeCardInZone
reparented it into the zone and did `style.cssText=''`, DESTROYING the fan-slot
custom properties (--rot, --cx, --lift, --wobble-d) that say where the card
lives. The slot only came back because buildCBar rebuilt it from scratch. Now a
drag has exactly one way to end - _returnCardToSlot - and it restores origStyle,
which is those very properties as captured at drag start. Nothing calls
cssText='' any more.

THE DECISION IS MADE AT RELEASE, and that answers the brief's mid-drag question.
The old code could fire the card during the momentum COAST, i.e. after the
player let go - so "where it ended up" decided, not "where they released". Under
a threshold that is the wrong rule and it also widened the window in which the
board could change under a selected target. The coast is now purely a return
flourish: canActivateCard is consulted once, at the release frame, immediately
before activateCard runs. There is no gap between the check and the effect for a
die to die in. Cards that need a target already refuse and refund themselves
(SELECT A DIE TO FREEZE FIRST), so that path is unchanged and still works.

THE ZONE'S RESERVED SPACE STAYS. --activate-zone-h and --dice-reserve-gap are
NOT reclaimed, deliberately: they now set where the dice block sits, and Denis
tuned that to his line two patches ago. Removing the zone's 76px would drop the
dice a further ~56px and undo it. The zone stops being drawn and stops being a
drop target; the numbers keep their new job and say so.
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


# ═══ 1. the gate: a flag, not a position ═══════════════════════════════════
sub(u"  function onDragStart(e){\n"
    u"    if(mcardEl.classList.contains('used'))return;\n"
    u"    /* Cards in the activation zone (already spent this turn) shouldn't\n"
    u"       be draggable — tap-for-tooltip still works via click listeners. */\n"
    u"    if(mcardEl.classList.contains('in-zone'))return;\n",
    u"  function onDragStart(e){\n"
    u"    /* P612: THE FLAG DECIDES, not a class and never a position. `.in-zone`\n"
    u"       used to refuse here, and because it was pure DOM position a card whose\n"
    u"       use had been refunded read as usable and still could not be picked up.\n"
    u"       usedCards is the source of truth; `.used` is only its mirror and is\n"
    u"       kept as a fallback for any card outside activeCardState. */\n"
    u"    if(!_cardHasUse(cardId))return;\n",
    'P612 drag gate')

# ═══ 2. the threshold, the arming, and one exit ════════════════════════════
sub(u"function hitTestActivateZone(clientX,clientY){",
    u"/* P612: THE INVISIBLE THRESHOLD.\n"
    u"   A horizontal line a fixed lift above the player's card row. Below it a\n"
    u"   drag is just a drag; above it the card glows, and that glow is the only\n"
    u"   sign the line exists. Measured off the row rather than stored as a screen\n"
    u"   coordinate, so it survives every viewport and the row moving. */\n"
    u"function _cardThresholdY(){\n"
    u"  var row=document.getElementById('playerCards');\n"
    u"  if(!row)return -1e9;/* no row: nothing can be above the line */\n"
    u"  var r=row.getBoundingClientRect();\n"
    u"  var lift=parseFloat(getComputedStyle(document.documentElement)\n"
    u"    .getPropertyValue('--card-arm-lift'))||0;\n"
    u"  /* the var is in cqw against the screen's width, same as the row's own\n"
    u"     sizing, so resolve it the same way rather than trusting a px read */\n"
    u"  var sc=document.getElementById('screen-match');\n"
    u"  var w=sc?sc.getBoundingClientRect().width:innerWidth;\n"
    u"  return r.top-(w*lift/100);\n"
    u"}\n"
    u"/* is THIS card currently above the line? the card's centre, which is the\n"
    u"   most predictable point for a finger to aim */\n"
    u"function _cardIsArmed(el){\n"
    u"  if(!el)return false;\n"
    u"  var r=el.getBoundingClientRect();\n"
    u"  return (r.top+r.height/2)<_cardThresholdY();\n"
    u"}\n"
    u"/* uses remaining, read from the flag. `.used` is a fallback only. */\n"
    u"function _cardHasUse(cardId){\n"
    u"  try{\n"
    u"    var u=G&&G.activeCardState&&G.activeCardState.usedCards;\n"
    u"    if(u&&u[cardId]!==undefined)return (u[cardId]||0)>0;\n"
    u"  }catch(e){}\n"
    u"  var el=document.querySelector('.mcard[data-cid=\"'+cardId+'\"]');\n"
    u"  return !(el&&el.classList.contains('used'));\n"
    u"}\n"
    u"/* THE ONLY WAY A DRAG ENDS. Both outcomes put the card back in its own\n"
    u"   slot; the only difference is whether it lands spent. origStyle is the\n"
    u"   fan-slot custom properties captured at drag start, which is why nothing\n"
    u"   here may ever call cssText='' - that was what destroyed the slot. */\n"
    u"function _returnCardToSlot(mcardEl,savedState,spent){\n"
    u"  mcardEl.classList.remove('dragging','peeked','armed');\n"
    u"  if(spent){\n"
    u"    /* A CUT, NOT A RETURN FLIGHT, as the brief asks: the dragged card is\n"
    u"       gone and the spent one is simply already home. Restoring origStyle\n"
    u"       with no FLIP is exactly that. */\n"
    u"    mcardEl.style.cssText=savedState.origStyle;\n"
    u"    mcardEl.classList.add('card-spent-cut');\n"
    u"    setTimeout(function(){mcardEl.classList.remove('card-spent-cut');},300);\n"
    u"  }else{\n"
    u"    snapCardBack(mcardEl,savedState);\n"
    u"  }\n"
    u"  /* the greyed rendering is DERIVED, every time, from the current flag -\n"
    u"     never written once at drop time and left to go stale */\n"
    u"  if(typeof _updatePlayerCardVisuals==='function')_updatePlayerCardVisuals();\n"
    u"  if(typeof _updateCardGlints==='function'){try{_updateCardGlints();}catch(e){}}\n"
    u"}\n"
    u"function hitTestActivateZone(clientX,clientY){",
    'P612 threshold helpers')

# ═══ 3. arming during the drag ═════════════════════════════════════════════
sub(u"    hitTestActivateZone(touch.clientX,touch.clientY);",
    u"    /* P612: the glow, and nothing else, tells the player the line is there */\n"
    u"    mcardEl.classList.toggle('armed',_cardIsArmed(mcardEl)&&canActivateCard(cardId));",
    'P612 arm during drag')

# ═══ 4. release decides ════════════════════════════════════════════════════
sub(u"    function tryDrop(){\n"
    u"      var zone=document.getElementById('activateZone');\n"
    u"      var cr=mcardEl.getBoundingClientRect();\n"
    u"      var zr=zone.getBoundingClientRect();\n"
    u"      var overlapL=Math.max(cr.left,zr.left),overlapR=Math.min(cr.right,zr.right);\n"
    u"      var overlapT=Math.max(cr.top,zr.top),overlapB=Math.min(cr.bottom,zr.bottom);\n"
    u"      var overlapArea=(overlapR>overlapL&&overlapB>overlapT)?(overlapR-overlapL)*(overlapB-overlapT):0;\n"
    u"      var cardArea=cr.width*cr.height;\n"
    u"      return overlapArea>cardArea*0.5;\n"
    u"    }\n"
    u"    var dropInZone=tryDrop();\n"
    u"    var canUse=canActivateCard(cardId);\n"
    u"    if(dropInZone&&canUse){\n"
    u"      _commitActivation(mcardEl,cardId,savedState);\n"
    u"      hideActivateZone();window._dragEndedAt=Date.now();_dragState=null;\n"
    u"    }else{\n"
    u"      /* Momentum: if velocity is high enough and moving upward, coast the card */\n"
    u"      var speed=Math.sqrt(savedState.vx*savedState.vx+savedState.vy*savedState.vy);\n"
    u"      if(speed>200&&savedState.vy<-80){\n"
    u"        /* Coast with deceleration */\n"
    u"        var vx=savedState.vx,vy=savedState.vy;\n"
    u"        var friction=0.92;var _momFrame=null;\n"
    u"        (function coast(){\n"
    u"          vx*=friction;vy*=friction;\n"
    u"          var curLeft=parseFloat(mcardEl.style.left)||0;\n"
    u"          var curTop=parseFloat(mcardEl.style.top)||0;\n"
    u"          mcardEl.style.left=(curLeft+vx/60)+'px';\n"
    u"          mcardEl.style.top=(curTop+vy/60)+'px';\n"
    u"          hitTestActivateZone(curLeft+savedState.origRect.width/2+vx/60,curTop+savedState.origRect.height/2+vy/60);\n"
    u"          if(tryDrop()&&canActivateCard(cardId)){\n"
    u"            _commitActivation(mcardEl,cardId,savedState);\n"
    u"            hideActivateZone();return;\n"
    u"          }\n"
    u"          if(Math.abs(vx)+Math.abs(vy)>30){\n"
    u"            _momFrame=requestAnimationFrame(coast);\n"
    u"          }else{\n"
    u"            snapCardBack(mcardEl,savedState);\n"
    u"            hideActivateZone();\n"
    u"          }\n"
    u"        })();\n"
    u"      }else{\n"
    u"        snapCardBack(mcardEl,savedState);\n"
    u"        hideActivateZone();\n"
    u"      }\n"
    u"      window._dragEndedAt=Date.now();_dragState=null;\n"
    u"    }\n"
    u"  }",
    u"    /* P612: RELEASED ABOVE THE LINE - that is the whole rule, and it is read\n"
    u"       on the release frame. The old code could also fire the card during the\n"
    u"       momentum COAST, i.e. after the player had let go, so where it drifted\n"
    u"       to decided rather than where they released. The coast survives as a\n"
    u"       purely visual flourish and can no longer activate anything.\n"
    u"       canActivateCard is consulted HERE, one statement before activateCard\n"
    u"       runs, so nothing can invalidate a target between the check and the\n"
    u"       effect. */\n"
    u"    var released=_cardIsArmed(mcardEl);\n"
    u"    var canUse=canActivateCard(cardId);\n"
    u"    mcardEl.classList.remove('armed');\n"
    u"    window._dragEndedAt=Date.now();_dragState=null;\n"
    u"    if(released&&canUse){\n"
    u"      _commitActivation(mcardEl,cardId,savedState);\n"
    u"    }else{\n"
    u"      _returnCardToSlot(mcardEl,savedState,false);\n"
    u"    }\n"
    u"  }",
    'P612 release decides')

# ═══ 5. commit: both outcomes go home ══════════════════════════════════════
sub(u"function _commitActivation(mcardEl,cardId,savedState){\n"
    u"  SFX.nav();\n"
    u"  activateCard(cardId);\n"
    u"  var usesLeft=(G&&G.activeCardState&&G.activeCardState.usedCards)?(G.activeCardState.usedCards[cardId]||0):0;\n"
    u"  /* The Pyre opens an async picker — keep the card in hand until it resolves\n"
    u"     (a Cancel refunds the use; parking it in the zone stranded it there). */\n"
    u"  if(usesLeft>0||(G&&G._pyrePickerOpen))returnCardToHand(mcardEl,savedState);\n"
    u"  else placeCardInZone(mcardEl,savedState);",
    u"function _commitActivation(mcardEl,cardId,savedState){\n"
    u"  SFX.nav();\n"
    u"  try{_haptic([12,30,12]);}catch(e){}\n"
    u"  mcardEl.classList.add('card-fired');\n"
    u"  setTimeout(function(){mcardEl.classList.remove('card-fired');},420);\n"
    u"  activateCard(cardId);\n"
    u"  var usesLeft=(G&&G.activeCardState&&G.activeCardState.usedCards)?(G.activeCardState.usedCards[cardId]||0):0;\n"
    u"  /* P612: BOTH OUTCOMES GO BACK TO THE SLOT - that is the redesign. A card\n"
    u"     with uses left flies home and stays live; a spent one cuts home and\n"
    u"     lands greyed. Nothing is parked anywhere and no space is reserved for a\n"
    u"     card before or after it fires.\n"
    u"     The Pyre's async picker still counts as \"uses left\" until it resolves,\n"
    u"     for the reason the old comment gives: a Cancel refunds the use. */\n"
    u"  var live=(usesLeft>0||(G&&G._pyrePickerOpen));\n"
    u"  if(live)returnCardToHand(mcardEl,savedState);\n"
    u"  else _returnCardToSlot(mcardEl,savedState,true);",
    'P612 commit goes home')

# ═══ 6. placeCardInZone retired ════════════════════════════════════════════
sub(u"function placeCardInZone(mcardEl,dragState){",
    u"/* P612: DEAD, and kept only as a loud stub for a stray caller. It reparented\n"
    u"   the card into #activateZone and ran style.cssText='' - which destroyed the\n"
    u"   fan-slot custom properties that say where the card lives. Nothing parks a\n"
    u"   card any more; see _returnCardToSlot. */\n"
    u"function placeCardInZone(mcardEl,dragState){\n"
    u"  try{console.warn('placeCardInZone is retired (P612)');}catch(e){}\n"
    u"  if(mcardEl&&dragState)_returnCardToSlot(mcardEl,dragState,true);\n"
    u"  return;\n"
    u"}\n"
    u"function _placeCardInZone_retired(mcardEl,dragState){",
    'P612 placeCardInZone retired')

# ═══ 7. the glint gate stops reading position ══════════════════════════════
sub(u"    if(!mc||mc.classList.contains('in-zone')||mc.classList.contains('used'))return;",
    u"    /* P612: `.in-zone` is gone; `.used` is the flag's mirror */\n"
    u"    if(!mc||mc.classList.contains('used'))return;",
    'P612 glint gate')

# ═══ 8. a drag cannot outlive its listeners ════════════════════════════════
sub(u"  _dragCleanups.push(()=>{\n"
    u"    document.removeEventListener('mousemove',moveFn);",
    u"  _dragCleanups.push(()=>{\n"
    u"    /* P612: a card mid-drag when the row is rebuilt (resume, a new turn, a\n"
    u"       card burned) would leave _dragState pointing at a detached element,\n"
    u"       and the next pointer event would move a card that is no longer in the\n"
    u"       DOM. Clearing it here makes teardown the third way a drag can end -\n"
    u"       silently, with the row about to be rebuilt from state anyway. */\n"
    u"    try{if(_dragState&&_dragState.el===mcardEl){mcardEl.classList.remove('dragging','armed');_dragState=null;}}catch(e){}\n"
    u"    document.removeEventListener('mousemove',moveFn);",
    'P612 drag teardown')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
