/* HOW OFTEN DOES P585 ACTUALLY COST A TURN?
 *
 * The aggregate bust rate could not answer it: measured at n=4000, the deltas
 * were +0.20pp and -0.22pp against a standard error of ~0.72pp, with a control
 * that was exactly flat. The rule's effect is real but rarer than the noise
 * floor of that measurement, so counting the EVENT is the only honest route.
 *
 * THE EVENT, precisely. P585 makes a spent brand stop counting as a live icon.
 * That changes an outcome only when ALL of these hold at the same moment:
 *   - the row scores nothing, so the bust gate is the thing deciding
 *   - a FREE die is showing its branded face
 *   - that brand has ALREADY fired this turn
 * Before P585 the row was rescued; now it busts. Note the second condition needs
 * the die to be free again after firing, which in practice means hot dice has
 * rebuilt the pool - that compound is why it is rare.
 *
 * MEASURED BY WRAPPING _iconOnTable, the predicate the bust gate consults, and
 * asking at each call whether the answer CHANGED because of the rule: true
 * without _brandSpent, false with it. That is exactly "the rule cost this row",
 * counted where the decision is made rather than inferred from a total.
 *
 * CONTROLS
 *   - the wrap actually fires. A count of zero from a hook that never ran is
 *     indistinguishable from a rule that never bites.
 *   - brands actually fire in the run. If none ever did, no brand could be
 *     spent and zero would again be meaningless. Counted at the source rather
 *     than from the harness's own iconsFired, which reads 0 by construction
 *     post-P585 (it splits AFTER the commit that marks the brand spent).
 */
var TURNS = 12000;
var out = { turns: TURNS };

var GEAR = { dice: ['bone','bone','bone','bone','bone','bone'],
             ench: ['tithe','tithe','tithe',null,null,null] };

var stats = { iconChecks:0, rescuedEither:0, costByRule:0, fires:0, turns:0, busts:0, hot:0 };

/* WRAPPED AT THE BUST GATE ITSELF. The first version wrapped _iconOnTable and
   its control caught that the hook never ran once in 12,000 turns - that
   predicate is not on this path. The harness's own header names the gate:
   "bust gate  anyScoring (which itself asks _dieIsIcon)". So anyScoring is where
   the decision is made and where the rule can flip it. */
var realAnyScoring = window.anyScoring;
var realIconFire = window._iconFire;
var realBrandSpent = window._brandSpent;

window._iconFire = function(d, side){ stats.fires++; return realIconFire.apply(this, arguments); };
window.anyScoring = function(){
  stats.iconChecks++;
  var args = arguments;
  var withRule = realAnyScoring.apply(this, args);
  /* the identical question with the rule switched off, nothing else changed */
  window._brandSpent = function(){ return false; };
  var withoutRule;
  try { withoutRule = realAnyScoring.apply(this, args); }
  finally { window._brandSpent = realBrandSpent; }
  if (withoutRule) stats.rescuedEither++;
  if (withoutRule && !withRule) stats.costByRule++;
  return withRule;
};

/* SWEEPING THE POLICIES, because the single-policy caveat is the one thing the
   two earlier checks could NOT test: they shared bea, the gear and the seed, so
   their agreement said nothing about any of those. The event needs a brand to
   fire and the turn to KEEP ROLLING afterwards, so a policy that banks later is
   where it would appear if it appears at all - bea banks at 500, rita at 200,
   greg gambles. */
var POLS = ['bea','carl','rita','ned','greg_naive','greg_informed'];
out.byPolicy = {};
FSIM.quiet();
try {
 POLS.forEach(function(pname){
  var pol = FSIM.POLICIES[pname]; if(!pol) return;
  stats = { iconChecks:0, rescuedEither:0, costByRule:0, fires:0, turns:0, busts:0, hot:0 };
  FSIM.installRng(20260810);
  FSIM.setupMatch({ tier: 3, dice: GEAR.dice, ench: GEAR.ench, fcards: [] });
  for (var i = 0; i < TURNS; i++) {
    var r;
    try { r = FSIM.simTurn(pol, { turnsLeft: 8, oppTotal: 0 }); } catch (e) { continue; }
    stats.turns++;
    if (r.busted) stats.busts++;
    stats.hot += r.hot || 0;
    if (i % 8 === 7) FSIM.setupMatch({ tier: 3, dice: GEAR.dice, ench: GEAR.ench, fcards: [] });
  }
  out.byPolicy[pname] = { turns:stats.turns, costByRule:stats.costByRule,
    hookFired:stats.iconChecks>100, rescuedEither:stats.rescuedEither,
    firesPerTurn:+(stats.fires/Math.max(1,stats.turns)).toFixed(3),
    rollsHot:+(stats.hot/Math.max(1,stats.turns)).toFixed(3),
    bustRate:+(stats.busts/Math.max(1,stats.turns)).toFixed(4) };
 });
} finally {
  window.anyScoring = realAnyScoring;
  window._iconFire = realIconFire;
  window._brandSpent = realBrandSpent;
  FSIM.restoreRng(); FSIM.loud();
}

out.everyHookFired = Object.keys(out.byPolicy).every(function(k){return out.byPolicy[k].hookFired;});
out.everyPolicyFiredBrands = Object.keys(out.byPolicy).every(function(k){return out.byPolicy[k].firesPerTurn>0;});
out.totalCostEvents = Object.keys(out.byPolicy).reduce(function(a,k){return a+out.byPolicy[k].costByRule;},0);
return out;
