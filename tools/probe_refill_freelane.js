/* DOES THE REFILL PICK A FREE LANE, OR GUESS FROM POOL LENGTH?
 *
 * P512 replaced
 *     const _lane=(G.pool.length+i)%G.matchDice.length;
 * with a pick from the lanes that are provably unoccupied.
 *
 * THE TEST HAS TO EXERCISE THE DEFECT DIRECTLY, not via Pickpocket. P510 made
 * Pickpocket decrement numDice, which drives needNew to 0 so the refill loop
 * never runs - it routes around this line rather than through it. And the
 * Pickpocket control (which forces numDice back up) lands on numDice >
 * matchDice.length, the OVERFLOW case P512 deliberately left unchanged. Neither
 * touches what was fixed.
 *
 * So: remove a die from the MIDDLE of the pool and leave numDice high. That is
 * the exact hazard shape - the surviving pool is non-contiguous, needNew is 1,
 * and the old expression computed (5+0)%6 = 5, stamping a second die onto the
 * last lane instead of refilling the hole.
 *
 * MEASURED, per REFILL (denominator stated: one roll that adds dice):
 *   which lane the new die takes
 *   whether any lane appears twice
 *   whether every lane 0..matchDice.length-1 is present exactly once
 *
 * PASS : the new die takes the VACATED lane, no duplicates, full coverage
 * FAIL : the new die takes the last lane, duplicating it - the old behaviour
 *
 * The expected-old value is computed alongside and reported, so the result
 * shows what the previous code would have done on the same state rather than
 * asking anyone to take that on trust.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };

const report = () => {
  const p = (typeof G !== 'undefined' && G && G.pool) ? G.pool : [];
  const lanes = p.map(d => d.lane);
  const seen = {}, dups = [];
  lanes.forEach(l => { seen[l] = (seen[l] || 0) + 1; });
  Object.keys(seen).forEach(l => { if (seen[l] > 1) dups.push({ lane: +l, count: seen[l] }); });
  const missing = [];
  for (let i = 0; i < (G.matchDice || []).length; i++) if (!seen[i]) missing.push(i);
  return { poolLen: p.length, numDice: G.numDice, lanes: lanes,
           mats: p.map(d => d.mat), duplicateLanes: dups, missingLanes: missing };
};

try {
  _getS();
  S.run = S.run || {};
  S.run.tier = 2;
  S.run.dice = ['bone','iron','flint','lead','amber','brass'];
  S.run.cards = S.run.cards || [];
  S.settings = S.settings || {}; S.settings.reducedMotion = true;
  launchBossMatch();
} catch (e) { return { error: 'launch: ' + e.message }; }

if (!(await until(() => typeof G !== 'undefined' && G && G.rung, 9000)))
  return { error: 'never reached a match' };
await sleep(700);
try { if (typeof startPTurn === 'function') startPTurn(); } catch (e) {}
await sleep(200);
try { if (typeof handleRoll === 'function') handleRoll(); } catch (e) {}
if (!(await until(() => G && G.pool && G.pool.length >= 6, 9000)))
  return { error: 'never reached a rolled pool' };
await sleep(600);

const before = report();

/* Remove the die on lane 2 - the MIDDLE - leaving numDice untouched. This is
   the pre-P510 hazard shape reproduced deliberately: a non-contiguous pool
   with numDice still at full. */
const VICTIM_LANE = 2;
let removed = null;
try {
  const idx = G.pool.findIndex(d => d.lane === VICTIM_LANE);
  if (idx < 0) return { error: 'no die on lane ' + VICTIM_LANE, before: before };
  removed = { lane: G.pool[idx].lane, mat: G.pool[idx].mat };
  if (G.pool[idx].el && G.pool[idx].el.parentNode) G.pool[idx].el.parentNode.removeChild(G.pool[idx].el);
  G.pool.splice(idx, 1);
} catch (e) { return { error: 'removal threw: ' + e.message }; }

const afterRemove = report();

/* what the OLD expression would have produced on exactly this state */
const oldWouldPick = (G.pool.length + 0) % G.matchDice.length;

/* roll - this runs the refill */
try { if (typeof handleRoll === 'function') handleRoll(); } catch (e) {}
await sleep(1500);
const afterRefill = report();

const newDieLane = (function () {
  const b = {}; afterRemove.lanes.forEach(l => { b[l] = (b[l] || 0) + 1; });
  for (const l of afterRefill.lanes) { if (!b[l]) return l; b[l]--; }
  return null;
})();

return {
  removedLane: removed ? removed.lane : null,
  removedMat: removed ? removed.mat : null,
  before: before, afterRemove: afterRemove, afterRefill: afterRefill,
  laneTakenByNewDie: newDieLane,
  oldExpressionWouldHavePicked: oldWouldPick,
  verdict: (afterRefill.duplicateLanes.length === 0
            && newDieLane === VICTIM_LANE
            && afterRefill.missingLanes.length === 0)
    ? 'PASS - refilled the vacated lane, no duplicates, full coverage'
    : (newDieLane === oldWouldPick && oldWouldPick !== VICTIM_LANE
        ? 'FAIL - took the lane the OLD expression would have, bug still live'
        : 'UNEXPECTED - see laneTakenByNewDie against removedLane')
};
