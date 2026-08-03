/* sim_power_probe.js — LENS 2 (SENSE OF POWER) smoke test.
 * Tail for tools/sim_run.js. Verifies the two reference loadouts build through
 * the REAL shop guards, that a worn badge is actually live, and times a batch.
 * Measures nothing that gets reported as a finding — this is the setup check.
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var out={seed:seed,harness:!!window.FSIM};

/* ── what does a fresh run actually own? read it off the real newRun ── */
try{
  out.freshRun={};
  var fr=(typeof _freshRun==='function')?_freshRun():null;
  out.freshRun.fn=!!fr;
  if(fr)out.freshRun.val={dice:fr.dice,gold:fr.gold,coins:fr.coins,cards:fr.cards};
}catch(e){out.freshRun='ERR '+e.message;}
out.starterPool=['amber','silver','obsidian','starstone','vagabond'];
out.buyIns=(typeof NIGHT_BUYINS!=='undefined')?NIGHT_BUYINS:null;
out.turnCaps=[TURN_CAP_PATRON,TURN_CAP_BOSS];

/* ── prices, straight off the shipped tables ── */
try{
  var dp={};DICE_STORE.forEach(function(d){dp[d.mat]=d.price;});
  out.dicePrices=dp;
  var ep={};Object.keys(ENCH_ICONS).forEach(function(k){ep[k]=ENCH_ICONS[k].price;});
  ep.quicksilver=(typeof ENCH_QS!=='undefined'&&ENCH_QS.price)||250;
  out.enchPrices=ep;
  out.bossGold=RUNGS.map(function(r){return r.gold;});
  out.tierSeats=TIERS.map(function(t){return t.pointsNeeded+2;});
  out.tierPoints=TIERS.map(function(t){return t.pointsNeeded;});
  out.patronTargets=TIERS.map(function(t){
    return Math.round(((t.patronStats.targetMin+t.patronStats.targetMax)/2)/100)*100;});
  out.bossTargets=RUNGS.map(function(r){return r.target;});
}catch(e){out.dicePrices='ERR '+e.message;}

/* ── the two loadouts, built through the real _iconFaceRoll/_wardOwned ── */
var N1={key:'night1',dice:['silver','bone','bone','bone','bone','bone'],
        ench:[null,null,null,null,null,null],badge:null,fcards:[]};
var N8={key:'night8',dice:['jade2','jade','starstone','silver','amber','amber'],
        ench:['break','snare','tithe','ward','trade','fog'],
        badge:'kindred',
        fcards:[{id:'slow_cook',tier:3},{id:'falling_star',tier:3},{id:'pickpocket',tier:3}]};
out.N1=N1;out.N8=N8;

try{
  FSIM.installRng(seed);
  var lo1=FSIM.buildLoadout(N1);
  var lo8=FSIM.buildLoadout(N8);
  out.built={
    n1:{dice:lo1.dice,ench:lo1.ench,refused:lo1.refused},
    n8:{dice:lo8.dice,
        ench:lo8.ench.map(function(e){return e?e.t+'@'+e.face:null;}),
        refused:lo8.refused}};
}catch(e){out.built='ERR '+e.stack;}

/* ── is the badge actually live in a real match? ── */
try{
  FSIM.installRng(seed);
  var s8=FSIM.setupMatch({tier:7,dice:N8.dice,ench:N8.ench,badge:'kindred',fcards:N8.fcards});
  var G=FSIM.getG();
  out.badge={sleeve:G._sleeve,tell:G._tell&&G._tell.id,
    kindredActive:(typeof _kindredActive==='function')?_kindredActive():'n/a',
    stillWaters:(typeof _stillWaters==='function')?_stillWaters():'n/a',
    ruleActiveCounterfeit:_ruleActive('kindred','p'),
    enchArr:(G._enchArr||[]).map(function(e){return e?e.t:null;}),
    target:G.target,matchDice:G.matchDice,oppDice:G.matchOppDice,
    turnCap:G.turnCap};
}catch(e){out.badge='ERR '+e.stack;}

/* ── a timed batch each, tiny n, just to see the shape and the speed ── */
function slim(b){return{win:+(100*b.winRate.p).toFixed(1),
  ci:[+(100*b.winRate.lo).toFixed(1),+(100*b.winRate.hi).toFixed(1)],
  medTurns:b.medianTurns,bustPerTurn:+(100*b.bustRate.p).toFixed(1),
  bank:b.meanBank.mean,opp:b.meanOppBank.mean,icons:b.iconsPerMatch,
  gold:b.meanGold.mean,capEnd:b.capEndPct,errors:b.errors,n:b.n};}
try{
  FSIM.quiet();
  var t0=performance.now();
  FSIM.installRng(seed);
  out.t3_n1=slim(FSIM.runBatch(FSIM.POLICIES.bea,{tier:3,gear:N1},150));
  FSIM.installRng(seed);
  out.t3_n8=slim(FSIM.runBatch(FSIM.POLICIES.bea,{tier:3,gear:N8,badge:'kindred'},150));
  FSIM.installRng(seed);
  out.t7_n1=slim(FSIM.runBatch(FSIM.POLICIES.bea,{tier:7,gear:N1},150));
  FSIM.installRng(seed);
  out.t7_n8=slim(FSIM.runBatch(FSIM.POLICIES.bea,{tier:7,gear:N8,badge:'kindred'},150));
  out.ms=Math.round(performance.now()-t0);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.batch='ERR '+e.stack;}

FSIM.restoreRng();
return out;
