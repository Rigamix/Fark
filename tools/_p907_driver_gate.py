# -*- coding: utf-8 -*-
u"""P907: the driver resets the run per match, and the gate stops firing on
losing honestly.

TWO DEFECTS, BOTH FOUND BY RUNNING IT.

THE THIRD MATCH NEVER STARTED. bank300 won, bank500 lost, and `hot` could not
launch - because losing a boss match ends the run, and the driver was reusing
whatever S.run was left over. It calls _freshRun() now, which is what the game
itself does at 11273, so every match starts from the same place. That is not
only a fix for the third match: matches that inherit each other's run are not
independent samples, which is the property a ladder is entirely made of.

THE GATE WAS WRONG IN A WAY THAT WOULD HAVE FIRED ON GOOD DATA. A 45% floor on
one match's total against its target refuses a match the player simply LOST -
bank500 scored 2900 of 7200 while the rival overshot to 8850, which is a real
result and not a broken driver. And it would not reliably catch the case it was
built for: the broken run's tier-0 match scored 3400 against a 3800 target, a
respectable 89%, while its tier-6 match scored 3550 against 12500.

Which is the actual diagnostic, stated properly: the player's total does not
SCALE. ~2000 whatever it is asked for. That needs two matches at different
tiers, not one against a floor - so the gate becomes a pair test: with the
targets a factor of 2.5 apart, the totals must move by at least 1.5x. Fed the
broken run's own numbers it refuses; fed a scaling pair it passes.

What survives per-match is structural rather than a performance bar: the match
ran to completion, somebody reached the target, and the player banked at least
once. A driver that never banks is broken; a driver that banks and loses is a
driver.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
    edits.append(label)


DRV = os.path.join(ROOT, 'tools', 'fark_driver.js')
PRB = os.path.join(ROOT, 'tools', 'apv_driver.js')

# ── 1. a fresh run per match ────────────────────────────────────────
sub(DRV,
    u"""    /* start it */
    try { delete S.pendingMatch; } catch (e) {}
    window._fkDiscardOk = true;""",
    u"""    /* start it. A FRESH RUN EVERY TIME, which is what the game does at 11273.
       Without it the third match never launched - bank300 won, bank500 lost,
       and losing a boss match ends the run, so `hot` had nothing to play. And
       independence is the property a ladder is made of: matches that inherit
       each other's run are not samples of the same thing. */
    try { if (typeof _freshRun === 'function') S.run = _freshRun(); } catch (e) {}
    try { delete S.pendingMatch; } catch (e) {}
    window._fkDiscardOk = true;""",
    '1 a fresh run per match')

# ── 2. the gate ─────────────────────────────────────────────────────
sub(DRV,
    u"""  /* ── the gate, and it runs on match one ────────────────────────── */
  const FLOOR = 0.45;
  function sanity(res) {
    if (!res || res.err) return {ok: false, why: (res && res.err) || 'no result'};
    if (res.stalled) return {ok: false, why: 'first match stalled: ' + res.stalled};
    /* THE DIAGNOSTIC DENIS NAMED, and it is visible in row one: a working
       player's total scales with the match it is in, because a higher target
       means a longer match means more banked. The broken run scored ~2000 at
       tier 0 and ~2000 at tier 7. */
    if (res.pOverTarget < FLOOR) return {ok: false,
      why: 'the player scored ' + res.pPts + ' against a target of ' + res.target +
           ' (' + Math.round(res.pOverTarget * 100) + '% of it, floor ' +
           Math.round(FLOOR * 100) + '%). A player that cannot approach the ' +
           'target is not playing the game, and a run on top of it would be ' +
           'precise and wrong. Fix the driver, not the floor.'};
    return {ok: true, pOverTarget: res.pOverTarget};
  }

  return {POLICIES, bankRule, policyByKey, playMatch, sanity, targetOf,
          extractWhy, until, sleep, tap, FLOOR};""",
    u"""  /* ── the gates ─────────────────────────────────────────────────── */

  /* PER MATCH: structural only. A performance bar here refuses a match the
     player simply lost - measured, bank500 scored 2900 of 7200 while the rival
     overshot to 8850, which is a result and not a broken driver. What a match
     must show is that it RAN: somebody reached the target, and the player
     banked at least once. A driver that never banks is broken; a driver that
     banks and loses is a driver. */
  function sanity(res) {
    if (!res || res.err) return {ok: false, why: (res && res.err) || 'no result'};
    if (res.stalled) return {ok: false, why: 'the match stalled: ' + res.stalled};
    if (!(res.banks > 0)) return {ok: false,
      why: 'the player banked nothing in a completed match - it is not playing'};
    if (!(res.winnerOverTarget >= 0.8 && res.winnerOverTarget <= 2.5))
      return {ok: false, why: 'nobody reached the target: winner had ' +
        Math.max(res.pPts, res.oPts) + ' against ' + res.target};
    return {ok: true, pOverTarget: res.pOverTarget};
  }

  /* THE ONE THAT PROTECTS A SIX-HOUR RUN, and it needs two matches because the
     defect is a failure to SCALE. The broken ladder scored ~2000 whatever it
     was asked for: 3400 against a 3800 target (a respectable 89%) and 3550
     against 12500. A floor on one match passes the first and would have to be
     set so high it refuses honest losses. Two targets a factor apart, and the
     totals have to move with them. */
  const TARGET_SPREAD = 2.5, TOTAL_SPREAD = 1.5;
  function sanityScale(lowRes, highRes) {
    const a = sanity(lowRes), b = sanity(highRes);
    if (!a.ok) return {ok: false, why: 'low-tier match: ' + a.why};
    if (!b.ok) return {ok: false, why: 'high-tier match: ' + b.why};
    const tRatio = highRes.target / lowRes.target;
    if (tRatio < TARGET_SPREAD) return {ok: false,
      why: 'the two tiers are only ' + tRatio.toFixed(2) + 'x apart in target; ' +
           'pick tiers at least ' + TARGET_SPREAD + 'x apart or this proves nothing'};
    const pRatio = lowRes.pPts ? (highRes.pPts / lowRes.pPts) : 0;
    if (pRatio < TOTAL_SPREAD) return {ok: false,
      why: 'the player scored ' + lowRes.pPts + ' against a target of ' +
           lowRes.target + ' and ' + highRes.pPts + ' against ' + highRes.target +
           ' - the target moved ' + tRatio.toFixed(1) + 'x and the total moved ' +
           pRatio.toFixed(2) + 'x. A player whose score does not scale with the ' +
           'match is not playing it, and a ladder on top of this would be ' +
           'precise and about a different quantity. Fix the driver, not the gate.'};
    return {ok: true, targetRatio: +tRatio.toFixed(2), totalRatio: +pRatio.toFixed(2)};
  }

  return {POLICIES, bankRule, policyByKey, playMatch, sanity, sanityScale,
          targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD};""",
    '2 the gate becomes a scaling test')

# ── 3. the probe checks the new gate on the real broken numbers ─────
sub(PRB,
    u"""/* ── 2. the gate would have refused the run that wasted an hour ────── */
out.gateOnBrokenRun = FDRV.sanity({ok: true, stalled: null, pPts: 3550,
                                   oPts: 12500, target: 12500,
                                   pOverTarget: 0.284});
out.gateOnHealthyRun = FDRV.sanity({ok: true, stalled: null, pPts: 12600,
                                    oPts: 9000, target: 12500,
                                    pOverTarget: 1.008});""",
    u"""/* ── 2. the gate, against the run that wasted an hour ───────────────
   Its OWN numbers: tier 0 scored 3400 against a 3800 target, tier 6 scored
   3550 against 12500. The per-match floor this replaces would have PASSED the
   tier-0 match at 89% - which is why the gate had to become a pair test. */
const brokenLow = {ok: true, stalled: null, pPts: 3400, oPts: 3800, target: 3800,
                   banks: 6, winnerOverTarget: 1.0, pOverTarget: 0.895};
const brokenHigh = {ok: true, stalled: null, pPts: 3550, oPts: 12500, target: 12500,
                    banks: 6, winnerOverTarget: 1.0, pOverTarget: 0.284};
out.gateOnBrokenRun = FDRV.sanityScale(brokenLow, brokenHigh);
out.perMatchWouldHavePassedTheLowOne = FDRV.sanity(brokenLow);
const healthyLow = {ok: true, stalled: null, pPts: 3600, oPts: 3900, target: 3800,
                    banks: 7, winnerOverTarget: 1.03, pOverTarget: 0.947};
const healthyHigh = {ok: true, stalled: null, pPts: 11800, oPts: 12600,
                     target: 12500, banks: 14, winnerOverTarget: 1.01,
                     pOverTarget: 0.944};
out.gateOnHealthyRun = FDRV.sanityScale(healthyLow, healthyHigh);""",
    '3a the probe uses the pair gate')

sub(PRB,
    u"""  theGateRefusesTheBrokenRun: out.gateOnBrokenRun.ok === false,
  andSaysWhy: /target/.test(out.gateOnBrokenRun.why || ''),
  theGatePassesAHealthyRun: out.gateOnHealthyRun.ok === true,""",
    u"""  theGateRefusesTheBrokenRun: out.gateOnBrokenRun.ok === false,
  andSaysWhy: /scale/.test(out.gateOnBrokenRun.why || ''),
  theGatePassesAHealthyRun: out.gateOnHealthyRun.ok === true,
  /* the reason it had to be a pair: the old per-match floor passes the broken
     run's low-tier match, because 3400 of 3800 looks fine on its own */
  aSingleMatchCannotSeeIt: out.perMatchWouldHavePassedTheLowOne.ok === true,
  /* and the real pair, played rather than supposed */
  theScalingGatePassesLive: !!out.livePair && out.livePair.gate.ok === true,""",
    '3b the verdict covers both')

sub(PRB,
    u"""const done = out.matches.filter(x => !x.err && !x.stalled);""",
    u"""/* ── 3b. and the pair the gate actually needs, played ───────────── */
const lowM = await FDRV.playMatch({policy: 'bank500', tier: 0, seat: 'boss',
                                   timeoutMs: 200000});
await FDRV.sleep(600);
const highM = await FDRV.playMatch({policy: 'bank500', tier: 7, seat: 'boss',
                                    timeoutMs: 240000});
out.livePair = (lowM && !lowM.err && highM && !highM.err)
  ? {low: lowM, high: highM, gate: FDRV.sanityScale(lowM, highM)} : null;

const done = out.matches.filter(x => !x.err && !x.stalled);""",
    '3c the live pair')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
