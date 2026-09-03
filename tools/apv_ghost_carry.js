/* P919 (brief 3.8) - does a lane-stamped ghost follow its die through a reorder?
 *
 * DRIVEN THROUGH BOTH REAL ENDS. The first version built _vgDragState by hand
 * and could not even find the dice - it guessed at D3X.dice's shape. It now
 * calls _startVagabondDrag(chipEl), which is the function the player's pointer
 * calls, sets only `to` (which is all the pointermove lerp ever writes), and
 * calls _commitVagabondDrag(). Nothing about the drag is reimplemented.
 *
 * AND THE FIRST RUN SHOWED WHY THE GATES MATTER. The drive failed, the die
 * therefore never moved seats, and `theGhostFollowedItsDie` came back TRUE -
 * trivially, because a stationary die's lane still equals the stamp it was
 * minted with. A pass that a broken drive can produce is not evidence. So the
 * verdict below is gated: the reorder must have run AND the die must have
 * changed lane, or every downstream result is about nothing.
 *
 * THE CONTROL IS A GHOST ON A DIE THAT DOES NOT MOVE, which must come back
 * unchanged - one arm says the carry fires, the other says it fires only where
 * it should.
 *
 * AND THE READER IS CHECKED LAST, because the point of 3.8 is not that a
 * dataset attribute changed - it is that _famRefloatGhosts, unmodified, lands
 * the float on the die the player is looking at.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!(r.freeDice > 0)) return Object.assign(out, {err: 'no dice: ' + r.why});

out.seam = {
  rosterIsAFunction: typeof _famLaneGhosts === 'function',
  readerExists: typeof _famRefloatGhosts === 'function',
  starterExists: typeof _startVagabondDrag === 'function',
  commitExists: typeof _commitVagabondDrag === 'function',
};

const free = () => G.pool.filter(d => !d.committed && !d._frozen && d.el);

const mintGhost = (lane) => {
  const g = document.createElement('div');
  g.className = 'peek-float';
  g.textContent = 'X';
  g.dataset.lane = String(lane);
  g.style.cssText = 'position:fixed;left:0;top:0';
  document.body.appendChild(g);
  window._pkGhosts = window._pkGhosts || [];
  window._pkGhosts.push(g);
  return g;
};
const clearGhosts = () => {
  (window._pkGhosts || []).forEach(g => { try { g.remove(); } catch (e) {} });
  window._pkGhosts = [];
};

/* the real starter, then only `to`, then the real commit */
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

/* which chip sits leftmost, and which index it holds in the drag's own order */
function chipAt(pos) {
  const info = (typeof _vgRowInfo === 'function') ? _vgRowInfo() : null;
  if (!info) return null;
  const ord = info.dice.slice().sort((a, b) => a.phys.x - b.phys.x);
  const d = ord[pos < 0 ? ord.length + pos : pos];
  return d ? d.chip : null;
}
const dieOfChip = chip => G.pool.filter(d => d.el === chip)[0] || null;

/* ── 1. the ghost stamped on the die that MOVES ───────────────────── */
clearGhosts();
const c1 = chipAt(0);
const mover = c1 && dieOfChip(c1);
if (!mover) return Object.assign(out, {err: 'no leftmost die'});
const laneBefore = mover.lane;
const g1 = mintGhost(laneBefore);
const rr1 = reorder(c1, 2);
out.movedDie = {
  drove: rr1, laneBefore, laneAfter: mover.lane,
  dieActuallyMoved: mover.lane !== laneBefore,
  ghostStampBefore: String(laneBefore),
  ghostStampAfter: g1.dataset.lane,
  followed: g1.dataset.lane === String(mover.lane),
};

/* ── 2. a ghost stamped on a die that does NOT move ───────────────── */
clearGhosts();
const c2 = chipAt(0), cLast = chipAt(-1);
const still = cLast && dieOfChip(cLast);
if (!still) return Object.assign(out, {err: 'no rightmost die'});
const stillLane = still.lane;
const g2 = mintGhost(stillLane);
const rr2 = reorder(c2, 1);   /* swaps the first two; the last is untouched */
out.unmovedDie = {
  drove: rr2, laneBefore: stillLane, laneAfter: still.lane,
  stayedPut: still.lane === stillLane,
  ghostStampAfter: g2.dataset.lane,
  unchanged: g2.dataset.lane === String(stillLane),
};

/* ── 3. and the reader lands it on the right die ──────────────────── */
clearGhosts();
const c3 = chipAt(0);
const mv = c3 && dieOfChip(c3);
const lb = mv ? mv.lane : null;
const g3 = mintGhost(lb);
const rr3 = reorder(c3, 2);
try { _famRefloatGhosts(); } catch (e) { out.refloatThrew = e.message; }
const box = mv && mv.el ? mv.el.getBoundingClientRect() : null;
out.reader = {
  drove: rr3, laneBefore: lb, laneAfter: mv ? mv.lane : null,
  dieActuallyMoved: mv ? mv.lane !== lb : null,
  ghostLane: g3.dataset.lane, dieLane: mv ? mv.lane : null,
  ghostLeft: g3.style.left, ghostTop: g3.style.top,
  dieCentreX: box ? Math.round(box.left + box.width / 2) : null,
  dieCentreY: box ? Math.round(box.top + box.height / 2) : null,
  onTheRightDie: box && g3.style.left
    ? Math.abs(parseFloat(g3.style.left) - (box.left + box.width / 2)) < 2
    : null,
};
clearGhosts();

/* THE GATE FIRST. Everything under it is meaningless if the drive did not
   actually move a die between seats. */
const drove = !out.movedDie.drove.err && !out.unmovedDie.drove.err &&
              !out.reader.drove.err;
const moved = out.movedDie.dieActuallyMoved === true &&
              out.reader.dieActuallyMoved === true;
out.VERDICT = {
  theSeamIsThere: Object.keys(out.seam).every(k => out.seam[k] === true),
  theReorderRan: drove,
  theDieActuallyMovedSeats: moved,
  /* the carry fires where it should - only askable once the two above hold */
  theGhostFollowedItsDie: (drove && moved) ? out.movedDie.followed === true : null,
  /* and only where it should */
  theUnmovedDieStayedPut: drove ? out.unmovedDie.stayedPut === true : null,
  theGhostOnItDidNotMove: drove ? out.unmovedDie.unchanged === true : null,
  /* and the ruling: the unmodified reader lands it on the die that moved */
  theFloatLandsOnTheRightDie: (drove && moved) ? out.reader.onTheRightDie === true : null,
  nothingThrew: !out.refloatThrew,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
