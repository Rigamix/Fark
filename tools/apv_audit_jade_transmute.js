/* TRANSMUTE under P829's in-world picker: arm (targets painted, charge
 * NOT billed), tap the 2, tap the '5' face button in the house modal,
 * then prove the CHANGE SCORES - selectable, worth 50 at the bank -
 * and the charge is billed AT THE PICK. Also the walk-away: 'leave it'
 * costs nothing. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(500);
G.pF=[{id:'transmute',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const two=G.pool.find(d=>!d.committed&&d.val===2);
if(!two)return {err:'no 2',vals:G.pool.map(d=>d.val)};
/* LEG 0: walk-away - arm, tap the die, then 'leave it': charge intact */
famUse(0);
await sleep(300);
if(!G._transArmed)return {err:'no arm'};
tap(two.el);
if(!await until(()=>document.getElementById('gbModalHost')&&document.getElementById('gbModalHost').classList.contains('on'),6000))return {err:'no modal'};
const leave=[...document.querySelectorAll('#gbModalHost .gbx-btn')].find(b=>/leave/i.test(b.textContent));
tap(leave);
await sleep(300);
const chargeAfterLeave=G.pF[0].charges;/* must still be 1 */
/* LEG 1: the real pick - arm again, tap the 2, pick 5 */
famUse(0);
await sleep(300);
tap(two.el);
if(!await until(()=>document.getElementById('gbModalHost').classList.contains('on'),6000))return {err:'no modal 2'};
const face5=document.querySelector('#gbModalHost [data-f="5"]');
if(!face5)return {err:'no face button'};
tap(face5);
await sleep(400);
const nowVal=two.val;
const chargeAfterPick=G.pF[0].charges;
/* the change must SCORE: select the transmuted 5 + the natural 1, bank */
tap(two.el);await sleep(250);
tap(G.pool.find(d=>!d.committed&&d.val===1&&d!==two).el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank',nowVal,chargeAfterPick};
const bank=G.pPts-p0;
return {chargeAfterLeave,nowVal,chargeAfterPick,bank,
  verdicts:{
    walkAwayFree:chargeAfterLeave===1,
    dieBecame5:nowVal===5,
    chargeBilledAtPick:chargeAfterPick===0,
    changeScores150:bank===150},
  verdict:chargeAfterLeave===1&&nowVal===5&&chargeAfterPick===0&&bank===150};
