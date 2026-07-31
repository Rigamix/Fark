/* Brief §2: brands only on a natural 1 or 5; illegal ones are refunded+cleared. */
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
/* a legacy save: brands sitting on 3 and 6, which the new rule forbids */
S.run.dice=['bone','bone','silver','bone','bone','bone'];
S.run.dieEnch=[{t:'tithe',face:3},{t:'ward',face:6},{t:'snare',face:1},null,null,null];
S.run.gold=1000; delete S.run._enchV;
const goldBefore=S.run.gold;
try{_enchInit();}catch(e){R.err=String(e);}
R.after=(S.run.dieEnch||[]).map(e=>e?(e.t+'@'+e.face):null);
R.illegalCleared=!(S.run.dieEnch[0])&&!(S.run.dieEnch[1]);
R.legalKept=!!(S.run.dieEnch[2]&&S.run.dieEnch[2].face===1);
R.goldRefunded=S.run.gold-goldBefore;
R.enchV=S.run._enchV;
/* idempotent: a second pass must not refund again */
const g2=S.run.gold;
try{_enchInit();}catch(e){}
R.secondPassRefunds=S.run.gold-g2;
return R;
