/* Which half of '#end-ov.fo-focus #foFocusScrim' fails to match? SUITE: exclude */
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
tap(document.querySelectorAll('#end-ov .fo-offer .fcv')[1]);await sleep(1000);
const ov=document.getElementById('end-ov');
const scrim=document.getElementById('foFocusScrim');
const pan=document.getElementById('foFocusPanel');
return {
 idCount:document.querySelectorAll('[id="end-ov"]').length,
 ovMatches:ov.matches('#end-ov.fo-focus'),
 ovClass:String(ov.className).slice(0,60),
 scrimIn:scrim?(scrim.closest('#end-ov')===ov):null,
 scrimMatches:scrim?scrim.matches('#end-ov.fo-focus #foFocusScrim'):null,
 panMatches:pan?pan.matches('#end-ov.fo-focus #foFocusPanel'):null,
 panParent:pan?pan.parentElement.id||pan.parentElement.tagName:null,
 qsVariant:!!document.querySelector('#end-ov.fo-focus #foFocusScrim'),
 scrimOp:scrim?getComputedStyle(scrim).opacity:null};
