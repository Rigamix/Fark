/* P945 (brief 3.1) - does an enchant occupy a SPOT rather than a die?
 *
 * THE TWO CASES THE RULING NAMES, and the old shape got both wrong in opposite
 * directions:
 *   TWO FOGS ON TWO LANES must both live. Keyed by type, the second _lmArm was
 *   a plain overwrite of G._fog, so the first silently vanished.
 *   FOG AND SNUFF ON ONE LANE must be refused. Keyed by type they lived in
 *   different slots, and nothing compared lanes across them.
 * A probe that only checks one of these passes on the old code.
 *
 * AND THE REFUSAL IS THE RETURN VALUE, so it is asserted directly rather than
 * inferred from the map afterwards - inferring would pass on a version that
 * refused by silently doing nothing, which is a different rule.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

out.seam = {
  map: typeof _lmMap === 'function',
  arm: typeof _lmArm === 'function',
  live: typeof _lmLive === 'function',
  dueList: typeof _lmDueList === 'function',
  occupied: typeof _lmOccupied === 'function',
  snuffed: typeof _lmSnuffed === 'function',
  /* the three type keys must be GONE, or something still reads them */
  noFogKey: G._fog === undefined,
  noSnuffKey: G._snuff === undefined,
  noSnareKey: G._snare === undefined,
};

const reset = () => { G._laneMark = {}; G.oppTurnCount = 0; };

/* ── 1. TWO FOGS ON TWO LANES both live ───────────────────────────── */
reset();
const a1 = _lmArm('_fog', 2, 1);
const a2 = _lmArm('_fog', 4, 1);
out.twoFogs = {
  firstArmed: a1, secondArmed: a2,
  liveCount: _lmLive('_fog').length,
  lanes: _lmLive('_fog').map(x => x.lane).sort(),
};

/* ── 2. A SECOND MARK ON ONE LANE is refused, any type against any ── */
reset();
const b1 = _lmArm('_fog', 3, 1);
const b2 = _lmArm('_snuff', 3, 1);      /* different type, same lane */
const b3 = _lmArm('_fog', 3, 1);        /* same type, same lane */
out.oneLane = {
  fogArmed: b1, snuffRefused: b2 === false, fogAgainRefused: b3 === false,
  liveCount: _lmLive().length,
  theSurvivorIsTheFirst: (_lmMap()[3] || {}).t === '_fog',
  occupiedReportsTaken: _lmOccupied(3) === true,
};

/* ── 3. A SPENT MARK FREES ITS SPOT ───────────────────────────────── */
reset();
_lmArm('_snare', 1, 1);
G.oppTurnCount = 1;                      /* the mark is now due */
const dueBefore = _lmDue('_snare');
_lmSpend('_snare');                      /* turns 1 -> 0, so it dies */
const rearm = _lmArm('_fog', 1, 1);
out.spentFreesTheSpot = {
  wasDue: dueBefore,
  spentIsDead: (_lmMap()[1] || {}).t === '_fog' || !_lmLive('_snare').length,
  laneReArmed: rearm === true,
  occupiedAfterSpend: _lmOccupied(1),
};

/* ── 4. TWO DUE MARKS OF A TYPE both spend ────────────────────────── */
reset();
_lmArm('_fog', 0, 2); _lmArm('_fog', 5, 2);   /* two attempts each */
G.oppTurnCount = 1;
const dueList = _lmDueList('_fog').length;
_lmSpend('_fog');
out.spendChargesAll = {
  dueBothArmed: dueList,
  turnsAfter: _lmLive('_fog').map(x => x.turns).sort(),
  stillLive: _lmLive('_fog').length,
};

/* ── 5. REMOVING A DIE RE-KEYS THE MAP ────────────────────────────── */
reset();
_lmArm('_fog', 1, 1); _lmArm('_snare', 4, 1);
const removed = (typeof _oRemoveOppDieAt === 'function' && G.matchOppDice &&
                 G.matchOppDice.length > 2) ? _oRemoveOppDieAt(2) : null;
out.removalRekeys = {
  drove: removed !== null,
  /* lane 1 is below the removal and must not move; lane 4 is above and shifts */
  laneOneStill: !!(_lmMap()[1] && _lmMap()[1].live),
  laneFourMovedToThree: !!(_lmMap()[3] && _lmMap()[3].live && _lmMap()[3].t === '_snare'),
  noStaleFour: !(_lmMap()[4] && _lmMap()[4].live),
};

/* ── 6. A MARK ON THE REMOVED LANE DIES WITH THE DIE ──────────────── */
reset();
_lmArm('_fog', 2, 1);
const removed2 = (typeof _oRemoveOppDieAt === 'function' && G.matchOppDice &&
                  G.matchOppDice.length > 2) ? _oRemoveOppDieAt(2) : null;
out.markDiesWithItsDie = {
  drove: removed2 !== null,
  noLiveMarks: _lmLive().length === 0,
};

try { G._laneMark = {}; } catch (e) {}

out.VERDICT = {
  theSeamIsThere: Object.keys(out.seam).every(k => out.seam[k] === true),
  /* THE CASE THE RULING EXISTS FOR */
  twoFogsOnTwoLanesBothLive: out.twoFogs.liveCount === 2 &&
    out.twoFogs.firstArmed === true && out.twoFogs.secondArmed === true,
  /* AND THE CASE IT FORBIDS - both types, so a same-type-only guard fails here */
  aSecondMarkOnOneLaneIsRefused:
    out.oneLane.snuffRefused === true && out.oneLane.fogAgainRefused === true,
  onlyOneMarkSurvivesThatLane: out.oneLane.liveCount === 1 &&
    out.oneLane.theSurvivorIsTheFirst === true,
  occupancyAgrees: out.oneLane.occupiedReportsTaken === true,
  /* a refusal must not be permanent */
  aSpentMarkFreesItsSpot: out.spentFreesTheSpot.laneReArmed === true &&
    out.spentFreesTheSpot.occupiedAfterSpend === true,
  /* every due mark of a type is charged, or one lurks for ever */
  spendChargesEveryDueMark: out.spendChargesAll.dueBothArmed === 2 &&
    out.spendChargesAll.turnsAfter.join(',') === '1,1',
  /* the removal re-keys rather than nudging fields */
  removalShiftsLanesAbove: out.removalRekeys.drove ? (
    out.removalRekeys.laneOneStill === true &&
    out.removalRekeys.laneFourMovedToThree === true &&
    out.removalRekeys.noStaleFour === true) : null,
  aMarkOnTheRemovedLaneDies: out.markDiesWithItsDie.drove
    ? out.markDiesWithItsDie.noLiveMarks === true : null,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
