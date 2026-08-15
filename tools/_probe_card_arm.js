/* SUITE: exclude. A2: drive a REAL drag on a fam card past the threshold,
 * HOLD it there (no touchend) so the final screenshot shows the mid-drag
 * armed state. Data: classes + computed filter at the hold. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const out={};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000))return {err:'no idle'};
G.pF=[{id:'preserve',tier:1,charges:1,state:{}},{id:'honeytrap',tier:2,charges:2,state:{}}];
famRenderRow();
await sleep(800);
const el=document.querySelector('#famRowP .fcv');
if(!el)return {err:'no fcv'};
/* preserve needs a kept scorer to be playable */
G.kept=[{vals:[1],mat:'iron',pts:100,dice:[{val:1,mat:'iron',ench:null,lane:2}]}];
const r=el.getBoundingClientRect();
const x0=r.left+r.width/2,y0=r.top+r.height/2;
const line=_famThresholdY();
out.canPlay=_famCanPlay(0);
out.line=line;out.cardY=y0;
const mk=(type,x,y)=>{
  let ev;
  try{
    const t=new Touch({identifier:1,target:el,clientX:x,clientY:y});
    ev=new TouchEvent(type,{touches:type==='touchend'?[]:[t],bubbles:true,cancelable:true});
  }catch(e){out.touchFail=String(e);return null;}
  return ev;
};
const ts=mk('touchstart',x0,y0);
if(ts){el.dispatchEvent(ts);
  await sleep(60);
  document.dispatchEvent(mk('touchmove',x0,y0-15));
  await sleep(60);
  /* well past the threshold, and HOLD */
  document.dispatchEvent(mk('touchmove',x0,line-60));
  await sleep(400);
}
out.classes=el.className;
out.armed=el.classList.contains('armed');
out.dragLive=el.classList.contains('fcv-drag');
const cs=getComputedStyle(el);
out.filter=cs.filter.slice(0,220);
out.transform=el.style.transform;
/* release: the cast fires, the row rebuilds - check the spent state */
document.dispatchEvent(mk('touchend',x0,line-60));
await sleep(1200);
const el2=document.querySelector('#famRowP .fcv');
out.after={
  charges:G.pF[0]&&G.pF[0].charges,
  record:G._famPreserve?G._famPreserve.val:null,
  classes:el2?el2.className:null,
  spent:el2?el2.classList.contains('spent'):null,
  filter:el2?getComputedStyle(el2).filter.slice(0,200):null,
  bob:el2?getComputedStyle(el2.querySelector('.fcvIn')).animationName:null,
  usesPips:[...document.querySelectorAll('#famRowP .fcv')].map(c=>c.querySelectorAll('.fcvUses i').length)
};
const pip=document.querySelector('#famRowP .fcvUses');
out.pip=pip?{rect:pip.getBoundingClientRect().toJSON(),
 display:getComputedStyle(pip).display,z:getComputedStyle(pip).zIndex,
 i0:pip.querySelector('i')?{w:getComputedStyle(pip.querySelector('i')).width,
  h:getComputedStyle(pip.querySelector('i')).height,
  bg:getComputedStyle(pip.querySelector('i')).backgroundColor,
  rect:pip.querySelector('i').getBoundingClientRect().toJSON()}:null}:null;
return out;
