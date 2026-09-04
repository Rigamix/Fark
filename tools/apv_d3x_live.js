/* IS THE 3D LAYER ACTUALLY RUNNING UNDER THE HARNESS?
 *
 * THE QUESTION, AND WHY IT IS ONE LINE OF ANSWER. _afterOppSettle polls
 * _rowSettled under a flat CAP=4200 that no multiplier scales. But _rowSettled's
 * early-outs - no D3X, not ready, D3X.fail, physics off, no dice, no row - ALL
 * RETURN TRUE, i.e. "settled". So the CAP is only reachable when the 3D layer is
 * genuinely running. If it runs headless at ~1fps, roughly twenty rival rolls a
 * match clip at 4.2s each and that is most of a boss match. If it does not run,
 * the settle wait costs nothing and the wall clock is real work.
 *
 * MEASURED, NOT INFERRED FROM THE FLAGS. Reading D3X.ready and PHYS.on says what
 * the layer thinks it is doing; what decides the cost is whether _rowSettled
 * ever returns FALSE, and for how long. So this samples the predicate itself
 * across real rival turns and times each settle, then reports both.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

out.flags = {
  d3xDefined: typeof D3X !== 'undefined' && !!D3X,
  ready: (typeof D3X !== 'undefined' && D3X) ? !!D3X.ready : null,
  fail: (typeof D3X !== 'undefined' && D3X) ? !!D3X.fail : null,
  physOn: (typeof D3X !== 'undefined' && D3X && D3X.PHYS) ? !!D3X.PHYS.on : null,
  diceCount: (typeof D3X !== 'undefined' && D3X && D3X.dice) ? D3X.dice.length : null,
  rowSettledExists: typeof _rowSettled === 'function',
};
/* the early-out verdict: if any of these is falsy, _rowSettled returns true
   unconditionally and the CAP is unreachable */
out.capIsReachable = !!(out.flags.d3xDefined && out.flags.ready && !out.flags.fail &&
                        out.flags.physOn && out.flags.diceCount);

/* ── sample the predicate across real rival turns ─────────────────── */
const samples = [];
const t0 = Date.now();
let unsettledRuns = 0, inRun = false, runStart = 0;
const iv = setInterval(() => {
  try {
    const s = _rowSettled('#oppDiceRow');
    const p = (typeof G !== 'undefined' && G) ? G.phase : null;
    if (!s && !inRun) { inRun = true; runStart = Date.now(); }
    if (s && inRun) {
      inRun = false; unsettledRuns++;
      samples.push({ms: Date.now() - runStart, phase: p});
    }
  } catch (e) {}
}, 50);

/* play a match so rival turns actually happen */
const free = () => G.pool.filter(d => !d.committed && d.el);
const tap = el => { if (el) el.click(); };
const deadline = Date.now() + 150000;
let rolls = 0;
while (typeof G !== 'undefined' && G && !G._endMatchFired && Date.now() < deadline) {
  try {
    if (G.phase === 'idle' && !G._oppTurnActive) { tap(document.getElementById('btnRoll')); rolls++; }
    await FXH.until(() => G._endMatchFired || (G.phase === 'choosing' &&
      (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 9000);
    if (G._endMatchFired) break;
    const fr = free();
    if (!fr.length) { await new Promise(r => setTimeout(r, 250)); continue; }
    let r = null;
    try { r = scoreRoll(fr.map(d => d.val), [], 0, {}, fr.map(d => d.mat)); } catch (e) {}
    if (!r || !r.total) { await FXH.until(() => G.phase === 'idle' || G._endMatchFired, 9000); continue; }
    for (let i = 0; i < fr.length; i++) if (r.used && r.used[i] && !fr[i].sel) tap(fr[i].el);
    await new Promise(res => setTimeout(res, 120));
    tap(document.getElementById('btnBank'));
    await new Promise(res => setTimeout(res, 250));
  } catch (e) { break; }
}
clearInterval(iv);

const ms = samples.map(s => s.ms);
const sum = ms.reduce((a, b) => a + b, 0);
out.settle = {
  elapsedMs: Date.now() - t0,
  playerRolls: rolls,
  unsettledEpisodes: samples.length,
  totalUnsettledMs: sum,
  longestMs: ms.length ? Math.max.apply(null, ms) : 0,
  meanMs: ms.length ? Math.round(sum / ms.length) : 0,
  atOrOverTheCap: ms.filter(x => x >= 4100).length,
  fractionOfWallClock: (Date.now() - t0) ? +(sum / (Date.now() - t0)).toFixed(3) : null,
  firstFew: ms.slice(0, 8),
};

out.VERDICT = {
  theProbeRan: rolls > 0,
  /* THE ANSWER: is the settle wait costing anything at all? */
  theCapIsReachable: out.capIsReachable,
  theRowWasEverUnsettled: samples.length > 0,
  /* and if it is reachable, is it big enough to be worth disabling 3D? */
  itCostsRealTime: sum > 5000,
  anySettleHitTheCap: out.settle.atOrOverTheCap > 0,
};
out.CONCLUSION = out.capIsReachable
  ? (sum > 5000
      ? 'the 3D layer runs and the settle wait costs ' + Math.round(sum / 1000) +
        's of ' + Math.round((Date.now() - t0) / 1000) + 's - disabling it headless is the saving'
      : 'the 3D layer runs but the settle wait is cheap - no saving here')
  : 'the 3D layer is NOT running under the harness, so _rowSettled always ' +
    'returns true and the CAP is unreachable - there is no saving here, the ' +
    'wall clock is real work';
return out;
