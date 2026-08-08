/* WHY DOES THE MODEL BUST MORE? Two possibilities, and this separates them.
 *
 * Confirmed target, deeply sampled: the model busts 1.9-3.8x more than the real
 * rival at CORVUS, BRUTUS and WHISPER. FINNICK matches on both sides and is the
 * control. Already eliminated: boss targets, agg, minBank, rival dice, player
 * thresh, the model's bank<3000 cap, banking-decision timing and state, keep-
 * chooser output, release-singles (ported faithfully, moved nothing) and
 * bust-save cards (zero fires on either side).
 *
 * A bust is a roll that scores nothing. Given the same dice and the same
 * materials, bust probability is fixed by HOW MANY DICE ARE ROLLED. So the
 * remaining space splits cleanly in two:
 *
 *   1. SAME bust rate per roll at matched dice count
 *      -> the roll and the scorer agree; the divergence is in the
 *         DISTRIBUTION of dice counts, i.e. the model rolls from worse
 *         positions (fewer dice in hand) more often
 *   2. DIFFERENT bust rate per roll at matched dice count
 *      -> the divergence is inside the roll itself: materials reaching the
 *         scorer differently, or the scorer being fed something different
 *
 * INTERPRETATION REGISTERED BEFORE THE RUN, so a clean result cannot be
 * re-read afterwards to fit whatever landed. Case 1 sends the hunt to "when
 * does each side choose to roll again"; case 2 sends it to the dice pipeline.
 *
 * INSTRUMENT: wrap _scoreRollBest, which BOTH sides call, so the two cannot
 * differ by instrumentation. Per call it records the dice count, the materials
 * and whether the result scored zero. That is the bust event at its source,
 * rather than inferred from a turn's point delta.
 *
 * SELF-CHECK: a wrap that fails to take reports zero calls, which reads exactly
 * like "this side never rolls". Both sides' call counts are reported and a zero
 * on either means the instrument failed, not that the mechanism is absent.
 *
 * FINNICK LIVE AS CONTROL. Its bust rates already match, so its per-roll curves
 * must match too. If CORVUS and FINNICK diverge the same way, whatever this
 * finds is not the cause of the bust gap.
 */
const TIERS = [3, 2];
const NAMES = {3: 'CORVUS (treatment)', 2: 'FINNICK (control)'};
const SIM_N = 60, REAL_MATCHES = 6, REAL_TURNS = 10;
const LOADOUT = {3: ['silver','jade','jade','bone','bone','bone'],
                 2: ['silver','jade','bone','bone','bone','bone']};
const PRATE = {3: 541, 2: 533};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof _scoreRollBest !== 'function') return { error: '_scoreRollBest not reachable' };

let tag = null;
const rolls = {};                     // tag -> diceCount -> [total, busts]
const mats = {};                      // tag -> material -> count
const _realScore = _scoreRollBest;
window._scoreRollBest = function (vals, cards, bank, ctx, ms) {
  const out = _realScore.apply(this, arguments);
  if (tag) {
    const n = (vals && vals.length) || 0;
    rolls[tag] = rolls[tag] || {};
    rolls[tag][n] = rolls[tag][n] || [0, 0];
    rolls[tag][n][0]++;
    if (!out || !out.total || out.total <= 0) rolls[tag][n][1]++;
    if (ms && ms.length) { mats[tag] = mats[tag] || {};
      ms.forEach(function (m) { mats[tag][m] = (mats[tag][m] || 0) + 1; }); }
  }
  return out;
};

const out = { tiers: [] };
for (const t of TIERS) {
  /* ---- MODEL ---- */
  tag = 'model:' + t;
  for (let i = 0; i < SIM_N; i++) {
    FSIM.installRng(20260813 + i);
    const gear = { key:'g', dice: LOADOUT[t].slice(),
                   ench:[null,null,null,null,null,null], badge:null, fcards:[] };
    try { FSIM.simMatch(FSIM.POLICIES.carl, { tier:t, boss:true, gear:gear }); } catch(e) {}
  }

  /* ---- REAL ---- */
  tag = null;
  let rTurns = 0;
  for (let m = 0; m < REAL_MATCHES; m++) {
    await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
    await sleep(150);
    try {
      _getS();
      S.run = S.run || {};
      S.run.tier = t;
      S.run.dice = LOADOUT[t].slice();
      S.run.cards = S.run.cards || [];
      S.settings = S.settings || {}; S.settings.fastRival = true; S.settings.reducedMotion = true;
      launchBossMatch();
    } catch (e) { break; }
    if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
    await sleep(280);
    for (let i = 0; i < REAL_TURNS; i++) {
      if (G._oppTurnActive) break;
      const t0 = (G.oTurns || 0);
      tag = 'real:' + t;
      try { runOppTurn(); } catch (e) { tag = null; break; }
      const ok = await until(() => G && (G.oTurns || 0) > t0, 20000);
      tag = null;
      if (!ok) break;
      rTurns++;
      try {
        G.pPts = (G.pPts || 0) + PRATE[t];
        if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
      } catch (e) { break; }
      await sleep(80);
    }
  }

  const pack = k => {
    const r = rolls[k] || {}, keys = Object.keys(r).sort((a, b) => a - b);
    let tot = 0, bu = 0;
    const per = {};
    keys.forEach(n => { tot += r[n][0]; bu += r[n][1];
      per[n] = { rolls: r[n][0], busts: r[n][1],
                 rate: r[n][0] ? +(r[n][1] / r[n][0]).toFixed(3) : null }; });
    return { totalRolls: tot, totalBusts: bu,
             overall: tot ? +(bu / tot).toFixed(4) : null, byDiceCount: per,
             materials: mats[k] || {} };
  };
  out.tiers.push({ tier: t, boss: NAMES[t], realTurns: rTurns,
                   model: pack('model:' + t), real: pack('real:' + t) });
}

window._scoreRollBest = _realScore;
return out;
