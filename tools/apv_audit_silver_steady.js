/* STEADY HAND, two legs. A: arm, tap the 6 -> queued reroll makes it
 * a 5, charge billed AT THE TAP, bank 1+5 = 150 exactly. B: next
 * turn, arm, tap the ONLY scorer (the 1) -> reroll to 2 -> table now
 * dead -> the P535 re-derive must BUST the turn. Dead wire gives: no
 * face change leg A, no bust leg B. */
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
G.pF=[{id:'steady_hand',tier:2,charges:2,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll A'};
await sleep(800);
/* LEG A: arm, tap the 6 */
famUse(0);
await sleep(250);
if(!G._steadyArmed)return {err:'no arm A'};
const six=G.pool.find(d=>!d.committed&&d.val===6);
if(!six)return {err:'no 6',vals:G.pool.map(d=>d.val)};
Q.push(5);/* the reroll draw */
tap(six.el);
if(!await until(()=>six.val===5,6000))return {err:'no reroll A',val:six.val,charges:G.pF[0].charges};
const chargesAfterA=G.pF[0].charges;
await sleep(400);
const one=G.pool.find(d=>!d.committed&&d.val===1);
const five=G.pool.find(d=>!d.committed&&d.val===5);
tap(one.el);await sleep(200);tap(five.el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const bankA=G.pPts-p0;
/* LEG B: fresh turn, arm, reroll the only scorer into a dead table */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2'};
await sleep(2000);
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(800);
famUse(0);
await sleep(250);
if(!G._steadyArmed)return {err:'no arm B',charges:G.pF[0].charges};
const oneB=G.pool.find(d=>!d.committed&&d.val===1);
if(!oneB)return {err:'no 1 B',vals:G.pool.map(d=>d.val)};
const p1=G.pPts;
Q.push(3);/* scorer becomes a dead 3 -> table [3,2,3,4,6,2]: pairs only (a 2 would have made a TRIPLE of 2s - first draft's bug) */
tap(oneB.el);
/* the re-derive must bust: turn ends, nothing pays */
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=3,20000))return {err:'no bust B',val:oneB.val,phase:G.phase};
await sleep(500);
return {bankA:bankA,chargesAfterA:chargesAfterA,rerolledTo5:true,
  bustFired:true,pPtsAfterBust:G.pPts,p1:p1,chargesAfterB:G.pF[0].charges,
  verdicts:{
    rerollLanded:true,
    chargeBilledAtTap:chargesAfterA===1,
    bankA150:bankA===150,
    bustOnDeadReroll:true,
    bustPaidNothing:G.pPts===p1,
    secondChargeSpent:G.pF[0].charges===0},
  verdict:chargesAfterA===1&&bankA===150&&G.pPts===p1&&G.pF[0].charges===0};
