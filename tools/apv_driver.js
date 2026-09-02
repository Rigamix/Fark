/* Does the driver play the game?
 *
 * THE GATE IS THE POINT. A driver that scores a fifth of the target produces a
 * ladder number that is precise, confident and about a different quantity, and
 * the last run spent an hour proving it. So the first thing checked is that the
 * driver's own sanity gate would have REFUSED that run - fed the observed
 * numbers (3550 against a boss target) it must say no.
 *
 * THEN THREE REAL MATCHES, one per policy, so all three thresholds are
 * exercised rather than one being assumed to stand for the others. Each reports
 * the player's total against its own target, which is the diagnostic that was
 * visible in row one of the broken run and that nobody read.
 *
 * AND THE RULES ARE CHECKED AGAINST THE MODEL, not against my memory of it: the
 * extracted policy keys must be exactly the three _runBalanceSim declares, and
 * the extracted bank rule must reproduce its three clauses on cases chosen to
 * separate them.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

/* ── 1. the rules came from the model ──────────────────────────────── */
out.extract = {
  failed: FDRV.extractWhy || null,
  keys: (FDRV.POLICIES || []).map(p => p.key),
  policies: FDRV.POLICIES,
};
if (FDRV.extractWhy) return Object.assign(out, {err: 'extraction: ' + FDRV.extractWhy});

/* the three clauses of playerTurn's bankFn, separated:
     diceLeft<=2 && turn>=100 | turn>=thresh && diceLeft<=4 | turn>=thresh*2 */
const p500 = FDRV.policyByKey('bank500');
out.bankRule = {
  lowDiceLowScore: FDRV.bankRule(p500, 100, 2),      /* clause 1 -> true  */
  lowDiceBelowFloor: FDRV.bankRule(p500, 90, 2),     /*            false */
  threshWithFourLeft: FDRV.bankRule(p500, 500, 4),   /* clause 2 -> true  */
  threshWithFiveLeft: FDRV.bankRule(p500, 500, 5),   /*            false */
  doubleThreshAnyDice: FDRV.bankRule(p500, 1000, 6), /* clause 3 -> true  */
  belowEverything: FDRV.bankRule(p500, 200, 6),      /*            false */
};

/* ── 2. the gate, against the run that wasted an hour ───────────────
   Its OWN numbers: tier 0 scored 3400 against a 3800 target, tier 6 scored
   3550 against 12500. The per-match floor this replaces would have PASSED the
   tier-0 match at 89% - which is why the gate had to become a pair test. */
const brokenLow = {ok: true, stalled: null, pPts: 3400, oPts: 3800, target: 3800,
                   banks: 6, winnerOverTarget: 1.0, pOverTarget: 0.895};
const brokenHigh = {ok: true, stalled: null, pPts: 3550, oPts: 12500, target: 12500,
                    banks: 6, winnerOverTarget: 1.0, pOverTarget: 0.284};
out.gateOnBrokenRun = FDRV.sanityScale(brokenLow, brokenHigh);
out.perMatchWouldHavePassedTheLowOne = FDRV.sanity(brokenLow);
const healthyLow = {ok: true, stalled: null, pPts: 3600, oPts: 3900, target: 3800,
                    banks: 7, winnerOverTarget: 1.03, pOverTarget: 0.947};
const healthyHigh = {ok: true, stalled: null, pPts: 11800, oPts: 12600,
                     target: 12500, banks: 14, winnerOverTarget: 1.01,
                     pOverTarget: 0.944};
out.gateOnHealthyRun = FDRV.sanityScale(healthyLow, healthyHigh);

/* ── 3. three real matches, one per policy ─────────────────────────── */
out.matches = [];
for (const key of out.extract.keys) {
  const res = await FDRV.playMatch({policy: key, tier: 2, seat: 'boss',
                                    timeoutMs: 200000});
  out.matches.push(Object.assign({key}, res));
  if (res && !res.err) out.matches[out.matches.length - 1].gate = FDRV.sanity(res);
  await FDRV.sleep(600);
}
/* ── 3b. and the pair the gate actually needs, played ───────────── */
const lowM = await FDRV.playMatch({policy: 'bank500', tier: 0, seat: 'boss',
                                   timeoutMs: 200000});
await FDRV.sleep(600);
const highM = await FDRV.playMatch({policy: 'bank500', tier: 7, seat: 'boss',
                                    timeoutMs: 240000});
out.livePair = (lowM && !lowM.err && highM && !highM.err)
  ? {low: lowM, high: highM, gate: FDRV.sanityScale(lowM, highM)} : null;

const done = out.matches.filter(x => !x.err && !x.stalled);
out.summary = {
  attempted: out.matches.length, completed: done.length,
  stalled: out.matches.filter(x => x.stalled).length,
  errors: out.matches.filter(x => x.err).map(x => x.err),
  pOverTarget: done.map(x => x.pOverTarget),
  busts: done.map(x => x.busts), banks: done.map(x => x.banks),
  wins: done.filter(x => x.win).length,
};

out.VERDICT = {
  /* 1 */
  theThreePoliciesAreTheModels:
    JSON.stringify(out.extract.keys) === JSON.stringify(['bank300','bank500','hot']),
  hotIsTheOnlyPusher: FDRV.POLICIES.filter(p => p.pushHot).length === 1 &&
                      FDRV.policyByKey('hot').pushHot === true,
  bankRuleClause1: out.bankRule.lowDiceLowScore === true &&
                   out.bankRule.lowDiceBelowFloor === false,
  bankRuleClause2: out.bankRule.threshWithFourLeft === true &&
                   out.bankRule.threshWithFiveLeft === false,
  bankRuleClause3: out.bankRule.doubleThreshAnyDice === true &&
                   out.bankRule.belowEverything === false,
  /* 2 - the gate must refuse the real broken numbers and pass real good ones */
  theGateRefusesTheBrokenRun: out.gateOnBrokenRun.ok === false,
  andSaysWhy: /scale/.test(out.gateOnBrokenRun.why || ''),
  theGatePassesAHealthyRun: out.gateOnHealthyRun.ok === true,
  /* the reason it had to be a pair: the old per-match floor passes the broken
     run's low-tier match, because 3400 of 3800 looks fine on its own */
  aSingleMatchCannotSeeIt: out.perMatchWouldHavePassedTheLowOne.ok === true,
  /* and the real pair, played rather than supposed */
  theScalingGatePassesLive: !!out.livePair && out.livePair.gate.ok === true,
  /* 3 - and the driver actually plays */
  everyMatchCompleted: out.summary.completed === out.summary.attempted,
  nothingStalled: out.summary.stalled === 0,
  everyMatchPassesItsOwnGate: done.length > 0 && done.every(x => x.gate && x.gate.ok),
  theyBankRatherThanBustOut: done.every(x => x.banks > 0),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
