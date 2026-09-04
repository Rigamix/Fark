/* THE TWO PREREQUISITES FOR RULING 3.12, MEASURED DETERMINISTICALLY.
 *
 * Both were nearly taken on trust, and both are load-bearing: if either is
 * false the ruling cannot be built as specified.
 *
 * 1. THE ANCHOR SURVIVES AN EMPTY LINE. The mark appears at bank and must sit
 *    at a lane while NEITHER row holds dice. apv_throwline_window claimed this
 *    and its claim was vacuous - at _ffMult 0.05 the rival's dice arrived
 *    before the sample, so "the box when empty" was measured with six dice in
 *    it. The state is produced here rather than raced for: both rows are
 *    cleared through the game's own clearRow and the cell is read.
 *    CSS says .throw-line>*{grid-area:1/1} with min-height:13cqw, so the
 *    prediction is that it holds. A prediction is not a measurement.
 *
 * 2. THE UNDER-CANVAS CAN BE WOKEN WITH NO DIE WEARING ANYTHING. Measured
 *    already, in passing: #dgCanvas was NULL through the whole player turn and
 *    only appeared once the rival's dice were up. It is created lazily by the
 *    paint pass, and the pass sleeps when no MARKS row matches a die. A table
 *    mark has no die, so on the current wake condition it would paint into a
 *    canvas that does not exist - silently, with no error, which is this
 *    layer's signature failure. This measures the sleep directly.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const R = (el) => {
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: Math.round(r.left), y: Math.round(r.top),
          w: Math.round(r.width), h: Math.round(r.height)};
};
const kids = (id) => (document.getElementById(id) || {children: []}).children.length;

const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};

/* ── 1. both rows full-then-empty, produced not raced ─────────────── */
out.withDice = {throwLine: R(document.getElementById('throwLine')),
                playerKids: kids('playerDiceRow'), oppKids: kids('oppDiceRow'),
                seatXs: [].slice.call(document.getElementById('playerDiceRow').children)
                  .map(e => Math.round(e.getBoundingClientRect().left)),
                seatW: Math.round((document.getElementById('playerDiceRow')
                  .children[0] || {getBoundingClientRect: () => ({width: 0})})
                  .getBoundingClientRect().width)};
try { clearRow('playerDiceRow'); clearRow('oppDiceRow'); } catch (e) { out.clearErr = e.message; }
await FXH.sleep(60);
out.bothEmpty = {throwLine: R(document.getElementById('throwLine')),
                 playerRow: R(document.getElementById('playerDiceRow')),
                 oppRow: R(document.getElementById('oppDiceRow')),
                 playerKids: kids('playerDiceRow'), oppKids: kids('oppDiceRow')};

/* ── 2. the wake condition with nothing worn ──────────────────────── */
const cvNow = () => {
  const cv = document.getElementById('dgCanvas');
  return cv ? {exists: true, w: cv.width, h: cv.height,
               sized: FXH.sizedOf(cv)} : {exists: false};
};
out.canvasBeforeDraw = cvNow();
/* nothing is selected or card-marked, and no state class is on any die, so no
   MARKS row matches: this is the sleeping case */
try { FXH.clearMarks(); } catch (e) {}
const drewClean = FXH.draw();
out.drawThrewClean = drewClean;
out.canvasAfterCleanDraw = cvNow();
out.marksLiveUnder = (typeof D3X !== 'undefined' && D3X._marksLive)
  ? D3X._marksLive('under', false) : null;
out.marksLiveOver = (typeof D3X !== 'undefined' && D3X._marksLive)
  ? D3X._marksLive('over', false) : null;
out.planUnder = (typeof D3X !== 'undefined' && D3X._markPlan)
  ? (D3X._markPlan('under', document.getElementById('screen-match'), false) || []).length
  : null;

out.VERDICT = {
  /* the state under test was actually produced */
  bothRowsWereEmptied: out.bothEmpty.playerKids === 0 && out.bothEmpty.oppKids === 0,
  /* 1. THE ANCHOR */
  throwLineHoldsItsBoxWithBothRowsEmpty: !!out.bothEmpty.throwLine &&
    out.bothEmpty.throwLine.w > 10 && out.bothEmpty.throwLine.h > 10,
  theAnchorDidNotMoveWhenTheDiceLeft: !!out.withDice.throwLine &&
    out.withDice.throwLine.x === out.bothEmpty.throwLine.x &&
    out.withDice.throwLine.y === out.bothEmpty.throwLine.y &&
    out.withDice.throwLine.w === out.bothEmpty.throwLine.w,
  /* and the rows themselves are useless as anchors, which is why it matters */
  theRowsCollapseAsTheFileSays: !!out.bothEmpty.oppRow &&
    (out.bothEmpty.oppRow.w < 4 || out.bothEmpty.oppRow.h < 4),
  /* 2. THE WAKE - reported as a FACT, not a pass. If the pass sleeps with
     nothing worn, a table mark needs the wake condition widened; that is a
     build requirement, not a defect. */
  thePassSleepsWithNothingWorn: out.marksLiveUnder === false,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
