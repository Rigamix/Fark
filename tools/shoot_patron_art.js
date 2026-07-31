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
/* we are on the gauntlet/night screen with patron cards */
const imgs=[...document.querySelectorAll('.ptcard img.lwho')];
const probe=async(u)=>{try{const r=await fetch(u);return r.ok;}catch(e){return false;}};
const out=[];
for(const im of imgs){
  out.push({src:im.getAttribute('src'), loaded:im.complete&&im.naturalWidth>0, natW:im.naturalWidth});
}
/* test both candidate shapes for one name */
const cand=['Art/Assets/Frames/Patrons/Krox.png',
  'Art/Assets/Frames/Patrons/Characters/Krox.png',
  'Art/Assets/Frames/Patrons/optimized/Krox_opt.webp'];
const candOk={};
for(const c of cand)candOk[c]=await probe(c);
return {PT_P:(typeof PT_P!=='undefined'?PT_P:null),
  pool:(typeof PT_ART_POOL!=='undefined'?PT_ART_POOL:null),
  cardsOnScreen:imgs.length, portraits:out, candOk};
