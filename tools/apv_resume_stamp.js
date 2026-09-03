/* P933 - does a turn survive a turnNum restore with its banked amount intact?
 *
 * THE SCENARIO. The resume path writes G.turnNum=rd.turnNum. P932 stamped
 * _pTurnBankedTurn only in startPTurn, which does NOT write turnNum - so after a
 * resume the stamp was stale against a restored turn number, the guard failed,
 * and endPTurn fell back to (G.turnPts||0)||0. On a banking turn that is 0,
 * which is P929's Ill Omen defect coming back through the resume path.
 *
 * THE CONTROL IS THE SAME RESTORE WITHOUT THE RESET, which is exactly what the
 * code did before this patch. Both arms restore turnNum to a different value;
 * only one calls the helper the patched resume path now calls. If both arms
 * agree, the probe is not testing the fix.
 *
 * AND THE STATE IS THE ONE handleBank LEAVES: turnPts cleared, the credited
 * total in _pTurnBanked. Setting turnPts instead would pass on the broken build,
 * because turnPts is the field that was never the problem.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

out.seam = {
  helper: typeof _pTurnBankReset === 'function',
  guardReadable: true,
};
if (typeof _pTurnBankReset !== 'function')
  return Object.assign(out, {err: '_pTurnBankReset is not defined'});

/* one turn, played through endPTurn, after a turnNum restore */
function turnAfterRestore(callTheReset) {
  try {
    G.phase = 'idle'; G._oppTurnActive = false; G._endMatchFired = false;
    G.oF = []; G._oIllOmen = null; G._famIllOmen = null;
  } catch (e) { return {err: 'cannot reset phase'}; }

  /* the turn begins normally: startPTurn's pair for the current turn */
  _pTurnBankReset();
  const stampAtStart = G._pTurnBankedTurn, turnAtStart = G.turnNum;

  /* THE RESUME: turnNum is restored to a different value. Pre-P933 nothing
     re-stamped here; post-P933 the resume path calls the helper. */
  G.turnNum = turnAtStart + 7;
  if (callTheReset) _pTurnBankReset();

  /* then the player banks, exactly as handleBank leaves it */
  G.turnPts = 0; G.kept = [];
  G._pTurnBanked = 1000;

  const before = G.pPts;
  try { endPTurn(); } catch (e) { return {err: 'endPTurn: ' + e.message}; }
  return {
    calledTheReset: callTheReset,
    turnAtStart, stampAtStart,
    turnAfterRestore: turnAtStart + 7,
    stampAtEnd: G._pTurnBankedTurn,
    pTurnPts: G._pTurnPts,
    staleCount: G._pTurnBankedStale || 0,
  };
}

/* ── the patched resume path: reset called ────────────────────────── */
out.withReset = turnAfterRestore(true);
/* ── the pre-P933 behaviour: turnNum restored, nothing re-stamped ─── */
out.withoutReset = turnAfterRestore(false);

const a = out.withReset, b = out.withoutReset;
out.VERDICT = {
  theHelperExists: out.seam.helper === true,
  bothArmsRan: !a.err && !b.err,
  /* THE FIX: a banked turn after a restore still reports its bank */
  theBankSurvivedTheRestore: a.pTurnPts === 1000,
  /* THE CONTROL: without the reset it does not - so the arms must differ, or
     this probe is measuring something the patch does not touch */
  theUnresetArmLostTheBank: b.pTurnPts === 0,
  theTwoArmsDiffer: a.pTurnPts !== b.pTurnPts,
  /* and the guard noticed, rather than silently returning 0 */
  theGuardFlaggedTheUnresetArm: b.staleCount > a.staleCount,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
