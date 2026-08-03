/* LENS 1, study D2 — the starstone dose-response across the WHOLE roster
   (is it dominant independent of agent?) and the badge sweep. */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:400;
var out={seed:seed,n:N,tier:3};
FSIM.quiet();
function cell(pol,gear,tier){
  FSIM.installRng(seed);
  var b=FSIM.runBatch(FSIM.POLICIES[pol],{tier:tier==null?3:tier,gear:gear,badge:gear.badge||null},N);
  return{win:+(100*b.winRate.p).toFixed(2),lo:+(100*b.winRate.lo).toFixed(2),
    hi:+(100*b.winRate.hi).toFixed(2),bank:b.meanBank.mean,turnBank:b.meanTurnBank.mean,
    med:b.medianTurns,bust:+(100*b.bustRate.p).toFixed(1),err:b.errors};
}
/* ── starstone dose, every agent ── */
out.ss={};
[0,1,2,3,6].forEach(function(k){
  var dice=[];for(var i=0;i<6;i++)dice.push(i<k?'starstone':'bone');
  out.ss['k'+k]={cost:k*700};
  FSIM.ROSTER.forEach(function(a){
    out.ss['k'+k][a]=cell(a,{dice:dice,ench:[null,null,null,null,null,null],badge:null,fcards:[]});
  });
});
/* one dose at a harder tier, to check it is not a tier-3 artefact */
out.ssT={};
[5,7].forEach(function(t){
  out.ssT['t'+t]={};
  [0,2].forEach(function(k){
    var dice=[];for(var i=0;i<6;i++)dice.push(i<k?'starstone':'bone');
    out.ssT['t'+t]['k'+k]={};
    ['carl','ned','otto'].forEach(function(a){
      out.ssT['t'+t]['k'+k][a]=cell(a,{dice:dice,ench:[null,null,null,null,null,null],badge:null,fcards:[]},t);
    });
  });
});
/* ── badge sweep ── */
var BASE=['amber','amber','silver','iron','bone','bone'];
var ENCH=['tithe','ward','snare',null,null,null];
var BADGES=[null,'last_call','kindred','still_waters','first_strike','steeped','pickpocket','drill_order','reckoning'];
out.badge={};
BADGES.forEach(function(bd){
  var key=bd||'none';
  FSIM.installRng(seed);
  var set=FSIM.setupMatch({tier:3,dice:BASE.slice(),ench:ENCH.slice(),badge:bd});
  out.badge[key]={live:set.badgeLive};
  ['carl','ned','otto'].forEach(function(a){
    out.badge[key][a]=cell(a,{dice:BASE.slice(),ench:ENCH.slice(),badge:bd,fcards:[]});
  });
});
FSIM.loud();FSIM.restoreRng();
return out;
