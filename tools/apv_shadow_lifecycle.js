/* THE SHADOW LIFECYCLE, MEASURED PER DIE: settle -> ink; keep -> that die's
 * ink gone, others stay; remove -> gone.  SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const inkUnder = d => { const cv = document.getElementById('dsCanvas'); if (!cv || !cv.width || !d.el) return -1;
  const r = d.el.getBoundingClientRect(), sc = document.getElementById('screen-match').getBoundingClientRect();
  const dpr = cv.width / sc.width;
  const x0 = Math.max(0, Math.round((r.left - sc.left - r.width * 0.4) * dpr));
  const y0 = Math.max(0, Math.round((r.top - sc.top - r.height * 0.2) * dpr));
  const w = Math.min(cv.width - x0, Math.round(r.width * 1.8 * dpr));
  const h = Math.min(cv.height - y0, Math.round(r.height * 1.6 * dpr));
  if (w < 2 || h < 2) return -1;
  const data = cv.getContext('2d').getImageData(x0, y0, w, h).data;
  let mx = 0; for (let i = 3; i < data.length; i += 8) if (data[i] > mx) mx = data[i];
  return mx; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchBossMatch();
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle', phase: (typeof G !== 'undefined' && G) ? G.phase : 'noG', runOk: !!(S && S.run) };
handleRoll();
await until(() => G.pool && G.pool.length >= 3, 6000);
/* POLL for the first shadow ink instead of sleeping blind - a random bust
   clears the pool ~1.7s after a scoreless settle, and two runs died inside
   that window. Ink appears at settle; measuring the moment it does keeps the
   whole test ahead of any bust clear. */
await until(() => G.pool && G.pool.length >= 3 && inkUnder(G.pool[0]) > 10, 8000);
const out = {};
if (!G.pool || G.pool.length < 3) return { err: 'pool cleared before settle (bust)', out };
out.settled = G.pool.slice(0, 4).map((d, i) => ({ i, ink: inkUnder(d) }));

/* keep die 0 through the state, then the canonical mark */
G.pool[0].committed = true;
_dsDirty();
await sleep(400); /* a few ticks */
out.afterKeep = G.pool.slice(0, 4).map((d, i) => ({ i, committed: !!d.committed, ink: inkUnder(d) }));

/* remove die 1 through the one exit path - guarded: a random bust between
   the roll and here clears the pool (it threw on 'el' of undefined once) */
if (!G.pool || G.pool.length < 2) { out.afterRemove = { skip: 'pool cleared (bust) before the removal test', poolLen: G.pool ? G.pool.length : 0 }; return out; }
const victim = G.pool[1];
const vRect = victim.el && victim.el.getBoundingClientRect();
_removeDieAt(victim.lane !== undefined ? victim.lane : 1);
await sleep(500);
out.afterRemove = { victimStillInPool: G.pool.includes(victim),
  inkAtVictimSpot: (() => { if (!vRect) return -1;
    const cv = document.getElementById('dsCanvas'), sc = document.getElementById('screen-match').getBoundingClientRect();
    if (!cv || !cv.width) return -1; const dpr = cv.width / sc.width;
    const x0 = Math.max(0, Math.round((vRect.left - sc.left - vRect.width * 0.4) * dpr));
    const y0 = Math.max(0, Math.round((vRect.top - sc.top - vRect.height * 0.2) * dpr));
    const data = cv.getContext('2d').getImageData(x0, y0,
      Math.min(cv.width - x0, Math.round(vRect.width * 1.8 * dpr)),
      Math.min(cv.height - y0, Math.round(vRect.height * 1.6 * dpr))).data;
    let mx = 0; for (let i = 3; i < data.length; i += 8) if (data[i] > mx) mx = data[i];
    return mx; })() };
return out;
