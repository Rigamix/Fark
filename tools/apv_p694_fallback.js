/* P694: the portable fallback must paint. Patron-first (the adoption-reliable
 * path), control ink on the capable branch, then force __cfBlur=false and
 * repaint the SAME dice through the else branch. SUITE: exclude */
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

const _origPaint = _diceShadowPaint;
window._pCalls = 0; window._pErr = null;
_diceShadowPaint = function () { window._pCalls++;
  try { return _origPaint.apply(this, arguments); }
  catch (e) { window._pErr = String(e && e.stack || e).slice(0, 200); throw e; } };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
window._fkDiscardOk = true; /* P693: probes launch, never resume */
launchSeat(0);
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000);
if (!ok) { try { G = null; } catch (e) {} launchSeat(0);
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000); }
if (!ok) return { err: 'no idle' };
handleRoll();
await until(() => G.pool && G.pool.length >= 3, 9000);
await sleep(2800);

const out = { adopted: !!(window.D3X && D3X._tbl && D3X.dice.some(d => d.match)) };
out.control = { cfBlur: _cfBlur(), ink: fullInk(), pCalls: window._pCalls, pErr: window._pErr };

window.__cfBlur = false; window._pCalls = 0; window._pErr = null;
_dsDirty(); await sleep(900);
out.forced = { cfBlur: _cfBlur(), ink: fullInk(), pCalls: window._pCalls, pErr: window._pErr };
out.verdict = out.adopted && out.control.ink.area > 40 && out.forced.ink.area > 40 && !out.forced.pErr;
return out;
