/* PR8 vs the refuted G5 - reconcile before probing, then probe.

   Both nominations are the same code. G5's kill covers the SINGLE-die case:
   on a refusal _dropLanes is skipped too, so numDice stays equal to
   matchDice.length, the only disagreement is pool 0 against matchDice 1, and
   the turn busts - which is what "the last free die left the table" should do.

   PR8 survives only on the TWO-die arm, and that is what this drives:

     matchDice has 2, BOTH dice shatter on one roll
     _shLanes is [1,0] descending
       _removeDieAt(1)  matchDice 2 -> 1, numDice 2 -> 1   succeeds
       _removeDieAt(0)  matchDice.length <= 1              REFUSES
     then the unconditional pool purge takes BOTH shattered dice anyway

   The question PR8 raises is whether the refusal leaves the state incoherent.
   The answer is not obvious from reading: the refusal also skips _dropLanes, so
   the counts may still agree. So measure the three facts that must agree, and
   then ask the only question that matters to a player - CAN THE TURN CONTINUE?
   A die that comes back on the next deal is a cosmetic gap; a table that never
   deals again is the unwinnable-match shape. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=2,8000)))return{error:'no pool'};
await sleep(700);

/* the two-die arm, constructed */
G.matchDice=['bone','iron'];
G._enchArr=[null,null];
G.numDice=2;
G.pool=G.pool.slice(0,2);
G.pool.forEach(function(d,i){d.lane=i;d.committed=false;d._shattered=true;d._shatterLane=i;});
const before={md:G.matchDice.slice(), numDice:G.numDice, pool:G.pool.length};

/* the shipped sweep, verbatim in shape */
const _shLanes=G.pool.filter(d=>d._shattered)
  .map(d=>d._shatterLane!==undefined?d._shatterLane:d.lane)
  .filter(L=>typeof L==='number'&&isFinite(L)&&L>=0).sort((a,b)=>b-a)
  .filter((L,i,a)=>i===0||L!==a[i-1]);
const rets=[];
if(_shLanes.length)_shLanes.forEach(function(L){rets.push(_removeDieAt(L,{permanent:false}));});
G.pool=G.pool.filter(function(d){return !d._shattered;});

const after={md:G.matchDice.slice(), numDice:G.numDice, pool:G.pool.length};
const countsAgree = after.md.length===after.numDice;

/* the only question a player feels: does the next deal put a die back? */
G.phase='choosing';
try{handleRoll();}catch(e){}
await until(()=>G&&G.pool&&G.pool.length>0,6000);
await sleep(900);
const recovered={pool:G.pool.length, lanes:(G.pool||[]).map(d=>d.lane),
                 md:G.matchDice.length, numDice:G.numDice, phase:G.phase};

return {
  before:before, shLanes:_shLanes, removeReturns:rets, after:after,
  countsAgreeAfterSweep:countsAgree,
  recovered:recovered,
  verdict:
    rets.length!==2 ? 'INCONCLUSIVE - the sweep did not attempt two removals: '+JSON.stringify(rets)
    : rets[1]!==false ? 'INCONCLUSIVE - the second removal was not refused, so the floor never engaged'
    : !countsAgree ? 'CONFIRMED - after the refusal matchDice ('+after.md.length+') and numDice ('+after.numDice+') disagree'
    : recovered.pool===0 ? 'CONFIRMED and SEVERE - the counts agree but the table never deals again'
    : 'REFUTED on this arm too - the refusal skips _dropLanes, the counts stay level, and the next deal restores the die'
};
