# -*- coding: utf-8 -*-
"""P761: one card pipe, two actors - and Preserve is the proof.

Denis's ruling (docs/NPC_AI_BRIEF.md section 4, and his words): "me
playing a card and them playing the same card should be the same code
bit with just the actor being different... A 'should I play Preserve'
should be a matter of giving them the lever for it, but the Preserve
effect itself should be virtually no different apart from the symmetry."

1. famUse(i, actor). The one entry point for playing a family card,
   actor 'p' (default - every existing call unchanged) or 'o'. Owner
   resolves the instance list (G.pF / G.oF), the same CFX effect runs
   with the actor in hand, the same charges decrement on the same
   instance, and FKFX plays on the rival's own card element in their
   row. NPC_FAM_READY is the registry: a card is offered to the rival
   only once its effect has an actor branch - un-migrated cards cannot
   corrupt player state by accident.

2. Preserve migrates - and the FAKE dies. The NPC 'preserve' was
   G._oPreserve=100: a flat point token, no die, no lane, no amber, and
   it ignored the trapped die's value and material. Now CFX.preserve.use
   with actor 'o' captures their actual kept scorer {val, mat, ench,
   lane} into G._ovDie - the mirror of the player's G._pvDie - and their
   next turn: the credit prices the REAL die (100 or 50), the die is
   re-seated in its own lane as a held die (G._oppHeld, so _oSeats deals
   around it exactly as it does for any die they hold), and the amber
   shell rides the same D3X.amberShell + _amberReturnWhenSettled the
   player's preserve uses. Same effect, upside down.

3. The lever. The bespoke block in finOpp becomes: policy (bank>0, a
   kept scorer on the table, a charged preserve in G.oF) -> famUse('o').
   The when is the NPC's; the what is the shared pipe.

4. The enchant thread. Their deal now carries ench per seat
   (rung.dieEnch when a rung supplies it) and every _scoreRollBest call
   on their path passes the ench array - so enchanted rival dice score
   through the same rules the player's do, the moment a loadout grants
   them. Materials already flowed; enchants were dropped on the floor.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label, count=1):
    global s
    c = s.count(old)
    if c != count:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == count:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d (want %d) for %s (nothing written)' % (c, count, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. famUse grows its actor ──
sub("""function famUse(i){
  if(!G||!G.pF||!G.pF[i])return;
  /* (Confession's seal retired with the rule) */
  var inst=G.pF[i],d=famDef(inst.id),fx=CFX[inst.id];
  if(!d||d.kind!=='active'||!fx||!fx.use)return;
  if(inst.charges<=0)return;
  if(fx.canUse&&!fx.canUse(inst)){famLog('NOT NOW');return;}
  if(fx.use(inst)){
    inst.charges--;
    /* P735: the card's own effect language plays on the card that
       fired - BEFORE the re-render, since that replaces the element
       (the P668 lesson); FKFX's own timers ride the descriptor-free
       primitives, which survive it. */
    try{var _fc=document.querySelectorAll('#famRowP .fcv')[i];
      if(_fc&&window.FKFX)FKFX.play(inst.id,_fc);}catch(e){}
    famRenderRow();
  }
}""",
    """/* P761: WHICH CARDS THE RIVAL MAY PLAY THROUGH THE PIPE. A card joins
   this registry when its CFX effect carries an actor branch - offering
   an un-migrated card to the rival would run player-global code against
   the wrong seat. Grown card by card as effects migrate; the registry
   is the honest inventory of what is truly symmetric so far. */
var NPC_FAM_READY={preserve:1};
function famUse(i,actor){
  /* P761: ONE ENTRY POINT, TWO ACTORS - Denis: "the same code bit with
     just the actor being different". 'p' is the default so every
     existing caller is unchanged. */
  actor=actor||'p';
  var list=(actor==='o')?(G&&G.oF):(G&&G.pF);
  if(!list||!list[i])return;
  /* (Confession's seal retired with the rule) */
  var inst=list[i],d=famDef(inst.id),fx=CFX[inst.id];
  if(!d||d.kind!=='active'||!fx||!fx.use)return;
  if(actor==='o'&&!NPC_FAM_READY[inst.id])return;
  if(inst.charges<=0)return;
  if(fx.canUse&&!fx.canUse(inst,actor)){if(actor==='p')famLog('NOT NOW');return;}
  if(fx.use(inst,actor)){
    inst.charges--;
    /* P735: the card's own effect language plays on the card that
       fired - BEFORE the re-render, since that replaces the element
       (the P668 lesson); FKFX's own timers ride the descriptor-free
       primitives, which survive it. The rival's card is found by id in
       THEIR row - same language, their table edge. */
    try{
      var _fc=null;
      if(actor==='o'){
        var _all=document.querySelectorAll('#famRowO .fcv');
        for(var _q=0;_q<_all.length;_q++){
          if((_all[_q].dataset&&_all[_q].dataset.cid)===inst.id){_fc=_all[_q];break;}
        }
      }else{
        _fc=document.querySelectorAll('#famRowP .fcv')[i];
      }
      if(_fc&&window.FKFX)FKFX.play(inst.id,_fc);
    }catch(e){}
    famRenderRow();
  }
}""",
    'famUse takes an actor')

# ── 2. CFX.preserve: the actor branch ──
sub("""CFX.preserve={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('scorer');/* P738: the shared view, same as honeytrap */
  },
  use:function(inst){""",
    """CFX.preserve={
  canUse:function(inst,actor){
    /* P761: the rival's reading of the same rule - a kept scorer on
       THEIR table, and no die already in amber */
    if(actor==='o'){
      return !!(G&&!G._ovDie&&(G.oppDice||[]).some(function(d){
        return d.kept&&(d.val===1||d.val===5);}));
    }
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('scorer');/* P738: the shared view, same as honeytrap */
  },
  use:function(inst,actor){
    /* P761: THE SAME EFFECT, UPSIDE DOWN. The rival's branch captures
       their actual kept scorer - value, material, brand, lane - into
       G._ovDie, the mirror of the player's G._pvDie below. The credit,
       the re-seat and the amber all happen at their next turn start,
       exactly as the player's deal rebuilds from _pvDie. The old NPC
       'preserve' was G._oPreserve=100: a flat token, no die, no amber,
       wrong price for a trapped 5. It is gone. */
    if(actor==='o'){
      var _kd=null;
      [1,5].some(function(w){
        _kd=(G.oppDice||[]).filter(function(d){return d.kept&&d.val===w;})[0];
        return !!_kd;
      });
      if(!_kd)return false;
      G._ovDie={val:_kd.val,mat:_kd.mat||'bone',ench:_kd.ench||null,lane:_kd.lane};
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' TRAPS A DIE IN AMBER FOR NEXT TURN','red');
      return true;
    }""",
    'preserve speaks both seats')

# ── 3. the lever replaces the fake (finOpp) ──
sub("""      if(pts>0&&(c=_npcFamCard('preserve'))){
        c.charges--;G._oPreserve=100;
        setStatusMsg(G.rung.name+' TRAPS A DIE IN AMBER FOR NEXT TURN','red');
      }""",
    """      /* P761: THE LEVER. Policy here (bank up, a kept scorer showing,
         a charged card) - the effect through the same famUse pipe the
         player's tap uses, actor 'o'. The fake (G._oPreserve=100) died
         with this line. */
      if(pts>0&&!G._ovDie&&(G.oppDice||[]).some(function(d){return d.kept&&(d.val===1||d.val===5);})){
        var _pvIx=-1;
        (G.oF||[]).some(function(o,ix){
          if(o.id==='preserve'&&!o.broken&&o.charges>0){_pvIx=ix;return true;}
          return false;
        });
        if(_pvIx>=0)famUse(_pvIx,'o');
      }""",
    'the lever')

# ── 4. the fake credit becomes the real return ──
sub("""  if(G._oPreserve){
    oppBank+=G._oPreserve;
    setStatusMsg(G.rung.name+': AMBER CRACKS — '+G._oPreserve+' ALREADY KEPT','red');
    G._oPreserve=0;
  }""",
    """  /* P761: the fake credit (G._oPreserve, a flat 100) is gone - the
     real return happens after the row clear below, where the trapped
     die is re-seated; the credit prices the actual die there. */""",
    'fake credit removed')

sub("""  clearRow('oppDiceRow');G.oppDice=[];
  /* P521: THE SEATS AND THE COUNT, FROM ONE PLACE.""",
    """  clearRow('oppDiceRow');G.oppDice=[];
  /* P761: THE AMBER RETURNS - the rival's preserved die, rebuilt the
     way the player's deal rebuilds G._pvDie: the REAL die (value,
     material, brand) seated in its own lane as a held die, so _oSeats
     deals around it; the credit prices what was actually trapped; the
     shell rides the same amberShell + settle watcher the player's
     uses. After the clear on purpose: clearRow resets G._oppHeld. */
  if(G._ovDie){
    var _ov=G._ovDie;G._ovDie=null;
    oppBank+=(_ov.val===1?100:50);
    setStatusMsg(G.rung.name+': AMBER CRACKS — THEIR '+_ov.val+' ALREADY SCORED','red');
    try{
      var _ovRow=document.getElementById('oppDiceRow');
      var _ovEl=mkDie(_ov.val,_ov.mat,null,true,_ov.ench);
      _ovEl.classList.add('kept-still');
      _seatDie(_ovRow,_ovEl,_ov.lane);
      G._oppHeld=G._oppHeld||[];
      G._oppHeld.push({val:_ov.val,el:_ovEl,kept:true,mat:_ov.mat,ench:_ov.ench,lane:_ov.lane});
      (function _oShell(t){
        var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(_ovEl);
        if(dd&&D3X.amberShell){
          D3X.amberShell(dd,true);
          window._fkAmberChip=_ovEl;window._fkAmberWrap=null;
          try{_amberReturnWhenSettled();}catch(e){}
          return;
        }
        if((t||0)<40)setTimeout(function(){_oShell((t||0)+1);},60);
      })(0);
    }catch(e){}
  }
  /* P521: THE SEATS AND THE COUNT, FROM ONE PLACE.""",
    'the real return')

# ── 5. the enchant thread ──
sub("      G.oppDice.push({val,el,kept:false,mat:dieMat,lane:_seat});}",
    """      G.oppDice.push({val,el,kept:false,mat:dieMat,
        ench:(((G.rung||{}).dieEnch)||[])[_seat]||null,/* P761: the brand travels */
        lane:_seat});}""",
    'deal carries ench')

# every NPC _scoreRollBest call gains the ench array, built beside its mats
PAIRS = [
    ("var _qhFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});",
     "var _qhFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});\n"
     "          var _qhFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P761 */"),
    ("var _qhR=_scoreRollBest(_qhFV,G.oCards,oppBank,crowsCtx,_qhFM);",
     "var _qhR=_scoreRollBest(_qhFV,G.oCards,oppBank,crowsCtx,_qhFM,_qhFE);"),
    ("var _gbFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});",
     "var _gbFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});\n"
     "          var _gbFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P761 */"),
    ("var _gbR=_scoreRollBest(_gbFV,G.oCards,oppBank,crowsCtx,_gbFM);",
     "var _gbR=_scoreRollBest(_gbFV,G.oCards,oppBank,crowsCtx,_gbFM,_gbFE);"),
    ("var _stFM=G.oppDice.map(function(d){return d.mat;});",
     "var _stFM=G.oppDice.map(function(d){return d.mat;});\n"
     "          var _stFE=G.oppDice.map(function(d){return d.ench||null;});/* P761 */"),
    ("var _stR=_scoreRollBest(_stFV,G.oCards,oppBank,crowsCtx,_stFM);",
     "var _stR=_scoreRollBest(_stFV,G.oCards,oppBank,crowsCtx,_stFM,_stFE);"),
]
for old, new in PAIRS:
    sub(old, new, 'ench: ' + old[:32])

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# the MAIN scoring call - locate by pattern, since I have not read its exact
# line: find "_scoreRollBest(fV," occurrences and require the known shape
s = io.open(P, encoding='utf-8', newline='').read()
import re
main_calls = re.findall(r"_scoreRollBest\(fV,G\.oCards,oppBank,crowsCtx,fM\)", s)
if main_calls:
    # fE must exist beside fV/fM: find the fM construction
    fm = re.search(r"(var fM=G\.oppDice\.filter\(function\(d\)\{return !d\.kept;\}\)\.map\(function\(d\)\{return d\.mat;\}\);)", s)
    if not fm:
        sys.exit('main fM construction not found (partial write!)')
    s = s.replace(fm.group(1),
                  fm.group(1) + "\n      var fE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P761 */",
                  1)
    s = s.replace("_scoreRollBest(fV,G.oCards,oppBank,crowsCtx,fM)",
                  "_scoreRollBest(fV,G.oCards,oppBank,crowsCtx,fM,fE)")
    edits.append('main scoring call carries ench (x%d)' % len(main_calls))
io.open(P, 'w', encoding='utf-8', newline='').write(s)

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
