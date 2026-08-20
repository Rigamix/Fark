/* PICKPOCKET t1 (P=100): every bank lifts 100 from the rival's purse.
 * Bank 100 with oPts 1000 -> pPts +200 total, oPts 900. Control: empty
 * their purse, bank again -> plain 100, no lift (min(P,0)=0). */
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
G.pF=[{id:'pickpocket',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=1000;try{updHUD();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p0=G.pPts,o0=G.oPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const pGainA=G.pPts-p0,oLossA=o0-G.oPts;
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',pGainA};
await sleep(2000);
G.oPts=0;try{updHUD();}catch(e){}
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts,o1=G.oPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank B',pGainA,oLossA};
const pGainB=G.pPts-p1,oLossB=o1-G.oPts;
return {pGainA,oLossA,pGainB,oLossB,
  verdicts:{bankLifts100:pGainA===200&&oLossA===100,
            emptyPurseNoLift:pGainB===100&&oLossB===0},
  verdict:pGainA===200&&oLossA===100&&pGainB===100&&oLossB===0};
