/* Does a cardmark actually PAINT when nothing is selected?
   _drawGlow early-exits unless some die carries .selected. P856 added the
   cardmark paint INSIDE that pass, so if the exit fires first the mark is a
   class that draws nothing. Measured on the canvas pixels, not the class. */
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
/* WAIT FOR THE PHYSICS TO SETTLE, not just for the phase. _drawGlow skips
   the whole pass while D3X._rolling() is true, and at 1.2s after `choosing`
   it still was - so the first version of this probe measured a canvas that
   had never been created and reported a clean zero for the wrong reason. */
await until(()=>!D3X._rolling(),12000);
await sleep(600);
window.__settled=!D3X._rolling();

function inkOn(id){
  const cv=document.getElementById(id);
  if(!cv||!cv.width)return {exists:!!cv,px:0};
  const x=cv.getContext('2d');
  const d=x.getImageData(0,0,cv.width,cv.height).data;
  let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>8)n++;
  return {exists:true,w:cv.width,h:cv.height,px:n};
}
const free=(G.pool||[]).filter(d=>!d.committed);
const out={dice:free.length,settledBeforeMeasuring:window.__settled};

/* A: cardmark with NOTHING selected - the real steady-hand situation */
free.forEach(d=>{if(d.el){d.el.classList.remove('selected','cardmark');d.sel=false;}});
free[0].el.classList.add('cardmark');
await sleep(500);
out.markAlone=inkOn('dgCanvas');

/* B: same mark, but with another die SELECTED - the pass now runs */
free[1].el.classList.add('selected');free[1].sel=true;
await sleep(500);
out.markPlusSelection=inkOn('dgCanvas');

/* C: selection only, mark removed - the control that the canvas can ink */
free[0].el.classList.remove('cardmark');
await sleep(500);
out.selectionOnly=inkOn('dgCanvas');

out.VERDICT={
  canvasCanInk: out.selectionOnly.px>0,
  markPaintsAlone: out.markAlone.px>0,
  markPaintsWithSelection: out.markPlusSelection.px>out.selectionOnly.px,
};
return out;
