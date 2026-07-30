/* THE RIVAL'S THROW, measured the same way the player's was.
 *
 * Denis: "NPC rolls aren't following the physics guidelines we've established
 * with lanes, etc... Dice bunch up and are chaotic."
 *
 * Records, for every solve on EITHER row: which row it was for, the lanes aimed
 * at, and the pitch. Then measures the RENDERED positions of the rival's dice -
 * gaps and overlaps in real pixels - because the aimed lane and the painted
 * result are different claims and only the second one is what Denis sees.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
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

/* log every solve, tagged with the row it was for */
const solves = [];
const origSolve = D3X._physSolve.bind(D3X);
D3X._physSolve = function (slotX, values, obstacles, limitX, rowPitch) {
  let key = null, n = 0;
  try {
    const withHx = (D3X.dice || []).filter(d => d.match && d.hx !== undefined);
    const keys = {};
    withHx.forEach(d => { const k = D3X._rowKey(d); keys[k] = (keys[k] || 0) + 1; });
    key = Object.keys(keys).sort((a, b) => keys[b] - keys[a])[0] || null;
    n = document.querySelectorAll('#oppDiceRow .die').length;
  } catch (e) {}
  /* what the solve was scaled by. sz = first thrown die's painted width * MSCALE,
     and every lane is (seat - (N-1)/2) * pitch * sz on screen - so two rows that
     agree on pitch can still land at different spacings if sz differs. */
  let szP = null, szO = null;
  try { const e = document.querySelector('#playerDiceRow .die'); if (e) szP = +e.getBoundingClientRect().width.toFixed(2); } catch (e) {}
  try { const e = document.querySelector('#oppDiceRow .die'); if (e) szO = +e.getBoundingClientRect().width.toFixed(2); } catch (e) {}
  let mid = null, mrw = null;
  try { mid = +D3X._rowMid(key).toFixed(1); } catch (e) {}
  try { mrw = +D3X.mount.getBoundingClientRect().width.toFixed(1); } catch (e) {}
  solves.push({ phase: (typeof G !== 'undefined' && G) ? G.phase : null,
    guessedRow: key, oppRowDice: n, limitX: +(+limitX).toFixed(3),
    dieWpl: szP, dieWopp: szO, rowMid: mid, mountW: mrw, MSCALE: D3X.MSCALE,
    aimedAt: slotX.map(v => +v.toFixed(3)), pitch: +(+rowPitch).toFixed(3), n: values.length });
  return origSolve(slotX, values, obstacles, limitX, rowPitch);
};

/* is the rival's row even going through the 3D layer? */
const tracked = (rowId) => (D3X.dice || []).filter(d => {
  try { return d.match && d.chip && d.chip.closest && d.chip.closest('#' + rowId); } catch (e) { return false; }
}).length;

/* measure painted spread of a row: real gaps between neighbouring dice */
const spread = (rowId) => {
  const els = [...document.querySelectorAll('#' + rowId + ' .die')].filter(vis);
  const boxes = els.map(e => { const r = e.getBoundingClientRect(); return { l: r.left, r: r.right, w: r.width, c: r.left + r.width / 2 }; })
    .sort((a, b) => a.c - b.c);
  const gaps = [];
  for (let i = 1; i < boxes.length; i++) gaps.push(+(boxes[i].l - boxes[i - 1].r).toFixed(1));
  return { count: boxes.length,
    widths: boxes.map(b => +b.w.toFixed(1)),
    centres: boxes.map(b => Math.round(b.c)),
    gaps,
    overlaps: gaps.filter(g => g < 0).length,
    minGap: gaps.length ? Math.min(...gaps) : null,
    span: boxes.length ? [Math.round(boxes[0].l), Math.round(boxes[boxes.length - 1].r)] : null };
};

/* ── our turn: throw once so the player row is measured, then hand over ── */
tap(document.getElementById('btnRoll'));
await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
await sleep(700);
const playerSpread = spread('playerDiceRow');
const playerTracked = tracked('playerDiceRow');

/* hand the table over: bank if we can, otherwise keep rolling until we bust.
   Either way the rival gets its turn - which is the only thing being measured. */
for (let g = 0; g < 10 && G.phase !== 'opp'; g++) {
  const free = G.pool.filter(d => !d.committed);
  const k = free.find(d => d.val === 1 || d.val === 5);
  if (k) { tap(k.el); await sleep(350); }
  const bankBtn = document.getElementById('btnBank');
  if (k && vis(bankBtn) && !bankBtn.classList.contains('disabled')) { tap(bankBtn); break; }
  const rb = document.getElementById('btnRoll');
  if (!rb || rb.classList.contains('disabled') || !vis(rb)) break;
  tap(rb);
  await until(() => G.phase === 'choosing' || G.phase === 'idle' || G.phase === 'opp', 14000);
  await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
  await sleep(500);
}

/* ── the rival's turn: sample the row repeatedly while it plays ── */
await until(() => G && G.phase === 'opp', 40000);
const samples = [];
for (let s = 0; s < 26; s++) {
  await sleep(600);
  const sp = spread('oppDiceRow');
  if (sp.count) samples.push({ t: s * 600, tracked3d: tracked('oppDiceRow'), ...sp });
  if (G.phase !== 'opp') break;
}

const worst = samples.filter(s => s.gaps.length).sort((a, b) => a.minGap - b.minGap)[0] || null;
const oppSolves = solves.filter(s => s.phase === 'opp');
return {
  playerRow: { tracked3d: playerTracked, ...playerSpread },
  oppSamples: samples.length,
  oppWorstMoment: worst,
  oppEverTracked3d: samples.some(s => s.tracked3d > 0),
  oppMaxTracked3d: samples.length ? Math.max(...samples.map(s => s.tracked3d)) : 0,
  oppAnyOverlap: samples.some(s => s.overlaps > 0),
  solveCount: solves.length,
  solvesDuringOppTurn: oppSolves.length,
  oppSolveDetail: oppSolves.slice(0, 6),
  playerSolveDetail: solves.filter(s => s.phase !== 'opp').slice(0, 3),
};
