/* How long until D3X._rolling() clears after a roll, in THIS harness?
   Everything the FX work needs to verify - hull marks, state paint, centroid
   tracking - is behind _drawGlow, which skips entirely while _rolling() is
   true. If it never clears headless, none of Part Six's pixel tests can run
   here and that has to be known before any of it is built. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1500);
const tap=el=>{const r=el.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
const t0=Date.now();
tap(document.getElementById('btnRoll'));
const phaseAt=await until(()=>G.phase==='choosing',15000)?Date.now()-t0:null;
const cleared=await until(()=>!D3X._rolling(),30000);
const clearedAt=cleared?Date.now()-t0:null;
/* frame rate, because that is the suspected cause */
let frames=0;const fr=()=>{frames++;requestAnimationFrame(fr);};requestAnimationFrame(fr);
await sleep(2000);
return {
  phaseChoosingAtMs:phaseAt,
  rollingClearedAtMs:clearedAt,
  stillRollingAfter30s:!cleared,
  diceWithLiveTape:D3X.dice.filter(d=>d.roll).length,
  fps:Math.round(frames/2),
  glowCanvasNow:!!document.getElementById('dgCanvas'),
};
