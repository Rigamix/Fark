/* THE CONTROL, REBUILT ON A SANE BASE.
 *
 * The first attempt used Gambler Greg for both sides of the A/B and failed its
 * own control: 89-92% bust per turn against an expected 26-49%, and Obsidian's
 * published timing result came out BACKWARDS. Measured across the whole roster
 * on the same gear, Greg is not merely the greediest policy - he is an OUTLIER:
 *
 *     rita 15.8  carl 20.1  otto 28.1  bea 32.0  ned 33.2  randy 33.9
 *     greg_naive 88.7   greg_informed 91.8
 *
 * and 1-1.75% win against 18-21% for the top four. A Break brand banks zero and
 * removes a die, and Greg's threshold-1000 policy answers that by rolling dead
 * hands. He was not playing the game brief section 4 measured.
 *
 * BEA IS THE BASE: balanced, mid-table on both bust (32.0%) and win (18.25%),
 * squarely inside the band the shipped game produces.
 *
 * The timing pair is built HERE rather than in the harness, by wrapping any
 * policy so the informed copy withholds the SKULL - and only the skull - until
 * the last turn. Same construction gregBase used inline, so the comparison is
 * the same one, on an agent that can actually play. */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260803;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:2000;
var BASE=(window.__FSIM_BASE!==undefined)?window.__FSIM_BASE:'bea';
var FAM=(window.__FSIM_FAM!==undefined)?window.__FSIM_FAM:'obsidian';
var out={base:BASE,fam:FAM,n:N,tier:4,seed:seed};

function informedOf(base){
  var o={};for(var k in base)o[k]=base[k];
  o.keep=function(f,c){
    if(!(c.state&&c.state.lastTurn)){
      var pool=c.keeps.filter(function(kp){
        return !kp.sel.some(function(d){return _dieIsIcon(d)&&d.ench.t==='break';});});
      if(pool.length&&pool.length<c.keeps.length){
        var c2={};for(var q in c)c2[q]=c[q];c2.keeps=pool;
        return base.keep.call(base,f,c2);
      }
    }
    return base.keep.call(base,f,c);
  };
  return o;
}
var gear={key:'brk_'+FAM,dice:['bone',FAM,'bone','bone','bone','bone'],
          ench:['break',null,null,null,null,null],badge:null,fcards:[]};
var pair={naive:FSIM.POLICIES[BASE],informed:informedOf(FSIM.POLICIES[BASE])};

FSIM.quiet();
var t0=performance.now();
Object.keys(pair).forEach(function(k){
  FSIM.installRng(seed);
  var b=FSIM.runBatch(pair[k],{tier:4,gear:gear},N);
  out[k]={win:+(100*b.winRate.p).toFixed(2),
          ci:[+(100*b.winRate.lo).toFixed(2),+(100*b.winRate.hi).toFixed(2)],
          bank:Math.round(b.meanBank.mean),
          bankCI:[Math.round(b.meanBank.lo),Math.round(b.meanBank.hi)],
          bustPerTurn:+(100*b.bustRate.p).toFixed(1),errors:b.errors};
});
out.timingDelta={win:+(out.informed.win-out.naive.win).toFixed(2),
                 bank:out.informed.bank-out.naive.bank};
/* brief section 4: breaking IMMEDIATELY is a net loss across a match, so
   holding the skull for the last turn should be BETTER. */
out.reproducesBrief=out.timingDelta.bank>0;
out.bustPlausible=(out.naive.bustPerTurn>=20&&out.naive.bustPerTurn<=60);
out.ms=Math.round(performance.now()-t0);
FSIM.loud();FSIM.restoreRng();
return out;
