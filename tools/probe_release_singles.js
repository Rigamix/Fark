/* WHAT, EXACTLY, IS THE REAL RIVAL RELEASING?
 *
 * Confirmed already: the real rival commits fewer dice than the chooser picks
 * (CORVUS 130/134 = 0.97) while the model is structurally incapable of a gap
 * (1890/1890 = 1.000 exactly, because `used` derives straight from the
 * chooser's selection). FINNICK, the control, read exactly 1.000 on the real
 * side too - the null the release hypothesis predicts there.
 *
 * NOT established: (a) the size of the effect - the Corvus ratio rests on FOUR
 * released dice across 19 turns - and (b) whether the released dice are
 * actually the low-value singles the source describes, rather than some other
 * post-choice adjustment that merely produces a gap.
 *
 * A gap existing is not the same claim as release-singles being the mechanism.
 * This pass separates them, and raises the sample, BEFORE anything is ported.
 *
 * PREDICTION, registered before running:
 *   1. Released dice are overwhelmingly 5s and 1s. The source sorts
 *      _optionalSingles to give up 5s first (50 pts) then 1s (100 pts),
 *      "sacrifice cheapest first".
 *   2. Released dice are NOT 2/3/4/6 in any quantity - those only score inside
 *      triples/straights, which the release path explicitly protects.
 *   3. FINNICK still releases ~nothing, at the larger sample too.
 * If released dice turn out to be a spread across all faces, the mechanism is
 * something else and release-singles is dead regardless of the gap.
 *
 * METHOD: stash the dice objects the chooser returns, then read their .kept
 * flag at TURN END. Object references survive the row being rebuilt, so a
 * stale object still carries the final flag it was left with - which is
 * exactly the value wanted. No async alignment needed.
 *
 * SELF-CHECK: dice whose .kept is neither true nor false are counted as
 * `unknown`. A high unknown count means the flag is not set where assumed and
 * the released/committed split is void - it does not silently become zero.
 */
const TIERS = [3, 2];
const NAMES = {3: 'CORVUS', 2: 'FINNICK'};
const MATCHES = 10, TURNS = 10;
const LOADOUT = {3: ['silver','jade','jade','bone','bone','bone'],
                 2: ['silver','jade','bone','bone','bone','bone']};
const PRATE = {3: 541, 2: 533};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof _oppChooseFrom !== 'function') return { error: '_oppChooseFrom not reachable' };

let recording = false, stash = [];
const _realChoose = _oppChooseFrom;
window._oppChooseFrom = function (freeD, total, bank) {
  const out = _realChoose.apply(this, arguments);
  if (recording && out && out.sel && out.sel.length) {
    out.sel.forEach(function (d) { stash.push({ d: d, val: d && d.val, mat: d && d.mat }); });
  }
  return out;
};

const rows = [];

for (const t of TIERS) {
  const relHist = {}, keepHist = {}, relMat = {};
  let chosen = 0, released = 0, committed = 0, unknown = 0, turns = 0;

  for (let m = 0; m < MATCHES; m++) {
    await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
    await sleep(160);
    try {
      _getS();
      S.run = S.run || {};
      S.run.tier = t;
      S.run.dice = LOADOUT[t].slice();
      S.run.cards = S.run.cards || [];
      S.settings = S.settings || {}; S.settings.fastRival = true;
      launchBossMatch();
    } catch (e) { break; }
    if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
    await sleep(300);

    for (let i = 0; i < TURNS; i++) {
      if (G._oppTurnActive) break;
      const t0 = (G.oTurns || 0);
      stash = []; recording = true;
      try { runOppTurn(); } catch (e) { recording = false; break; }
      const ok = await until(() => G && (G.oTurns || 0) > t0, 20000);
      recording = false;
      if (!ok) break;
      turns++;

      stash.forEach(function (s) {
        chosen++;
        const k = s.d ? s.d.kept : undefined;
        /* STRICT three-way split. An earlier draft of this line read
           `k === false || k === undefined && s.d`, which by precedence is
           `k === false || (k === undefined && s.d)` - i.e. a die whose flag was
           NEVER SET counted as released. That is exactly the case `unknown`
           exists to expose, so the self-check would have been defeated by the
           line it was checking, and the release count inflated by dice the flag
           never reached. Only an explicit false is a release. */
        if (k === true) { committed++; keepHist[s.val] = (keepHist[s.val] || 0) + 1; }
        else if (k === false) {
          released++; relHist[s.val] = (relHist[s.val] || 0) + 1;
          relMat[s.mat] = (relMat[s.mat] || 0) + 1;
        } else unknown++;
      });

      try {
        G.pPts = (G.pPts || 0) + PRATE[t];
        if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
      } catch (e) { break; }
      await sleep(90);
    }
  }

  const pct = h => { const tot = Object.values(h).reduce((p, c) => p + c, 0);
    return tot ? Object.keys(h).sort().map(k => k + ':' + Math.round(100 * h[k] / tot) + '%').join(' ') : '-'; };
  rows.push({ tier: t, boss: NAMES[t], turns: turns,
              chosen: chosen, committed: committed, released: released, unknown: unknown,
              releaseRate: chosen ? +(released / chosen).toFixed(3) : null,
              releasedPerTurn: turns ? +(released / turns).toFixed(2) : null,
              releasedFaces: pct(relHist), releasedFacesRaw: relHist,
              releasedMats: relMat, committedFaces: pct(keepHist) });
}

window._oppChooseFrom = _realChoose;
return rows;
