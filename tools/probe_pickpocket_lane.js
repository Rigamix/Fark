/* DOES THE PICKPOCKET FIX ACTUALLY STOP THE LANE DUPLICATE?
 *
 * THE BUG (P510), verified in source: _maybeFireCutpurse splices the palmed die
 * out of G.pool (11525) without touching G.numDice, so the next refill computes
 * needNew = numDice - pool.length = 1 (24980) and _lane =
 * (G.pool.length + i) % G.matchDice.length = 5 % 6 = 5 (25028). G.pool is not
 * reassigned until 25054, so the length is loop-invariant. The lane is stamped
 * explicitly at 25047, so _laneOf returns a genuine duplicate.
 *
 * The fix adds `if(G.numDice>1)G.numDice--;` after the splice, mirroring
 * activateVanishingAct. It works by driving needNew to 0.
 *
 * THIS PROBE DOES NOT READ THE PATCH. It drives a real match, palms a die
 * through the game's own path, rolls, and reads the resulting lanes. A patch
 * being present in the file is not evidence it works - that is the whole
 * lesson of this session.
 *
 * MEASURED, per PALM (denominator stated):
 *   duplicate lanes in G.pool after the next roll   - the defect itself
 *   G.numDice vs G.pool.length                      - must agree
 *   materials and enchants per lane                 - the player-visible harm
 *
 * PASS  : zero duplicate lanes, numDice === pool.length, pool 6 -> 5 -> stays 5
 * FAIL  : any repeated lane, which is the bug still live
 *
 * SEMANTICS DRIFTED AFTER P512 - READ THIS BEFORE TRUSTING THE VERDICT.
 * P512 made the refill assign provably-free lanes, closing the middle-removal
 * defect at source. This probe's control neutralises P510 by pushing numDice
 * UP, which produces numDice > matchDice.length - the OVERFLOW branch P512
 * deliberately left unchanged, because what a 7th die's lane and material
 * should be on a 6-lane loadout is an unmade design decision, not a bug.
 * So when the control now says "reproduces the bug" it is reproducing the
 * overflow branch, NOT the defect P512 fixed. For that one see
 * probe_refill_freelane.js, which removes a die from the middle and leaves
 * numDice alone.
 * This probe is also timing-sensitive: afterRoll can sample across a turn
 * boundary, where startPTurn has cleared the pool and reset numDice to
 * matchDice.length. pool 0 or pool 6 there are both normal; the invariant that
 * matters is duplicateLanes staying empty.
 *
 * A CONTROL RUN IS INCLUDED. The same sequence is driven with the decrement
 * neutralised at runtime (numDice put back up by 1 immediately after the palm),
 * reproducing the pre-fix behaviour. If the control does NOT show duplicates,
 * this probe cannot see the bug at all and its PASS is meaningless - that
 * distinction is the difference between a fix and a blind spot.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof _maybeFireCutpurse !== 'function') return { error: '_maybeFireCutpurse not reachable' };
if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };

const laneReport = () => {
  const p = (typeof G !== 'undefined' && G && G.pool) ? G.pool : [];
  const lanes = p.map(d => d.lane);
  const seen = {}, dups = [];
  lanes.forEach(l => { seen[l] = (seen[l] || 0) + 1; });
  Object.keys(seen).forEach(l => { if (seen[l] > 1) dups.push({ lane: +l, count: seen[l] }); });
  return { poolLen: p.length, numDice: G.numDice, lanes: lanes,
           mats: p.map(d => d.mat), enchs: p.map(d => d.ench || '-'),
           duplicateLanes: dups, agree: p.length === G.numDice };
};

async function oneRun(neutraliseFix) {
  try {
    _getS();
    S.run = S.run || {};
    S.run.tier = 2;                       // FINNICK - pickpocket is his tell
    S.run.dice = ['bone','iron','flint','lead','amber','brass'];
    S.run.cards = S.run.cards || [];
    S.settings = S.settings || {}; S.settings.reducedMotion = true;
    launchBossMatch();
  } catch (e) { return { error: 'launch: ' + e.message }; }
  /* launchBossMatch reaches the match screen but does not roll - the player
     does. Drive the game's own first roll rather than building a pool by hand,
     so the refill path under test is the real one. */
  if (!(await until(() => typeof G !== 'undefined' && G && G.rung, 9000)))
    return { error: 'never reached a match' };
  await sleep(700);
  try { if (typeof startPTurn === 'function') startPTurn(); } catch (e) {}
  await sleep(200);
  try { if (typeof handleRoll === 'function') handleRoll();
        else if (typeof rollPool === 'function') rollPool(); } catch (e) {}
  if (!(await until(() => G && G.pool && G.pool.length >= 6, 9000)))
    return { error: 'never reached a rolled pool',
             diag: { hasPool: !!(G && G.pool), poolLen: (G && G.pool) ? G.pool.length : null,
                     numDice: G && G.numDice, phase: G && String(G.phase) } };
  await sleep(600);

  const before = laneReport();

  /* arm the tell the palm gates on, then fire it through the game's own path */
  G._tell = { id: 'pickpocket' };
  const poolBefore = G.pool.length;
  try { _maybeFireCutpurse(); } catch (e) { return { error: 'cutpurse threw: ' + e.message }; }

  /* the palm removes on a 650ms timer */
  const fired = await until(() => G.pool.length < poolBefore, 3000);
  if (!fired) return { skipped: 'palm did not fire (suppressed or no safe candidate)', before: before };

  if (neutraliseFix) G.numDice = G.numDice + 1;   /* undo the fix, reproduce pre-P510 */

  const afterPalm = laneReport();

  /* now roll - this is where the refill stamps the duplicate lane */
  try { if (typeof handleRoll === 'function') handleRoll(); } catch (e) {}
  await sleep(1400);
  const afterRoll = laneReport();

  return { before: before, afterPalm: afterPalm, afterRoll: afterRoll };
}

const fixed = await oneRun(false);
await sleep(700);
const control = await oneRun(true);

return {
  WITH_FIX: fixed,
  CONTROL_fix_neutralised: control,
  verdict: (fixed && fixed.afterRoll && control && control.afterRoll)
    ? ((fixed.afterRoll.duplicateLanes.length === 0 && control.afterRoll.duplicateLanes.length > 0)
        ? 'PASS - fix holds and the control reproduces the bug'
        : (control.afterRoll.duplicateLanes.length === 0
            ? 'INCONCLUSIVE - the control did not reproduce the bug, so this probe cannot see it'
            : 'FAIL - duplicates present with the fix applied'))
    : 'INCOMPLETE - one or both runs did not produce a rolled pool'
};
