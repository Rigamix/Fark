/* ONE family per page load — the workaround the scaling diagnosis implies.
 *
 * The wall is CUMULATIVE MATCHES IN A PAGE, not batch size and not wall-clock:
 * ~46KB is retained per match and never released, so a page dies somewhere
 * between 321MB (7,040 matches, completed) and 435MB (9,600, failed). Twelve
 * batches of 2,000 in one page is 24,000 matches and ~1GB; two batches of 2,000
 * is 4,000 matches and ~185MB, comfortably under.
 *
 * So the six-family pass runs as six invocations, not one. Same numbers, same
 * instrument, split across pages that each stay under the ceiling.
 *
 * OBSIDIAN FIRST ON PURPOSE. It is the one row with a published result, so
 * running it through this instrument at a real sample size tests the
 * INSTRUMENT, not just the row - if it cannot reproduce the known finding, the
 * other five are not worth running. */
var FAM=(window.__FSIM_FAM!==undefined)?window.__FSIM_FAM:'obsidian';
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260803;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:2000;
var TIER=(window.__FSIM_TIER!==undefined)?window.__FSIM_TIER:4;
var out={fam:FAM,n:N,tier:TIER,seed:seed};
var gear={key:'brk_'+FAM,dice:['bone',FAM,'bone','bone','bone','bone'],
          ench:['break',null,null,null,null,null],badge:null,fcards:[]};
FSIM.quiet();
var t0=performance.now();
['greg_naive','greg_informed'].forEach(function(k){
  FSIM.installRng(seed);
  var b=FSIM.runBatch(FSIM.POLICIES[k],{tier:TIER,gear:gear},N);
  out[k]={win:+(100*b.winRate.p).toFixed(2),
          ci:[+(100*b.winRate.lo).toFixed(2),+(100*b.winRate.hi).toFixed(2)],
          bank:Math.round(b.meanBank.mean),
          bankCI:[Math.round(b.meanBank.lo),Math.round(b.meanBank.hi)],
          bustPerTurn:+(100*b.bustRate.p).toFixed(1),errors:b.errors};
});
out.timingDelta={win:+(out.greg_informed.win-out.greg_naive.win).toFixed(2),
                 bank:out.greg_informed.bank-out.greg_naive.bank};
out.ms=Math.round(performance.now()-t0);
try{out.heapMB=+(performance.memory.usedJSHeapSize/1048576).toFixed(1);}catch(e){}
FSIM.loud();FSIM.restoreRng();
return out;
