/* Is the "mystery trim" just Pickpocket's palm - a designed rival effect?

   The trace showed the drop at t=1240: one pool entry gone, G.numDice 6 -> 5,
   G.matchDice unchanged at 6. That is the fingerprint of a per-turn removal
   that KEEPS the seat, and _maybeFireCutpurse has exactly that shape - it
   splices the victim from G.pool, calls _dropLanes(1), and does both inside a
   setTimeout for the flight animation, which would explain the ~1s delay.

   A matching fingerprint is not proof. This instruments the function itself and
   requires it to fire at the same moment the pool drops. If it does, the
   "phantom survives while a real die is discarded" observation is not a defect
   at all - it is the rival palming a die, working as designed, and the phantom
   simply was not the one chosen.

   The control matters as much: with the tell absent the palm must NOT fire and
   the pool must NOT drop. Otherwise something else is doing it and the palm is
   an innocent bystander that happened to be in the room. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _maybeFireCutpurse!=='function')return{error:'_maybeFireCutpurse is not global'};

const palmCalls=[];
const realPalm=window._maybeFireCutpurse;
window._maybeFireCutpurse=function(){
  const before=(G&&G.pool)?G.pool.length:null;
  const r=realPalm.apply(this,arguments);
  palmCalls.push({enteredAt:Date.now(), poolAtEntry:before});
  return r;
};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000))){window._maybeFireCutpurse=realPalm;return{error:'no match'};}
await sleep(700);

async function arm(label, wantTell){
  try{startPTurn();}catch(e){}
  await sleep(250);
  G.matchDice=['bone','iron','flint','lead','amber','brass'];
  G._enchArr=[null,null,null,null,null,null];G.numDice=6;G.pool=[];
  /* the tell is what licenses the palm - _ruleActive('pickpocket','p') */
  if(wantTell){ G._tell={id:'pickpocket'}; }
  else { G._tell=null; G._sleeve=null; }
  palmCalls.length=0;
  try{handleRoll();}catch(e){}
  if(!(await until(()=>G&&G.pool&&G.pool.length>0,8000)))return{label,error:'no pool'};
  await sleep(650);
  if(!G.pool.length)return{label,error:'pool emptied'};
  const keep=G.pool[0];
  G.pool=[keep]; keep.lane=99;
  const t0=Date.now();
  let dropAt=null, lastLen=null;
  const tick=setInterval(function(){
    try{
      if(!G||!G.pool)return;
      const len=G.pool.length;
      if(lastLen!==null&&len<lastLen&&dropAt===null)dropAt=Date.now()-t0;
      lastLen=len;
    }catch(e){}
  },30);
  try{handleRoll();}catch(e){}
  await sleep(2600);
  clearInterval(tick);
  return {label:label, tellPresent:!!wantTell,
          palmFired:palmCalls.length, dropAtMs:dropAt,
          numDiceEnd:G.numDice, matchDiceEnd:(G.matchDice||[]).length,
          lanesEnd:(G.pool||[]).map(d=>d.lane)};
}

const WITH = await arm('tell present', true);
await sleep(500);
const WITHOUT = await arm('no tell', false);
window._maybeFireCutpurse=realPalm;

return {
  WITH_TELL:WITH, WITHOUT_TELL:WITHOUT,
  verdict:
    (WITH.error||WITHOUT.error) ? ('INCONCLUSIVE - '+(WITH.error||WITHOUT.error))
    : (WITH.palmFired>0 && WITH.dropAtMs!==null && WITHOUT.dropAtMs===null)
        ? 'EXPLAINED - the drop is Pickpocket palming a die. Designed behaviour, not a defect.'
    : (WITHOUT.dropAtMs!==null)
        ? 'NOT EXPLAINED - the pool dropped with no tell and no palm; something else does it'
    : (WITH.palmFired===0 && WITH.dropAtMs!==null)
        ? 'NOT EXPLAINED - the pool dropped without the palm firing'
    : 'INCONCLUSIVE - no drop in either arm, nothing was exercised'
};
