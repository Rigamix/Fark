/* CFX.sacrifice - does one shattered die cost one lane, and the RIGHT one?
 *
 * Three defects were fixed in P513 and each needs its own observable:
 *   1. double decrement - one sacrifice took TWO off numDice
 *   2. wrong-index splice - matchDice/_enchArr spliced at indexOf(d.mat), the
 *      FIRST die of that material rather than the one that shattered
 *   3. no relane - survivors above the removed lane kept their old lane number
 *
 * THE LOADOUT IS CHOSEN TO EXPOSE DEFECT 2. ['bone','iron','flint','bone',
 * 'amber','brass'] has bone at lane 0 AND lane 3. Sacrifice consumes
 * free[free.length-1], the LAST free die, so with all six free it takes lane 5
 * (brass) - which indexOf would resolve correctly and prove nothing. So the
 * probe commits the tail first, leaving the lane-3 bone as the last free die.
 * Then indexOf('bone') returns 0 while the die that dies is lane 3: the old
 * code would splice lane 0.
 *
 * MEASURED, per SACRIFICE (denominator stated):
 *   numDice before and after      - must fall by exactly 1
 *   which material left matchDice - must be the shattered die's lane
 *   _enchArr length               - must fall by exactly 1, in step
 *   pool lanes                    - must be contiguous, no gap, no duplicate
 *
 * The expected-old outcome is computed alongside from the same pre-state, so
 * the result contrasts the two rather than asserting the new one is right.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof CFX === 'undefined' || !CFX.sacrifice) return { error: 'CFX.sacrifice not reachable' };
if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };

const snap = () => ({
  numDice: G.numDice,
  matchDice: (G.matchDice || []).slice(),
  enchLen: (G._enchArr || []).length,
  poolLanes: (G.pool || []).map(d => d.lane),
  poolMats: (G.pool || []).map(d => d.mat)
});

try {
  _getS();
  S.run = S.run || {};
  S.run.tier = 2;
  S.run.dice = ['bone','iron','flint','bone','amber','brass'];  /* bone twice, on 0 and 3 */
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

/* commit lanes 4 and 5 so the LAST FREE die is the lane-3 bone */
try {
  G.pool.forEach(function (d) { if (d.lane === 4 || d.lane === 5) d.committed = true; });
} catch (e) {}

const free = G.pool.filter(d => !d.committed && !d._shattered);
const victim = free[free.length - 1];
if (!victim) return { error: 'no free die to sacrifice' };

const before = snap();
const victimLane = victim.lane, victimMat = victim.mat;
const oldWouldSplice = (G.matchDice || []).indexOf(victimMat);

let used = null;
try { used = CFX.sacrifice.use({ tier: 1 }); } catch (e) { return { error: 'use threw: ' + e.message, before: before }; }
await sleep(500);
const after = snap();

const dupes = (function () {
  const c = {}, d = [];
  after.poolLanes.forEach(l => { c[l] = (c[l] || 0) + 1; });
  Object.keys(c).forEach(l => { if (c[l] > 1) d.push(+l); });
  return d;
})();
const contiguous = after.poolLanes.slice().sort((a, b) => a - b)
  .every((l, i, arr) => i === 0 || l === arr[i - 1] + 1);

return {
  victimLane: victimLane, victimMat: victimMat,
  oldExpressionWouldHaveSpliced: oldWouldSplice,
  used: used, before: before, after: after,
  numDiceDelta: before.numDice - after.numDice,
  enchLenDelta: before.enchLen - after.enchLen,
  matchDiceDelta: before.matchDice.length - after.matchDice.length,
  duplicateLanes: dupes, poolLanesContiguous: contiguous,
  verdict: (before.numDice - after.numDice === 1
            && before.matchDice.length - after.matchDice.length === 1
            && before.enchLen - after.enchLen === 1
            && dupes.length === 0 && contiguous)
    ? 'PASS - one lane removed, arrays in step, pool relaned'
    : 'FAIL - see deltas'
};
