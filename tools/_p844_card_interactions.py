# -*- coding: utf-8 -*-
"""P844: card interactions get a written rule and an enforcer.

Denis (2026-08-21): "I played Stargazer and then another card but by
doing so I broke Stargazer, its numbers remaining stuck on screen."
Measured (probe _p844_before): stargazer -> sacrifice leaves all six
ghosts up over five dice, the six-entry promise armed, and the next
roll lands the promised faces LANE-SHIFTED onto the wrong dice.

THE RULE (docs/CARD_INTERACTION_RULES.md): a promise or an arm is a
claim about the table AS IT STOOD when the card was played. Any effect
that mutates the free pool outside the roll path voids it - values and
visuals together, through the existing one exit (_clearRollForces).

The enforcer: famTableChanged() - _steadyDisarm + _transDisarm +
_clearRollForces + a player-facing THE STARS BLUR log when a promise
actually died. Enrolled at every mutation moment:
  fam layer: steady_hand tap, _transPick, powder_keg, encore,
             _removeDieAt (sacrifice/break/seizures/shatter)
  CARDS layer: one hook after activateCard's dispatch, keyed on the
             16 handlers classified as dice-mutating (awk census)
Plus the same-class holes the census found in passing:
  - transmute's rings/onclick hijack now disarm with the flag
    (_transDisarm; was cleaned only by steady_hand's sweep -
    safety by coincidence)
  - transmute's leave-it button leaked window._transDie/_transInst
    (dead die ref) - now routes through _transPick(0) which nulls
  - steady_hand had NO exit reachable from the bank flow - endPTurn
    now disarms
  - encore's 500ms callback ran against live G with no identity guard
    (every other deferred card callback has one) - guarded
  - G._pvDie.lane had no maintainer in _removeDieAt (preserve's
    third door to right-numbers-empty-board) - repaired beside
    _pvLane
  - ghosts/marks are lane-stamped and _famRefloatGhosts() re-anchors
    them after a vagabond drag reorder (reorder is cosmetic - it
    must NOT void the promise, just move the floats)
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# E1: _transDisarm + famTableChanged + _famRefloatGhosts, and the
# transmute-arm void inside _clearRollForces routes through the disarm
sub("""  G._transArmed=false;/* P829: a roll voids a stranded transmute arm */""",
    """  try{_transDisarm();}catch(e){}/* P829/P844: a stranded transmute arm is
     voided WITH its rings and hijacked taps - the rings used to be
     cleaned only by steady_hand's sweep on the roll path (safety by
     coincidence) */""",
    'E1b transmute void routes through the disarm')

sub("""  try{(window._htMarks||[]).forEach(function(g){if(g.parentNode)g.remove();});window._htMarks=[];}catch(e){}
}
function famApplyRollForces(){""",
    """  try{(window._htMarks||[]).forEach(function(g){if(g.parentNode)g.remove();});window._htMarks=[];}catch(e){}
}
/* P844: transmute's disarm owns flag AND visuals together - the
   _steadyDisarm model. Guarded so the every-roll clear path does not
   re-bind onclicks the roll flow owns. */
function _transDisarm(){
  if(!G||!G._transArmed)return;
  G._transArmed=false;
  try{(G.pool||[]).forEach(function(d){
    if(d.el&&!d.committed){d.el.classList.remove('break-target');d.el.onclick=function(){toggleDie(d);};}
  });}catch(e){}
}
/* P844: THE TABLE CHANGED UNDER A PROMISE. A peek, a pull, or an arm
   is a claim about the table AS IT STOOD when the card was played -
   any effect that mutates the free pool outside the roll path voids
   it, values and visuals together, through the one existing exit.
   Measured before this: stargazer -> sacrifice left the ghosts up and
   landed the promised faces lane-shifted onto the WRONG dice.
   docs/CARD_INTERACTION_RULES.md is the written rule; every new
   mutating card enrolls here (the _steadyDisarm precedent). */
function famTableChanged(){
  if(!G)return;
  var _hadPromise=!!(G._famPeekVals||G._famHoneyVal);
  try{_steadyDisarm();}catch(e){}
  if(_hadPromise||((window._pkGhosts||[]).length)||((window._htMarks||[]).length)||G._transArmed){
    _clearRollForces();
    if(_hadPromise)try{famLog('THE STARS BLUR \u2014 THE TABLE CHANGED');}catch(e){}
  }
}
/* P844: a vagabond reorder is COSMETIC - same dice, same values, new
   seats. It must not void a promise; the floats just follow their
   dice. Ghosts and marks are lane-stamped at mint for exactly this. */
function _famRefloatGhosts(){
  try{
    var byLane={};(G&&G.pool||[]).forEach(function(d){if(d.el&&!d.committed)byLane[d.lane]=d;});
    [].concat(window._pkGhosts||[],window._htMarks||[]).forEach(function(g){
      if(!g.isConnected)return;
      var d=byLane[+g.dataset.lane];
      if(!d){if(g.parentNode)g.remove();return;}
      var r=d.el.getBoundingClientRect();if(!(r.width>0))return;
      g.style.left=(r.left+r.width/2)+'px';g.style.top=(r.top+r.height/2)+'px';
    });
  }catch(e){}
}
function famApplyRollForces(){""",
    'E1 famTableChanged + _transDisarm + _famRefloatGhosts')

# E2: stargazer ghosts carry their lane
sub("""        g.className='peek-float';g.textContent=String(G._famPeekVals[i].val);""",
    """        g.className='peek-float';g.textContent=String(G._famPeekVals[i].val);
        g.dataset.lane=String(G._famPeekVals[i].lane);/* P844: refloat key */""",
    'E2 ghost lane stamp')

# E3: honeytrap marks carry their lane
sub("""          g.className='honey-float';g.textContent='\\uD83C\\uDF6F';""",
    """          g.className='honey-float';g.textContent='\\uD83C\\uDF6F';
          g.dataset.lane=String(d.lane);/* P844: refloat key */""",
    'E3 mark lane stamp')

# E4: steady_hand's reroll is a table change
sub("""        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}
        /* P535: RE-DERIVE.""",
    """        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}
        try{famTableChanged();}catch(e){}/* P844: the reroll changed the table a promise was read from */
        /* P535: RE-DERIVE.""",
    'E4 steady tap enrolls')

# E5: transmute's pick is a table change
sub("""  famLog('TRANSMUTED TO '+f);
  try{refreshSelUI();}catch(e){}try{famRenderRow();}catch(e){}""",
    """  famLog('TRANSMUTED TO '+f);
  try{famTableChanged();}catch(e){}/* P844 */
  try{refreshSelUI();}catch(e){}try{famRenderRow();}catch(e){}""",
    'E5 transmute pick enrolls')

# E6: the leave-it button stops leaking the stashed die ref
sub("""          +'<div class="gbx-btn" style="height:40px" onclick="_gbModalClose()">leave it</div>');""",
    """          +'<div class="gbx-btn" style="height:40px" onclick="_gbModalClose();_transPick(0)">leave it</div>');/* P844: _transPick(0) nulls the stashed refs, fails validation, bills nothing */""",
    'E6 leave-it leak')

# E7: encore - table change + G-identity guard on the deferred check
sub("""    _steadyDisarm();/* these dice are new - the arm was about the old ones */
    /* held across the resolve window, and cleared on every way out of it */
    G._encorePending=true;
    G.phase='rolling';
    setTimeout(function(){
      G._encorePending=false;""",
    """    famTableChanged();/* P844: these dice are new - every arm and promise was about the old ones */
    /* held across the resolve window, and cleared on every way out of it */
    G._encorePending=true;
    G.phase='rolling';
    var _eg=G;/* P844: the _ddG pattern - a match torn down inside the
       window must not let this run against the next match's G */
    setTimeout(function(){
      if(G!==_eg)return;
      G._encorePending=false;""",
    'E7 encore enrolls + G guard')

# E8: powder keg - the whole table blows
sub("""    _steadyDisarm();/* these dice are new - the arm was about the old ones */
    var free=G.pool.slice();""",
    """    famTableChanged();/* P844: these dice are new - every arm and promise was about the old ones */
    var free=G.pool.slice();""",
    'E8 keg enrolls')

# E9: _removeDieAt - _pvDie repair beside _pvLane, then the void
sub("""    if(typeof G._pvLane==='number'){
      if(G._pvLane===lane)G._pvLane=null;
      else if(G._pvLane>lane)G._pvLane--;
    }
  }catch(e){}""",
    """    if(typeof G._pvLane==='number'){
      if(G._pvLane===lane)G._pvLane=null;
      else if(G._pvLane>lane)G._pvLane--;
    }
    /* P844: _pvDie is a lane record in the same sense - the third door
       to right-numbers-empty-board (a removal in the restore-to-first-
       deal window aimed it at a moved seat and the deal's occupancy
       guard silently never placed it). */
    var _pvd=G._pvDie;
    if(_pvd&&typeof _pvd.lane==='number'){
      if(_pvd.lane===lane)G._pvDie=null;
      else if(_pvd.lane>lane)_pvd.lane--;
    }
  }catch(e){}
  /* P844: a die leaving the table is a table change - promises void
     rather than land lane-shifted on the wrong dice (measured). */
  try{famTableChanged();}catch(e){}""",
    'E9 removeDieAt: _pvDie repair + void')

# E10: steady_hand gets an exit reachable from the bank flow
sub("""  _clearRollForces();
  /* P766 (Q3): the bespoke omen consumer is DELETED""",
    """  _clearRollForces();
  try{_steadyDisarm();}catch(e){}/* P844: the one arm with no exit on this path */
  /* P766 (Q3): the bespoke omen consumer is DELETED""",
    'E10 endPTurn disarms steady')

# E11: the CARDS layer - one hook after the dispatch, classified list
sub("""    case 'double_down_die': activateDoubleDownDie(); break;
  }""",
    """    case 'double_down_die': activateDoubleDownDie(); break;
  }
  /* P844: the dice-mutating actives void pending promises/arms - one
     site, one classified list (each handler verified to write d.val,
     splice the pool, or freeze). Flag-only and points-only actives
     stay off it: a promise survives a wager. A NEW active that touches
     dice joins this list - docs/CARD_INTERACTION_RULES.md. */
  if(['grogs_flask','finnicks_palm','brutus_fist','ambrose_grace','vanishing_act',
      'old_bones','frozen_die','double_down','wild_die','seven_dice','coin_flip',
      'the_nudge','alchemists_chisel','alchemist_touch','twinning_charm',
      'double_down_die'].indexOf(cardId)>=0){try{famTableChanged();}catch(e){}}""",
    'E11 activateCard hook')

# E12: the vagabond reorder re-anchors the floats
sub("""  try{_snapDiceOnly();}catch(e){}
  try{_haptic(20);}catch(e){}
  try{SFX.commit&&SFX.commit();}catch(e){}
  setStatusMsg('REARRANGED','active');""",
    """  try{_snapDiceOnly();}catch(e){}
  /* P844: the floats follow their dice to the new seats - once now,
     once after the glide settles. */
  try{_famRefloatGhosts();}catch(e){}
  setTimeout(function(){try{_famRefloatGhosts();}catch(e){}},350);
  try{_haptic(20);}catch(e){}
  try{SFX.commit&&SFX.commit();}catch(e){}
  setStatusMsg('REARRANGED','active');""",
    'E12 drag refloat')

# post-asserts
for needed in ['function famTableChanged()', 'function _transDisarm()',
               'function _famRefloatGhosts()', "dataset.lane=String(G._famPeekVals[i].lane)",
               "_transPick(0)"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
n = s.count('famTableChanged()')
if n != 7:  # the definition + 6 enrollment sites (E4,E5,E7,E8,E9,E11)
    sys.exit('ENROLLMENT COUNT %d != 7 (nothing written)' % n)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s); famTableChanged sites=%d' % (len(edits), ', '.join(edits), n))
