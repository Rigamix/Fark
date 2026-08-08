/* DOES THE REAL RIVAL RESCUE ZERO-SCORING ROLLS, AND THE MODEL NEVER?
 *
 * The previous pass produced two findings and one instrument flaw that turned
 * out to BE the second finding:
 *
 *   1. distribution - the model rolls from 1-2 dice positions the real rival
 *      never enters at CORVUS: 53 rolls, bust .737/.382, 30% of all model
 *      busts from 5% of its rolls
 *   2. conversion   - real per-roll zero rate (.076) times ~2 rolls/turn
 *      predicts ~.15 busts/turn, but the real turn rate is .037. The gap is
 *      rolls that scored zero and were then RESCUED
 *
 * runOppTurn calls _scoreRollBest at seven sites. Site 1 scores the actual
 * roll; _enc (Encore), _res, _qh (Quick Hands), _gb (Grog's Bump) and _st
 * (Stargazer) RE-SCORE that same roll after a rescue; _sw is a fully
 * speculative roll built with rollFace. F.oppTurn has no rescue path at all -
 * a zero ends the turn immediately.
 *
 * PREDICTIONS, registered before running:
 *   1. real CORVUS  - a substantial share of zero-scoring first-calls are
 *                     followed by a NON-ZERO re-score from a different site
 *   2. model CORVUS - zero rescues, structurally: the model breaks out of the
 *                     loop on a zero and never scores again
 *   3. real FINNICK - few or no rescues, because its bust rate already MATCHES
 *                     the model's. If Finnick rescues as often as Corvus, then
 *                     rescues cannot be what separates them and this is dead.
 *
 * Prediction 3 is the one that can kill it, and it is the reason Finnick stays
 * live rather than being dropped now that three tiers are confirmed.
 *
 * METHOD: identify call sites by stack frame (line:col) rather than by
 * guessing from arguments, then walk each turn's call sequence in order. A
 * zero followed by a non-zero from a DIFFERENT site, with no new roll between,
 * is a rescue. Recording the site keys also shows how many distinct sites each
 * side actually uses - the model should show at most two.
 *
 * SELF-CHECK: zero recorded calls on either side means the wrap failed, which
 * reads identically to "never rolls". Both counts are reported.
 */
const TIERS = [3, 2];
const NAMES = {3: 'CORVUS (treatment)', 2: 'FINNICK (control)'};
const SIM_N = 40, REAL_MATCHES = 6, REAL_TURNS = 10;
const LOADOUT = {3: ['silver','jade','jade','bone','bone','bone'],
                 2: ['silver','jade','bone','bone','bone','bone']};
const PRATE = {3: 541, 2: 533};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof _scoreRollBest !== 'function') return { error: '_scoreRollBest not reachable' };

function siteKey() {
  try {
    const st = (new Error()).stack || '';
    const lines = st.split('\n');
    /* frame 0 is Error, 1 is siteKey, 2 is the wrapper, 3 is the caller */
    const f = lines[3] || lines[2] || '';
    const m = f.match(/(\d+):(\d+)\)?\s*$/);
    return m ? (m[1] + ':' + m[2]) : 'unknown';
  } catch (e) { return 'unknown'; }
}

let tag = null, seq = [];
const sites = {}, turnSeqs = {};
const _realScore = _scoreRollBest;
window._scoreRollBest = function (vals, cards, bank, ctx, ms) {
  const out = _realScore.apply(this, arguments);
  if (tag) {
    const k = siteKey();
    sites[tag] = sites[tag] || {};
    sites[tag][k] = (sites[tag][k] || 0) + 1;
    seq.push({ site: k, total: (out && out.total) || 0, n: (vals && vals.length) || 0 });
  }
  return out;
};

function flush(t) {
  if (!seq.length) return;
  (turnSeqs[t] = turnSeqs[t] || []).push(seq);
  seq = [];
}

function analyse(key) {
  const turns = turnSeqs[key] || [];
  let calls = 0, zeros = 0, rescued = 0, unrescuedZeros = 0;
  const distinct = {};
  turns.forEach(function (s) {
    calls += s.length;
    s.forEach(function (c) { distinct[c.site] = 1; });
    for (let i = 0; i < s.length; i++) {
      if (s[i].total > 0) continue;
      zeros++;
      /* a rescue: a later call in the SAME turn, from a different site,
         returning non-zero before any further zero-scoring fresh roll */
      let saved = false;
      for (let j = i + 1; j < s.length; j++) {
        if (s[j].site !== s[i].site && s[j].total > 0) { saved = true; break; }
        if (s[j].site === s[i].site) break;      /* a new roll from the same site */
      }
      if (saved) { rescued++; i = i; } else unrescuedZeros++;
    }
  });
  return { turnsSeen: turns.length, calls: calls, distinctSites: Object.keys(distinct).length,
           zeroScoringCalls: zeros, rescued: rescued, unrescued: unrescuedZeros,
           rescueRate: zeros ? +(rescued / zeros).toFixed(3) : null,
           siteHistogram: sites[key] || {} };
}

const out = { tiers: [] };
for (const t of TIERS) {
  /* ---- MODEL ---- */
  tag = 'model:' + t; seq = [];
  for (let i = 0; i < SIM_N; i++) {
    FSIM.installRng(20260814 + i);
    const gear = { key:'g', dice: LOADOUT[t].slice(),
                   ench:[null,null,null,null,null,null], badge:null, fcards:[] };
    try { FSIM.simMatch(FSIM.POLICIES.carl, { tier:t, boss:true, gear:gear }); } catch(e) {}
    flush('model:' + t);
  }
  tag = null;

  /* ---- REAL ---- */
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
      tag = 'real:' + t; seq = [];
      try { runOppTurn(); } catch (e) { tag = null; break; }
      const ok = await until(() => G && (G.oTurns || 0) > t0, 20000);
      flush('real:' + t);
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

  out.tiers.push({ tier: t, boss: NAMES[t], realTurnsDriven: rTurns,
                   model: analyse('model:' + t), real: analyse('real:' + t) });
}

window._scoreRollBest = _realScore;
return out;
