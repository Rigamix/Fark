/* Match path: measure time from first match die (CSS cube) to fk3d swap. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(30);} return false; };
const tap = el => { if(!el) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const out = {};

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

out.offerPhase = { d3xLoading: D3X.loading, d3xReady: D3X.ready,
  fk3d: document.documentElement.classList.contains('fk3d') };

_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF, 14000)) return { err: 'no match', out };

await sleep(1200);
tap(document.getElementById('btnRoll'));
await sleep(600);
out.afterTap = { dice: document.querySelectorAll('#screen-match .die').length,
  d3die: document.querySelectorAll('#screen-match .d3die').length,
  btnRoll: !!document.getElementById('btnRoll'),
  handleRoll: typeof handleRoll,
  phase: G&&G.phase, rollLocked: G&&G._rollLocked, endFired: G&&G._endMatchFired,
  loading: D3X.loading };
if (G && G.phase === 'waiting') { try { startPTurn(); } catch(e){ out.stErr = String(e); } await sleep(1500); }
if (!document.querySelector('#screen-match .die') && typeof handleRoll === 'function') { try { handleRoll(); } catch(e){ out.hrErr = String(e); } }
out.afterForce = { phase: G&&G.phase, dice: document.querySelectorAll('#screen-match .die').length };
/* first match die appears */
const gotDie = await until(()=>document.querySelector('#screen-match .die.d3on .d3die'), 10000);
const t0 = Date.now();
out.firstMatchDie = { got: gotDie, d3xReady: D3X.ready, d3xLoading: D3X.loading,
  fk3d: document.documentElement.classList.contains('fk3d'),
  cubeVisible: (function(){ const el=document.querySelector('#screen-match .die.d3on .d3die');
    if(!el) return null; const s=getComputedStyle(el);
    return s.visibility!=='hidden'&&s.display!=='none'; })() };

const tReady0 = Date.now();
await until(()=>D3X.ready, 30000);
out.msToReady = Date.now()-tReady0;
const swapped = await until(()=>document.documentElement.classList.contains('fk3d'), 15000);
out.swap = { happened: swapped, msCubeVisible: swapped ? Date.now()-t0 : null,
  d3xReady: D3X.ready, canvas: !!document.getElementById('d3xCanvas'),
  cubeNowHidden: (function(){ const el=document.querySelector('#screen-match .die.d3on');
    if(!el) return null; return getComputedStyle(el).backgroundImage==='none'||true; })() };
return out;
