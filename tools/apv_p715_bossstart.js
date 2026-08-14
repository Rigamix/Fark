/* P715: a boss match starts cleanly WITHOUT the splash - no .boss-splash
 * element, the turn begins, no pouch image anywhere. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
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
launchBossMatch();
const sawSplash=await until(()=>document.querySelector('.boss-splash'),3500);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000);
if(!ok){try{G=null;}catch(e){}launchBossMatch();
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000);}
return {idle:ok,sawSplash,isBoss:!!(G&&G._isBoss),
 pouchImgs:document.querySelectorAll('img[src*="pouch.png"]').length,
 verdict:ok&&!sawSplash&&(G&&G._isBoss)&&document.querySelectorAll('img[src*="pouch.png"]').length===0};
