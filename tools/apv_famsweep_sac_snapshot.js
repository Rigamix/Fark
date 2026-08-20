/* NOTE (P816, 2026-08-20): sacrifice now pays G._turnBonusPot, not
 * G.pPts - pointsPaid reads 0 here by design; the verdict gates are
 * the snapshot fields, unchanged. */
/* SACRIFICE vs THE MID-MATCH SNAPSHOT.  SUITE: exclude.
 *
 * _removeDieAt closes with a mid-turn re-snapshot (19232-19244) - matchDice,
 * _enchArr, numDice, _fairTrade, _diceOut - written precisely because "a quit
 * between a Break and the next turn resumed from one that still held six
 * dice, and the destroyed die walked straight back into the same match".
 * CFX.sacrifice does its own splice and never re-snapshots. This reads
 * S.pendingMatch after a live sacrifice. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el) => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

const out = {};
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(1900);
const patron = [...document.querySelectorAll('.ptcard')].filter(vis)[0];
if (patron) { tap(patron); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 20000);
out.ready = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 25000);
const ms = document.getElementById('screen-match'); if (ms) ms.classList.remove('has-splash');
['turn-ov','hot-ov'].forEach(id => { const e = document.getElementById(id); if (e) e.classList.remove('flash'); });
await sleep(400);

_getS();
G._enchArr = [null, null, null, null, null, { t: 'ward', face: 5 }];
G.numDice = G.matchDice.length;
const sacInst = { id: 'sacrifice', tier: 1, charges: 1, state: {} };
G.pF = [sacInst];

let dealt = false;
const w = setInterval(() => { const p = G.pool || [];
  if (p.length >= 6) { p.forEach(d => { d.val = 3; }); p[0].val = 1;
    p.forEach(d => { try { reDrawDieFace(d); } catch (e) {} }); dealt = true; } }, 20);
tap(document.getElementById('btnRoll'));
if (!await until(() => dealt, 3000)) { try { handleRoll(); } catch (e) {} await until(() => dealt, 9000); }
clearInterval(w);
await until(() => G.phase === 'choosing', 12000);

const pm = () => S.pendingMatch ? {
  matchDice: (S.pendingMatch.matchDice || []).slice(),
  enchArr: (S.pendingMatch._enchArr || []).map(e => e ? e.t : null),
  numDice: S.pendingMatch.numDice,
  diceOut: (S.pendingMatch._diceOut || []).length,
} : null;
out.snapshotExists = !!S.pendingMatch;
out.beforeSac = { live: { matchDice: G.matchDice.slice(), numDice: G.numDice,
                          enchArr: G._enchArr.map(e => e ? e.t : null) }, snap: pm() };
out.pPtsBefore = G.pPts;
out.sacUsed = CFX.sacrifice.use(sacInst);
out.pPtsAfter = G.pPts;
out.afterSac = { live: { matchDice: G.matchDice.slice(), numDice: G.numDice,
                         enchArr: G._enchArr.map(e => e ? e.t : null),
                         diceOut: (G._diceOut || []).length }, snap: pm() };

out.verdict = {
  livePaidALane: out.afterSac.live.matchDice.length < out.beforeSac.live.matchDice.length,
  pointsPaid: out.pPtsAfter - out.pPtsBefore,
  snapshotStillHoldsSixDice: !!(out.afterSac.snap && out.afterSac.snap.matchDice.length
                                === out.beforeSac.live.matchDice.length),
  snapshotNumDice: out.afterSac.snap ? out.afterSac.snap.numDice : null,
  snapshotMissedTheDiceOutRecord: !!(out.afterSac.snap && out.afterSac.snap.diceOut === 0
                                     && out.afterSac.live.diceOut > 0),
};
return out;
