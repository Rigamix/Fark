/* P585's DIFFICULTY COST, measured instead of asserted.
 *
 * I shipped the spent-brand rule calling it "a difficulty change" on the
 * strength of "a row whose only live face is a spent brand is now a bust" -
 * which says it CAN happen and nothing about how often. Denis: that is a real
 * gap for something being called a difficulty change.
 *
 * THE INSTRUMENT. FSIM's PLAYER side drives the real game - startPTurn,
 * rollPool, afterRollLite, handleBank - and its own header records that the bust
 * gate runs `anyScoring`, "which itself asks _dieIsIcon". _dieIsIcon is exactly
 * the predicate P585 changed, so the thing under test is genuinely exercised.
 * (FSIM's OPPONENT is a separate model - see OPEN section 1a - which is why this
 * measures PLAYER TURNS and never a win rate.)
 *
 * THE ARMS differ in ONE line. `_brandSpent` is a top-level declaration, so it
 * is a property of the global object and _dieIsIcon resolves it through the
 * scope chain; stubbing it to `false` restores exactly the pre-P585 rule with no
 * other change. Same build, same policy, same gear, same seed.
 *
 * WHY THE STREAMS DIVERGE, AND WHY THAT IS CORRECT. With the rule on, a spent
 * brand is not kept, so a different number of dice roll next - the two arms stop
 * seeing identical dice the moment the rule first bites. That IS the effect
 * being measured; pinning them together would measure nothing.
 *
 * DENOMINATOR, stated because a rate without one means nothing: everything below
 * is PER PLAYER TURN, on gear that actually carries brands. A player with no
 * branded dice cannot meet this rule at all, so the honest headline is
 * conditional on holding brands - reported separately for one brand and three.
 */
var TURNS = 4000;
var out = { turns: TURNS, arms: {} };

function run(ruleOn, gear, seedTag) {
  var real = window._brandSpent;
  if (!ruleOn) window._brandSpent = function () { return false; };
  var busts = 0, turns = 0, iconsFired = 0, hots = 0, banked = 0, errs = 0;
  try {
    FSIM.setupMatch({ tier: 3, dice: gear.dice, ench: gear.ench, fcards: [] });
    var pol = FSIM.POLICIES.bea;
    for (var i = 0; i < TURNS; i++) {
      var r;
      try { r = FSIM.simTurn(pol, { turnsLeft: 8, oppTotal: 0 }); }
      catch (e) { errs++; continue; }
      if (r.err) { errs++; }
      turns++;
      if (r.busted) busts++;
      iconsFired += r.iconsFired || 0;
      hots += r.hot || 0;
      banked += r.banked || 0;
      /* a fresh match every 8 turns, so the run does not sit in one end-state */
      if (i % 8 === 7) FSIM.setupMatch({ tier: 3, dice: gear.dice, ench: gear.ench, fcards: [] });
    }
  } finally { window._brandSpent = real; }
  return { turns: turns, busts: busts, bustRate: +(busts / Math.max(1, turns)).toFixed(4),
           iconsFiredPerTurn: +(iconsFired / Math.max(1, turns)).toFixed(3),
           hotPerTurn: +(hots / Math.max(1, turns)).toFixed(3),
           meanBanked: Math.round(banked / Math.max(1, turns)), errs: errs };
}

/* CONTROL GEAR: no brands at all. The rule cannot apply, so both arms must
   agree - if they do not, the harness is noisy enough that the real arms below
   mean nothing either. */
var GEAR_NONE = { dice: ['bone','bone','bone','bone','bone','bone'],
                  ench: [null,null,null,null,null,null] };
/* ONE brand, and THREE - the rule's cost should scale with how many the player
   holds, and a player with none is the control above. */
var GEAR_ONE  = { dice: ['bone','bone','bone','bone','bone','bone'],
                  ench: ['tithe',null,null,null,null,null] };
var GEAR_MANY = { dice: ['bone','bone','bone','bone','bone','bone'],
                  ench: ['tithe','tithe','tithe',null,null,null] };

FSIM.quiet();
FSIM.installRng(20260810);
out.arms.noBrands_ruleOff = run(false, GEAR_NONE);
FSIM.installRng(20260810);
out.arms.noBrands_ruleOn  = run(true,  GEAR_NONE);

FSIM.installRng(20260810);
out.arms.oneBrand_ruleOff = run(false, GEAR_ONE);
FSIM.installRng(20260810);
out.arms.oneBrand_ruleOn  = run(true,  GEAR_ONE);

FSIM.installRng(20260810);
out.arms.threeBrands_ruleOff = run(false, GEAR_MANY);
FSIM.installRng(20260810);
out.arms.threeBrands_ruleOn  = run(true,  GEAR_MANY);
FSIM.restoreRng();
FSIM.loud();

function delta(a, b) { return +((b.bustRate - a.bustRate) * 100).toFixed(2); }
out.deltaPP = {
  noBrands:    delta(out.arms.noBrands_ruleOff,    out.arms.noBrands_ruleOn),
  oneBrand:    delta(out.arms.oneBrand_ruleOff,    out.arms.oneBrand_ruleOn),
  threeBrands: delta(out.arms.threeBrands_ruleOff, out.arms.threeBrands_ruleOn),
};
/* the control has to be ~0 or nothing else here is readable */
out.controlIsFlat = Math.abs(out.deltaPP.noBrands) < 1.5;
return out;
