/* THE LANE CENSUS THAT DOES NOT CONSULT THE ROSTER.
 *
 * _famLaneRecords() cannot certify itself and neither can grep: both answer
 * "what did somebody remember to enrol", which is the same question that was
 * wrong four times running. This walks the live G for every object carrying a
 * numeric `lane`, snapshots WHICH DIE each one points at by object identity,
 * reorders, and asserts the mapping survived. A record nobody enrolled shows up
 * because its die changed underneath it, not because it was on a list.
 *
 * IDENTITY, NOT INDEX. The assertion is `the die object at record.lane is the
 * same object it was before`. Lane numbers all change in a reorder; object
 * identity cannot be confused by renumbering.
 *
 * THE DICE THEMSELVES ARE EXCLUDED - they carry `lane` too, and they are the
 * subject rather than a record of it. Rival-side records are reported but not
 * asserted on: `oLane` indexes the rival board and a player reorder must NOT
 * move it (P531), so a rival record whose player-lane die changed is expected.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
if (!(r.freeDice > 0)) return {err: 'no dice: ' + r.why};

const free = () => G.pool.filter(d => !d.committed && !d._frozen && d.el);

/* ── seed the known lane-stamped records so the assert has teeth ──── */
const fr0 = free();
if (fr0.length < 4) return {err: 'need four free dice, have ' + fr0.length};
G._famPeekVals = fr0.map((d, i) => ({lane: d.lane, val: (i % 6) + 1}));
G._fairTrade = {lane: fr0[1].lane, was: 'bone', borrowed: 'iron'};
G._tradeSwaps = [{lane: fr0[2].lane, from: 'bone', to: 'silver'}];
G._famPreserve = {val: 5, mat: 'bone', ench: null, lane: fr0[0].lane, pts: 50, crack: 0};
/* a DOM ghost, the other kind */
(window._pkGhosts || []).forEach(g => { try { g.remove(); } catch (e) {} });
window._pkGhosts = [];
fr0.forEach((d, i) => {
  const g = document.createElement('div');
  g.className = 'peek-float';
  g.textContent = String((i % 6) + 1);
  g.dataset.lane = String(d.lane);
  g.style.cssText = 'position:fixed;left:0;top:0';
  document.body.appendChild(g);
  window._pkGhosts.push(g);
});
/* AND AN UNENROLLED ONE, deliberately - the probe has to be able to catch a
   record nobody put on the roster, or it is only testing the roster again.
   IT GOES ON A DIE THAT WILL MOVE. The first version planted it on fr0[3],
   outside the span the reorder rotates, so it "kept its die" by never having
   been at risk and the negative control passed vacuously - it could not have
   failed however broken the carry was. fr0[0] is the die the drag picks up, so
   an uncarried record on it MUST end up pointing at a stranger. */
G._zzUnenrolledProbeRecord = {lane: fr0[0].lane, note: 'nobody enrolled me'};

/* ── the walk ─────────────────────────────────────────────────────── */
function census() {
  const found = [], seen = new Set(), poolSet = new Set(G.pool || []);
  const d3x = new Set((typeof D3X !== 'undefined' && D3X.dice) ? D3X.dice : []);
  (function walk(obj, path, depth) {
    if (!obj || depth > 4 || typeof obj !== 'object') return;
    if (seen.has(obj)) return;
    seen.add(obj);
    if (typeof Node !== 'undefined' && obj instanceof Node) return;
    if (Array.isArray(obj)) {
      obj.forEach((v, i) => walk(v, path + '[' + i + ']', depth + 1));
      return;
    }
    if (typeof obj.lane === 'number' && isFinite(obj.lane) &&
        !poolSet.has(obj) && !d3x.has(obj)) {
      found.push({path, obj, lane: obj.lane,
                  hasOLane: typeof obj.oLane === 'number'});
    }
    for (const k in obj) {
      if (k === 'el' || k === 'chip' || k === 'phys') continue;
      let v; try { v = obj[k]; } catch (e) { continue; }
      if (v && typeof v === 'object') walk(v, path + '.' + k, depth + 1);
    }
  })(G, 'G', 0);
  return found;
}

const dieAtLane = (L) => G.pool.filter(d => d.lane === L && !d.committed)[0] || null;

const recs = census();
const enrolled = new Set((typeof _famLaneRecords === 'function') ? _famLaneRecords() : []);
const before = recs.map(x => ({
  path: x.path, obj: x.obj, laneBefore: x.lane, hasOLane: x.hasOLane,
  dieBefore: dieAtLane(x.lane),
  onTheRoster: enrolled.has(x.obj),
}));
const ghostsBefore = (window._pkGhosts || []).map(g => ({
  g, laneBefore: +g.dataset.lane, dieBefore: dieAtLane(+g.dataset.lane),
}));

out.censusBefore = {
  records: before.length,
  onTheRoster: before.filter(x => x.onTheRoster).length,
  notOnTheRoster: before.filter(x => !x.onTheRoster).map(x => x.path),
  paths: before.map(x => x.path + '@' + x.laneBefore),
  ghosts: ghostsBefore.length,
};

/* ── reorder, through the real ends ───────────────────────────────── */
function chipAt(pos) {
  const info = (typeof _vgRowInfo === 'function') ? _vgRowInfo() : null;
  if (!info) return null;
  const ord = info.dice.slice().sort((a, b) => a.phys.x - b.phys.x);
  const d = ord[pos < 0 ? ord.length + pos : pos];
  return d ? d.chip : null;
}
let attempts = 0; out.drove = {err: 'not attempted'};
for (; attempts < 12; attempts++) {
  const chip = chipAt(0);
  if (chip) {
    const info = _vgRowInfo();
    if (info) {
      try { _startVagabondDrag(chip); } catch (e) {}
      const st = window._vgDragState;
      if (st) { st.to = 2; try { _commitVagabondDrag(); out.drove = {ok: true}; break; }
                catch (e) { out.drove = {err: 'commit: ' + e.message}; } }
      else out.drove = {err: 'drag did not start'};
    } else out.drove = {err: '_vgRowInfo null'};
  } else out.drove = {err: 'no chip'};
  try { if (window._vgDragState) _vgDragCancel(); } catch (e) {}
  await new Promise(res => setTimeout(res, 400));
}
out.driveAttempts = attempts + 1;

/* ── did every record still point at its own die? ─────────────────── */
const rows = before.map(x => {
  const dieAfter = dieAtLane(x.obj.lane);
  return {
    path: x.path, onTheRoster: x.onTheRoster, rivalSide: x.hasOLane,
    laneBefore: x.laneBefore, laneAfter: x.obj.lane,
    itsDieMoved: x.dieBefore ? x.dieBefore.lane !== x.laneBefore : null,
    stillPointsAtItsOwnDie: x.dieBefore ? dieAfter === x.dieBefore : null,
  };
});
const ghostRows = ghostsBefore.map(x => {
  const dieAfter = dieAtLane(+x.g.dataset.lane);
  return {
    laneBefore: x.laneBefore, laneAfter: +x.g.dataset.lane,
    itsDieMoved: x.dieBefore ? x.dieBefore.lane !== x.laneBefore : null,
    stillPointsAtItsOwnDie: x.dieBefore ? dieAfter === x.dieBefore : null,
  };
});
out.records = rows;
out.ghosts = ghostRows;

/* cleanup */
(window._pkGhosts || []).forEach(g => { try { g.remove(); } catch (e) {} });
window._pkGhosts = [];
try { delete G._zzUnenrolledProbeRecord; G._famPeekVals = null;
      G._fairTrade = null; G._tradeSwaps = null; G._famPreserve = null; } catch (e) {}

const playerSide = rows.filter(x => !x.rivalSide);
const anyMoved = rows.some(x => x.itsDieMoved === true);
const unenrolled = playerSide.filter(x => !x.onTheRoster);
out.VERDICT = {
  theReorderRan: !out.drove.err,
  someDiceMovedSeats: anyMoved,
  /* THE PROBE CAN SEE AN UNENROLLED RECORD AT ALL - a deliberately planted one
     must be found by the walk, or a clean result means the walk is blind */
  thePlantedRecordWasFound:
    rows.some(x => x.path.indexOf('_zzUnenrolledProbeRecord') >= 0),
  /* and it must FAIL, because nothing carries it - if this passes, the probe
     cannot distinguish enrolled from unenrolled and proves nothing. It is
     planted on the die the drag picks up, so "it did not move" is not an
     available excuse. */
  thePlantedRecordWasNotCarried: (function () {
    const p = rows.filter(x => x.path.indexOf('_zzUnenrolledProbeRecord') >= 0)[0];
    /* gated on its die having actually moved - otherwise this reports a pass
       for a canary that was never exposed */
    if (!p || p.itsDieMoved !== true) return null;
    return p.stillPointsAtItsOwnDie === false;
  })(),
  thePlantedRecordWasExposed: (function () {
    const p = rows.filter(x => x.path.indexOf('_zzUnenrolledProbeRecord') >= 0)[0];
    return p ? p.itsDieMoved === true : false;
  })(),
  /* THE FINDING: every player-side record that IS on the roster kept its die */
  everyEnrolledRecordKeptItsDie: (anyMoved && !out.drove.err)
    ? playerSide.filter(x => x.onTheRoster)
        .every(x => x.stillPointsAtItsOwnDie === true) : null,
  everyGhostKeptItsDie: (anyMoved && !out.drove.err)
    ? ghostRows.every(x => x.stillPointsAtItsOwnDie === true) : null,
  /* and nothing real turned up outside the roster */
  noUnenrolledPlayerRecords:
    unenrolled.filter(x => x.path.indexOf('_zzUnenrolledProbeRecord') < 0).length === 0,
};
out.unenrolledFound = unenrolled.map(x => x.path);
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
