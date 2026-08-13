/* Measure the old-dice-first window: time between the first CSS-cube die
 * (D3 layer) appearing and html.fk3d hiding it (D3X ready). */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(30);} return false; };
const tap = el => { if(!el) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const out = {};

out.atLoad = { d3xReady: D3X.ready, d3xLoading: D3X.loading, fail: D3X.fail,
  fk3d: document.documentElement.classList.contains('fk3d'),
  threeLoaded: typeof THREE !== 'undefined' };

/* open new-run offer */
tap(document.getElementById('hsBtnBottom'));
const tDieShown = Date.now();
const gotDie = await until(()=>document.querySelector('.d3die'), 8000);
const tCssCube = Date.now();
out.cssCubeAppeared = gotDie;
out.atFirstCssCube = gotDie ? {
  msAfterTap: tCssCube - tDieShown,
  d3xReady: D3X.ready, d3xLoading: D3X.loading,
  fk3d: document.documentElement.classList.contains('fk3d'),
  cubeVisible: (function(){ const el=document.querySelector('.d3die');
    const s=getComputedStyle(el); return s.visibility!=='hidden'&&s.display!=='none'; })(),
  faceBg: (function(){ const f=document.querySelector('.d3f');
    return f?getComputedStyle(f).backgroundImage.slice(0,80):null; })()
} : null;

/* wait for the swap: fk3d added AND canvas present */
const swapped = await until(()=>document.documentElement.classList.contains('fk3d'), 15000);
const tSwap = Date.now();
out.swap = { happened: swapped,
  msCssCubeVisible: swapped ? tSwap - tCssCube : null,
  d3xReady: D3X.ready,
  canvas: !!document.getElementById('d3xCanvas'),
  cubeNowHidden: (function(){ const el=document.querySelector('#nrDice .d3die')||document.querySelector('.d3die');
    if(!el) return null; return getComputedStyle(el).visibility==='hidden'; })()
};
return out;
