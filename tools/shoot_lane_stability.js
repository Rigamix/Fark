/* THE INVARIANT: a die's lane is the lane it started in, for the whole match,
 * and a kept die's lane is never handed to a thrown die.
 *
 * Records the lane every die is AIMED at on every throw, keyed by the die's own
 * element, so a lane that moves between rolls is visible as a changed number.
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

/* every lane aimed at, per throw. If lanes are an index ladder, every value
   across the whole match must come from ONE ladder - that is the invariant. */
const laneLog = [];
const origSolve = D3X._physSolve.bind(D3X);
D3X._physSolve = function (slotX, values, obst, limitX, rowPitch) {
  laneLog.push({ aimedAt: slotX.map(v => +v.toFixed(3)),
    pitch: +(+rowPitch).toFixed(3), obstacles: obst.length, n: values.length });
  return origSolve(slotX, values, obst, limitX, rowPitch);
};
/* stamp every die with a stable identity so lanes can be compared across rolls */
let seq = 0;
const stamp = () => document.querySelectorAll('#playerDiceRow .die').forEach(d => {
  if (!d.dataset.laneId) d.dataset.laneId = 'd' + (seq++); });

const rowState = () => [...document.querySelectorAll('#playerDiceRow .die')].map(d => ({
  id: d.dataset.laneId, kept: d.classList.contains('kept-still'),
  mid: Math.round(d.getBoundingClientRect().left + d.getBoundingClientRect().width / 2) }));

const rolls = [];
for (let k = 0; k < 4; k++) {
  stamp();
  tap(document.getElementById('btnRoll'));
  await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
  await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
  await sleep(800);
  stamp();
  rolls.push({ roll: k + 1, row: rowState(), lastAim: laneLog[laneLog.length - 1] || null });
  const free = G.pool.filter(d => !d.committed);
  const keep = free.find(d => d.val === 1 || d.val === 5);
  if (!keep) break;
  tap(keep.el); await sleep(400);
  if (document.getElementById('btnRoll').classList.contains('disabled')) break;
}
/* every aimed lane, across every throw, must sit on one ladder */
const all = [];
laneLog.forEach(L => L.aimedAt.forEach(v => all.push(v)));
const uniq = [...new Set(all)].sort((a, b) => a - b);
const pitches = laneLog.map(L => L.pitch);
/* a ladder means consecutive distinct lanes differ by a constant */
const steps = [];
for (let i = 1; i < uniq.length; i++) steps.push(+(uniq[i] - uniq[i-1]).toFixed(3));
return { rolls, throwCount: laneLog.length,
  distinctLanesUsed: uniq,
  gapsBetweenThem: steps,
  pitchPerThrow: pitches,
  pitchStable: new Set(pitches).size === 1,
  onOneLadder: steps.length ? steps.every(g => Math.abs(g - steps[0]) < 0.01) : true };
