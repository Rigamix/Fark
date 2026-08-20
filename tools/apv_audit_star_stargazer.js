
/* P811 probe: the stars must hold - peek, KEEP A DIE, roll: every
 * rolled die shows its lane's promised face. This is the exact path
 * that silently discarded the peek before. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
const QUEUE=[1,2,2,3,4,6];
const real=window._enchRollM;
window._enchRollM=(m,e)=>QUEUE.length?QUEUE.shift():real(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(600);
G.pF=[{id:'stargazer',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
famUse(0);
await sleep(200);
if(!G._famPeekVals||!G._famPeekVals.length)return {err:'no peek stored'};
const promise=JSON.parse(JSON.stringify(G._famPeekVals));
/* keep the 1 - the move that used to kill the peek */
const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(!one)return {err:'no 1',vals:G.pool.map(d=>d.val)};
tap(one.el);
await sleep(300);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.kept||[]).length>0,15000))return {err:'no reroll'};
await sleep(500);
const freeNow=G.pool.filter(d=>!d.committed&&!d._frozen);
const map={};promise.forEach(p=>{map[p.lane]=p.val;});
const rows=freeNow.map(d=>({lane:d.lane,val:d.val,promised:map[d.lane]}));
const held=rows.every(r=>r.promised!==undefined&&r.val===r.promised);
return {promise:promise,rolled:rows,
  verdicts:{fewerDice:freeNow.length<promise.length,starsHold:held,
    consumed:!G._famPeekVals||!G._famPeekVals.length},
  verdict:held&&freeNow.length<promise.length};

