/* Does the P694 fallback PAINT? Force __cfBlur=false, then measure with the
 * dice census recorded beside the ink - a zero with no dice is no finding.
 * SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const fullInk = () => { const cv = document.getElementById('dsCanvas'); if (!cv || !cv.width) return {area:0,max:0};
  const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
  let a = 0, mx = 0; for (let i = 3; i < d.length; i += 16) { if (d[i] > 30) a++; if (d[i] > mx) mx = d[i]; }
  return { area: a, max: mx }; };

window.__cfBlur = false;

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
window._fkDiscardOk = true; /* P693: never resume in this diag */
launchBossMatch();
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchBossMatch();
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle' };
handleRoll();
const rolled = await until(() => G.pool && G.pool.length >= 3, 9000);
await sleep(2800);
const cv = document.getElementById('dsCanvas');
return { cfBlurForced: window.__cfBlur === false, cfBlurFn: _cfBlur(),
  rolled, dieCount: G.pool ? G.pool.length : -1, phase: G.phase,
  committed: G.pool ? G.pool.filter(d => d.committed).length : -1,
  canvas: cv ? { w: cv.width, h: cv.height, cssShown: vis(cv) } : null,
  ink: fullInk() };
