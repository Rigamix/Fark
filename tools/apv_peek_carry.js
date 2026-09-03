/* P922 - does the STARGAZER PROMISE follow its die through a reorder?
 *
 * THIS ASSERTS ON THE ROLL, NOT THE FLOAT. P919's probe checked that the float
 * moved, and the float was never the broken half. The promise lives in two
 * places that must agree: G._famPeekVals[i] = {lane,val}, which decides which
 * die RECEIVES the face, and a DOM float whose dataset.lane is copied off it at
 * mint. P919 taught the float to follow its die and left the record behind, so
 * a float promising 5 sat over a die that rolled 6 - and a probe that only
 * watched the float passed.
 *
 * SO THE TEST IS THE AGREEMENT ITSELF: after a reorder, the value a die
 * actually receives from the real consume path must be the value that was
 * promised to THAT DIE at mint, and the float standing over it must show the
 * same number. Die identity is tracked by object reference, which no lane
 * renumbering can confuse.
 *
 * THE CONSUME IS THE GAME'S. famApplyRollForces() is what every player roll
 * calls (34266); the probe calls the same function rather than reimplementing
 * the lane lookup it is testing.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
if (!(r.freeDice > 0)) return {err: 'no dice: ' + r.why};

out.seam = {
  recordRoster: typeof _famLaneRecords === 'function',
  ghostRoster: typeof _famLaneGhosts === 'function',
  consume: typeof famApplyRollForces === 'function',
  starter: typeof _startVagabondDrag === 'function',
};

const free = () => G.pool.filter(d => !d.committed && !d._frozen && d.el);

/* mint the stargazer promise exactly as 17932/17940-17948 do, but with
   DISTINCT values so any mix-up is visible rather than coincidentally equal */
function mintPromise() {
  const fr = free();
  const promised = new Map();
  G._famPeekVals = fr.map((d, i) => {
    const v = (i % 6) + 1;
    promised.set(d, v);
    return {lane: d.lane, val: v};
  });
  (window._pkGhosts || []).forEach(g => { try { g.remove(); } catch (e) {} });
  window._pkGhosts = [];
  fr.forEach((d, i) => {
    if (!d.el) return;
    const box = d.el.getBoundingClientRect();
    const g = document.createElement('div');
    g.className = 'peek-float';
    g.textContent = String(G._famPeekVals[i].val);
    g.dataset.lane = String(G._famPeekVals[i].lane);
    g.style.cssText = 'position:fixed;left:' + (box.left + box.width / 2) +
                      'px;top:' + (box.top + box.height / 2) + 'px';
    document.body.appendChild(g);
    window._pkGhosts.push(g);
  });
  return promised;
}

function reorder(fromChip, toIdx) {
  const info = (typeof _vgRowInfo === 'function') ? _vgRowInfo() : null;
  if (!info) return {err: '_vgRowInfo returned null'};
  try { _startVagabondDrag(fromChip); } catch (e) { return {err: 'start: ' + e.message}; }
  const st = window._vgDragState;
  if (!st) return {err: 'the drag did not start'};
  const from = st.from;
  st.to = toIdx;
  try { _commitVagabondDrag(); } catch (e) { return {err: 'commit: ' + e.message}; }
  return {ok: true, from, to: toIdx, rowSize: info.dice.length};
}

function chipAt(pos) {
  const info = (typeof _vgRowInfo === 'function') ? _vgRowInfo() : null;
  if (!info) return null;
  const ord = info.dice.slice().sort((a, b) => a.phys.x - b.phys.x);
  const d = ord[pos < 0 ? ord.length + pos : pos];
  return d ? d.chip : null;
}

/* ── the run ──────────────────────────────────────────────────────── */
const promised = mintPromise();
const before = free().map(d => ({d, lane: d.lane, want: promised.get(d)}));
out.mint = {
  dice: before.length,
  recordsSeen: (typeof _famLaneRecords === 'function') ? _famLaneRecords().length : null,
  ghostsSeen: (typeof _famLaneGhosts === 'function') ? _famLaneGhosts().length : null,
  lanes: before.map(b => b.lane), promises: before.map(b => b.want),
};

/* RETRY THE DRIVE. _vgRowInfo returns null unless at least two dice share a
   row key, which is false while the 3D layer is still settling - so the drive
   is flaky on a ~1fps headless harness, and a run where nothing moved proves
   nothing in either direction. Retrying is honest here because the thing under
   test is what happens AFTER a reorder; failing to start one is a harness
   condition, not a result. The attempt count is reported so a run that needed
   ten tries is visible rather than smoothed away. */
let chip = null, attempts = 0;
out.drove = {err: 'not attempted'};
for (; attempts < 12; attempts++) {
  chip = chipAt(0);
  if (chip) {
    out.drove = reorder(chip, 2);
    if (!out.drove.err) break;
  } else {
    out.drove = {err: '_vgRowInfo returned null (dice not in a settled row)'};
  }
  try { if (window._vgDragState) _vgDragCancel(); } catch (e) {}
  await FXH.sleep ? FXH.sleep(400) : new Promise(r => setTimeout(r, 400));
}
out.driveAttempts = attempts + 1;

const moved = before.filter(b => b.d.lane !== b.lane).length;
out.reorder = {
  lanesAfter: before.map(b => b.d.lane),
  diceThatMoved: moved,
  recordLanesAfter: (typeof _famLaneRecords === 'function')
    ? _famLaneRecords().map(x => x.lane) : null,
  ghostStampsAfter: (window._pkGhosts || []).map(g => g.dataset.lane),
};

/* THE FLOAT IS READ BEFORE THE CONSUME, because the consume destroys it.
   famApplyRollForces calls _clearRollForces at its tail - the floats live
   exactly as long as the forces they mark - so reading them afterwards gave
   null for every die and made the on-screen-agreement check unanswerable in
   BOTH arms, which reads as a shared failure rather than as a probe sampling
   outside the window its subject exists in. */
const floatText = new Map();
before.forEach(b => {
  const g = (window._pkGhosts || [])
    .filter(x => x.dataset.lane === String(b.d.lane))[0] || null;
  floatText.set(b.d, g ? g.textContent : null);
});
out.floatsBeforeConsume = before.map(b => floatText.get(b.d));

/* THE REAL CONSUME - the same call every player roll makes */
try { famApplyRollForces(); } catch (e) { out.consumeThrew = e.message; }
out.ghostsAfterConsume = (window._pkGhosts || []).length;

const rows = before.map(b => {
  const ghost = floatText.get(b.d);
  return {
    laneBefore: b.lane, laneAfter: b.d.lane, moved: b.d.lane !== b.lane,
    promisedToThisDie: b.want, dieGot: b.d.val,
    dieGotWhatItWasPromised: b.d.val === b.want,
    floatOverIt: ghost,
    floatMatchesTheDie: ghost != null ? String(b.d.val) === ghost : null,
  };
});
out.rows = rows;
(window._pkGhosts || []).forEach(g => { try { g.remove(); } catch (e) {} });
window._pkGhosts = [];
try { G._famPeekVals = null; } catch (e) {}

const drove = !out.drove.err;
out.VERDICT = {
  theSeamIsThere: Object.keys(out.seam).every(k => out.seam[k] === true),
  theReorderRan: drove,
  /* nothing below means anything unless dice actually changed seats */
  someDiceMovedSeats: moved > 0,
  /* THE INVARIANT: the die receives the face promised to IT */
  everyDieGotItsOwnPromise: (drove && moved > 0)
    ? rows.every(x => x.dieGotWhatItWasPromised === true) : null,
  /* and specifically the ones that moved, which is where it broke */
  theMovedDiceGotTheirs: (drove && moved > 0)
    ? rows.filter(x => x.moved).every(x => x.dieGotWhatItWasPromised === true) : null,
  /* and the float agrees with the die under it - the half P919 fixed alone */
  /* the float was actually readable in the window it was sampled in - without
     this, a null float reads as a shared failure instead of a missing sample */
  theFloatsWereSampledWhileTheyExisted: rows.every(x => x.floatOverIt != null),
  theFloatAgreesWithTheDie: (drove && moved > 0 && rows.every(x => x.floatOverIt != null))
    ? rows.every(x => x.floatMatchesTheDie === true) : null,
  nothingThrew: !out.consumeThrew,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
