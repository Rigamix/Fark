/* S7(b)+(c) / P530 - does the loan's seat survive the things that move seats?

   One arm per browser session was the lesson from S6, but these three arms do
   not roll or end turns, so they cannot degrade the fixture the way that one
   did - they mutate state and call one function. Stated so the choice is a
   choice rather than an oversight.

   THREE PROPERTIES:
     A  a REORDER must carry the loan with it, or the loan protects whichever
        die moved into the seat it used to hold - S7(b)'s real mechanism, since
        _breakBorrowed gates on the lane before it ever tests the material
     B  CONFISCATION must shift the loan when it takes a seat below it, and must
        honour the one-die floor
     C  a loan pointing OUTSIDE the loadout must not protect anything */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _breakBorrowed!=='function')return{error:'_breakBorrowed is not global'};

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
await sleep(800);
if(G.pool.length<4)return{error:'pool too small'};

/* ---- A: a reorder must carry the loan --------------------------------- */
G.matchDice=['bone','iron','obsidian','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];
G._fairTrade={lane:2,was:'flint',borrowed:'obsidian'};
const meshes=(G.pool||[]).map((d,i)=>({chip:d.el,phys:{x:i*10,y:0},hx:undefined,tx:0,ty:0,match:true}));
const laneBeforeA=G._fairTrade.lane;
const dieInLoanSeat=(G.pool||[]).filter(d=>d.lane===2)[0]||null;
/* THE FIXTURE MUST BE INTERNALLY CONSISTENT. Setting matchDice[2]='obsidian'
   while the die standing there still had mat 'flint' created a state real play
   cannot produce, and P520 deliberately takes the material from the DIE (what
   is painted) - so it wrote 'flint' back and the arm scored a working fix as a
   failure. Brand the die itself, not just the seat. */
if(dieInLoanSeat)dieInLoanSeat.mat='obsidian';
if(meshes.length>=3){
  _vgDragState={die:meshes[0].chip,me:meshes[0],order:meshes.slice(),
    homes:meshes.map(m=>m.phys.x),target:meshes.map(m=>m.phys.x),
    from:0,to:2,raf:0,y0:0,onMove:function(){},info:{mount:null,mid:0,sz:1}};
  try{_commitVagabondDrag();}catch(e){}
}
await sleep(400);
const A={laneBefore:laneBeforeA, laneAfter:(G._fairTrade||{}).lane,
  loanDieNowAtLane:dieInLoanSeat?dieInLoanSeat.lane:null,
  loanStillOnItsOwnDie:!!(dieInLoanSeat&&G._fairTrade&&G._fairTrade.lane===dieInLoanSeat.lane),
  matAtLoanSeat:(G.matchDice||[])[(G._fairTrade||{}).lane]};

/* ---- B: confiscation shifts the loan, and honours the floor ----------- */
G.matchDice=['bone','iron','flint','lead','obsidian','brass'];
G._enchArr=[null,null,null,null,null,null];
G.numDice=6;
G._fairTrade={lane:4,was:'amber',borrowed:'obsidian'};
const bBefore=G._fairTrade.lane;
_removeDieAt(1);                       /* a seat BELOW the loan goes */
const B={laneBefore:bBefore, laneAfterRemovalBelow:(G._fairTrade||{}).lane,
  shifted:(G._fairTrade||{}).lane===bBefore-1,
  matAtLoanSeat:(G.matchDice||[])[(G._fairTrade||{}).lane]};

/* the floor: down to one die, the removal must refuse */
G.matchDice=['bone']; G._enchArr=[null]; G.numDice=1;
const floorHeld=_removeDieAt(0)===false && G.matchDice.length===1;

/* ---- C: an out-of-range loan must not protect ------------------------- */
G.matchDice=['bone','iron','flint'];
G._enchArr=[null,null,null];
G._fairTrade={lane:5,was:'amber',borrowed:'obsidian'};
const victim={lane:5,mat:'bone'};
const protectedOutOfRange=_breakBorrowed(victim);

return {
  A_reorderCarriesLoan:A,
  B_confiscationShift:B, oneDieFloorHeld:floorHeld,
  C_outOfRangeProtects:protectedOutOfRange,
  verdict:
    !A.loanStillOnItsOwnDie ? 'FAIL - the reorder left the loan on the wrong seat (lane '+A.laneBefore+' -> '+A.laneAfter+')'
    : A.matAtLoanSeat!=='obsidian' ? 'FAIL - the loan seat no longer holds the borrowed material ('+A.matAtLoanSeat+')'
    : !B.shifted ? 'FAIL - a removal below the loan did not shift it ('+B.laneBefore+' -> '+B.laneAfterRemovalBelow+')'
    : B.matAtLoanSeat!=='obsidian' ? 'FAIL - after the shift the loan seat holds '+B.matAtLoanSeat
    : !floorHeld ? 'FAIL - the one-die floor did not hold'
    : protectedOutOfRange ? 'FAIL - a loan pointing outside the loadout still protects a die'
    : 'PASS - the loan rides reorders and removals, and a stale loan protects nothing'
};
