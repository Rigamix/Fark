/* STEP 9's REMAINDER, ASKED BACKWARDS: can the thing be SEEN before it is built?
 *
 * The brief says "lane marks painted from _lmArm state, ARM-TO-FIRE, both
 * sides". A mark is armed on the player's turn and fires on the rival's. So
 * the rival-seat half of "both sides" is only paintable if a rival die is on
 * the table during the arm window - and 37714 does clearRow('oppDiceRow') and
 * G.oppDice=[] at the end of every rival turn, which says it is not.
 *
 * That is the whole reason this runs first. Building the paint and then
 * discovering the surface is empty for the entire window is the shape that has
 * cost this project three times: a feature that works on its one built path
 * and is invisible on every other way in. The census is cheap; the patch is
 * not.
 *
 * WHAT ELSE PRODUCES A ZERO HERE, named before it is read: D3X not running
 * under the harness (then no mark of any kind paints and this measures the
 * probe); dice present but obj.visible false; records present but .match
 * false - _markDice requires match && obj.visible && chip, so a die failing
 * any of the three is invisible to the paint pass while being perfectly
 * present in D3X.dice. All three are reported separately from the count.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

/* THE RIVAL TURN AT 1fps IS THE PROBE'S REAL DEADLINE, not the game's. Run 2
   waited 40s for phase=opp and got null, which reads exactly like "the rival
   turn never happens" and is not that. ladder_band drives boss matches to
   completion with this knob and the driver, which does not set it, stalls at
   phase=opp - so the knob is the difference between an engine that finishes a
   rival turn and one that does not. Re-asserted on an interval because the
   turn machinery rewrites it. */
const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

/* WHERE IT GOT TO, not just whether it arrived. A null wait that cannot say
   which phases it saw sends the search to the wrong place. */
const trace = [];
const _tr = setInterval(() => {
  try {
    const ph = (typeof G !== 'undefined' && G) ? G.phase : null;
    const oc = (document.getElementById('oppDiceRow') || {children: []}).children.length;
    const k = ph + '/' + oc;
    if (trace[trace.length - 1] !== k) trace.push(k);
  } catch (e) {}
}, 250);

/* THE INSTRUMENT MUST BE ABLE TO SEE. If D3X is not running, every census
   below reads zero for a reason that has nothing to do with the question. */
/* D3X.ready IS THE WRONG TEST AND THE FIRST RUN PROVED IT: ready came back
   false while D3X.dice held six records, all match+visible+chip, i.e. all
   paintable. `ready` is about the renderer being up; the census asks whether
   there are RECORDS for the mark pass to walk. Gating on ready would have
   failed this probe on every run for a reason unrelated to the question -
   a check that fails on correct code. */
out.instrument = {
  d3xReady: !!(window.D3X && D3X.ready),
  physOn: !!(window.D3X && D3X.PHYS && D3X.PHYS.on),
  diceRecords: (window.D3X && D3X.dice || []).length,
  hasMarkPass: typeof D3X._markDice === 'function' && !!(D3X.MARKS || []).length,
};

const rowOf = (d) => {
  try {
    const e = d.chip && d.chip.closest &&
      d.chip.closest('#playerDiceRow,#keptRow,#keptTray,#oppDiceRow');
    return e ? e.id : null;
  } catch (e) { return null; }
};

/* one census: every D3X record, split by row, and by the three conditions
   _markDice actually applies. A record that fails one of them is present and
   unpaintable, which is a different finding from absent. */
function census(tag) {
  const ds = (window.D3X && D3X.dice) || [];
  const rows = {};
  let paintable = 0;
  ds.forEach(d => {
    const r = rowOf(d) || '(detached)';
    const k = rows[r] || (rows[r] = {n: 0, match: 0, visible: 0, chip: 0, paintable: 0});
    k.n++;
    if (d.match) k.match++;
    if (d.obj && d.obj.visible) k.visible++;
    if (d.chip) k.chip++;
    if (d.match && d.obj && d.obj.visible && d.chip) { k.paintable++; paintable++; }
  });
  return {
    tag, phase: (typeof G !== 'undefined' && G) ? G.phase : null,
    records: ds.length, paintable, rows,
    oppRowChildren: (document.getElementById('oppDiceRow') || {children: []}).children.length,
    oppDice: ((typeof G !== 'undefined' && G && G.oppDice) || []).length,
    liveMarks: (typeof _lmLive === 'function') ? _lmLive().length : null,
  };
}

/* ── the arm window: the player's turn, with a mark armed ─────────── */
const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice'});

out.beforeArm = census('player turn, nothing armed');

let armed = null;
try { G._laneMark = {}; armed = _lmArm('_fog', 0, 1); } catch (e) { armed = 'threw: ' + e.message; }
out.armed = armed;

out.armWindow = census('player turn, fog armed on lane 0');

/* ── the fire window: drive to the rival's turn ───────────────────── */
let reachedOpp = null, oppCensus = null;
/* BANKING WITH NOTHING KEPT DOES NOT END A TURN. The first run called
   handleBank() on an untouched roll, the turn stayed the player's, and the
   fire window came back null - a void measurement whose verdict fields all
   read false as though the game had answered. Keep the scoring faces first,
   then bank, and report whether the keep actually took. */
let kept = 0;
try {
  const free = ((G && G.pool) || []).filter(d => !d.committed);
  free.forEach(d => { if ((d.val === 1 || d.val === 5) && d.el) { FXH.tap(d.el); kept++; } });
  await FXH.until(() => (G.kept || []).length > 0 || (G.turnPts || 0) > 0, 8000);
} catch (e) {}
out.keptForBank = {clicked: kept, turnPts: (typeof G !== 'undefined' && G) ? G.turnPts : null,
                   keptLen: (typeof G !== 'undefined' && G && G.kept) ? G.kept.length : null};
/* WHY THE BANK WAS REFUSED, recorded because it is a fact about writing
   probes and not about this feature. Run 3 sat 180s in `choosing` with the
   trace showing rolling -> choosing and nothing after: handleBank() returned
   without ending the turn. THE MENDING (32057) holds the bank shut while the
   turn is one roll old, and a probe that rolls once and banks hits it every
   time. The state is read rather than assumed, then the turn is ended through
   endPTurn - the canonical exit the game itself uses - because the subject
   here is the rival's ROW, not the banking rule. */
try {
  const bb = document.getElementById('btnBank');
  out.bankGate = {
    disabled: !!(bb && bb.classList.contains('disabled')),
    mendHeld: !!(bb && bb.classList.contains('mend-held')),
    canRollNow: (typeof G !== 'undefined' && G) ? !!G._canRollNow : null,
  };
  if (bb && !bb.classList.contains('disabled')) FXH.tap(bb);
} catch (e) { out.bankGate = {err: e.message}; }

try {
  const before = (typeof G !== 'undefined' && G) ? (G.pTurns || 0) : -1;
  const moved = await FXH.until(() => (G.pTurns || 0) !== before ||
    G.phase === 'opp' || G._oppTurnActive, 15000);
  if (moved == null) { try { endPTurn(); } catch (e) {} out.usedEndPTurn = true; }
  reachedOpp = await FXH.until(() =>
    typeof G !== 'undefined' && G && (G.phase === 'opp' || G._oppTurnActive) &&
    (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 180000);
  if (reachedOpp != null) oppCensus = census('rival turn, row just dealt');
  /* AND AGAIN AFTER THE RIVAL'S DICE SETTLE. The early census fired the
     instant oppDiceRow gained a child - the moment the DOM chips exist, which
     is not the moment D3X adopts them. It reported six rival chips and ZERO
     D3X records for them, and that reads identically to "the rival's dice are
     never in the 3D layer at all". Those are different answers and they decide
     whether a rival seat can wear a mark, so the late sample waits for a
     record to appear rather than concluding from the early one. */
  const adopted = await FXH.until(() => ((window.D3X && D3X.dice) || []).some(
    d => { try { return d.chip && d.chip.closest &&
                 d.chip.closest('#oppDiceRow'); } catch (e) { return false; } }),
    90000);
  out.rivalAdoptedMs = adopted;
  out.fireWindowSettled = census('rival turn, after the dice are adopted');
} catch (e) { reachedOpp = 'threw: ' + e.message; }
try { clearInterval(_ff); clearInterval(_tr); } catch (e) {}
out.reachedOppMs = reachedOpp;
out.phaseTrace = trace.slice(0, 40);
out.afterBank = {phase: (typeof G !== 'undefined' && G) ? G.phase : null,
                 pPts: (typeof G !== 'undefined' && G) ? G.pPts : null,
                 pTurns: (typeof G !== 'undefined' && G) ? G.pTurns : null,
                 oppTurnActive: !!(typeof G !== 'undefined' && G && G._oppTurnActive)};
out.fireWindow = oppCensus;

/* do rival dice carry the .lane the marks are keyed by? The fire sites match
   _oFree[j].lane against m.lane, so a paint predicate has to do the same. */
out.rivalLanes = (function () {
  try {
    const od = (G && G.oppDice) || [];
    return {n: od.length,
            lanes: od.map(d => (d && d.lane !== undefined) ? d.lane : null),
            allStamped: od.length > 0 && od.every(d => typeof d.lane === 'number'),
            haveEl: od.filter(d => d && d.el).length};
  } catch (e) { return {err: e.message}; }
})();

const A = out.armWindow, F = out.fireWindow;
out.VERDICT = {
  /* the probe could see anything at all */
  theInstrumentRuns: out.instrument.hasMarkPass === true &&
                     out.beforeArm.records > 0 && out.beforeArm.paintable > 0,
  theMarkWasActuallyArmed: out.armed === true && A.liveMarks === 1,
  /* THE QUESTION. Is there a rival die to wear the mark while it is armed? */
  aRivalSeatExistsDuringTheArmWindow:
    A.oppRowChildren > 0 && (A.rows['oppDiceRow'] || {paintable: 0}).paintable > 0,
  /* and at the moment it fires */
  /* THE TURN ENDED, not "I clicked". The previous form gated on clicked > 0,
     which passed on run 3 while the trace showed the turn never left
     `choosing` - a check measuring the probe's own action instead of the
     game's response, and the third of that species this session. */
  theTurnActuallyEnded: out.afterBank.phase !== 'choosing' ||
                        (out.afterBank.pTurns || 0) > 0,
  reachedTheRivalTurn: reachedOpp != null && typeof reachedOpp === 'number',
  aRivalSeatExistsDuringTheFireWindow: F
    ? (F.oppRowChildren > 0 && (F.rows['oppDiceRow'] || {paintable: 0}).paintable > 0)
    : null,
  /* THE ONE THAT DECIDES THE DESIGN: can a rival seat ever wear a mark? */
  aRivalSeatIsPaintableOnceSettled: out.fireWindowSettled
    ? ((out.fireWindowSettled.rows['oppDiceRow'] || {paintable: 0}).paintable > 0)
    : null,
  /* the player's own brand die stays paintable after the turn ends */
  thePlayerSeatSurvivesTheTurn: F
    /* NO '#'. rowOf returns el.id, which carries no hash, so every one of
       these lookups was undefined and the verdict read false against a census
       that plainly showed six paintable player dice. A false negative from a
       key that never matched - and the rival verdicts had the same fault, but
       were saved by the oppRowChildren half of the test being independently
       true. A probe bug that got the right answer for the wrong reason is
       still a probe bug. */
    ? ((F.rows['playerDiceRow'] || {paintable: 0}).paintable +
       (F.rows['keptTray'] || {paintable: 0}).paintable +
       (F.rows['keptRow'] || {paintable: 0}).paintable) > 0
    : null,
  rivalDiceCarryTheLaneKey: out.rivalLanes.allStamped === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
