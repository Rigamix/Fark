/* SUITE: exclude. A4: a fresh feat lands on shelf entry - class, spray,
 * fanfare, and the fresh flag consumed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
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
await until(()=>typeof S!=='undefined'&&S&&S.run,9000);
_getS();
/* earn teetotaller the data way, then enter the shelf */
S.featsDone=S.featsDone||{};S.featsDone.teetotaller=1;
S.featsPinned=S.featsPinned||{};S.featsPinned.teetotaller=1;
S.featsFresh={teetotaller:1};
let sprays=0,fanfares=0;
const _fx=window._fxSpray;window._fxSpray=function(){sprays++;return _fx.apply(this,arguments);};
const _hd=SFX.hotDice;SFX.hotDice=function(){fanfares++;try{return _hd.apply(this,arguments);}catch(e){}};
famLoadoutShow();
out.pinExists=!!document.querySelector('#gbLoadout .loFeat[data-png="Teetotaller"]');
out.landed=await until(()=>{
  const el=document.querySelector('#gbLoadout .loFeat[data-png="Teetotaller"]');
  return el&&el.classList.contains('pin-land');},4000);
await until(()=>sprays>0,4000);
out.sprays=sprays;out.fanfares=fanfares;
out.freshCleared=Object.keys(S.featsFresh||{}).length===0;
out.verdict=out.pinExists&&out.landed&&sprays>0&&fanfares===1&&out.freshCleared;
return out;
