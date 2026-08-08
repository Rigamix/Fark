/* S5 - the shatter sweep. Denis's gate first: is the DUPLICATE-lane producer
   still alive after P519, or is that arm now latent?

   Three questions, in the order that decides whether anything needs building:

   1. THE GATE. Can the refill still stamp two pool dice into one lane? P512
      replaced the modulo with a free-lane walk and P519 refuses a lane that is
      not a real index - but neither dedupes the OVERFLOW fallback, which still
      computes (pool.length+i) % matchDice.length when the free lanes run out.
      Driven over many refills rather than argued from the source.

   2. THE CONSEQUENCE, regardless of (1). `.sort` descending protects against
      SHIFTING, not against duplicates - a sort cannot dedupe. Hand the same
      seat to _removeDieAt twice and the second call destroys an innocent
      neighbour. Constructed directly, so the answer holds whether or not the
      producer is currently reachable. A latent bug and a live one need
      different urgency, not different truth.

   3. D24's arm, re-checked post-P519: a laneless shattered die is dropped from
      _shLanes by the >=0 filter, and the `else` that would sweep it out of the
      pool runs only when _shLanes is EMPTY - so a MIXED batch strands it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);

/* ---- 1. THE GATE: does a duplicate lane ever appear in a live pool? ----- */
let dupSeen=0, refills=0, worstPool=null;
const tick=setInterval(function(){
  try{
    if(!G||!G.pool||!G.pool.length)return;
    refills++;
    const lanes=G.pool.map(d=>d.lane);
    if(new Set(lanes).size!==lanes.length){dupSeen++;if(!worstPool)worstPool=lanes.slice();}
  }catch(e){}
},70);
for(let t=0;t<4;t++){
  if(!G||G._endMatchFired)break;
  try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
  await sleep(200);
  for(let r=0;r<4;r++){
    try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
    await sleep(800);
    if(G.pool&&G.pool.length)G.pool.forEach(function(d,i){if(i===0)d.committed=true;});
  }
}
clearInterval(tick);

/* ---- 2. THE CONSEQUENCE: two shattered dice sharing one seat ------------ */
try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
await sleep(250);
try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
await until(()=>G&&G.pool&&G.pool.length>=4,7000);
await sleep(600);

G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];
G.numDice=6;
const mdBeforeDup=G.matchDice.slice();
/* two dice both claiming seat 2, both shattered - exactly what S1's fallback
   would mint, constructed here so the answer does not depend on it */
G.pool.forEach(function(d,i){d._shattered=false;d._shatterLane=undefined;});
G.pool[0].lane=2; G.pool[0]._shattered=true; G.pool[0]._shatterLane=2;
G.pool[1].lane=2; G.pool[1]._shattered=true; G.pool[1]._shatterLane=2;
const _shLanesDup=G.pool.filter(d=>d._shattered)
  .map(d=>d._shatterLane!==undefined?d._shatterLane:d.lane)
  .filter(L=>typeof L==='number'&&isFinite(L)&&L>=0).sort((a,b)=>b-a)
  .filter((L,i,a)=>i===0||L!==a[i-1]);
if(_shLanesDup.length)_shLanesDup.forEach(function(L){_removeDieAt(L,{permanent:false});});
G.pool=G.pool.filter(d=>!d._shattered);
const mdAfterDup=G.matchDice.slice();
/* seat 2 held 'flint'. Only flint should be gone; 'lead' is the innocent
   neighbour that inherits seat 2 after the first splice. */
const innocentKilled = mdBeforeDup.indexOf('lead')!==-1 && mdAfterDup.indexOf('lead')===-1;

/* ---- 3. D24's arm: a MIXED batch with one laneless shattered die -------- */
try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
await sleep(250);
try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
await until(()=>G&&G.pool&&G.pool.length>=3,7000);
await sleep(600);
G.pool.forEach(function(d){d._shattered=false;d._shatterLane=undefined;});
G.pool[0]._shattered=true; G.pool[0]._shatterLane=G.pool[0].lane;   // has a lane
G.pool[1]._shattered=true; G.pool[1].lane=undefined; G.pool[1]._shatterLane=-1; // laneless
const _shLanesMix=G.pool.filter(d=>d._shattered)
  .map(d=>d._shatterLane!==undefined?d._shatterLane:d.lane)
  .filter(L=>typeof L==='number'&&isFinite(L)&&L>=0).sort((a,b)=>b-a)
  .filter((L,i,a)=>i===0||L!==a[i-1]);
if(_shLanesMix.length)_shLanesMix.forEach(function(L){_removeDieAt(L,{permanent:false});});
G.pool=G.pool.filter(d=>!d._shattered);
const strandedLaneless = G.pool.filter(d=>d._shattered).length;

return {
  GATE_duplicateProducerLive: dupSeen>0,
  poolSamples:refills, duplicateSamples:dupSeen, firstDuplicatePool:worstPool,
  DUP_shLanes:_shLanesDup,
  DUP_mdBefore:mdBeforeDup, DUP_mdAfter:mdAfterDup,
  DUP_innocentNeighbourKilled:innocentKilled,
  MIX_shLanes:_shLanesMix, MIX_strandedShatteredInPool:strandedLaneless,
  verdict:
    (innocentKilled&&dupSeen>0) ? 'LIVE - duplicates occur AND the sweep kills a neighbour'
    : innocentKilled ? 'STILL BROKEN - the sweep kills a neighbour, but no duplicate was observed in '+refills+' pool samples'
    : dupSeen>0 ? 'PRODUCER LIVE but the sweep survived it - re-read'
    : (strandedLaneless>0) ? 'FAIL - a laneless shattered die is still stranded in the pool'
    : 'FIXED - one seat removed once, no neighbour killed, nothing stranded'
};
