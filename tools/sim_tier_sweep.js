/* TIER SWEEP — the two numbers the flat-difficulty finding is about, re-measured.
 *
 * The archived finding: night-1 win rate at tiers 3-7 was 30.8 / 33.0 / 36.4 /
 * 33.9 / 32.3 (flat), and cap-decided endings went 0.3% -> 85.5%. Late nights
 * were not harder, they were LONGER. Every one of those numbers predates the
 * zero-point sweep removal, the Trade harness fix and the 2026-08-02 rulings,
 * so they are directions only.
 *
 * Un-upgraded build (GEAR.night1: six bone dice, no enchants, no badge, no
 * cards) because that is what the finding measured. Every roster agent per
 * tier, so the result is not one policy's quirk. */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:220;
var out={seed:seed,n:N,gear:'night1',tiers:{},notes:[]};
out.turnCapPatron=(typeof TURN_CAP_PATRON!=='undefined')?TURN_CAP_PATRON:'?';

FSIM.quiet();
var t0=performance.now();
for(var t=0;t<8;t++){
  var wins=[],caps=[],banks=[],opps=[],turns=[];
  /* FOUR AGENTS, NOT EIGHT. 8 tiers x 8 agents x 600 ran past ten minutes;
     this is the same question at a quarter the cost. Picked as a spread rather
     than a sample: a naive baseline, an informed one, and two ends of the
     bank-threshold range, so `spread` still shows whether tiers behave
     differently for cautious and reckless play. */
  ['greg_naive','greg_informed','carl','randy'].forEach(function(k){
    if(!FSIM.POLICIES[k])return;
    FSIM.installRng(seed+t);
    var b=FSIM.runBatch(FSIM.POLICIES[k],{tier:t,gear:FSIM.GEAR.night1},N);
    wins.push(100*b.winRate.p); caps.push(b.capEndPct);
    banks.push(b.meanBank.mean); opps.push(b.meanOppBank.mean);
    turns.push(b.medianTurns);
  });
  var mean=function(a){return +(a.reduce(function(x,y){return x+y;},0)/a.length).toFixed(1);};
  out.tiers[t]={win:mean(wins),capEnd:mean(caps),
                bank:Math.round(mean(banks)),oppBank:Math.round(mean(opps)),
                medTurns:mean(turns),
                spread:+(Math.max.apply(null,wins)-Math.min.apply(null,wins)).toFixed(1)};
}
out.ms=Math.round(performance.now()-t0);
FSIM.loud();FSIM.restoreRng();
return out;
