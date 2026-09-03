/* P929 - does a RIVAL-HELD ILL OMEN still land when the player BANKED?
 *
 * The card reads "BUST NEXT TURN AND PAY". It resolves in
 * CFX.ill_omen.rivalTurn, which branches on `ev.pts<=0` - and ev.pts is
 * _pTurnPts, fired from endPTurn. Measured at 0 on every banked turn, so the
 * omen landed unconditionally.
 *
 * THE TEST IS THE CARD'S OWN OUTCOME, not the field. Both arms arm a real
 * rival omen and call the game's real endPTurn; the only difference is whether
 * the turn banked. A banked turn must make the omen MISS - the player keeps
 * their points and the rival takes nothing from them - and a busted turn must
 * make it LAND. One arm on its own proves nothing: pre-fix, both landed.
 *
 * THE BANKED STATE IS SET THE WAY handleBank LEAVES IT: turnPts already cleared
 * and _pTurnBanked carrying the credited total. Reproducing that exactly is the
 * point - reading turnPts is what was wrong, so a probe that sets turnPts
 * instead would pass on the broken build.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const tierP = (function () {
  try { const d = famDef('ill_omen'); return (d && d.p && d.p[0]) || null; }
  catch (e) { return null; }
})();
out.cardNumbers = {tier1: tierP};

/* ONE endPTurn HANDS THE TURN TO THE RIVAL, so waiting for a second idle phase
   timed out and the BANKED arm - the only one that can show the bug - never ran
   in either build. The phase is reset directly between arms instead. That is
   synthetic, and it is sound for this test: what is under examination is the
   value endPTurn fires and the branch the handler takes on it, neither of which
   reads the phase. The player is also given a bank to be taken FROM, because at
   pPts=0 the "take" clamps to zero and the landing is invisible. */
async function arm(banked) {
  try {
    G.phase = 'idle'; G._oppTurnActive = false; G._endMatchFired = false;
    G.pPts = 3000;
  } catch (e) { return {err: 'cannot reset phase'}; }
  /* A REAL RIVAL-HELD OMEN, WHICH MEANS AN INSTANCE IN G.oF. The first version
     set only G._oIllOmen - the ARMED STATE - and the omen never resolved in
     either arm, because famFire dispatches by iterating G.pF / G.oF for card
     instances whose CFX entry has the hook. Arming the state without holding
     the card is not a rival with an Ill Omen; it is a flag nothing reads. */
  G.oF = [{id: 'ill_omen', tier: 1, charges: 1, state: {}}];
  G._oIllOmen = {tier: 1};
  G._famIllOmen = null;
  /* the state handleBank leaves behind: turnPts CLEARED, the credited total
     living in _pTurnBanked. Setting turnPts instead would pass pre-fix. */
  G.turnPts = 0;
  G.kept = [];
  G._pTurnBanked = banked;
  const pBefore = G.pPts, oBefore = G.oPts;
  try { endPTurn(); } catch (e) { return {err: 'endPTurn: ' + e.message}; }
  return {
    banked, pTurnPts: G._pTurnPts,
    /* proof the dispatch could see the card at all */
    rivalHeld: (G.oF || []).map(function (x) { return x.id; }),
    handlerExists: !!(typeof CFX !== 'undefined' && CFX.ill_omen && CFX.ill_omen.rivalTurn),
    pDelta: G.pPts - pBefore, oDelta: G.oPts - oBefore,
    omenStillArmed: !!G._oIllOmen,
  };
}

/* ── the busted turn: the omen SHOULD land ─────────────────────────── */
out.busted = await arm(0);
/* ── the banked turn: the omen should MISS ─────────────────────────── */
out.banked = await arm(1000);

const b = out.busted, k = out.banked;
const landAmt = tierP ? tierP[0] : null;   /* taken from the player */
const missAmt = tierP ? tierP[1] : null;   /* consolation to the rival */

out.VERDICT = {
  bothArmsRan: !b.err && !k.err,
  /* THE DISPATCH COULD REACH THE CARD - without this, two quiet arms read as
     "the omen behaved" when the truth is "nothing was asked" */
  theRivalActuallyHeldTheCard: (b.rivalHeld || []).indexOf('ill_omen') >= 0,
  theHandlerExists: b.handlerExists === true,
  theCardNumbersWereReadable: !!tierP,
  /* the omen consumed its arming in both arms, or it never resolved at all */
  theOmenResolvedBothTimes: b.omenStillArmed === false && k.omenStillArmed === false,
  /* THE BUSTED TURN: the player is taken from */
  theOmenLandedOnTheBust: (b.pDelta != null && landAmt != null)
    ? (b.pDelta < 0 && b.oDelta > 0) : null,
  /* THE BANKED TURN: the player loses nothing - this is what was broken */
  /* THE MISS PAYS THE PLAYER, and the first version had the direction backwards.
     The handler's else branch is `G.pPts+=_ioP[1]` with the log "THEIR OMEN
     MISSES - YOU GAIN 400", so a missed rival omen is +400 to the PLAYER and
     nothing to the rival - not a smaller take. Reading the outcome off the card
     rather than off an assumption about who benefits. */
  theOmenMissedOnTheBank: (k.pDelta != null && missAmt != null)
    ? k.pDelta === missAmt : null,
  theMissTookNothingFromThePlayer: (k.oDelta != null) ? k.oDelta === 0 : null,
  /* and _pTurnPts actually carried the banked total, which is the mechanism */
  thePTurnPtsCarriedTheBank: k.pTurnPts === 1000,
  thePTurnPtsWasZeroOnTheBust: b.pTurnPts === 0,
  /* the two arms must DIFFER, or the probe cannot tell a fix from a coincidence */
  theTwoArmsDiffer: (b.pDelta != null && k.pDelta != null)
    ? b.pDelta !== k.pDelta : null,
};
out.PASS = Object.keys(out.VERDICT).every(k2 => out.VERDICT[k2] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k2 => out.VERDICT[k2] !== true);
return out;
