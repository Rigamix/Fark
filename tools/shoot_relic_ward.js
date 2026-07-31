/* Brief section 1 + AUDIT #1: the relic is a die that permanently carries Ward
 * on FACE 5, inherits Silver's weighted table, and counts against the one-Ward
 * loadout cap. Measured, not read. */
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
/* 1. the die's own definition */
const d=getDie('brutus_shield');
R.rollTable=(d&&d.rollTable)||null;
R.bornEnch=(d&&d.bornEnch)||null;
R.effectCleared=!(d&&d.effect);
/* 2. it actually rolls Silver's odds */
const c={};for(let i=0;i<120000;i++){const v=rollFace('brutus_shield');c[v]=(c[v]||0)+1;}
R.faceDist={};[1,2,3,4,5,6].forEach(f=>R.faceDist[f]=+((c[f]||0)/1200).toFixed(2));
/* 3. put it in the loadout: born ward stamped, cap sees it */
S.run.dice=['brutus_shield','bone','bone','bone','bone','bone'];
S.run.dieEnch=[null,null,null,null,null,null];
try{_enchInit();}catch(e){R.enchInitErr=String(e);}
R.dieEnch0=S.run.dieEnch[0];
R.wardOwned=(typeof _wardOwned==='function')?_wardOwned(-1):'no fn';
/* 4. idempotent */
const before=JSON.stringify(S.run.dieEnch);
try{_enchInit();}catch(e){}
R.idempotent=JSON.stringify(S.run.dieEnch)===before;
/* 5. a second Ward is unbuyable while the relic is held */
S.run.gold=5000;
try{_gbEnchantApply('ward',1,5);}catch(e){}
R.secondWardBlocked=!(S.run.dieEnch[1]&&S.run.dieEnch[1].t==='ward');
return R;
