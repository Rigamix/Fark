# -*- coding: utf-8 -*-
"""P766: Denis's four rulings land - sleight resurrected both ways,
stargazer becomes the peek, ill_omen mirrors, falling_star grants THEM
the extra turn (flagged for the retune batch).

Q1 SLEIGHT (a): the player's half is BUILT - their first roll of the
   turn comes back different, the mirror of _afterRollImpl's rival
   version - and the card is un-retired from the player's draft. The
   rival's arm goes through famUse('o'); the bespoke arm block dies.

Q2 STARGAZER: the bespoke bust-dodge dies (it was a different card
   wearing the name - the honeytrap disease). The faithful card: they
   READ their next roll (values pre-rolled for exactly the seats the
   next deal will fill), and the AI plays with the knowledge - a dead
   roll foreseen turns the push into a bank, in the open. A scoring
   peek rides to the deal and IS the roll, the mirror of the player's
   famApplyRollForces contract (spent whether or not it lands).

Q3 ILL_OMEN: one hook, both owners - ev.mine on the rivalTurn seam that
   already fires both ways. Exactly the player's numbers upside down,
   minting included (the old bespoke consumer took capped-only; the
   P708 minting rule now applies to their side too, which is the
   ruling's 'same numbers' made true). Bespoke arm + bespoke endPTurn
   consumer both die.

Q4 FALLING_STAR: the rival's big bank sets G._oExtraTurn; the normal
   finOpp handoff consumes it - THEY GO AGAIN instead of passing the
   table. RETUNE FLAG: shipped loud per the ruling, difficulty to be
   measured once live, not assumed.
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


# ═══ Q1: SLEIGHT ═══
sub("""CFX.sleight={
  canUse:function(){return G&&G.phase!=='opp'&&!G._famSleight;},
  use:function(inst){
    G._famSleight=true;
    famLog('SLEIGHT READY — THEIR NEXT ROLL COMES BACK');
    cardFx('churn',{row:'oppDice'});
    return true;
  }
};""",
    """/* P766 (Q1 ruling a): RESURRECTED BOTH WAYS. The player's half was
   never built (retired as 'inert'); the rival's proved the design. One
   card now: either owner arms it, the OTHER side's next first roll
   comes back different - the player's consumer is in _afterRollImpl,
   the rival's is at their deal. */
CFX.sleight={
  canUse:function(inst,actor){
    if(actor==='o')return !!(G&&!G._oSleight);
    return G&&G.phase!=='opp'&&!G._famSleight;},
  use:function(inst,actor){
    if(actor==='o'){
      G._oSleight=true;
      famLog((G.rung&&G.rung.name||'RIVAL')+' FINGERS A CARD — SLEIGHT. YOUR NEXT ROLL COMES BACK','red');
      return true;
    }
    G._famSleight=true;
    famLog('SLEIGHT READY — THEIR NEXT ROLL COMES BACK');
    cardFx('churn',{row:'oppDice'});
    return true;
  }
};""",
    'sleight both seats')

sub("var FAM_PLAYER_RETIRED={sleight:1};",
    """/* P766 (Q1): sleight is UN-RETIRED - it was parked because the player
   half was broken, not because the design was; the half is built now. */
var FAM_PLAYER_RETIRED={};""",
    'sleight un-retired')

sub("""  /* CUNNING: sleight when trailing a strong player */
  if((c=_npcFamCard('sleight'))&&!G._oSleight&&(G.pPts-G.oPts)>=800){
    c.charges--;G._oSleight=true;
    famLog(G.rung.name+' FINGERS A CARD — SLEIGHT. YOUR NEXT ROLL COMES BACK','red');
  }""",
    """  /* P766: SLEIGHT through the pipe - the lever is the when (trailing a
     strong player), famUse('o') is the how. */
  if(!G._oSleight&&(G.pPts-G.oPts)>=800){
    var _slIx=-1;
    (G.oF||[]).some(function(o,ix){
      if(o.id==='sleight'&&!o.broken&&o.charges>0){_slIx=ix;return true;}
      return false;
    });
    if(_slIx>=0)famUse(_slIx,'o');
  }""",
    'sleight lever')

# ═══ Q2: STARGAZER ═══
sub("""CFX.stargazer={
  canUse:function(){return G&&G.phase==='choosing';},
  use:function(inst){
    var free=G.pool.filter(function(d){return !d.committed&&!d._frozen;});""",
    """/* P766 (Q2): ONE CARD - the peek - both seats. The rival's version is
   the same read: values pre-rolled for exactly the seats their next
   deal will fill; the AI then plays WITH the knowledge (the lever banks
   a foreseen dead roll, in the open). The bust-dodge that wore this
   card's name is deleted. */
CFX.stargazer={
  canUse:function(inst,actor){
    if(actor==='o')return !!(G&&!G._oPeekVals);
    return G&&G.phase==='choosing';},
  use:function(inst,actor){
    if(actor==='o'){
      var _all=(G.matchOppDice&&G.matchOppDice.length)?G.matchOppDice.length:6;
      var _hl={};
      (G._oppHeld||[]).forEach(function(d){if(d.lane!==undefined)_hl[d.lane]=1;});
      (G.oppDice||[]).forEach(function(d){if(d.kept&&d.lane!==undefined)_hl[d.lane]=1;});
      var _vals=[],_mats=[];
      for(var _si=0;_si<_all;_si++){
        if(_hl[_si]||_si===G._oSnuffLane)continue;
        var _m=(G.matchOppDice&&G.matchOppDice[_si])||'bone';
        _mats.push(_m);_vals.push(rollFace(_m));
      }
      if(!_vals.length)return false;
      G._oPeekVals=_vals;G._oPeekMats=_mats;
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' READS THE STARS','red');
      return true;
    }
    var free=G.pool.filter(function(d){return !d.committed&&!d._frozen;});""",
    'stargazer both seats')

sub("""        if(!_oEnc)_oEnc=_npcFamCard('stargazer');
        if(_oEnc&&_oEnc.id==='stargazer'){
          _oEnc.charges--;
          G.oppDice.filter(function(d){return !d.kept;})
            .forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
          setStatusMsg(G.rung.name+': THE OMEN — THEY ROLL AGAIN','red');
        }
        /* the continuation below reads _encFree - the same objects the
           reroll just mutated, so mapping now reads the NEW faces */""",
    """        /* P766 (Q2): the stargazer bust-dodge is DELETED - it was a
           different card wearing the name. The faithful stargazer (the
           peek) lives at the push decision now. */
        /* the continuation below reads _encFree - the same objects the
           reroll just mutated, so mapping now reads the NEW faces */""",
    'the dodge dies')

sub("""      /* P764: THE HONEYTRAP LEVER - pushing with a pair on the table is""",
    """      /* P766 (Q2): THE STARGAZER LEVER - pushing with the card charged,
         they read the stars first; a dead roll foreseen turns the push
         into a bank, announced, so the player can SEE the card work. */
      if(!bank&&!G._oPeekVals){
        var _sgIx=-1;
        (G.oF||[]).some(function(o,ix){
          if(o.id==='stargazer'&&!o.broken&&o.charges>0){_sgIx=ix;return true;}
          return false;
        });
        if(_sgIx>=0){
          famUse(_sgIx,'o');
          if(G._oPeekVals){
            var _sgR=null;
            try{_sgR=scoreRoll(G._oPeekVals,G.oCards,0,{},G._oPeekMats||[]);}catch(e){}
            if(!_sgR||!_sgR.total){
              bank=true;
              setStatusMsg('THE STARS WARN THEM — THEY BANK','red');
              /* the read was for THIS turn's next roll; banking ends the
                 turn, so the peek is spent unlanded - the same contract
                 as the player's roll-forces buffer */
              G._oPeekVals=null;G._oPeekMats=null;
            }
          }
        }
      }
      /* P764: THE HONEYTRAP LEVER - pushing with a pair on the table is""",
    'stargazer lever')

sub("""      const bank=(_pl&&_pl.verdict===true&&_pl.base===oppBank)
        ?true
        :oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);""",
    """      var bank=(_pl&&_pl.verdict===true&&_pl.base===oppBank)
        ?true
        :oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);/* P766: var - the stargazer lever may revise a push into a bank */""",
    'bank is revisable')

# their deal consumes sleight + the peek (before honeytrap, mirroring the
# player's ordering: sleight first, then the exact-values force)
sub("""    sootyActive=false;
    /* P764: HONEYTRAP LANDS""",
    """    sootyActive=false;
    /* P766 (Q1): SLEIGHT'S PLAYER HALF - their FIRST roll of the turn
       comes back different, the mirror of _afterRollImpl's rival side. */
    if(G._famSleight&&oppRollNum===1){
      G._famSleight=false;
      G.oppDice.filter(function(d){return !d.kept;})
        .forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
      setStatusMsg('SLEIGHT — THEIR ROLL COMES BACK DIFFERENT','gold');
    }
    /* P766 (Q2): STARGAZER LANDS - the peeked roll IS the roll, spent
       whether or not it fit (the player's famApplyRollForces contract). */
    if(G._oPeekVals){
      if(G._oPeekVals.length===_dealCount){
        for(var _pkI=0;_pkI<_dealCount;_pkI++){
          var _pkD=G.oppDice[G.oppDice.length-_dealCount+_pkI];
          if(_pkD){_pkD.val=G._oPeekVals[_pkI];try{reDrawDieFace(_pkD);}catch(e){}}
        }
      }
      G._oPeekVals=null;G._oPeekMats=null;
    }
    /* P764: HONEYTRAP LANDS""",
    'their deal consumes sleight + peek')

# ═══ Q3: ILL_OMEN ═══
sub("""CFX.ill_omen={
  /* declared on `use`, paid here, one rival turn later */
  rivalTurn:function(ev){if(!_fxMine(ev)||!G._famIllOmen)return;
    var _ioT=G._famIllOmen.tier||1,_ioP=famDef('ill_omen').p[_ioT-1];
    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;
      /* P708: a right call pays the FULL tier reward - what their board
         cannot fund is minted, exactly as the miss branch mints theirs.
         'YOU TAKE 0' on a first-turn bust was Denis's missing points. */
      G.pPts+=_ioP[0];
      G._featOmenTrue=true;/* OMENS TRUE */
      famLog('THE OMEN LANDS — YOU TAKE '+_ioP[0]);
      cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}
    else{G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);
      cardFx('hit',{row:'score'});}
    G._famIllOmen=null;try{updHUD();}catch(e){}},
  canUse:function(){return G&&G.phase!=='opp'&&!G._famIllOmen;},
  use:function(inst){
    G._famIllOmen={tier:inst.tier};""",
    """/* P766 (Q3): ONE HOOK, BOTH OWNERS - the rivalTurn seam already fires
   both ways ({actor:'p'} at finOpp, {actor:'o'} at endPTurn), so ev.mine
   is the whole routing. Exactly the player's numbers upside down,
   MINTING INCLUDED - the old bespoke consumer took capped-only, which
   was the drift the ruling closes. */
CFX.ill_omen={
  /* declared on `use`, paid here, one rival turn later */
  rivalTurn:function(ev){
    if(!ev.mine)return;
    var _meP=(ev.owner==='p');
    var _armed=_meP?G._famIllOmen:G._oIllOmen;
    if(!_armed)return;
    var _ioT=_armed.tier||1,_ioP=famDef('ill_omen').p[_ioT-1]||[0,0];
    if(ev.pts<=0){
      var take=Math.min(_ioP[0],_meP?G.oPts:G.pPts);
      if(_meP){G.oPts-=take;G.pPts+=_ioP[0];
        G._featOmenTrue=true;/* OMENS TRUE */
        famLog('THE OMEN LANDS — YOU TAKE '+_ioP[0]);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}
      else{G.pPts-=take;G.oPts+=_ioP[0];
        famLog('THEIR OMEN LANDS — THEY TAKE '+_ioP[0]);}
    }else{
      if(_meP){G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);
        cardFx('hit',{row:'score'});}
      else{G.pPts+=_ioP[1];famLog('THEIR OMEN MISSES — YOU GAIN '+_ioP[1]);}
    }
    if(_meP)G._famIllOmen=null;else G._oIllOmen=null;
    try{updHUD();}catch(e){}},
  canUse:function(inst,actor){
    if(actor==='o')return !!(G&&!G._oIllOmen);
    return G&&G.phase!=='opp'&&!G._famIllOmen;},
  use:function(inst,actor){
    if(actor==='o'){
      G._oIllOmen={tier:inst.tier};
      famLog((G.rung&&G.rung.name||'RIVAL')+' FINGERS A CARD — AN ILL OMEN. BUST NEXT TURN AND PAY','red');
      return true;
    }
    G._famIllOmen={tier:inst.tier};""",
    'ill_omen one hook')

# the bespoke endPTurn consumer dies (the hook pays now)
i = s.find("  if(G._oIllOmen){")
j = s.find("    G._oIllOmen=null;try{updHUD();}catch(e){}\n  }")
if j < 0:
    j = s.find("    G._oIllOmen=null;try{updHUD();}catch(e){}\r\n  }")
if i < 0 or j < 0 or j <= i:
    sys.exit('bespoke omen consumer not found (nothing written)')
j = s.find("}", j + 40) + 1 if False else j + len("    G._oIllOmen=null;try{updHUD();}catch(e){}\n  }")
BLOCK = s[i:j]
if 'THEIR OMEN LANDS' not in BLOCK or len(BLOCK) > 2400:
    sys.exit('bespoke omen block looks wrong (nothing written)')
s = s[:i] + (
    "  /* P766 (Q3): the bespoke omen consumer is DELETED - CFX.ill_omen's\n"
    "     one hook pays for both owners off the rivalTurn seam fired just\n"
    "     above, and keeping this copy would have paid the boss twice. */\n"
) + s[j:]
edits.append('bespoke omen consumer dies')

sub("""  /* STEADY: ill omen against a many-rolls player */
  if((c=_npcFamCard('ill_omen'))&&!G._oIllOmen&&(G._pLastRolls||0)>=3){
    c.charges--;G._oIllOmen={tier:c.tier};
    famLog(G.rung.name+' FINGERS A CARD — AN ILL OMEN. BUST NEXT TURN AND PAY','red');
  }""",
    """  /* P766: ILL OMEN through the pipe - the lever is the when (a
     many-rolls player), famUse('o') is the how. */
  if(!G._oIllOmen&&(G._pLastRolls||0)>=3){
    var _ioIx=-1;
    (G.oF||[]).some(function(o,ix){
      if(o.id==='ill_omen'&&!o.broken&&o.charges>0){_ioIx=ix;return true;}
      return false;
    });
    if(_ioIx>=0)famUse(_ioIx,'o');
  }""",
    'ill_omen lever')

# ═══ Q4: FALLING_STAR ═══
sub("""CFX.falling_star={
  bank:function(ev){if(!_fxMine(ev))return;
    if(ev.amt>=ev.P&&!G._fExtraTurn){G._fExtraTurn=true;
      G._featStarChain=(G._featStarChain||0)+1;/* WISH GRANTED */
      famLog('FALLING STAR — ANOTHER TURN COMES');}}
};""",
    """/* P766 (Q4): SYMMETRIC - a big enough bank buys another turn, either
   seat. RETUNE FLAG: the rival's half is parity, shipped loud - Denis:
   measure the difficulty once live, do not assume it either way. */
CFX.falling_star={
  bank:function(ev){if(!ev.mine||ev.amt<ev.P)return;
    if(ev.owner==='p'){
      if(!G._fExtraTurn){G._fExtraTurn=true;
        G._featStarChain=(G._featStarChain||0)+1;/* WISH GRANTED */
        famLog('FALLING STAR — ANOTHER TURN COMES');}
    }else{
      if(!G._oExtraTurn){G._oExtraTurn=true;
        setStatusMsg('FALLING STAR — THEY WILL GO AGAIN','red');}
    }}
};""",
    'falling_star symmetric')

sub("""  flashYourTurn();setTimeout(()=>{setTurnMode(false);startPTurn();},_oppDelay(800));
}
function endPTurn(){""",
    """  /* P766 (Q4): the rival's falling star - the mirror of endPTurn's
     player consumer, same target guards. They go again instead of
     passing the table. */
  if(G._oExtraTurn&&G.pPts<G.target&&G.oPts<G.target){
    G._oExtraTurn=false;
    setStatusMsg('FALLING STAR — '+(G.rung?G.rung.name:'THE RIVAL')+' GOES AGAIN','red');
    setTimeout(function(){runOppTurn();},_oppDelay(1100));
    return;
  }
  flashYourTurn();setTimeout(()=>{setTurnMode(false);startPTurn();},_oppDelay(800));
}
function endPTurn(){""",
    'they go again')

# ═══ the registry ═══
sub("var NPC_FAM_READY={preserve:1,double_or_nothing:1,honeytrap:1,encore:1};",
    "var NPC_FAM_READY={preserve:1,double_or_nothing:1,honeytrap:1,encore:1,sleight:1,stargazer:1,ill_omen:1};",
    'registry grows')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
