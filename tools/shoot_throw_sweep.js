/* Statistics on the throw, in PAINTED units, over many solves.
 *
 * The overlap that survived P347 showed up on first rolls only - roughly one in
 * four - so four rolls in a played match cannot tell you whether it is fixed.
 * _physSolve is a pure function of its arguments plus Math.random(), so it can
 * be run hundreds of times with no canvas. This measures what the eye actually
 * objects to: gaps between painted silhouettes, not between centres.
 *
 *   node tools/shoot.js --eval-file tools/shoot_throw_sweep.js --out sweep.png
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
/* the 3D layer boots on demand: give it a match screen to boot for */
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el) => { if (!vis(el)) return false;
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(1900);
const p = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (p) { tap(p); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);
tap(document.getElementById('btnRoll'));
await until(() => (D3X.dice || []).length > 0, 12000);
await until(() => !(D3X.dice || []).some(d => d.roll), 14000);
await sleep(500);

/* the row's real geometry, read off the dice standing in it */
const row = document.getElementById('playerDiceRow');
const chip = row.querySelector('.die');
const sz = chip.getBoundingClientRect().width * D3X.MSCALE;
const mids = [...row.querySelectorAll('.die')].map(d => {
  const w = d.parentElement, b = (w && w.classList.contains('die-wrap')) ? w : d;
  const r = b.getBoundingClientRect(); return r.left + r.width / 2;
}).sort((a, b) => a - b);
const mid = (mids[0] + mids[mids.length - 1]) / 2;
const mrw = D3X.mount ? D3X.mount.getBoundingClientRect().width : innerWidth;
const limitX = Math.max(1.2, (Math.min(mid, mrw - mid) - sz * (D3X.PHYS.drawn / 2)) / sz);
const slots = mids.map(m => (m - mid) / sz);
let pitch = 0;
for (let i = 1; i < slots.length; i++) { const g = slots[i] - slots[i-1];
  if (g > 1e-4 && (!pitch || g < pitch)) pitch = g; }

const geom = { sz: +sz.toFixed(2), mid: Math.round(mid), mrw: Math.round(mrw),
  limitX: +limitX.toFixed(3), pitch: +pitch.toFixed(3),
  slots: slots.map(v => +v.toFixed(3)),
  drawn: D3X.PHYS.drawn, drawnMid: D3X.PHYS.drawnMid,
  slotEase: D3X.PHYS.slotEase, stopV: D3X.PHYS.stopV, stopW: D3X.PHYS.stopW,
  dropY: D3X.PHYS.dropY, MSCALE: D3X.MSCALE, screenW: innerWidth };

/* painted half-extent along the row, from the yaw a die landed on */
const halfExt = (x, q) => {
  const e = new THREE.Euler().setFromQuaternion(
    new THREE.Quaternion(q.qx, q.qy, q.qz, q.qw), 'YXZ').y;
  return D3X._drawnAt(x, limitX) * (Math.abs(Math.cos(e)) + Math.abs(Math.sin(e))) / 2;
};

const N = 200;
let overlapRolls = 0, worstOverlap = 0, offEdge = 0, capped = 0;
let sumFrames = 0, maxFrames = 0, penTotal = 0, sumMinGap = 0;
const hist = {};
for (let t = 0; t < N; t++) {
  const sol = D3X._physSolve(slots, [1,2,3,4,5,6], [], limitX, pitch);
  const last = sol.frames[sol.frames.length - 1];
  sumFrames += sol.frames.length; if (sol.frames.length > maxFrames) maxFrames = sol.frames.length;
  if (sol.frames.length >= D3X.PHYS.cap) capped++;
  const boxes = last.map(f => { const h = halfExt(f.x, f);
    return { lo: f.x - h, hi: f.x + h }; }).sort((a, b) => a.lo - b.lo);
  let worst = Infinity, bad = 0;
  for (let i = 1; i < boxes.length; i++) { const g = boxes[i].lo - boxes[i-1].hi;
    if (g < worst) worst = g; if (g < 0) bad++; }
  sumMinGap += worst;
  if (bad) { overlapRolls++; if (-worst > worstOverlap) worstOverlap = -worst; }
  hist[bad] = (hist[bad] || 0) + 1;
  if (boxes[0].lo < -limitX - 0.02 || boxes[boxes.length-1].hi > limitX + 0.02) offEdge++;
  penTotal += last.reduce((a, f, i) => a + 0, 0);
}
return { geom, trials: N,
  overlapRollsPct: Math.round(100 * overlapRolls / N) + '%',
  worstOverlapPainted: +worstOverlap.toFixed(3),
  worstOverlapPx: Math.round(worstOverlap * sz),
  avgMinPaintedGap: +(sumMinGap / N).toFixed(3),
  avgMinPaintedGapPx: Math.round((sumMinGap / N) * sz),
  offEdgeRolls: offEdge, cappedRolls: capped,
  avgFrames: Math.round(sumFrames / N), maxFrames,
  overlappingPairsHistogram: hist };
