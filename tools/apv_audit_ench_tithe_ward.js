/* TITHE + WARD through the real icon-keep seam.
 * Tithe: brand lane 0's 1, keep it with a 5, BANK: the icon banks
 * NOTHING (bank +50, not 150) and pays +15 gold.
 * Ward: next turn, brand ward, keep branded 1 + a 5 by ROLLING (arms),
 * remaining dice come up dead -> the bust pays HALF the turn (25). */
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
G.pF=[];try{famRenderRow();}catch(e){}
const Q=[1,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G._enchArr=[{t:'tithe',face:1},null,null,null,null,null];
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(600);
const branded=G.pool.find(d=>d.lane===0&&d.val===1);
if(!branded||!branded.ench)return {err:'no brand',ench:G.pool.map(d=>d.ench&&d.ench.t)};
const five=G.pool.find(d=>!d.committed&&d.val===5);
tap(branded.el);await sleep(150);tap(five.el);await sleep(300);
const g0=(S.run.gold||0),p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const bankA=G.pPts-p0,goldGain=(S.run.gold||0)-g0;
/* WARD turn */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankA,goldGain};
await sleep(2000);
G._enchArr=[{t:'ward',face:1},null,null,null,null,null];
[1,5,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(600);
const brandedW=G.pool.find(d=>d.lane===0&&d.val===1);
const fiveB=G.pool.find(d=>!d.committed&&d.val===5);
if(!brandedW)return {err:'no ward brand'};
tap(brandedW.el);await sleep(150);tap(fiveB.el);await sleep(300);
/* commit by rolling; the remaining four come up dead */
[2,2,3,4].forEach(v=>Q.push(v));
const p1=G.pPts;
tap(document.getElementById('btnRoll'));
await until(()=>!!G._wardArmed,8000);
const wardArmed=!!G._wardArmed;
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,25000))return {err:'no bust B',wardArmed};
await sleep(800);
const bustPay=G.pPts-p1;/* half of the 50 the turn held */
return {bankA,goldGain,wardArmed,bustPay,
  verdicts:{
    iconBankedNothing:bankA===50,
    tithePaid15:goldGain===15,
    wardArmedOnKeep:wardArmed,
    bustPaidHalf:bustPay===25},
  verdict:bankA===50&&goldGain===15&&wardArmed&&bustPay===25};
