const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1500);
const Q=[];for(let i=0;i<12;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const tap=el=>{const r=el.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await until(()=>!D3X._rolling(),12000);
await sleep(700);

/* select a die THROUGH THE GAME, the way a player does */
const free=(G.pool||[]).filter(d=>!d.committed);
const target=free.find(d=>d.val===1||d.val===5)||free[0];
if(target&&target.el)tap(target.el);
await sleep(700);

const out={
  settled:!D3X._rolling(),
  poolSelected:(G.pool||[]).filter(d=>d.sel).length,
  chipsWithSelectedClass:[...document.querySelectorAll('#playerDiceRow .die.selected')].length,
  d3xSelected:D3X.dice.filter(d=>d.match&&d.obj.visible&&d.chip.classList.contains('selected')).length,
  anyMatch:D3X.dice.some(d=>d.match),
  glowInk:D3X._glowInk,
  canvasExists:!!document.getElementById('dgCanvas'),
};
/* force one pass and look again */
try{D3X._drawGlow();}catch(e){out.threw=e.message;}
await sleep(120);
const cv=document.getElementById('dgCanvas');
out.afterForcedDraw={exists:!!cv,w:cv&&cv.width,h:cv&&cv.height};
if(cv&&cv.width){
  const x=cv.getContext('2d');const d=x.getImageData(0,0,cv.width,cv.height).data;
  let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>8)n++;
  out.afterForcedDraw.inkPx=n;
}
/* now add a cardmark with the selection REMOVED, and force again */
(G.pool||[]).forEach(d=>{if(d.el){d.el.classList.remove('selected');d.sel=false;}});
if(target&&target.el)target.el.classList.add('cardmark');
try{D3X._drawGlow();}catch(e){out.threw2=e.message;}
await sleep(120);
if(cv&&cv.width){
  const x=cv.getContext('2d');const d=x.getImageData(0,0,cv.width,cv.height).data;
  let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>8)n++;
  out.markAloneInkPx=n;
}
return out;
