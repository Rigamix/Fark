/* Drive a real match to a win and hold the end overlay open for a look. */
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
await sleep(3200);

const ov=document.getElementById('end-ov');
const R=el=>{if(!el)return null;const r=el.getBoundingClientRect();
  return {t:+(100*r.top/innerHeight).toFixed(1),b:+(100*r.bottom/innerHeight).toFixed(1),
          l:+(100*r.left/innerWidth).toFixed(1),w:+(100*r.width/innerWidth).toFixed(1)};};
return {
  artOn:ov.classList.contains('win-art-on'),
  viewport:innerWidth+'x'+innerHeight,
  bg:R(ov.querySelector('.win-bg')), banner:R(ov.querySelector('.win-banner')),
  hands:R(ov.querySelector('.win-hands')), panel:R(ov.querySelector('.win-panel')),
  scores:R(ov.querySelector('.res-scores')), gold:R(ov.querySelector('.res-gold-wrap')),
  card:R(ov.querySelector('.res-card')), slots:R(ov.querySelector('.end-draft-slots')),
  broken:[...ov.querySelectorAll('img')].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'))
};
