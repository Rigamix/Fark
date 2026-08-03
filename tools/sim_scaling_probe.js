/* WHY DOES THIS HARNESS STOP SCALING?
 *
 * Measured, not assumed: N=260 completes in ~13s and N=800 never produces a
 * result at all, even with the wait ceiling raised 60s -> 300s. A 5x ceiling
 * moving nothing rules out a simple wall-clock timeout on its own, which points
 * at something hanging or growing without bound rather than something slow.
 *
 * The two candidates are distinguishable by per-match COST:
 *   flat ms/match      -> not growth; the wall is elsewhere (a hang, a cap)
 *   rising ms/match    -> state accumulating across matches within a batch
 * and by heap, where the browser will report it.
 *
 * ONE PAGE LOAD, ascending sizes, same config throughout - so nothing differs
 * between the points except how many matches have already run. Sizes stop short
 * of the known wall so the probe itself returns a result instead of joining the
 * thing it is measuring. */
var out={steps:[],notes:[]};
var GEAR={key:'scale',dice:['bone','obsidian','bone','bone','bone','bone'],
          ench:['break',null,null,null,null,null],badge:null,fcards:[]};
function heapMB(){
  try{ return performance.memory?+(performance.memory.usedJSHeapSize/1048576).toFixed(1):null; }
  catch(e){ return null; }
}
FSIM.quiet();
out.heapStart=heapMB();
[100,200,400,600].forEach(function(N){
  FSIM.installRng(20260803);
  var t0=performance.now();
  var b=FSIM.runBatch(FSIM.POLICIES.greg_naive,{tier:4,gear:GEAR},N);
  var ms=performance.now()-t0;
  out.steps.push({n:N,ms:Math.round(ms),msPerMatch:+(ms/N).toFixed(2),
                  heapMB:heapMB(),errors:b.errors,
                  domNodes:document.getElementsByTagName('*').length});
});
FSIM.loud();FSIM.restoreRng();
/* the verdict the numbers support, computed rather than eyeballed */
var first=out.steps[0].msPerMatch, last=out.steps[out.steps.length-1].msPerMatch;
out.msPerMatchGrowth=+(last/first).toFixed(2);
out.verdict={
  perMatchCostFlat: out.msPerMatchGrowth<1.35,
  heapStable: (out.heapStart===null||out.steps[out.steps.length-1].heapMB===null)
              ? null
              : (out.steps[out.steps.length-1].heapMB-out.heapStart)<150
};
return out;
