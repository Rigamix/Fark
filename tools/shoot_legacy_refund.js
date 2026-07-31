/* #37/#38/#39: refund per MISSING die, uniformly, hoisted to run-load. */
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
_getS();
const R={};
/* a legacy save down TWO dice from the old run-scoped Break */
S.run.dice=['bone','bone','bone','bone'];
S.run.dieEnch=[null,null,null,null];
S.run.gold=100; delete S.run._diceV; delete S.run._breakRefundV;
const before=S.run.gold;
let fired=null;
for(const fn of ['_famDiceMigrate','_diceMigrate','_runLoadMigrate','_enchInit']){
  if(typeof window[fn]==='function'||typeof eval('typeof '+fn)!=='undefined'){
    try{eval(fn+'()');fired=fired||fn;}catch(e){}
  }
}
R.goldDelta=S.run.gold-before;
R.diceAfter=(S.run.dice||[]).length;
R.expectedPerDie=450;
R.twoDiceRefunded=R.goldDelta===900;
R.migrationsRun=fired;
return R;
