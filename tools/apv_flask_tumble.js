/* Item 0 - does the flask reroll really have no tumble?
 *
 * WHY THIS IS MEASURED BEFORE IT IS BUILT. The claim is that
 * activateGrogsFlask never sets `d.roll`, so the value pops and §18's reroll
 * sheet decorates a jump cut. Reading the chain the other way suggests the
 * opposite: activateGrogsFlask calls _setDieVal, which calls reDrawDieFace,
 * which for a `_d3` die calls D3.roll(..., {dur:420}), which at 22398 calls
 * D3X._physQueue(d, d.result) whenever d.group === 'match'. That is the same
 * entry the ordinary roll uses, and _physStart is what assigns d.roll.
 *
 * Both readings are just reading. So: drive the real path and watch the real
 * field, with the pieces separated so a negative says WHICH link is broken
 * rather than only that something is.
 *
 *   A  the exact call the flask makes, on a real match die
 *   B  D3.roll directly, if A is silent - is the queue reached at all?
 *   C  _physQueue directly, if B is silent - is the queue itself the problem?
 *   D  the preconditions each of those depends on, reported either way
 *
 * THE POLL IS ON STATE, NOT THE CLOCK. _physQueue defers through a setTimeout
 * and then an async cannon load, and this harness renders at about one frame a
 * second, so a fixed wait would report whatever the scheduler felt like. It
 * polls for d.roll and reports how long it took, or that it gave up.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const sleep = ms => new Promise(res => setTimeout(res, ms));
const rolling = () => D3X.dice.filter(d => d.match && d.roll).length;
const waitForRoll = async (ms) => {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    if (rolling() > 0) return Date.now() - t0;
    await sleep(50);
  }
  return null;
};
/* HOW LONG THE TUMBLE LASTS, which is the question §18's sheet actually needs
   answering. Wall-clock in this harness is not the phone's - the 3D layer runs
   at about 1fps here - so the playback length is read off the SOLUTION rather
   than timed: sol.frames at PHYS.dt each is what the die will play, on any
   machine. The wall-clock number is reported beside it as a sanity check, not
   as the answer. */
const plannedTumbleMs = () => {
  const d = D3X.dice.filter(x => x.match && x.roll)[0];
  if (!d || !d.roll || !d.roll.sol || !d.roll.sol.frames) return null;
  return Math.round(d.roll.sol.frames.length * (D3X.PHYS.dt || 0) * 1000);
};

/* preconditions, reported whatever happens - a null below is only readable
   next to these */
const pool = (typeof G !== 'undefined' && G && G.pool) ? G.pool : [];
const free = pool.filter(d => !d.committed && !d._frozen && d.el);
out.preconditions = {
  physOn: !!(D3X.PHYS && D3X.PHYS.on),
  d3xReady: !!D3X.ready,
  d3xFail: !!D3X.fail,
  cannonLoaded: !!window.CANNON,
  freeDice: free.length,
  firstDieHasD3: free.length ? !!free[0].el._d3 : null,
  firstDieGroup: (free.length && free[0].el._d3) ? free[0].el._d3.group : null,
  alreadyRolling: rolling(),
};
if (!free.length) return Object.assign(out, {err: 'no free dice to reroll'});

/* settle first: a die still in flight would answer the question for us */
await FXH.until(() => rolling() === 0, 20000);
out.settledBefore = rolling();

/* ── A. the call the flask actually makes ──────────────────────────── */
const dA = free[0];
const valBefore = dA.val;
let threwA = null;
try {
  _setDieVal(dA, (typeof rollFaceExclude === 'function')
    ? rollFaceExclude(dA.mat, dA.val, dA)
    : (dA.val % 6) + 1);
} catch (e) { threwA = e.message; }
const msToTumbleA = await waitForRoll(6000);
out.setDieVal = {
  threw: threwA,
  valueChanged: dA.val !== valBefore,
  msToTumble: msToTumbleA,
  diceRollingNow: rolling(),
  /* the sheet gives the whole card-reroll 400ms and puts the value change at
     +210. This is how long the die is actually in the air. */
  plannedTumbleMs: plannedTumbleMs(),
};

/* ── B. D3.roll directly, only if A was silent ─────────────────────── */
if (out.setDieVal.msToTumble === null) {
  await FXH.until(() => rolling() === 0, 8000);
  let threwB = null;
  try { D3.roll(dA.el._d3, (dA.val % 6) + 1, {dur: 420, homeX: 0, homeY: 0}); }
  catch (e) { threwB = e.message; }
  out.d3RollDirect = {threw: threwB, msToTumble: await waitForRoll(6000)};

  /* ── C. and the queue itself, only if B was silent ──────────────── */
  if (out.d3RollDirect.msToTumble === null) {
    await FXH.until(() => rolling() === 0, 8000);
    let threwC = null;
    try { D3X._physQueue(dA.el._d3, dA.val); } catch (e) { threwC = e.message; }
    out.physQueueDirect = {threw: threwC, msToTumble: await waitForRoll(6000)};
  }
}

/* ── and the reverse control: does an ORDINARY roll set d.roll here? ──
   If it does not, this probe cannot see a tumble at all and every null above
   means nothing. */
await FXH.until(() => rolling() === 0, 10000);
let ctrlThrew = null;
try {
  const btn = document.getElementById('btnRoll');
  if (btn && !btn.disabled) FXH.tap(btn);
  else ctrlThrew = 'roll button unavailable';
} catch (e) { ctrlThrew = e.message; }
const ctrlMs = await waitForRoll(12000);
out.ordinaryRollControl = {why: ctrlThrew, msToTumble: ctrlMs,
                           plannedTumbleMs: plannedTumbleMs()};

out.VERDICT = {
  /* the control decides whether any null above is readable */
  theProbeCanSeeATumble: out.ordinaryRollControl.msToTumble !== null,
  /* and the claim under test */
  theFlaskPathTumbles: out.setDieVal.msToTumble !== null,
  theValueActuallyChanged: out.setDieVal.valueChanged === true,
  nothingThrew: !out.setDieVal.threw,
  /* and the tumble must be a real flight, not a one-frame twitch - otherwise
     "it tumbles" would be true and useless */
  theTumbleIsARealFlight: out.setDieVal.plannedTumbleMs > 200,
  /* the flask's reroll and an ordinary roll should be the same flight: it is
     the same entry point, and a difference would mean the card gets its own
     physics by accident */
  itIsTheSameFlightAsAnOrdinaryRoll:
    out.ordinaryRollControl.plannedTumbleMs > 200 &&
    Math.abs(out.setDieVal.plannedTumbleMs -
             out.ordinaryRollControl.plannedTumbleMs) <
      out.ordinaryRollControl.plannedTumbleMs * 0.5,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
