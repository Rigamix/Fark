/* P888 - the balance sim's free bust save for owning a silver die.
 *
 * THE DISCRIMINATOR IS EXACT ZERO, so no statistics are needed. Before the
 * fix, a loadout containing 'silver' produced bustsPerMatch of exactly 0 -
 * not a small number, zero - because one silver die was a 100% bust save on
 * every turn of the run. A no-silver loadout produced a normal rate through
 * the same code. So "the silver row is now non-zero while the bone row is
 * still non-zero" separates fixed from broken without any noise argument.
 *
 * The clone is the isolating control. 'silverx' is registered at runtime with
 * Silver's roll table copied byte for byte under a different id, so the old
 * indexOf('silver') test missed it. Before the fix, silver read 0 and the
 * clone read a normal rate - which is what pinned the defect to the string
 * comparison rather than to the weighting. After the fix the two must agree,
 * because they are now the same die in everything but name.
 *
 * Both entry points are checked: playMatch (bustsPerMatch) and the persona
 * path (_psRows bustRate), which reaches the same simTurn by another route
 * and collapsed to exactly 0.000 for all four personas when fed silver.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

/* register a byte-identical clone of silver under a different id */
/* the table is DICE_TYPES (a const array, so on the global binding rather
   than on window) - getDie() and _rollTable both read it, so a row pushed
   here is a real die everywhere the sim looks. */
const DICE = (typeof DICE_TYPES !== 'undefined' && DICE_TYPES) || null;
out.dieTableFound = !!DICE;
let cloneOk = false;
if (DICE && Array.isArray(DICE)) {
  const sv = DICE.filter(d => d && d.id === 'silver')[0];
  if (sv && !DICE.some(d => d && d.id === 'silverx')) {
    DICE.push(Object.assign({}, sv, {id: 'silverx', name: 'SILVERX'}));
    cloneOk = true;
  } else if (sv) cloneOk = true;
  out.silverRollTable = sv ? sv.rollTable : null;
}
out.cloneRegistered = cloneOk;

const ITERS = 90, TIERS = [0], POL = [{key: 'bank500', thresh: 500}];
const run = (dice) => {
  const rows = _runBalanceSim({
    iters: ITERS, tiers: TIERS, policies: POL,
    gears: [{key: 'T', dice: dice, bankAdd: 0}],
  }) || [];
  return rows.length ? rows[0] : null;
};

const BASE = ['iron', 'iron', 'flint', 'bone', 'bone'];
const rBone   = run(BASE.concat(['bone']));
const rSilver = run(BASE.concat(['silver']));
const rClone  = cloneOk ? run(BASE.concat(['silverx'])) : null;

out.playMatch = {
  bone:   rBone   ? {busts: rBone.bustsPerMatch,   win: rBone.patronWin}   : null,
  silver: rSilver ? {busts: rSilver.bustsPerMatch, win: rSilver.patronWin} : null,
  clone:  rClone  ? {busts: rClone.bustsPerMatch,  win: rClone.patronWin}  : null,
};

/* the persona path reaches the same simTurn by another route */
const persona = (dice) => {
  const rows = _runBalanceSim({personaStats: {turns: 400, dice: dice}}) || [];
  return rows.map(r => ({persona: r.persona || r.key, bustRate: r.bustRate}));
};
out.personaBone   = persona(['bone', 'bone', 'bone', 'bone', 'bone', 'bone']);
out.personaSilver = persona(['bone', 'bone', 'bone', 'bone', 'bone', 'silver']);

const rateOf = a => (a || []).map(r => r.bustRate).filter(v => typeof v === 'number');
const boneRates = rateOf(out.personaBone), silverRates = rateOf(out.personaSilver);
out.personaSummary = {
  boneAllNonZero:   boneRates.length > 0 && boneRates.every(v => v > 0),
  silverAllNonZero: silverRates.length > 0 && silverRates.every(v => v > 0),
  boneRates, silverRates,
};

/* the special-case string is gone from the code, not merely unused */
out.sourceHasNoSilverSpecialCase = !/indexOf\('silver'\)/.test(
  (typeof _runBalanceSim === 'function') ? _runBalanceSim.toString() : '');

out.VERDICT = {
  /* the runs happened at all */
  simProducedRows: !!rBone && !!rSilver,
  cloneWasRegistered: cloneOk === true,
  /* the control: a no-silver loadout always busted and still does */
  boneStillBusts: !!rBone && rBone.bustsPerMatch > 0,
  /* the fix: silver is no longer immune */
  silverNowBusts: !!rSilver && rSilver.bustsPerMatch > 0,
  /* and it is no longer distinguishable from a die that is identical
     except for its name - which is what the defect made it */
  silverMatchesItsClone: !rClone ||
    Math.abs(rSilver.bustsPerMatch - rClone.bustsPerMatch) <
      Math.max(0.35, 0.5 * rClone.bustsPerMatch),
  /* the other entry point into the same simTurn */
  personaBoneBusts:   out.personaSummary.boneAllNonZero === true,
  personaSilverBusts: out.personaSummary.silverAllNonZero === true,
  /* the string comparison is gone from the source */
  noSilverSpecialCaseInSource: out.sourceHasNoSilverSpecialCase === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
