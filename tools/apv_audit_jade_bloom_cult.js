/* BLOOM + CULTIVATE with a CONTROL: turn 1 keeps a triple USING the
 * jade die (must pay +300 and grow the lane); turn 2 keeps a triple
 * WITHOUT it (must pay base only). The control falsifies an always-on
 * bonus; the jade turn falsifies a dead one. */
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
G.matchDice=['jade','bone','bone','bone','bone','bone'];
G.pF=[{id:'bloom',tier:1,charges:0,state:{}},{id:'cultivate',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[5,5,5,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(500);
const fives=G.pool.filter(d=>!d.committed&&d.val===5);
if(fives.length<3)return {err:'no triple',vals:G.pool.map(d=>d.val)};
for(const d of fives.slice(0,3)){tap(d.el);await sleep(150);}
[1,2,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>(G.kept||[]).length>0,15000))return {err:'no commit'};
await sleep(500);
const jadePts=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
const cult0=(G._cultArr||[])[0]||0;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,60000))return {err:'no turn 2',jadePts:jadePts,cult0:cult0};
await sleep(1500);
[2,5,5,5,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing 2'};
await sleep(500);
const fives2=G.pool.filter(d=>!d.committed&&d.val===5);
if(fives2.length<3)return {err:'no control triple',vals:G.pool.map(d=>d.val)};
for(const d of fives2.slice(0,3)){tap(d.el);await sleep(150);}
[1,2,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>(G.kept||[]).length>0,15000))return {err:'no commit 2'};
await sleep(500);
const controlPts=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
/* turn 3: the GROWN jade die scores again - growth must PAY (+50) */
tap(document.getElementById('btnBank'));
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=3,60000))return {err:'no turn 3',jadePts,controlPts};
await sleep(1500);
[5,5,5,2,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing 3'};
await sleep(500);
const fives3=G.pool.filter(d=>!d.committed&&d.val===5);
for(const d of fives3.slice(0,3)){tap(d.el);await sleep(150);}
[1,2,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>(G.kept||[]).length>0,15000))return {err:'no commit 3'};
await sleep(500);
const grownPts=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
return {jadePts:jadePts,controlPts:controlPts,grownPts:grownPts,cultLane0AtJadeTurn:cult0,
  verdicts:{
    bloomPays:jadePts===800,
    cultivateGrows:cult0===50,
    controlPaysBase:controlPts===500,
    growthPays:grownPts===850},
  verdict:jadePts===800&&cult0===50&&controlPts===500&&grownPts===850};
