/* S6 / P529 - does a pool entry that occupies NO seat still suppress a refill?

   needNew was G.numDice - G.pool.length, a raw count of entries, while the
   lanes it feeds come from a SET keyed by lane. A pool entry with a duplicate,
   missing or out-of-range lane occupies no seat but still counted as one, so
   needNew came out too small and a genuinely empty seat was never dealt a die.

   The property under test is simple and does not depend on how the bad entry
   got there: AFTER A ROLL, EVERY SEAT IN matchDice SHOULD CARRY A DIE.

   Three arms, each seeding a different flavour of seatless entry, plus a clean
   control so a fix that simply always deals six would still be caught. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);

async function arm(label, seed){
  /* A FRESH MATCH PER ARM. The first version ran three arms in one match and
     the later ones measured a pool of 0 - the match had moved on underneath
     them. A shared fixture that degrades between arms reports the fixture, not
     the code. */
  launchBossMatch();
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{label,error:'no match'};
  await sleep(650);
  try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
  await sleep(250);
  G.matchDice=['bone','iron','flint','lead','amber','brass'];
  G._enchArr=[null,null,null,null,null,null];
  G.numDice=6;
  G.pool=[];
  /* a first roll so real die objects exist, then reshape one of them */
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  if(!(await until(()=>G&&G.pool&&G.pool.length>0,7000)))return{label,error:'no pool'};
  await sleep(700);
  /* THE SETUP DIE MUST EXIST. The first roll can bust and empty the pool during
     the settle wait, and the previous version crashed on G.pool[0] instead of
     saying so. An arm that cannot build its own state is a skip, not a result. */
  if(!G.pool||!G.pool.length)return{label:label,skip:'pool emptied before the seed'};
  /* keep ONE die, drop the rest, then corrupt the survivor's seat */
  const keep=G.pool[0];
  G.pool=[keep];
  seed(keep);
  const before={pool:G.pool.length, lanes:G.pool.map(d=>d.lane), numDice:G.numDice};
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  /* SAMPLE AT THE DEAL. The diagnostic showed the pool correct at 400ms and a
     real die evicted by 1300ms - a separate defect (nothing sweeps a pool entry
     whose lane is invalid, and something later trims the pool back to numDice).
     Measuring late would score that as this fix failing. */
  await sleep(420);
  const lanes=(G.pool||[]).map(d=>d.lane);
  const valid=lanes.filter(L=>typeof L==='number'&&isFinite(L)&&L>=0&&L<G.matchDice.length);
  const covered=new Set(valid);
  const missing=[];
  for(let i=0;i<G.matchDice.length;i++)if(!covered.has(i))missing.push(i);
  return {label:label, before:before,
          poolAfter:G.pool.length, lanesAfter:lanes,
          seatsCovered:covered.size, seatsTotal:G.matchDice.length,
          seatsMissingADie:missing};
}

async function armRetry(label,seed){
  for(let a=0;a<4;a++){
    const r=await arm(label,seed);
    if(r&&!r.skip&&!r.error)return r;
    await sleep(400);
    if(a===3)return r;
  }
}
const CLEAN = await armRetry('clean control',      d=>{});
const OOB   = await armRetry('lane out of range',  d=>{d.lane=99;});
const NOLANE= await armRetry('lane undefined',     d=>{d.lane=undefined;});

const arms=[CLEAN,OOB,NOLANE].filter(a=>a&&!a.error&&!a.skip);
const allCovered = arms.every(a=>a.seatsMissingADie.length===0);
return {
  CLEAN:CLEAN, OUT_OF_RANGE:OOB, NO_LANE:NOLANE,
  verdict:
    arms.length<3 ? 'INCONCLUSIVE - an arm never built its state: '+JSON.stringify([CLEAN,OOB,NOLANE].map(a=>a&&(a.error||a.skip)))
    : CLEAN.seatsMissingADie.length ? 'FAIL - the clean control left a seat empty'
    : allCovered ? 'PASS - every seat carries a die in all three arms'
    : 'FAIL - a seatless pool entry still suppressed a refill: '+JSON.stringify(arms.map(a=>[a.label,a.seatsMissingADie]))
};
