/* P927 - does the rebuild guard fire when it should, and stay quiet otherwise?
 *
 * A GUARD THAT HAS NEVER FIRED IS NOT A GUARD. Tar Pit is fixed, so on the
 * current build nothing sets numDice above the rebuild and the guard is silent
 * - which is indistinguishable from a guard that cannot fire at all. So this
 * plants the exact fault it exists to catch and requires it to be caught, then
 * removes the fault and requires silence.
 *
 * THE INJECTION POINT IS REAL. _renderSelTags is called near the top of
 * startPTurn, after the entry stamp and before the rebuild - the same window
 * Tar Pit and Preserve both sat in. Wrapping it to set numDice reproduces
 * exactly the shape of all three historical bugs.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
/* NO ROLL FIRST. rollAndSettle leaves the phase in `choosing`, so the idle wait
   below timed out - and this test does not need dice on the table, only two
   passes through startPTurn. */

out.seam = {
  guardPresent: (function () {
    try { return typeof G._ndAtTurnTop !== 'undefined' ||
                 typeof startPTurn === 'function'; } catch (e) { return false; }
  })(),
  injectionPoint: typeof _renderSelTags === 'function',
};

const idle = async () => await FXH.until(() => {
  try { return G && G.phase === 'idle' && !G._oppTurnActive && !G._endMatchFired; }
  catch (e) { return false; }
}, 20000);

/* ── 1. THE FAULT IS PLANTED and must be caught ────────────────────── */
if (await idle() == null) return Object.assign(out, {err: 'no idle turn to start from'});
try { G._ndDiscarded = 0; G._ndDiscardedVal = null; } catch (e) {}
const orig = window._renderSelTags;
window._renderSelTags = function () {
  /* set numDice from inside the window between the stamp and the rebuild -
     the same position Tar Pit occupied */
  try { G.numDice = 3; } catch (e) {}
  return orig.apply(this, arguments);
};
try { startPTurn(); } catch (e) { out.plantThrew = e.message; }
window._renderSelTags = orig;
out.withFault = {
  discarded: G._ndDiscarded, discardedVal: G._ndDiscardedVal,
  ndAtTurnTop: G._ndAtTurnTop, numDiceAfter: G.numDice,
};

/* ── 2. THE FAULT IS REMOVED and it must go quiet ──────────────────── */
const wasDiscarded = G._ndDiscarded;
if (await idle() == null) { out.secondTurn = {err: 'no second idle turn'}; }
else {
  try { startPTurn(); } catch (e) { out.cleanThrew = e.message; }
  out.withoutFault = {
    discarded: G._ndDiscarded, unchanged: G._ndDiscarded === wasDiscarded,
    numDiceAfter: G.numDice,
    loadout: (G.matchDice || []).length,
  };
}

const a = out.withFault, b = out.withoutFault || {};
out.VERDICT = {
  theInjectionPointExists: out.seam.injectionPoint === true,
  /* THE POSITIVE CONTROL: the planted fault was caught */
  theGuardFiredOnThePlantedFault: a.discarded === 1,
  /* and it reported the value that was about to be lost, not just a count */
  theGuardNamedTheLostValue: a.discardedVal === 3,
  /* the rebuild still happened - the guard reports, it does not repair */
  theRebuildStillWon: a.numDiceAfter === (G.matchDice || []).length,
  /* THE NEGATIVE CONTROL: a clean turn is silent */
  theSecondTurnRan: !b.err && b.discarded !== undefined,
  theGuardStayedQuietWithoutTheFault: b.unchanged === true,
  nothingThrew: !out.plantThrew && !out.cleanThrew,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
