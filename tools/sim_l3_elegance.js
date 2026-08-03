/* ══════════════════════════════════════════════════════════════════════════
   sim_l3_elegance.js — LENS 3, the seven targeted ELEGANCE checks plus the
   seven Break family rows and the Silver bust ratio.

   Tail file for tools/sim_run.js (the FSIM harness is concatenated in front).
   Every check drives a SHIPPED function: _breakDie / _breakBegin /
   _removeDieAt / BREAK_TRIGGERS[*].fire / _iconFire / ENCH_ICONS[*].fire /
   _tradeRestore / _gbEnchantApply / _enchInit / _iconFaceRoll / _iconFaces /
   _wardOwned / _bornEnch / _stillWaters / _famHushed / _dieEffect /
   _zeroHourClose / famDieStash / famDieEquip / _stTrade / newG.
   fark_proto.html is NOT edited.
   ══════════════════════════════════════════════════════════════════════════ */
var SEED = (window.__FSIM_SEED!==undefined ? window.__FSIM_SEED : 20260731);
var R = {seed:SEED, checks:{}, notes:[], errors:[]};

function J(x){return JSON.parse(JSON.stringify(x===undefined?null:x));}
function eq(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function G_(){return FSIM.getG();}
function el(){var e=document.createElement('div');e.className='die';return e;}
/* build a pool the way the game builds one: lane-stamped, element-backed */
function mkPool(spec){
  var G=G_();
  G.pool=spec.map(function(s,i){
    return {val:(s.val===undefined?2:s.val), mat:s.mat, ench:(s.ench||null),
            sel:false, committed:!!s.committed, el:el(),
            lane:(s.lane===undefined?i:s.lane)};
  });
  return G.pool;
}
function wrap(name, fn){
  try{ R.checks[name]=fn(); }
  catch(e){ R.checks[name]={VERDICT:'ERROR', err:e.message,
    at:(e.stack||'').split('\n')[1]||''}; R.errors.push(name+': '+e.message); }
}
/* a fresh run + match, from the real generators */
function fresh(o){
  o=o||{};
  return FSIM.setupMatch({tier:(o.tier==null?3:o.tier), boss:!!o.boss,
    dice:o.dice||['obsidian','amber','starstone','silver','jade','vagabond'],
    ench:o.ench||[null,null,null,null,null,null],
    badge:o.badge||null, fcards:[], diceInv:o.diceInv||[], gold:o.gold||0});
}
/* Wilson, from the harness */
var ci=FSIM.ci95;

/* the shipped file itself, read back over the wire, so "is this feature even
   built" is answered by counting writers rather than by asserting it */
var SRC='';
try{ SRC = await fetch(location.href).then(function(r){return r.text();}); }
catch(e){ R.errors.push('src fetch: '+e.message); }

FSIM.installRng(SEED);
FSIM.quiet();

/* ─────────────────────────────────────────────────────────────────────────
   E1 — BREAK IS MATCH-SCOPED, AND THE DIE IS BACK NEXT MATCH
   ───────────────────────────────────────────────────────────────────────── */
wrap('E1_break_match_scoped', function(){
  var o={};
  var set=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                 ench:['break','tithe',null,null,null,'fog']});
  var G=G_();
  var runBefore={dice:J(S.run.dice), ench:J(S.run.dieEnch),
                 inv:J(S.run.diceInv), invE:J(S.run.dieEnchInv)};
  var mdBefore=J(G.matchDice), enBefore=J(G._enchArr);
  o.loadout={dice:runBefore.dice, ench:enBefore.map(function(e){return e?e.t+'@'+e.face:null;})};

  var pool=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},
                   {mat:'silver'},{mat:'jade'},{mat:'vagabond'}]);
  G.numDice=6;
  G._breakArmed=true;
  _breakDie(pool[2]);                       /* the REAL destroyer, lane 2 */
  G=G_();

  o.afterBreak={
    matchDice:J(G.matchDice),
    matchDiceLen:G.matchDice.length,
    enchArrLen:(G._enchArr||[]).length,
    numDice:G.numDice,
    poolLanes:G.pool.map(function(d){return d.lane;}),
    diceOut:J(G._diceOut)
  };
  o.runUntouched = eq(J(S.run.dice),runBefore.dice) && eq(J(S.run.dieEnch),runBefore.ench)
                && eq(J(S.run.diceInv),runBefore.inv) && eq(J(S.run.dieEnchInv),runBefore.invE);
  o.goneThisMatch = (G.matchDice.length===5) && (G.matchDice.indexOf('starstone')<0)
                 && ((G._enchArr||[]).length===5);

  /* and it STAYS gone across a turn boundary inside the same match */
  try{ startPTurn(); }catch(e){ o.startPTurnErr=e.message; }
  G=G_();
  o.afterTurnBoundary={numDice:G.numDice, matchDiceLen:G.matchDice.length,
                       matchDice:J(G.matchDice)};
  o.stillGoneNextTurn = (G.matchDice.length===5) && (G.numDice===5);

  /* THE NEXT MATCH, built the way the game builds it: newG reads S.run.dice,
     initMatchScreen copies S.run.dieEnch into G._enchArr. */
  var rung2=generatePatron(3);
  var g2=newG(rung2,[],[],0,0);
  FSIM.setG(g2);
  g2._enchArr=(S.run.dieEnch||[]).slice();
  o.nextMatch={matchDice:J(g2.matchDice),
               ench:(g2._enchArr||[]).map(function(e){return e?e.t+'@'+e.face:null;})};
  o.restoredNextMatch = eq(J(g2.matchDice), mdBefore) && eq(J(g2._enchArr), enBefore);

  o.VERDICT = (o.goneThisMatch && o.runUntouched && o.stillGoneNextTurn
               && o.restoredNextMatch) ? 'PASS' : 'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E2 — TRADE IS MATCH-SCOPED AND BOTH LOADOUTS COME BACK BIT-FOR-BIT
   ───────────────────────────────────────────────────────────────────────── */
wrap('E2_trade_match_scoped', function(){
  var o={};
  /* --- 2a: the simple case, one trade, restored at match end --- */
  var set=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                 ench:[null,null,null,'trade',null,'tithe']});
  var G=G_();
  var runBefore={dice:J(S.run.dice), ench:J(S.run.dieEnch)};
  var mdBefore=J(G.matchDice), oppBefore=J(G.matchOppDice), enBefore=J(G._enchArr);
  var rungDiceBefore=J(set.rung.dice);
  var tr=G._enchArr[3];
  o.brand={lane:3, t:tr&&tr.t, face:tr&&tr.face};

  var pool=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},
                   {mat:'silver',ench:tr,val:(tr&&tr.face)||1},
                   {mat:'jade'},{mat:'vagabond'}]);
  var fired=_iconFire(pool[3],'p');         /* the REAL universal rule */
  G=G_();
  o.iconBanked=fired;
  o.afterFire={md:J(G.matchDice), opp:J(G.matchOppDice),
               ench3:G._enchArr[3], ledger:J(G._tradeSwaps)};
  o.swapHappened = (G.matchDice[3]===oppBefore[3]) && (G.matchOppDice[3]===mdBefore[3])
                && (G._enchArr[3]===null);
  o.runUntouchedDuringMatch = eq(J(S.run.dice),runBefore.dice)
                           && eq(J(S.run.dieEnch),runBefore.ench);
  o.rungUntouched = eq(J(set.rung.dice), rungDiceBefore);

  var n=_tradeRestore();                     /* the REAL match-end restore */
  G=G_();
  o.restoredCount=n;
  o.mineBack   = eq(J(G.matchDice),  mdBefore);
  o.theirsBack = eq(J(G.matchOppDice), oppBefore);
  o.brandBack  = eq(J(G._enchArr),   enBefore);
  o.runBitForBit = eq(J(S.run.dice),runBefore.dice) && eq(J(S.run.dieEnch),runBefore.ench);
  o.idempotent = (_tradeRestore()===0);

  /* --- 2b: whole real matches with a Trade brand, run end to end --- */
  FSIM.installRng(SEED+11);
  var GEAR={dice:['obsidian','amber','starstone','silver','jade','vagabond'],
            ench:['trade','tithe',null,null,null,'fog'],badge:null,fcards:[]};
  var bad=0, traded=0, runDrift=0, brandLost=0, n2=150;
  for(var i=0;i<n2;i++){
    var m=FSIM.simMatch(FSIM.POLICIES.bea,{tier:3,gear:GEAR,playerFirst:i%2===0});
    traded+=m.tradesRestored||0;
    var g=G_();
    if(g._tradeSwaps&&g._tradeSwaps.length)bad++;
    /* the OWNED loadout must be exactly the gear spec after every match:
       Trade's fire never writes S.run.dice, so any drift is a leak */
    if(!eq(J(S.run.dice),GEAR.dice))runDrift++;
    var t0=S.run.dieEnch&&S.run.dieEnch[0];
    if(!(t0&&t0.t==='trade'&&(t0.face===1||t0.face===5)))brandLost++;
  }
  o.matchRun={n:n2, tradesRestored:traded, ledgerLeftOver:bad,
              ownedLoadoutDrift:runDrift, tradeBrandLost:brandLost,
              runDiceAfter:J(S.run.dice)};
  o.noResidueAfterMatches = (bad===0 && runDrift===0 && brandLost===0);

  /* --- 2c: a Break in a lane BELOW a traded lane (the shifting-index case) --- */
  var set3=fresh({dice:['obsidian','amber','starstone','silver','jade','vagabond'],
                  ench:[null,null,null,null,'trade',null]});
  G=G_();
  var md3=J(G.matchDice), opp3=J(G.matchOppDice), en3=J(G._enchArr);
  var tr3=G._enchArr[4];
  var p3=mkPool([{mat:'obsidian'},{mat:'amber'},{mat:'starstone'},{mat:'silver'},
                 {mat:'jade',ench:tr3,val:(tr3&&tr3.face)||1},{mat:'vagabond'}]);
  G.numDice=6;
  _iconFire(p3[4],'p');                       /* trade lane 4 */
  G=G_();
  var afterTrade=J(G.matchDice);
  G._breakArmed=true;
  _breakDie(G.pool.filter(function(d){return d.lane===1;})[0]);  /* break lane 1 */
  G=G_();
  var afterBreak=J(G.matchDice);
  var n3=_tradeRestore();
  G=G_();
  o.breakUnderTrade={afterTrade:afterTrade, afterBreak:afterBreak,
    afterRestore:J(G.matchDice), enchAfterRestore:(G._enchArr||[]).map(function(e){return e?e.t:null;}),
    restored:n3,
    expectMaterials:md3.filter(function(_,i){return i!==1;}),
    materialsRight: eq(J(G.matchDice), md3.filter(function(_,i){return i!==1;})),
    runStillClean: eq(J(S.run.dice), md3) };

  o.VERDICT = (o.swapHappened && o.runUntouchedDuringMatch && o.rungUntouched
    && o.mineBack && o.theirsBack && o.brandBack && o.runBitForBit
    && o.noResidueAfterMatches) ? 'PASS' : 'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E3 — STILL WATERS SILENCES BREAK'S *GUARANTEED* OBSIDIAN PAYOUT
   ───────────────────────────────────────────────────────────────────────── */
wrap('E3_still_waters_break', function(){
  var o={cases:{}};
  function trial(label, mat, brandTheTarget, badge){
    var set=fresh({dice:[mat,'bone','bone','bone','bone','bone'],
                   ench:brandTheTarget?['tithe',null,null,null,null,null]
                                      :[null,null,null,null,null,'tithe'],
                   badge:badge||null});
    var G=G_();
    var en=G._enchArr[0]||null;
    var pool=mkPool([{mat:mat,ench:en},{mat:'bone'},{mat:'bone'}]);
    G.numDice=6;G.turnPts=0;G.kept=[];
    var sw=_stillWaters();
    var hush=_famHushed(pool[0]);
    var effBefore=_dieEffect(pool[0]);
    G._breakArmed=true;
    _breakDie(pool[0]);
    G=G_();
    return {label:label, mat:mat, targetBranded:!!brandTheTarget, badgeOn:sw,
            famHushed:hush, dieEffect:effBefore?effBefore.mechanic+'/'+effBefore.amount:null,
            turnPtsAfter:G.turnPts||0, keptRows:(G.kept||[]).length,
            paid:(G.turnPts||0)>0};
  }
  var SW=FSIM.BADGE.still_waters;                       /* 'still_waters' */
  o.cases.obsidian_worked_SWon   = trial('worked obsidian, Still Waters ON','obsidian',true, SW);
  o.cases.obsidian_worked_SWoff  = trial('worked obsidian, Still Waters OFF','obsidian',true, null);
  o.cases.obsidian_plain_SWon    = trial('PLAIN obsidian, Still Waters ON','obsidian',false, SW);
  o.cases.obsidian_plain_SWoff   = trial('PLAIN obsidian, Still Waters OFF','obsidian',false,null);
  o.cases.grogstooth_worked_SWon = trial("Grog's Tooth worked, SW ON",'grogs_tooth',true, SW);
  o.cases.grogstooth_worked_SWoff= trial("Grog's Tooth worked, SW OFF",'grogs_tooth',true, null);

  /* THE PASSIVE 6% CHECK, for the same die, so the two can be compared. The
     harness's afterRoll runs the shipped _dieEffect gate and the real removal. */
  function passive(badge, worked, n){
    FSIM.installRng(SEED+7);
    var shatters=0, turns=0;
    for(var s=0;s<n;s++){
      fresh({dice:['obsidian','obsidian','obsidian','obsidian','obsidian','obsidian'],
             ench:worked?['tithe','tithe','tithe','tithe','tithe','tithe']
                        :[null,null,null,null,null,null],
             badge:badge});
      var G=G_();
      var before=G.matchDice.length;
      var t=FSIM.simTurn(FSIM.POLICIES.carl,{turnsLeft:8,oppTotal:0,lastTurn:false});
      G=G_();
      shatters+=(before-G.matchDice.length);
      turns++;
    }
    return {shattersPerTurn:+(shatters/turns).toFixed(4), turns:turns, shatters:shatters};
  }
  o.passive={
    worked_SWon : passive(SW, true, 500),
    worked_SWoff: passive(null,true, 500),
    plain_SWon  : passive(SW, false,500)
  };

  o.guaranteedSilencedOnWorkedDie =
      (o.cases.obsidian_worked_SWon.turnPtsAfter===0) &&
      (o.cases.obsidian_worked_SWoff.turnPtsAfter===1000);
  o.passiveSilencedOnWorkedDie =
      (o.passive.worked_SWon.shatters===0) && (o.passive.worked_SWoff.shatters>0);
  o.plainDieStillPays = (o.cases.obsidian_plain_SWon.turnPtsAfter===1000);
  o.VERDICT = (o.guaranteedSilencedOnWorkedDie && o.passiveSilencedOnWorkedDie)
              ? 'PASS' : 'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E4 — TWO WARD-BRANDED DICE, UNDER ANY PURCHASE SEQUENCE
   ───────────────────────────────────────────────────────────────────────── */
wrap('E4_ward_cap', function(){
  var o={sequences:[]};
  function wardCount(){
    _enchInit();
    var lo=(S.run.dieEnch||[]).filter(function(e){return e&&e.t==='ward';}).length;
    var iv=(S.run.dieEnchInv||[]).filter(function(e){return e&&e.t==='ward';}).length;
    return {loadout:lo, inv:iv, total:lo+iv};
  }
  function reset(dice, inv, gold){
    _getS();
    S.run.dice=(dice||['bone','bone','bone','bone','bone','bone']).slice();
    S.run.dieEnch=[null,null,null,null,null,null];
    S.run.diceInv=(inv||[]).slice();
    S.run.dieEnchInv=[];
    S.run.gold=(gold==null?9000:gold);
    S.run._enchV=3;S.run._enchTradeV=1;
    S.run.diceStock=_initDiceStock();
    _enchInit();
  }
  /* the SHOP's own sale, exactly as _stEnchChoose and _gbEnchantDie call it */
  function buyWard(lane){
    var f=_iconFaceRoll(S.run.dice[lane]);
    var g0=S.run.gold;
    _gbEnchantApply('ward',lane,f,null,true);
    var e=S.run.dieEnch[lane];
    return {lane:lane, face:f, landed:!!(e&&e.t==='ward'), goldSpent:g0-S.run.gold};
  }
  function seq(name, fn){
    var r={name:name}; try{ r.result=fn(); }catch(e){ r.err=e.message; }
    r.wards=wardCount(); r.ok=(r.wards.loadout<=1 && r.wards.total<=1);
    o.sequences.push(r); return r;
  }
  /* the real loadout moves; their trailing repaint is DOM-only */
  function stash(i){try{famDieStash(i);}catch(e){}}
  function equip(i){try{famDieEquip(i);}catch(e){}}
  function counterTrade(m,i){try{_stTrade(m,i);}catch(e){}}

  seq('A. buy Ward on lane 0, then lane 1', function(){
    reset(); return [buyWard(0), buyWard(1)];
  });
  seq('B. Ward on 0, stash that die, Ward on the fresh lane 0', function(){
    reset(['silver','bone','bone','bone','bone','bone']);
    var a=buyWard(0);
    stash(0);                             /* the real loadout stash */
    var b=buyWard(0);
    return [a,{stashed:J(S.run.diceInv),invEnch:J(S.run.dieEnchInv)},b];
  });
  seq("C. Brutus's relic already in the loadout, then buy a Ward", function(){
    reset(['bone','bone','brutus_shield','bone','bone','bone']);
    return [{bornStamped:J(S.run.dieEnch[2])}, buyWard(0), buyWard(4)];
  });
  seq("D. buy a Ward first, THEN win Brutus's relic into the inventory", function(){
    reset();
    var a=buyWard(0);
    var g0=S.run.gold;
    S.run.diceInv.push('brutus_shield');   /* exactly what famSpoilsPick does */
    _enchInit();
    return [a,{relicInInv:true, refund:S.run.gold-g0,
               loadoutEnch:J(S.run.dieEnch), invEnch:J(S.run.dieEnchInv)}];
  });
  seq("E. Ward bought, relic won, then EQUIP the relic into the six", function(){
    reset();
    var a=buyWard(3);
    S.run.diceInv.push('brutus_shield');_enchInit();
    equip(0);                              /* the real equip */
    return [a,{dice:J(S.run.dice), ench:J(S.run.dieEnch), invE:J(S.run.dieEnchInv)}];
  });
  seq('F. forged point-of-sale call: second Ward, face supplied by hand', function(){
    reset();
    var a=buyWard(0);
    var g0=S.run.gold;
    _gbEnchantApply('ward',1,5,null,true);
    _gbEnchantApply('ward',2,1,null,true);
    return [a,{secondSpent:g0-S.run.gold, ench:J(S.run.dieEnch)}];
  });
  seq('G. relic traded out of the loadout, then a Ward bought', function(){
    reset(['bone','bone','brutus_shield','bone','bone','bone']);
    S.run.gold=9000;
    counterTrade('iron',2);                /* the real counter trade */
    var a=buyWard(0);
    return [{dice:J(S.run.dice)},a];
  });
  seq('H. Ward in the loadout AND a stashed relic, both live at once', function(){
    reset(['bone','bone','bone','bone','bone','bone'],['brutus_shield']);
    var a=buyWard(0);
    return [a,{ench:J(S.run.dieEnch), invE:J(S.run.dieEnchInv)}];
  });
  /* ADVERSARIAL, outside any purchase sequence: two relic dice at once. There
     is one Brutus per run and brutus_shield is not in DICE_STORE, so this is
     not reachable by buying — it is here to show WHERE the cap lives. */
  seq('I. [not purchasable] two brutus_shield dice forced into the loadout', function(){
    reset(['brutus_shield','brutus_shield','bone','bone','bone','bone']);
    return [{ench:J(S.run.dieEnch)}];
  });
  o.storeHasRelic = DICE_STORE.some(function(d){return d.mat==='brutus_shield';});
  o.bossKeys = TIERS.map(function(t){return t.boss?t.boss.key:null;});
  o.brutusSeats = o.bossKeys.filter(function(k){return k==='soldier';}).length;

  var purchasable=o.sequences.filter(function(s){return s.name.indexOf('[not purchasable]')<0;});
  o.VERDICT = purchasable.every(function(s){return s.ok;}) ? 'PASS' : 'FAIL';
  o.adversarialLeak = o.sequences.filter(function(s){return !s.ok;}).map(function(s){return s.name;});
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E5 — A BRANDED ICON FACE ONLY EVER LANDS ON A NATURAL 1 OR 5
   ───────────────────────────────────────────────────────────────────────── */
wrap('E5_face_1_or_5', function(){
  var o={};
  /* every die type, every draw */
  var bad=[], perDie={};
  DICE_TYPES.forEach(function(dt){
    var seen={}, legal=_iconFaces(dt.id);
    for(var i=0;i<4000;i++){
      var f=_iconFaceRoll(dt.id);
      seen[String(f)]=(seen[String(f)]||0)+1;
      if(f!==null&&f!==1&&f!==5)bad.push({mat:dt.id,face:f});
      if(f!==null&&dt.faces.indexOf(f)<0)bad.push({mat:dt.id,face:f,why:'not a natural face'});
    }
    perDie[dt.id]={legal:legal, drew:seen};
  });
  o.drawsPerDie=perDie; o.illegalDraws=bad.length; o.illegalSample=bad.slice(0,5);
  o.diceTypes=DICE_TYPES.length; o.drawsEach=4000;
  o.totalDraws=DICE_TYPES.length*4000;

  /* every BORN brand in the catalogue */
  o.bornBrands=DICE_TYPES.filter(function(d){return d.bornEnch;})
    .map(function(d){return {mat:d.id, t:d.bornEnch.t, face:d.bornEnch.face,
      legalHere:_iconFaces(d.id).indexOf(d.bornEnch.face)>=0};});

  /* the SALE refuses a forged face */
  _getS();
  S.run.dice=['bone','bone','bone','bone','bone','bone'];
  S.run.dieEnch=[null,null,null,null,null,null];
  S.run.diceInv=[];S.run.dieEnchInv=[];S.run.gold=9000;S.run._enchV=3;
  _enchInit();
  var forged=[];
  [2,3,4,6].forEach(function(f){
    var g0=S.run.gold;
    _gbEnchantApply('tithe',0,f,null,true);
    forged.push({face:f, landed:!!S.run.dieEnch[0], spent:g0-S.run.gold});
  });
  o.forgedSale=forged;
  o.forgedRefused=forged.every(function(x){return !x.landed && x.spent===0;});

  /* the v3 MIGRATION refunds a legacy brand sitting on an illegal face */
  S.run.dice=['bone','amber','silver','obsidian','jade','starstone'];
  S.run.dieEnch=[{t:'tithe',face:3},{t:'ward',face:6},{t:'snare',face:1},
                 {t:'fog',face:2},{t:'break',face:5},{t:'trade',face:4}];
  S.run.diceInv=['iron'];S.run.dieEnchInv=[{t:'tithe',face:4}];
  S.run.gold=0; S.run._enchV=2; S.run._enchTradeV=1;
  _enchInit();
  o.migration={survivors:J(S.run.dieEnch), invSurvivors:J(S.run.dieEnchInv),
               refunded:S.run.gold};
  o.migrationClean=(S.run.dieEnch||[]).every(function(e){
      return !e || !ENCH_ICONS[e.t] || _iconFaces(S.run.dice[S.run.dieEnch.indexOf(e)])
        .indexOf(e.face)>=0; })
    && (S.run.dieEnch||[]).filter(function(e){return e&&[3,6,2,4].indexOf(e.face)>=0;}).length===0;

  /* and the LIVE match array, over many generated loadouts */
  var live=0, liveBad=0;
  var mats=DICE_TYPES.map(function(d){return d.id;});
  for(var t=0;t<200;t++){
    var pick=[];for(var q=0;q<6;q++)pick.push(mats[(Math.random()*mats.length)|0]);
    var kinds=['tithe','ward','snare','break','trade','snuff','fog'];
    var en=[];for(var q2=0;q2<6;q2++)en.push(kinds[(Math.random()*kinds.length)|0]);
    fresh({dice:pick,ench:en});
    (G_()._enchArr||[]).forEach(function(e){
      if(!e||!ENCH_ICONS[e.t])return;
      live++; if(e.face!==1&&e.face!==5)liveBad++;
    });
  }
  o.liveMatchBrands={checked:live, illegal:liveBad};

  /* the jade wild-6 / relic-altered clause: is it ever load-bearing? */
  o.faceAlteredEverMatters=DICE_TYPES.some(function(d){
    return [1,5].some(function(f){return d.faces.indexOf(f)>=0 && _faceAltered(d.id,f);});});

  o.VERDICT=(bad.length===0 && o.forgedRefused && liveBad===0
    && o.bornBrands.every(function(b){return (b.face===1||b.face===5)&&b.legalHere;})
    && o.migrationClean) ? 'PASS':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E6 — A PRESERVED DIE IS NEVER A LEGAL BREAK TARGET
   (guard-verified-but-feature-absent, per the task note)
   ───────────────────────────────────────────────────────────────────────── */
wrap('E6_preserve_guard', function(){
  var o={shapes:{}};
  function attempt(setup){
    fresh({dice:['obsidian','obsidian','obsidian','bone','bone','bone']});
    var G=G_();
    var pool=mkPool([{mat:'obsidian'},{mat:'obsidian'},{mat:'obsidian'}]);
    G.numDice=6;G.turnPts=0;G.kept=[];
    setup(G,pool);
    var lenBefore=G.matchDice.length;
    var began=_breakBegin(pool[0]);                 /* the REAL targeting arm */
    var outlined=pool.map(function(d){return d.el.classList.contains('break-target');});
    var handlers=pool.map(function(d){return typeof d.el.onclick==='function';});
    G._breakArmed=true;
    _breakDie(pool[1]);                             /* try to kill the guarded one */
    G=G_();
    return {begun:began, outlined:outlined, handlers:handlers,
            preservedByGuard:_breakPreserved(pool[1]),
            matchDiceBefore:lenBefore, matchDiceAfter:G.matchDice.length,
            turnPts:G.turnPts||0, survived:(G.matchDice.length===lenBefore)};
  }
  o.shapes.perDieFlag = attempt(function(G,p){ p[1]._preserved=true; });
  o.shapes.famPreserveDie = attempt(function(G,p){ G._famPreserve={die:p[1],val:5,pts:50}; });
  o.shapes.famPreserveLane= attempt(function(G,p){ G._famPreserve={lane:1,val:5,pts:50}; });
  o.shapes.control_notPreserved = attempt(function(){});

  /* nothing left to break when every other die is guarded */
  fresh({dice:['obsidian','obsidian','bone','bone','bone','bone']});
  var G=G_();
  var p=mkPool([{mat:'obsidian'},{mat:'obsidian'}]);
  p[1]._preserved=true;
  o.allTargetsGuarded={breakBeginReturned:_breakBegin(p[0])};

  /* IS THE FEATURE THERE AT ALL? count writers in the shipped file */
  o.featurePresent=null;
  try{
    var writes=(SRC.match(/_preserved\s*=[^=]/g)||[]).length;
    var reads=(SRC.match(/_preserved/g)||[]).length;
    var fp=(SRC.match(/_famPreserve\s*=\s*\{[^}]*\}/g)||[]);
    o.featurePresent={ preservedAssignments:writes, preservedMentions:reads,
      famPreserveLiterals:fp.map(function(s){return s.replace(/\s+/g,' ').slice(0,110);}) };
  }catch(e){ o.featurePresent={err:e.message}; }

  var guardHolds = o.shapes.perDieFlag.survived && o.shapes.famPreserveDie.survived
                && o.shapes.famPreserveLane.survived
                && !o.shapes.control_notPreserved.survived
                && o.shapes.perDieFlag.outlined[1]===false
                && o.shapes.famPreserveDie.outlined[1]===false
                && o.shapes.famPreserveLane.outlined[1]===false
                && o.allTargetsGuarded.breakBeginReturned===false;
  o.VERDICT = guardHolds ? 'GUARD-VERIFIED (feature absent)' : 'GUARD FAILS';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   E7 — ZERO HOUR ENDS THE TURN ON ANY ICON KEEP, NO HOT-DICE EXCEPTION
   ───────────────────────────────────────────────────────────────────────── */
wrap('E7_zero_hour', function(){
  var o={perIcon:{}};
  var ZH=FSIM.BADGE.zero_hour;                      /* 'last_call' */
  /* which rung actually carries it */
  o.tellHome=RUNGS.map(function(r,i){return r.tell?i+':'+r.tell.id:null;})
                  .filter(Boolean).join(' ');
  var kinds=['tithe','ward','snare','break','trade','snuff','fog'];
  kinds.forEach(function(k){
    var set=fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
                   ench:[k,null,null,null,null,null], boss:true, tier:0});
    var G=G_();
    G._zeroHourEnds=false;
    var en=G._enchArr[0];
    var pool=mkPool([{mat:'silver',ench:en,val:(en&&en.face)||1},{mat:'amber'},{mat:'jade'}]);
    G.oppTurnCount=1;G._oLastBank=300;
    _iconFire(pool[0],'p');
    G=G_();
    o.perIcon[k]={tellId:G._tell&&G._tell.id, brandFace:en&&en.face,
                  zeroHourEnds:!!G._zeroHourEnds};
  });
  o.allSevenEndTheTurn=kinds.every(function(k){return o.perIcon[k].zeroHourEnds;});

  /* WITHOUT the badge nothing ends */
  var s2=fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
                ench:['tithe',null,null,null,null,null]});
  var G2=G_();var e2=G2._enchArr[0];
  var p2=mkPool([{mat:'silver',ench:e2,val:e2.face}]);
  _iconFire(p2[0],'p');
  o.controlNoBadge={tellId:G_()._tell?G_()._tell.id:null, zeroHourEnds:!!G_()._zeroHourEnds};

  /* THE HOT-DICE QUESTION. Source order first, off the LIVE function object:
     handleRoll must reach _zeroHourClose() before the hot-dice branch. */
  var src=handleRoll.toString();
  var iZH=src.indexOf('_zeroHourClose()');
  var iHOT=src.indexOf("G._lastHotDice=true");
  o.handleRollOrder={zeroHourCloseAt:iZH, hotDiceBranchAt:iHOT,
                     zeroHourFirst:(iZH>=0&&iHOT>=0&&iZH<iHOT)};
  var bsrc=handleBank.toString();
  o.handleBankHasZeroHour=bsrc.indexOf('_zeroHourClose()')>=0;

  /* and behaviourally: with the whole row committed — the hot-dice condition —
     _zeroHourClose still claims the turn, so the caller returns above the
     branch that would have awarded the fresh six. */
  var s3=fresh({dice:['silver','amber','starstone','obsidian','jade','vagabond'],
                ench:['tithe',null,null,null,null,null], boss:true, tier:0});
  var G3=G_();
  var e3=G3._enchArr[0];
  var p3=mkPool([{mat:'silver',ench:e3,val:e3.face,committed:true},
                 {mat:'amber',committed:true},{mat:'starstone',committed:true},
                 {mat:'obsidian',committed:true},{mat:'jade',committed:true},
                 {mat:'vagabond',committed:true}]);
  G3.kept=[{vals:[1],mat:'amber',pts:100,dice:[]}];
  G3._featHotDiceCount=0;G3._lastHotDice=false;
  _iconFire(p3[0],'p');
  G3=G_();
  var claimed=_zeroHourClose();
  G3=G_();
  o.hotDiceCase={allCommitted:G3.pool.every(function(d){return d.committed;}),
    zeroHourEndsWasSet:true, zeroHourCloseClaimedTurn:claimed,
    hotDiceAwarded:(G3._featHotDiceCount||0)>0, lastHotDice:!!G3._lastHotDice,
    poolLen:G3.pool.length};
  o.noHotDiceException = claimed===true && !o.hotDiceCase.hotDiceAwarded
                      && o.handleRollOrder.zeroHourFirst;

  /* SLEEVE / SEAL reachability — the file's own comment calls last_call a
     retired id, and _iconFire reads G._tell.id rather than _ruleActive. */
  function reach(kind){
    var set=fresh({dice:['silver','bone','bone','bone','bone','bone'],
                   ench:['tithe',null,null,null,null,null],
                   boss:(kind==='sleeveOnBoss'), tier:(kind==='sleeveOnBoss'?3:3)});
    var G=G_();
    if(kind==='sleevePatron'||kind==='sleeveOnBoss'){
      S.run.sleeve='last_call';
      if(kind==='sleevePatron'){G._tell=null;G._tellState=null;}
      try{_applySleeve();}catch(e){}
    }
    if(kind==='seal'){ G._sealRule='last_call'; G._tell=null; try{_applySeal();}catch(e){} }
    G=G_();
    G._zeroHourEnds=false;
    var en=G._enchArr[0];
    var pool=mkPool([{mat:'silver',ench:en,val:en.face},{mat:'bone'}]);
    _iconFire(pool[0],'p');
    G=G_();
    return {tell:G._tell?G._tell.id:null, sleeve:G._sleeve||null, seal:G._sealRule||null,
            ruleActive:_ruleActive('last_call','p'), fired:!!G._zeroHourEnds};
  }
  o.reachability={bossTell:{fired:o.perIcon.tithe.zeroHourEnds},
                  sleeveOnPatron:reach('sleevePatron'),
                  sleeveInBossMatch:reach('sleeveOnBoss'),
                  sealedSeat:reach('seal')};
  try{S.run.sleeve=null;}catch(e){}

  o.VERDICT=(o.allSevenEndTheTurn && !o.controlNoBadge.zeroHourEnds
             && o.noHotDiceException) ? 'PASS':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   THE SEVEN BREAK FAMILY ROWS — exactly one row each, no cross-contamination
   ───────────────────────────────────────────────────────────────────────── */
wrap('BREAK_seven_rows', function(){
  var o={rows:{}, crossContamination:[]};
  var CASES=[
    {fam:'obsidian', mat:'obsidian'}, {fam:'amber', mat:'amber'},
    {fam:'starstone',mat:'starstone'},{fam:'silver', mat:'silver'},
    {fam:'jade',     mat:'jade'},     {fam:'vagabond',mat:'vagabond'},
    {fam:'mundane',  mat:'bone'},     {fam:'mundane',  mat:'iron'},
    {fam:'mundane',  mat:'flint'},    {fam:'mundane',  mat:'lead'}
  ];
  CASES.forEach(function(c){
    fresh({dice:[c.mat,'bone','bone','bone','bone','bone']});
    var G=G_();
    G.turnPts=0;G.kept=[];G.oPts=1200;G._oLastBank=450;
    G._bustImmuneTurn=false;G._extraTurn=0;
    /* OBSERVE the row's own write of _breakBankNow — _breakDie consumes and
       clears the flag on its way out, so a plain read after the call cannot
       see Silver's row fire. The setter below records, then stores. */
    var bankNowWrites=[];
    var _bn=false;
    Object.defineProperty(G,'_breakBankNow',{configurable:true,
      get:function(){return _bn;}, set:function(v){bankNowWrites.push(v);_bn=v;}});
    /* and count the real _rollD calls, which is Jade's row and nothing else's */
    var realRollD=window._rollD, rollDCalls=0;
    window._rollD=function(){rollDCalls++;return realRollD.apply(null,arguments);};

    var pool=mkPool([{mat:c.mat,val:2},{mat:'bone',val:3},{mat:'bone',val:4},{mat:'bone',val:6}]);
    var valsBefore=pool.map(function(d){return d.val;});
    G.numDice=6;
    G._breakArmed=true;
    _breakDie(pool[0]);
    window._rollD=realRollD;
    G=G_();
    var row={mat:c.mat, expectFam:(c.fam==='mundane'?null:c.fam), sawFam:_matFam(c.mat),
      d_turnPts:(G.turnPts||0)-0,
      d_keptRows:(G.kept||[]).length,
      keptMats:(G.kept||[]).map(function(k){return k.mat+':'+k.pts;}),
      bustImmune:!!G._bustImmuneTurn,
      extraTurn:G._extraTurn||0,
      bankNowSetTrue:bankNowWrites.indexOf(true)>=0,
      oPts:G.oPts, d_oPts:G.oPts-1200,
      rollDCalls:rollDCalls,
      freeVals:G.pool.filter(function(d){return !d.committed;}).map(function(d){return d.val;}),
      valsBefore:valsBefore.slice(1),
      matchDiceLen:G.matchDice.length};
    /* the signature vector: which of the six verbs fired */
    row.fired={obsidianPay:row.d_turnPts===1000&&row.keptMats.indexOf('obsidian:1000')>=0,
               amberImmune:row.bustImmune,
               starstoneExtra:row.extraTurn>0,
               silverBank:row.bankNowSetTrue,
               jadeScatter:row.rollDCalls>0,
               vagabondSteal:row.d_oPts<0&&row.d_turnPts>0&&row.d_turnPts!==1000};
    delete G._breakBankNow; G._breakBankNow=false;
    o.rows[c.mat]=row;
  });
  var EXPECT={obsidian:'obsidianPay', amber:'amberImmune', starstone:'starstoneExtra',
              silver:'silverBank', jade:'jadeScatter', vagabond:'vagabondSteal',
              bone:null, iron:null, flint:null, lead:null};
  Object.keys(EXPECT).forEach(function(mat){
    var r=o.rows[mat], want=EXPECT[mat];
    var on=Object.keys(r.fired).filter(function(k){return r.fired[k];});
    r.verbsFired=on;
    r.exactlyRight = want ? (on.length===1 && on[0]===want) : (on.length===0);
    if(!r.exactlyRight)o.crossContamination.push({mat:mat, want:want, got:on});
  });
  o.allSeven=['obsidian','amber','starstone','silver','jade','vagabond','bone']
    .every(function(m){return o.rows[m].exactlyRight;});
  o.jadeNeverPaysObsidian = o.rows.jade.d_turnPts===0 &&
    o.rows.jade.keptMats.indexOf('obsidian:1000')<0;
  o.mundaneNoOp = ['bone','iron','flint','lead'].every(function(m){
    return o.rows[m].verbsFired.length===0 && o.rows[m].d_turnPts===0;});
  o.VERDICT=(o.allSeven && o.jadeNeverPaysObsidian && o.mundaneNoOp)?'PASS':'FAIL';
  return o;
});

/* ─────────────────────────────────────────────────────────────────────────
   RULING #24 — SILVER BUSTS ~0.55x AS OFTEN AS BONE (a RATIO, not a figure)
   ───────────────────────────────────────────────────────────────────────── */
wrap('SILVER_bust_ratio', function(){
  var o={n:20000, policies:{}};
  var six=function(m){return [m,m,m,m,m,m];};
  var noE=[null,null,null,null,null,null];
  var THRESH=[300,500,800,1200];
  var rows=[];
  THRESH.forEach(function(t){
    FSIM.installRng(SEED+t);
    var bone=FSIM.measureTurnBust(six('bone'),noE,t,o.n);
    FSIM.installRng(SEED+t);
    var silv=FSIM.measureTurnBust(six('silver'),noE,t,o.n);
    FSIM.installRng(SEED+t);
    var relic=FSIM.measureTurnBust(six('brutus_shield'),noE,t,o.n);
    var p1=silv.bust.p, p2=bone.bust.p, n=o.n;
    /* delta method on log(p1/p2) */
    var se=Math.sqrt((1-p1)/(n*p1)+(1-p2)/(n*p2));
    var lr=Math.log(p1/p2);
    rows.push({thresh:t,
      bone:{p:+(p2*100).toFixed(2), lo:+(bone.bust.lo*100).toFixed(2), hi:+(bone.bust.hi*100).toFixed(2)},
      silver:{p:+(p1*100).toFixed(2), lo:+(silv.bust.lo*100).toFixed(2), hi:+(silv.bust.hi*100).toFixed(2)},
      brutusRelic:{p:+(relic.bust.p*100).toFixed(2)},
      ratio:+(p1/p2).toFixed(4),
      ratioLo:+Math.exp(lr-1.96*se).toFixed(4),
      ratioHi:+Math.exp(lr+1.96*se).toFixed(4),
      rollsPerTurn:{bone:bone.rollsPerTurn, silver:silv.rollsPerTurn}});
  });
  o.byThreshold=rows;
  /* the SINGLE-ROLL rate too, since the brief's 49-50 / 26 pair reads like one */
  function singleRoll(mat,n){
    var cards=effectiveCards(), bust=0;
    for(var s=0;s<n;s++){
      var vals=[],ms=[],ds=[];
      for(var i=0;i<6;i++){var d={mat:mat,ench:null};d.val=_enchRollM(mat,null);
        vals.push(d.val);ms.push(mat);ds.push(d);}
      if(!anyScoring(vals,cards,ms,ds))bust++;
    }
    return ci(bust,n);
  }
  FSIM.installRng(SEED+99);
  o.singleRollSixDice={bone:singleRoll('bone',40000), silver:singleRoll('silver',40000)};
  o.singleRollRatio=+(o.singleRollSixDice.silver.p/o.singleRollSixDice.bone.p).toFixed(4);

  var mid=rows.filter(function(r){return r.thresh===500;})[0];
  o.headlineRatio=mid.ratio; o.headlineCI=[mid.ratioLo,mid.ratioHi];
  o.inBand_0_54_to_0_58 = rows.every(function(r){return r.ratio>=0.54&&r.ratio<=0.58;});
  o.ratioSpread=[Math.min.apply(null,rows.map(function(r){return r.ratio;})),
                 Math.max.apply(null,rows.map(function(r){return r.ratio;}))];
  o.silverAbsoluteVsBrief26 = rows.map(function(r){return r.thresh+':'+r.silver.p+'%';}).join(' ');
  o.VERDICT = (mid.ratioLo<=0.55&&mid.ratioHi>=0.55)?'PASS (0.55 inside the interval)':'MISMATCH';
  return o;
});

FSIM.loud();
FSIM.restoreRng();
R.limits=FSIM.LIMITS;
return R;
