/* FALLING STAR t3 (threshold 1000): bank a triple of 1s (1000) ->
 * ANOTHER FULL TURN, opponent skipped (phase must never touch 'opp'
 * on the way to the next idle). Control: in the extra turn bank 100
 * -> the opponent DOES play. Dead wire: opp plays after both. */
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
G.pF=[{id:'falling_star',tier:3,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* phase touches 'opp' at endPTurn's top EVEN when the star skips the
   rival (the early-return sits mid-function) - the honest signal is
   whether the rival ROLLED: G._oRollNum increments per rival roll */
let orn0=0;
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
if(ones.length<3)return {err:'no triple',vals:G.pool.map(d=>d.val)};
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
const p0=G.pPts,tn0=G.turnNum||0;orn0=G._oRollNum||0;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank'};
const bank1=G.pPts-p0;
/* the extra turn must arrive WITHOUT an opp phase */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>tn0,30000))return {err:'no extra turn'};
const oppSkipped=((G._oRollNum||0)===orn0);
const extraTurnFlagCleared=!G._fExtraTurn;
/* CONTROL: bank 100 in the extra turn - the opponent must play */
await sleep(1500);
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2',oppSkipped};
await sleep(500);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
const orn1=G._oRollNum||0;
const p1=G.pPts,tn1=G.turnNum||0;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank 2',oppSkipped};
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>tn1,90000))return {err:'no turn 3',oppSkipped};
const oppPlayedAfterSmallBank=((G._oRollNum||0)>orn1);
return {bank1:bank1,oppSkipped:oppSkipped,extraTurnFlagCleared:extraTurnFlagCleared,
  oppPlayedAfterSmallBank:oppPlayedAfterSmallBank,
  verdicts:{
    bigBankBanked1000:bank1===1000,
    extraTurnNoOpp:oppSkipped,
    flagConsumed:extraTurnFlagCleared,
    controlOppPlays:oppPlayedAfterSmallBank},
  verdict:bank1===1000&&oppSkipped&&extraTurnFlagCleared&&oppPlayedAfterSmallBank};
