/* SACRIFICE under P816 (Denis's ruling: the TURN, not the bank).
 * Leg A: keep a 1, shatter -> pPts UNCHANGED at the fire (the old
 * build paid instantly - this line is the different-when-old), pot
 * carries 800, the BANK collects 900. Leg B: fresh instance, keep a
 * 1, shatter, roll dead -> the bust burns the 800 with the turn:
 * pPts unchanged, pot zeroed. Die-permanence asserted both legs. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'sacrifice',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const md0=(G.matchDice||[]).length;
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p0=G.pPts;
famUse(0);
await sleep(600);
const instantPay=G.pPts-p0;          /* MUST be 0 now (was 800) */
const potA=G._turnBonusPot||0;       /* MUST be 800 */
const md1=(G.matchDice||[]).length;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A',instantPay,potA};
const bankA=G.pPts-p0;               /* 100 keep + 800 pot = 900 */
/* LEG B: the burn */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankA};
await sleep(2000);
G.pF=[{id:'sacrifice',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
famUse(0);
await sleep(600);
const potB=G._turnBonusPot||0;
const md2=(G.matchDice||[]).length;
/* instrument the dead-check before the roll */
const AS=[];const _oas=window.anyScoring;
window.anyScoring=function(fv){const r=_oas.apply(this,arguments);AS.push({fv:Array.isArray(fv)?fv.slice():fv,r:r});return r;};
let bustCalled=false;const _odb=window._delayedDoBust;
window._delayedDoBust=function(){bustCalled=true;return _odb.apply(this,arguments);};
/* roll the remaining free dice into a dead spread -> bust. THREE
   draws happen (5-die deal, one kept, one shattered) and the leg-A
   queue leaves a stray 2 in front - so push [3,4] to land [2,3,4].
   The first draft pushed [2,2,3,3]: with the stray that dealt [2,2,2],
   a scoring TRIPLE, and the game rightly refused to bust. */
[3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,25000))return {err:'no bust B',potB,phase:G.phase,rc:G.turnRollCount,locked:!!G._rollLocked,pool:G.pool.map(d=>({v:d.val,c:!!d.committed,sh:!!d._shattered})),qLeft:Q.length,AS:AS.slice(-6),bustCalled:bustCalled};
await sleep(800);
const burned=(G.pPts===p1);          /* the 800 died with the turn */
const potAfterBust=G._turnBonusPot||0;
return {instantPay,potA,bankA,md0,md1,potB,md2,burned,potAfterBust,pPts:G.pPts,p1,
  verdicts:{
    noInstantPay:instantPay===0,
    potCarries800:potA===800,
    bankCollects900:bankA===900,
    dieGoneLegA:md1===md0-1,
    bustBurnsThePot:burned&&potAfterBust===0,
    dieStillGoneLegB:md2===md1-1},
  verdict:instantPay===0&&potA===800&&bankA===900&&md1===md0-1&&burned&&potAfterBust===0&&md2===md1-1};
