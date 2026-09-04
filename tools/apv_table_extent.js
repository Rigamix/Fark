/* RULING 3.12: CAN THE UNDER-CANVAS REACH THE RIVAL'S SIDE OF THE TABLE?
 *
 * Denis's caution is the whole reason this runs before any paint code:
 * #dgCanvas was built as the DIE-HALO painter, so it may well be sized to the
 * player's dice area and not to the table. If it does not span the rival's row
 * the cloud cannot be painted there at all, and the ruling needs a different
 * surface - which is a decision, not a bug to discover halfway through a patch.
 *
 * THE SECOND MEASUREMENT IS THE ONE THE RULING ACTUALLY DEPENDS ON. The mark
 * appears at BANK and must sit at lane N on the rival's side for the whole
 * window before their dice arrive - and that window is exactly when their row
 * is empty. The file says in a comment that #oppDiceRow "collapses to zero"
 * when empty. A comment is not a measurement, so the empty rect is read
 * directly, at the moment the game is really in it.
 *
 * WHAT ELSE PRODUCES A ZERO HERE, named first: the canvas is created lazily by
 * _drawGlow and the harness may return before it is sized (P899a), so a missing
 * or 300x150 canvas means "the painter never ran", not "the canvas is small".
 * `sized` is reported against what the painters actually use, separately from
 * the rect.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

const R = (el) => {
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: Math.round(r.left), y: Math.round(r.top),
          w: Math.round(r.width), h: Math.round(r.height),
          right: Math.round(r.right), bottom: Math.round(r.bottom)};
};
const byId = (id) => R(document.getElementById(id));

/* does rect A fully contain rect B? and if not, by how much does B escape? */
const contains = (a, b) => {
  if (!a || !b || !b.w || !b.h) return null;
  return {inside: a.x <= b.x && a.y <= b.y && a.right >= b.right && a.bottom >= b.bottom,
          overhangTop: Math.max(0, a.y - b.y), overhangBottom: Math.max(0, b.bottom - a.bottom),
          overhangLeft: Math.max(0, a.x - b.x), overhangRight: Math.max(0, b.right - a.right)};
};

function survey(tag) {
  return {
    tag, phase: (typeof G !== 'undefined' && G) ? G.phase : null,
    dg: byId('dgCanvas'), st: byId('stCanvas'), d3x: byId('d3xCanvas'),
    screenMatch: byId('screen-match'),
    playerRow: byId('playerDiceRow'), oppRow: byId('oppDiceRow'),
    oppRowChildren: (document.getElementById('oppDiceRow') || {children: []}).children.length,
    dgSized: FXH.sizedOf(document.getElementById('dgCanvas')),
    stSized: FXH.sizedOf(document.getElementById('stCanvas')),
    expected: FXH.expectedSize(),
    /* the seat rects, so a lane -> x mapping can be compared against something */
    seats: [].slice.call(
      (document.getElementById('oppDiceRow') || {children: []}).children).map(R),
    playerSeats: [].slice.call(
      (document.getElementById('playerDiceRow') || {children: []}).children).map(R),
  };
}

/* ── 1. the player's turn: the rival's row is EMPTY ───────────────── */
const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};
FXH.draw();                       /* force the painter so the canvas exists+sizes */
out.emptyWindow = survey('player turn - the rival row is empty');

/* ── 2. the rival's turn: the row is dealt ────────────────────────── */
try {
  const free = ((G && G.pool) || []).filter(d => !d.committed);
  free.forEach(d => { if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el); });
} catch (e) {}
try { endPTurn(); } catch (e) {}
const dealt = await FXH.until(() => (G.phase === 'opp' || G._oppTurnActive) &&
  ((G.oppDice || []).length > 0) &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);
out.reachedOpp = dealt;
if (dealt != null) { FXH.draw(); out.dealtWindow = survey('rival turn - the row is dealt'); }
try { clearInterval(_ff); } catch (e) {}

const E = out.emptyWindow, D = out.dealtWindow;
out.reach = {
  /* THE QUESTION DENIS ASKED */
  dgCoversOppRowWhenDealt: D ? contains(D.dg, D.oppRow) : null,
  dgCoversPlayerRow: E ? contains(E.dg, E.playerRow) : null,
  dgIsTheWholeScreen: E && E.dg && E.screenMatch
    ? (E.dg.w >= E.screenMatch.w - 2 && E.dg.h >= E.screenMatch.h - 2) : null,
  /* THE CLAIM IN THE COMMENT, measured */
  emptyOppRowRect: E ? E.oppRow : null,
  emptyOppRowCollapses: E && E.oppRow ? (E.oppRow.h < 4 || E.oppRow.w < 4) : null,
  /* is there any usable seat geometry while empty? */
  seatsWhileEmpty: E ? E.seats.length : null,
  seatsWhenDealt: D ? D.seats.length : null,
};
out.VERDICT = {
  theCanvasExistsAndIsSized: !!(E && E.dg && E.dgSized === true),
  /* a reading from an unsized canvas says nothing, so this gates the rest */
  reachedTheRivalTurn: dealt != null,
  dgSpansTheRivalRow: out.reach.dgCoversOppRowWhenDealt
    ? out.reach.dgCoversOppRowWhenDealt.inside === true : null,
  dgSpansThePlayerRow: out.reach.dgCoversPlayerRow
    ? out.reach.dgCoversPlayerRow.inside === true : null,
  /* NOT a pass/fail - the answer decides the design, so it is reported as a
     fact and read by a human. Left here so the shape is visible in FAILED. */
  theEmptyRowHasUsableGeometry: out.reach.emptyOppRowCollapses === false,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
