# -*- coding: utf-8 -*-
"""P765: retort, reprisal, short_fuse symmetric; encore through the pipe.

The sweep continues (Denis: "proceed with it all"). This batch is the
bust/bank passives whose seams fire on both sides, plus encore - whose
rival 'version' was a shared bespoke dodge with stargazer's name on it
half the time.

- retort: the owner's bust makes the OTHER side pay. Both bust seams
  fire; the rival's now carries `lost` like the player's.
- reprisal: the owner's bank steals when trailing; pools by owner.
- short_fuse: the only multiplier - lights from the owner's third roll
  (their roll count published as G._oRollNum), doubles their commits
  through the same ev.mul, and their bust burns their OWN bank pool.
- encore: use(inst,'o') rerolls THEIR free dice - the same effect as the
  player's proactive reroll; the rival's lever pulls it at a dead roll
  (their one chance to act), the turn code keeps its local rescore +
  persona continuation exactly as before. stargazer's bespoke dodge
  stays UNTIL Denis rules on Q2 (the faithful version is the peek).

NOT in this batch, awaiting rulings (asked in chat): sleight (Q1),
stargazer (Q2), ill_omen (Q3), falling_star (Q4), the rival-only
legacy roster (Q5).
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


# ── 0. the rival bust seam carries what was lost ──
sub("""        try{famFire('bust',{actor:'o'});}catch(e){}""",
    """        try{famFire('bust',{actor:'o',lost:oppBank});}catch(e){}/* P765: lost, like the player's seam */""",
    'rival bust carries lost')

# ── 1. retort ──
sub("""CFX.retort={
  bust:function(ev){if(!_fxMine(ev))return;
    G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);try{updHUD();}catch(e){}}
};""",
    """/* P765: SYMMETRIC - the owner's bust makes the OTHER side pay. */
CFX.retort={
  bust:function(ev){if(!ev.mine)return;
    if(ev.owner==='p'){G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);}
    else{G.pPts=Math.max(0,G.pPts-ev.P);setStatusMsg('THEIR RETORT — YOU LOSE '+ev.P,'red');}
    try{updHUD();}catch(e){}}
};""",
    'retort symmetric')

# ── 2. reprisal ──
sub("""CFX.reprisal={
  bank:function(ev){if(!_fxMine(ev))return;
    var trailing=(G.oPts-(G.pPts-ev.amt))>=1000; /* judged before this bank landed */
    if(!trailing)return;
    var steal=Math.min(Math.round(ev.amt*ev.P),G.oPts);
    if(steal>0){G.oPts-=steal;famLog('REPRISAL TAKES '+steal+' FROM THEM');try{updHUD();}catch(e){}}}
};""",
    """/* P765: SYMMETRIC - the owner banks while trailing, the leader bleeds. */
CFX.reprisal={
  bank:function(ev){if(!ev.mine)return;
    var _meP=(ev.owner==='p');
    /* judged before this bank landed, from the owner's side of the table */
    var trailing=_meP?((G.oPts-(G.pPts-ev.amt))>=1000)
                     :((G.pPts-(G.oPts-ev.amt))>=1000);
    if(!trailing)return;
    var steal=Math.min(Math.round(ev.amt*ev.P),_meP?G.oPts:G.pPts);
    if(steal>0){
      if(_meP){G.oPts-=steal;G.pPts+=steal;famLog('REPRISAL TAKES '+steal+' FROM THEM');}
      else{G.pPts-=steal;G.oPts+=steal;setStatusMsg('THEIR REPRISAL — '+steal+' TAKEN FROM YOU','red');}
      try{updHUD();}catch(e){}}}
};""",
    'reprisal symmetric')

# ── 3. short_fuse ──
sub("""CFX.short_fuse={
  /* THE ONLY MULTIPLIER IN THE GAME so far, and the reason ev.mul exists. */
  commit:function(ev){if(!_fxMine(ev)||(G.turnRollCount||0)<3)return;
    ev.mul(2);ev.me.state.lit=true;_famPop('x2 SHORT FUSE');},
  turnStart:function(ev){if(ev.owner==='p')ev.me.state.lit=false;},
  /* the three jade/positional adders that used to sit in famCommitBonus.
     Each keeps its own gate verbatim - they are NOT one condition. */
  bust:function(ev){if(!_fxMine(ev)||!ev.me.state.lit)return;
    var burn=ev.lost||0;
    if(burn>0){G.pPts=Math.max(0,G.pPts-burn);famLog('THE FIRE SPREADS — '+burn+' BURNS OFF YOUR BANK');try{updHUD();}catch(e){}}
    ev.me.state.lit=false;}
};""",
    """/* P765: SYMMETRIC. The fuse lights from the OWNER's third roll (the
   rival's count is published as G._oRollNum), doubles their commits
   through the same ev.mul, and a lit bust burns the OWNER's own bank. */
CFX.short_fuse={
  /* THE ONLY MULTIPLIER IN THE GAME so far, and the reason ev.mul exists. */
  commit:function(ev){if(!ev.mine)return;
    var rc=(ev.owner==='p')?(G.turnRollCount||0):(G._oRollNum||0);
    if(rc<3)return;
    ev.mul(2);ev.me.state.lit=true;
    if(ev.owner==='p')_famPop('x2 SHORT FUSE');
    else setStatusMsg('THEIR FUSE BURNS — x2','red');},
  turnStart:function(ev){if(ev.mine)ev.me.state.lit=false;},
  /* the three jade/positional adders that used to sit in famCommitBonus.
     Each keeps its own gate verbatim - they are NOT one condition. */
  bust:function(ev){if(!ev.mine||!ev.me.state.lit)return;
    var burn=ev.lost||0;
    if(burn>0){
      if(ev.owner==='p'){G.pPts=Math.max(0,G.pPts-burn);famLog('THE FIRE SPREADS — '+burn+' BURNS OFF YOUR BANK');}
      else{G.oPts=Math.max(0,G.oPts-burn);setStatusMsg('THE FIRE SPREADS — '+burn+' BURNS OFF THEIR BANK','gold');}
      try{updHUD();}catch(e){}}
    ev.me.state.lit=false;}
};""",
    'short_fuse symmetric')

# publish their roll count where oppRollNum ticks
sub("""    _oppHoldKept();oppRollNum++;""",
    """    _oppHoldKept();oppRollNum++;G._oRollNum=oppRollNum;/* P765: short_fuse reads the owner's count */""",
    'their roll count published')

# ── 4. encore through the pipe at the dodge ──
sub("""CFX.encore={
  /* NOT WHILE ITS OWN REROLL IS RESOLVING. use() schedules the scoring check
     500ms out and used to leave the phase at 'choosing' the whole time, so
     canUse said yes again and a second play queued a SECOND check against the
     same dice: doBust ran twice, famFire('bust') twice, two of the player's
     eight turns burned in one go, and Retort fired twice off the one bust. */
  canUse:function(inst){return G&&G.phase==='choosing'&&!G._encorePending
    &&G.pool&&G.pool.some(function(d){return !d.committed;});},
  use:function(inst){""",
    """CFX.encore={
  /* NOT WHILE ITS OWN REROLL IS RESOLVING. use() schedules the scoring check
     500ms out and used to leave the phase at 'choosing' the whole time, so
     canUse said yes again and a second play queued a SECOND check against the
     same dice: doBust ran twice, famFire('bust') twice, two of the player's
     eight turns burned in one go, and Retort fired twice off the one bust. */
  canUse:function(inst,actor){
    /* P765: the rival's reading - free dice on their table. The LEVER
       decides the moment (their dead roll); this only says it is legal. */
    if(actor==='o')return !!(G&&(G.oppDice||[]).some(function(d){return !d.kept;}));
    return G&&G.phase==='choosing'&&!G._encorePending
    &&G.pool&&G.pool.some(function(d){return !d.committed;});},
  use:function(inst,actor){
    /* P765: THE SAME EFFECT - reroll the owner's free dice. The rival's
       continuation (rescore, persona re-pick) lives with their turn
       code, exactly as the player's bust-check lives with theirs. */
    if(actor==='o'){
      var _oFree2=(G.oppDice||[]).filter(function(d){return !d.kept;});
      if(!_oFree2.length)return false;
      _oFree2.forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+': ENCORE — THEY ROLL AGAIN','red');
      return true;
    }""",
    'encore both seats')

sub("""        var _oEnc=_npcFamCard('encore')||_npcFamCard('stargazer');
        if(_oEnc){
          _oEnc.charges--;
          var _encFree=G.oppDice.filter(function(d){return !d.kept;});
          _encFree.forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
          setStatusMsg(G.rung.name+': '+(_oEnc.id==='encore'?'ENCORE':'THE OMEN')+' — THEY ROLL AGAIN','red');""",
    """        /* P765: ENCORE THROUGH THE PIPE - the lever is 'my roll died',
           famUse('o') is the how, the reroll is CFX.encore's own body.
           stargazer's dodge stays bespoke pending Denis's Q2 ruling
           (the faithful version is the peek, a different build). */
        var _oEnc=null,_encIx=-1;
        (G.oF||[]).some(function(o,ix){
          if(o.id==='encore'&&!o.broken&&o.charges>0){_encIx=ix;_oEnc=o;return true;}
          return false;
        });
        if(_encIx>=0){
          var _encB4=_oEnc.charges;
          famUse(_encIx,'o');
          if(_oEnc.charges===_encB4)_oEnc=null;/* refused - fall through */
        }
        if(!_oEnc)_oEnc=_npcFamCard('stargazer');
        if(_oEnc&&_oEnc.id==='stargazer'){
          _oEnc.charges--;
          G.oppDice.filter(function(d){return !d.kept;})
            .forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
          setStatusMsg(G.rung.name+': THE OMEN — THEY ROLL AGAIN','red');
        }
        /* the continuation below reads _encFree - the same objects the
           reroll just mutated, so mapping now reads the NEW faces */
        var _encFree=G.oppDice.filter(function(d){return !d.kept;});
        if(_oEnc){""",
    'encore lever at the dodge')

sub("var NPC_FAM_READY={preserve:1,double_or_nothing:1,honeytrap:1};",
    "var NPC_FAM_READY={preserve:1,double_or_nothing:1,honeytrap:1,encore:1};",
    'registry grows')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
