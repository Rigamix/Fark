/* BREAK + QUICKSILVER.
 * Break: brand lane 0, keep the branded 1 + a 5, BANK -> the pending
 * break must resolve through the targeting flow: another of the
 * player's dice dies for good (matchDice 6->5 by the next deal).
 * Quicksilver: whole-die - the chip rerolls one free die, once per
 * turn (the second tap refuses). */
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
const md0=(G.matchDice||[]).length;
const Q=[1,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G._enchArr=[{t:'break',face:1},null,null,null,null,null];
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const branded=G.pool.find(d=>d.lane===0&&d.val===1);
if(!branded||!branded.ench)return {err:'no brand'};
tap(branded.el);await sleep(150);
tap(G.pool.find(d=>!d.committed&&d.val===5).el);await sleep(300);
tap(document.getElementById('btnBank'));
/* the targeting flow: dice offered as .break-target, tap one */
const offered=await until(()=>document.querySelectorAll('#playerDiceRow .die.break-target').length>0,10000);
let tappedTarget=false;
if(offered){
  await sleep(400);
  const t=document.querySelector('#playerDiceRow .die.break-target');
  if(t){tap(t);tappedTarget=true;}
}
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',offered,tappedTarget,pending:G._breakPending};
await sleep(2000);
const md1=(G.matchDice||[]).length;
/* QUICKSILVER on the fresh turn */
G._enchArr=(G._enchArr||[]).slice();G._enchArr[0]={t:'quicksilver'};
/* the deal reads _enchArr per lane; a quicksilver die needs no face */
const dealN=md1;
const dq=[1,2,3,4,6].slice(0,dealN);dq.forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2',md1};
await sleep(700);
const qsDie=G.pool.find(d=>d.ench&&d.ench.t==='quicksilver'&&!d.committed);
if(!qsDie)return {err:'no qs die',md1,enchs:G.pool.map(d=>d.ench&&d.ench.t)};
const v0=qsDie.val;
Q.push(6);
famQuicksilver();
await sleep(400);
const v1=qsDie.val;
Q.push(2);
famQuicksilver();/* once per turn - must refuse */
await sleep(400);
const v2=qsDie.val;
return {offered,tappedTarget,md0,md1,qsFrom:v0,qsTo:v1,qsSecond:v2,
  verdicts:{
    breakTargetingOffered:offered,
    dieGoneForGood:md1===md0-1,
    qsRerolled:v1===6&&v1!==v0,
    qsOncePerTurn:v2===v1},
  verdict:offered&&md1===md0-1&&v1===6&&v2===v1};
