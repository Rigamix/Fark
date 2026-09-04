/* WHICH ENTRY POINTS DEAL THE LOADOUT THE CALLER ASKED FOR?
 *
 * apv_boss_flat found G.matchDice all-bone at the patron seat and correct at
 * boss - the opposite of the hypothesis, and it inverts the ladder result: the
 * ladder's patron arm calls launchPatronMatch, so its 22% may not be a band-2
 * number at all. Before that is claimed, three entry points, twice each,
 * because a single reading of a state this surprising is not a finding.
 *
 * launchSeat is included because the envelope work used it and its dealt
 * loadout came back correct - so if the two patron paths disagree, that
 * difference is the whole story.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {rounds: []};
const boot = await FXH.match(1);
if (!boot.ok) return {err: 'boot: ' + boot.why};
const WANT = ['amber','silver','bone','bone','iron','iron'];
const want = WANT.slice().sort().join(',');

const nextSeat = () => { try { const n = S.run && S.run.night; if (!n) return -1;
  const p = n.seatsPlayed || []; for (let i=0;i<p.length;i++) if (!p[i]) return i; return -1; }
  catch (e) { return -1; } };

async function one(how, tier) {
  try {
    _getS(); window._fkDiscardOk = true;
    S.run = _freshRun(); S.run.tier = tier; S.run.dice = WANT.slice();
    S.run._bossSeen = {drunkard:1,peasant:1,commoner:1,merchant:1,soldier:1,knight:1,noble:1,bishop:1};
    S.run.night = null;
    try { delete S.pendingMatch; } catch (e) {}
    if (how === 'launchSeat') { try { _ensureNight(); } catch (e) {} }
  } catch (e) { return {how, err: 'setup: ' + e.message}; }
  /* WAIT FOR A NEW G, BY OBJECT IDENTITY. The first version waited on
     "idle, not ended, pTurns 0" - which the PREVIOUS match's G already
     satisfies, because it was started moments earlier and has not been played.
     launchBossMatch defers through setTimeout(...,80), so the wait returned
     instantly on stale state and every reading was shifted by one launch:
     "launchPatronMatch" reported rung MABEL isBoss true, and "launchBossMatch"
     reported rung PATRON. That produced a false finding - patron all-bone -
     which is retracted. Identity is the only signal that cannot be satisfied by
     the match already on screen. */
  const prevG = (typeof G !== 'undefined') ? G : null;
  try {
    if (how === 'launchPatronMatch') launchPatronMatch();
    else if (how === 'launchBossMatch') launchBossMatch();
    else { const i = nextSeat(); if (i < 0) return {how, err: 'no seat'}; launchSeat(i); }
  } catch (e) { return {how, err: 'launch: ' + e.message}; }
  const live = await FXH.until(() => typeof G !== 'undefined' && G && G !== prevG &&
    G.phase === 'idle' && !G._endMatchFired && (G.pTurns||0) === 0, 20000);
  if (live == null) return {how, err: 'never started (no new G)'};
  const md = (G.matchDice||[]).slice().sort().join(',');
  return {how, tier, matchDice: md, correct: md === want,
          runDice: ((S.run&&S.run.dice)||[]).slice().sort().join(','),
          rung: (G.rung&&G.rung.name)||null, isBoss: !!G._isBoss, target: G.target};
}

for (let round = 0; round < 2; round++) {
  const r = {};
  for (const how of ['launchPatronMatch', 'launchSeat', 'launchBossMatch']) {
    r[how] = await one(how, 3);
    await new Promise(res => setTimeout(res, 400));
  }
  out.rounds.push(r);
}

const all = out.rounds;
const ok = (how) => all.every(r => r[how] && r[how].correct === true);
const bad = (how) => all.every(r => r[how] && r[how].correct === false);
out.VERDICT = {
  everyLaunchStarted: all.every(r => Object.values(r).every(x => !x.err)),
  /* THE PROBE READ THE SEAT IT ASKED FOR - without this the readings can be
     shifted by one launch and every row below is about the wrong match */
  eachLaunchLandedOnItsOwnSeat: all.every(r =>
    r.launchBossMatch && r.launchBossMatch.isBoss === true &&
    r.launchPatronMatch && r.launchPatronMatch.isBoss === false &&
    r.launchSeat && r.launchSeat.isBoss === false),
  bossDealsTheLoadout: ok('launchBossMatch'),
  launchSeatDealsTheLoadout: ok('launchSeat'),
  /* THE FINDING, if it holds twice */
  launchPatronMatchDoesNot: bad('launchPatronMatch'),
  /* and the run config was never disturbed - so it is the launch, not the setup */
  runDiceIntactThroughout: all.every(r => Object.values(r).every(x => x.err || x.runDice === want)),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
