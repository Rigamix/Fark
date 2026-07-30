/* WHY DO THE DICE LEAVE THEIR LANES?
 *
 * The P336 slot work was measured through tools/dice_harness.js, which calls
 * _physSolve directly with synthetic arguments. That validated the SOLVER and
 * says nothing about the arguments the game actually hands it. This measures
 * the caller: every roll, in a real match, records what was passed in and where
 * the dice ended up on screen.
 *
 *   node tools/shoot.js --eval-file tools/shoot_lanes.js --out lanes.png
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const trace = [];
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el, why) => { if (!vis(el)) { trace.push('SKIP ' + why); return false; }
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); trace.push('tap ' + why); return true; };

tap(document.getElementById('hsBtnBottom'), 'NEW RUN'); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie'), 'die'); await sleep(1300);
tap(document.getElementById('nrTakeBtn'), 'TAKE IT'); await sleep(1900);
const pt = [...document.querySelectorAll('.ptcard')].filter(vis)[0];
if (pt) { tap(pt, 'patron'); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit, 'SIT DOWN'); if (sit.parentElement) tap(sit.parentElement, 'parent'); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

/* ── record what the caller hands the solver ── */
const solves = [];
const origSolve = D3X._physSolve;
D3X._physSolve = function (slotX, values, obst, limitX, rowPitch) {
  const sol = origSolve.apply(this, arguments);
  let restX = null;
  try {
    const last = sol.frames[sol.frames.length - 1];
    restX = last.map(f => +f.x.toFixed(3));
  } catch (e) {}
  const sorted = slotX.slice().sort((a, b) => a - b);
  const gaps = [];
  for (let i = 1; i < sorted.length; i++) gaps.push(+(sorted[i] - sorted[i - 1]).toFixed(3));
  solves.push({ n: values.length,
    slotX: slotX.map(v => +v.toFixed(3)), slotGaps: gaps,
    rowPitch: +(+rowPitch).toFixed(3), limitX: +(+limitX).toFixed(3),
    obstacles: obst.length,
    proxy: D3X.PHYS.proxy,
    slotR: +(Math.max(0.12, ((rowPitch > 1e-4 ? rowPitch : 0) - D3X.PHYS.proxy) / 2)).toFixed(3),
    restX: restX,
    drift: restX ? restX.map((x, i) => +(x - slotX[i]).toFixed(3)) : null });
  return sol;
};

/* what the caller measured for scale, captured at the same moment */
const scale = [];
const origRoll = D3X.roll ? D3X.roll.bind(D3X) : null;

/* ── on-screen truth, once everything has settled ── */
const seen = () => {
  const row = document.getElementById('playerDiceRow');
  const out = [];
  row.querySelectorAll('.die').forEach(d => {
    const w = d.parentElement;
    const boxEl = (w && w.classList && w.classList.contains('die-wrap')) ? w : d;
    const wr = boxEl.getBoundingClientRect();
    let mesh = null;
    const m = (D3X.dice || []).find(x => x.chip === d);
    if (m && m.obj) mesh = +m.obj.position.x.toFixed(3);
    out.push({ wrapMid: Math.round(wr.left + wr.width / 2), wrapW: Math.round(wr.width),
      cls: d.className.replace(/die ?/, '').slice(0, 34),
      committed: d.classList.contains('committed'), meshX: mesh,
      hx: m ? Math.round(m.hx) : null });
  });
  return out;
};
const drawnBoxes = () => {
  /* where the MESH is actually drawn, in screen px, via the shared canvas */
  const cam = D3X.cam, cv = D3X.rend ? D3X.rend.domElement : null;
  if (!cam || !cv) return null;
  const cr = cv.getBoundingClientRect();
  return (D3X.dice || []).filter(d => d.match && d.obj).map(d => {
    const v = d.obj.position.clone().project(cam);
    return { x: Math.round(cr.left + (v.x + 1) / 2 * cr.width) };
  });
};
const gapReport = () => {
  const s = seen().map(d => d.wrapMid).sort((a, b) => a - b);
  const g = []; for (let i = 1; i < s.length; i++) g.push(s[i] - s[i - 1]);
  return { mids: s, gaps: g, minGap: g.length ? Math.min.apply(null, g) : null };
};

const rounds = [];
const errs = []; window.addEventListener('error', e => errs.push(String(e.message)));

const rollAndSettle = async why => {
  tap(document.getElementById('btnRoll'), 'ROLL ' + why);
  await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
  await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
  await sleep(700);
};

for (let r = 0; r < 4; r++) {
  const before = solves.length;
  await rollAndSettle('#' + (r + 1));
  const gr = gapReport();
  rounds.push({ roll: r + 1, solves: solves.slice(before),
    dice: seen(), gaps: gr, drawn: drawnBoxes(),
    sz: (function () { const d = document.querySelector('#playerDiceRow .die');
      return d ? +(d.getBoundingClientRect().width * D3X.MSCALE).toFixed(2) : null; })(),
    MSCALE: D3X.MSCALE });
  /* keep one scoring die so the next roll is a genuine subset */
  const free = G.pool.filter(d => !d.committed);
  const keep = free.find(d => d.val === 1 || d.val === 5);
  if (!keep) { trace.push('round ' + (r + 1) + ': no lone scorer, stopping'); break; }
  tap(keep.el, 'keep ' + keep.val);
  await sleep(400);
  if (document.getElementById('btnRoll').classList.contains('disabled')) {
    trace.push('round ' + (r + 1) + ': ROLL disabled after keep, stopping'); break;
  }
}

return { trace, errs, rounds };
