/* P950b: a snuff that takes a seat must record a FIRE.
 *
 * Focused, because the full state probe measured this as part of a seven-turn
 * run and the fix is one ordering change. The bug it closes: _lmSpend ran above
 * the loop that decides which seats are taken, so _lmEnd computed the outcome
 * while `hit` was still false and a snuff that worked recorded 'miss'.
 *
 * THE CHECK IS AGAINST THE MECHANIC, NOT THE FIELD. outcome is derived from
 * hit, so asserting outcome==='fire' when hit is true is an identity. What makes
 * it a test is that the rival's turn must independently show the seat gone -
 * published contains the lane, and the dealt seats do not.
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
try { G._laneMark = {}; } catch (e) {}
out.armed = _lmArm('_snuff', 2, 1);

const pts0 = G.pPts || 0;
for (let i = 0; i < 2; i++) {
  const r = await FXH.rollAndSettle({vals: SCORE.slice()});
  if (!r.ok) { try { clearInterval(_ff); } catch (e) {} return Object.assign(out, {err: 'roll ' + i + ': ' + r.why}); }
  try {
    ((G && G.pool) || []).filter(d => !d.committed).forEach(d => {
      if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el);
    });
  } catch (e) {}
}
const bb = document.getElementById('btnBank');
if (bb && !bb.classList.contains('disabled')) FXH.tap(bb);
out.banked = (await FXH.until(() => (G.pPts || 0) !== pts0, 60000)) != null;
out.landed = !!((_lmMap()[2] || {}).shownAt);

const dealt = await FXH.until(() => (G.oppDice || []).length > 0 &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);
out.rival = dealt == null ? null : {published: ((G._oSnuffLanes) || []).slice(),
                                    seats: (G.oppDice || []).map(d => d && d.lane)};
await FXH.until(() => !((_lmMap()[2] || {}).live), 60000);
const e = _lmMap()[2] || {};
out.mark = {live: !!e.live, hit: !!e.hit, outcome: e.outcome || null,
            endedAt: !!e.endedAt};
try { clearInterval(_ff); } catch (e) {}

out.VERDICT = {
  armedAndLanded: out.armed === true && out.banked === true && out.landed === true,
  theRivalPlayed: out.rival !== null,
  /* INDEPENDENT of the mark: did the snuff actually take seat 2? */
  theSeatWasActuallyTaken: !!(out.rival && out.rival.published.indexOf(2) >= 0 &&
                              out.rival.seats.indexOf(2) < 0),
  /* and only then is the recorded outcome meaningful */
  itRecordedAFire: out.mark.outcome === 'fire' && out.mark.hit === true,
  theMarkEnded: out.mark.live === false && out.mark.endedAt === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
