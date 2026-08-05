/* ══════════════════════════════════════════════════════════════════════════
   sim_harness.js — the SHARED FARK sim harness (FSIM).

   An eval file for tools/shoot.js. Other eval files CONCATENATE this file in
   front of their own code (see the "HOW TO USE" block at the bottom) and then
   drive FSIM. Plain JS, no modules, no exports.

   WHAT IS REAL AND WHAT IS NOT — read this before trusting a number.

   REAL (the harness calls the shipped function, never a copy of it):
     faces        _rollD / _enchRollM / _rollTable / rollFace   (Silver's
                  weighted table, Still Waters' hush of it, and the enchant
                  face set all come from the game)
     scoring      scoreRoll, scoreSelection, _applyCommitBonuses
     bust gate    anyScoring (which itself asks _dieIsIcon), _anchorRescues
     bust save    _tryBustSave, then doBust — so WARD's halving, AMBER's
                  immunity, the Fang and Ill Omen tolls are the shipped ones
     bank         handleBank — every card/relic/famFire('bankBonus') hook
     icons        _splitIcons + _iconFire  (the universal rule, and every
                  ENCH_ICONS[k].fire body: Tithe, Ward, Snare, Break, Trade,
                  Snuff, Fog)
     badges       _ruleActive / _kindredActive / _stillWaters / _applySleeve /
                  _applyTell, all read by the real code that consumes them
     break        _breakDie + BREAK_TRIGGERS (all seven rows)
     removal      _removeDieAt (match-scoped splice + the loan hand-back)
     shatter      _dieEffect (so Still Waters is honoured) driving the real
                  Obsidian check
     families     famFire / CFX (turnStart, roll, bust, bank, bankBonus)
     turn start   startPTurn — Fair Trade loan expiry, Tar Pit, The Tab, …
     opponent     oppShouldBank, and the opponent's scoring is scoreRoll
     generation   generatePatron / RUNGS / newG / _enchInit / _iconFaces /
                  _iconFaceRoll / _wardOwned

   NOT REAL (stated so no one reads a modelled number as a measured one):
     1. TURN SEQUENCING. handleRoll and _afterRollImpl are animation-driven
        (a 480 ms setTimeout stands between the roll and afterRoll), so the
        harness re-creates their CONTROL FLOW — reroll free dice, shatter
        check, bust gate, commit, Break, Zero Hour, hot dice — while calling
        the real function at every rule. _FSIM_ROLL_SKIPS lists, in code, the
        afterRoll branches this flow does not reproduce; all of them are
        G.pCards-gated and G.pCards is empty in this build (effectiveCards()
        returns [] — the old card pool is retired), so they are unreachable
        anyway. Verified by FSIM.selfTest().
     2. THE OPPONENT TURN LOOP. runOppTurn is one long animation chain. The
        harness re-creates its loop and applies Snuff / Fog / Snare by reading
        the same G fields with the same one-turn windows, but the loop itself
        is harness code. The BANK DECISION and the SCORING inside it are the
        real oppShouldBank and scoreRoll.
     3. ZERO HOUR'S 700 ms CLOSE. _zeroHourClose schedules the turn's end on a
        timer; the harness reads G._zeroHourEnds and ends the turn itself. The
        rule is the game's, the timing is the harness's.
     4. INTERACTIVE CARD ACTIVES (Steady Hand, Fair Trade, Transmute, Encore,
        Powder Keg …). They need a tap. Passives fire normally through famFire.
     5. ANIMATION TIMERS. setTimeout/setInterval/rAF are dropped for the whole
        run so no animation tail fires into a match that has already moved on.
        Everything a dropped timer would have done is either cosmetic or is
        done by the harness itself (see 3).

   Anything the harness cannot reach it says so about, loudly, rather than
   substituting a model: see FSIM.LIMITS.

   VERIFIED LIVE — seed 20260731, ~12,000 matches, tools/sim_verify*.js.
   A call census over one 8,400-match run: scoreRoll 16.6M, scoreSelection
   5.2M, anyScoring 5.3M, _rollTable 19.4M, handleBank 33,385, doBust 34,835,
   _tryBustSave 34,835, startPTurn 62,768, _iconFire 67,686, _breakDie 6,959,
   _removeDieAt 6,959, oppShouldBank 98,982, famFire 346,208, _kindredActive
   52,580, _stillWaters 88.9M, generatePatron/newG 8,400 each. Nothing in
   that list is a harness copy.
   Headline, night-4 loadout vs a tier-3 patron, n=400 a side, same seed:
     bust 12.5-13.6% of turns (~1.0 busted turns a match) and a mean end-of-
     match bank of ~4,400 for the mid agents; ORACLE OTTO 89.8% [86.4-92.4]
     against RANDOM RANDY 2.5% [1.4-4.5]. Reproducible: the same seed replays
     the same matches (FSIM.selfTest checks this and reports it).
   Speed: ~250 matches a second. n=1000 is cheap; use it.
   ══════════════════════════════════════════════════════════════════════════ */
(function(){
'use strict';
if(window.FSIM&&window.FSIM.__v===2)return;

var F=window.FSIM={__v:2};

F.LIMITS=[
 'turn sequencing (handleRoll/_afterRollImpl) is re-created, not called',
 'opponent turn LOOP is re-created; oppShouldBank + scoreRoll inside it are real',
 'Zero Hour ends the turn synchronously instead of on its 700ms timer',
 'interactive card ACTIVES are never played (they need a tap); passives fire',
 'animation timers are dropped for the duration of a run'
];
/* afterRoll branches the harness flow does NOT reproduce. Every one is gated
   on G.pCards, and G.pCards is [] for every sim loadout, so none is reachable.
   Listed by name so a future build that revives the card pool sees the gap. */
var _FSIM_ROLL_SKIPS=['flintlock','finnicks_trick','loaded_die','gamblers_ghost',
 'gamblers_thumb','hot_streak','the_forge','last_stand','anchor','aldrics_vow',
 'second_wind','thick_skin','mabels_stitch','powder_keg','warm_hands'];
F.ROLL_SKIPS=_FSIM_ROLL_SKIPS;

/* ─────────────────────────── 1. SEEDED RNG ─────────────────────────── */
var _realRandom=Math.random;
F.seed=null;
function mulberry32(a){
  return function(){
    a=a+0x6D2B79F5|0;
    var t=Math.imul(a^a>>>15,1|a);
    t=t+Math.imul(t^t>>>7,61|t)^t;
    return ((t^t>>>14)>>>0)/4294967296;
  };
}
F.mulberry32=mulberry32;
/* Installs OVER Math.random, which is what every roll, every patron draw and
   every NPC coin-flip in the game calls. Nothing in the game is reseeded
   anywhere else, so one call here makes the whole run reproducible. */
F.installRng=function(seed){
  seed=(seed===undefined||seed===null)?0x5EEDFA24:(seed|0);
  F.seed=seed>>>0;
  Math.random=mulberry32(seed);
  return F.seed;
};
F.restoreRng=function(){Math.random=_realRandom;};
/* a private stream, for harness bookkeeping that must not consume game rolls */
F.aux=mulberry32(0x0BADF00D);

/* ───────────────────── 2. WILSON 95% INTERVAL ──────────────────────── */
/* A rate without one of these is not a result. Wilson, not normal-approx:
   at n=200 with p near 0 or 1 the normal interval runs off the end of [0,1]
   and reports impossible bounds. */
F.ci95=function(k,n){
  if(!n)return{p:0,lo:0,hi:0,n:0,k:0,halfWidth:0};
  var z=1.959963985,ph=k/n,z2=z*z;
  var den=1+z2/n;
  var ctr=(ph+z2/(2*n))/den;
  var rad=(z*Math.sqrt(ph*(1-ph)/n+z2/(4*n*n)))/den;
  return{p:+(ph).toFixed(6),lo:+Math.max(0,ctr-rad).toFixed(6),
         hi:+Math.min(1,ctr+rad).toFixed(6),n:n,k:k,
         halfWidth:+((Math.min(1,ctr+rad)-Math.max(0,ctr-rad))/2).toFixed(6)};
};
/* the same thing for a mean: normal interval on the sample sd */
F.ciMean=function(arr){
  var n=arr.length;if(!n)return{mean:0,lo:0,hi:0,n:0,sd:0};
  var m=0;for(var i=0;i<n;i++)m+=arr[i];m/=n;
  var v=0;for(i=0;i<n;i++)v+=(arr[i]-m)*(arr[i]-m);
  v=n>1?v/(n-1):0;var sd=Math.sqrt(v),se=sd/Math.sqrt(n);
  return{mean:+m.toFixed(2),lo:+(m-1.959963985*se).toFixed(2),
         hi:+(m+1.959963985*se).toFixed(2),n:n,sd:+sd.toFixed(2)};
};
F.median=function(arr){
  if(!arr.length)return 0;
  var a=arr.slice().sort(function(x,y){return x-y;});
  var h=a.length>>1;
  return a.length%2?a[h]:(a[h-1]+a[h])/2;
};

/* ──────────────── 3. QUIET MODE — drop timers and noise ─────────────── */
/* Only two categories are replaced: (a) schedulers, so no animation tail can
   fire into a match that has already been torn down and rebuilt, and (b)
   sound/particles/localStorage, which cost real time at 10^5 calls and carry
   no rule. Every function that decides anything stays exactly as shipped. */
var _saved=null;
var _QUIET_FN=['spawnPop','spawnBankPop','spawnPixelSparks','spawnObsidianBurst',
  'spawnSawdust','showCritFlash','flashYourTurn','_bustImpact','save','saveMatchState',
  '_alignOverlayWord',
  /* P471: side-effect-only - no return value, no caller consuming one, no
     writes to G or S. updHUD is NOT here on purpose: it writes
     G._featMaxDeficit, which a feat condition reads. */
  'triggerCard','setStatusMsg','famLog'];
F.quiet=function(){
  if(_saved)return;
  _saved={setTimeout:window.setTimeout,setInterval:window.setInterval,
          requestAnimationFrame:window.requestAnimationFrame,fns:{},sfx:{},hap:{}};
  window.setTimeout=function(){return 0;};
  window.setInterval=function(){return 0;};
  window.requestAnimationFrame=function(){return 0;};
  _QUIET_FN.forEach(function(n){
    if(typeof window[n]==='function'){_saved.fns[n]=window[n];window[n]=function(){};}
  });
  ['SFX','Haptic'].forEach(function(o){
    var box=window[o];if(!box)return;
    var store=(o==='SFX')?_saved.sfx:_saved.hap;
    Object.keys(box).forEach(function(k){
      if(typeof box[k]==='function'){store[k]=box[k];box[k]=function(){};}
    });
  });
  window.__FSIM_QUIET=true;
};
F.loud=function(){
  if(!_saved)return;
  window.setTimeout=_saved.setTimeout;window.setInterval=_saved.setInterval;
  window.requestAnimationFrame=_saved.requestAnimationFrame;
  Object.keys(_saved.fns).forEach(function(n){window[n]=_saved.fns[n];});
  Object.keys(_saved.sfx).forEach(function(k){window.SFX[k]=_saved.sfx[k];});
  Object.keys(_saved.hap).forEach(function(k){window.Haptic[k]=_saved.hap[k];});
  _saved=null;window.__FSIM_QUIET=false;
};

/* ───────────── 4. REACHING `G` — it is a top-level `let` ───────────── */
/* `let G` lives in the global LEXICAL environment, so it is NOT a property of
   window and `window.G=x` silently writes a different variable (which is a
   real bug in the shipped _runBalanceSim: its `window.G=null` never neutralised
   anything). Indirect eval runs in global scope and CAN see that binding. */
function setG(g){window.__FSIM_G=g;(0,eval)('G = window.__FSIM_G');return getG();}
function getG(){return (0,eval)('G');}
F.setG=setG;F.getG=getG;

/* a real, detached element per seat, so the shipped code's unguarded
   d.el.classList / d.el.onclick writes land somewhere harmless */
var _elPool=[];
function elFor(i){
  if(!_elPool[i]){var e=document.createElement('div');e.className='die';_elPool[i]=e;}
  var e=_elPool[i];e.className='die';e.onclick=null;return e;
}

/* ─────────────────────── 5. GEAR AND MATCH SETUP ───────────────────── */
/* Night-1 and night-8 reference loadouts for the POWER lens. Materials only —
   the harness never invents a die type, it names ones the game ships. */
F.GEAR={
  night1:{key:'night1',dice:['bone','bone','bone','bone','bone','bone'],
          ench:[null,null,null,null,null,null],badge:null,fcards:[]},
  night4:{key:'night4',dice:['amber','amber','silver','iron','bone','bone'],
          ench:['tithe',null,'ward',null,null,null],badge:null,
          fcards:[{id:'slow_cook',tier:1}]},
  night8:{key:'night8',dice:['jade','jade2','amber','amber','silver','starstone'],
          ench:['tithe','ward','snare','break','trade','fog'],badge:'kindred',
          fcards:[{id:'slow_cook',tier:3},{id:'falling_star',tier:3},{id:'pickpocket',tier:3}]}
};
/* THE IDS AND THE RULES MATCH NOW (P427/P428), so this map is an identity -
   and that is the point. It existed only to paper over a divergence where a
   badge showed one rule name and keyed on another, which is what got removed.
   Kept as a table, not deleted, so an agent still has one place to name a rule.

   IT WAS WRONG IN TWO WAYS BEFORE THIS, both silent:
     kindred/still_waters/first_strike pointed at counterfeit/confession/
     in_arrears, none of which resolves any more - _tellById returns null and
     the badge is simply not applied. GEAR.night8 asks for Kindred, so every
     night-8 batch would have run BARE while reporting itself as a Kindred build.
     zero_hour pointed at 'last_call', which is worse than a no-op: after P427
     that is a LIVE rule again (Grog's LAST CALL, voids a bank under 800). The
     harness would have measured a bank-void rule and labelled it Zero Hour. */
F.BADGE={zero_hour:'zero_hour',kindred:'kindred',still_waters:'still_waters',
         first_strike:'first_strike',last_call:'last_call',
         steeped:'steeped',pickpocket:'pickpocket',
         drill_order:'drill_order',reckoning:'reckoning'};

/* Build a brand the way the SHOP builds one: the face is drawn by the real
   _iconFaceRoll from the real _iconFaces set. If the die has no legal face the
   sale is refused, exactly as the shop refuses it — the harness never invents
   a face, which is the whole point of the 1/5 check. */
F.mkEnch=function(mat,type){
  if(!type)return null;
  if(type==='quicksilver')return{t:'quicksilver'};
  var f=_iconFaceRoll(mat);
  if(f===null||f===undefined)return null;
  return{t:type,face:f};
};

/* Turn a gear spec into the two run arrays. Honours the shipped one-Ward
   loadout cap by asking the real _wardOwned as it goes, so a gear spec that
   asks for two Wards produces one — and reports that it did. */
F.buildLoadout=function(spec){
  _getS();
  var dice=(spec.dice||['bone','bone','bone','bone','bone','bone']).slice(0,6);
  while(dice.length<6)dice.push('bone');
  S.run.dice=dice.slice();
  S.run.dieEnch=[null,null,null,null,null,null];
  S.run.dieEnchInv=[];
  /* THE SHIPPED MIGRATIONS' TARGET VERSIONS, and they are NOT the same number.
     _enchInit guards on `_enchV!==3` and `_enchTradeV!==1` - two independent
     keys on purpose (fark_proto.html:17947 explains why). This line used to
     write 2 for the Trade key, which does not satisfy that guard, it trips it:
     the legacy-Trade pass then nulled every {t:'trade'} brand and refunded 350g
     before a single match was played. newG calls _enchInit() unconditionally
     right after this function, so EVERY Trade measurement made with this
     harness measured an empty lane, with an inflated gold curve on top.
     If either guard changes in the game, these two numbers must follow. */
  S.run._enchV=3;S.run._enchTradeV=1;
  var refused=[];
  (spec.ench||[]).forEach(function(t,i){
    if(!t||i>5)return;
    if(t==='ward'&&_wardOwned(i)){refused.push({lane:i,t:t,why:'ward cap'});return;}
    var e=F.mkEnch(dice[i],t);
    if(!e){refused.push({lane:i,t:t,why:'no legal face'});return;}
    S.run.dieEnch[i]=e;
  });
  return{dice:dice.slice(),ench:S.run.dieEnch.slice(),refused:refused};
};

/* Build a REAL match. rung comes from the real generator; G comes from the
   real newG; the brand array is copied the way initMatchScreen copies it. */
F.setupMatch=function(o){
  o=o||{};
  var tier=(o.tier==null)?3:o.tier;
  _getS();
  S.run.tier=tier;
  S.run.gold=(o.gold==null)?0:o.gold;
  S.run.fcards=(o.fcards||[]).slice();
  S.run.diceInv=(o.diceInv||[]).slice();
  S.run.sleeve=o.badge||null;
  S.run.tells=[];
  S.run._grudges=null;
  S.run._hotdNext=false;
  var lo=F.buildLoadout(o);
  var rung=o.rung||(o.boss?RUNGS[tier]:generatePatron(tier));
  if(o.boss)rung=Object.assign({},RUNGS[tier]);/* per-match copy: newG keeps a ref */
  /* P472 - THE PATRON'S CARDS, dealt the way the game deals them.
     This read `rung.cards`, AND NO RUNG HAS THAT FIELD - not one boss, not one
     generated patron. They carry cardPool / cardCount / cardChance, which
     generateOppCards turns into an actual list. So oCards was ALWAYS [] and
     the sim has never modelled a patron holding cards at all, on any run.
     That is why wiring the card effects in P471 changed nothing: the effects
     were correct and there was simply nothing to fire them on. Two independent
     causes of the same silence, and only fixing both makes a difference. */
  var oCards=(typeof generateOppCards==='function')
    ? (generateOppCards(rung,(lo&&lo.cards?lo.cards.length:0))||[]).slice()
    : (rung.cards||[]).slice();
  var g=newG(rung,[],oCards,0,0);
  setG(g);
  /* DID THE BUILD SURVIVE newG? newG runs _enchInit(), which is where the save
     migrations live, and a migration can legally delete a brand. This used to
     copy S.run.dieEnch straight into _enchArr - AFTER that had happened - so
     the harness's own record agreed with the damage and nothing ever compared
     what was ASKED FOR against what was STANDING. That is how a wrong
     _enchTradeV silently emptied every Trade lane in the whole sim: the numbers
     looked fine.
     `refused` is buildLoadout declining to fit a brand. `lost` is a brand that
     WAS fitted and then removed by something downstream. They are different
     failures and they are reported separately. */
  var _lost=[];
  (lo.ench||[]).forEach(function(e,i){
    if(e&&!(S.run.dieEnch||[])[i])_lost.push({lane:i,t:e.t,why:'removed by _enchInit'});
  });
  if(_lost.length)lo.lost=_lost;
  g._enchArr=(S.run.dieEnch||[]).slice();
  g.turnCap=o.boss?TURN_CAP_BOSS:TURN_CAP_PATRON;
  g.phase='idle';
  try{_applyTellAndSleeve();}catch(e){}
  _elPool.length=0;
  return{g:g,rung:rung,loadout:lo,target:g.target,
         /* surfaced at the top level too - a caller reading only the summary
            still cannot miss that the build it asked for is not the build that
            was measured. */
         lostEnch:lo.lost||null,
         badgeLive:o.badge?_ruleActive(o.badge,'p'):false};
};

/* ────────────────────── 6. THE PLAYER TURN ─────────────────────────── */
/* Roll: mirrors handleRoll's dice bookkeeping exactly (same lane arithmetic,
   same "reroll the free ones, top up the rest"), rolling every face with the
   game's own roller so weighting, brands and Still Waters all apply. */
function rollPool(){
  var G=getG();
  var before=G.pool.length;
  var need=G.numDice-before;
  G.pool.forEach(function(d){
    if(d.committed||d._frozen)return;
    d.val=_rollD(d);d.sel=false;
  });
  for(var i=0;i<need;i++){
    var lane=(before+i)%G.matchDice.length;
    var mat=G.matchDice[lane]||'bone';
    var en=(G._enchArr||[])[lane]||null;
    G.pool.push({val:_enchRollM(mat,en),mat:mat,ench:en,sel:false,committed:false,
                 el:elFor(before+i),lane:lane});
  }
}

/* afterRoll's rule-bearing half. Returns 'ok' | 'bust' | 'saved'. */
function afterRollLite(){
  var G=getG();
  try{famFire('roll',{actor:'p',rolls:G.turnRollCount||0});}catch(e){}
  G.turnRollCount++;
  /* the real Obsidian check, through _dieEffect so Still Waters hushes it and
     through _removeDieAt so the removal is match-scoped and lane-correct */
  var pre=G.pool.filter(function(d){return !d.committed;});
  if(pre.some(function(d){var e=_dieEffect(d);return e&&e.mechanic==='shatter_bonus';})){
    pre.forEach(function(d){
      var fx=_dieEffect(d);
      if(!fx||fx.mechanic!=='shatter_bonus'||d._shattered)return;
      if(Math.random()<(fx.chance||0.06)){
        d._shattered=true;G.pPts+=(fx.amount||500);
        d._shatterLane=(d.lane!==undefined?d.lane:-1);
      }
    });
    var lanes=G.pool.filter(function(d){return d._shattered;})
      .map(function(d){return d._shatterLane!==undefined?d._shatterLane:d.lane;})
      .filter(function(L){return L!==undefined&&L>=0;}).sort(function(a,b){return b-a;});
    if(lanes.length)lanes.forEach(function(L){_removeDieAt(L,{permanent:false});});
    else G.pool=G.pool.filter(function(d){return !d._shattered;});
  }
  var free=G.pool.filter(function(d){return !d.committed;});
  var vals=free.map(function(d){return d.val;});
  var mats=free.map(function(d){return d.mat;});
  var cards=effectiveCards();
  if(!anyScoring(vals,cards,mats,free)&&!_anchorRescues(cards)){
    /* SHIPPED-COMPAT: not a rule, an emulation of a KNOWN STALE assumption in
       the game's own in-file _runBalanceSim (it grants one free bust-save a
       turn for owning a silver die — Silver's deleted identity). Off by
       default; used once, by sim_verify, to prove the gap between the two
       harnesses is that stale assumption and not a bug in this one. */
    if(F.__shippedCompat&&_compatSaveLeft>0){_compatSaveLeft--;return 'compatsave';}
    if(_tryBustSave(free))return 'saved';
    doBust();
    return G._bustImmuneTurn?'ok':'bust';
  }
  G.phase='choosing';
  return 'ok';
}
var _compatSaveLeft=0;
F.__shippedCompat=false;

/* The commit, exactly as the roll commit runs it: split the icons out, score
   the rest with the real engine, apply the real per-commit bonuses, fire each
   icon through the real universal rule. Returns pts, or -1 if the engine
   refused the selection. */
function commit(sel){
  var G=getG();
  if(!sel||!sel.length)return 0;
  var sp=_splitIcons(sel),icons=sp.icons,rest=sp.rest;
  var v=rest.map(function(d){return d.val;});
  var m=rest.map(function(d){return d.mat;});
  var en=rest.map(function(d){return d.ench||null;});
  var locked=G.kept.reduce(function(a,k){return a+k.pts;},0);
  var cards=effectiveCards();
  var ctx=_pCrowsForScore()||{};
  ctx._bookendsEligible=_bookendsEligible(sel);
  var pts=rest.length?scoreSelection(v,cards,locked,ctx,m,en):0;
  if(rest.length===0&&icons.length)pts=0;
  /* THE SHIPPED ACCEPT RULE. This used to carry `if(pts<0&&icons.length)pts=0;`
     - a verbatim copy of a line the game has since removed (P404), which
     means this harness was measuring a REPLICA of the rule rather than the
     rule. `rest` is already the non-icon half, so pts<0 says that half is
     illegal on its own and an icon riding along must not forgive it. */
  if(pts<0||(pts===0&&!icons.length))return -1;
  _pCrowsCommit(ctx);
  pts=_applyCommitBonuses(rest,pts,cards);
  icons.forEach(function(d){_iconFire(d,'p');});
  sel.forEach(function(d){
    d.committed=true;d._frozen=false;d.sel=false;
    if(d.el){d.el.classList.remove('selected','die-frozen');d.el.classList.add('committed');d.el.onclick=null;}
  });
  if(pts>0||rest.length)
    G.kept.push({vals:v,mat:sel[0].mat,pts:pts,
      dice:sel.map(function(d){return{val:d.val,mat:d.mat};})});
  G.turnPts=G.kept.reduce(function(a,k){return a+k.pts;},0)+(G._turnBonusPot||0);
  if((G.turnRollCount||0)===1)G._firstRollCommitted=(G._firstRollCommitted||0)+v.length;
  return pts;
}

/* Every subset of the free dice the real engine will actually accept. Capped
   at 6 free dice = 63 subsets, which is the whole space. */
function legalKeeps(free){
  var G=getG(),out=[];
  var n=free.length;if(!n)return out;
  var locked=G.kept.reduce(function(a,k){return a+k.pts;},0);
  var cards=effectiveCards();
  for(var m=1;m<(1<<n);m++){
    var sel=[];
    for(var i=0;i<n;i++)if(m&(1<<i))sel.push(free[i]);
    var sp=_splitIcons(sel),rest=sp.rest;
    var ctx=_pCrowsForScore()||{};
    ctx._bookendsEligible=_bookendsEligible(sel);
    var pts=rest.length?scoreSelection(rest.map(function(d){return d.val;}),cards,locked,ctx,
      rest.map(function(d){return d.mat;}),rest.map(function(d){return d.ench||null;})):0;
    if(rest.length===0&&sp.icons.length)pts=0;
    /* same shipped rule as above - no icon forgiveness for a dead half */
    if(pts<0||(pts===0&&!sp.icons.length))continue;
    out.push({sel:sel,pts:pts,icons:sp.icons.length,left:n-sel.length});
  }
  return out;
}
F.legalKeeps=legalKeeps;

/* the "keep every scoring die" baseline, read off the real engine's own `used`
   array rather than guessed at */
F.allScorers=function(free){
  var cards=effectiveCards();
  var r=scoreRoll(free.map(function(d){return d.val;}),cards,0,{},
                  free.map(function(d){return d.mat;}),
                  free.map(function(d){return d.ench||null;}));
  var sel=[];
  for(var i=0;i<free.length;i++)if(r.used&&r.used[i])sel.push(free[i]);
  free.forEach(function(d){if(_dieIsIcon(d)&&sel.indexOf(d)<0)sel.push(d);});
  return sel;
};

/* ONE PLAYER TURN.
   policy: see §7. state: {turnsLeft, oppTotal, lastTurn}
   returns {banked, busted, rolls, iconsFired, hot, zeroHour, saved} */
F.simTurn=function(policy,state){
  state=state||{};
  var G=getG();
  var pBefore=G.pPts;
  var res={banked:0,busted:false,rolls:0,iconsFired:0,hot:0,zeroHour:false,saved:false,err:null};
  try{startPTurn();}catch(e){res.err='startPTurn: '+e.message;}
  G=getG();
  if(G._endMatchFired)return res;
  G.phase='idle';
  _compatSaveLeft=F.__shippedCompat?1:0;
  var guard=0;
  while(guard++<60){
    rollPool();
    res.rolls++;
    var st=afterRollLite();
    if(st==='bust'){res.busted=true;break;}
    if(st==='compatsave'){try{handleBank();}catch(e){}break;}
    if(st==='saved'){res.saved=true;
      /* _tryBustSave cleared the free dice and set phase idle: the real code
         then auto-rolls after 1.7s. Same thing, without the wait. */
      if(G.kept.length&&policy.bankAt({turnPts:G.turnPts,diceLeft:0,rolls:res.rolls,
        state:state,G:G})){break;}
      continue;}
    G=getG();
    var free=G.pool.filter(function(d){return !d.committed;});
    var keeps=legalKeeps(free);
    if(!keeps.length){/* engine says nothing is committable — treat as bust */
      doBust();res.busted=true;break;}
    var sel=policy.keep(free,{keeps:keeps,G:G,state:state,rolls:res.rolls});
    if(!sel||!sel.length)sel=keeps[keeps.length-1].sel;
    var got=commit(sel);
    if(got<0){sel=F.allScorers(free);got=commit(sel);}
    if(got<0){doBust();res.busted=true;break;}
    res.iconsFired+=_splitIcons(sel).icons.length;
    G=getG();
    /* BREAK: the real arm/fire pair. _breakBegin needs live tap handlers, so
       the target is chosen here and handed straight to the real _breakDie. */
    if(G._breakPending){
      var bp=G._breakPending;G._breakPending=null;
      var cands=G.pool.filter(function(d){return !d.committed&&d!==bp.src&&!_breakPreserved(d);});
      if(cands.length){
        var t=(policy.breakTarget?policy.breakTarget(cands,{G:G,state:state}):cands[0])||cands[0];
        G._breakArmed=true;
        try{_breakDie(t);}catch(e){res.err=(res.err||'')+'|break: '+e.message;}
        G=getG();
        if(G._breakBankNow){/* SILVER row: banks the turn where it stands */
          G._breakBankNow=false;
          try{handleBank();}catch(e){}
          G=getG();res.banked=G.pPts-pBefore;res.hot=G._featHotDiceCount||0;return res;
        }
      }
    }
    if(G._zeroHourEnds){
      G._zeroHourEnds=false;res.zeroHour=true;
      var tp=(G.kept||[]).reduce(function(a,k){return a+(k.pts||0);},0)+(G._turnBonusPot||0);
      if(tp>0){try{handleBank();}catch(e){res.err=(res.err||'')+'|bank: '+e.message;}}
      else{G.pool=[];G.turnPts=0;G.kept=[];}
      break;
    }
    /* hot dice — the real rule: all six committed means a fresh six */
    if(G.pool.filter(function(d){return !d.committed;}).length===0&&G.pool.length>0){
      G.pool=[];G.numDice=G.matchDice?G.matchDice.length:6;
      G._lastHotDice=true;G._featHotDiceCount=(G._featHotDiceCount||0)+1;
      /* the shipped hot-dice bonus. The game's own _runBalanceSim omits it —
         see __shippedCompat. */
      if(!F.__shippedCompat)G._turnBonusPot=(G._turnBonusPot||0)+250;
      G.turnPts=G.kept.reduce(function(a,k){return a+k.pts;},0)+(G._turnBonusPot||0);
      res.hot++;
      continue;
    }
    var leftN=G.pool.filter(function(d){return !d.committed;}).length;
    if(policy.bankAt({turnPts:G.turnPts,diceLeft:leftN,rolls:res.rolls,state:state,G:G})){
      try{handleBank();}catch(e){res.err=(res.err||'')+'|bank: '+e.message;}
      break;
    }
  }
  G=getG();
  res.banked=Math.max(0,G.pPts-pBefore);
  if(res.busted)res.banked=Math.max(0,G.pPts-pBefore);/* a Ward half still lands */
  return res;
};

/* ─────────────────── 6b. THE OPPONENT TURN (loop re-created) ────────── */
/* runOppTurn is an animation chain end to end. This reproduces its LOOP and
   its Snuff/Fog/Snare handling, and calls the real oppShouldBank and the real
   scoreRoll for every decision and every point. */
F.oppTurn=function(){
  var G=getG();
  var out={banked:0,busted:false,rolls:0,snuffed:false,fogged:false,snared:false};
  G.oppTurnCount=(G.oppTurnCount||0)+1;
  ['_snare','_fog','_snuff'].forEach(function(k){
    if(G[k]&&G[k].live&&G.oppTurnCount>(G[k].turn||0)+1)G[k]=null;
  });
  var dice=(G.matchOppDice||[]).slice();
  var snuffLane=-1;
  if(G._snuff&&G._snuff.live){
    snuffLane=G._snuff.lane;
    G._snuff.turns=(G._snuff.turns||1)-1;
    if(G._snuff.turns>0)G._snuff.turn=(G.oppTurnCount||0)+1;
    else G._snuff.live=false;
  }
  var seats=[];
  for(var i=0;i<dice.length;i++){
    if(i===snuffLane&&dice.length>1){out.snuffed=true;continue;}
    seats.push({mat:dice[i],lane:i});
  }
  var bank=0,rolls=0,live=seats.slice();
  var guard=0;
  while(guard++<40){
    rolls++;
    live.forEach(function(s){s.val=rollFace(s.mat);});
    var vals=live.map(function(s){return s.val;});
    var mats=live.map(function(s){return s.mat;});
    /* FOG: hide one seat from the reckoning the NPC already runs */
    var fV=vals.slice(),fM=mats.slice(),fogIdx=-1;
    if(G._fog&&G._fog.live&&G._fog.turn===G.oppTurnCount){
      for(var j=0;j<live.length;j++)if(live[j].lane===G._fog.lane){fogIdx=j;break;}
      if(fogIdx>=0&&fV.length>1){fV.splice(fogIdx,1);fM.splice(fogIdx,1);out.fogged=true;}
      G._fog.turns=(G._fog.turns||1)-1;
      if(G._fog.turns>0)G._fog.turn=(G.oppTurnCount||0)+1;
      else G._fog.live=false;
    }
    var r=scoreRoll(fV,G.oCards||[],bank,G.crowsLuckCtx||{},fM);
    var total=r.total,used=r.used;
    /* SNARE: their die in the marked seat is halved once if it scores */
    if(G._snare&&G._snare.live&&G._snare.turn===G.oppTurnCount){
      var si=-1;
      for(var k2=0;k2<live.length;k2++)if(live[k2].lane===G._snare.lane){si=k2;break;}
      /* index shift: `used` is indexed against the fogged array */
      var ui=(fogIdx>=0&&si>fogIdx)?si-1:si;
      if(total>0&&si>=0&&ui>=0&&used&&used[ui]){
        total=Math.floor(total/(G._snare.x2?4:2));
        G._snare.live=false;out.snared=true;
      }
    }
    if(!total||total<=0){out.busted=true;out.rolls=rolls;bank=0;break;}
    bank+=total;
    var keptIdx={};
    for(var q=0;q<fV.length;q++)if(used&&used[q])keptIdx[q]=1;
    var nextLive=[];
    var fi=0;
    for(var w=0;w<live.length;w++){
      if(w===fogIdx){nextLive.push(live[w]);continue;}/* unseen seat is never kept */
      if(!keptIdx[fi])nextLive.push(live[w]);
      fi++;
    }
    if(!nextLive.length){live=seats.slice();if(bank<3000)continue;}
    else live=nextLive;
    if((G.oPts+bank)>=G.target)break;
    if(oppShouldBank(G.rung,bank,live.length,G.oPts,G.pPts,G.target))break;
  }
  out.rolls=rolls;
  /* P471 - THE PATRON'S CARD EFFECTS, in finOpp's exact order. Without these
     the sim modelled a game where no bank-triggered card fired for either seat:
     three of the nine are the patron's own, six are the PLAYER's taking from
     the patron's bank. Guarded on !busted because finOpp is only called when
     the patron banks. Guarded on typeof so an older page still runs. */
  if(!out.busted){
    if(typeof _oppFxOwnA==='function')  bank=_oppFxOwnA(bank);
    if(typeof _oppFxOwnB==='function')  bank=_oppFxOwnB(bank);
    if(typeof _oppFxPlayer==='function')bank=_oppFxPlayer(bank);
    G.oPts=(G.oPts||0)+bank;out.banked=bank;
    if(typeof _oppFxDrain==='function') _oppFxDrain();
  }
  /* the field Break's Vagabond row reads; finOpp writes it at exactly this
     moment on the real path */
  G._oLastBank=out.busted?0:bank;
  G.oTurns=(G.oTurns||0)+1;
  return out;
};

/* ─────────────────────────── 6c. A MATCH ───────────────────────────── */
/* opts: {tier, boss, gear, badge, fcards, playerFirst, rung}
   returns {won, playerBank, oppBank, turns, ...} */
F.simMatch=function(policy,opts){
  opts=opts||{};
  var spec=opts.gear||F.GEAR.night1;
  var tierN=opts.tier==null?3:opts.tier;
  /* THE PEEK, AND WHAT IT BUYS. The rival is generated FIRST — that is exactly
     what the pre-match peek shows the player — and the policy is given their
     six lane materials before the loadout is locked. A policy with no
     lanePlan (or a policy that returns the identity order) is unaffected, so
     any difference between two agents here is the planning system's doing and
     nothing else's. */
  var rung=opts.rung||(opts.boss?RUNGS[tierN]:generatePatron(tierN));
  var dice=(spec.dice||[]).slice(),ench=(spec.ench||[]).slice();
  var planned=null;
  if(policy.lanePlan&&opts.lanePlan!==false){
    try{
      var plan=policy.lanePlan((rung.dice||[]).slice(),{dice:dice.slice(),ench:ench.slice()});
      if(plan&&plan.length===6){
        var nd=[],ne=[];
        for(var pi=0;pi<6;pi++){nd.push(dice[plan[pi]]);ne.push(ench[plan[pi]]||null);}
        dice=nd;ench=ne;planned=plan;
      }
    }catch(e){}
  }
  var set=F.setupMatch({tier:tierN,boss:!!opts.boss,
    dice:dice,ench:ench,badge:opts.badge||spec.badge||null,
    fcards:opts.fcards||spec.fcards||[],diceInv:opts.diceInv||[],
    gold:opts.gold||0,rung:rung});
  var G=getG();
  var cap=G.turnCap||TURN_CAP_PATRON;
  var playerFirst=(opts.playerFirst===undefined)?true:!!opts.playerFirst;
  var pTurns=0,oTurns=0,busts=0,rolls=0,icons=0,hots=0,zh=0,saves=0;
  var pBanks=[],turnGold0=(S.run.gold||0);
  var guard=0,decided=null,capEnd=false;
  var order=playerFirst?['p','o']:['o','p'];
  while(guard++<80&&decided===null){
    for(var k=0;k<2;k++){
      var side=order[k];
      G=getG();
      if(side==='p'){
        if(G.pPts>=G.target){decided=true;break;}
        var extra=1;
        while(extra-->0){
          /* informed-Greg needs to know whether a future turn exists */
          var lastTurn=(pTurns+1>=cap)||((G.oPts>=G.target));
          var t=F.simTurn(policy,{lastTurn:lastTurn,turnsLeft:cap-pTurns,
            oppTotal:G.oPts,target:G.target});
          pTurns++;rolls+=t.rolls;icons+=t.iconsFired;hots+=t.hot;
          if(t.zeroHour)zh++;if(t.saved)saves++;
          if(t.busted)busts++;else if(t.banked>0)pBanks.push(t.banked);
          G=getG();
          G.turnNum++;G.pTurns=pTurns;
          if(G._extraTurn>0){G._extraTurn--;extra++;}
          if(G.pPts>=G.target){decided=true;break;}
        }
        if(decided!==null)break;
      }else{
        if(G.oPts>=G.target){decided=false;break;}
        F.oppTurn();oTurns++;
        G=getG();
        if(G.oPts>=G.target){
          /* the player's answering turn, exactly as the real match grants it */
          if(G.pPts>=G.target){decided=G.pPts>G.oPts;break;}
          var t2=F.simTurn(policy,{lastTurn:true,turnsLeft:1,oppTotal:G.oPts,target:G.target});
          pTurns++;rolls+=t2.rolls;icons+=t2.iconsFired;
          if(t2.busted)busts++;else if(t2.banked>0)pBanks.push(t2.banked);
          G=getG();G.pTurns=pTurns;
          decided=(G.pPts>G.oPts);break;
        }
      }
    }
    G=getG();
    if(decided===null&&pTurns>=cap&&oTurns>=cap){
      if(G.pPts===G.oPts){if(guard>cap+6){decided=true;capEnd=true;}continue;}
      decided=(G.pPts>G.oPts);capEnd=true;
    }
  }
  G=getG();
  if(decided===null)decided=(G.pPts>=G.oPts);
  G._endMatchFired=true;
  /* the real match-end restores of Trade and Break */
  var restored=0;
  try{if(typeof _tradeRestore==='function')restored=_tradeRestore()||0;}catch(e){}
  return{won:!!decided,playerBank:G.pPts,oppBank:G.oPts,turns:pTurns,oppTurns:oTurns,
         busts:busts,rolls:rolls,icons:icons,hots:hots,zeroHour:zh,bustSaves:saves,
         capEnd:capEnd,target:G.target,banks:pBanks,
         goldGained:(S.run.gold||0)-turnGold0,tradesRestored:restored,
         lanePlan:planned,
         rung:(set.rung.gname||set.rung.name||'?'),loadoutRefused:set.loadout.refused};
};

/* ───────────────────── 7. THE POLICY INTERFACE ──────────────────────── */
/*  {
      name,
      bankAt({turnPts,diceLeft,rolls,state,G}) -> bool
      keep(freeDice,{keeps,G,state,rolls})     -> array of dice to commit
      draft(offer,{G,S,owned})                 -> index into offer
      enchant(choice,{owned,gold})             -> enchant key or null
      lanePlan(peek,{dice,ench})               -> array of lane indices
      breakTarget(cands,{G,state})             -> one of cands   (optional)
    }
  Agents differ by DECISIONS, not by code: every policy runs through the same
  F.simTurn / F.simMatch above.                                              */

function pick(arr){return arr[(Math.random()*arr.length)|0];}
/* the highest-scoring legal keep, then the one that keeps most dice alive */
function bestPts(keeps){
  var b=keeps[0];
  for(var i=1;i<keeps.length;i++){
    if(keeps[i].pts>b.pts||(keeps[i].pts===b.pts&&keeps[i].left>b.left))b=keeps[i];
  }
  return b.sel;
}
/* the smallest keep that scores at all — maximum dice left */
function leanest(keeps){
  var b=null;
  for(var i=0;i<keeps.length;i++){
    if(keeps[i].pts<=0)continue;
    if(!b||keeps[i].sel.length<b.sel.length||
       (keeps[i].sel.length===b.sel.length&&keeps[i].pts>b.pts))b=keeps[i];
  }
  return (b||keeps[0]).sel;
}
/* keeps that fire an icon, preferred; used by the enchant-leaning agents */
function withIcons(keeps){
  var ic=keeps.filter(function(k){return k.icons>0;});
  return ic.length?ic:null;
}

function mkPolicy(o){
  var p={
    name:o.name,
    thresh:o.thresh,
    bankAt:o.bankAt||function(c){
      if(c.G.pPts+c.turnPts>=c.G.target)return true;
      if(c.diceLeft<=0)return true;
      if(c.state&&c.state.lastTurn&&c.state.oppTotal!=null&&
         c.G.pPts+c.turnPts>c.state.oppTotal&&c.diceLeft<=3)return true;
      if(c.diceLeft<=2&&c.turnPts>=Math.max(100,o.thresh*0.4))return true;
      if(c.turnPts>=o.thresh&&c.diceLeft<=4)return true;
      return c.turnPts>=o.thresh*2;
    },
    keep:o.keep||function(f,c){return bestPts(c.keeps);},
    draft:o.draft||function(offer){return 0;},
    enchant:o.enchant||function(ch){return ch&&ch.length?ch[0]:null;},
    lanePlan:o.lanePlan||function(peek,c){return [0,1,2,3,4,5];},
    breakTarget:o.breakTarget||function(cands){return cands[0];}
  };
  return p;
}

/* rank a Break target by which family row it would fire — the real table */
function breakRowValue(mat){
  var fam=_matFam(mat);
  return({obsidian:5,vagabond:4,starstone:3,amber:2,silver:1,jade:1}[fam])||0;
}

F.POLICIES={};

/* CAUTIOUS CARL — low threshold, defensive. Drafts Silver and Ward, keeps
   everything that scores so nothing is left in the bust pool. */
F.POLICIES.carl=mkPolicy({name:'CAUTIOUS CARL',thresh:300,
  keep:function(f,c){
    /* the defensive read: arm the Ward before pushing, because the halved
       bank is worth more than the points the shield face forfeits */
    if(!c.G._wardArmed){
      var w=c.keeps.filter(function(k){
        return k.sel.some(function(d){return _dieIsIcon(d)&&d.ench.t==='ward';});});
      if(w.length)return bestPts(w);
    }
    return bestPts(c.keeps);
  },
  draft:function(offer){
    var pref=['silver','brutus_shield','amber','bone'];
    for(var i=0;i<pref.length;i++){
      var j=offer.indexOf(pref[i]);if(j>=0)return j;
    }
    return 0;
  },
  enchant:function(ch){
    var pref=['ward','tithe','fog','snare'];
    for(var i=0;i<pref.length;i++)if(ch.indexOf(pref[i])>=0)return pref[i];
    return ch[0]||null;
  },
  breakTarget:function(cands){
    /* Carl breaks the least valuable thing he owns */
    var b=cands[0];cands.forEach(function(d){if(dieRank(d.mat)<dieRank(b.mat))b=d;});
    return b;
  }});

/* BALANCED BEA — mid threshold, drafts toward owned families, and the ONE
   agent that uses pre-match lane planning: she reorders her loadout so the
   lane-targeting brands (Snare, Trade, Snuff, Fog) sit opposite the rival's
   best seats, which is the only thing the peek can buy. */
F.POLICIES.bea=mkPolicy({name:'BALANCED BEA',thresh:500,
  keep:function(f,c){
    var ic=withIcons(c.keeps);
    /* fire a brand when the roll is otherwise thin — an icon banks zero, so
       spending a fat roll on one is the mistake this avoids */
    if(ic&&c.G.turnPts<400)return bestPts(ic);
    return bestPts(c.keeps);
  },
  draft:function(offer,c){
    var owned=(c&&c.owned)||[];
    var fams={};owned.forEach(function(m){fams[_matFam(m)]=(fams[_matFam(m)]||0)+1;});
    var best=0,bv=-1;
    offer.forEach(function(m,i){
      var v=(fams[_matFam(m)]||0)*1000+dieRank(m);
      if(v>bv){bv=v;best=i;}
    });
    return best;
  },
  enchant:function(ch){
    var pref=['snare','trade','fog','snuff','tithe','ward'];
    for(var i=0;i<pref.length;i++)if(ch.indexOf(pref[i])>=0)return pref[i];
    return ch[0]||null;
  },
  /* THE LANE PLAN. peek = the rival's six materials in lane order. Bea puts
     her lane-targeting brands opposite their strongest seats and everything
     else where it lands. */
  lanePlan:function(peek,c){
    var ench=(c&&c.ench)||[];
    var targeting=[],plain=[];
    for(var i=0;i<6;i++){
      var e=ench[i];var t=e?(e.t||e):null;
      if(t==='snare'||t==='trade'||t==='snuff'||t==='fog')targeting.push(i);
      else plain.push(i);
    }
    var lanes=[0,1,2,3,4,5].sort(function(a,b){
      return dieRank((peek||[])[b]||'bone')-dieRank((peek||[])[a]||'bone');});
    var plan=new Array(6);
    var src=targeting.concat(plain);
    for(var j=0;j<6;j++)plan[lanes[j]]=src[j];
    return plan;
  },
  breakTarget:function(cands){
    var b=cands[0],bv=-1;
    cands.forEach(function(d){var v=breakRowValue(d.mat);if(v>bv){bv=v;b=d;}});
    return b;
  }});

/* GAMBLER GREG — high threshold, obsidian/volatility, pushes hot dice.
   TWO VARIANTS, per the brief: naive fires Break the moment it can, informed
   fires it only when no future turn is left to protect. */
function gregBase(name,informed){
  return mkPolicy({name:name,thresh:1000,
    bankAt:function(c){
      if(c.G.pPts+c.turnPts>=c.G.target)return true;
      if(c.diceLeft<=0)return true;
      if(c.diceLeft<=1&&c.turnPts>=800)return true;
      return c.turnPts>=1000&&c.diceLeft<=2;
    },
    keep:function(f,c){
      var pool=c.keeps;
      /* THE ONLY DIFFERENCE BETWEEN THE TWO GREGS. The informed one withholds
         the SKULL — and nothing else — until there is no future turn left to
         protect, which is exactly the timing read brief §4 says the mechanic
         is meant to teach. Every other brand behaves identically in both, so
         a gap between them is the Break timing and not a side effect of
         playing fewer icons. */
      if(informed&&!(c.state&&c.state.lastTurn)){
        pool=c.keeps.filter(function(k){
          return !k.sel.some(function(d){return _dieIsIcon(d)&&d.ench.t==='break';});});
        if(!pool.length)pool=c.keeps;
      }
      var ic=withIcons(pool);
      if(ic)return bestPts(ic);
      /* volatility: keep the least you legally can, roll the rest */
      return leanest(pool);
    },
    draft:function(offer){
      var pref=['obsidian','jade2','jade','starstone','vagabond'];
      for(var i=0;i<pref.length;i++){var j=offer.indexOf(pref[i]);if(j>=0)return j;}
      return 0;
    },
    enchant:function(ch){
      var pref=['break','trade','snare','tithe'];
      for(var i=0;i<pref.length;i++)if(ch.indexOf(pref[i])>=0)return pref[i];
      return ch[0]||null;
    },
    breakTarget:function(cands){
      var b=cands[0],bv=-1;
      cands.forEach(function(d){var v=breakRowValue(d.mat);if(v>bv){bv=v;b=d;}});
      return b;
    }});
}
F.POLICIES.greg_naive=gregBase('GAMBLER GREG (naive Break)',false);
F.POLICIES.greg_informed=gregBase('GAMBLER GREG (informed Break)',true);

/* NEWBIE NED — the CONTROL, not the floor. He knows the obvious things a
   first-time player picks up in ten minutes (take the scoring dice, bank once
   there is something worth banking, do not roll one die for fun) and nothing
   at all about build. The gap between Ned and a deliberate agent is what
   "drafting/build skill is worth ~45 points" means; the gap between Ned and
   Randy is what "knowing the rules at all" is worth. */
F.POLICIES.ned=mkPolicy({name:'NEWBIE NED',thresh:400,
  bankAt:function(c){
    if(c.G.pPts+c.turnPts>=c.G.target)return true;
    if(c.diceLeft<=0)return true;
    if(c.turnPts<=0)return false;
    if(c.diceLeft<=1)return true;/* the one lesson everybody learns fast */
    if(c.turnPts>=300)return Math.random()<0.6;
    return Math.random()<0.2;
  },
  /* half the time he takes the fat keep, half the time whatever he fancies */
  keep:function(f,c){
    if(Math.random()<0.5)return bestPts(c.keeps);
    return pick(c.keeps).sel;
  },
  draft:function(offer){return (Math.random()*offer.length)|0;},
  enchant:function(ch){return ch.length?pick(ch):null;},
  breakTarget:function(cands){return pick(cands);}});

/* RUSHER RITA — minimal seats, rushes the boss. Banks the moment anything is
   on the table; drafts cheap so the gold goes to buy-ins rather than dice. */
F.POLICIES.rita=mkPolicy({name:'RUSHER RITA',thresh:200,
  bankAt:function(c){
    if(c.G.pPts+c.turnPts>=c.G.target)return true;
    if(c.diceLeft<=0)return true;
    return c.turnPts>=200;
  },
  keep:function(f,c){return bestPts(c.keeps);},
  draft:function(offer){
    var b=0;offer.forEach(function(m,i){if(dieRank(m)<dieRank(offer[b]))b=i;});
    return b;
  },
  enchant:function(ch){return ch.indexOf('tithe')>=0?'tithe':(ch[0]||null);}});

/* RANDOM RANDY — the floor. Random at every decision the interface exposes. */
F.POLICIES.randy=mkPolicy({name:'RANDOM RANDY',thresh:0,
  bankAt:function(c){
    if(c.diceLeft<=0)return true;
    if(c.turnPts<=0)return false;
    return Math.random()<0.5;
  },
  keep:function(f,c){return pick(c.keeps).sel;},
  draft:function(offer){return (Math.random()*offer.length)|0;},
  enchant:function(ch){return ch.length?pick(ch):null;},
  lanePlan:function(){
    var a=[0,1,2,3,4,5];
    for(var i=5;i>0;i--){var j=(Math.random()*(i+1))|0,t=a[i];a[i]=a[j];a[j]=t;}
    return a;
  },
  breakTarget:function(cands){return pick(cands);}});

/* ORACLE OTTO — the ceiling. EV-optimal banking AND drafting, both computed by
   MEASURING the real engine rather than by a formula about it:
     - bust odds and continuation value per dice-count come from rolling the
       player's own materials with the real roller and asking the real
       anyScoring / scoreRoll.
     - a draft offer is scored by measuring the mean turn value of the loadout
       with that die swapped in.
   The table is rebuilt whenever the loadout changes, so Silver's weighting,
   a brand's stolen face and Still Waters all show up in Otto's numbers. */
var _evCache=null,_evKey='';
function evTable(mats,enchs){
  var key=mats.join(',')+'|'+(enchs||[]).map(function(e){return e?e.t+e.face:'-';}).join(',');
  if(_evKey===key&&_evCache)return _evCache;
  var N=900,cards=effectiveCards();
  var tab={bust:[0,0,0,0,0,0,0],gain:[0,0,0,0,0,0,0]};
  for(var k=1;k<=6;k++){
    var bust=0,gain=0;
    for(var s=0;s<N;s++){
      var vals=[],ms=[],ds=[];
      for(var i=0;i<k;i++){
        var mat=mats[i%mats.length],en=(enchs||[])[i%mats.length]||null;
        var v=_enchRollM(mat,en);
        vals.push(v);ms.push(mat);ds.push({val:v,mat:mat,ench:en});
      }
      if(!anyScoring(vals,cards,ms,ds)){bust++;continue;}
      var r=scoreRoll(vals,cards,0,{},ms,ds.map(function(d){return d.ench;}));
      gain+=(r.total||0);
    }
    tab.bust[k]=bust/N;
    tab.gain[k]=gain/N;
  }
  _evCache=tab;_evKey=key;
  return tab;
}
F.evTable=evTable;
F.POLICIES.otto=mkPolicy({name:'ORACLE OTTO',thresh:0,
  /* push while the measured expected gain beats the measured expected loss */
  bankAt:function(c){
    var G=c.G;
    if(G.pPts+c.turnPts>=G.target)return true;
    if(c.diceLeft<=0)return true;
    /* behind with no future turn: push regardless, a bank that loses is a loss */
    if(c.state&&c.state.lastTurn&&c.state.oppTotal!=null&&
       G.pPts+c.turnPts<=c.state.oppTotal)return false;
    var t=evTable(G.matchDice||['bone'],G._enchArr||[]);
    var k=Math.min(6,Math.max(1,c.diceLeft));
    var pb=t.bust[k];
    /* a Ward already armed this turn halves what a bust costs */
    var atRisk=c.turnPts*(G._wardArmed?0.5:1);
    return (pb*atRisk)>((1-pb)*t.gain[k]);
  },
  /* keep the subset with the best measured pts + continuation value */
  keep:function(f,c){
    var G=c.G;
    var t=evTable(G.matchDice||['bone'],G._enchArr||[]);
    var best=null,bv=-1e9;
    c.keeps.forEach(function(kp){
      var left=kp.left||0;
      var k=left===0?6:left;/* hot dice hands back a full six */
      var cont=(1-t.bust[k])*t.gain[k]+(left===0?250:0);
      var v=kp.pts+cont*0.85;
      if(kp.icons)v+=60;/* a fired brand is worth something the score can't see */
      if(v>bv){bv=v;best=kp;}
    });
    return (best||c.keeps[0]).sel;
  },
  /* measure each offer instead of ranking it by price */
  draft:function(offer,c){
    var owned=((c&&c.owned)||['bone','bone','bone','bone','bone','bone']).slice(0,6);
    var worst=0;
    owned.forEach(function(m,i){if(dieRank(m)<dieRank(owned[worst]))worst=i;});
    var best=0,bv=-1;
    offer.forEach(function(m,i){
      var trial=owned.slice();trial[worst]=m;
      _evKey='';/* force a fresh measurement for this trial loadout */
      var t=evTable(trial,[]);
      var v=(1-t.bust[6])*t.gain[6];
      if(v>bv){bv=v;best=i;}
    });
    _evKey='';
    return best;
  },
  enchant:function(ch){
    /* Tithe is the only additive brand and the only one Kindred doubles;
       Ward is the only one that changes a bust's price. Otto takes the two
       that a measurement can actually see. */
    var pref=['ward','tithe','snare','fog','snuff','trade','break'];
    for(var i=0;i<pref.length;i++)if(ch.indexOf(pref[i])>=0)return pref[i];
    return ch[0]||null;
  },
  lanePlan:F.POLICIES.bea?F.POLICIES.bea.lanePlan:null,
  breakTarget:function(cands){
    var b=cands[0],bv=-1;
    cands.forEach(function(d){
      var v=breakRowValue(d.mat)*100-dieRank(d.mat)/50;
      if(v>bv){bv=v;b=d;}});
    return b;
  }});
F.POLICIES.otto.lanePlan=F.POLICIES.bea.lanePlan;

F.ROSTER=['carl','bea','greg_naive','greg_informed','ned','rita','randy','otto'];

/* ────────── 7b. PER-TURN BUST RATE, on the real path ──────────────── */
/* The brief's Silver anchor ("all-bone ~49-50%, all-silver ~26%, ratio held
   at 0.54-0.58 across every policy tested") is a PER-TURN number, so a
   single-roll measurement cannot be compared to it. This plays real turns
   with the real roller, the real bust gate and the real keep engine, against
   a bare loadout with no match around it — which is why the policy is a
   plain bank threshold rather than one of the roster.                      */
F.measureTurnBust=function(mats,enchs,thresh,n){
  n=n||4000;thresh=thresh||500;
  var cards=effectiveCards(),busts=0,tot=0,rolls=0;
  for(var s=0;s<n;s++){
    var live=mats.map(function(m,i){return{mat:m,ench:(enchs||[])[i]||null};});
    var turn=0,r=0,busted=false;
    while(r++<30){
      live.forEach(function(d){d.val=_enchRollM(d.mat,d.ench);});
      var vals=live.map(function(d){return d.val;});
      var ms=live.map(function(d){return d.mat;});
      rolls++;
      if(!anyScoring(vals,cards,ms,live)){busted=true;break;}
      var sc=scoreRoll(vals,cards,0,{},ms,live.map(function(d){return d.ench;}));
      turn+=(sc.total||0);
      var left=[];
      for(var i=0;i<live.length;i++)if(!sc.used||!sc.used[i])left.push(live[i]);
      if(!left.length)left=mats.map(function(m,i){return{mat:m,ench:(enchs||[])[i]||null};});
      live=left;
      if(left.length<=2&&turn>=100)break;
      if(turn>=thresh&&left.length<=4)break;
      if(turn>=thresh*2)break;
    }
    tot++;if(busted)busts++;
  }
  return{bust:F.ci95(busts,tot),rollsPerTurn:+(rolls/tot).toFixed(2),n:tot,thresh:thresh};
};

/* ─────────────────────── 8. BATCH RUNNER ───────────────────────────── */
/* Runs n matches and returns everything with an interval on it. Alternates
   who moves first, exactly as the shipped sim does, so first-mover advantage
   cannot be mistaken for agent skill. */
F.runBatch=function(policy,opts,n){
  n=n||200;opts=opts||{};
  var wins=0,bustTurns=0,turnsTot=0,rollsTot=0,iconsTot=0,capEnds=0,errs=0;
  var turnsArr=[],bankArr=[],allBanks=[],goldArr=[],oppArr=[];
  for(var i=0;i<n;i++){
    var m;
    try{
      m=F.simMatch(policy,Object.assign({},opts,{playerFirst:i%2===0}));
    }catch(e){errs++;continue;}
    if(m.won)wins++;
    turnsArr.push(m.turns);turnsTot+=m.turns;rollsTot+=m.rolls;
    iconsTot+=m.icons;bustTurns+=m.busts;
    if(m.capEnd)capEnds++;
    bankArr.push(m.playerBank);oppArr.push(m.oppBank);
    goldArr.push(m.goldGained);
    for(var b=0;b<m.banks.length;b++)allBanks.push(m.banks[b]);
  }
  var ok=n-errs;
  return{
    n:ok,errors:errs,
    winRate:F.ci95(wins,ok),
    bustRate:F.ci95(bustTurns,Math.max(1,turnsTot)),
    medianTurns:F.median(turnsArr),
    bustsPerMatch:+(bustTurns/Math.max(1,ok)).toFixed(2),
    meanBank:F.ciMean(bankArr),
    meanOppBank:F.ciMean(oppArr),
    meanTurnBank:F.ciMean(allBanks),
    meanGold:F.ciMean(goldArr),
    iconsPerMatch:+(iconsTot/Math.max(1,ok)).toFixed(2),
    rollsPerTurn:+(rollsTot/Math.max(1,turnsTot)).toFixed(2),
    capEndPct:+(100*capEnds/Math.max(1,ok)).toFixed(1)
  };
};

/* ───────────────────────── 9. SELF TEST ────────────────────────────── */
/* Proves the harness is LIVE: that it reached the real functions, that the
   seed reproduces, and that the numbers are not degenerate. */
F.selfTest=function(n,seed){
  n=n||200;
  var out={seed:F.installRng(seed),n:n};
  F.quiet();
  var spies={scoreRoll:0,scoreSelection:0,iconFire:0,tryBustSave:0,doBust:0,
             handleBank:0,breakDie:0,oppShouldBank:0,rollTable:0};
  var real={};
  ['scoreRoll','scoreSelection','_iconFire','_tryBustSave','doBust','handleBank',
   '_breakDie','oppShouldBank','_rollTable'].forEach(function(fn){
    real[fn]=window[fn];
  });
  window.scoreRoll=function(){spies.scoreRoll++;return real.scoreRoll.apply(null,arguments);};
  window.scoreSelection=function(){spies.scoreSelection++;return real.scoreSelection.apply(null,arguments);};
  window._iconFire=function(){spies.iconFire++;return real._iconFire.apply(null,arguments);};
  window._tryBustSave=function(){spies.tryBustSave++;return real._tryBustSave.apply(null,arguments);};
  window.doBust=function(){spies.doBust++;return real.doBust.apply(null,arguments);};
  window.handleBank=function(){spies.handleBank++;return real.handleBank.apply(null,arguments);};
  window._breakDie=function(){spies.breakDie++;return real._breakDie.apply(null,arguments);};
  window.oppShouldBank=function(){spies.oppShouldBank++;return real.oppShouldBank.apply(null,arguments);};
  window._rollTable=function(){spies.rollTable++;return real._rollTable.apply(null,arguments);};
  var t0=performance.now();
  out.batches={};
  ['carl','bea','otto','randy'].forEach(function(k){
    F.installRng(out.seed);
    out.batches[k]=F.runBatch(F.POLICIES[k],{tier:3,gear:F.GEAR.night4},n);
  });
  out.ms=Math.round(performance.now()-t0);
  out.realCalls=spies;
  /* reproducibility: the same seed must give the same answer, twice */
  F.installRng(out.seed);
  var a=F.runBatch(F.POLICIES.bea,{tier:3,gear:F.GEAR.night4},40);
  F.installRng(out.seed);
  var b=F.runBatch(F.POLICIES.bea,{tier:3,gear:F.GEAR.night4},40);
  out.reproducible=(a.winRate.k===b.winRate.k&&a.meanBank.mean===b.meanBank.mean);
  Object.keys(real).forEach(function(fn){window[fn]=real[fn];});
  F.loud();F.restoreRng();
  return out;
};

})();
/* ══════════════════════════════════════════════════════════════════════════
   HOW TO USE (from another eval file)

     node tools/shoot.js --eval-file tools/sim_yours.js

   and start tools/sim_yours.js with the harness inlined:

     // ── paste or read the whole of sim_harness.js here ──
     FSIM.installRng(12345);
     FSIM.quiet();
     var r = FSIM.runBatch(FSIM.POLICIES.bea, {tier:3, gear:FSIM.GEAR.night8}, 400);
     FSIM.loud(); FSIM.restoreRng();
     return r;

   Concatenating is deliberate: shoot.js runs ONE file, and a harness that had
   to be fetched would be a second thing that can fail. Read the file in node
   and prepend it, or copy it — either way state the seed in the result.
   ══════════════════════════════════════════════════════════════════════════ */
