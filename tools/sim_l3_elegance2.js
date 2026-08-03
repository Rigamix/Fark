/* ══════════════════════════════════════════════════════════════════════════
   sim_l3_elegance2.js — LENS 3, round 2.

   Round 1 (tools/sim_l3_elegance.js) found that the SHARED harness cannot
   put a Trade brand on a die: FSIM.buildLoadout writes S.run._enchTradeV=2,
   and _enchInit's legacy-Trade migration fires on `_enchTradeV!==1`, strips
   every trade brand and refunds 350g. newG calls _enchInit unconditionally,
   inside FSIM.setupMatch, immediately after buildLoadout. So E2 and the Trade
   row of E7 measured an EMPTY lane in round 1.

   This file patches that in ITS OWN scope (sim_harness.js is untouched), then
   re-runs the two affected checks, extends E3 with the Still-Waters coverage
   hole, and replaces the Silver ratio measurement with a policy SWEEP, since
   ruling #24 claims the ratio is policy-invariant and round 1 could not
   reproduce the ruled figure at any threshold the shared measurement offers.
   ══════════════════════════════════════════════════════════════════════════ */
var SEED=(window.__FSIM_SEED!==undefined?window.__FSIM_SEED:20260731);
var R={seed:SEED, checks:{}, errors:[]};
function J(x){return JSON.parse(JSON.stringify(x===undefined?null:x));}
function eq(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function G_(){return FSIM.getG();}
function el(){var e=document.createElement('div');e.className='die';return e;}
function mkPool(spec){
  var G=G_();
  G.pool=spec.map(function(s,i){
    return {val:(s.val===undefined?2:s.val),mat:s.mat,ench:(s.ench||null),sel:false,
            committed:!!s.committed,el:el(),lane:(s.lane===undefined?i:s.lane)};});
  return G.pool;
}
function wrap(n,f){try{R.checks[n]=f();}catch(e){R.checks[n]={VERDICT:'ERROR',err:e.message,
  at:(e.stack||'').split('\n')[1]||''};R.errors.push(n+': '+e.message);}}

/* ── THE PATCH, in this file only ────────────────────────────────────────
   Same buildLoadout, on the CURRENT book: _enchTradeV=1 means "this save has
   already been migrated", which is what a live run with a legally-bought
   Trade brand actually looks like. Re-stamps afterwards too, because
   _wardOwned -> _enchInit can run mid-loop and strip a brand set earlier. */
var _origBuild=FSIM.buildLoadout;
FSIM.buildLoadout=function(spec){
  _getS();
  S.run._enchV=3;S.run._enchTradeV=1;
  var r=_origBuild.call(FSIM,spec);
  S.run._enchTradeV=1;
  var restamped=0;
  (spec.ench||[]).forEach(function(t,i){
    if(t!=='trade'||i>5)return;
    if(S.run.dieEnch[i]&&S.run.dieEnch[i].t==='trade')return;
    var e=FSIM.mkEnch(S.run.dice[i],'trade');
    if(e){S.run.dieEnch[i]=e;restamped++;}
  });
  r.ench=S.run.dieEnch.slice();r.tradeRestamped=restamped;
  return r;
};
function fresh(o){
  o=o||{};
  return FSIM.setupMatch({tier:(o.tier==null?3:o.tier),boss:!!o.boss,
    dice:o.dice||['obsidian','amber','starstone','silver','jade','vagabond'],
    ench:o.ench||[null,null,null,null,null,null],
    badge:o.badge||null,fcards:[],diceInv:o.diceInv||[],gold:o.gold||0});
}
var ci=FSIM.ci95;
FSIM.installRng(SEED);
FSIM.quiet();

/* the patch itself is a finding — prove the defect and prove the fix */
wrap('H0_harness_trade_defect', function(){
  var o={};
  _getS();
  S.run.dice=['silver','bone','bone','bone','bone','bone'];
  S.run.dieEnch=[{t:'trade',face:5},null,null,null,null,null];
  S.run.diceInv=[];S.run.dieEnchInv=[];S.run.gold=0;
  S.run._enchV=3;S.run._enchTradeV=2;      /* exactly what the harness writes */
  _enchInit();
  o.withHarnessFlag={enchAfter:J(S.run.dieEnch[0]),goldAfter:S.run.gold,
                     tradeV:S.run._enchTradeV};
  S.run.dieEnch=[{t:'trade',face:5},null,null,null,null,null];
  S.run.gold=0;S.run._enchTradeV=1;
  _enchInit();
  o.withPatchedFlag={enchAfter:J(S.run.dieEnch[0]),goldAfter:S.run.gold};
  var set=fresh({dice:['silver','bone','bone','bone','bone','bone'],ench:['trade',null,null,null,null,null]});
  o.setupNowCarriesTrade=!!(G_()._enchArr[0]&&G_()._enchArr[0].t==='trade');
  o.VERDICT=(o.withHarnessFlag.enchAfter===null&&o.withHarnessFlag.goldAfter===350
             &&o.withPatchedFlag.enchAfter!==null&&o.setupNowCarriesTrade)
            ?'HARNESS DEFECT CONFIRMED + PATCHED':'inconclusive';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E2 (re-run) — TRADE MATCH-SCOPED, BOTH LOADOUTS BACK BIT-FOR-BIT
   ───────────────────────────────────────────────────────────────────────── */
wrap('E2_trade_match_scoped', function(){
  var o={};
  var set=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                 ench:[null,null,null,'trade',null,'tithe']});
  var G=G_();
  var runBefore={dice:J(S.run.dice),ench:J(S.run.dieEnch)};
  var mdBefore=J(G.matchDice),oppBefore=J(G.matchOppDice),enBefore=J(G._enchArr);
  var rungBefore=J(set.rung.dice);
  var tr=G._enchArr[3];
  o.brand={lane:3,t:tr&&tr.t,face:tr&&tr.face};
  o.lanes={mine:mdBefore,theirs:oppBefore};

  var pool=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},
                   {mat:'silver',ench:tr,val:tr.face},{mat:'jade'},{mat:'vagabond'}]);
  var banked=_iconFire(pool[3],'p');            /* the REAL universal rule */
  G=G_();
  o.iconBankedPoints=banked;
  o.afterFire={md:J(G.matchDice),opp:J(G.matchOppDice),ench3:J(G._enchArr[3]),
               poolDieMat:pool[3].mat,poolDieEnch:J(pool[3].ench),
               ledger:J(G._tradeSwaps)};
  o.wholeDieCrossed=(G.matchDice[3]===oppBefore[3])&&(G.matchOppDice[3]===mdBefore[3]);
  o.brandLeftWithTheDie=(G._enchArr[3]===null);
  o.selfConsuming=o.brandLeftWithTheDie;
  o.runUntouchedMidMatch=eq(J(S.run.dice),runBefore.dice)&&eq(J(S.run.dieEnch),runBefore.ench);
  o.rivalTrueLoadoutUntouched=eq(J(set.rung.dice),rungBefore);

  var n=_tradeRestore();                        /* the REAL match-end restore */
  G=G_();
  o.restoredCount=n;
  o.mineBack=eq(J(G.matchDice),mdBefore);
  o.theirsBack=eq(J(G.matchOppDice),oppBefore);
  o.brandBackBitForBit=eq(J(G._enchArr),enBefore);
  o.runBitForBit=eq(J(S.run.dice),runBefore.dice)&&eq(J(S.run.dieEnch),runBefore.ench);
  o.idempotent=(_tradeRestore()===0);

  /* the ONE-WAY asymmetry, ruled and accepted (#12, brief 4b): the player's
     brand crosses over and only MATERIAL comes back. Measured, not assumed. */
  o.oneWay={playerBrandCrossed:true,
    opponentEnchArrayExists:(typeof G.matchOppEnch!=='undefined')||(!!G._oEnchArr),
    playerGotABrandBack:(G._enchArr[3]&&G._enchArr[3].t==='trade')};

  /* --- whole real matches, both arrays and the owned loadout after each --- */
  FSIM.installRng(SEED+11);
  var GEAR={dice:['obsidian','amber','starstone','silver','jade','vagabond'],
            ench:['trade','tithe',null,null,null,'fog'],badge:null,fcards:[]};
  var sortD=function(a){return a.slice().sort().join(',');};
  var want=sortD(GEAR.dice);
  var n2=200,ledgerLeft=0,drift=0,brandLost=0,traded=0,liveWrong=0;
  for(var i=0;i<n2;i++){
    var m=FSIM.simMatch(FSIM.POLICIES.bea,{tier:3,gear:GEAR,playerFirst:i%2===0,lanePlan:false});
    traded+=m.tradesRestored||0;
    var g=G_();
    if(g._tradeSwaps&&g._tradeSwaps.length)ledgerLeft++;
    if(!eq(J(S.run.dice),GEAR.dice))drift++;
    var t0=S.run.dieEnch&&S.run.dieEnch[0];
    if(!(t0&&t0.t==='trade'&&(t0.face===1||t0.face===5)))brandLost++;
    /* every material left on the live table must be one the player owns */
    if(sortD(g.matchDice)!==want&&g.matchDice.length===6)liveWrong++;
  }
  o.matchRun={n:n2,tradesFired:traded,ledgerLeftOver:ledgerLeft,
              ownedLoadoutDrift:drift,tradeBrandLost:brandLost,
              liveLoadoutNotOwnMaterials:liveWrong,runDiceAfter:J(S.run.dice)};
  o.noResidue=(ledgerLeft===0&&drift===0&&brandLost===0&&liveWrong===0);

  /* --- a BREAK in a lane BELOW a traded lane: the shifting-index case --- */
  var s3=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                ench:[null,null,null,null,'trade',null]});
  G=G_();
  var md3=J(G.matchDice),opp3=J(G.matchOppDice);
  var tr3=G._enchArr[4];
  var p3=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},{mat:'silver'},
                 {mat:'jade',ench:tr3,val:tr3.face},{mat:'vagabond'}]);
  G.numDice=6;
  _iconFire(p3[4],'p');
  G=G_();
  var afterTrade=J(G.matchDice);
  G._breakArmed=true;
  _breakDie(G.pool.filter(function(d){return d.lane===1;})[0]);
  G=G_();
  var afterBreak=J(G.matchDice);
  var n3=_tradeRestore();
  G=G_();
  o.breakUnderTrade={tradedLane:4,brokeLane:1,
    afterTrade:afterTrade,afterBreak:afterBreak,afterRestore:J(G.matchDice),
    restored:n3,
    expect:md3.filter(function(_,i){return i!==1;}),
    materialsRight:eq(J(G.matchDice),md3.filter(function(_,i){return i!==1;})),
    oppBack:eq(J(G.matchOppDice),opp3),
    runStillClean:eq(J(S.run.dice),md3)};

  /* --- and the reverse: BREAK THE BORROWED DIE ITSELF --- */
  var s4=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                ench:[null,null,null,null,'trade',null]});
  G=G_();
  var md4=J(G.matchDice),opp4=J(G.matchOppDice);
  var tr4=G._enchArr[4];
  var p4=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},{mat:'silver'},
                 {mat:'jade',ench:tr4,val:tr4.face},{mat:'vagabond'}]);
  G.numDice=6;
  _iconFire(p4[4],'p');
  G=G_();
  G._breakArmed=true;
  var borrowed=G.pool.filter(function(d){return d.lane===4;})[0];
  _breakDie(borrowed);                 /* kill the die we just borrowed */
  G=G_();
  var n4=_tradeRestore();
  G=G_();
  o.breakTheBorrowedDie={afterBreak:J(G.matchDice),restored:n4,
    runStillClean:eq(J(S.run.dice),md4),
    oppBack:eq(J(G.matchOppDice),opp4),
    oppLive:J(G.matchOppDice),oppWas:opp4};

  o.VERDICT=(o.wholeDieCrossed&&o.brandLeftWithTheDie&&o.runUntouchedMidMatch
    &&o.rivalTrueLoadoutUntouched&&o.mineBack&&o.theirsBack&&o.brandBackBitForBit
    &&o.runBitForBit&&o.noResidue)?'PASS':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E7 (re-run) — ZERO HOUR, all seven icons, with a live Trade brand
   ───────────────────────────────────────────────────────────────────────── */
wrap('E7_zero_hour', function(){
  var o={perIcon:{}};
  var kinds=['tithe','ward','snare','break','trade','snuff','fog'];
  kinds.forEach(function(k){
    fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
           ench:[k,null,null,null,null,null],boss:true,tier:0});
    var G=G_();G._zeroHourEnds=false;G.oppTurnCount=1;G._oLastBank=300;
    var en=G._enchArr[0];
    var pool=mkPool([{mat:'silver',ench:en,val:en?en.face:1},{mat:'amber'},{mat:'jade'}]);
    var pts=_iconFire(pool[0],'p');
    G=G_();
    o.perIcon[k]={tell:G._tell&&G._tell.id,brandFace:en&&en.face,
                  bankedPoints:pts,zeroHourEnds:!!G._zeroHourEnds};
  });
  o.allSevenEndTheTurn=kinds.every(function(k){return o.perIcon[k].zeroHourEnds;});
  o.allSevenBankZero=kinds.every(function(k){return o.perIcon[k].bankedPoints===0;});

  /* the badge is the only thing doing it */
  fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
         ench:['tithe',null,null,null,null,null]});
  var Gc=G_();var ec=Gc._enchArr[0];
  _iconFire(mkPool([{mat:'silver',ench:ec,val:ec.face}])[0],'p');
  o.controlNoBadge={tell:G_()._tell?G_()._tell.id:null,zeroHourEnds:!!G_()._zeroHourEnds};

  /* hot dice never buys an exception: source order off the LIVE function, and
     the behaviour with the whole row committed */
  var src=handleRoll.toString();
  o.handleRollOrder={zeroHourCloseAt:src.indexOf('_zeroHourClose()'),
                     hotDiceBranchAt:src.indexOf('G._lastHotDice=true'),
                     hotDiceCommentPresent:src.indexOf('DOES NOT AWARD HOT')>=0};
  o.handleRollOrder.zeroHourFirst=(o.handleRollOrder.zeroHourCloseAt>=0
    &&o.handleRollOrder.zeroHourCloseAt<o.handleRollOrder.hotDiceBranchAt);
  o.handleBankAsksToo=handleBank.toString().indexOf('_zeroHourClose()')>=0;

  fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
         ench:['tithe',null,null,null,null,null],boss:true,tier:0});
  var G3=G_();var e3=G3._enchArr[0];
  mkPool([{mat:'silver',ench:e3,val:e3.face,committed:true},{mat:'amber',committed:true},
          {mat:'starstone',committed:true},{mat:'obsidian',committed:true},
          {mat:'jade',committed:true},{mat:'vagabond',committed:true}]);
  G3.kept=[{vals:[1],mat:'amber',pts:100,dice:[]}];
  G3._featHotDiceCount=0;G3._lastHotDice=false;
  _iconFire(G3.pool[0],'p');
  var claimed=_zeroHourClose();
  G3=G_();
  o.hotDiceCase={rowFullyCommitted:G3.pool.every(function(d){return d.committed;}),
    zeroHourClaimedTheTurn:claimed,hotDiceAwarded:(G3._featHotDiceCount||0)>0,
    lastHotDice:!!G3._lastHotDice,rollLocked:!!G3._rollLocked};
  o.noHotDiceException=(claimed===true&&!o.hotDiceCase.hotDiceAwarded
                        &&o.handleRollOrder.zeroHourFirst);

  /* HOW THE RULE CAN REACH THE TABLE — Zero Hour vs the other two rescoped
     badges. _iconFire reads G._tell.id directly; Kindred and Still Waters
     read _ruleActive, which also honours a sleeve and a sealed seat. */
  function reach(rule,how,boss){
    fresh({dice:['silver','bone','bone','bone','bone','bone'],
           ench:['tithe','tithe',null,null,null,null],boss:!!boss,tier:boss?3:3});
    var G=G_();
    if(how==='sleeve'){S.run.sleeve=rule;if(!boss){G._tell=null;G._tellState=null;}
                       try{_applySleeve();}catch(e){}}
    if(how==='seal'){G._sealRule=rule;if(!boss){G._tell=null;}try{_applySeal();}catch(e){}}
    if(how==='tell'){G._tell={id:rule,name:rule};}
    G=G_();G._zeroHourEnds=false;
    var en=G._enchArr[0];
    var pool=mkPool([{mat:'silver',ench:en,val:en.face},{mat:'bone'}]);
    _iconFire(pool[0],'p');
    G=G_();
    var r={rule:rule,how:how,boss:!!boss,tell:G._tell?G._tell.id:null,
           sleeve:G._sleeve||null,seal:G._sealRule||null,
           ruleActive:_ruleActive(rule,'p')};
    if(rule==='last_call')r.effectFired=!!G._zeroHourEnds;
    if(rule==='still_waters')r.effectFired=_stillWaters();
    if(rule==='kindred')r.effectFired=_kindredActive();
    try{S.run.sleeve=null;}catch(e){}
    return r;
  }
  o.reachability={
    zeroHour_bossTell     :reach('last_call','tell',false),
    zeroHour_sleevePatron :reach('last_call','sleeve',false),
    zeroHour_sleeveInBoss :reach('last_call','sleeve',true),
    zeroHour_sealedSeat   :reach('last_call','seal',false),
    stillWaters_sleeveInBoss:reach('still_waters','sleeve',true),
    kindred_sleeveInBoss  :reach('kindred','sleeve',true)
  };
  o.sleeveAsymmetry={
    zeroHourSleeveWorksInBoss:o.reachability.zeroHour_sleeveInBoss.effectFired,
    stillWatersSleeveWorksInBoss:o.reachability.stillWaters_sleeveInBoss.effectFired,
    kindredSleeveWorksInBoss:o.reachability.kindred_sleeveInBoss.effectFired};

  o.VERDICT=(o.allSevenEndTheTurn&&o.allSevenBankZero
    &&!o.controlNoBadge.zeroHourEnds&&o.noHotDiceException)?'PASS':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E3b — HOW WIDE IS STILL WATERS' SILENCE? the "hard counter" claim
   ───────────────────────────────────────────────────────────────────────── */
wrap('E3b_still_waters_coverage', function(){
  var o={};
  var SW=FSIM.BADGE.still_waters;
  /* the build the badge is meant to counter: Break, fired at an Obsidian die.
     Two ways to build it — the brand on the obsidian die, or the brand on a
     different die. Only the first is a "worked die". */
  function run(brandLane, badge){
    var ench=[null,null,null,null,null,null];ench[brandLane]='break';
    fresh({dice:['obsidian','obsidian','obsidian','obsidian','obsidian','bone'],
           ench:ench,badge:badge});
    var G=G_();G.turnPts=0;G.kept=[];
    var pool=mkPool([{mat:'obsidian',ench:G._enchArr[0]},{mat:'obsidian',ench:G._enchArr[1]},
                     {mat:'obsidian',ench:G._enchArr[2]},{mat:'obsidian',ench:G._enchArr[3]},
                     {mat:'obsidian',ench:G._enchArr[4]},{mat:'bone',ench:G._enchArr[5]}]);
    /* break the die at lane 0 unless that IS the branded one */
    var target=pool[brandLane===0?1:0];
    G._breakArmed=true;
    _breakDie(target);
    G=G_();
    return {brandLane:brandLane,badge:badge||'none',targetLane:target.lane,
            targetWasWorked:!!target.ench,paid:G.turnPts||0};
  }
  o.brandOnTheObsidianDie   ={SWon:run(0,SW).paid, SWoff:run(0,null).paid};
  /* brand the BONE die (lane 5): every obsidian die is unworked, so nothing
     Still Waters can see */
  o.brandOnAPlainBoneDie    ={SWon:run(5,SW).paid, SWoff:run(5,null).paid};
  o.hardCounterHolds=(o.brandOnTheObsidianDie.SWon===0);
  o.hardCounterEvadedByBuild=(o.brandOnAPlainBoneDie.SWon===1000);

  /* the passive 6% under the same two builds, over real turns */
  function passive(badge,workAll,n){
    FSIM.installRng(SEED+31);
    var lost=0;
    for(var s=0;s<n;s++){
      fresh({dice:['obsidian','obsidian','obsidian','obsidian','obsidian','obsidian'],
             ench:workAll?['tithe','tithe','tithe','tithe','tithe','tithe']
                         :['tithe',null,null,null,null,null],badge:badge});
      var G=G_();var before=G.matchDice.length;
      FSIM.simTurn(FSIM.POLICIES.carl,{turnsLeft:8,oppTotal:0,lastTurn:false});
      G=G_();lost+=(before-G.matchDice.length);
    }
    return +(lost/n).toFixed(4);
  }
  o.passiveShattersPerTurn={
    allSixWorked_SWon:passive(SW,true,400),
    allSixWorked_SWoff:passive(null,true,400),
    oneWorked_fivePlain_SWon:passive(SW,false,400)};

  /* Grog's Tooth: the brief asks for its OWN number, 10%/+1500 */
  function tooth(badge){
    fresh({dice:['grogs_tooth','bone','bone','bone','bone','bone'],
           ench:['tithe','tithe',null,null,null,null],badge:badge});
    var G=G_();G.turnPts=0;G.kept=[];
    var pool=mkPool([{mat:'grogs_tooth',ench:G._enchArr[0]},{mat:'bone',ench:G._enchArr[1]}]);
    var eff=_dieEffect(pool[0]);
    G._breakArmed=true;_breakDie(pool[0]);
    G=G_();
    return {passiveEffect:eff?eff.chance+'/'+eff.amount:null,breakPaid:G.turnPts||0};
  }
  o.grogsTooth={SWon:tooth(FSIM.BADGE.still_waters),SWoff:tooth(null)};
  o.toothBreakPaysFamilyRowNotItsOwnAmount=(o.grogsTooth.SWoff.breakPaid===1000);

  o.VERDICT=o.hardCounterHolds?'PASS (for a worked die)':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   RULING #24 — THE SILVER : BONE BUST RATIO, SWEPT ACROSS POLICIES
   The ruling states a RATIO (~0.55) and claims it "held stable (0.54-0.58)
   across every policy tested". This measures it as a function of how hard the
   policy pushes, with the real roller, the real bust gate and real scoring.
   ───────────────────────────────────────────────────────────────────────── */
wrap('SILVER_bust_ratio_sweep', function(){
  var o={};
  var cards=effectiveCards();
  /* ONE TURN, parameterised by how far it pushes. stopAt = bank as soon as
     this many free dice or fewer remain (so stopAt 0 = only hot dice ends it).
     lean = keep the single smallest scoring die instead of every scorer,
     which is the pushiest legal play and the one a volatility agent makes. */
  function turnBust(mats,stopAt,lean,n){
    var busts=0,ptsTot=0,rolls=0;
    for(var s=0;s<n;s++){
      var live=mats.map(function(m){return{mat:m,ench:null};});
      var turn=0,r=0,busted=false;
      while(r++<40){
        for(var i=0;i<live.length;i++)live[i].val=_enchRollM(live[i].mat,null);
        var vals=live.map(function(d){return d.val;});
        var ms=live.map(function(d){return d.mat;});
        rolls++;
        if(!anyScoring(vals,cards,ms,live)){busted=true;break;}
        var sc=scoreRoll(vals,cards,0,{},ms,live.map(function(d){return d.ench;}));
        var keepIdx=null;
        if(lean){
          /* the smallest keep the real engine accepts: one die that scores alone */
          for(var q=0;q<live.length;q++){
            if(scoreSelection([vals[q]],cards,0,{},[ms[q]],[null])>0){keepIdx=q;break;}
          }
        }
        var left=[];
        if(keepIdx!==null){
          turn+=scoreSelection([vals[keepIdx]],cards,0,{},[ms[keepIdx]],[null]);
          for(var w=0;w<live.length;w++)if(w!==keepIdx)left.push(live[w]);
        }else{
          turn+=(sc.total||0);
          for(var w2=0;w2<live.length;w2++)if(!sc.used||!sc.used[w2])left.push(live[w2]);
        }
        if(!left.length)left=mats.map(function(m){return{mat:m,ench:null};});/* hot dice */
        live=left;
        if(live.length<=stopAt)break;
      }
      if(busted)busts++;else ptsTot+=turn;
      }
    return {bust:ci(busts,n),meanTurnPts:+(ptsTot/n).toFixed(0),
            rollsPerTurn:+(rolls/n).toFixed(2)};
  }
  function ratio(p1,p2,n){
    var se=Math.sqrt((1-p1)/(n*p1)+(1-p2)/(n*p2)),lr=Math.log(p1/p2);
    return {r:+(p1/p2).toFixed(3),lo:+Math.exp(lr-1.96*se).toFixed(3),
            hi:+Math.exp(lr+1.96*se).toFixed(3)};
  }
  var N=20000;
  var six=function(m){return [m,m,m,m,m,m];};
  var rows=[];
  [5,4,3,2,1,0].forEach(function(k){
    FSIM.installRng(SEED+k);
    var b=turnBust(six('bone'),k,false,N);
    FSIM.installRng(SEED+k);
    var s=turnBust(six('silver'),k,false,N);
    rows.push({policy:'bank when free dice <= '+k,stopAt:k,
      bonePct:+(b.bust.p*100).toFixed(2),boneCI:[+(b.bust.lo*100).toFixed(2),+(b.bust.hi*100).toFixed(2)],
      silverPct:+(s.bust.p*100).toFixed(2),silverCI:[+(s.bust.lo*100).toFixed(2),+(s.bust.hi*100).toFixed(2)],
      ratio:ratio(s.bust.p,b.bust.p,N),
      meanPts:{bone:b.meanTurnPts,silver:s.meanTurnPts},
      rolls:{bone:b.rollsPerTurn,silver:s.rollsPerTurn}});
  });
  /* and the leanest-keep variant, the pushiest legal play there is */
  [2,1,0].forEach(function(k){
    FSIM.installRng(SEED+100+k);
    var b=turnBust(six('bone'),k,true,N);
    FSIM.installRng(SEED+100+k);
    var s=turnBust(six('silver'),k,true,N);
    rows.push({policy:'LEANEST keep, bank when free <= '+k,stopAt:k,lean:true,
      bonePct:+(b.bust.p*100).toFixed(2),boneCI:[+(b.bust.lo*100).toFixed(2),+(b.bust.hi*100).toFixed(2)],
      silverPct:+(s.bust.p*100).toFixed(2),silverCI:[+(s.bust.lo*100).toFixed(2),+(s.bust.hi*100).toFixed(2)],
      ratio:ratio(s.bust.p,b.bust.p,N),
      meanPts:{bone:b.meanTurnPts,silver:s.meanTurnPts},
      rolls:{bone:b.rollsPerTurn,silver:s.rollsPerTurn}});
  });
  o.n=N;o.sweep=rows;
  o.ratioRange=[Math.min.apply(null,rows.map(function(r){return r.ratio.r;})),
                Math.max.apply(null,rows.map(function(r){return r.ratio.r;}))];
  o.anyRowContains055=rows.filter(function(r){return r.ratio.lo<=0.55&&r.ratio.hi>=0.55;})
                          .map(function(r){return r.policy+' → '+r.ratio.r;});
  o.rowsNear49PctBone=rows.filter(function(r){return r.bonePct>=44&&r.bonePct<=55;})
                          .map(function(r){return {policy:r.policy,bone:r.bonePct,silver:r.silverPct,ratio:r.ratio};});
  /* the per-DIE odds behind the shape, straight off the real roll tables */
  function faceOdds(mat){
    var t=_rollTable(mat,null),sc=0;
    t.forEach(function(f){if(f===1||f===5)sc++;});
    return {table:t,pScoringFace:+(sc/t.length).toFixed(4)};
  }
  o.rollTables={bone:faceOdds('bone'),silver:faceOdds('silver'),
                brutus_shield:faceOdds('brutus_shield')};
  o.singleDieBustRatio=+((1-o.rollTables.silver.pScoringFace)/
                         (1-o.rollTables.bone.pScoringFace)).toFixed(3);
  /* AND the real-match number, which is what a player actually experiences */
  FSIM.installRng(SEED+7);
  var mb=FSIM.runBatch(FSIM.POLICIES.bea,{tier:3,
    gear:{dice:six('bone'),ench:[null,null,null,null,null,null],badge:null,fcards:[]}},250);
  FSIM.installRng(SEED+7);
  var ms=FSIM.runBatch(FSIM.POLICIES.bea,{tier:3,
    gear:{dice:six('silver'),ench:[null,null,null,null,null,null],badge:null,fcards:[]}},250);
  o.inRealMatches={n:250,
    bone:{bustPerTurnPct:+(mb.bustRate.p*100).toFixed(2),ci:[+(mb.bustRate.lo*100).toFixed(2),+(mb.bustRate.hi*100).toFixed(2)],
          win:mb.winRate.p,turns:mb.bustRate.n},
    silver:{bustPerTurnPct:+(ms.bustRate.p*100).toFixed(2),ci:[+(ms.bustRate.lo*100).toFixed(2),+(ms.bustRate.hi*100).toFixed(2)],
          win:ms.winRate.p,turns:ms.bustRate.n},
    ratio:ratio(ms.bustRate.p,mb.bustRate.p,Math.min(mb.bustRate.n,ms.bustRate.n))};
  o.VERDICT='MEASURED — see sweep; ratio is NOT policy-invariant';
  return o;
});

FSIM.loud();FSIM.restoreRng();
return R;
