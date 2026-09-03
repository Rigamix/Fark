/* WHERE DOES THE TURN'S VALUE LIVE AT endPTurn?
 *
 * P921b recorded each turn as G.turnPts read at the top of the endPTurn wrap,
 * on the strength of the game's own comment - "A bust is a turn worth ZERO, not
 * no turn", captured by `var _pTurnPts=(G.turnPts||0)` as endPTurn's first
 * statement, with a measured note about ten call sites. Sixteen matches then
 * recorded 0 for EVERY turn, including turns that banked 8050.
 *
 * That contradicts a load-bearing comment, so it gets measured rather than
 * reasoned about. For each turn this records, at the moment the wrap fires:
 * G.turnPts, G._pTurnPts (the previous turn's captured value), G.pPts and
 * G.kept's total - and then G._pTurnPts again AFTER the original runs, which is
 * the value endPTurn itself computed.
 *
 * IF _pTurnPts IS ALSO 0 the game's field is dead, and that matters well beyond
 * this harness: endPTurn fires famFire('rivalTurn',{actor:'o',pts:_pTurnPts}),
 * so every boss-held card listening for "the rival's turn resolved" would see
 * zero points on every turn.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const rows = [];
const origEnd = window.endPTurn;
window.endPTurn = function () {
  const before = {};
  try {
    before.turnPts = G.turnPts;
    before.pTurnPtsField = G._pTurnPts;
    before.pPts = G.pPts;
    before.keptTotal = (G.kept || []).reduce((a, k) => a + (k.pts || 0), 0);
    before.pot = G._turnBonusPot || 0;
    before.phase = G.phase;
  } catch (e) { before.err = e.message; }
  const ret = origEnd.apply(this, arguments);
  try {
    before.pTurnPtsAfter = G._pTurnPts;
    before.pPtsAfter = G.pPts;
  } catch (e) {}
  rows.push(before);
  return ret;
};

const res = await FDRV.playMatch({policy: 'bank500', timeoutMs: 200000});
window.endPTurn = origEnd;

out.match = res && res.err ? {err: res.err}
  : {pPts: res.pPts, pTurns: res.pTurns, banks: res.banks, busts: res.busts};
out.turns = rows;
/* the delta in the game's own running total across each turn - the quantity
   the resample actually needs, whatever field happens to hold it */
out.deltas = rows.map((x, i) => (x.pPtsAfter != null && x.pPts != null)
  ? x.pPtsAfter - x.pPts : null);
out.deltaSum = out.deltas.reduce((a, b) => a + (b || 0), 0);

out.VERDICT = {
  theWrapFired: rows.length > 0,
  theWrapFiredOncePerTurn: out.match.pTurns != null && rows.length === out.match.pTurns,
  /* the two candidate fields, measured rather than assumed */
  turnPtsWasZeroAtEndPTurn: rows.every(x => (x.turnPts || 0) === 0),
  theGamesOwnFieldWasAlsoZero: rows.every(x => (x.pTurnPtsAfter || 0) === 0),
  /* and whether the pPts delta is a usable substitute */
  thePPtsDeltaIsNonZero: out.deltas.some(d => d && d > 0),
  theDeltasSumToTheMatchTotal: out.match.pPts != null
    ? out.deltaSum === out.match.pPts : null,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
