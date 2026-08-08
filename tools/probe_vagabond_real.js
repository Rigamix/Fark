/* P520 - did the Vagabond reorder become real, and do the tap targets follow?

   A completed pointer drag is not possible under SwiftShader, so the commit
   state is CONSTRUCTED and _commitVagabondDrag is called directly. That is the
   function P520 changes, so it is the right unit - but it means this probe
   proves the commit, not the gesture, and says so.

   Two properties:
     1. seat == lane. After the move, every die's material and enchant sit in
        the lane the die now occupies.
     2. the chip cache is fresh. d.hx is the cached layout centre; if it still
        matches _rawCentre then _slaveHost draws the chip where the hit box is.

   AND THE INSTRUMENT IS TESTED. A "cache is fresh" check that cannot see a
   stale cache would pass on a broken build too, so the last arm deliberately
   re-stales one die and requires the check to catch it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
await sleep(250);
try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,9000)))return{error:'no pool'};
await sleep(900);

/* brand two lanes so the enchant question is answerable, not assumed */
G._enchArr=G._enchArr||[];
G._enchArr[0]={t:'tithe',face:1};
G._enchArr[2]={t:'ward'};

const meshOf=el=>{let m=null;(D3X.dice||[]).forEach(q=>{if(q.chip===el)m=q;});return m;};
const rowMesh=()=>(G.pool||[]).map(d=>meshOf(d.el)).filter(Boolean);

const before=(G.pool||[]).map(d=>({lane:d.lane,mat:d.mat,
  md:G.matchDice[d.lane],ench:JSON.stringify((G._enchArr||[])[d.lane]||null)}));

/* --- freshness of the chip cache, measured the way _slaveHost consumes it -- */
function cacheDrift(){
  try{
    const mr=D3X.mount.getBoundingClientRect();
    return (D3X.dice||[]).filter(d=>d.match&&d.chip&&d.chip.closest('#playerDiceRow'))
      .map(d=>{
        if(d.hx===undefined)return {stale:false,undef:true,drift:0};
        const c=D3X._rawCentre(d.chip,d.tx,d.ty);
        const drift=Math.abs(d.hx-(c.x-mr.left));
        return {drift:Math.round(drift*10)/10, stale:drift>1.5};
      });
  }catch(e){return [{error:e.message}];}
}
const driftBefore=cacheDrift();

/* --- construct the commit state and move die 0 to slot 2 ------------------ */
/* THE 3D LAYER DOES NOT INITIALISE HEADLESS - D3X.dice is empty and D3X.mount
   is falsy under SwiftShader, which is the hazard the sweep already recorded.
   _commitVagabondDrag only ever reads .chip and .phys off the objects in
   st.order, so synthetic stand-ins carrying the REAL DOM chips exercise the
   permutation code exactly. What they cannot exercise is d.hx, which lives on
   the meshes that do not exist here - so the tap-target half of P520 is NOT
   verified by this probe, and the result says so rather than implying it. */
let meshes=rowMesh();
const SYNTHETIC=meshes.length===0;
if(SYNTHETIC){
  meshes=(G.pool||[]).map((d,i)=>({chip:d.el,phys:{x:i*10,y:0},hx:undefined,tx:0,ty:0,match:true}));
}
if(meshes.length<3)return{error:'not enough dice: '+meshes.length};
const FROM=0, TO=2;
_vgDragState={
  die:meshes[FROM].chip, me:meshes[FROM], order:meshes.slice(),
  homes:meshes.map(m=>m.phys.x), target:meshes.map(m=>m.phys.x),
  from:FROM, to:TO, raf:0, y0:meshes[FROM].phys.y,
  onMove:function(){}, info:{mount:null,mid:0,sz:1}
};
try{ _commitVagabondDrag(); }catch(e){ return {error:'commit threw: '+e.message}; }
await sleep(600);

const after=(G.pool||[]).map(d=>({lane:d.lane,mat:d.mat,
  md:G.matchDice[d.lane],ench:JSON.stringify((G._enchArr||[])[d.lane]||null)}));

/* did the die that was at lane 0 carry its material AND its brand along? */
const moved=before[FROM];
const movedNow=after.find(a=>a.mat===moved.mat&&a.ench===moved.ench)||null;

const seatMatchesLane = after.every(a=>a.md===a.mat);
const lanesUnique = new Set(after.map(a=>a.lane)).size===after.length;
const lanesArePermutation =
  JSON.stringify(after.map(a=>a.lane).slice().sort((x,y)=>x-y))===
  JSON.stringify(before.map(a=>a.lane).slice().sort((x,y)=>x-y));
const brandsPreserved =
  JSON.stringify(before.map(b=>b.ench).slice().sort())===
  JSON.stringify(after.map(a=>a.ench).slice().sort());

const driftAfter=cacheDrift();
const anyStaleAfter=driftAfter.some(d=>d.stale);

/* --- can this check even SEE a stale cache? deliberately break one -------- */
let instrumentWorks=false;
try{
  const victim=(D3X.dice||[]).find(d=>d.match&&d.chip&&d.chip.closest('#playerDiceRow')&&d.hx!==undefined);
  if(victim){ victim.hx=victim.hx+72; instrumentWorks=cacheDrift().some(d=>d.stale); victim.hx=victim.hx-72; }
}catch(e){}

return {
  NOTE:'commit constructed directly - SwiftShader cannot complete a real pointer drag',
  SYNTHETIC_MESHES:SYNTHETIC,
  TAP_TARGETS_NOT_VERIFIED_HERE:SYNTHETIC,
  before:before, after:after,
  movedDieNowAt:movedNow,
  seatMatchesLane:seatMatchesLane,
  lanesUnique:lanesUnique,
  lanesArePermutation:lanesArePermutation,
  brandTravelled:brandsPreserved&&!!movedNow,
  cacheDriftBefore:driftBefore, cacheDriftAfter:driftAfter,
  cacheFreshAfterDrag:!anyStaleAfter,
  instrumentCanSeeStaleness:instrumentWorks,
  verdict:
    (!SYNTHETIC&&!instrumentWorks) ? 'INCONCLUSIVE - the freshness check cannot detect a stale cache, so its green is worthless'
    : !seatMatchesLane ? 'FAIL - a die is not standing in the lane holding its material'
    : !lanesUnique||!lanesArePermutation ? 'FAIL - lanes are not a permutation of the occupied seats'
    : !brandsPreserved ? 'FAIL - an enchant was lost or duplicated by the move'
    : (!SYNTHETIC&&anyStaleAfter) ? 'FAIL - the chip cache is still stale, tap targets remain offset'
    : SYNTHETIC ? 'PASS (reorder only) - seat==lane and the brand travelled. TAP TARGETS UNTESTED: no 3D layer headless'
    : 'PASS - seat==lane, the brand travelled, and the tap targets follow'
};
