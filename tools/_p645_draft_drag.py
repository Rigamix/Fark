# -*- coding: utf-8 -*-
"""P645: drag an offered card into a slot to take it.

Denis: "even without having them in focus I'd want to be able to drag them in a
slot to pick one. There is a point the players will be familiar enough with card
art that they won't need to read their tooltips before deciding and we should
allow for this. Whatever slot I drag the card in, show the card in. But when I'm
out of the screen just put the cards in the order that makes sense. So if I have
one card it's always in the middle slot, etc. It's just visual on that screen"

THE TAP PATH IS UNTOUCHED. Tapping a card still opens its sheet and CLAIM still
takes it, through famDraftPick exactly as before. The drag is a second way in,
not a replacement, which is what "even without having them in focus" asks for.

A TAP IS NOT A SHORT DRAG. The gesture only becomes a drag past 8px of travel;
under that the pointer sequence is left alone and the card's own onclick opens
the sheet. Past it, the click is swallowed on the way out - otherwise every drop
would also open the sheet of the card you just took.

WHERE IT LANDS DECIDES WHAT HAPPENS, and both cases already had a function:
  empty slot   -> famDraftPick, the same call CLAIM makes
  filled slot  -> _famReplaceDo on that slot's card, the same call the TRADE OUT
                  picker makes - so dropping onto a card you hold IS choosing it
                  to let go, without the extra sheet
Nothing new decides anything; the drop only picks which existing door to use.

"SHOW THE CARD IN" WHATEVER SLOT IT WAS DROPPED IN. The old finish wrote a
"TAKEN: NAME" line over the whole panel, which throws away the one thing the
gesture just established. A drag finish re-renders the deck with the new card in
the position it was dropped, and drops the offer row - so the screen answers the
gesture with the picture rather than with a word.

AND THE DEFAULT ARRANGEMENT IS CENTRED, per "if I have one card it's always in
the middle slot, etc." _foLayout is the whole rule and it is one function:
  1 card  -> the middle position
  2 cards -> the outer two, symmetric about it
  3 cards -> all three
That is the only reading that generalises from the case Denis named. It is
PURELY VISUAL - S.run.fcards stays the dense array _famDiceMigrate normalises it
to, so nothing downstream sees a hole, and the arrangement is recomputed from
the count every time this screen opens. Change the function, change the rule.
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


# ── 1. the layout rule + the deck renderer, shared by both finishes ──────
sub(u"function famOfferHtml(offer,pickFn,declineGold){",
    u"/* P645: WHICH OF THE THREE POSITIONS HOLD CARDS. Denis's rule - \"if I have\n"
    u"   one card it's always in the middle slot, etc.\" - so the hand is centred\n"
    u"   rather than left-packed. Returns a position->card-index map with nulls for\n"
    u"   the empty places.\n"
    u"   PURELY VISUAL. S.run.fcards stays the dense array _famDiceMigrate\n"
    u"   normalises it to, so nothing downstream ever sees a hole, and this is\n"
    u"   recomputed from the count each time the screen opens. One function, one\n"
    u"   rule: change it here and every deck row on this screen follows. */\n"
    u"function _foLayout(count){\n"
    u"  if(count<=0)return [null,null,null];\n"
    u"  if(count===1)return [null,0,null];\n"
    u"  if(count===2)return [0,null,1];\n"
    u"  return [0,1,2];\n"
    u"}\n"
    u"/* the deck row, with an optional OVERRIDE: {pos:index} pins one card to the\n"
    u"   position it was just dropped in, which is the whole point of the drag. */\n"
    u"function _foDeckHtml(pin){\n"
    u"  _getS();S.run.fcards=S.run.fcards||[];\n"
    u"  var cards=S.run.fcards,lay=_foLayout(cards.length);\n"
    u"  if(pin&&pin.pos!=null&&pin.idx!=null){\n"
    u"    /* the pinned card takes its slot and the rest fill the others in order */\n"
    u"    var rest=[];for(var r=0;r<cards.length;r++)if(r!==pin.idx)rest.push(r);\n"
    u"    lay=[null,null,null];lay[pin.pos]=pin.idx;\n"
    u"    for(var p=0,q=0;p<3&&q<rest.length;p++)if(lay[p]===null)lay[p]=rest[q++];\n"
    u"  }\n"
    u"  var h='<div class=\"fo-deck\">';\n"
    u"  for(var _s=0;_s<3;_s++){\n"
    u"    var _ci=lay[_s],_c=(_ci!=null)?cards[_ci]:null;\n"
    u"    if(_c){\n"
    u"      var _cd=famDef(_c.id);\n"
    u"      h+='<div class=\"fo-slot filled\" data-pos=\"'+_s+'\" data-ci=\"'+_ci+'\"'\n"
    u"        +' onclick=\"famCardSheet(\\''+_c.id+'\\','+_c.tier+')\">'\n"
    u"        +famCardArt(_c.id,_c.tier,{tierAlways:(_cd&&_cd.fam!=='tavern')})+'</div>';\n"
    u"    }else{\n"
    u"      h+='<div class=\"fo-slot empty\" data-pos=\"'+_s+'\"></div>';\n"
    u"    }\n"
    u"  }\n"
    u"  return h+'</div>';\n"
    u"}\n"
    u"function famOfferHtml(offer,pickFn,declineGold){",
    'P645 the layout rule and the shared deck renderer')

# ── 2. the offer uses it ─────────────────────────────────────────────────
sub(u"  _getS();S.run.fcards=S.run.fcards||[];\n"
    u"  h+='<div class=\"fo-decklbl\">YOUR DECK</div>'\n"
    u"    +'<div class=\"fo-deck\">';\n"
    u"  for(var _s=0;_s<3;_s++){\n"
    u"    var _c=S.run.fcards[_s];\n"
    u"    if(_c){\n"
    u"      var _cd=famDef(_c.id);\n"
    u"      h+='<div class=\"fo-slot filled\" onclick=\"famCardSheet(\\''+_c.id+'\\','+_c.tier+')\">'\n"
    u"        +famCardArt(_c.id,_c.tier,{tierAlways:(_cd&&_cd.fam!=='tavern')})+'</div>';\n"
    u"    }else{\n"
    u"      h+='<div class=\"fo-slot empty\">+</div>';\n"
    u"    }\n"
    u"  }\n"
    u"  h+='</div>';",
    u"  h+='<div class=\"fo-decklbl\">YOUR DECK</div>'+_foDeckHtml(null);",
    'P645 the offer draws its deck through the shared renderer')

# ── 3. the drag ──────────────────────────────────────────────────────────
sub(u"function famApplyPick(o){",
    u"/* P645: DRAG AN OFFER ONTO A SLOT. Installed on the offer row after it\n"
    u"   renders; delegated, so it survives the row being rebuilt.\n"
    u"   A TAP IS NOT A SHORT DRAG - nothing happens under 8px of travel, so the\n"
    u"   card's own onclick still opens its sheet. Past the threshold the click is\n"
    u"   swallowed on release, or every drop would open the sheet of the card the\n"
    u"   player just took. */\n"
    u"var _FO_DRAG_MIN=8;\n"
    u"function _foInstallDrag(){\n"
    u"  var offer=document.querySelector('#end-ov .fo-offer');if(!offer)return;\n"
    u"  if(offer._foDrag)return;offer._foDrag=1;\n"
    u"  var st=null;\n"
    u"  function slotAt(x,y){\n"
    u"    var el=document.elementFromPoint(x,y);\n"
    u"    return el&&el.closest?el.closest('#end-ov .fo-slot'):null;\n"
    u"  }\n"
    u"  function clearHover(){\n"
    u"    document.querySelectorAll('#end-ov .fo-slot.drop-hover')\n"
    u"      .forEach(function(e){e.classList.remove('drop-hover');});\n"
    u"  }\n"
    u"  offer.addEventListener('pointerdown',function(ev){\n"
    u"    var card=ev.target.closest&&ev.target.closest('.fo-card');if(!card)return;\n"
    u"    var idx=[].indexOf.call(offer.children,card);if(idx<0)return;\n"
    u"    st={card:card,idx:idx,x0:ev.clientX,y0:ev.clientY,live:false};\n"
    u"  });\n"
    u"  offer.addEventListener('pointermove',function(ev){\n"
    u"    if(!st)return;\n"
    u"    var dx=ev.clientX-st.x0,dy=ev.clientY-st.y0;\n"
    u"    if(!st.live&&Math.hypot(dx,dy)<_FO_DRAG_MIN)return;\n"
    u"    if(!st.live){st.live=true;st.card.classList.add('fo-dragging');\n"
    u"      try{st.card.setPointerCapture(ev.pointerId);}catch(e){}}\n"
    u"    st.card.style.transform='translate('+dx+'px,'+dy+'px) scale(1.04)';\n"
    u"    clearHover();\n"
    u"    var sl=slotAt(ev.clientX,ev.clientY);if(sl)sl.classList.add('drop-hover');\n"
    u"    ev.preventDefault();\n"
    u"  });\n"
    u"  function end(ev){\n"
    u"    if(!st)return;var s0=st;st=null;\n"
    u"    s0.card.classList.remove('fo-dragging');s0.card.style.transform='';\n"
    u"    clearHover();\n"
    u"    if(!s0.live)return;/* it was a tap - let the onclick through */\n"
    u"    /* swallow exactly one click, the one this release is about to produce */\n"
    u"    var eat=function(e){e.stopPropagation();e.preventDefault();};\n"
    u"    document.addEventListener('click',eat,{capture:true,once:true});\n"
    u"    setTimeout(function(){document.removeEventListener('click',eat,true);},300);\n"
    u"    var sl=slotAt(ev.clientX,ev.clientY);if(!sl)return;\n"
    u"    _foDropOn(s0.idx,sl);\n"
    u"  }\n"
    u"  offer.addEventListener('pointerup',end);\n"
    u"  offer.addEventListener('pointercancel',end);\n"
    u"}\n"
    u"/* WHERE IT LANDED DECIDES WHICH EXISTING DOOR IT USES. An empty slot is the\n"
    u"   CLAIM path; a filled one is the TRADE OUT path with the choice already\n"
    u"   made by where the player let go. Neither decision is re-implemented here. */\n"
    u"function _foDropOn(offerIdx,slotEl){\n"
    u"  var o=_famOffer&&_famOffer[offerIdx];if(!o)return;\n"
    u"  var pos=+slotEl.getAttribute('data-pos');\n"
    u"  var ciAttr=slotEl.getAttribute('data-ci');\n"
    u"  try{SFX.cardTrigger&&SFX.cardTrigger();}catch(e){}\n"
    u"  _getS();S.run.fcards=S.run.fcards||[];\n"
    u"  if(ciAttr!=null&&ciAttr!==''){\n"
    u"    /* dropped onto a card you hold: that is the one you are letting go */\n"
    u"    window._famReplaceOffer=o;\n"
    u"    var ci=+ciAttr;\n"
    u"    S.run.fcards[ci]={id:o.id,tier:o.tier};save();\n"
    u"    window._famReplaceOffer=null;\n"
    u"    _foDraftDoneAt(o,pos,ci);\n"
    u"    return;\n"
    u"  }\n"
    u"  if(!o.upgrade&&S.run.fcards.length>=3){_famReplacePick(o);return;}\n"
    u"  famApplyPick(o);\n"
    u"  var newIdx=-1;\n"
    u"  for(var i=0;i<S.run.fcards.length;i++)if(S.run.fcards[i].id===o.id)newIdx=i;\n"
    u"  _foDraftDoneAt(o,pos,newIdx);\n"
    u"}\n"
    u"/* the drag's own finish. _famDraftDone writes \"TAKEN: NAME\" over the panel,\n"
    u"   which throws away the one thing this gesture just established - WHERE the\n"
    u"   card went. This answers with the picture instead: the deck, with the card\n"
    u"   pinned to the slot it was dropped in. */\n"
    u"function _foDraftDoneAt(o,pos,idx){\n"
    u"  var rc=document.querySelector('#end-ov .res-card')||document.getElementById('resCard');\n"
    u"  if(rc)rc.innerHTML='<div class=\"fo-wrap\"><div class=\"fo-title\">TAKEN</div>'\n"
    u"    +_foDeckHtml({pos:pos,idx:idx})+'</div>';\n"
    u"  _famEndReady();\n"
    u"}\n"
    u"function famApplyPick(o){",
    'P645 the drag, the drop resolver and the drag finish')

# ── 4. install it where the offer is built ───────────────────────────────
sub(u"    try{\n"
    u"      var _ovSk=document.getElementById('end-ov');\n"
    u"      _ovSk.querySelectorAll(':scope>.fo-skip').forEach(function(e){e.remove();});\n"
    u"      var _sk=resCard&&resCard.querySelector('.fo-skip');\n"
    u"      if(_sk&&_ovSk)_ovSk.appendChild(_sk);\n"
    u"    }catch(e){}",
    u"    try{\n"
    u"      var _ovSk=document.getElementById('end-ov');\n"
    u"      _ovSk.querySelectorAll(':scope>.fo-skip').forEach(function(e){e.remove();});\n"
    u"      var _sk=resCard&&resCard.querySelector('.fo-skip');\n"
    u"      if(_sk&&_ovSk)_ovSk.appendChild(_sk);\n"
    u"    }catch(e){}\n"
    u"    try{_foInstallDrag();}catch(e){}",
    'P645 install the drag with the offer')

# ── 5. the two states the drag needs to be visible ───────────────────────
sub(u".fo-card{position:relative;transition:transform .18s ease}\n"
    u".fo-card:active{transform:translateY(1px) scale(.985)}",
    u".fo-card{position:relative;transition:transform .18s ease;touch-action:none}\n"
    u".fo-card:active{transform:translateY(1px) scale(.985)}\n"
    u"/* P645: the card in hand. No transition while dragging - the transform is\n"
    u"   being set every pointermove and an easing curve on it lags the finger. */\n"
    u".fo-card.fo-dragging{transition:none;z-index:9;pointer-events:none;\n"
    u"  filter:drop-shadow(0 6px 10px rgba(0,0,0,.55))}\n"
    u"/* the slot under the finger, in the same gold the slots are drawn in */\n"
    u"#end-ov .fo-slot.drop-hover{border-color:rgba(255,216,120,.95);\n"
    u"  background:rgba(255,216,120,.16);\n"
    u"  box-shadow:0 0 10px rgba(255,216,120,.35)}",
    'P645 the drag and drop-target states')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
