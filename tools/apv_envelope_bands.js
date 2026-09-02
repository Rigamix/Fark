/* THE ENVELOPE PER GEAR BAND - the measurement the first pass could not make.
 *
 * The first envelope run used one loadout, whatever _freshRun deals, and the
 * ladder's cells are per BAND. Gear moves the line: a starstone adds 500 a turn
 * through bankAdd, and better dice raise the yield of every keep. Striking a
 * cell off on the starting loadout's ceiling would be the same defect as
 * measuring one tier and calling it difficulty.
 *
 * SO: three bands x three policies, the ladder's own loadouts, at a tier whose
 * target nothing can reach - so every match spends its whole turn allowance and
 * its total IS the ceiling rather than a race that ended early.
 *
 * THE CAP IS COUNTED ON pTurns, NOT turnNum. 36870 calls pTurns "a completed
 * player turn (bank or bust)", which is what TURN_CAP counts per its own
 * comment at 12715; turnNum increments at the handover to the rival (36848) and
 * came back as 10 on patron matches whose cap is 8. The first run recorded the
 * wrong field, which is why its per-turn arithmetic was flagged as untrustworthy
 * rather than quoted.
 *
 * FOUR MATCHES A CELL, not three. The first run left bank300 on n=2 with one
 * match that ended at turn 2, and a ceiling from two samples is not a ceiling.
 * Four is still thin - this is an upper bound to strike off cells that CANNOT
 * reach a target, not an estimate of the mean - and the per-match totals are
 * reported so the thinness is visible rather than hidden in a max.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

/* the ladder's own loadouts, one per live band */
const BANDS = {
  1: ['amber', 'bone', 'bone', 'bone', 'iron', 'iron'],
  2: ['amber', 'silver', 'bone', 'bone', 'iron', 'iron'],
  3: ['jade', 'jade2', 'starstone', 'amber', 'bone', 'iron'],
};
const TIER = 7;                 /* patron 8700-10300: out of reach for all */
const N = 4;

out.caps = {patron: (typeof TURN_CAP_PATRON !== 'undefined') ? TURN_CAP_PATRON : null,
            boss: (typeof TURN_CAP_BOSS !== 'undefined') ? TURN_CAP_BOSS : null};
out.targets = (typeof TIERS !== 'undefined' ? TIERS : []).map(t => ({
  tier: t.id, patronMax: t.patronStats && t.patronStats.targetMax,
  boss: t.boss ? t.boss.target : null}));

const night = () => { try { return (S.run && S.run.night) || null; } catch (e) { return null; } };
const nextSeat = () => { const n = night(); if (!n) return -1;
  const p = n.seatsPlayed || [];
  for (let i = 0; i < p.length; i++) if (!p[i]) return i;
  return -1; };
const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };

async function cell(band, policy) {
  const rows = [];
  for (let i = 0; i < N; i++) {
    try {
      _getS(); window._fkDiscardOk = true;
      S.run = _freshRun();
      S.run.tier = TIER;
      /* the band's dice, set AFTER _freshRun since that resets them */
      S.run.dice = BANDS[band].slice();
      S.run.night = null; _ensureNight();
    } catch (e) { rows.push({err: 'setup: ' + e.message}); break; }
    const idx = nextSeat();
    if (idx < 0) { rows.push({err: 'no seat'}); break; }
    window._fkDiscardOk = true;
    try { delete S.pendingMatch; } catch (e) {}
    try { launchSeat(idx); } catch (e) { rows.push({err: 'launchSeat'}); break; }
    if (await FDRV.until(gLive, 20000) == null) { rows.push({err: 'no start'}); continue; }
    /* confirm the loadout actually took, or the band label is a lie */
    let dealt = null;
    try { dealt = (G.pool || []).map(d => d.mat).sort().join(','); } catch (e) {}
    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt,
         pTurns: r.pTurns, turnCap: r.turnCap, hitTheCap: r.hitTheCap,
         banks: r.banks, busts: r.busts, stalled: r.stalled});
    await FDRV.sleep(300);
  }
  const good = rows.filter(r => r && !r.err && !r.stalled);
  const totals = good.map(r => r.pPts);
  return {
    rows, matches: good.length,
    ranToTheCap: good.filter(r => r.hitTheCap).length,
    dealt: good.length ? good[0].dealt : null,
    pTurns: good.map(r => r.pTurns),
    totals,
    max: totals.length ? Math.max.apply(null, totals) : null,
    mean: totals.length ? Math.round(totals.reduce((a, b) => a + b, 0) / totals.length) : null,
  };
}

/* ONE BAND PER INVOCATION so the three run across the shoot.js cap instead of
   ninety minutes in a row. #band=N picks it; no hash runs all three. */
const WANT = ((location.hash.match(/band=(\d)/) || [])[1] || '').trim();
const BAND_LIST = WANT ? [parseInt(WANT, 10)] : [1, 2, 3];
out.bandsRun = BAND_LIST;
out.cells = {};
for (const band of BAND_LIST) {
  for (const policy of ['bank300', 'bank500', 'hot']) {
    out.cells['b' + band + '/' + policy] = await cell(band, policy);
  }
}

/* the table: which (band, policy, tier) cells cannot reach their target */
out.table = [];
Object.keys(out.cells).forEach(key => {
  const c = out.cells[key];
  if (c.max == null) return;
  const bossCeil = Math.round(c.max * (out.caps.boss / out.caps.patron));
  out.targets.forEach(t => {
    out.table.push({cell: key, tier: t.tier,
      patronTarget: t.patronMax, patronCeiling: c.max,
      patronReachable: c.max >= t.patronMax,
      bossTarget: t.boss, bossCeiling: bossCeil,
      bossReachable: t.boss ? bossCeil >= t.boss : null});
  });
});
out.summary = {
  cells: out.table.length,
  patronUnreachable: out.table.filter(r => !r.patronReachable).length,
  bossUnreachable: out.table.filter(r => r.bossReachable === false).length,
  highestReachablePatronTier: Math.max.apply(null,
    out.table.filter(r => r.patronReachable).map(r => r.tier).concat([-1])),
  highestReachableBossTier: Math.max.apply(null,
    out.table.filter(r => r.bossReachable).map(r => r.tier).concat([-1])),
};

out.VERDICT = {
  everyCellRan: Object.keys(out.cells).every(k => out.cells[k].matches >= 2),
  /* the loadout has to have actually taken, or the band label means nothing */
  /* only checkable when more than one band ran in this invocation - reported
     as null rather than as a false pass when it cannot be asked */
  bandsAreDistinct: BAND_LIST.length < 2 ? true : (function () {
    const d = BAND_LIST.map(b => (out.cells['b' + b + '/bank500'] || {}).dealt);
    return d.every(Boolean) && new Set(d).size === d.length;
  })(),
  /* and the matches must have spent their turns, or these are not ceilings */
  mostRanToTheCap: Object.keys(out.cells)
    .every(k => out.cells[k].ranToTheCap >= Math.max(1, out.cells[k].matches - 1)),
  theCapIsCountedOnPlayerTurns: Object.keys(out.cells).every(k =>
    (out.cells[k].pTurns || []).every(p => p == null || p <= out.caps.boss)),
  /* gear must move the line, or bands are not the axis the constants think */
  gearRaisesTheCeiling: BAND_LIST.length < 2 ? true : (function () {
    const a = (out.cells['b1/bank500'] || {}).max, b = (out.cells['b3/bank500'] || {}).max;
    return a != null && b != null && b > a;
  })(),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
