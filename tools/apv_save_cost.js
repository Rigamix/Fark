/* SAVE/RESUME COST MEASUREMENT (audit-only, writes nothing to the repo)
 * SUITE: exclude
 *
 * Measures, in a live boss match:
 *  a) JSON.stringify(S) and stringify(S.pendingMatch) sizes (KB), early + late
 *  b) wall-clock ms of saveMatchState(), save(), _snapDiceOnly(), a raw
 *     localStorage.setItem of the full payload, and JSON.stringify alone,
 *     each averaged over 50 calls, at two different match states
 *  c) actions in a scripted player turn (rolls, die taps, bank)
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(80); } return false; };
const vis = el => { if (!el || !el.isConnected) return false; const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = { bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 };
  el.dispatchEvent(new PointerEvent('pointerdown', o)); el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }

const out = {};
_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.matchDice, 14000)) return { err: 'no match' };
out.snapAppeared = await until(() => S && S.pendingMatch, 15000);
await sleep(600);

function bench(fn, n) {
  const t = [];
  for (let i = 0; i < n; i++) { const a = performance.now(); fn(); t.push(performance.now() - a); }
  t.sort((x, y) => x - y);
  const avg = t.reduce((a, b) => a + b, 0) / t.length;
  return { avg: +avg.toFixed(3), p95: +t[Math.floor(t.length * 0.95)].toFixed(3), max: +t[t.length - 1].toFixed(3) };
}
function measure(tag) {
  const m = {};
  const js = JSON.stringify(S);
  m.kbS = +(js.length / 1024).toFixed(1);
  m.kbPM = (S && S.pendingMatch) ? +(JSON.stringify(S.pendingMatch).length / 1024).toFixed(2) : null;
  m.tStringifyS = bench(() => JSON.stringify(S), 50);
  m.tSetItemRaw = bench(() => { localStorage.setItem('__fk_probe', js); }, 50);
  localStorage.removeItem('__fk_probe');
  m.tSave = bench(() => save(), 50);
  if (G && !G._endMatchFired) m.tSaveMatchState = bench(() => saveMatchState(), 50);
  m.tSnapDiceOnly = bench(() => _snapDiceOnly(), 50);
  out[tag] = m;
}
measure('early');

/* ── scripted player turn, counting user actions ── */
const actions = { rolls: 0, dieTaps: 0, banks: 0 };
async function doRoll() { actions.rolls++; handleRoll();
  return await until(() => G && (G.phase === 'choosing' || G.phase === 'opp' || G.phase === 'idle' || G._endMatchFired), 14000); }
function pickKeepers() { let n = 0;
  (G.pool || []).forEach(q => { if (!q.committed && !q.sel && (q.val === 1 || q.val === 5)) { toggleDie(q); actions.dieTaps++; n++; } });
  return n; }

let rollsTried = 0, turnDone = false;
await until(() => G && (G.phase === 'idle' || G.phase === 'choosing'), 12000);
while (!turnDone && rollsTried < 4) {
  const ok = await doRoll(); rollsTried++;
  if (!ok || !G || G._endMatchFired) { turnDone = true; break; }
  if (G.phase !== 'choosing') { turnDone = true; break; } /* bust ended the turn */
  await sleep(500);
  const k = pickKeepers();
  if (k === 0) { turnDone = true; break; }
  await sleep(400);
  if (rollsTried >= 2) {
    actions.banks++; handleBank();
    turnDone = await until(() => G && (G.phase === 'opp' || G.phase === 'idle' || G._endMatchFired), 9000);
  }
}
out.actions = actions;
out.actionsTotal = actions.rolls + actions.dieTaps + actions.banks;
out.turnPtsAtEnd = G ? G.turnPts : null;
out.phaseAfter = G ? G.phase : null;
out.turnNum = G ? G.turnNum : null;

/* let the rival turn play a moment so 'late' is a different, richer state */
await sleep(4000);
_getS();
measure('late');
return out;
