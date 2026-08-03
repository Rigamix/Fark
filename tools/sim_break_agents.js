/* WHICH AGENT PLAYS PLAUSIBLY WITH A BREAK BRAND IN HAND?
 *
 * The Obsidian control failed at 89-92% bust per turn against an expected
 * 26-49%, and both sides of that A/B were Gambler Greg at threshold 1,000. A
 * Break brand banks ZERO and removes a die, so a greedy policy ends up rolling
 * dead hands - the agent was not playing the game brief section 4 measured.
 *
 * Before building a new timing pair, find out which base policies stay in a
 * believable bust band with this gear. Whole roster, same gear, same seed - the
 * only variable is the policy. */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260803;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:400;
var out={n:N,tier:4,agents:{},notes:[]};
var gear={key:'brk_obsidian',dice:['bone','obsidian','bone','bone','bone','bone'],
          ench:['break',null,null,null,null,null],badge:null,fcards:[]};
FSIM.quiet();
FSIM.ROSTER.forEach(function(k){
  FSIM.installRng(seed);
  var b=FSIM.runBatch(FSIM.POLICIES[k],{tier:4,gear:gear},N);
  out.agents[k]={win:+(100*b.winRate.p).toFixed(2),
                 bustPerTurn:+(100*b.bustRate.p).toFixed(1),
                 bank:Math.round(b.meanBank.mean),
                 medTurns:b.medianTurns,
                 capEnd:b.capEndPct};
});
FSIM.loud();FSIM.restoreRng();
/* the band the shipped game actually produces: all-bone ~49%, all-silver ~26% */
out.plausible=Object.keys(out.agents).filter(function(k){
  var b=out.agents[k].bustPerTurn; return b>=20&&b<=60;});
return out;
