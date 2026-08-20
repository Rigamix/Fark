/* SHORT FUSE. Leg A: keeps on rolls 1,2 (100 each, no double), keep
 * a 5 on roll 3 committed BY ROLLING (rc=3 at the commit tap - x2:
 * 100), keep a 5 on roll 4 committed BY BANKING. Bank total says
 * whether the bank-commit path doubles: 350 = it does NOT (suspect:
 * famCommitBonus only runs on the roll path), 400 = it does.
 * Leg B: get lit (a roll-3 commit), then bust - the fire must spread:
 * pPts drops by the turn's lost points. */
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
G.pF=[{id:'short_fuse',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const keepValAndRoll=async(val,next)=>{
  const d=G.pool.find(x=>!x.committed&&x.val===val);
  if(!d)return false;
  tap(d.el);await sleep(250);
  next.forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing'||G.phase==='opp',15000))return false;
  await sleep(500);return true;
};
tap(document.getElementById('btnRoll'));/* roll 1 */
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(500);
if(!await keepValAndRoll(1,[1,2,3,4,6]))return {err:'roll 2 failed'};
if(!await keepValAndRoll(1,[5,2,3,4]))return {err:'roll 3 failed'};
/* roll 3 is on the table; commit its 5 BY ROLLING (rc=3 at the tap) */
if(!await keepValAndRoll(5,[5,2,3]))return {err:'roll 4 failed'};
const litAfterR3=!!G.pF[0].state.lit;
/* roll 4 on the table: keep its 5 and commit BY BANKING */
const five=G.pool.find(x=>!x.committed&&x.val===5);
if(!five)return {err:'no 5 r4',vals:G.pool.map(d=>d.val)};
tap(five.el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const bankDelta=G.pPts-p0;
/* LEG B: lit then bust */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankDelta};
await sleep(2000);
[1,2,3,4,6,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B1'};
await sleep(500);
if(!await keepValAndRoll(1,[1,2,3,4,6]))return {err:'roll B2 failed'};
if(!await keepValAndRoll(1,[5,2,3,4]))return {err:'roll B3 failed'};
/* commit roll 3's 5 by rolling -> lit; the roll comes up DEAD -> bust */
const pBefore=G.pPts;
if(!await keepValAndRoll(5,[2,3,4]))return {err:'roll B4 failed'};
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,20000))return {err:'no bust B',phase:G.phase};
await sleep(800);
const burned=pBefore-G.pPts;
/* the lost turn: 100+100+100(the lit x2 five) = 300 */
return {bankDelta:bankDelta,litAfterR3:litAfterR3,burned:burned,pBefore:pBefore,pPts:G.pPts,
  verdicts:{
    litFromRollThree:litAfterR3,
    rollCommitDoubled_bankTotal350:bankDelta===350,
    bankCommitAlsoDoubled_total400:bankDelta===400,
    fireSpreadToBank:burned>0,
    burnedExactlyTheLostTurn:burned===300},
  verdict:litAfterR3&&burned===300&&(bankDelta===350||bankDelta===400)};
