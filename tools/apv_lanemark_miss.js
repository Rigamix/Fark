/* THE MISS BRANCH, FORCED - because three rounds of snare all FIRED.
 *
 * The state probe reported ["fire","fire","fire"] and said so: the miss is
 * UNPROVEN, not working. 3.3 is a ruling and P951 built a separate ending for
 * it, so shipping that branch on the strength of hand-built state would be
 * exactly the wrong-expectation shape - a check that passes because the probe
 * wrote the state it then read back.
 *
 * FORCING IT WITHOUT FAKING IT: a snare only bites the seat it marked, so a
 * mark on a lane the rival does not deal cannot land. Trimming the rival's
 * loadout to five leaves lanes 0-4, and a snare on lane 5 comes DUE, finds no
 * seat, and misses - which is a real path (3.2: a due mark that takes nothing
 * has missed, and a miss costs an attempt exactly as a hit does).
 *
 * The control is the same run's fire, on a lane that does exist, so a probe
 * that simply broke the mechanic would fail it.
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
async function bankTurn() {
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
  return {ok: (await FXH.until(() => (G.pPts || 0) !== pts0, 60000)) != null};
}
const rivalPlays = () => FXH.until(() => (G.oppDice || []).length > 0 &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);

/* THE RIVAL PLAYS FIVE SEATS, so lane 5 is a seat that does not exist */
out.loadoutBefore = ((G.matchOppDice) || []).length;
try { G.matchOppDice = (G.matchOppDice || []).slice(0, 5); } catch (e) {}
out.loadoutAfter = ((G.matchOppDice) || []).length;

await mine();
try { G._laneMark = {}; } catch (e) {}
out.armedMiss = _lmArm('_snare', 5, 1);   /* a lane the rival will not deal */
out.armedFire = _lmArm('_snuff', 1, 1);   /* the control, on a lane that exists */
out.bank = await bankTurn();
out.dealt = (await rivalPlays()) != null
  ? {seats: (G.oppDice || []).map(d => d && d.lane),
     published: ((G._oSnuffLanes) || []).slice()} : null;
await FXH.until(() => !((_lmMap()[5] || {}).live) && !((_lmMap()[1] || {}).live), 90000);
const miss = _lmMap()[5] || {}, fire = _lmMap()[1] || {};
out.miss = {outcome: miss.outcome || null, hit: !!miss.hit, ended: !!miss.endedAt};
out.fire = {outcome: fire.outcome || null, hit: !!fire.hit, ended: !!fire.endedAt};

/* AND THE TWO RENDER DIFFERENTLY, from state the GAME produced */
const SR = document.getElementById('screen-match').getBoundingClientRect();
try { miss.endedAt = Date.now() - 200; fire.endedAt = Date.now() - 200; } catch (e) {}
const plan = D3X._seatPlan(SR) || [];
out.plan = plan.map(g => ({style: g.style, col: g.col, am: +g.am.toFixed(3)}));
try { clearInterval(_ff); } catch (e) {}

out.VERDICT = {
  theLoadoutWasTrimmed: out.loadoutAfter === 5 && out.loadoutBefore === 6,
  bothArmed: out.armedMiss === true && out.armedFire === true,
  theBankLanded: out.bank.ok === true,
  theRivalPlayed: out.dealt !== null,
  /* the forced condition actually held: lane 5 was never dealt */
  laneFiveWasNeverDealt: !!(out.dealt && out.dealt.seats.indexOf(5) < 0),
  /* THE MISS - produced by the game, not written by the probe */
  aDueMarkThatTookNothingMissed: out.miss.outcome === 'miss' &&
                                 out.miss.hit === false && out.miss.ended === true,
  /* THE CONTROL - the same run still fires on a lane that exists, so this is
     not just a broken mechanic reporting misses */
  theControlStillFired: out.fire.outcome === 'fire' && out.fire.hit === true,
  andTheSeatWasReallyTaken: !!(out.dealt && out.dealt.published.indexOf(1) >= 0),
  /* and the two endings do not render the same */
  theEndingsRenderDifferently: out.plan.length === 2 &&
    out.plan[0].am !== out.plan[1].am,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
