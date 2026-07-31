const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2500);
_getS();
(S.run.night.roster||[]).forEach((p,i)=>{if(i===0)p._art='Dunstan';});
save();showScreen('gauntlet');await sleep(1500);
const c=[...document.querySelectorAll('.ptcard')].filter(vis)[0];
if(c)tap(c);
await sleep(1800);
const im=document.querySelector('#ptPort .pwho');
const port=document.getElementById('ptPort');
const pr=port?port.getBoundingClientRect():null;
const ir=im?im.getBoundingClientRect():null;
return {panelOpen:vis(document.getElementById('ptPanelSheet'))||vis(document.getElementById('ptPanel')),
  imgSrc:im?im.getAttribute('src'):null, loaded:im?(im.complete&&im.naturalWidth>0):null,
  portBox:pr?{x:Math.round(pr.left),y:Math.round(pr.top),w:Math.round(pr.width),h:Math.round(pr.height)}:null,
  imgBox:ir?{x:Math.round(ir.left),y:Math.round(ir.top),w:Math.round(ir.width),h:Math.round(ir.height)}:null,
  overflowsTop: ir&&pr? Math.round(pr.top-ir.top):null};
