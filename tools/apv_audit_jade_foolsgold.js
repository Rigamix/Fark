/* FOOL'S GOLD, the harsh path: keep 100, dead roll, the card rerolls
 * on its own, the reroll fails too - the bust must ALSO burn 100 off
 * the bank. A dead card leaves the reroll queue undrawn and pPts whole. */
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
G.pPts=1000;try{updHUD();}catch(e){}
G.pF=[{id:'fools_gold_f',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(400);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);
await sleep(300);
[2,3,4,3,4, 2,3,4,2,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G&&(G.pPts<1000||G.phase==='opp'),20000))return {err:'no bust',pPts:G.pPts,phase:G.phase,qLeft:Q.length};
await sleep(1500);
return {pPts:G.pPts,charges:G.pF[0]?G.pF[0].charges:null,queueLeft:Q.length,
  verdicts:{rerollDrawn:Q.length===0,
    burned:G.pPts===900,
    spent:!G.pF[0]||G.pF[0].charges===0},
  verdict:Q.length===0&&G.pPts===900&&(!G.pF[0]||G.pF[0].charges===0)};
