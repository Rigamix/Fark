/* Count frame() and _physPose() calls; capture any swallowed stack. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame&&D3X._physPose,9000);
let fc=0,fe=null,pc=0,pe=null;
const oF=D3X.frame;D3X.frame=function(){fc++;try{return oF.apply(this,arguments);}catch(e){if(!fe)fe=String(e&&e.stack||e).slice(0,400);throw e;}};
const oP=D3X._physPose;D3X._physPose=function(d){pc++;try{return oP.apply(this,arguments);}catch(e){if(!pe)pe=String(e&&e.stack||e).slice(0,400);throw e;}};
for(let a=0;a<3;a++){tap(document.getElementById('hsBtnBottom'));await sleep(2000);
 await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
 tap(document.querySelector('.nrdie'));await sleep(1200);
 tap(document.getElementById('nrTakeBtn'));await sleep(2400);
 if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000))break;}
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {err:'no idle',fc,fe};
const fcAtIdle=fc;
handleRoll();
await sleep(6000);
return {fcAtIdle,fc,pc,fe,pe,
 dice:(D3X.dice||[]).filter(d=>d.match).slice(0,3).map(d=>({roll:!!d.roll,phys:!!d.phys}))};
