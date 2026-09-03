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
    /* CONFIRM THE LOADOUT AGAINST WHAT WAS ASKED FOR, not against the other
       bands. The first version read G.pool at the idle phase - before any dice
       are on the table - so it came back EMPTY every match, and the check that
       compared bands to each other short-circuited to true because only one
       band ran per invocation. A guard that cannot fail in the way it is
       actually run is not a guard.
       S.run.dice is readable now; the pool is read after the first roll below
       and both are reported. */
    const want = BANDS[band].slice().sort().join(',');
    let asked = null;
    try { asked = (S.run.dice || []).slice().sort().join(','); } catch (e) {}
    const loadoutTook = asked === want;
    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    /* and the pool, read AFTER the match has actually dealt dice */
    let dealt = null;
    try { dealt = (G.pool || []).map(d => d.mat).sort().join(','); } catch (e) {}
    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt, asked, want,
         loadoutTook,
         pTurns: r.pTurns, turnCap: r.turnCap, hitTheCap: r.hitTheCap,
         endReason: r.endReason, finalAnswerUsed: r.finalAnswerUsed,
         extraTurnsLeft: r.extraTurnsLeft,
         overran: (r.pTurns != null && r.turnCap) ? (r.pTurns > r.turnCap) : null,
         banks: r.banks, busts: r.busts, stalled: r.stalled});
    await FDRV.sleep(300);
  }
  const good = rows.filter(r => r && !r.err && !r.stalled);
  const totals = good.map(r => r.pPts);
  /* THE CEILING AT EXACTLY THE CAP, apart from the overrun ones. The cap is
     soft three ways and an envelope that mixes them is measuring a longer match
     than it claims - and the trailing-player final answer turn fires in EVERY
     match here, because an envelope is taken where the player cannot win. */
  const atCap = good.filter(r => r.pTurns != null && r.turnCap &&
                                 r.pTurns === r.turnCap);
  const over = good.filter(r => r.overran === true);
  const maxOf = a => a.length ? Math.max.apply(null, a.map(r => r.pPts)) : null;
  /* A CELL THAT DID NOT REACH THE CAP HAS NO CEILING TO REPORT. This was a
     field before and the table was printed over it: mostRanToTheCap came back
     false in both band runs and the 17/22/23 unreachable counts were computed
     anyway. It refuses now. The reason it failed is worth stating - the RIVAL
     reaches its target and ends the match long before the player's eighth turn,
     so tier 7 does not produce a capped match, it produces a short one. */
  const capped = good.filter(r => r.hitTheCap).length;
  const refusal = (good.length && capped < good.length)
    ? ('only ' + capped + ' of ' + good.length + ' matches reached the cap ' +
       '(pTurns ' + JSON.stringify(good.map(r => r.pTurns)) + ') - the rival ' +
       'ended them first, so these totals are "what the player scored before ' +
       'losing", not a ceiling')
    : null;
  return {
    rows, matches: good.length, refusal,
    loadoutTook: good.length ? good.every(r => r.loadoutTook) : null,
    asked: good.length ? good[0].asked : null,
    want: good.length ? good[0].want : null,
    /* the only quantity the short matches could support, reported so the next
       design chooses deliberately between normalising and stopping the rival */
    perTurn: good.length ? good.map(r => r.pTurns ? Math.round(r.pPts / r.pTurns) : null) : [],
    ranToTheCap: capped,
    exactlyAtCap: atCap.length, overran: over.length,
    endedEarly: good.length - atCap.length - over.length,
    endReasons: good.map(r => r.endReason),
    finalAnswerUsed: good.filter(r => r.finalAnswerUsed).length,
    dealt: good.length ? good[0].dealt : null,
    pTurns: good.map(r => r.pTurns),
    totals,
    /* the honest ceiling: exactly-at-cap only. maxAny is reported beside it so
       the inflation is visible rather than absorbed. */
    ceilingAtCap: maxOf(atCap),
    ceilingOverran: maxOf(over),
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
  /* skip a cell that refused - a table row built on a non-ceiling is worse
     than a missing row, because it looks like an answer */
  if (c.refusal) return;
  if (c.loadoutTook === false) return;
  /* THE TABLE USES THE AT-CAP CEILING, falling back to the overall max only
     when no match landed exactly on the cap - and saying which, because a
     pruning decision built on an overrun ceiling would strike off fewer cells
     than it should and look conservative while being wrong. */
  const ceil = (c.ceilingAtCap != null) ? c.ceilingAtCap : c.max;
  const ceilFrom = (c.ceilingAtCap != null) ? 'at-cap' : 'any';
  if (ceil == null) return;
  const bossCeil = Math.round(ceil * (out.caps.boss / out.caps.patron));
  out.targets.forEach(t => {
    out.table.push({cell: key, tier: t.tier, ceilFrom,
      patronTarget: t.patronMax, patronCeiling: ceil,
      patronReachable: ceil >= t.patronMax,
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
  /* the two that were vacuous or ignored last time */
  everyLoadoutTook: Object.keys(out.cells).every(k => out.cells[k].loadoutTook === true),
  noCellRefused: Object.keys(out.cells).every(k => !out.cells[k].refusal),
  /* the loadout has to have actually taken, or the band label means nothing */
  /* only checkable when more than one band ran in this invocation - reported
     as null rather than as a false pass when it cannot be asked */
  /* REPLACED, not repaired. Comparing bands to each other cannot be asked when
     one band runs per invocation, and short-circuiting to true made it vacuous
     in the configuration actually shipped. everyLoadoutTook above compares each
     cell to the loadout it ASKED FOR, which is answerable with one band. */
  /* and the matches must have spent their turns, or these are not ceilings */
  mostRanToTheCap: Object.keys(out.cells)
    .every(k => out.cells[k].ranToTheCap >= Math.max(1, out.cells[k].matches - 1)),
  /* the finding this patch exists for: an envelope taken where the player
     cannot win collects the trailing-player final answer turn every time, so
     if NOTHING overran, the soft cap is not doing what the code says */
  theSoftCapIsVisible: Object.keys(out.cells)
    .some(k => out.cells[k].overran > 0 || out.cells[k].finalAnswerUsed > 0),
  theCapIsCountedOnPlayerTurns: Object.keys(out.cells).every(k =>
    (out.cells[k].pTurns || []).every(p => p == null || p <= out.caps.boss)),
  /* gear must move the line, or bands are not the axis the constants think */

};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
