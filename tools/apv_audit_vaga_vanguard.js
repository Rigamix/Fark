/* VANGUARD t1: a scorer in the FIRST row spot (+200). Leg A: deal
 * puts the 1 first - select it, bank: 300. Leg B control: the 1 is
 * NOT first - bank: plain 100. Dead wire: both pay 100. */
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
G.pF=[{id:'vanguard_f',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];/* the 1 lands FIRST in the row */
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(500);
const firstIsOne=(G.pool[0]&&G.pool[0].val===1);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const bankA=G.pPts-p0;
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankA};
await sleep(2000);
[2,1,3,4,6,2].forEach(v=>Q.push(v));/* the 1 is SECOND now */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
const firstIsTwo=(G.pool[0]&&G.pool[0].val===2);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank B',bankA};
const bankB=G.pPts-p1;
return {bankA,bankB,firstIsOne,firstIsTwo,
  verdicts:{firstSpotPays300:firstIsOne&&bankA===300,
            controlPlain100:firstIsTwo&&bankB===100},
  verdict:firstIsOne&&bankA===300&&firstIsTwo&&bankB===100};
