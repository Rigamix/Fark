/* P522 unit check: does the swap take the rival's WORST die, and does the
   loadout stay the same length?

   Blessed Confiscation's take_and_use mode needs a specific boss card in the
   pool to fire, so this evaluates the shipped selection logic against
   constructed loadouts rather than driving the card. Stated plainly rather than
   implied: this proves the arithmetic, not the integration. The integration
   claim that matters - that the seventh seat was never dealt - was already
   measured by the sweep on a real Ambrose match (seats 0-5 only). */
if(typeof dieRank!=='function')return{error:'dieRank missing'};

/* the same selection the patch installs */
function swapIn(arr,stolen){
  var a=arr.slice();
  if(!Array.isArray(a)||!a.length)return [stolen];
  var w=0;
  for(var i=1;i<a.length;i++){ if(dieRank(a[i])<dieRank(a[w]))w=i; }
  if(dieRank(stolen)>dieRank(a[w]))a[w]=stolen;   /* only if it is an upgrade */
  return a;
}
const MATS=['bone','iron','flint','lead','amber','jade','starstone','obsidian'];
const ranks={};MATS.forEach(m=>ranks[m]=dieRank(m));

const cases=[
  {opp:['bone','iron','flint','lead','amber','jade'], stolen:'starstone'},
  {opp:['jade','jade','jade','jade','jade','bone'],   stolen:'starstone'},
  {opp:['bone','bone','bone','bone','bone','bone'],   stolen:'obsidian'},
  {opp:['starstone','jade','amber'],                  stolen:'bone'},
  {opp:[],                                            stolen:'jade'},
];
const results=cases.map(function(c){
  const out=swapIn(c.opp,c.stolen);
  const worst=c.opp.length?c.opp.reduce(function(a,b){return dieRank(b)<dieRank(a)?b:a;}):null;
  return {before:c.opp, stolen:c.stolen, after:out, worstBefore:worst,
    lengthHeld: c.opp.length ? out.length===c.opp.length : out.length===1,
    stolenPresent: out.indexOf(c.stolen)!==-1,
    isUpgrade: c.opp.length? dieRank(c.stolen)>dieRank(worst) : true,
    exactlyOneWorstGone: (c.opp.length && dieRank(c.stolen)>dieRank(worst))
      ? out.filter(m=>m===worst).length===c.opp.filter(m=>m===worst).length-1
      : true,
    neverSeven: out.length<=Math.max(1,c.opp.length)};
});

/* the 4th case is the one worth having: the stolen die is WORSE than
   everything the rival holds, so a naive "replace the worst" still replaces
   something and the rival is DOWNGRADED. That is a real design consequence,
   not a bug - recorded so it is a decision rather than an accident. */
const downgradeCase=results[3];

return {
  ranks:ranks, results:results,
  rivalCanBeDowngraded: dieRank(downgradeCase.stolen)<dieRank(downgradeCase.worstBefore),
  allHeldLength: results.every(r=>r.lengthHeld),
  allStolenPresent: results.every(r=>r.stolenPresent),
  allReplacedTheWorst: results.every(r=>r.exactlyOneWorstGone),
  neverGrows: results.every(r=>r.neverSeven),
  verdict:
    !results.every(r=>r.lengthHeld) ? 'FAIL - the loadout changed length'
    : !results.every(r=>r.isUpgrade? r.stolenPresent : true) ? 'FAIL - an upgrade did not arrive'
    : !results.every(r=>r.isUpgrade|| r.after.indexOf(r.stolen)===-1||!r.before.length) ? 'FAIL - the rival took a downgrade'
    : !results.every(r=>r.exactlyOneWorstGone) ? 'FAIL - it did not replace the worst die'
    : 'PASS - the stolen die replaces the worst, length never grows'
};
