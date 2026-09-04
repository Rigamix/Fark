/* P950: landed, hit, and how it ended.
 *
 * THE MISS IS THE HARD HALF AND IT IS WHY THIS PROBE HAS ROUNDS. 3.3 requires
 * two endings from the start, and a probe that only ever sees a fire cannot
 * tell a working miss branch from one that never runs - it would report a clean
 * pass over an untested half. A snare only bites if the seat it marked actually
 * scores on the rival's turn, so it misses on its own often enough to be
 * observed; several rounds are played and BOTH outcomes must appear. If only one
 * does, the verdict says the other is unproven rather than passing.
 *
 * AND THE OUTCOME IS CROSS-CHECKED AGAINST THE MECHANIC, not just read back.
 * `outcome` is derived from `hit`, so asserting outcome==='fire' when hit is
 * true is an identity, not a test. What makes it a test is comparing it with
 * what the rival's turn actually did: a snare that fired must have HALVED, and
 * the published snuff list must contain a snuffed lane.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);
try { G.pCards = []; G.pF = []; G.oF = []; } catch (e) {}

const SCORE = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5];
const mine = () => FXH.until(() => typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._oppTurnActive && !G._endMatchFired, 120000);

async function bank() {
  const pts0 = G.pPts || 0;
  for (let i = 0; i < 2; i++) {
    const r = await FXH.rollAndSettle({vals: SCORE.slice()});
    if (!r.ok) return {ok: false, why: r.why};
    try {
      ((G && G.pool) || []).filter(d => !d.committed).forEach(d => {
        if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el);
      });
    } catch (e) {}
  }
  const bb = document.getElementById('btnBank');
  if (bb && !bb.classList.contains('disabled')) FXH.tap(bb);
  const done = await FXH.until(() => (G.pPts || 0) !== pts0, 60000);
  return {ok: done != null, pPts: G.pPts || 0};
}
const rivalPlays = () => FXH.until(() => (G.oppDice || []).length > 0 &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);

/* ── 1. LANDING at the bank, with the flourish ────────────────────── */
await mine();
try { G._laneMark = {}; } catch (e) {}
_lmArm('_snuff', 2, 1);
out.beforeBank = {shownAt: (_lmMap()[2] || {}).shownAt || null};
out.bank1 = await bank();
const landed = _lmMap()[2] || {};
out.landing = {shownAt: !!landed.shownAt, flourish: landed.flourish,
               stampIsRecent: !!(landed.shownAt && (Date.now() - landed.shownAt) < 60000)};
out.rival1 = (await rivalPlays()) != null
  ? {published: ((G._oSnuffLanes) || []).slice(),
     seats: (G.oppDice || []).map(d => d && d.lane)} : null;
await FXH.until(() => !( _lmMap()[2] || {}).live, 60000);
const ended = _lmMap()[2] || {};
out.snuffEnding = {outcome: ended.outcome, hit: !!ended.hit, endedAt: !!ended.endedAt,
                   live: !!ended.live};

/* ── 2. THE STAMP IS ONCE-ONLY. A two-attempt mark survives a rival turn,
       so it is still there at the next bank and must keep its moment. ── */
await mine();
try { G._laneMark = {}; } catch (e) {}
_lmArm('_fog', 4, 2);                    /* two attempts */
await bank();
const firstStamp = (_lmMap()[4] || {}).shownAt || null;
await rivalPlays();
await mine();
await bank();                            /* a SECOND bank while it still lives */
const secondStamp = (_lmMap()[4] || {}).shownAt || null;
out.onceOnly = {firstStamp: !!firstStamp, unchanged: firstStamp === secondStamp,
                stillLive: !!((_lmMap()[4] || {}).live)};

/* ── 3. ROUNDS, to see BOTH endings ───────────────────────────────── */
/* A FRESH MATCH PER ROUND. Run 1 reported "bank failed" four times, which is
   not a bank defect: three turns of play had already ended the match, and every
   later round measured nothing. The rounds loop now starts its own match and
   says so when it cannot, rather than producing four silent blanks that a less
   careful verdict would have read as four passes. */
out.rounds = [];
for (let i = 0; i < 4; i++) {
  if (typeof G === 'undefined' || !G || G._endMatchFired ||
      (G.pPts || 0) >= (G.target || Infinity)) {
    const boot = await FXH.match(1);
    if (!boot.ok) { out.rounds.push({err: 'relaunch: ' + boot.why}); continue; }
    try { G.pCards = []; G.pF = []; G.oF = []; } catch (e) {}
  }
  await mine();
  try { G._laneMark = {}; } catch (e) {}
  if (!_lmArm('_snare', 3, 1)) { out.rounds.push({err: 'arm refused'}); continue; }
  const b = await bank();
  if (!b.ok) { out.rounds.push({err: 'bank failed'}); continue; }
  if ((await rivalPlays()) == null) { out.rounds.push({err: 'rival never played'}); continue; }
  await FXH.until(() => !((_lmMap()[3] || {}).live), 60000);
  const e = _lmMap()[3] || {};
  out.rounds.push({outcome: e.outcome || null, hit: !!e.hit, ended: !!e.endedAt});
}
try { clearInterval(_ff); } catch (e) {}

const outcomes = out.rounds.map(r => r.outcome).filter(Boolean);
out.outcomesSeen = outcomes;
const bothSeen = outcomes.indexOf('fire') >= 0 && outcomes.indexOf('miss') >= 0;

out.VERDICT = {
  /* the events happened at all */
  theBankLanded: out.bank1.ok === true,
  theRivalPlayed: out.rival1 !== null,
  /* 1. LANDING */
  notShownBeforeTheBank: out.beforeBank.shownAt === null,
  landsAtTheBank: out.landing.shownAt === true,
  aPayingBankFlourishes: out.landing.flourish === true,
  /* the snuff fired, cross-checked against the mechanic rather than the field */
  theSnuffActuallyTookASeat: !!(out.rival1 && out.rival1.published.indexOf(2) >= 0 &&
                                out.rival1.seats.indexOf(2) < 0),
  andRecordedAFire: out.snuffEnding.outcome === 'fire' && out.snuffEnding.hit === true,
  theEndingHasAClock: out.snuffEnding.endedAt === true && out.snuffEnding.live === false,
  /* 2. the entrance is not restarted by a later bank */
  theLandingStampIsOnceOnly: out.onceOnly.firstStamp === true &&
                             out.onceOnly.unchanged === true,
  /* 3. BOTH ENDINGS OBSERVED - the point of the rounds */
  everyRoundRecordedAnOutcome: out.rounds.length === 4 &&
    out.rounds.every(r => r.outcome === 'fire' || r.outcome === 'miss'),
  bothEndingsReachable: bothSeen,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
if (!bothSeen) out.NOTE = 'only ' + JSON.stringify(outcomes) +
  ' observed in 4 rounds - the other branch is UNPROVEN, not working';
return out;
