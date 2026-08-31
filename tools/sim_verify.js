/* sim_verify.js — tail for sim_run.js. Is the harness measuring the real game?
 *  A. vs the game's OWN shipped harness (_runBalanceSim), twice: once as-is,
 *     once with __shippedCompat on. P890: that flag now emulates ONE
 *     difference, the missing hot-dice bonus. Its other half - one free
 *     bust-save a turn from Silver's retired identity - emulated a stale
 *     assumption the shipped sim really had, and P888 deleted it there, so
 *     keeping it here would have made the compat arm MORE generous than the
 *     thing it models. If compat lands on the shipped number, the gap is that
 *     sim's staleness and not a bug here.
 *  B. FULL ROSTER on night-8 gear — does Break fire, does Trade restore.
 *  C. SILVER, per turn, against the brief's 0.54-0.58 ratio anchor.
 *  D. BRAND FACES + the Ward loadout cap, through the real shop guards.
 *  E. Does BEA's lane plan buy her anything (brief: if not, the system is not
 *     pulling its weight).
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var out={seed:seed};
var GEAR_MID={dice:['amber','amber','jade','iron','silver','flint'],
              ench:[null,null,null,null,null,null],fcards:[],badge:null};
var mirror={name:'MIRROR bank500',
  bankAt:function(c){
    if(c.G.pPts+c.turnPts>=c.G.target)return true;
    if(c.diceLeft<=0)return true;
    if(c.diceLeft<=2&&c.turnPts>=100)return true;
    if(c.turnPts>=500&&c.diceLeft<=4)return true;
    return c.turnPts>=1000;
  },
  keep:function(f,c){return FSIM.allScorers(f);},
  draft:function(){return 0;},enchant:function(){return null;},
  lanePlan:null,breakTarget:function(a){return a[0];}};

/* ── A ───────────────────────────────────────────────────────────────── */
try{
  FSIM.installRng(seed);
  var savedG=FSIM.getG();FSIM.setG(null);
  var rows=_runBalanceSim({iters:400,tiers:[3],
    gears:[{key:'G2-mid',dice:GEAR_MID.dice,bankAdd:0}],
    policies:[{key:'bank500',thresh:500}]});
  FSIM.setG(savedG);
  out.shipped={win:rows[0].patronWin,medTurns:rows[0].medTurns,
    bustsPerMatch:rows[0].bustsPerMatch,
    ci:[+(100*FSIM.ci95(Math.round(rows[0].patronWin*4),400).lo).toFixed(1),
        +(100*FSIM.ci95(Math.round(rows[0].patronWin*4),400).hi).toFixed(1)]};
}catch(e){out.shipped='ERR '+(e&&e.message);}

function slim(b){return{win:+(100*b.winRate.p).toFixed(1),
  ci:[+(100*b.winRate.lo).toFixed(1),+(100*b.winRate.hi).toFixed(1)],
  medTurns:b.medianTurns,bustsPerMatch:b.bustsPerMatch,
  bustPerTurn:+(100*b.bustRate.p).toFixed(1),
  bank:b.meanBank.mean,opp:b.meanOppBank.mean,turnBank:b.meanTurnBank.mean,
  icons:b.iconsPerMatch,gold:b.meanGold.mean,capEnd:b.capEndPct,errors:b.errors,n:b.n};}

try{
  FSIM.quiet();
  FSIM.installRng(seed);
  out.harness=slim(FSIM.runBatch(mirror,{tier:3,gear:GEAR_MID},400));
  FSIM.__shippedCompat=true;
  FSIM.installRng(seed);
  out.harnessCompat=slim(FSIM.runBatch(mirror,{tier:3,gear:GEAR_MID},400));
  FSIM.__shippedCompat=false;
  FSIM.loud();
}catch(e){try{FSIM.loud();FSIM.__shippedCompat=false;}catch(e2){}out.harness='ERR '+(e&&e.stack);}

/* ── B ───────────────────────────────────────────────────────────────── */
try{
  FSIM.quiet();
  var spy={breakDie:0,iconFire:0,tradeFire:0,breakRows:{}};
  var rbd=window._breakDie,rif=window._iconFire;
  window._breakDie=function(d){spy.breakDie++;
    var f=_matFam(d&&d.mat);spy.breakRows[f]=(spy.breakRows[f]||0)+1;
    return rbd.apply(null,arguments);};
  window._iconFire=function(d){spy.iconFire++;if(d&&d.ench&&d.ench.t==='trade')spy.tradeFire++;
    return rif.apply(null,arguments);};
  out.roster={};var restored=0;
  FSIM.ROSTER.forEach(function(k){
    FSIM.installRng(seed);
    var r=FSIM.runBatch(FSIM.POLICIES[k],{tier:5,gear:FSIM.GEAR.night8},200);
    out.roster[k]=slim(r);
  });
  /* one match watched end to end for the Trade restore */
  FSIM.installRng(seed);
  var one=FSIM.simMatch(FSIM.POLICIES.bea,{tier:5,gear:FSIM.GEAR.night8});
  out.oneMatch={won:one.won,turns:one.turns,tradesRestored:one.tradesRestored,
    lanePlan:one.lanePlan,icons:one.icons,rung:one.rung};
  window._breakDie=rbd;window._iconFire=rif;
  out.spies=spy;
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.roster='ERR '+(e&&e.stack);}

/* ── C ───────────────────────────────────────────────────────────────── */
try{
  FSIM.quiet();
  var savedG2=FSIM.getG();FSIM.setG(null);
  out.silverPerTurn={};
  [300,500,800].forEach(function(t){
    FSIM.installRng(seed);
    var bone=FSIM.measureTurnBust(['bone','bone','bone','bone','bone','bone'],null,t,6000);
    var silv=FSIM.measureTurnBust(['silver','silver','silver','silver','silver','silver'],null,t,6000);
    out.silverPerTurn['bank'+t]={
      bone:+(100*bone.bust.p).toFixed(1),boneCI:[+(100*bone.bust.lo).toFixed(1),+(100*bone.bust.hi).toFixed(1)],
      silver:+(100*silv.bust.p).toFixed(1),silverCI:[+(100*silv.bust.lo).toFixed(1),+(100*silv.bust.hi).toFixed(1)],
      ratio:+(silv.bust.p/bone.bust.p).toFixed(3)};
  });
  FSIM.setG(savedG2);FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.silverPerTurn='ERR '+(e&&e.message);}

/* ── D ───────────────────────────────────────────────────────────────── */
try{
  FSIM.installRng(seed);
  var faces={},mats=['bone','iron','flint','lead','amber','silver','obsidian',
                     'starstone','jade','jade2','vagabond','lucky','brutus_shield','grogs_tooth'];
  mats.forEach(function(m){
    var seen={};
    for(var i=0;i<600;i++){var e=FSIM.mkEnch(m,'tithe');seen[e?e.face:'REFUSED']=1;}
    faces[m]=Object.keys(seen).sort();
  });
  out.brandFaces=faces;
  var lo=FSIM.buildLoadout({dice:['silver','silver','bone','bone','bone','bone'],
                            ench:['ward','ward',null,null,null,null]});
  out.wardCap={granted:lo.ench.filter(function(e){return e&&e.t==='ward';}).length,
               refused:lo.refused};
  var lo2=FSIM.buildLoadout({dice:['brutus_shield','silver','bone','bone','bone','bone'],
                             ench:[null,'ward',null,null,null,null]});
  out.wardCapVsRelic={relicInLane0:'brutus_shield',
    grantedWards:lo2.ench.filter(function(e){return e&&e.t==='ward';}).length,
    refused:lo2.refused};
}catch(e){out.brandFaces='ERR '+(e&&e.message);}

/* ── E — does the lane plan buy Bea anything? ────────────────────────── */
try{
  FSIM.quiet();
  FSIM.installRng(seed);
  var withPlan=FSIM.runBatch(FSIM.POLICIES.bea,{tier:5,gear:FSIM.GEAR.night8},400);
  FSIM.installRng(seed);
  var noPlan=FSIM.runBatch(FSIM.POLICIES.bea,{tier:5,gear:FSIM.GEAR.night8,lanePlan:false},400);
  FSIM.loud();
  out.lanePlanning={
    withPlan:[+(100*withPlan.winRate.p).toFixed(1),+(100*withPlan.winRate.lo).toFixed(1),+(100*withPlan.winRate.hi).toFixed(1)],
    noPlan:[+(100*noPlan.winRate.p).toFixed(1),+(100*noPlan.winRate.lo).toFixed(1),+(100*noPlan.winRate.hi).toFixed(1)],
    deltaPts:+(100*(withPlan.winRate.p-noPlan.winRate.p)).toFixed(1),
    bankWith:withPlan.meanBank.mean,bankWithout:noPlan.meanBank.mean};
}catch(e){try{FSIM.loud();}catch(e2){}out.lanePlanning='ERR '+(e&&e.message);}

FSIM.restoreRng();
return out;
