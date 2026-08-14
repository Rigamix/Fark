/* P724: each rolling die carries its OWN settle frame; they differ. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(50);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame,9000);
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
if(!ok)return {err:'no idle'};
handleRoll();
/* sample mid-flight, after a few frames computed the lazy _setF */
await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.roll),9000);
await sleep(700);
const rolls=D3X.dice.filter(d=>d.match&&d.roll&&d.roll._setF!==undefined)
 .map(d=>({i:d.roll.i,setF:d.roll._setF,tape:d.roll.sol.frames.length}));
const setFs=rolls.map(r=>r.setF);
return {computed:rolls.length,rolls,
 allInBounds:rolls.every(r=>r.setF>=1&&r.setF<=r.tape),
 spread:setFs.length?Math.max(...setFs)-Math.min(...setFs):0,
 verdict:rolls.length>=3&&rolls.every(r=>r.setF>=1&&r.setF<=r.tape)};
