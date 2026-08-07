/* IS THE HARNESS'S OPPONENT MODEL FAITHFUL?
 *
 * tools/sim_harness.js drives the REAL game for the player (F.simTurn calls
 * startPTurn/rollPool/afterRollLite/handleBank) but reimplements the opponent
 * (F.oppTurn has its own roll loop; its own comment says "the SIM has its own
 * copy of the rival's scoring"). So every boss win rate measured through the
 * sim compares the real player against a MODEL of the rival, and the whole
 * measured gap is per-turn scoring:
 *
 *     ALDRIC   model says the rival banks 688/turn, the player 368
 *
 * This probe pulls the same number out of the REAL engine and prints both, so
 * the model can be checked instead of trusted.
 *
 * HOW, and why this way: finOpp(pts) is the game's own end-of-rival-turn hook
 * and receives exactly what the turn banked (0 on a bust). Wrapping it means
 * no state is guessed and no scoring is reimplemented here - which would just
 * be a third copy, and a third copy could not settle an argument between the
 * first two.
 *
 * TWO STATISTICS, deliberately:
 *   openers  - the FIRST rival turn of a fresh match, repeated. Carries no
 *              assumption at all: both totals are 0, exactly as the match
 *              starts. This is the honest number.
 *   running  - turns as the match actually proceeds, with the player's score
 *              advanced at the sim's own player rate so oppShouldBank sees a
 *              realistic gap (it clamps agg on playerTotal vs oppTotal). This
 *              is the closer like-for-like, but it INHERITS the sim's player
 *              rate as an input, so it is reported separately and never alone.
 *
 * Usage: node tools/shoot.js --url <dev>/fark_proto.html \
 *          --eval-file tools/probe_oppturn_real.js --wait 240000 --out shot.png
 * Reads window.__oppReal.
 */
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async (fn, ms) => { const t0 = Date.now();
    while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
    return false; };

  const TIER = 5;                    // ALDRIC, night 6
  const MODAL = ['bone','jade','jade','jade2','silver','starstone'];  // measured modal night-6 loadout
  const PLAYER_RATE = 368;           // the sim's own player pts/turn at this tier
  const TARGET_TURNS = 40;
  const MATCHES = 9;
  const out = { tier: TIER, loadout: MODAL, modelSaysOpp: 688, modelSaysPlayer: PLAYER_RATE,
                openers: [], running: [], rolls: [], matches: 0, notes: [] };

  if (typeof S === 'undefined' || typeof launchBossMatch !== 'function') {
    return { error: 'game globals missing - probe never reached the game' };
  }

  /* fast rival: pacing only. _oppDelay floors at 40ms and multiplies, it does
     not change a single scoring or banking decision. */
  try { S.settings = S.settings || {}; S.settings.fastRival = true; } catch (e) {}

  /* NO HOOK. The first cut wrapped finOpp via `window.finOpp = ...` and got 13
     launched matches with zero completed turns - and that null was
     uninterpretable, because it has two very different causes: the turn never
     ran, or the hook never fired. If finOpp is a lexical binding inside the
     game's closure, assigning window.finOpp creates a NEW global the game
     never calls, and the probe reports silence while the engine works fine.
     So observe state the engine certainly updates instead: finOpp itself does
     G.oTurns++ and the banked points land in G.oPts. */
  const wrap = () => {};
  const diag = { sawActive: 0, sawTurnTick: 0, stuckBefore: 0, stalled: 0, stalledStillActive: 0, phases: [] };

  async function freshMatch() {
    try {
      _getS();
      S.run = S.run || {};
      S.run.tier = TIER;
      S.run.dice = MODAL.slice();
      S.run.cards = S.run.cards || [];
      launchBossMatch();
    } catch (e) { out.notes.push('launch threw: ' + e.message); return false; }
    const ok = await until(() => (typeof G !== 'undefined') && G && G.rung && G.matchOppDice, 9000);
    if (ok) { out.matches++; wrap(); }
    return ok;
  }

  /* one real rival turn, measured off engine state rather than a hook.
     A completed turn is G.oTurns ticking up (finOpp does that on bank AND on
     bust); the points are the G.oPts delta, which is 0 on a bust. */
  async function oneTurn() {
    const t0 = (G.oTurns || 0), p0 = (G.oPts || 0);
    if (diag.phases.length < 6) diag.phases.push(String(G.phase));
    /* runOppTurn early-returns while _oppTurnActive is set. So a PRE-call
       check is the only honest one: my first diagnostic waited for the flag
       AFTER calling and counted 13 "starts" that were really one stalled turn
       leaving the flag stuck - the flag was a proxy for "a turn began" and it
       is not that property. If it is already set, the call did nothing. */
    if (G._oppTurnActive) { diag.stuckBefore++; return null; }
    try { runOppTurn(); } catch (e) { out.notes.push('runOppTurn threw: ' + e.message); return null; }
    diag.sawActive++;
    const done = await until(() => G && (G.oTurns || 0) > t0, 20000);
    if (!done) { diag.stalled++; diag.stalledStillActive += (G._oppTurnActive ? 1 : 0); return null; }
    diag.sawTurnTick++;
    return { pts: (G.oPts || 0) - p0, rolls: (typeof oppRollNum === 'number') ? oppRollNum : null };
  }

  /* ONE MATCH, CONSECUTIVE TURNS - relaunching per turn was the bug, not the
     engine. finOpp clears _oppTurnActive and THEN hits a ghost-timer guard,
     `if(G!==_matchG||!G||G._endMatchFired)return`, which sits BEFORE the
     G.oTurns++. Relaunching swaps G, so an in-flight turn belonging to the old
     G returns at the guard: the turn really happened, banked nothing visible,
     and looked to the probe like a stall. Diagnosed off stalled=4 with
     stalledStillActive=0 - the turns had ended, the counter just never moved.

     So the rival's score is left to accumulate naturally and the player's is
     advanced at the sim's own rate, because oppShouldBank clamps agg on the
     playerTotal-vs-oppTotal gap and a frozen player score would hold it at a
     floor it never sees in a real match. That inherited rate is an input, so
     the first turn of the match is reported separately as the assumption-free
     number. */
  for (let m = 0; m < MATCHES; m++) {
    /* never relaunch over a live turn - that is what orphaned G and produced
       the phantom stalls. Drain first, then swap. */
    await until(() => !G || !G._oppTurnActive, 8000);
    await sleep(200);
    if (!(await freshMatch())) break;
    await sleep(400);
    for (let i = 0; i < TARGET_TURNS; i++) {
      const t = await oneTurn();
      if (!t) { out.notes.push('m' + m + ' stopped at turn ' + i); break; }
      if (i === 0) out.openers.push(t.pts);
      out.running.push(t.pts);
      if (t.rolls != null) out.rolls.push(t.rolls);
      try {
        G.pPts = (G.pPts || 0) + PLAYER_RATE;
        if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
      } catch (e) { break; }
      await sleep(110);
    }
  }

  const stat = a => {
    if (!a.length) return null;
    const s = a.slice().sort((x, y) => x - y);
    return { n: a.length,
             mean: Math.round(a.reduce((p, c) => p + c, 0) / a.length),
             median: s[Math.floor(s.length / 2)],
             busts: a.filter(x => x <= 0).length,
             min: s[0], max: s[s.length - 1] };
  };
  out.diag = diag;
  out.openerStat = stat(out.openers);
  out.runningStat = stat(out.running);
  out.rollsPerTurn = out.rolls.length ? +(out.rolls.reduce((p,c)=>p+c,0)/out.rolls.length).toFixed(2) : null;
  window.__oppReal = out;
  return out;
