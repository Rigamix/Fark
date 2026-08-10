/* D23(a) - every live boss tell must have a cursed-seat route.
 *
 * still_waters was the one that did not: eight boss tells in TIERS, seven of
 * them in _SEAL_POOL, and the eighth slot held the PARKED `steeped` instead. So
 * Aldric's badge was the only one a player could never meet on a sealed seat -
 * on a rule the file had already unblocked for exactly that purpose (see the
 * note above _SEAL_POOL about "a rule the player had won and could not use").
 *
 * ASSERTS THE CLASS, NOT THE INSTANCE. A check for `still_waters` in the array
 * would pass forever and catch nothing the next time a tell is added. This
 * derives the tell list from the LIVE TIERS table and asks whether the pool
 * covers it, so a ninth boss with a new rule fails here on the day it lands.
 *
 * CONTROLS
 *   - the census found a plausible number of tells at all. A TIERS walk that
 *     silently yielded [] would make "every tell is covered" vacuously true,
 *     which is the shape a zero-from-a-name-search keeps taking in this project.
 *   - _rollSealTell can actually PRODUCE the newly-added rule. Membership in the
 *     array and reachability through the picker are different claims; the picker
 *     is driven 400 times rather than read.
 *   - a rule NOT in the pool is never produced, so the picker is bounded by the
 *     array rather than by something else.
 */
const v = {}, notes = {};

/* The live tell list, off RUNGS rather than off a hand-kept copy.
   IT WAS TIERS IN THE FIRST VERSION and TIERS carries no `tell` field, so the
   walk returned [] and `missing` was empty for the most vacuous reason there
   is. The census control below is the only thing that made that visible - the
   coverage key was reporting a clean pass over nothing at all. */
const tells = [];
try {
  (typeof RUNGS !== 'undefined' ? RUNGS : []).forEach(function (r) {
    if (r && r.tell && r.tell.id && tells.indexOf(r.tell.id) < 0) tells.push(r.tell.id);
  });
} catch (e) { notes._rungsErr = String(e).slice(0, 80); }

const pool = (typeof _SEAL_POOL !== 'undefined' ? _SEAL_POOL : []).slice();
const missing = tells.filter(function (id) { return pool.indexOf(id) < 0; });
notes._census = { tells: tells, tellCount: tells.length, pool: pool, poolCount: pool.length,
                  missing: missing };

/* CONTROL: the walk found tells at all. Without this, an empty list makes the
   coverage claim below true and meaningless. */
v.tellCensusFoundTells = tells.length >= 8;
v.everyLiveTellHasACursedSeatRoute = tells.length >= 8 && missing.length === 0;

/* CONTROL: membership is not reachability - drive the picker. */
const drawn = {};
try { for (let i = 0; i < 400; i++) { const r = _rollSealTell(); drawn[r] = (drawn[r] || 0) + 1; } }
catch (e) { notes._pickErr = String(e).slice(0, 80); }
notes._picker = { distinct: Object.keys(drawn).length, drawn: drawn };
v.pickerProducesEveryPooledRule = pool.every(function (id) { return drawn[id] > 0; });
/* and produces nothing else - the picker is bounded by the array */
v.pickerProducesNothingOutsideThePool = Object.keys(drawn).every(function (id) { return pool.indexOf(id) >= 0; });

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
