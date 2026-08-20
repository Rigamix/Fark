/* SLOW COOK, measured against the card text 'every roll past your
 * second adds +150' - a three-roll turn must bank base+150. Suspect
 * found on read: the player's roll event fires BEFORE turnRollCount
 * increments and carries `rolls` (the handler reads `rollNum`), so
 * accrual may start a roll late. The bank amount decides. Then a
 * spill turn: accrue and bust - nothing may pay. */
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
G.pF=[{id:'slow_cook',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const keepOneAndRoll=async(next)=>{
  const d=G.pool.find(x=>!x.committed&&(x.val===1||x.val===5));
  if(!d)return false;
  tap(d.el);await sleep(250);
  next.forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing'||G.phase==='opp',15000))return false;
  await sleep(400);return true;
};
tap(document.getElementById('btnRoll'));/* roll 1 */
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(400);
if(!await keepOneAndRoll([1,2,3,4,6]))return {err:'roll 2 failed'};   /* roll 2 */
if(!await keepOneAndRoll([5,2,3,4]))return {err:'roll 3 failed'};     /* roll 3 */
/* keep the 5 from roll 3, then bank: base 100+100+50=250; text says
   roll 3 accrues +150 -> 400 expected */
const five=G.pool.find(x=>!x.committed&&x.val===5);
if(!five)return {err:'no 5',vals:G.pool.map(d=>d.val)};
tap(five.el);await sleep(250);
const acc=(G.pF[0].state&&G.pF[0].state.acc)||0;
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank',acc:acc};
const bankDelta=G.pPts-p0;
/* SPILL turn: three keeps then a dead roll -> bust; nothing may pay */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankDelta,acc};
await sleep(1500);
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'t2 roll1'};
await sleep(400);
if(!await keepOneAndRoll([1,2,3,4,6]))return {err:'t2 roll2'};
if(!await keepOneAndRoll([1,2,3,4]))return {err:'t2 roll3'};
const accT2=(G.pF[0].state&&G.pF[0].state.acc)||0;
const p1=G.pPts;
/* dead roll -> bust */
const d2=G.pool.find(x=>!x.committed&&(x.val===1||x.val===5));
if(!d2)return {err:'t2 no keeper'};
tap(d2.el);await sleep(250);
[2,3,4].forEach(v=>Q.push(v));/* only dead values remain: 3 free after keep? adjust below */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='opp'||G.pPts!==p1||(G.turnNum||0)>=3,25000)){}
await sleep(1500);
return {bankDelta:bankDelta,accAtBank:acc,accT2BeforeBust:accT2,pPtsAfterBust:G.pPts,p1:p1,
  verdicts:{
    textSaysFour:bankDelta===400,          /* 250 base + 150 roll-3 accrual */
    offByOne:bankDelta===250,              /* accrual never fired by roll 3 */
    spillPaysNothing:G.pPts<=p1},
  verdict:bankDelta===400&&G.pPts<=p1};
