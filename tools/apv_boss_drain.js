/* IS THE PLAYER OUT-SCORED AT A HIGH-TIER BOSS, OR DRAINED?
 *
 * The ladder's boss cell is 0/30, and the player's score COLLAPSES at tiers 6-7
 * (0, 30, 50, 550, 555, 827, 900 - against 3550-7375 at tiers 3-4) with the same
 * loadout and policy. Finishing on exactly 0 three times is the tell: a
 * 500-threshold policy over ten turns does not reach zero by bad luck, and two
 * sites subtract from pPts under a Math.max(0,...) clamp - periodic_drain
 * (36797, on the player's TOTAL every interval turns) and challengePenalty
 * (35950).
 *
 * SO THE QUESTION IS BANKED VERSUS KEPT, which is exactly what P938 built. The
 * driver records turnSeq - the game's own per-turn value - so sum(turnSeq)
 * against final pPts separates "never scored" from "scored and lost it". Those
 * are different findings and only one of them is a difficulty result.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {matches: []};
const boot = await FXH.match(1);
if (!boot.ok) return {err: 'boot: ' + boot.why};

const BAND2 = ['amber','silver','bone','bone','iron','iron'];

for (const tier of [3, 3]) {  /* tier 3, where the ladder still saw the player score 3550-7375 */
  const r = await FDRV.playMatch({policy: 'bank500', tier, dice: BAND2,
                                  seat: 'boss', timeoutMs: 240000});
  if (r && r.err) { out.matches.push({tier, err: r.err}); continue; }
  const seq = r.turnSeq || [];
  const banked = seq.reduce((a, b) => a + b, 0);
  out.matches.push({
    tier, pPts: r.pPts, oPts: r.oPts, target: r.target, pTurns: r.pTurns,
    banked, kept: r.pPts, lostToDrain: banked - r.pPts,
    turnSeq: seq, banks: r.banks, busts: r.busts,
    heldTheTable: r.heldTheTable, turnsAddUp: r.turnsAddUp,
    stalled: r.stalled, endReason: r.endReason, lostTheTable: r.lostTheTable,
    turnCap: r.turnCap, rolls: r.rolls, keeps: r.keeps,
    oppCards: (function(){ try { return (G.oCards||[]).slice(0,6); } catch(e){ return null; } })(),
  });
  await FDRV.sleep(400);
}

const good = out.matches.filter(m => !m.err);
const drained = good.filter(m => m.lostToDrain > 0);
out.summary = {
  matches: good.length,
  totalBanked: good.reduce((a, m) => a + m.banked, 0),
  totalKept: good.reduce((a, m) => a + m.pPts, 0),
  totalLost: good.reduce((a, m) => a + m.lostToDrain, 0),
  matchesWithLoss: drained.length,
};
/* A MATCH THAT ENDED AFTER ONE TURN WITH THE RIVAL ON ZERO IS NOT A MATCH, and
   the first version of this probe reported "OUT-SCORED" from exactly that. The
   internal-consistency gates passed because one turn is trivially consistent.
   Plausibility has to be its own gate: an implausible rate beats the verdict. */
const played = good.filter(m => (m.pTurns || 0) >= 3 && (m.oPts || 0) > 0);
out.played = played.length;
out.VERDICT = {
  matchesRan: good.length >= 2,
  theMatchesActuallyPlayed: played.length >= 2,
  theTurnRecordIsSound: good.every(m => m.turnsAddUp === true && m.heldTheTable === true),
  /* THE QUESTION: did the player bank points and then lose them? */
  thePlayerBankedRealPoints: played.some(m => m.banked > 3000),
  pointsWereSubtractedAfterBanking: played.some(m => m.lostToDrain > 0),
  /* and how much - a few hundred is the known periodic_drain, thousands is not */
  theLossIsLarge: out.summary.totalLost > 1500,
};
out.CONCLUSION = played.length < 2
  ? ('NO CONCLUSION: only ' + played.length + ' of ' + good.length +
     ' matches actually played (pTurns ' + JSON.stringify(good.map(m => m.pTurns)) +
     ', oPts ' + JSON.stringify(good.map(m => m.oPts)) + '). A match that ends ' +
     'after one turn with the rival on zero measures nothing.')
  : out.summary.totalLost > 1500
  ? ('DRAINED: banked ' + out.summary.totalBanked + ', kept ' + out.summary.totalKept +
     ', lost ' + out.summary.totalLost + ' after banking')
  : (out.summary.totalLost > 0
      ? ('mostly out-scored; ' + out.summary.totalLost + ' lost after banking')
      : 'OUT-SCORED: the player simply never banked enough, nothing subtracted');
return out;
