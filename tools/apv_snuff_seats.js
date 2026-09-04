/* P946 REWROTE THE SEAT CUT, SO THE SEAT CUT GETS DRIVEN.
 *
 * The crash fix is proven by the rival's turn completing at all. That says
 * nothing about whether a SNUFF still takes the right seat, and P946 changed
 * that line from one splice to an iterated descending one. Re-reading the new
 * code would run back through the same understanding that wrote it; this drives
 * the real rival turn and reads the seats it actually deals.
 *
 * WHAT MAKES THIS MORE THAN A COUNT. "One fewer die" passes on a version that
 * removes the WRONG seat, and the surviving lane numbers are the whole point of
 * the machinery - P521 exists because a loop indexed materials by its own
 * counter instead of the seat. So the assertion is on the surviving LANES, not
 * on how many are left.
 *
 * AND THE ARITHMETIC IDENTITY, because a check derived from the implementation
 * can agree with a bug: the lanes dealt must be exactly the full seat list with
 * the snuffed ones removed - computed here from the loadout size and the lanes
 * armed, never from anything the rival turn produced.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

/* drive one rival turn with `lanes` snuffed, and report the seats dealt */
async function turnWith(lanes) {
  /* WAIT FOR THE TABLE BACK BEFORE STARTING A TRIAL. Run 1 measured the first
     turn correctly and reported "no roll / never reached choosing" for the
     second, because it began arming while the rival still held the table. The
     system's own signal that the player may act is phase idle; a sleep would
     have been a guess about a turn whose length is the thing being changed. */
  const mine = await FXH.until(() => typeof G !== 'undefined' && G &&
    G.phase === 'idle' && !G._oppTurnActive && !G._endMatchFired, 120000);
  if (mine == null) return {err: 'the table never came back',
                            phase: (G || {}).phase, oppActive: !!(G || {})._oppTurnActive};
  try { G._laneMark = {}; G._oSnuffLanes = []; } catch (e) {}
  const armed = lanes.map(L => { try { return _lmArm('_snuff', L, 1); } catch (e) { return 'threw'; } });
  /* a mark is due on the turn it was stamped FOR: oppTurnCount+1 at arm time */
  const r = await FXH.rollAndSettle();
  if (!r.ok) return {err: 'no roll', why: r.why};
  try {
    const free = ((G && G.pool) || []).filter(d => !d.committed);
    free.forEach(d => { if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el); });
  } catch (e) {}
  const before = (G.pTurns || 0);
  try { endPTurn(); } catch (e) { return {err: 'endPTurn threw: ' + e.message}; }
  const got = await FXH.until(() => (G.phase === 'opp' || G._oppTurnActive) &&
    ((G.oppDice || []).length > 0), 120000);
  if (got == null) return {err: 'never dealt a rival row', armed,
                           phase: G.phase, pTurns: G.pTurns, before};
  /* G.oppDice IS THE FREE SEATS, NOT THE TURN'S SEATS. Run 2 read [2,3,5] for
     snuffs on 1 and 4 and lane 0 was missing too, which reads exactly like the
     splice taking a third seat. It is not: the poll fires on the first deal it
     SEES, and at _ffMult 0.05 the rival can already have kept a die and rolled
     again, and a kept die leaves the free list. Rather than race the roll
     counter - which is a local inside runOppTurn and not published - the check
     becomes an identity over the seats that exist at all: dealt plus held must
     be the full seat list minus the snuffed ones, whichever roll this lands on. */
  const dealt = (G.oppDice || []).map(d => (d && d.lane !== undefined) ? d.lane : null);
  const held = ((G._oppHeld) || []).map(d => (d && d.lane !== undefined) ? d.lane : null)
                 .filter(L => typeof L === 'number');
  const seats = dealt.concat(held).filter(L => typeof L === 'number')
                  .sort((a, b) => a - b);
  return {armed, dealt, held, seats, n: dealt.length,
          published: ((G._oSnuffLanes) || []).slice(),
          loadout: ((G.matchOppDice) || []).length};
}

/* the identity: what the seats MUST be, from the loadout and the arming */
const expect = (size, lanes) => {
  const all = []; for (let i = 0; i < size; i++) all.push(i);
  return all.filter(i => lanes.indexOf(i) < 0);
};

out.loadoutSize = ((G.matchOppDice) || []).length ||
                  (((G.rung || {}).dice) || []).length || 6;

out.one = await turnWith([2]);
out.two = await turnWith([1, 4]);
try { clearInterval(_ff); } catch (e) {}

const sz = out.loadoutSize;
const chk = (r, lanes) => {
  if (!r || r.err) return {ok: null, why: (r && r.err) || 'no result'};
  const want = expect(sz, lanes);
  return {ok: r.seats.join(',') === want.join(','), got: r.seats.join(','),
          want: want.join(','), dealt: r.dealt.join(','), held: r.held.join(','),
          n: r.seats.length, wantN: want.length,
          /* the snuffed seats must be absent from BOTH lists, which is the
             half a count can never check */
          noSnuffedSeatSurvives: lanes.every(L => r.seats.indexOf(L) < 0)};
};
out.oneCheck = chk(out.one, [2]);
out.twoCheck = chk(out.two, [1, 4]);

out.VERDICT = {
  /* the window contained the event, or the rest is about nothing */
  bothTurnsDealtARow: !out.one.err && !out.two.err,
  theMarksArmed: !out.one.err && !out.two.err &&
                 out.one.armed.every(x => x === true) &&
                 out.two.armed.every(x => x === true),
  /* ONE SNUFF takes seat 2 and the survivors keep their real numbers */
  oneSnuffTakesTheRightSeat: out.oneCheck.ok,
  /* TWO SNUFFS take BOTH - the case a single stored lane could not express,
     and the case P946's descending splice exists for */
  twoSnuffsTakeBothSeats: out.twoCheck.ok,
  neitherSnuffedSeatSurvives: out.oneCheck.noSnuffedSeatSurvives === true &&
                              out.twoCheck.noSnuffedSeatSurvives === true,
  /* and the published list is what the readers will see */
  publishedMatchesArmed: !out.two.err &&
    out.two.published.slice().sort().join(',') === '1,4',
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
