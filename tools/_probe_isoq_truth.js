/* SUITE: exclude. _isoQ truth table: mint still dice 1..6 into keptRow
 * exactly as the Preserve payout does; the screenshot reads the faces. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000))return {err:'no idle'};
const kr=document.getElementById('keptRow');
for(let v=1;v<=6;v++){
  const c=mkDie(v,'bone',null,true,null);
  c.classList.add('in-tray');
  kr.appendChild(typeof _wrapDie==='function'?_wrapDie(c):c);
}
await sleep(2000);
return {minted:[...kr.querySelectorAll('.die')].map(c=>c._trueVal),
 adopted:[...kr.querySelectorAll('.die')].map(c=>{
  const dx=D3X.dice.find(d=>d.chip===c);return dx?1:0;})};
