/* P521 - do the rival's seats and its dice count still disagree?

   The sweep's reproduction: rival loadout with six distinct materials, Snuff on
   lane 2. Roll 1 dealt seats [0,1,3,4,5] correctly; every roll after dealt
   [0,1,3,4,5,5] - a duplicate, because the hot-dice reset put `left` back to a
   literal 6 while _snuffLane kept the seat list at 5, and the index guess
   `:i` invented seat 5 a second time. Measured at fourteen consecutive
   corrupted rolls in one turn.

   Sampled every 100ms across whole rival turns, so a corruption that only shows
   on later rolls of a turn cannot hide. Two arms: snuffed and clean.

   THE CLEAN ARM IS NOT DECORATION. A fix that simply dealt fewer dice would
   pass the snuffed arm; the clean arm is what catches it having broken the
   ordinary case. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof runOppTurn!=='function')return{error:'runOppTurn is not global'};

const MATS=['bone','iron','flint','lead','amber','jade'];

async function arm(label,snuffLane,turns){
  _getS(); S.run=S.run||{}; S.run.tier=2;
  S.run.dice=['bone','iron','flint','lead','amber','brass'];
  S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
  launchBossMatch();
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{label,error:'no match'};
  await sleep(700);
  G.matchOppDice=MATS.slice();

  const seen=[];            // every distinct lane-set observed
  const seenMats=[];
  let last='';
  const tick=setInterval(function(){
    try{
      if(!G||!G.oppDice||!G.oppDice.length)return;
      const lanes=G.oppDice.map(d=>d.lane);
      const key=lanes.join(',');
      if(key!==last){ last=key; seen.push(lanes.slice());
        seenMats.push(G.oppDice.map(d=>d.mat)); }
    }catch(e){}
  },100);

  for(let t=0;t<turns;t++){
    if(!G||G._endMatchFired)break;
    /* PROVE THE HOOK FIRES. runOppTurn increments G.oppTurnCount at 28036,
       BEFORE _lmDue('_snuff') tests turn===oppTurnCount - so arming with the
       current count guarantees a miss, and the first run of this probe reported
       "the snuffed seat was dealt" when the snuff had simply never armed. */
    if(snuffLane>=0){ G._snuff={lane:snuffLane,live:true,turn:(G.oppTurnCount||0)+1}; }
    try{ runOppTurn(); }catch(e){ clearInterval(tick); return {label,error:'runOppTurn threw: '+e.message}; }
    /* a rival turn runs on timers; wait for it to settle */
    await sleep(6000);
  }
  clearInterval(tick);

  /* did the snuff actually take effect even once? a five-seat set that skips
     the snuffed lane is the signature. Without it this arm proves nothing. */
  const snuffEverFired=(snuffLane<0)||seen.some(l=>l.length===MATS.length-1&&l.indexOf(snuffLane)===-1);
  const dupes=seen.filter(l=>new Set(l).size!==l.length);
  const hitSnuffed=(snuffLane>=0)?seen.filter(l=>l.indexOf(snuffLane)!==-1):[];
  const overCount=seen.filter(l=>l.length>MATS.length);
  /* the material a seat deals must be the material that LIVES there */
  const matMismatch=[];
  seen.forEach((lanes,n)=>{
    lanes.forEach((L,k)=>{ if(MATS[L]&&seenMats[n][k]&&MATS[L]!==seenMats[n][k])
      matMismatch.push({rollSet:n,seat:L,dealt:seenMats[n][k],lives:MATS[L]}); });
  });

  return {label:label, snuffLane:snuffLane,
          snuffEverFired:snuffEverFired,
          distinctLaneSets:seen.length,
          sample:seen.slice(0,8),
          duplicateSeatSets:dupes.length, duplicateExamples:dupes.slice(0,3),
          snuffedSeatDealt:hitSnuffed.length, snuffedExamples:hitSnuffed.slice(0,3),
          overCountSets:overCount.length,
          materialMismatches:matMismatch.length, materialExamples:matMismatch.slice(0,3)};
}

const SNUFFED=await arm('snuff on lane 2',2,4);
await sleep(800);
const CLEAN=await arm('no snuff',-1,3);

const bad=x=>!x||x.error||x.duplicateSeatSets>0||x.overCountSets>0||x.materialMismatches>0;
return {
  SNUFFED:SNUFFED, CLEAN:CLEAN,
  verdict:
    (SNUFFED.error||CLEAN.error) ? ('ERROR - '+(SNUFFED.error||CLEAN.error))
    : (SNUFFED.distinctLaneSets<3||CLEAN.distinctLaneSets<3)
        ? 'INCONCLUSIVE - too few rolls observed to say anything'
    : !SNUFFED.snuffEverFired ? 'INCONCLUSIVE - the snuff never armed, so this arm tested nothing'
    : SNUFFED.snuffedSeatDealt>0 ? 'FAIL - the snuffed seat was dealt, the enchant is undone mid-turn'
    : bad(SNUFFED) ? 'FAIL - the snuffed arm still corrupts seats'
    : bad(CLEAN) ? 'FAIL - the ordinary case broke'
    : 'PASS - no duplicate seats, no snuffed seat dealt, every material in its own lane'
};
