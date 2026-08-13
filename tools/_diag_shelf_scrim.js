/* Control: does the SHELF's own focus scrim also read opacity 0 headless?
 * SUITE: exclude */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof showScreen==='function'&&S&&S.run,9000);
/* open the loadout/shelf directly */
try{famLoadoutShow();}catch(e){return {err:'famLoadoutShow: '+e};}
await until(()=>vis(document.getElementById('gbLoadout')),9000);
await sleep(1500);
const die=document.querySelector('#loStage .loDie');
if(!die)return {err:'no shelf die'};
try{_loFocus(die);}catch(e){return {err:'loFocus threw: '+e};}
await sleep(800);
const ov=document.getElementById('gbLoadout');
const scrim=document.getElementById('loFocusScrim');
const pan=document.getElementById('loFocusPanel');
return {cls:ov.classList.contains('lo-focus'),
 scrimOp:scrim?getComputedStyle(scrim).opacity:null,
 panOp:pan?getComputedStyle(pan).opacity:null,
 trans:scrim?(scrim.getAnimations()||[]).map(a=>({state:a.playState,cur:a.currentTime})):null};
