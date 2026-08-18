# -*- coding: utf-8 -*-
"""P764: the commit-seam passives go symmetric; honeytrap becomes the
PLAYER'S card in the rival's hand.

- bloom / cultivate / vanguard_f: their seam (famCommitBonus) already
  fires for both actors with the payload derived per seat - only the
  _fxMine gate kept them player-only. ev.mine now. Cultivate's growth
  store is per-seat (G._cultArr / G._oCultArr - lanes are per-seat
  identities); the player's FEAT counters stay player-only (feats are
  the player's ledger, not an effect).

- honeytrap: the rival's bespoke version was a DIFFERENT CARD - a
  random modal-face pull with no pair requirement. Under Denis's ruling
  they play the player's: armed on a pair from _tablePairs(actor) (the
  shared view), their next deal pulls one fresh die to the pair value
  through the mirror of the player's consumption line, guaranteed
  triple. The lever arms it when they hold a pair and push. The bespoke
  block is deleted.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the shared views take the actor everywhere ──
sub("""function _tablePairs(){
  var seen={},out=[],all=_tableDice();""",
    """function _tablePairs(actor){
  var seen={},out=[],all=_tableDice(actor);""",
    'pairs view takes the actor')

# ── 2. bloom ──
sub("""CFX.bloom={
  commit:function(ev){if(!_fxMine(ev)||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    ev.add(ev.P);_famPop('+'+ev.P+' BLOOM');
    G._featBloom=(G._featBloom||0)+1;/* FULL BLOOM */}
};""",
    """/* P764: SYMMETRIC - the seam already derives the payload per seat;
   only the gate was player-only. Feats stay the player's ledger. */
CFX.bloom={
  commit:function(ev){if(!ev.mine||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    ev.add(ev.P);
    if(ev.owner==='p'){_famPop('+'+ev.P+' BLOOM');
      G._featBloom=(G._featBloom||0)+1;/* FULL BLOOM */}
    else setStatusMsg('THEIR JADE BLOOMS — +'+ev.P,'red');}
};""",
    'bloom symmetric')

# ── 3. cultivate: per-seat growth store ──
sub("""  commit:function(ev){if(!_fxMine(ev)||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    var grown=0;
    G._cultArr=G._cultArr||[];
    ev.jade.forEach(function(d){
      var L=d.lane;
      if(typeof L!=='number'||!(L>=0))return;/* NaN fails >=0, unlike <0 */
      grown+=(G._cultArr[L]||0);
      G._cultArr[L]=(G._cultArr[L]||0)+50;
    });
    if(grown>0){ev.add(grown);_famPop('+'+grown+' CULTIVATE');}
    else _famPop('CULTIVATE GROWS');}
};""",
    """  commit:function(ev){if(!ev.mine||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    /* P764: the growth store is PER SEAT - lanes are per-seat identities,
       so one array would grow the player's dice off the rival's jade */
    var grown=0;
    var _arr=(ev.owner==='p')?(G._cultArr=G._cultArr||[]):(G._oCultArr=G._oCultArr||[]);
    ev.jade.forEach(function(d){
      var L=d.lane;
      if(typeof L!=='number'||!(L>=0))return;/* NaN fails >=0, unlike <0 */
      grown+=(_arr[L]||0);
      _arr[L]=(_arr[L]||0)+50;
    });
    if(ev.owner==='p'){
      if(grown>0){ev.add(grown);_famPop('+'+grown+' CULTIVATE');}
      else _famPop('CULTIVATE GROWS');
    }else{
      if(grown>0){ev.add(grown);setStatusMsg('THEIR JADE GROWS — +'+grown,'red');}
    }}
};""",
    'cultivate per-seat store')

# ── 4. vanguard ──
sub("""  commit:function(ev){if(!_fxMine(ev))return;
    var vb=0,t=ev.me.tier;
    if(t===1){if(ev.hitFirst)vb=200;}
    else if(t===2){if(ev.hitFirst)vb+=350;if(ev.hitLast)vb+=350;}
    else{if(ev.hitFirst&&ev.hitLast)vb=1200;else if(ev.hitFirst||ev.hitLast)vb=350;}
    if(vb>0){ev.add(vb);_famPop('+'+vb+' VANGUARD');}}
};""",
    """  commit:function(ev){if(!ev.mine)return;/* P764: either seat */
    var vb=0,t=ev.me.tier;
    if(t===1){if(ev.hitFirst)vb=200;}
    else if(t===2){if(ev.hitFirst)vb+=350;if(ev.hitLast)vb+=350;}
    else{if(ev.hitFirst&&ev.hitLast)vb=1200;else if(ev.hitFirst||ev.hitLast)vb=350;}
    if(vb>0){ev.add(vb);
      if(ev.owner==='p')_famPop('+'+vb+' VANGUARD');
      else setStatusMsg('THEIR VANGUARD — +'+vb,'red');}}
};""",
    'vanguard symmetric')

# ── 5. honeytrap: one card, two seats ──
sub("""CFX.honeytrap={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('pair');/* P738: the shared view */
  },
  use:function(inst){
    var pairVal=_tablePairs()[0]||0;/* P738: intent order */
    if(!pairVal)return false;
    G._famHoneyVal=pairVal;
    famLog('HONEYTRAP SET — THE NEXT ROLL PULLS A '+pairVal);
    return true;
  }
};""",
    """/* P764: ONE CARD, TWO SEATS. The rival's old version was a different
   effect entirely (a random modal-face pull, no pair needed) - under
   the ruling they play the PLAYER'S card: a pair from the shared view
   arms it, the next deal pulls a die to the pair value. Same rule, the
   slot and the announce are the only per-seat parts. */
CFX.honeytrap={
  canUse:function(inst,actor){
    if(actor==='o')return !!(G&&!G._oHoneyVal&&_tablePairs('o')[0]);
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('pair');/* P738: the shared view */
  },
  use:function(inst,actor){
    var pairVal=_tablePairs(actor)[0]||0;/* P738: intent order */
    if(!pairVal)return false;
    if(actor==='o'){
      G._oHoneyVal=pairVal;
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+': HONEYTRAP — THEIR NEXT ROLL PULLS A '+pairVal,'red');
    }else{
      G._famHoneyVal=pairVal;
      famLog('HONEYTRAP SET — THE NEXT ROLL PULLS A '+pairVal);
    }
    return true;
  }
};""",
    'honeytrap both seats')

# ── 6. their deal consumes it - the mirror of the player's line ──
sub("""    sootyActive=false;""",
    """    sootyActive=false;
    /* P764: HONEYTRAP LANDS - the mirror of the player's consumption
       (handleRoll ~16948): one fresh die is pulled to the armed value.
       Spent by this roll either way, exactly like the player's. */
    if(G._oHoneyVal){
      var _htFresh=G.oppDice.filter(function(d){return !d.kept;});
      if(_htFresh.length){
        var _htD=_htFresh[0];_htD.val=G._oHoneyVal;
        try{reDrawDieFace(_htD);}catch(e){}
        setStatusMsg(G.rung.name+': HONEYTRAP → '+G._oHoneyVal,'red');
      }
      G._oHoneyVal=null;
    }""",
    'their deal consumes the trap')

# ── 7. the bespoke pull dies; the lever arms at the push ──
sub("""    /* BULLISH honeytrap: pull one fresh die into the modal face (P5/P9) */
    (function(){
      var c=_npcFamCard('honeytrap');
      if(!c||oppRollNum<2||Math.random()>=0.5)return;
      var fresh=G.oppDice.filter(function(d){return !d.kept;});
      if(fresh.length<3)return;
      var cnt={};fresh.forEach(function(d){cnt[d.val]=(cnt[d.val]||0)+1;});
      var modal=Object.keys(cnt).sort(function(a,b){return cnt[b]-cnt[a];})[0];
      var vic=fresh.filter(function(d){return d.val!==Number(modal);})[0];
      if(!vic)return;
      c.charges--;vic.val=Number(modal);try{reDrawDieFace(vic);}catch(e){}
      setStatusMsg(G.rung.name+': HONEYTRAP — A DIE IS PULLED TO '+modal,'red');
    })();""",
    """    /* P764: the bespoke 'modal-face pull' honeytrap is DELETED - it was
       a different card wearing the same name. The rival plays the
       player's honeytrap now: armed at the push decision (the lever,
       below in step()), consumed by the deal above. */""",
    'bespoke pull deleted')

sub("""      setTimeout(()=>{if(bank)finOpp(oppBank);else step();},_oppDelay(1900));""",
    """      /* P764: THE HONEYTRAP LEVER - pushing with a pair on the table is
         the card's moment (the player's rule: pair armed, next roll
         pulls the third). famUse('o') is the how. */
      if(!bank&&!G._oHoneyVal){
        try{
          if(_tablePairs('o')[0]){
            var _htIx=-1;
            (G.oF||[]).some(function(o,ix){
              if(o.id==='honeytrap'&&!o.broken&&o.charges>0){_htIx=ix;return true;}
              return false;
            });
            if(_htIx>=0)famUse(_htIx,'o');
          }
        }catch(e){}
      }
      setTimeout(()=>{if(bank)finOpp(oppBank);else step();},_oppDelay(1900));""",
    'the honeytrap lever')

# ── 8. the registry grows ──
sub("var NPC_FAM_READY={preserve:1,double_or_nothing:1};",
    "var NPC_FAM_READY={preserve:1,double_or_nothing:1,honeytrap:1};",
    'registry grows')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
