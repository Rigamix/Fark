/* WHO PAINTS DICE SHADOWS, AND WHEN? Patron vs boss, measured. SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const inkOn = cv => { if (!cv || !cv.width) return 0;
  const x = cv.getContext('2d'); let mx = 0;
  const d = x.getImageData(0, Math.floor(cv.height*0.4), cv.width, Math.floor(cv.height*0.3)).data;
  for (let i = 3; i < d.length; i += 16) if (d[i] > mx) mx = d[i];
  return mx; };
const bandArea = () => { const cv = document.getElementById('dsCanvas'); if (!cv || !cv.width) return 0;
  const d = cv.getContext('2d').getImageData(0, Math.floor(cv.height*0.35), cv.width, Math.floor(cv.height*0.4)).data;
  let a = 0; for (let i = 3; i < d.length; i += 16) if (d[i] > 30) a++; return a; };
const snap = label => ({ label, area: bandArea(),
  mLight: window._mLight ? { on: window._mLight.on } : null,
  plate: (() => { const p = document.getElementById('matchPlate'); return p ? getComputedStyle(p).display : 'none-el'; })(),
  dsInk: inkOn(document.getElementById('dsCanvas')),
  shInk: inkOn(document.getElementById('shCanvas')),
  isBoss: !!(G && G._isBoss) });

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS();
const out = { runs: [] };

/* patron */
try { G = null; } catch (e) {}
launchSeat(0);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000);
handleRoll();
await until(() => G.pool && G.pool.length, 6000);
await sleep(2600); /* settled */
out.runs.push(snap('patron-settled'));
/* P686 lifecycle: keep one die -> its shadow leaves on the next repaint */
if (G.pool && G.pool.length) {
  G.pool[0].committed = true;
  _dsDirty();
  await sleep(500);
  out.runs.push(snap('patron-after-keep-1-of-' + G.pool.length));
  const v = G.pool[1];
  if (v) { _removeDieAt(v.lane !== undefined ? v.lane : 1); await sleep(500);
    out.runs.push(snap('patron-after-remove')); }
}

/* boss */
try { exitMatch && exitMatch(); } catch (e) {}
await sleep(800);
try { G = null; } catch (e) {}
launchBossMatch();
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000);
out.runs.push(snap('boss-preroll'));
handleRoll();
await until(() => G.pool && G.pool.length, 6000);
await sleep(2600);
out.runs.push(snap('boss-settled'));
/* the keep filter, tested where painting is reliable */
if (G.pool && G.pool.length >= 2) {
  G.pool[0].committed = true; _dsDirty(); await sleep(500);
  out.runs.push(snap('boss-after-keep-1-of-' + G.pool.length));
  G.pool[1].committed = true; _dsDirty(); await sleep(500);
  out.runs.push(snap('boss-after-keep-2'));
}
return out;
