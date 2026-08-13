/* THE SHADOW LIFECYCLE VIA INK AREA - no position math (the mesh paints
 * translated from the wrap, which sank the per-die sampler).
 *   settle: total shadow area A0 > 0
 *   keep one die (+_dsDirty): A1 noticeably below A0, still > 0
 *   remove one die: A2 below A1
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
const inkArea = () => { const cv = document.getElementById('dsCanvas'); if (!cv || !cv.width) return 0;
  const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
  let a = 0; for (let i = 3; i < d.length; i += 32) if (d[i] > 30) a++;
  return a; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
/* PATRON, not boss: in some headless runs a fresh boss never gets its match
   dice adopted by D3X (matchDice 0, no _tbl) - an environment race, since
   every screenshot run adopts fine. The patron flow paints reliably and the
   lifecycle under test is identical. */
launchSeat(0);
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchSeat(1);
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle' };
/* NO ink polling - a full-canvas getImageData every 60ms starves the
   SwiftShader rAF loop and the shadows never paint (measured: the polled run
   read 0 where the sleep-once diag read 121). Sleep like the diag does, and
   retry the roll once if it busted scoreless. */
let out = null;
for (let attempt = 0; attempt < 2 && !out; attempt++) {
  handleRoll();
  await until(() => G.pool && G.pool.length >= 3, 8000);
  await sleep(2600);
  if (!G.pool || G.pool.length < 3) {
    await until(() => G && G.phase === 'idle', 25000); /* opp turn passes */
    continue;
  }
  out = { attempt, nDice: G.pool.length };
}
if (!out) return { err: 'busted twice' };
out.state = (() => { const cv = document.getElementById('dsCanvas');
  const band = (() => { if (!cv || !cv.width) return -1;
    const d = cv.getContext('2d').getImageData(0, Math.floor(cv.height*0.4), cv.width, Math.floor(cv.height*0.3)).data;
    let mx = 0; for (let i = 3; i < d.length; i += 16) if (d[i] > mx) mx = d[i]; return mx; })();
  return { cvW: cv ? cv.width : -1, cvH: cv ? cv.height : -1,
    mOn: window._mLight ? window._mLight.on : 'none', band,
    shDirty: window.D3X ? D3X._shDirty : 'noD3X', d3xOn: window.D3X ? D3X.on : false,
    fk3d: document.documentElement.classList.contains('fk3d'),
    tbl: { complete: window._tblImg && _tblImg.complete, nw: window._tblImg && _tblImg.naturalWidth,
           src: window._tblImg && _tblImg.src.split('/').pop() },
    d3xTbl: !!(window.D3X && D3X._tbl), d3xDice: window.D3X ? D3X.dice.length : -1,
    matchDice: window.D3X ? D3X.dice.filter(d => d.match).length : -1 }; })();
out.A0 = inkArea();

G.pool[0].committed = true;
_dsDirty();
await sleep(350);
out.A1 = inkArea();
out.keepShrank = out.A1 < out.A0 * 0.95 && out.A1 > 0;

if (G.pool.length >= 2) {
  const victim = G.pool[1];
  _removeDieAt(victim.lane !== undefined ? victim.lane : 1);
  await sleep(450);
  out.A2 = inkArea();
  out.removeShrank = out.A2 < out.A1;
} else out.A2 = 'pool too small';
return out;
