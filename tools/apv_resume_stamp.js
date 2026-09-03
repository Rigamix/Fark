/* P934 - the invariant, tested in the order the game actually runs.
 *
 * THE PREVIOUS VERSION OF THIS FILE TESTED A SCENARIO THAT CANNOT HAPPEN. It ran
 * startPTurn's reset FIRST and the turnNum restore SECOND, then asserted the
 * bank was lost - but the real sequence is restore -> startPTurn -> bank ->
 * endPTurn, because initMatchScreen's tail reaches
 * `setTimeout(startPTurn,_matchStartDelay)` unconditionally and the early
 * returns above it are all inside `if(!params._resumeData)`. Its control arm
 * reproduced a state the shipping code never reaches, so the clean separation
 * between its two arms was an artefact of the inversion, not a finding.
 *
 * WHAT IS ACTUALLY WORTH ASSERTING: after startPTurn, the stamp matches turnNum,
 * whatever turnNum was set to beforehand - so a banked turn reports its bank.
 * The negative arm is the one state that would break it: a turn ENTERED WITHOUT
 * startPTurn, which is the only thing the guard now claims to catch.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

out.seam = {helper: typeof _pTurnBankReset === 'function',
            startPTurn: typeof startPTurn === 'function'};
if (!out.seam.helper || !out.seam.startPTurn)
  return Object.assign(out, {err: 'seam missing'});

function bankedTurn(goThroughStartPTurn, restoreTurnNumTo) {
  try {
    G.phase = 'idle'; G._oppTurnActive = false; G._endMatchFired = false;
    G.oF = []; G._oIllOmen = null; G._famIllOmen = null;
    G._pTurnBankedStale = 0;
  } catch (e) { return {err: 'cannot reset phase'}; }

  /* THE RESTORE FIRST, as initMatchScreen does it */
  if (restoreTurnNumTo != null) G.turnNum = restoreTurnNumTo;
  const turnAfterRestore = G.turnNum;

  /* THEN the turn begins - or, in the negative arm, does not */
  if (goThroughStartPTurn) { try { startPTurn(); } catch (e) { return {err: 'startPTurn: ' + e.message}; } }

  /* then the player banks, in the state handleBank leaves */
  G.turnPts = 0; G.kept = [];
  G._pTurnBanked = 1000;
  if (!goThroughStartPTurn) G._pTurnBankedTurn = turnAfterRestore - 3;/* a turn that never started */

  try { endPTurn(); } catch (e) { return {err: 'endPTurn: ' + e.message}; }
  return {
    wentThroughStartPTurn: goThroughStartPTurn,
    turnAfterRestore, pTurnPts: G._pTurnPts,
    staleCount: G._pTurnBankedStale || 0,
  };
}

/* ── the real sequence: restore, then startPTurn, then bank ───────── */
out.restoredThenStarted = bankedTurn(true, (G.turnNum || 1) + 7);
/* ── a plain turn with no restore at all ──────────────────────────── */
out.plainTurn = bankedTurn(true, null);
/* ── the negative arm: a turn that never went through startPTurn ──── */
out.neverStarted = bankedTurn(false, null);

const a = out.restoredThenStarted, b = out.plainTurn, c = out.neverStarted;
out.VERDICT = {
  allArmsRan: !a.err && !b.err && !c.err,
  /* A RESTORE DOES NOT BREAK THE BANK, because startPTurn follows it */
  theBankSurvivesARestore: a.pTurnPts === 1000,
  aPlainTurnAlsoCarriesItsBank: b.pTurnPts === 1000,
  /* and the restore arm is not special - which is the point of the retraction */
  theRestoreArmMatchesThePlainTurn: a.pTurnPts === b.pTurnPts,
  /* THE GUARD STILL CATCHES ITS ONE REAL CASE: a turn that never started */
  theGuardCatchesAnUnstartedTurn: c.staleCount > 0 && c.pTurnPts === 0,
  /* the arms must differ, or the negative arm is testing nothing */
  theNegativeArmDiffers: c.pTurnPts !== b.pTurnPts,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
