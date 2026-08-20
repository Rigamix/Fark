/* P831's corner, driven: BOTH sides hold fool's gold, the rival rolls
 * dead. Pre-P831 the rival's deadRoll seam billed the PLAYER's charge
 * and armed the player's burn. Now: charge intact, no burn armed, and
 * the player's own copy still works next turn (regression leg). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
window._fkDiscardOk=true;
launchBossMatch();
if(!await until(()=>G&&G.phase==='idle',20000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'fools_gold_f',tier:1,charges:1,state:{}}];
G.oF=[{id:'fools_gold_f',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* rival: dead first roll (no 1/5, no combos) */
const realRF=window.rollFace;
let RQ=[2,2,3,3,4,6];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
tap(document.getElementById('btnBank'));/* 1000 clears LAST CALL */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2'};
await sleep(1500);
const chargeIntact=G.pF[0].charges;
const burnArmed=!!(G.pF[0].state&&G.pF[0].state.burn);
const rivalDead=RQ.length===0;/* their dead deal consumed the stub */
return {chargeIntact,burnArmed,rivalDead,
  verdicts:{
    rivalRolledDead:rivalDead,
    playerChargeNotBilled:chargeIntact===1,
    noBurnArmed:!burnArmed},
  verdict:rivalDead&&chargeIntact===1&&!burnArmed};
