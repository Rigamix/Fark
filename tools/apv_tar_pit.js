/* P923 - does TAR PIT actually take a die away?
 *
 * THE ASSERTION IS ON THE DICE ON THE TABLE, not on numDice and not on the log.
 * The bug was precisely that numDice went to 5, the log said "YOU ROLL 5", and
 * six dice were rolled - so any check that read numDice at the wrong moment, or
 * trusted the message, would have passed on the broken build. What counts is
 * how many dice the player is actually handed.
 *
 * AND THE CONTROL IS THE CHARGE. Tar Pit consumes G._oTarPit whether or not it
 * works, so "the player rolled 5" only means something alongside proof that the
 * counter went down on that same turn - otherwise a turn where Tar Pit simply
 * did not fire looks identical to a turn where it fired and worked.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

async function turnWithTarPit(arm) {
  /* get to a clean idle turn */
  const idle = await FXH.until(() => {
    try { return G && G.phase === 'idle' && !G._oppTurnActive && !G._endMatchFired; }
    catch (e) { return false; }
  }, 20000);
  if (idle == null) return {err: 'no idle turn: ' + (FXH.until.lastError || '')};

  try { G._oTarPit = arm ? 1 : 0; } catch (e) { return {err: 'cannot arm'}; }
  const armed = G._oTarPit;
  /* startPTurn is what applies it - the same call the handover makes */
  const loadout = (G.matchDice || []).length;
  try { startPTurn(); } catch (e) { return {err: 'startPTurn: ' + e.message}; }
  const numDiceAfterStart = G.numDice;
  const chargeAfter = G._oTarPit;

  /* now roll, and count what actually reaches the table */
  try { _tap(document.getElementById('btnRoll')); } catch (e) {
    try { document.getElementById('btnRoll').click(); } catch (e2) {}
  }
  const rolled = await FXH.until(() => {
    try { return (G.pool || []).filter(d => d.el).length > 0; } catch (e) { return false; }
  }, 15000);
  const onTable = rolled == null ? null : G.pool.filter(d => d.el).length;
  return {
    arm, armed, loadout,
    numDiceAfterStart, chargeAfter,
    chargeWasSpent: arm ? chargeAfter === armed - 1 : chargeAfter === 0,
    diceOnTable: onTable,
    numDiceAtRoll: G.numDice,
  };
}

/* THE BASELINE IS THE LOADOUT ON THE SAME TURN, not a second turn. The first
   version played an armed turn and then tried to play an unarmed one for
   comparison - but the armed turn consumes the turn, so the second arm found no
   idle phase and returned an error, and `b.diceOnTable === b.loadout` compared
   undefined to undefined and PASSED. A vacuous check: it could not fail in the
   configuration it actually ran in.
   G.matchDice.length is what the player is entitled to roll, read on the armed
   turn itself, so the comparison needs no second turn and cannot go vacuous. */
out.withTarPit = await turnWithTarPit(true);

const a = out.withTarPit;
const measured = !a.err && typeof a.diceOnTable === 'number' &&
                 typeof a.loadout === 'number' && a.loadout > 0;
/* A SECOND MECHANIC CUTS THE PLAYER TO FIVE DICE, AND IT IS RANDOM. The rung's
   `reduce_first_roll` card (POCKET SAND) fires on the first roll with a default
   0.7 chance and does `G.numDice=Math.min(G.numDice,5)` - gated on numDice>5.
   So "five dice reached the table" is NOT evidence about Tar Pit: on the
   pre-fix build, where Tar Pit's 5 is overwritten back to 6, the random cut
   then takes it to 5 anyway 70% of the time. The first version of this probe
   asserted on diceOnTable and the pre-fix control PASSED on one such draw,
   which is a random baseline making a dead mechanism look alive.

   THE DISCRIMINATOR IS numDiceAfterStart, which is deterministic: Tar Pit's
   effect either survives startPTurn or it does not. The random cut cannot
   reach it, because it runs later and needs numDice>5 - which Tar Pit, when it
   works, has already made false. So the two checks below are:
     numDiceAfterStart === loadout-1   Tar Pit survived the rebuild
     diceOnTable === numDiceAfterStart the table honoured it
   On the pre-fix build the first is false (6, not 5) and the second is false
   whenever the random cut fires (table 5, numDice 6) - so the arms separate on
   the mechanism rather than on a coin flip. */
const cutAfterStart = measured && a.numDiceAtRoll < a.numDiceAfterStart;
out.otherCutFired = cutAfterStart;
out.VERDICT = {
  theTurnRan: !a.err,
  /* every number the verdict rests on is a number, not an absent field */
  theCountsWereReadable: measured,
  /* the control: the charge really was spent, so this was a live Tar Pit turn
     and not a turn where it simply did not fire */
  theChargeWasSpent: a.chargeWasSpent === true,
  /* THE THING ITSELF, and it is deterministic - Tar Pit's die is still gone
     after the rebuild that used to overwrite it */
  tarPitSurvivedTheRebuild: measured
    ? a.numDiceAfterStart === a.loadout - 1 : null,
  /* the table honours the count, and no later effect moved it */
  theTableMatchesTheCount: measured
    ? a.diceOnTable === a.numDiceAfterStart : null,
  /* stated so a run where the random cut fired is legible rather than silently
     flattering the result */
  noOtherEffectCutTheDice: measured ? cutAfterStart === false : null,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
