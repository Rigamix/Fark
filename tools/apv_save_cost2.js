/* SAVE COST, SECOND INSTRUMENT CHECK (audit-only)
 * SUITE: exclude
 * The first run benched 50 IDENTICAL writes; Chromium may no-op an unchanged
 * setItem. This one forces a different payload every iteration, mutates S/G
 * between save() / saveMatchState() calls, and adds a 100KB slope probe.
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
await until(() => G && (G.phase === 'idle' || G.phase === 'choosing'), 20000);
/* one roll so we bench in a genuine mid-turn state */
handleRoll();
await until(() => G && G.phase === 'choosing', 14000);
out.phase = G.phase;

function bench(fn, n) {
  const t = [];
  for (let i = 0; i < n; i++) { const a = performance.now(); fn(i); t.push(performance.now() - a); }
  t.sort((x, y) => x - y);
  const avg = t.reduce((a, b) => a + b, 0) / t.length;
  return { avg: +avg.toFixed(3), p95: +t[Math.floor(t.length * 0.95)].toFixed(3), max: +t[t.length - 1].toFixed(3) };
}
const js = JSON.stringify(S);
out.kbS = +(js.length / 1024).toFixed(1);
out.kbPM = (S && S.pendingMatch) ? +(JSON.stringify(S.pendingMatch).length / 1024).toFixed(2) : null;

/* unique payload every write — no identical-value shortcut possible */
out.tSetItemUnique = bench(i => { localStorage.setItem('__fk_probe', js + '#' + i); }, 50);
/* mutate S between saves so the stored string genuinely changes */
out.tSaveMutating = bench(i => { S.run._probeTick = i; save(); }, 50);
/* mutate G between full snapshots */
if (G && !G._endMatchFired) out.tSaveMatchStateMutating = bench(i => { G.turnPts = i; saveMatchState(); }, 50);
out.tSnapDiceOnlyMutating = bench(i => { G.numDice = 6; _snapDiceOnly(); }, 50);
/* slope: a 100KB payload, unique each time */
const big = js + 'x'.repeat(100 * 1024);
out.tSetItem100KB = bench(i => { localStorage.setItem('__fk_probe', big + i); }, 50);
localStorage.removeItem('__fk_probe');
delete S.run._probeTick; G.turnPts = 0; save();
return out;
