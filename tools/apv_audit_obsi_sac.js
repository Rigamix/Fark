/* SACRIFICE: from idle, shatter -> +800 lands IMMEDIATELY (code pays
 * G.pPts - the spec says turn total; measure which), the die is gone
 * for the match: matchDice 6->5 and the NEXT deal is five dice. Then
 * a normal keep+bank must still work on the smaller table. */
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
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* roll first so there is a table to shatter from */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
const md0=(G.matchDice||[]).length;
const p0=G.pPts,t0=G.turnPts||0;
famUse(0);
await sleep(600);
const pGain=G.pPts-p0;
const tGain=(G.turnPts||0)-t0;
const md1=(G.matchDice||[]).length;
const shatteredGone=!G.pool.some(d=>d._shattered&&!d.committed&&d.el&&d.el.isConnected);
/* the table now has 5 dice; keep the 1 and bank */
const one=G.pool.find(d=>!d.committed&&!d._shattered&&d.val===1);
if(!one)return {err:'no 1',vals:G.pool.filter(d=>!d._shattered).map(d=>d.val)};
tap(one.el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank',pGain};
const bankDelta=G.pPts-p1;
/* NEXT deal must be five dice */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',pGain,bankDelta};
await sleep(2000);
[1,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2'};
await sleep(700);
const dealt=G.pool.filter(d=>!d.committed).length;
return {pGain:pGain,tGain:tGain,md0:md0,md1:md1,bankDelta:bankDelta,
  dealtNextTurn:dealt,chargesLeft:G.pF[0].charges,
  verdicts:{
    paid800:(pGain===800&&tGain===0)||(pGain===0&&tGain===800),
    paysBankNotTurn:pGain===800,/* the spec-vs-code question, recorded */
    dieGoneForMatch:md0===6&&md1===5,
    nextDealFive:dealt===5,
    bankStillWorks:bankDelta===100,
    chargeSpent:G.pF[0].charges===0},
  verdict:(pGain===800||tGain===800)&&md1===5&&dealt===5&&bankDelta===100&&G.pF[0].charges===0};
