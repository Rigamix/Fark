# -*- coding: utf-8 -*-
"""P762: the passive hooks go symmetric - and the rival's bankBonus seam
was discarding every delta.

Denis: "they should be able to use ALL of the same things I can use,
cards, enchants, etc. Not just a few." The pipe (P761) is the mechanism;
this is the sweep continuing through the bank/roll passives - the ones
whose seams already fire on the rival's turn, so ungating them is real
today, not aspirational.

FOUND ON THE WAY, a live parity bug: the player's bank seam consumes
famFire's returned delta BEFORE adding (`total+=famFire('bankBonus',...)`)
- the rival's fired it AFTER `G.oPts+=pts` and threw the return away. Any
bankBonus card the rival ever held was silently void. The rival seam now
mirrors the player's exactly: delta consumed into pts, then banked.

MIGRATED (bespoke copies deleted in the same move - the double-fire trap
docs/P5_NPC_CARDS.md warned about):
  slow_cook          roll-accumulator per owner (ev.rollNum from the
                     rival's seam, G.turnRollCount for the player's),
                     resets on the OWNER's turnStart/bust (ev.mine)
  pickpocket         the actor's bank lifts from the OTHER seat
  double_or_nothing  armed through famUse('o') at turn start when
                     trailing >=1000 (the lever); the flip resolves at
                     their bank through the same hook as the player's,
                     pool chosen by owner

Also: the enchant thread reaches the three scoring sites P761 missed
(fog - spliced in parallel with vals/mats; encore reroll; bust-rescue
rescore)."""
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


# ── 0. the rival bankBonus seam consumes its delta, like the player's ──
sub("""      else{G.oPts+=pts;_npcActuallyBanked=true;famFire('bankBonus',{actor:'o',amt:pts});setStatusMsg((G.rung?G.rung.name:'RIVAL')+' BANKED '+pts.toLocaleString(),'active');if(window.DLG&&pts>=600)DLG.trigger('OPP_BIG_BANK');}""",
    """      else{
        /* P762: CONSUME THE DELTA, like the player's seam at handleBank -
           this fired AFTER the add and discarded famFire's return, so a
           rival-owned bankBonus card (slow_cook's simmer, any future one)
           was silently void. Delta first, then the bank. */
        pts+=famFire('bankBonus',{actor:'o',amt:pts,total:pts});
        G.oPts+=pts;_npcActuallyBanked=true;setStatusMsg((G.rung?G.rung.name:'RIVAL')+' BANKED '+pts.toLocaleString(),'active');if(window.DLG&&pts>=600)DLG.trigger('OPP_BIG_BANK');}""",
    'rival seam consumes delta')

# ── 1. slow_cook: per-owner accumulator ──
sub("""CFX.slow_cook={
  roll:function(ev){if(!_fxMine(ev))return;
    if((G.turnRollCount||0)>=3){ev.me.state.acc=(ev.me.state.acc||0)+ev.P;_famPop('+'+ev.P+' SLOW COOK');}},
  bankBonus:function(ev){if(!_fxMine(ev))return;
    var a=ev.me.state.acc||0;if(a>0){ev.add(a);famLog('SLOW COOK +'+a);}ev.me.state.acc=0;},
  /* `ev.owner==='p'` ALONE, not _fxMine - and the difference is real, not a
     spelling. ev.mine is (ev.actor===owner), so this ALSO fires when the RIVAL
     is the actor: the accumulator resets on their turn start as well as yours.
     Left exactly as it was. Whether that is intended (reset before your turn,
     whoever triggered it) or an oversight is a BEHAVIOUR question, and
     unifying the two spellings would have answered it silently in whichever
     direction the shared helper happened to pick. Same shape as short_fuse's
     turnStart and slow_cook's bust below. */
  turnStart:function(ev){if(ev.owner==='p')ev.me.state.acc=0;},
  bust:function(ev){if(ev.owner==='p')ev.me.state.acc=0;}
};""",
    """/* P762: SYMMETRIC. One pot, either side of the table. The roll count
   comes from the event when the caller has its own (the rival's seam
   passes oppRollNum) and from G.turnRollCount for the player's. The
   accumulator resets on the OWNER's turnStart and bust - for a player
   instance that is the same moments as before (acc is only ever fed on
   the player's own rolls and drained at their bank), so the visible
   behaviour is unchanged; for a rival instance it is the mirror. The
   bespoke finOpp copy ((oppRollNum-2)*P at bank - the same sum this
   accumulates roll by roll) is deleted in this patch. */
CFX.slow_cook={
  roll:function(ev){if(!ev.mine)return;
    var rc=(ev.rollNum!=null)?ev.rollNum:(G.turnRollCount||0);
    if(rc>=3){ev.me.state.acc=(ev.me.state.acc||0)+ev.P;
      if(ev.owner==='p')_famPop('+'+ev.P+' SLOW COOK');}},
  bankBonus:function(ev){if(!ev.mine)return;
    var a=ev.me.state.acc||0;
    if(a>0){ev.add(a);
      if(ev.owner==='p')famLog('SLOW COOK +'+a);
      else setStatusMsg('THEIR POT SIMMERS — +'+a+' SLOW COOK','red');}
    ev.me.state.acc=0;},
  turnStart:function(ev){if(ev.mine)ev.me.state.acc=0;},
  bust:function(ev){if(ev.mine)ev.me.state.acc=0;}
};""",
    'slow_cook symmetric')

sub("""    try{famFire('roll',{actor:'o'});}catch(e){}""",
    """    try{famFire('roll',{actor:'o',rollNum:oppRollNum});}catch(e){}/* P762 */""",
    'rival roll seam carries its count')

# ── 2. pickpocket: the actor lifts from the other seat ──
sub("""CFX.pickpocket={
  bank:function(ev){if(!_fxMine(ev))return;
    var lift=Math.min(ev.P,G.oPts);
    if(lift>0){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);
      cardFx('steal',{row:'oppDice'},{to:{row:'score'}});
      try{updHUD();}catch(e){}}}
};""",
    """/* P762: SYMMETRIC - whoever banks, their fingers find the OTHER purse.
   The bespoke finOpp copy is deleted in this patch. */
CFX.pickpocket={
  bank:function(ev){if(!ev.mine)return;
    var _meP=(ev.owner==='p');
    var lift=Math.min(ev.P,_meP?G.oPts:G.pPts);
    if(lift>0){
      if(_meP){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}
      else{G.pPts-=lift;G.oPts+=lift;
        setStatusMsg('THEIR FINGERS — '+lift+' LIFTED FROM YOU','red');}
      try{updHUD();}catch(e){}}}
};""",
    'pickpocket symmetric')

# ── 3. double_or_nothing: one flip, owner's pool ──
sub("""CFX.double_or_nothing={
  canUse:function(inst){return G&&(G.phase==='choosing'||G.phase==='idle')&&!inst.state.armed;},
  use:function(inst){inst.state.armed=true;famLog('DOUBLE OR NOTHING ARMED — NEXT BANK FLIPS');return true;},
  bank:function(ev){if(!_fxMine(ev)||!ev.me.state.armed)return;
    ev.me.state.armed=false;
    var winFlip=Math.random()<0.5;
    if(winFlip){G.pPts+=ev.amt;famLog('THE FLIP LANDS — BANK DOUBLED (+'+ev.amt+')');_famPop('x2 BANK');}
    else{var lose=Math.round(ev.amt*ev.P);G.pPts=Math.max(0,G.pPts-lose);famLog('THE FLIP FAILS — '+lose+' GONE');_famPop('-'+lose);}
    try{updHUD();}catch(e){}}
};""",
    """/* P762: SYMMETRIC - the flip is the flip; only the pool differs by
   owner. The rival arms it through famUse('o') at turn start when
   trailing (the lever in _npcArmActives); the bespoke finOpp flip is
   deleted in this patch. */
CFX.double_or_nothing={
  canUse:function(inst,actor){
    if(actor==='o')return !!(G&&!inst.state.armed);
    return G&&(G.phase==='choosing'||G.phase==='idle')&&!inst.state.armed;},
  use:function(inst,actor){
    inst.state.armed=true;
    if(actor==='o')setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' ARMS DOUBLE OR NOTHING','red');
    else famLog('DOUBLE OR NOTHING ARMED — NEXT BANK FLIPS');
    return true;},
  bank:function(ev){if(!ev.mine||!ev.me.state.armed)return;
    ev.me.state.armed=false;
    var _meP=(ev.owner==='p');
    var winFlip=Math.random()<0.5;
    if(winFlip){
      if(_meP){G.pPts+=ev.amt;famLog('THE FLIP LANDS — BANK DOUBLED (+'+ev.amt+')');_famPop('x2 BANK');}
      else{G.oPts+=ev.amt;setStatusMsg('THEY FLIP — DOUBLE ('+(ev.amt*2)+')','red');}
    }else{
      var lose=Math.round(ev.amt*ev.P);
      if(_meP){G.pPts=Math.max(0,G.pPts-lose);famLog('THE FLIP FAILS — '+lose+' GONE');_famPop('-'+lose);}
      else{G.oPts=Math.max(0,G.oPts-lose);setStatusMsg('THEY FLIP AND LOSE — '+lose+' GONE','gold');}
    }
    try{updHUD();}catch(e){}}
};""",
    'double_or_nothing symmetric')

# ── 4. the registry grows; the levers move to the pipe ──
sub("var NPC_FAM_READY={preserve:1};",
    "var NPC_FAM_READY={preserve:1,double_or_nothing:1};",
    'registry grows')

sub("""  /* CUNNING: sleight when trailing a strong player */""",
    """  /* P762: DOUBLE OR NOTHING through the pipe - the lever is the when
     (trailing by 1000+), famUse('o') is the how, and the flip itself is
     the same CFX hook the player's card resolves through. */
  (function(){
    if((G.pPts-G.oPts)>=1000){
      var _dnIx=-1;
      (G.oF||[]).some(function(o,ix){
        if(o.id==='double_or_nothing'&&!o.broken&&o.charges>0&&!o.state.armed){_dnIx=ix;return true;}
        return false;
      });
      if(_dnIx>=0)famUse(_dnIx,'o');
    }
  })();
  /* CUNNING: sleight when trailing a strong player */""",
    'double-or-nothing lever')

# ── 5. the bespoke copies die ──
sub("""      if(pts>0&&(c=_npcFamCard('slow_cook'))&&oppRollNum>2){
        var sb=(oppRollNum-2)*famDef('slow_cook').p[c.tier-1];pts+=sb;
        setStatusMsg('THEIR POT SIMMERS — +'+sb+' SLOW COOK','red');
      }
      if(pts>0&&(c=_npcFamCard('double_or_nothing'))&&(G.pPts-G.oPts)>=1000){
        c.charges--;
        if(Math.random()<0.5){pts*=2;setStatusMsg('THEY FLIP — DOUBLE ('+pts+')','red');}
        else{pts=Math.round(pts*(1-famDef('double_or_nothing').p[c.tier-1]));setStatusMsg('THEY FLIP AND LOSE — '+pts+' LEFT','gold');}
      }
      if(pts>0&&(c=_npcFamCard('pickpocket'))){
        var lift=Math.min(famDef('pickpocket').p[c.tier-1],G.pPts);
        if(lift>0){G.pPts-=lift;G.oPts+=lift;setStatusMsg('THEIR FINGERS — '+lift+' LIFTED FROM YOU','red');}
      }""",
    """      /* P762: slow_cook, double_or_nothing and pickpocket left this
         block for the shared CFX hooks - the same code the player's
         copies run, actor-routed. Keeping a copy here would fire them
         twice, the exact trap docs/P5_NPC_CARDS.md documented. */""",
    'bespoke trio deleted')

# ── 6. the enchant thread: the three remaining scoring sites ──
sub("""        if(_fi>=0&&_fogV.length>1){
          _fogV.splice(_fi,1);_fogM.splice(_fi,1);_fogCut=_fi;""",
    """        if(_fi>=0&&_fogV.length>1){
          _fogV.splice(_fi,1);_fogM.splice(_fi,1);if(_fogE)_fogE.splice(_fi,1);_fogCut=_fi;/* P762 */""",
    'fog splices ench')

i = s.find("var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM);")
if i < 0:
    o2 = "var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM);".replace('\n', '\r\n')
    i = s.find(o2)
if i < 0:
    sys.exit('fog scoring call not found (partial write!)')
s = s.replace("var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM);",
              "var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM,_fogE);/* P762 */")
edits.append('fog call carries ench')

# the free-list gains its ench array; the fog copies gain theirs
sub("""      const _oFree=G.oppDice.filter(d=>!d.kept);
      const fV=_oFree.map(d=>d.val);
      const fMats=_oFree.map(d=>d.mat);""",
    """      const _oFree=G.oppDice.filter(d=>!d.kept);
      const fV=_oFree.map(d=>d.val);
      const fMats=_oFree.map(d=>d.mat);
      const fEnchs=_oFree.map(d=>d.ench||null);/* P762: the brand scores */""",
    'free list carries ench')

sub("""      var _fogV=fV.slice(),_fogM=fMats.slice();""",
    """      var _fogV=fV.slice(),_fogM=fMats.slice(),_fogE=fEnchs.slice();/* P762 */""",
    'fog copies ench')

sub("""          var _encV=_encFree.map(function(d){return d.val;}),_encM=_encFree.map(function(d){return d.mat;});
          var _encRs=_scoreRollBest(_encV,G.oCards,oppBank,crowsCtx,_encM);""",
    """          var _encV=_encFree.map(function(d){return d.val;}),_encM=_encFree.map(function(d){return d.mat;});
          var _encE=_encFree.map(function(d){return d.ench||null;});/* P762 */
          var _encRs=_scoreRollBest(_encV,G.oCards,oppBank,crowsCtx,_encM,_encE);""",
    'encore carries ench')

sub("""            var _resFV=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.val;});
            var _resFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});
            var _resR=_scoreRollBest(_resFV,G.oCards,oppBank,crowsCtx,_resFM);""",
    """            var _resFV=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.val;});
            var _resFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});
            var _resFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P762 */
            var _resR=_scoreRollBest(_resFV,G.oCards,oppBank,crowsCtx,_resFM,_resFE);""",
    'rescue carries ench')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
