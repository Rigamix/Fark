/* THE ENVELOPE: can any policy reach these targets inside the turn cap?
 *
 * The hard cell returned 0 from 10 and I could not say whether that was the
 * driver or the game. It is neither - it is arithmetic. TURN_CAP_PATRON is 8
 * and TURN_CAP_BOSS is 10 (12715-6), and the comment there is load-bearing:
 * "banked turns per side; bank AND bust both count". The resource is eight
 * ATTEMPTS, so the most a policy can put on the board is eight times whatever
 * it banks per attempt - busts included at zero.
 *
 * THAT IS A CALCULATION, AND IT COSTS AN HOUR OF BROWSER TIME TO LEARN BY
 * MEASUREMENT. Any (tier, band, policy) cell whose ceiling sits below its
 * target is pre-determined: it returns 0% by construction and tells you nothing
 * about difficulty. Running those cells in the ladder would produce precise,
 * confident zeros.
 *
 * SO THE PER-TURN YIELD IS MEASURED AT A TIER WHOSE TARGET CANNOT BE REACHED.
 * At tier 7 the patron target is 8700-10300; if the envelope is anywhere near
 * the ~3450 the last run suggested, every match runs to the cap and its total
 * IS the envelope rather than a race that ended early. Three matches a policy,
 * eight turns each, gives 24 attempts a policy - enough for a ceiling, which is
 * what the question needs, without pretending to be a distribution.
 *
 * AND THE TARGETS COME FROM THE CODE, NOT FROM THE COMMENTS BESIDE THEM. TIERS
 * annotates its bosses "Grog @ 4000 ... Ambrose @ 28000"; RUNGS says 3700 and
 * 12500. The comments are stale by more than a factor of two at the top, and an
 * envelope table built on them would condemn cells that are actually reachable.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

/* ── the real targets, read off the live objects ─────────────────── */
out.caps = {patron: (typeof TURN_CAP_PATRON !== 'undefined') ? TURN_CAP_PATRON : null,
            boss: (typeof TURN_CAP_BOSS !== 'undefined') ? TURN_CAP_BOSS : null};
out.targets = (typeof TIERS !== 'undefined' ? TIERS : []).map(t => ({
  tier: t.id, name: t.name,
  patronMin: t.patronStats && t.patronStats.targetMin,
  patronMax: t.patronStats && t.patronStats.targetMax,
  boss: t.boss ? t.boss.target : null,
  bossName: t.boss ? t.boss.name : null,
}));

/* ── the per-turn yield, measured where the target cannot be met ─── */
const night = () => { try { return (S.run && S.run.night) || null; } catch (e) { return null; } };
const nextSeat = () => { const n = night(); if (!n) return -1;
  const p = n.seatsPlayed || [];
  for (let i = 0; i < p.length; i++) if (!p[i]) return i;
  return -1; };
const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };

async function envelopeFor(policy, tier, n) {
  const rows = [];
  try { _getS(); window._fkDiscardOk = true;
        S.run = _freshRun(); S.run.tier = tier; S.run.night = null; _ensureNight(); }
  catch (e) { return {err: 'setup: ' + e.message, rows}; }
  for (let i = 0; i < n; i++) {
    let idx = nextSeat();
    if (idx < 0) { try { S.run.night = null; _ensureNight(); } catch (e) {} idx = nextSeat(); }
    if (idx < 0) { rows.push({err: 'no seat'}); break; }
    window._fkDiscardOk = true;
    try { delete S.pendingMatch; } catch (e) {}
    try { launchSeat(idx); } catch (e) { rows.push({err: 'launchSeat'}); break; }
    if (await FDRV.until(gLive, 20000) == null) { rows.push({err: 'no start'}); break; }
    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    rows.push(r && r.err ? {err: r.err}
      : {target: r.target, pPts: r.pPts, banks: r.banks, busts: r.busts,
         turnsUsed: r.turnsUsed, turnCap: r.turnCap, hitTheCap: r.hitTheCap,
         bankAmounts: r.bankAmounts, stalled: r.stalled});
    await FDRV.sleep(300);
  }
  return {rows};
}

const TIER = 7;                     /* target 8700-10300: unreachable, so capped */
out.measured = {};
for (const key of ['bank300', 'bank500', 'hot']) {
  const e = await envelopeFor(key, TIER, 3);
  const good = e.rows.filter(r => r && !r.err && !r.stalled);
  const amounts = good.reduce((a, r) => a.concat(r.bankAmounts || []), []);
  const totals = good.map(r => r.pPts);
  out.measured[key] = {
    matches: good.length, err: e.err || null,
    hitTheCap: good.filter(r => r.hitTheCap).length,
    turnsUsed: good.map(r => r.turnsUsed),
    totals,
    perTurnBanks: amounts,
    meanBank: amounts.length
      ? Math.round(amounts.reduce((a, b) => a + b, 0) / amounts.length) : null,
    maxBank: amounts.length ? Math.max.apply(null, amounts) : null,
    meanTotal: totals.length
      ? Math.round(totals.reduce((a, b) => a + b, 0) / totals.length) : null,
    maxTotal: totals.length ? Math.max.apply(null, totals) : null,
  };
}

/* ── the table: which cells are pre-determined ───────────────────── */
out.envelopeTable = [];
for (const key of Object.keys(out.measured)) {
  const mm = out.measured[key];
  if (!mm.meanTotal) continue;
  /* the ceiling a match of THIS length can hold, scaled from the measured
     8-turn patron total to the boss cap of 10 */
  const perTurn = mm.meanTotal / out.caps.patron;
  const bestTurn = mm.maxTotal / out.caps.patron;
  out.targets.forEach(t => {
    out.envelopeTable.push({
      policy: key, tier: t.tier,
      patronTarget: t.patronMax,
      patronCeilingMean: Math.round(perTurn * out.caps.patron),
      patronCeilingBest: Math.round(bestTurn * out.caps.patron),
      patronReachable: (bestTurn * out.caps.patron) >= t.patronMax,
      bossTarget: t.boss,
      bossCeilingBest: Math.round(bestTurn * out.caps.boss),
      bossReachable: t.boss ? (bestTurn * out.caps.boss) >= t.boss : null,
    });
  });
}
const rows = out.envelopeTable;
out.summary = {
  cells: rows.length,
  patronPreDetermined: rows.filter(r => !r.patronReachable).length,
  bossPreDetermined: rows.filter(r => r.bossReachable === false).length,
};

out.VERDICT = {
  theCapsAreWhatTheySay: out.caps.patron === 8 && out.caps.boss === 10,
  theTargetsCameFromCode: out.targets.length === 8 && out.targets[7].boss > 0,
  /* the comments beside TIERS are stale and this says by how much */
  bossCommentsAreStale: out.targets[7].boss < 28000,
  everyPolicyMeasured: Object.keys(out.measured).every(k => out.measured[k].matches > 0),
  /* the matches used for the envelope must actually have hit the cap, or they
     are not envelopes - they are races that ended early */
  theyRanToTheCap: Object.keys(out.measured)
    .every(k => out.measured[k].hitTheCap === out.measured[k].matches),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
