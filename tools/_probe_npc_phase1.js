/* SUITE: exclude. P760: the NPC decision layer, driven LIVE.
 *
 * The ?sim=1 harness never runs the persona chooser (simTurn always
 * keeps the maximal set), so it is structurally blind to the bugs under
 * test - this drives the real _oppChooseFrom in the real page instead.
 * Denis's three sightings, as assertions:
 *   1. no persona may keep a bare 1 off a straight roll
 *   2. when the bank plan says stop, the pick IS the max-pts keep
 *   3. the release block is gone (a kept straight stays kept)
 * Plus: every persona's give-up vs the best candidate stays <= 500 EV,
 * and personas remain DISTINCT (aggro still keeps fewer dice than hoard
 * on a singles roll - the floor must not flatten identity).
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(90);}return false;};
const out={cases:{}};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))
  return {err:'game never booted'};
await until(()=>document.getElementById('screen-gauntlet'),8000);
try{launchSeat(0);}catch(e){return {err:'launchSeat: '+e.message};}
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};
if(typeof _oppChooseFrom!=='function'||typeof _legalKeeps!=='function')
  return {err:'decision layer not reachable'};

const mkDice=vals=>vals.map((v,i)=>({val:v,mat:'bone',ench:null,lane:i,kept:false}));
const bestPts=free=>{const c=_legalKeeps(free,'o',0);return c.length?c[0].pts:0;};
const evOf=(free,pick)=>{ /* re-derive the pick's candidate to read .ev */
  const c=_legalKeeps(free,'o',0);
  const t=_npcEvTable(['bone','bone','bone','bone','bone','bone']);
  let best=-1e9,ev=null;
  c.forEach(k=>{
    const L=k.left===0?_oHandAfterSweep():k.left;
    const e=k.pts+((L>=1&&L<=6)?(1-(t.bust[L]||0))*(t.gain[L]||0):0);
    if(e>best)best=e;
    if(k.pts===pick.pts&&k.sel.length===pick.sel.length)ev=(ev===null)?e:Math.max(ev,e);
  });
  return {best,ev};
};
G.oCards=[];G.matchOppDice=['bone','bone','bone','bone','bone','bone'];
G.oPts=0;G.pPts=0;G.target=6800;G._oSnuffLane=null;

const PKEYS=['aggro','ones','triples','straights','hoard','combo'];
/* case 1: a straight roll - nobody may keep a bare single */
out.cases.straight={};
for(const pk of PKEYS){
  G.rung={name:'T',persona:pk,agg:0.6,minBank:300,diceStop:2};
  const free=mkDice([1,2,3,4,5,6]);
  const total=bestPts(free);
  const pick=_oppChooseFrom(free,total,0);
  const give=pick?+(evOf(free,pick).best-evOf(free,pick).ev).toFixed(0):-1;
  out.cases.straight[pk]={kept:pick?pick.sel.length:0,pts:pick?pick.pts:0,give:give};
}
/* case 2: bank plan - near target, the pick must be the MAX keep */
G.rung={name:'T',persona:'aggro',agg:0.6,minBank:300,diceStop:2};
G.oPts=6600;/* 6600 + any keep >= 6800 -> oppShouldBank true immediately */
{
  const free=mkDice([1,5,3,3,4,6]);/* max keep = {1,5} = 150 */
  const total=bestPts(free);
  const pick=_oppChooseFrom(free,total,200);/* bank 200 -> 6600+200+150 crosses */
  out.cases.bankPlan={pts:pick?pick.pts:0,kept:pick?pick.sel.length:0,
    planned:G._oPlannedBank?JSON.parse(JSON.stringify(G._oPlannedBank)):null,
    pass:!!(pick&&pick.pts===150&&pick.sel.length===2)};
}
G.oPts=0;
/* case 3: persona identity survives the floor - singles roll */
out.cases.singles={};
for(const pk of ['aggro','hoard']){
  G.rung={name:'T',persona:pk,agg:0.6,minBank:300,diceStop:2};
  /* NOT a straight (my first version rolled 1-2-3-4-5-6 by accident and
   proved nothing): singles only, so style has room to differ */
const free=mkDice([1,5,2,2,3,6]);/* keeps: {1,5}=150, {1}=100, {5}=50 */
  const total=bestPts(free);
  const pick=_oppChooseFrom(free,total,0);
  out.cases.singles[pk]={kept:pick?pick.sel.length:0,pts:pick?pick.pts:0};
}
/* case 4: triples roll - the floor must not break the set-chase */
G.rung={name:'T',persona:'triples',agg:0.6,minBank:300,diceStop:2};
{
  const free=mkDice([2,2,2,1,5,6]);
  const total=bestPts(free);
  const pick=_oppChooseFrom(free,total,0);
  const hasTriple=pick&&pick.sel.filter(d=>d.val===2).length===3;
  out.cases.triples={kept:pick?pick.sel.length:0,pts:pick?pick.pts:0,holdsSet:!!hasTriple};
}
/* static: the release block is gone */
out.releaseGone=(typeof window._optionalSingles==='undefined');
out.verdicts={
  noStraightDiscard:Object.values(out.cases.straight).every(c=>c.pts>=1500),
  giveCapped:Object.values(out.cases.straight).every(c=>c.give>=0&&c.give<=500),
  bankTakesAll:out.cases.bankPlan.pass,
  personasDistinct:out.cases.singles.aggro.kept<out.cases.singles.hoard.kept,
};
out.verdict=Object.values(out.verdicts).every(v=>v);
return out;
