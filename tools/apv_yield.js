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
    /* EVERY TURN'S OUTCOME, which is the unit the cap actually counts. A match
       total is a sum of eight or nine of these, so the reach question - "does
       this cell ever make target T" - is answerable by resampling turns rather
       than by fitting a normal to ten match totals and reading its tail. The
       tail is where a normal fit is least trustworthy and these outcomes are
       right-skewed (a bust is a hard zero, a hot streak has no ceiling), so the
       fit understates reach, which for pruning is the direction that strikes
       cells that were reachable.
       A busted turn is a zero, not a missing entry - that is what makes the
       lengths check below meaningful. */
    /* P921: THE ORDERED RECORD. The first version appended busts as zeros at the
       END, which loses position - and position is exactly what separates the two
       exchangeability failures, since heterogeneity by turn makes a pooled
       resample run hot while coupling makes the observed spread run hot, and a
       single ratio cannot tell them apart. turnSeq comes from the driver, one
       entry per completed turn, in order. */
    turnSeq: r.turnSeq || [],
    turnSeqComplete: r.turnSeqComplete === true,
    turnSeqBusts: r.turnSeqBusts,
    /* THE IDENTITY THAT VALIDATES THE PER-TURN RECORD, and it is a different
       pair of sources from P920's: pPts is the game's running score, turnSeq is
       a wrap reading turnPts once per endPTurn. A match total is the sum of its
       turns, so a mismatch means the record is missing or inventing one - which
       resampling would never reveal, it would just answer confidently about the
       wrong distribution. */
    turnSeqSum: (r.turnSeq || []).reduce(function (a, b) { return a + b; }, 0),
    turnSeqSumsToTotal: (r.turnSeq || []).reduce(function (a, b) { return a + b; }, 0) === r.pPts,
    turnOutcomes: (r.bankAmounts || []).concat(
      new Array(Math.max(0, r.busts || 0)).fill(0)),
    turnOutcomesComplete: ((r.bankAmounts || []).length + (r.busts || 0)) === r.pTurns,
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
  /* MARK THE ROWS THAT REACHED THE RESULT. The identity checks below were
     scanning every non-error row, including ones the cap-run filter had already
     thrown away - so a contaminated row that never touched a reported number
     failed the whole run, which conflates "a number I published is wrong" with
     "a row I correctly discarded was broken". Both are worth seeing; only the
     first should fail. */
  good.forEach(r => { r.usedInResult = capRuns.indexOf(r) >= 0; });
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
    /* the turn-level sample, pooled across the cell's matches */
    turns: good.reduce((a, r) => a.concat(r.turnOutcomes || []), []),
    turnsComplete: good.every(r => r.turnOutcomesComplete === true),
    /* the discarded rows, reported rather than silently dropped - two of them in
       the silver run carried impossible arithmetic (banks 3 with pTurns 2; four
       banks and zero points), and both were the same rows the cap-run filter
       had already refused. Two independent filters agreeing on which rows are
       contaminated is worth seeing. */
    discarded: good.filter(r => !r.usedInResult).map(r => ({
      pPts: r.pPts, pTurns: r.pTurns, banks: r.banks, busts: r.busts,
      inferred: r.driverBustsInferred, endReason: r.endReason,
      targetHeld: r.targetHeld, addUp: r.driverTurnsAddUp})),
    /* the ordered records, kept per match rather than flattened - flattening is
       what threw the position away the first time */
    turnSeqs: good.map(r => r.turnSeq),
    turnSeqsComplete: good.every(r => r.turnSeqComplete === true),
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
       is not a price, it is noise with a sign.
       SIZING IS TWO-SAMPLE. Both arms are measured here, so n per arm is
       2(z_a/2 + z_b)^2 * CV^2 / d^2 - the leading 2 and the power term z_b are
       both required. Sizing this as one arm against a known mean halves every
       figure, which is the error the first pass made: it read 13/36/80 per arm
       for 25/15/10% effects when the answer is 26/72/163. This pair is sized
       for a 50% effect (~7 per arm), which is the resolution the decision
       actually needs - silver at 580g has to earn ~5.8x iron to be priced
       right and is measuring about 1x, so the live question is "about iron"
       versus "about 1.5x iron", not a 10% distinction no player can feel. */
    ironSpread: a.perTurn, silverSpread: b.perTurn,
    ironTotals: a.totals, silverTotals: b.totals,
    ironMeanTotal: a.meanTotal, silverMeanTotal: b.meanTotal,
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
    (out.cells[k].rows || []).filter(r => r && !r.err && r.usedInResult)
      .every(r => r.loadoutDealt === true)),
  /* THE CONTROL, NOT THE FINDING. This says the bust hook is on the path the
     game actually calls; it says nothing about how many busts there were. A
     bust count is only readable when this is true. */
  theBustHookIsOnThePath: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err && r.usedInResult)
      .every(r => r.wrapIsOnThePath === true)),
  /* P920's identity: a player turn ends in exactly one of a bank or a bust */
  theTurnsAddUp: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err && r.usedInResult)
      .every(r => r.driverTurnsAddUp === true)),
  /* every turn is accounted for as a bank or a zero, or the resample is drawing
     from a sample with holes in it */
  everyTurnIsRecorded: keys.every(k => out.cells[k].turnsComplete === true),
  /* and recorded IN ORDER, or the stratified baseline cannot be built */
  everyTurnHasAPosition: keys.every(k => out.cells[k].turnSeqsComplete === true),
  theTurnRecordSumsToTheTotal: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err && r.usedInResult)
      .every(r => r.turnSeqSumsToTotal === true)),
  /* and the two independent wraps see the same events */
  theTwoWrapsAgree: keys.every(k =>
    (out.cells[k].rows || []).filter(r => r && !r.err && r.usedInResult)
      .every(r => r.probeAndDriverAgree === true)),
  /* the soft cap should be visible somewhere - it fires in every match where
     the player trails, and with the rival unable to win it often will */
  /* stated, not hidden: how many rows were thrown away, and whether any of
     them carried impossible arithmetic */
  discardedRows: keys.reduce((n, k) => n + (out.cells[k].discarded || []).length, 0),
  aDiscardedRowWasImpossible: keys.some(k =>
    (out.cells[k].discarded || []).some(r => r.addUp === false)),
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
/* discardedRows is a count and aDiscardedRowWasImpossible is information about
   rows that reached nothing, so neither is a pass/fail term */
const INFO = ['discardedRows', 'aDiscardedRowWasImpossible'];
out.PASS = Object.keys(out.VERDICT).filter(k => INFO.indexOf(k) < 0)
  .every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => INFO.indexOf(k) < 0)
  .filter(k => out.VERDICT[k] !== true);
return out;
