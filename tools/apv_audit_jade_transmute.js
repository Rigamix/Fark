/* TRANSMUTE: change a die, then prove the CHANGE SCORES - the value
 * flip alone could leave a die the scorer refuses. */
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
const answers=['2','5'];
const realP=window.prompt;
window.prompt=()=>answers.shift();
famUse(0);
window.prompt=realP;
await sleep(300);
const free=G.pool.filter(d=>!d.committed);
const changed=free[1];
tap(changed.el);
await sleep(300);
const sel=changed.sel===true||changed.el.classList.contains('selected');
[1,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.kept||[]).length>0,15000))return {err:'no commit',sel:sel,val:changed.val};
await sleep(400);
const keptPts=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
return {newVal:changed.val,selected:sel,charges:G.pF[0].charges,keptPts:keptPts,
  verdicts:{valChanged:changed.val===5,selectable:sel,spent:G.pF[0].charges===0,
    scored:keptPts>=50},
  verdict:changed.val===5&&sel&&G.pF[0].charges===0&&keptPts>=50};
