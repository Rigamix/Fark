/* POWDER KEG: commit 200 (two 1s), detonate - EVERYTHING rerolls from
 * the queue, kept emptied - select the fresh triple of 5s and bank:
 * exactly 500 (the old 200 must NOT ride along; kept dice went back
 * into play). Leg B: detonate into a dead queue - the P535 re-derive
 * must bust the turn. */
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
G.pF=[{id:'powder_keg',tier:2,charges:2,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,1,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
if(ones.length<2)return {err:'no ones',vals:G.pool.map(d=>d.val)};
tap(ones[0].el);await sleep(150);tap(ones[1].el);await sleep(250);
[5,2,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===2,20000))return {err:'no commit roll'};
await sleep(700);
const keptBefore=(G.kept||[]).length;
if(!keptBefore)return {err:'nothing kept'};
/* DETONATE - all six reroll from the queue */
[5,5,5,2,3,4].forEach(v=>Q.push(v));
famUse(0);
if(!await until(()=>G.phase==='choosing'&&(G.kept||[]).length===0,15000))return {err:'no detonation',kept:(G.kept||[]).length};
await sleep(900);
const freeVals=G.pool.filter(d=>!d.committed&&!d._shattered).map(d=>d.val).sort();
const fives=G.pool.filter(d=>!d.committed&&d.val===5);
if(fives.length<3)return {err:'no triple',freeVals};
tap(fives[0].el);await sleep(150);tap(fives[1].el);await sleep(150);tap(fives[2].el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank'};
const bankDelta=G.pPts-p0;
/* LEG B: detonate into a DEAD table - must bust */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankDelta};
await sleep(2000);
[1,2,3,4,6,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(600);
const p1=G.pPts;
[2,2,3,3,4,6].forEach(v=>Q.push(v));/* dead: pairs only */
famUse(0);
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,20000))return {err:'no bust B',phase:G.phase,vals:G.pool.map(d=>d.val)};
await sleep(500);
return {bankDelta:bankDelta,freeValsAfterKeg:freeVals,chargesLeft:G.pF[0].charges,
  bustPaid:G.pPts,p1:p1,
  verdicts:{
    keptWentBackInPlay:true,
    bankExactly500:bankDelta===500,
    kegIntoDeadTableBusts:true,
    bustPaidNothing:G.pPts===p1,
    bothChargesSpent:G.pF[0].charges===0},
  verdict:bankDelta===500&&G.pPts===p1&&G.pF[0].charges===0};
