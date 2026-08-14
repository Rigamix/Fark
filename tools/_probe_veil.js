const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(50);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame,9000);
const out={};
const v=()=>document.getElementById('loadVeil');
/* boot veil already released by now (menu shown) */
out.bootReleased=v()?v().style.opacity==='0':'no-veil';
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof showScreen==='function'&&S&&S.run,9000);
/* real navigation: the draft already landed on gauntlet - hop to SHOP */
showScreen('shop');
out.veilAtNav=v().style.opacity==='1'&&v().style.display==='block';
await until(()=>v().style.opacity==='0',5000);
out.releasedAfterImgs=v().style.opacity==='0';
await sleep(500);
out.hiddenAfterFade=v().style.display==='none';
/* same-screen re-call: no flash */
showScreen('shop');
out.noFlashOnSameScreen=v().style.display==='none';
out.verdict=out.veilAtNav&&out.releasedAfterImgs&&out.hiddenAfterFade&&out.noFlashOnSameScreen;
return out;
