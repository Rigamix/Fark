/* DOUBLE OR NOTHING: arm, bank 100 with the flip FORCED LOST
 * (Math.random 0.9) -> tier-1 loses half the bank: net +50. Fresh
 * instance turn 2, flip FORCED WON (0.1) -> bank 100 doubles: +200.
 * Dead wire: both banks pay plain 100. */
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
G.pF=[{id:'double_or_nothing',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const realRandom=Math.random;
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(500);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
famUse(0);
await sleep(250);
if(!G.pF[0].state.armed)return {err:'no arm A'};
Math.random=()=>0.9;/* the flip LOSES */
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts!==p0,15000)){Math.random=realRandom;return {err:'no bank A'};}
await sleep(300);
Math.random=realRandom;
const netA=G.pPts-p0;
/* LEG B: fresh instance, flip WINS */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',netA};
await sleep(2000);
G.pF=[{id:'double_or_nothing',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
const oneB=G.pool.find(d=>!d.committed&&d.val===1);
tap(oneB.el);await sleep(300);
famUse(0);
await sleep(250);
if(!G.pF[0].state.armed)return {err:'no arm B'};
Math.random=()=>0.1;/* the flip WINS */
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000)){Math.random=realRandom;return {err:'no bank B'};}
await sleep(300);
Math.random=realRandom;
const netB=G.pPts-p1;
return {netA:netA,netB:netB,
  verdicts:{
    lostFlipNets50:netA===50,
    wonFlipNets200:netB===200,
    armConsumed:!G.pF[0].state.armed},
  verdict:netA===50&&netB===200};
