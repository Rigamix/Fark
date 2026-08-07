/* CHOOSER OUTPUT vs DICE ACTUALLY COMMITTED.
 *
 * PREDICTION, registered before the run:
 *   MODEL  ratio committed/chosen == 1.000 exactly. There is no code between
 *          the choice and the commit - `used` is derived straight from
 *          _vpick.sel, so a gap is structurally impossible.
 *   REAL   ratio < 1.000, because the release-singles subsystem
 *          (_canRelease / _minUsefulReroll) hands low-value 1s and 5s BACK
 *          after the choice to keep dice in play.
 *
 * If the model shows a gap, the hypothesis is dead and so is my reading of
 * its code. If the real side shows no gap, release-singles is not the
 * mechanism and the search moves on. Either way this falsifies cleanly rather
 * than reporting a direction.
 *
 * The model side is MEASURED, not asserted, even though the code says it must
 * be 1.000 - reading code to predict behaviour is exactly what failed three
 * times this session.
 *
 * MEASURED AT TURN GRANULARITY, deliberately: per-roll alignment across the
 * real game's async animation steps is fiddly and would introduce its own
 * bugs. G._oTurnDiceCommitted is reset at the top of every runOppTurn and
 * accumulates that turn's commits, so comparing it against the chooser sel
 * counts recorded during the same turn needs no alignment at all.
 *
 * FINNICK LIVE AS CONTROL. Release predicts its own null there - the rival
 * banks early with ~3.5 dice in hand, so the release path rarely triggers.
 * Expect real ratio at FINNICK to sit much closer to 1.000 than at CORVUS.
 * A mechanism that moves Finnick is disqualified.
 */
const TIERS = [3, 2];
const NAMES = {3: 'CORVUS', 2: 'FINNICK'};
const SIM_N = 40, REAL_MATCHES = 5, REAL_TURNS = 10;
const LOADOUT = {3: ['silver','jade','jade','bone','bone','bone'],
                 2: ['silver','jade','bone','bone','bone','bone']};
const PRATE = {3: 541, 2: 533};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof _oppChooseFrom !== 'function') return { error: '_oppChooseFrom not reachable' };

let chosen = 0, calls = 0, recording = false;
const _realChoose = _oppChooseFrom;
window._oppChooseFrom = function (freeD, total, bank) {
  const out = _realChoose.apply(this, arguments);
  if (recording) { calls++; chosen += (out && out.sel && out.sel.length) || 0; }
  return out;
};

const rows = [];

for (const t of TIERS) {
  /* ---------- MODEL ---------- */
  chosen = 0; calls = 0; recording = true;
  let mCommitted = 0, mTurns = 0;
  for (let i = 0; i < SIM_N; i++) {
    FSIM.installRng(20260807 + i);
    const gear = { key: 'g', dice: LOADOUT[t].slice(),
                   ench: [null,null,null,null,null,null], badge: null, fcards: [] };
    try {
      const r = FSIM.simMatch(FSIM.POLICIES.carl, { tier: t, boss: true, gear: gear });
      mCommitted += r.oKept || 0; mTurns += r.oppTurns || 0;
    } catch (e) {}
  }
  recording = false;
  const mChosen = chosen, mCalls = calls;

  /* ---------- REAL ---------- */
  chosen = 0; calls = 0;
  let rCommitted = 0, rTurns = 0, rChosen = 0, rCalls = 0;
  for (let m = 0; m < REAL_MATCHES; m++) {
    await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
    await sleep(180);
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
    await sleep(320);
    for (let i = 0; i < REAL_TURNS; i++) {
      if (G._oppTurnActive) break;
      const t0 = (G.oTurns || 0);
      chosen = 0; calls = 0; recording = true;
      try { runOppTurn(); } catch (e) { recording = false; break; }
      const ok = await until(() => G && (G.oTurns || 0) > t0, 20000);
      recording = false;
      if (!ok) break;
      rTurns++;
      rChosen += chosen; rCalls += calls;
      rCommitted += (G._oTurnDiceCommitted || 0);
      try {
        G.pPts = (G.pPts || 0) + PRATE[t];
        if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
      } catch (e) { break; }
      await sleep(100);
    }
  }

  rows.push({
    tier: t, boss: NAMES[t],
    model: { turns: mTurns, calls: mCalls, chosen: mChosen, committed: mCommitted,
             ratio: mChosen ? +(mCommitted / mChosen).toFixed(3) : null },
    real:  { turns: rTurns, calls: rCalls, chosen: rChosen, committed: rCommitted,
             ratio: rChosen ? +(rCommitted / rChosen).toFixed(3) : null }
  });
}

window._oppChooseFrom = _realChoose;
return rows;
