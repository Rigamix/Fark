/* THE INVARIANT, ACROSS A TURN BOUNDARY: the six lanes are a fixture of the
 * MATCH, not of a turn. Banking tears the row down and builds it again, the
 * rival throws into the same table in between, and the lanes on the other side
 * must be the lanes from before.
 *
 * shoot_lane_stability.js proves the grid holds across throws WITHIN a turn.
 * This is the route that one does not cover, and the row rebuild is exactly
 * where a re-derived grid would come back different.
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

/* tag every aimed lane with the turn it was aimed in. There is no G.turn -
   a player turn BEGINS at startPTurn(), so that is the signal. */
const laneLog = [];
let turnTag = 1;
const origStart = startPTurn;
startPTurn = function () { turnTag++; return origStart.apply(this, arguments); };
const origSolve = D3X._physSolve.bind(D3X);
D3X._physSolve = function (slotX, values, obst, limitX, rowPitch) {
  laneLog.push({ turn: turnTag, aimedAt: slotX.map(v => +v.toFixed(3)),
    pitch: +(+rowPitch).toFixed(3), n: values.length });
  return origSolve(slotX, values, obst, limitX, rowPitch);
};

const throwOnce = async () => {
  tap(document.getElementById('btnRoll'));
  await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
  await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
  await sleep(700);
};
const keepOne = () => {
  const free = G.pool.filter(d => !d.committed);
  const k = free.find(d => d.val === 1 || d.val === 5);
  if (!k) return false; tap(k.el); return true;
};

/* ── TURN 1: throw, keep what we can, then BANK. A bust is just as good for
      this test - either way the turn ends and the row is rebuilt. ── */
await throwOnce();
if (keepOne()) { await sleep(400); await throwOnce(); }
const bank = document.getElementById('btnBank');
let banked = false;
if (vis(bank) && !bank.classList.contains('disabled')) { tap(bank); banked = true; }

/* ── the rival's turn, then back to ours ── */
await sleep(1200);
const backToUs = await until(() => turnTag >= 2 && G && G.phase === 'idle'
  && !(D3X.dice || []).some(d => d.roll), 60000);

/* ── TURN 2: the row has been torn down and rebuilt in between ── */
let secondTurnThrew = false;
if (backToUs) {
  await sleep(600);
  await throwOnce();
  secondTurnThrew = true;
  if (keepOne()) { await sleep(400); await throwOnce(); }
}

const t1 = laneLog.filter(L => L.turn === 1), t2 = laneLog.filter(L => L.turn >= 2);
const lanesOf = a => [...new Set(a.flatMap(L => L.aimedAt))].sort((x, y) => x - y);
const L1 = lanesOf(t1), L2 = lanesOf(t2), ALL = lanesOf(laneLog);
const steps = []; for (let i = 1; i < ALL.length; i++) steps.push(+(ALL[i] - ALL[i-1]).toFixed(3));
const pitches = [...new Set(laneLog.map(L => L.pitch))];
/* every turn-2 lane must be one the match already had */
const strayLanes = L2.filter(v => !L1.some(w => Math.abs(w - v) < 0.01));

return { banked, backToUs, secondTurnThrew,
  throwsTurn1: t1.length, throwsTurn2: t2.length,
  lanesTurn1: L1, lanesTurn2: L2,
  pitchesSeen: pitches, pitchStableAcrossTurns: pitches.length === 1,
  strayLanesInTurn2: strayLanes,
  gapsAcrossWholeMatch: steps,
  onOneLadder: steps.length ? steps.every(g => Math.abs(g - steps[0]) < 0.01) : true };
