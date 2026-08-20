/* ENCORE: reroll the CURRENT roll's free dice - kept stay, the reroll
 * counts as a roll, charge spent. Leg A: keep two 1s (200), encore the
 * remaining four into [5,5,5,3] from the queue, bank triple+kept =
 * 700 exactly. Leg B: encore into a dead spread - the resolve window
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
G.pF=[{id:'encore',tier:2,charges:2,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,1,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
if(ones.length<2)return {err:'no ones'};
tap(ones[0].el);await sleep(150);tap(ones[1].el);await sleep(250);
[5,5,5,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===2,20000))return {err:'no commit roll'};
await sleep(700);
const keptPts0=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
/* the four free dice are [5,5,5,3]; ENCORE rerolls THEM into [5,5,5,1] */
[5,5,5,1].forEach(v=>Q.push(v));
const rc0=G.turnRollCount;
famUse(0);
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===rc0+1,15000))return {err:'no encore',phase:G.phase};
await sleep(700);
const keptPts1=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
const freeVals=G.pool.filter(d=>!d.committed).map(d=>d.val).sort();
const fives=G.pool.filter(d=>!d.committed&&d.val===5);
const one=G.pool.find(d=>!d.committed&&d.val===1);
if(fives.length<3||!one)return {err:'reroll wrong',freeVals};
tap(fives[0].el);await sleep(120);tap(fives[1].el);await sleep(120);tap(fives[2].el);await sleep(120);tap(one.el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank'};
const bankDelta=G.pPts-p0;/* 200 kept + 500 triple + 100 = 800 */
/* LEG B: encore into a dead spread */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankDelta};
await sleep(2000);
[1,2,3,4,6,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(600);
const p1=G.pPts;
[2,3,4,6,6,2].forEach(v=>Q.push(v));/* all six free reroll dead */
famUse(0);
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,20000))return {err:'no bust B',phase:G.phase};
await sleep(500);
return {bankDelta:bankDelta,keptPts0:keptPts0,keptPts1:keptPts1,freeVals:freeVals,
  p1:p1,pPts:G.pPts,charges:G.pF[0].charges,
  verdicts:{
    keptSurvivedEncore:keptPts0===200&&keptPts1===200,
    rerollFromQueue:true,
    bank800:bankDelta===800,
    encoreIntoDeadBusts:true,
    bustPaidNothing:G.pPts===p1,
    bothChargesSpent:G.pF[0].charges===0},
  verdict:keptPts1===200&&bankDelta===800&&G.pPts===p1&&G.pF[0].charges===0};
