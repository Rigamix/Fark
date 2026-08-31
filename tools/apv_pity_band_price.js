/* P892 - the pity denominator, band 0's removal, and Silver's price.
 *
 * THE PITY TEST NEEDS RUNS TO DIE, or it proves nothing. When every run
 * survives to night 3, reachedN3 == RUNS and the old and new denominators are
 * the same number - a cell where the fix is invisible by construction. So the
 * win rates are set to kill a real fraction before night 3, and the check is
 * that the reported figure is now strictly larger than what the old formula
 * would have said on the same data. The old value is recovered arithmetically
 * from the reported pair rather than by re-running a shimmed build, so both
 * numbers come from one population.
 *
 * The all-zero cell is the one that matters most: it is where the metric used
 * to read 0% and look like a measurement. It should still read 0%, but with
 * pityBase 0 beside it, which is the difference between "no run failed to buy"
 * and "no run got far enough to be asked".
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const RUNS = 4000;
const run = (pwin, bwin) => {
  const cfg = {runs: RUNS};
  if (pwin) cfg.pwin = pwin;
  if (bwin) cfg.bwin = bwin;
  return _runEconomySim(cfg);
};

/* ══ 1. PITY - a cell where a real fraction dies before night 3 ═════ */
const mid = run({1: 0.45, 2: 0.50, 3: 0.55}, {1: 0.35, 2: 0.40, 3: 0.45});
const noBuy = Math.round(mid.pityNoBuyByN3 * mid.pityBase / 100);
out.pity = {
  reported: mid.pityNoBuyByN3,
  base: mid.pityBase,
  runs: mid.runs,
  reconstructedNoBuyCount: noBuy,
  oldFormulaWouldSay: Math.round(100 * noBuy / mid.runs),
  aliveAtNight: mid.aliveAtNight,
};

/* ══ 1b. A CELL WHERE THE NUMERATOR IS NOT EMPTY ═══════════════════
   The cell above returns 0 because every SURVIVING run had bought something -
   which is the argument, not a refutation: a run too poor to buy is a run that
   also dies before the test. To show the denominator actually matters, the
   prices are shimmed out of reach at runtime (toString + eval, nothing on
   disk), so every survivor fails to buy. The numerator then equals the base,
   the corrected figure reads ~100%, and the old formula would have reported
   the same data as ~23% - because it divided by runs that never got there. */
const shimmed = (function () {
  const src = _runEconomySim.toString();
  const marker = 'var FAM_PRICE={';
  const i = src.indexOf(marker);
  if (i < 0) return null;
  const j = src.indexOf('}', i);
  const patched = src.slice(0, i) +
    'var FAM_PRICE={amber:99999,obsidian:99999,silver:99999,starstone:99999,' +
    'vagabond:99999,jade:99999,jade2:99999' + src.slice(j);
  return (0, eval)('(' + patched + ')');
})();
out.unaffordable = shimmed
  ? (function () {
      const rr = shimmed({runs: RUNS, pwin: {1:0.45,2:0.50,3:0.55},
                          bwin: {1:0.35,2:0.40,3:0.45}});
      const n = Math.round(rr.pityNoBuyByN3 * rr.pityBase / 100);
      return {reported: rr.pityNoBuyByN3, base: rr.pityBase, runs: rr.runs,
              noBuyCount: n, oldFormulaWouldSay: Math.round(100 * n / rr.runs)};
    })()
  : null;

/* ══ 2. THE ALL-ZERO CELL - where it used to look like a measurement ══ */
const dead = run({1: 0, 2: 0, 3: 0}, {1: 0, 2: 0, 3: 0});
out.allZero = {reported: dead.pityNoBuyByN3, base: dead.pityBase,
               runsWon: dead.runsWon};

/* ══ 3. A CELL WHERE NEARLY EVERYONE SURVIVES - old == new ══════════
   the control: with almost no deaths the two denominators converge, so the
   fix must NOT invent a difference where there is none. */
const easy = run({1: 0.99, 2: 0.99, 3: 0.99}, {1: 0.99, 2: 0.99, 3: 0.99});
const easyNoBuy = Math.round(easy.pityNoBuyByN3 * easy.pityBase / 100);
out.nearlyAllSurvive = {
  reported: easy.pityNoBuyByN3, base: easy.pityBase, runs: easy.runs,
  oldFormulaWouldSay: Math.round(100 * easyNoBuy / easy.runs),
};

/* ══ 4. BAND 0 ══════════════════════════════════════════════════════ */
const src = _runEconomySim.toString();
out.band0 = {
  literalsGone: !/0:0\.48/.test(src) && !/0:0\.30/.test(src),
  gearLevelFloorsAtOne: /return 1;\s*\}/.test(src.slice(src.indexOf('function gearLevel'))),
  /* and moving what WOULD have been band 0 must change nothing */
  runsWonWithoutBand0: run({1: 0.55, 2: 0.62, 3: 0.68}, {1: 0.45, 2: 0.55, 3: 0.62}).runsWon,
};
/* POISON the band rather than nudge it. Comparing two runsWon integers with a
   +/-1 tolerance was a thin margin on binomial noise (~0.7pp per arm at
   n=4000) and flaked about one run in four - a probe failing for a reason that
   is not the code. NaN is the deterministic version: if band 0 were ever
   indexed, `Math.random() < NaN` is false, that seat always loses, and runsWon
   would collapse toward zero. So the signal is ~23 against ~0 instead of 23
   against 24, and no tolerance is needed. */
out.band0.runsWonWithPoisonedBand0 =
  run({0: NaN, 1: 0.55, 2: 0.62, 3: 0.68},
      {0: NaN, 1: 0.45, 2: 0.55, 3: 0.62}).runsWon;

/* ══ 5. SILVER'S PRICE, in all three tables ═════════════════════════ */
const store = (typeof DICE_STORE !== 'undefined' ? DICE_STORE : [])
  .filter(d => d && d.mat === 'silver')[0] || null;
const def = (typeof DICE_TYPES !== 'undefined' ? DICE_TYPES : [])
  .filter(d => d && d.id === 'silver')[0] || null;
const famPrice = /FAM_PRICE=\{[^}]*silver:(\d+)/.exec(src);
out.price = {
  shop: store ? store.price : null,
  shopStock: store ? store.stock : null,
  dieCost: def ? def.cost : null,
  economyModel: famPrice ? +famPrice[1] : null,
  amber: /amber:(\d+)/.exec(src) ? +/amber:(\d+)/.exec(src)[1] : null,
  obsidian: /obsidian:(\d+)/.exec(src) ? +/obsidian:(\d+)/.exec(src)[1] : null,
  /* the identity that made 580 hard to defend: no effect */
  effect: def ? def.effect : 'MISSING',
  rollTable: def ? def.rollTable : null,
};

out.VERDICT = {
  /* the pity fix, where it can show */
  runsActuallyDiedBeforeN3: out.pity.base > 0 && out.pity.base < out.pity.runs,
  /* The ordinary cell's numerator is near-empty - a run too poor to buy dies
     before the test can ask it - but it is STOCHASTIC, not zero by law. It
     read 0 on one run and non-zero on the next, so it is reported rather than
     asserted: turning one observation into an invariant is how a probe starts
     failing for reasons that are not the code. The two structural facts below
     are the load-bearing ones. */
  theOldDenominatorWasFarTooLarge: out.pity.base < out.pity.runs * 0.5,
  /* and where the numerator is NOT empty, the two formulas diverge hugely */
  shimBuilt: !!out.unaffordable,
  unaffordableCellFiresPity: !!out.unaffordable && out.unaffordable.reported >= 95,
  correctedIsFarAboveTheOldFormula: !!out.unaffordable &&
    out.unaffordable.reported > out.unaffordable.oldFormulaWouldSay * 2,
  theDenominatorIsReported: typeof out.pity.base === 'number',
  /* the all-zero cell still reads 0 but no longer looks like a measurement */
  allZeroStillReadsZero: out.allZero.reported === 0,
  allZeroShowsAnEmptyBase: out.allZero.base === 0,
  allZeroReallyKilledEveryone: out.allZero.runsWon === 0,
  /* the control: no invented difference when nobody dies */
  noInventedDifferenceWhenAllSurvive:
    Math.abs(out.nearlyAllSurvive.reported - out.nearlyAllSurvive.oldFormulaWouldSay) <= 1,
  /* band 0 */
  band0LiteralsDeleted: out.band0.literalsGone === true,
  gearLevelFloorsAtBand1: out.band0.gearLevelFloorsAtOne === true,
  aPoisonedBand0IsNeverRead: out.band0.runsWonWithPoisonedBand0 > 10 &&
                             out.band0.runsWonWithoutBand0 > 10,
  /* the price, in all three places, and still buyable */
  shopPriceIsThreeTwenty: out.price.shop === 320,
  dieCostIsThreeTwenty: out.price.dieCost === 320,
  economyModelIsThreeTwenty: out.price.economyModel === 320,
  stillStockedAtOne: out.price.shopStock === 1,
  sitsBetweenAmberAndObsidian:
    out.price.amber < out.price.economyModel && out.price.economyModel < out.price.obsidian,
  /* the premise for the cut: it carries no effect */
  silverStillHasNoEffect: out.price.effect === null,
  weightingUntouched: JSON.stringify(out.price.rollTable) === JSON.stringify([1,5,1,5,2,3,4,6]),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
