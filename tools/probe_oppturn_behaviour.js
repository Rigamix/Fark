/* BEHAVIOURAL DIFF: the real rival turn, measured the way the model now is.
 *
 * Three hypotheses about WHY the sim diverges were read out of the code and
 * all three were wrong, because grepping a name across two independently
 * written implementations can only tell you whether that word appears - the
 * real game calls hot dice `_oLastHotDice`/`_oppSweep`, the model expresses
 * the identical logic with zero shared tokens. So this stops reading code and
 * measures output on both sides instead.
 *
 * FOUR COMPARABLE QUANTITIES, chosen because each side already tracks them:
 *   rolls per turn        real: oppRollNum          model: out.rolls
 *   dice committed / turn real: G._oTurnDiceCommitted model: out.kept
 *   bust rate per turn    real: oPts delta === 0     model: out.busted
 *   points per turn       real: oPts delta           model: banked
 *
 * Committed-per-turn is the load-bearing one: a turn cannot commit more than
 * six dice without the row refreshing, so committed/6 is a direct read on how
 * often hot dice chained - without depending on either side's name for it.
 *
 * THE TARGET IS THE SHAPE, NOT THE SIZE. The model/real points ratio per night
 * is 1.15 / 0.84 / 1.71 / 1.13 / 0.88 / 0.82 / 0.47 / 0.76 - it OVERSTATES at
 * three nights and UNDERSTATES at five. Any explanation must account for the
 * direction flip. One uniform mechanism cannot produce it, so a candidate that
 * would only shift the average is disqualified before it is tested.
 *
 * Standing lesson kept: never relaunch over a live turn (finOpp clears the
 * active flag then hits a ghost-timer guard before G.oTurns++, so an orphaned
 * turn really ran but never registered), and check _oppTurnActive BEFORE
 * calling, never after.
 */
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async (fn, ms) => { const t0 = Date.now();
    while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
    return false; };

  if (typeof S === 'undefined' || typeof launchBossMatch !== 'function')
    return { error: 'game globals missing' };
  try { S.settings = S.settings || {}; S.settings.fastRival = true; } catch (e) {}

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
  const PRATE = [292, 591, 533, 541, 679, 368, 536, 594];
  const MATCHES = 4, TURNS = 12;
  const rows = [];

  for (let tier = 0; tier < 8; tier++) {
    const pts = [], rolls = [], committed = [];
    let busts = 0, done = 0, stalled = 0;
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
      await sleep(320);
      for (let i = 0; i < TURNS; i++) {
        if (G._oppTurnActive) break;
        const t0 = (G.oTurns || 0), p0 = (G.oPts || 0);
        try { runOppTurn(); } catch (e) { break; }
        if (!(await until(() => G && (G.oTurns || 0) > t0, 20000))) { stalled++; break; }
        done++;
        const gained = (G.oPts || 0) - p0;
        pts.push(gained);
        if (gained <= 0) busts++;
        if (typeof oppRollNum === 'number') rolls.push(oppRollNum);
        if (typeof G._oTurnDiceCommitted === 'number') committed.push(G._oTurnDiceCommitted);
        try {
          G.pPts = (G.pPts || 0) + PRATE[tier];
          if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
        } catch (e) { break; }
        await sleep(100);
      }
    }
    const avg = a => a.length ? +(a.reduce((p, c) => p + c, 0) / a.length).toFixed(2) : null;
    rows.push({ night: tier + 1, boss: (RUNGS[tier] && RUNGS[tier].name) || '?',
                turns: done, stalled: stalled,
                ptsPerTurn: pts.length ? Math.round(avg(pts)) : null,
                rollsPerTurn: avg(rolls),
                committedPerTurn: avg(committed),
                bustRate: done ? +(busts / done).toFixed(2) : null,
                hotChainsPerTurn: committed.length ? +(avg(committed) / 6).toFixed(2) : null });
  }
  window.__oppBehaviour = rows;
  return rows;
