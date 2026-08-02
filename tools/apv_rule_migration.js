/* THE RULE-ID MIGRATION, ON A COLD START.
 *
 * P428 renamed three rule ids to match the rules they carry (in_arrears ->
 * first_strike, confession -> still_waters, counterfeit -> kindred). Saves hold
 * those ids in two places that MATTER TO A PLAYER: `S.run.sleeve` is a rule
 * they chose to wear, and `S.run.tells` is the list they WON off bosses. A
 * rename without a migration silently deletes a hard-won spoil - it does not
 * error, the shelf is just emptier than it was.
 *
 * THE TEST HAS TO REPRODUCE A COLD START, and getting that wrong is why this
 * file exists rather than a one-off check. The migration lives inside
 * `if(!S){...}` in _getS - correct, that is run-load, where the brief asks
 * migrations to sit - so calling _getS() twice on a warm page skips it
 * entirely and reports a working migration as broken. Seed localStorage, drop
 * S, call in: that is the only path that exercises it.
 *
 * It also asserts the migrated ids RESOLVE. A rename that produces a tidy
 * string nothing answers to is the same lost spoil with better spelling. */
const OLD_TO_NEW = {
  in_arrears:  'first_strike',
  confession:  'still_waters',
  counterfeit: 'kindred'
};
const KEY = 'gambit4_proto';
const out = {};

_getS();
const backup = localStorage.getItem(KEY);

const seeded = JSON.parse(JSON.stringify(S));
seeded.run.sleeve = 'confession';
seeded.run.tells  = ['in_arrears', 'counterfeit', 'drill_order'];/* one already-current id, to prove the map does not touch it */
seeded.run.night  = seeded.run.night || { tier: 0, roster: [], seatsPlayed: [], results: [] };
seeded.run.night.sealTell = 'counterfeit';
localStorage.setItem(KEY, JSON.stringify(seeded));

S = undefined;   /* cold start */
_getS();

out.after = {
  sleeve: S.run.sleeve,
  tells:  (S.run.tells || []).slice(),
  seal:   S.run.night && S.run.night.sealTell
};
out.resolves = {};
out.after.tells.concat([out.after.sleeve, out.after.seal]).filter(Boolean)
  .forEach(id => { out.resolves[id] = !!_tellById(id); });

/* no old id may survive anywhere in the migrated save */
const blob = JSON.stringify(S);
out.staleLeftInSave = Object.keys(OLD_TO_NEW).filter(o =>
  new RegExp('"' + o + '"').test(blob));

/* put the real save back - a probe that leaves a doctored save behind is a
   probe that poisons whatever runs next */
try { if (backup !== null) localStorage.setItem(KEY, backup); else localStorage.removeItem(KEY); } catch (e) {}

out.verdict = {
  sleeveMigrated:   out.after.sleeve === 'still_waters',
  tellsMigrated:    out.after.tells.join() === 'first_strike,kindred,drill_order',
  sealMigrated:     out.after.seal === 'kindred',
  everyIdResolves:  Object.keys(out.resolves).length > 0
                    && Object.keys(out.resolves).every(k => out.resolves[k]),
  noStaleIdsInSave: out.staleLeftInSave.length === 0
};
return out;
