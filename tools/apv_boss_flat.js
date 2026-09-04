/* WHY IS BOSS FLAT ZERO AT EVERY TIER?
 *
 * THE FLATNESS IS THE TELL. Boss came back 0 wins in 30 across tiers 0-7.
 * Difficulty scales with tier; a result that does not move with tier is not a
 * difficulty result. Patron moved (45%, 12%, 57%, 0, 0, 17%, 0, 0 - noisy but
 * moving); boss did not move at all.
 *
 * AND THE SCORES SAY THE SAME THING. The boss losses read 827 v 11823, 50 v
 * 11550, 1500 v 3850. Patron matches ran 2650-8050. That is not a strong rival,
 * it is a player scoring almost nothing - which would be flat across tiers
 * exactly as observed.
 *
 * SO: IS THE PLAYER DEALT THE LOADOUT AT BOSS? ladder_band sets S.run.dice and
 * then reports the value it SET, never what reached the table - which is P918's
 * defect exactly, a loadout check reading the config instead of the dice. Both
 * seats are launched the same way here and compared on what the table actually
 * holds.
 *
 * THE SECOND ANOMALY IS ON THE SAME SEAT, so it is treated as one hypothesis
 * rather than two: seven boss stalls against patron's one, all at
 * phase=choosing turn=1. The dice are checked for the onclick the driver waits
 * on, because a die with no handler is a match that stalls exactly there.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

/* BOOT THE SAME WAY EVERY OTHER PROBE DOES. Waiting on `S` alone returned
   "no boot": S does not exist until a run is started, and FXH.match is what
   starts one. The probe then re-launches each seat itself. */
const boot = await FXH.match(1);
if (!boot.ok) return {err: 'boot: ' + boot.why, detail: boot};

const WANT = ['amber', 'silver', 'bone', 'bone', 'iron', 'iron'];

async function trySeat(seat, tier) {
  try {
    _getS(); window._fkDiscardOk = true;
    S.run = _freshRun();
    S.run.tier = tier;
    S.run.dice = WANT.slice();
    S.run._bossSeen = {drunkard:1, peasant:1, commoner:1, merchant:1,
                       soldier:1, knight:1, noble:1, bishop:1};
    if (seat === 'patron') { S.run.night = null; }
    try { delete S.pendingMatch; } catch (e) {}
  } catch (e) { return {err: 'setup: ' + e.message}; }

  const askedAtLaunch = (S.run.dice || []).slice();
  try {
    if (seat === 'patron') launchPatronMatch(); else launchBossMatch();
  } catch (e) { return {err: 'launch: ' + e.message}; }

  const live = await FXH.until(() => typeof G !== 'undefined' && G &&
    G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0, 20000);
  if (live == null) return {err: 'never started'};

  /* WHAT THE TABLE HOLDS, not what was asked for */
  const matchDice = (G.matchDice || []).slice();
  const runDiceAfter = ((S.run && S.run.dice) || []).slice();

  /* roll once and read the pool */
  try { document.getElementById('btnRoll').click(); } catch (e) {}
  await FXH.until(() => G._endMatchFired || (G.phase === 'choosing' &&
    (G.pool || []).length > 0), 12000);
  const pool = (G.pool || []);
  const poolMats = pool.map(d => d.mat);
  const clickable = pool.filter(d => d.el && d.el.onclick).length;
  let best = null;
  try {
    const fr = pool.filter(d => !d.committed);
    const r = scoreRoll(fr.map(d => d.val), [], 0, {}, fr.map(d => d.mat));
    best = r ? r.total : null;
  } catch (e) {}

  return {
    seat, tier,
    askedAtLaunch: askedAtLaunch.slice().sort().join(','),
    runDiceAfter: runDiceAfter.slice().sort().join(','),
    matchDice: matchDice.slice().sort().join(','),
    poolMats: poolMats.slice().sort().join(','),
    poolSize: pool.length,
    clickable,
    firstRollScore: best,
    target: G.target,
    rung: (G.rung && G.rung.name) || null,
    isBoss: !!G._isBoss,
    numDice: G.numDice,
  };
}

out.patron = await trySeat('patron', 3);
out.boss = await trySeat('boss', 3);

const want = WANT.slice().sort().join(',');
const p = out.patron, b = out.boss;
out.VERDICT = {
  bothSeatsStarted: !p.err && !b.err,
  /* THE HYPOTHESIS: is the loadout on the table at boss? */
  patronGotTheLoadout: p.matchDice === want,
  bossGotTheLoadout: b.matchDice === want,
  patronPoolMatches: p.poolMats === want,
  bossPoolMatches: b.poolMats === want,
  /* the stall candidate: dice the driver can actually click */
  patronDiceClickable: p.clickable > 0,
  bossDiceClickable: b.clickable > 0,
  /* and the seats must differ somewhere, or this probe found nothing */
  theSeatsDifferSomewhere: JSON.stringify({d: p.matchDice, c: p.clickable, n: p.poolSize}) !==
                           JSON.stringify({d: b.matchDice, c: b.clickable, n: b.poolSize}),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
