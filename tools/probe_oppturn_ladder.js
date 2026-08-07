/* THE REAL RIVAL, ALL EIGHT NIGHTS.
 *
 * probe_oppturn_real.js settled the question at ALDRIC: the sim's model says
 * the rival banks 688/turn, the real engine banks 1041. This sweeps the same
 * measurement across the whole ladder, because one tier cannot tell you
 * whether the model is uniformly low or wrong in a shape.
 *
 * WHY NOT JUST FIX THE MODEL: measured, not assumed. Stripping comments and
 * counting decision-carrying identifiers, the real runOppTurn has 131 against
 * F.oppTurn's 5, and 53,502 chars of code against 3,207 - and the real one's
 * decision identifiers outnumber its presentation identifiers 131 to 72, so
 * this is not an animation wrapper. The model is missing most of the rival's
 * decision-making (hot dice, diceStop, the release-singles-to-chase-combos
 * subsystem). Porting that rule by rule is a rewrite, not a calibration.
 * Measuring the real per-turn distribution and letting the fast sim sample
 * from it is the cheap path to a trustworthy ladder.
 *
 * INSTRUMENT LESSONS ALREADY PAID FOR, all three kept here:
 *  1. Do not hook finOpp by assigning window.finOpp - if it is a lexical
 *     binding the assignment creates a new global the game never calls, and
 *     the probe reports silence while the engine works fine. Read G.oTurns /
 *     G.oPts, which the engine itself moves.
 *  2. Check _oppTurnActive BEFORE calling, never after. runOppTurn early-
 *     returns while it is set, so waiting for it afterwards counts a stalled
 *     turn's stuck flag as a fresh start.
 *  3. Never relaunch a match over a live turn. finOpp clears the flag and THEN
 *     hits `if(G!==_matchG||...)return`, which sits before G.oTurns++, so an
 *     orphaned turn really ran but never registered - and looks like a stall.
 *
 * Usage: node tools/shoot.js --url <dev>/fark_proto.html \
 *          --eval-file tools/probe_oppturn_ladder.js --wait 1500 --out shot.png
 */
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async (fn, ms) => { const t0 = Date.now();
    while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
    return false; };

  /* measured modal loadout per night; past night 5 the modal share collapses
     to 1-2% so it is only a representative pick, not a typical one. It reaches
     the rival ONLY through oppShouldBank's playerTotal-vs-oppTotal clamps. */
  const LOADOUTS = [
    ['bone','bone','bone','bone','bone','bone'],
    ['silver','bone','bone','bone','bone','bone'],
    ['silver','jade','bone','bone','bone','bone'],
    ['silver','jade','jade','bone','bone','bone'],
    ['silver','jade','jade','jade','bone','bone'],
    ['silver','jade','jade','starstone','jade2','bone'],
    ['amber','jade','jade','jade2','starstone','jade2'],
    ['amber','jade','jade','jade2','starstone','jade2']
  ];
  /* the sim's own player pts/turn per tier, from the real player engine - used
     only to advance G.pPts so the rival sees a realistic gap */
  const PRATE = [292, 591, 533, 541, 679, 368, 536, 594];
  const MODEL = [640, 824, 377, 893, 792, 688, 1122, 1391];  // what F.oppTurn claims
  const MATCHES = 5, TURNS = 12;

  if (typeof S === 'undefined' || typeof launchBossMatch !== 'function')
    return { error: 'game globals missing - probe never reached the game' };
  try { S.settings = S.settings || {}; S.settings.fastRival = true; } catch (e) {}

  const rows = [];
  for (let tier = 0; tier < 8; tier++) {
    const pts = [];
    const diag = { launched: 0, done: 0, stalled: 0, stuck: 0 };
    for (let m = 0; m < MATCHES; m++) {
      await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
      await sleep(180);
      try {
        _getS();
        S.run = S.run || {};
        S.run.tier = tier;
        S.run.dice = LOADOUTS[tier].slice();
        S.run.cards = S.run.cards || [];
        launchBossMatch();
      } catch (e) { break; }
      if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
      diag.launched++;
      await sleep(350);
      for (let i = 0; i < TURNS; i++) {
        if (G._oppTurnActive) { diag.stuck++; break; }
        const t0 = (G.oTurns || 0), p0 = (G.oPts || 0);
        try { runOppTurn(); } catch (e) { break; }
        if (!(await until(() => G && (G.oTurns || 0) > t0, 20000))) { diag.stalled++; break; }
        diag.done++;
        pts.push((G.oPts || 0) - p0);
        try {
          G.pPts = (G.pPts || 0) + PRATE[tier];
          if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
        } catch (e) { break; }
        await sleep(100);
      }
    }
    const srt = pts.slice().sort((a, b) => a - b);
    const mean = pts.length ? Math.round(pts.reduce((p, c) => p + c, 0) / pts.length) : null;
    rows.push({ night: tier + 1, boss: (RUNGS[tier] && RUNGS[tier].name) || '?',
                model: MODEL[tier], real: mean,
                ratio: (mean != null && MODEL[tier]) ? +(mean / MODEL[tier]).toFixed(2) : null,
                n: pts.length, median: srt.length ? srt[Math.floor(srt.length / 2)] : null,
                busts: pts.filter(x => x <= 0).length, max: srt.length ? srt[srt.length - 1] : null,
                target: RUNGS[tier] && RUNGS[tier].target, diag: diag });
  }
  window.__oppLadder = rows;
  return rows;
