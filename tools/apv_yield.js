/* 4b - THE PER-TURN YIELD INSTRUMENT, and the repair to the envelope's premise.
 *
 * WHAT WAS WRONG. P918 withdrew the band envelope because the matches did not
 * run to the turn cap: they ended when the RIVAL reached the target. The
 * premise had been "tier 7's target is out of reach, so every match spends its
 * whole allowance", and only half of that was true - out of reach for the
 * PLAYER. What got measured was "what the player scored before losing", which
 * is not a ceiling and is not comparable between matches of different lengths.
 *
 * AND THE FIX IS ONE NUMBER, because G.target IS SHARED. _handBackOrCap reads
 * `G.pPts<G.target && G.oPts<G.target`; there is no separate rival target to
 * raise. So the target is set out of BOTH sides' reach after the match starts,
 * and the turn cap becomes the only way a match can end. Nothing about the
 * player's scoring depends on the target - the policies bank on turn total and
 * dice left, never on the target - so this changes when the match stops, not
 * how the player plays.
 *
 * ONE KNOWN INFLATION, IN THE SAFE DIRECTION. Starstone's extra turn is gated
 * on `G.pPts<G.target&&G.oPts<G.target`, so an unreachable target grants every
 * one it can. The measured number is therefore an upper bound that is slightly
 * generous - which for a pruning tool is the correct way to be wrong: it
 * strikes off fewer cells than it could, never more. pTurns is reported beside
 * every total so the inflation is visible rather than absorbed.
 *
 * THE INSTRUMENT IS VALIDATED BEFORE IT IS USED, in three ways this file can
 * run separately (#job=):
 *   probe   - do matches now actually end at the cap? Two matches, one cell.
 *   tier    - is the ceiling a property of (band, policy) at all? Same cell at
 *             tier 0 and tier 7. If these differ materially, the ladder's cells
 *             are not the axis the envelope assumes and the design is wrong.
 *   bands   - the envelope itself, one band per invocation (#band=N).
 *   silver  - two silver against two iron, same policy, same band: the gear
 *             price, measured on the same instrument rather than asserted.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const BANDS = {
  1: ['amber', 'bone', 'bone', 'bone', 'iron', 'iron'],
  2: ['amber', 'silver', 'bone', 'bone', 'iron', 'iron'],
  3: ['jade', 'jade2', 'starstone', 'amber', 'bone', 'iron'],
};
/* the gear-price pair: identical but for the two dice under test */
const PAIR = {
  iron:   ['amber', 'bone', 'bone', 'bone', 'iron', 'iron'],
  silver: ['amber', 'bone', 'bone', 'bone', 'silver', 'silver'],
};
const UNREACHABLE = 10000000;

out.caps = {patron: (typeof TURN_CAP_PATRON !== 'undefined') ? TURN_CAP_PATRON : null,
            boss: (typeof TURN_CAP_BOSS !== 'undefined') ? TURN_CAP_BOSS : null};

const night = () => { try { return (S.run && S.run.night) || null; } catch (e) { return null; } };
const nextSeat = () => { const n = night(); if (!n) return -1;
  const p = n.seatsPlayed || [];
  for (let i = 0; i < p.length; i++) if (!p[i]) return i;
  return -1; };
const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };

/* ONE MATCH, run to the cap and nothing else */
async function one(dice, policy, tier) {
  try {
    _getS(); window._fkDiscardOk = true;
    S.run = _freshRun();
    S.run.tier = tier;
    S.run.dice = dice.slice();       /* after _freshRun, which resets them */
    S.run.night = null; _ensureNight();
  } catch (e) { return {err: 'setup: ' + e.message}; }
  const idx = nextSeat();
  if (idx < 0) return {err: 'no seat'};
  window._fkDiscardOk = true;
  try { delete S.pendingMatch; } catch (e) {}
  try { launchSeat(idx); } catch (e) { return {err: 'launchSeat: ' + e.message}; }
  if (await FDRV.until(gLive, 20000) == null) return {err: 'no start'};

  /* THE TARGET GOES OUT OF REACH - AND STAYS THERE. A single write here loses
     a race: gLive (phase idle, pTurns 0) fires BEFORE the match finishes
     installing its rung target, so the first probe run had one match write
     10000000 and end holding 9500, the rung's own number, which would have
     been reported as a ceiling if targetHeld had not caught it. Polling for
     "setup looks done" would only narrow the window. An interval cannot lose
     the race at all: whatever writes the target afterwards is overwritten
     within a frame, and the end-of-match check still has to agree. */
  const targetFromRung = G.target;
  G.target = UNREACHABLE;
  /* AND THE SAME TICK SAMPLES THE POOL. `dealt` was read after playMatch
     returned - with the match over and the pool cleared - so it came back null,
     which is P918's defect verbatim: a loadout check that reads the dice where
     there are none. The interval runs DURING the match, so it sees the pool
     with dice in it, and the first non-empty sample is the loadout that was
     actually dealt rather than the one that was asked for. */
  /* THE BUST COUNT IS MEASURED GAME-SIDE, WITH A POSITIVE CONTROL.
     The driver reported busts:0 across 26 player turns at bank500 - a policy
     that rolls five dice, then four, then three before its diceLeft<=2 rule
     fires, so cumulative farkle risk per turn is well over 25%. Zero is not a
     result, it is a counter that cannot see. The driver can only reach its
     busts++ if the game presents a `choosing` phase with clickable dice on a
     farkle, which is an assumption about the UI, not about the game.
     So doBust is counted where it happens. AND endPTurn is counted beside it
     as the control: every player turn ends there, bank or bust, so its count
     MUST equal pTurns. If it does not, the wrap is not on the path the game
     calls and the bust zero means nothing - which is the only way to tell a
     real zero from a dead hook. */
  let bustsSeen = 0, bustsEaten = 0, endPTurnsSeen = 0;
  const origBust = window.doBust, origEnd = window.endPTurn;
  const wrapsInstalled = typeof origBust === 'function' && typeof origEnd === 'function';
  if (wrapsInstalled) {
    window.doBust = function () {
      bustsSeen++;
      try { if (G && G._bustImmuneTurn) bustsEaten++; } catch (e) {}
      return origBust.apply(this, arguments);
    };
    window.endPTurn = function () {
      endPTurnsSeen++;
      return origEnd.apply(this, arguments);
    };
  }

  let dealtSeen = null;
  const hold = setInterval(function () {
    try { if (G && G.target !== UNREACHABLE) G.target = UNREACHABLE; } catch (e) {}
    try {
      if (dealtSeen == null && G && G.pool && G.pool.length)
        dealtSeen = G.pool.map(function (d) { return d.mat; }).sort().join(',');
    } catch (e) {}
  }, 60);
  const want = dice.slice().sort().join(',');
  let asked = null;
  try { asked = (S.run.dice || []).slice().sort().join(','); } catch (e) {}

  const r = await FDRV.playMatch({policy, timeoutMs: 260000, alreadyStarted: true});
  /* read the target BEFORE releasing the hold, or the check reads its own
     handiwork from after the match rather than during it */
  let targetWhileHeld = null;
  try { targetWhileHeld = G.target; } catch (e) {}
  clearInterval(hold);
  if (wrapsInstalled) { window.doBust = origBust; window.endPTurn = origEnd; }
  if (r && r.err) return {err: r.err};
  const targetAtEnd = targetWhileHeld;
  const dealt = dealtSeen;
  const cap = r.turnCap || out.caps.patron;
  return {
    pPts: r.pPts, oPts: r.oPts, pTurns: r.pTurns, turnCap: cap,
    endReason: r.endReason, banks: r.banks, busts: r.busts, stalled: r.stalled,
    /* game-side, and the control that says whether to believe it.
       THIS PROBE'S WRAP IS DELIBERATELY LEFT IN PLACE NOW THAT THE DRIVER HAS
       ITS OWN (P920). The driver wraps on top of this one, so both count and
       both delegate - two independent tallies of the same event, and if they
       disagree one of the two wraps is not seeing every call. */
    wrapsInstalled, bustsSeen, bustsEaten, endPTurnsSeen,
    driverBusts: r.busts, driverBustsInferred: r.bustsInferred,
    driverBustsDerived: r.bustsDerived, driverHookOnPath: r.bustHookOnPath,
    driverCountsAgree: r.bustCountsAgree, driverTurnsAddUp: r.turnsAddUp,
    probeAndDriverAgree: r.busts === bustsSeen,
    wrapIsOnThePath: wrapsInstalled && r.pTurns != null && endPTurnsSeen === r.pTurns,
    /* the driver's count against the game's own - a disagreement is the
       driver's blind spot, measured rather than argued about */
    driverSawEveryBust: r.busts === bustsSeen,
    finalAnswerUsed: r.finalAnswerUsed, extraTurnsLeft: r.extraTurnsLeft,
    targetFromRung, targetAtEnd,
    /* THE THREE THINGS THAT MAKE THIS A CEILING RATHER THAN A SCORE */
    targetHeld: targetAtEnd === UNREACHABLE,
    endedOnTheCap: r.endReason === 'cap',
    spentTheAllowance: r.pTurns != null && cap ? r.pTurns >= cap : false,
    overran: r.pTurns != null && cap ? r.pTurns > cap : null,
    perTurn: (r.pTurns && r.pPts != null) ? Math.round(r.pPts / r.pTurns) : null,
    /* BOTH ENDS OF THE LOADOUT: what was asked for, and what reached the table.
       asked===want catches a setup that did not stick; dealt===want catches a
       game that dealt something else regardless. The second is the one that
       could not be asked before, and it is the one that makes the band label
       mean anything. */
    asked, want, dealt,
    loadoutTook: asked === want,
    loadoutDealt: dealt === want,
  };
}

/* A CELL REFUSES unless every one of its matches is a cap run. A cell that
   returns a refusal is not averaged and does not reach a table - the whole
   failure of the last attempt was reporting over a check that had said no. */
async function cell(dice, policy, tier, n) {
  const rows = [];
  for (let i = 0; i < n; i++) {
    rows.push(await one(dice, policy, tier));
    await FDRV.sleep(300);
  }
  const good = rows.filter(r => r && !r.err && !r.stalled);
  const capRuns = good.filter(r => r.endedOnTheCap && r.spentTheAllowance && r.targetHeld);
  const reasons = [];
  if (!good.length) reasons.push('no match completed');
  if (good.length && capRuns.length < good.length)
    reasons.push('only ' + capRuns.length + ' of ' + good.length +
      ' were cap runs (endReason ' + JSON.stringify(good.map(r => r.endReason)) +
      ', pTurns ' + JSON.stringify(good.map(r => r.pTurns)) +
      ', targetHeld ' + JSON.stringify(good.map(r => r.targetHeld)) + ')');
  if (good.length && !good.every(r => r.loadoutTook))
    reasons.push('the loadout did not take: asked ' +
      JSON.stringify(good.map(r => r.asked)) + ' wanted ' + (good[0] || {}).want);
  if (good.length && !good.every(r => r.loadoutDealt))
    reasons.push('the table was dealt something else: dealt ' +
      JSON.stringify(good.map(r => r.dealt)) + ' wanted ' + (good[0] || {}).want);
  const totals = capRuns.map(r => r.pPts);
  const yields = capRuns.map(r => r.perTurn);
  const mean = a => a.length ? Math.round(a.reduce((x, y) => x + y, 0) / a.length) : null;
  return {
    rows, matches: good.length, capRuns: capRuns.length,
    refusal: reasons.length ? reasons.join('; ') : null,
    totals, pTurns: capRuns.map(r => r.pTurns),
    endReasons: good.map(r => r.endReason),
    overran: capRuns.filter(r => r.overran).length,
    finalAnswerUsed: capRuns.filter(r => r.finalAnswerUsed).length,
    perTurn: yields, meanPerTurn: mean(yields), meanTotal: mean(totals),
    /* the bust picture, game-side */
    bustsSeen: good.map(r => r.bustsSeen), bustsEaten: good.map(r => r.bustsEaten),
    driverBusts: good.map(r => r.busts),
    endPTurnsVsPTurns: good.map(r => r.endPTurnsSeen + '/' + r.pTurns),
    bustRate: (function () {
      const b = good.reduce((a, r) => a + (r.bustsSeen || 0), 0);
      const t = good.reduce((a, r) => a + (r.pTurns || 0), 0);
      return t ? Math.round(b / t * 100) + '% of ' + t + ' turns' : null;
    })(),
    /* THE CEILING IS A MAX OF n AND THAT IS A BIASED ESTIMATOR - it can only
       rise as n grows, so cells are only comparable at equal n, and the true
       ceiling is above this one by an unknown amount. Band 1 / bank500 came
       back 3500 and 7500 on two matches, a 2.1x spread, which is why the
       spread is reported rather than a max standing alone: a pruning rule that
       strikes a cell whose target merely exceeds this number would strike
       reachable cells. Strike on a MARGIN over it, not on it. */
    ceiling: totals.length ? Math.max.apply(null, totals) : null,
    spread: totals.length ? (Math.max.apply(null, totals) - Math.min.apply(null, totals)) : null,
    dealt: (good[0] || {}).dealt || null,
  };
}

const H = location.hash || '';
const JOB = ((H.match(/job=(\w+)/) || [])[1] || 'probe');
const BAND = parseInt((H.match(/band=(\d)/) || [])[1] || '1', 10);
const N = parseInt((H.match(/n=(\d+)/) || [])[1] || '0', 10);
out.job = JOB; out.band = BAND;

if (JOB === 'probe') {
  /* DOES THE OVERRIDE WORK AT ALL. Two matches, one cell - the cheapest thing
     that can tell me whether the rest of this file is worth six hours. */
  out.cells = {probe: await cell(BANDS[BAND], 'bank500', 7, N || 2)};
} else if (JOB === 'tier') {
  /* IS THE CEILING A PROPERTY OF (band, policy)? If tier moves it, the
     envelope cannot prune per-tier cells from one measurement and the design
     is wrong - which is worth knowing before, not after. */
  out.cells = {
    't0': await cell(BANDS[BAND], 'bank500', 0, N || 3),
    't7': await cell(BANDS[BAND], 'bank500', 7, N || 3),
  };
} else if (JOB === 'bands') {
  out.cells = {};
  for (const policy of ['bank300', 'bank500', 'hot'])
    out.cells['b' + BAND + '/' + policy] = await cell(BANDS[BAND], policy, 7, N || 4);
} else if (JOB === 'silver') {
  /* THE GEAR PRICE. Identical loadouts but for the two dice under test, same
     policy, same tier, on the instrument that was just validated. */
  out.cells = {
    iron:   await cell(PAIR.iron, 'bank500', 7, N || 4),
    silver: await cell(PAIR.silver, 'bank500', 7, N || 4),
  };
  const a = out.cells.iron, b = out.cells.silver;
  out.price = (a.refusal || b.refusal) ? null : {
    ironPerTurn: a.meanPerTurn, silverPerTurn: b.meanPerTurn,
    deltaPerTurn: (b.meanPerTurn != null && a.meanPerTurn != null)
      ? b.meanPerTurn - a.meanPerTurn : null,
    pctPerTurn: (b.meanPerTurn && a.meanPerTurn)
      ? Math.round((b.meanPerTurn / a.meanPerTurn - 1) * 100) : null,
    /* AND THE SPREAD, because a difference smaller than the run-to-run spread
       is not a price, it is noise with a sign. */
    ironSpread: a.perTurn, silverSpread: b.perTurn,
  };
} else {
  out.err = 'unknown job ' + JOB;
}

const keys = Object.keys(out.cells || {});
out.VERDICT = {
  everyCellRan: keys.length > 0 && keys.every(k => out.cells[k].matches >= 2),
  /* THE INSTRUMENT'S OWN CLAIM: every reported match spent its allowance and
     ended on the cap with the target still out of reach */
  noCellRefused: keys.every(k => !out.cells[k].refusal),
  everyCellIsCapRuns: keys.every(k => out.cells[k].capRuns === out.cells[k].matches),
  /* the loadout reached the table, not merely the config */
  everyLoadoutWasDealt: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err).every(r => r.loadoutDealt === true)),
  /* THE CONTROL, NOT THE FINDING. This says the bust hook is on the path the
     game actually calls; it says nothing about how many busts there were. A
     bust count is only readable when this is true. */
  theBustHookIsOnThePath: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err).every(r => r.wrapIsOnThePath === true)),
  /* P920's identity: a player turn ends in exactly one of a bank or a bust */
  theTurnsAddUp: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err).every(r => r.driverTurnsAddUp === true)),
  /* and the two independent wraps see the same events */
  theTwoWrapsAgree: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err).every(r => r.probeAndDriverAgree === true)),
  /* the soft cap should be visible somewhere - it fires in every match where
     the player trails, and with the rival unable to win it often will */
  theSoftCapIsVisible: keys.some(k =>
    out.cells[k].overran > 0 || out.cells[k].finalAnswerUsed > 0),
};
if (JOB === 'tier') {
  const a = out.cells.t0, b = out.cells.t7;
  out.tierInvariance = (a.refusal || b.refusal) ? null : {
    t0PerTurn: a.meanPerTurn, t7PerTurn: b.meanPerTurn,
    t0Spread: a.perTurn, t7Spread: b.perTurn,
    pctApart: (a.meanPerTurn && b.meanPerTurn)
      ? Math.round(Math.abs(b.meanPerTurn / a.meanPerTurn - 1) * 100) : null,
  };
}
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
