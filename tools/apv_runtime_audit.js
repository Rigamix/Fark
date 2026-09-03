/* P928 - does the runtime lane audit fire on a real reorder, and stay silent on
 * a clean one? And does P927's guard actually throw in dev?
 *
 * THE NEGATIVE CASE IS THE ONE THAT DECIDES WHETHER THIS SHIPS. An audit that
 * flags the ordinary game state is noise, and a noisy guard gets switched off -
 * which is worse than no guard, because it looks like coverage. So the clean
 * reorder is run FIRST, with the real records seeded and nothing planted, and
 * it must report zero.
 *
 * THEN the fault is planted on a die that will actually move - the mistake the
 * probe version of this made was planting the canary outside the rotated span,
 * where it passed vacuously - and the audit must catch it by path.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
window._fkDbgOn = true;

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
if (!(r.freeDice > 0)) return {err: 'no dice: ' + r.why};

out.seam = {
  walk: typeof _famLaneWalk === 'function',
  before: typeof _famLaneAuditBefore === 'function',
  after: typeof _famLaneAuditAfter === 'function',
  ignoreList: (typeof _LANE_AUDIT_IGNORE !== 'undefined') ? _LANE_AUDIT_IGNORE.length : null,
  devFlag: !!window._fkDbgOn,
};

const free = () => G.pool.filter(d => !d.committed && !d._frozen && d.el);
function chipAt(pos) {
  const info = (typeof _vgRowInfo === 'function') ? _vgRowInfo() : null;
  if (!info) return null;
  const ord = info.dice.slice().sort((a, b) => a.phys.x - b.phys.x);
  const d = ord[pos < 0 ? ord.length + pos : pos];
  return d ? d.chip : null;
}
async function reorder() {
  for (let i = 0; i < 12; i++) {
    const chip = chipAt(0);
    if (chip && _vgRowInfo()) {
      try { _startVagabondDrag(chip); } catch (e) {}
      const st = window._vgDragState;
      if (st) { st.to = 2; try { _commitVagabondDrag(); return {ok: true}; }
                catch (e) { return {err: 'commit: ' + e.message}; } }
    }
    try { if (window._vgDragState) _vgDragCancel(); } catch (e) {}
    await new Promise(res => setTimeout(res, 400));
  }
  return {err: 'could not start a drag'};
}
function seedRealRecords() {
  const fr = free();
  G._famPeekVals = fr.map((d, i) => ({lane: d.lane, val: (i % 6) + 1}));
  G._fairTrade = {lane: fr[1].lane, was: 'bone', borrowed: 'iron'};
  G._tradeSwaps = [{lane: fr[2].lane, from: 'bone', to: 'silver'}];
  G._famPreserve = {val: 5, mat: 'bone', ench: null, lane: fr[0].lane, pts: 50, crack: 0};
  return fr;
}

/* ── 1. THE CLEAN CASE. Real records, nothing planted. Must be silent. ── */
G._laneAuditViolations = 0; G._laneAuditPaths = null;
const fr1 = seedRealRecords();
out.cleanRecordsSeeded = _famLaneWalk().map(x => x.path);
out.cleanDrove = await reorder();
out.clean = {
  violations: G._laneAuditViolations || 0,
  paths: G._laneAuditPaths,
};

/* ── 2. THE PLANTED FAULT, on a die that will move ─────────────────── */
G._laneAuditViolations = 0; G._laneAuditPaths = null;
const fr2 = seedRealRecords();
G._zzUnenrolled = {lane: fr2[0].lane, note: 'nobody enrolled me'};
const laneAtRisk = fr2[0].lane, dieAtRisk = fr2[0];
out.faultDrove = await reorder();
out.planted = {
  laneAtRisk, dieMoved: dieAtRisk.lane !== laneAtRisk,
  violations: G._laneAuditViolations || 0,
  paths: G._laneAuditPaths,
  namedTheRecord: (G._laneAuditPaths || []).some(p => p.indexOf('_zzUnenrolled') >= 0),
};
try { delete G._zzUnenrolled; } catch (e) {}

/* ── 3. P927's guard must THROW in dev, not just log ───────────────── */
G._ndDiscarded = 0;
const origRender = window._renderSelTags;
window._renderSelTags = function () {
  try { G.numDice = 3; } catch (e) {}
  return origRender.apply(this, arguments);
};
let threw = null;
await FXH.until(() => { try { return G && G.phase === 'idle' && !G._oppTurnActive; }
                        catch (e) { return false; } }, 20000);
try { startPTurn(); } catch (e) { threw = e.message; }
window._renderSelTags = origRender;
out.guard = {
  threw: threw, counted: G._ndDiscarded,
  mentionsTheValue: !!(threw && threw.indexOf('numDice=3') >= 0),
};

try { G._famPeekVals = null; G._fairTrade = null;
      G._tradeSwaps = null; G._famPreserve = null; } catch (e) {}

out.VERDICT = {
  theSeamIsThere: out.seam.walk && out.seam.before && out.seam.after && out.seam.devFlag,
  theAuditSawTheRealRecords: (out.cleanRecordsSeeded || []).length >= 4,
  bothReordersRan: !out.cleanDrove.err && !out.faultDrove.err,
  /* THE ONE THAT DECIDES IT SHIPS: the ordinary state is silent */
  theCleanReorderWasSilent: out.clean.violations === 0,
  /* the canary was actually exposed, or its catch means nothing */
  thePlantedRecordWasExposed: out.planted.dieMoved === true,
  theAuditCaughtThePlantedRecord: out.planted.violations > 0,
  theAuditNamedItByPath: out.planted.namedTheRecord === true,
  /* P927 is loud now */
  theGuardThrewInDev: !!out.guard.threw,
  theThrowNamedTheValue: out.guard.mentionsTheValue === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
