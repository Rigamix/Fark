/* P524 - does a rival bust-save still throw away the dice it is holding?

   THE INVARIANT, checked continuously rather than at one moment: a seat that is
   in G._oppHeld must never also appear in G.oppDice. Held means the rival is
   sitting on it; dealt means it was just thrown. The two sets intersecting is
   precisely D2 - the held record wiped, the seats re-derived from nothing, and
   the rival re-rolling dice it had already committed.

   Brutus's Grit is the carrier, so the arm is inconclusive unless a Grit save
   actually fires - a clean run where the rival never busted proves nothing.

   AND THE INSTRUMENT IS TESTED at the end: a fake overlap is injected and the
   checker must catch it, or its zero is worthless. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof runOppTurn!=='function')return{error:'runOppTurn is not global'};

const MATS=['bone','iron','flint','lead','amber','jade'];
const lanesOf=a=>(a||[]).map(d=>d&&d.lane).filter(l=>typeof l==='number');
function overlap(){
  const held=lanesOf(G&&G._oppHeld), dealt=lanesOf(G&&G.oppDice);
  if(!held.length||!dealt.length)return null;
  const h=new Set(held), bad=dealt.filter(l=>h.has(l));
  return bad.length?{held:held.slice(),dealt:dealt.slice(),collide:bad}:null;
}

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
G.matchOppDice=MATS.slice();

const collisions=[];
let gritSaves=0, lastGrit=0, samples=0;
const tick=setInterval(function(){
  try{
    samples++;
    const g=(G&&G._oGritUses)||0;
    if(g>lastGrit){gritSaves+=(g-lastGrit);lastGrit=g;}
    const o=overlap();
    if(o&&collisions.length<6)collisions.push(o);
  }catch(e){}
},80);

/* run turns until a Grit save fires, or we run out of patience */
for(let t=0;t<10;t++){
  if(!G||G._endMatchFired)break;
  G.oCards=['brutus_grit'];
  G._oGritUses=0;              // re-arm so more than one save is reachable
  lastGrit=0;
  try{ runOppTurn(); }catch(e){ clearInterval(tick); return {error:'runOppTurn threw: '+e.message}; }
  await sleep(6500);
  if(gritSaves>=2)break;
}
clearInterval(tick);

/* --- can the checker even SEE an overlap? --------------------------------- */
let instrumentWorks=false;
try{
  G._oppHeld=[{lane:0},{lane:1}];
  G.oppDice=[{lane:1},{lane:2}];
  instrumentWorks=!!overlap();
}catch(e){}

return {
  samples:samples, gritSavesObserved:gritSaves,
  collisionCount:collisions.length, collisions:collisions,
  instrumentCanSeeOverlap:instrumentWorks,
  verdict:
    !instrumentWorks ? 'INCONCLUSIVE - the overlap checker cannot detect an overlap'
    : gritSaves===0 ? 'INCONCLUSIVE - no bust-save fired, so nothing was tested'
    : collisions.length>0 ? 'FAIL - the rival dealt into a seat it was still holding'
    : 'PASS - held seats and dealt seats never intersected across '+gritSaves+' bust-save(s)'
};
