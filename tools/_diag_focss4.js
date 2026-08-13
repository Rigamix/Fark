/* The stuck transition: read it, then kill it. SUITE: exclude */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
try{dbgWin();}catch(e){}
await until(()=>vis(document.getElementById('end-ov')),9000);
await sleep(2500);
tap(document.querySelectorAll('#end-ov .fo-offer .fcv')[1]);await sleep(800);
const scrim=document.getElementById('foFocusScrim');
const out={op0:getComputedStyle(scrim).opacity};
out.trans=(scrim.getAnimations()||[]).map(a=>{
 let kf=[];try{kf=a.effect.getKeyframes().map(k=>({o:k.opacity,off:k.offset,ease:String(k.easing).slice(0,10)}));}catch(e){}
 let t={};try{t=a.effect.getComputedTiming();}catch(e){}
 return {prop:a.transitionProperty||'?',state:a.playState,cur:a.currentTime,
  prog:t.progress,dur:t.duration,delay:t.delay,kf:kf};});
/* display chain */
out.chain=[];let e2=scrim;while(e2&&e2!==document.body){const cs=getComputedStyle(e2);
 out.chain.push({el:(e2.id||e2.className||e2.tagName).toString().slice(0,22),d:cs.display,cv:cs.contentVisibility||''});e2=e2.parentElement;}
/* kill the transition */
const st=document.createElement('style');
st.textContent='#foFocusScrim,#foFocusPanel{transition:none !important}';
document.head.appendChild(st);
await sleep(200);
out.afterKill={scrim:getComputedStyle(scrim).opacity,
 panel:getComputedStyle(document.getElementById('foFocusPanel')).opacity};
return out;
