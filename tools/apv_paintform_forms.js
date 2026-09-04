/* P949: the three forms still paint, and a fourth one fails loudly.
 *
 * THE REGRESSION IS THE IMPORTANT HALF. Naming `rim` changed the live dispatch
 * every selection, card mark and reroll state goes through, so "an unknown style
 * throws" is worth nothing if the known ones stopped painting. The selection is
 * driven through the REAL pass - FXH.paintWith runs _drawGlow on real dice - and
 * read back as pixels, not as a return value.
 *
 * AND THE UNKNOWN-STYLE ARM IS CALLED DIRECTLY, because inside the frame pass a
 * throw is swallowed by tick()'s bare catch and the probe would learn nothing
 * from it either way. Direct is where the throw is observable, which is also
 * why the patch logs as well as throws.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};
if (!r.ok) return Object.assign(out, {err: 'no dice to paint'});

/* ── 1. THE REGRESSION: a selection still lights the under-canvas ─── */
const lit = FXH.paintWith(() => {
  FXH.clearMarks();
  const free = ((G && G.pool) || []).filter(d => !d.committed);
  if (free[0] && free[0].el) free[0].el.classList.add('selected');
});
out.selectionPaint = {exists: lit.exists, sized: lit.sized, px: lit.px,
                      threw: lit.drawThrew || null};

/* a second form through the same pass, so `rim` is not the only one proven */
const crust = FXH.paintWith(() => {
  FXH.clearMarks();
  const free = ((G && G.pool) || []).filter(d => !d.committed);
  if (free[0] && free[0].el) free[0].el.classList.add('die-frozen');
});
out.crustPaint = {exists: crust.exists, px: crust.px, threw: crust.drawThrew || null};
try {
  ((G && G.pool) || []).forEach(d => d.el && d.el.classList.remove('die-frozen'));
} catch (e) {}

/* ── 2. the direct calls, where a throw is observable ─────────────── */
const cv = document.getElementById('dgCanvas');
const sc = document.getElementById('screen-match').getBoundingClientRect();
const ctx = cv ? cv.getContext('2d') : null;
const dpr = Math.min(devicePixelRatio || 1, (window.D3X && D3X.GLOW_DPR_MAX) || 3);
const hull = (window.D3X && D3X._rectHull)
  ? D3X._rectHull(100, 400, 60, 60, 20) : null;
out.rectHullPoints = hull ? hull.length : null;

const tryForm = (style) => {
  if (!ctx || !hull) return {ran: false, why: 'no canvas or hull'};
  try {
    D3X._paintForm(style, cv, ctx, sc, dpr, [hull], '#a8b0b8', '#a8b0b8', 1, false, false);
    return {ran: true, threw: null};
  } catch (e) { return {ran: true, threw: (e && e.message) || String(e)}; }
};
out.forms = {
  rim: tryForm('rim'), crust: tryForm('crust'), veil: tryForm('veil'),
  unknown: tryForm('squircle'),
  unknownAgain: tryForm('squircle'),   /* the dedupe must not stop the throw */
};
out.badFormsRecorded = (window.D3X && D3X._badForms)
  ? Object.keys(D3X._badForms) : null;

out.VERDICT = {
  /* the probe could see anything at all */
  theCanvasWasSized: out.selectionPaint.sized === true,
  /* THE REGRESSION - both a rim row and a crust row still reach the canvas */
  aSelectionStillPaints: out.selectionPaint.px > 0 && !out.selectionPaint.threw,
  aCrustStillPaints: out.crustPaint.px > 0 && !out.crustPaint.threw,
  /* the reused hull producer is real */
  rectHullReturnsAPolygon: out.rectHullPoints >= 12,
  /* the three named forms do not throw on a die-free hull */
  rimAccepted: out.forms.rim.threw === null,
  crustAccepted: out.forms.crust.threw === null,
  veilAccepted: out.forms.veil.threw === null,
  /* and the fourth fails */
  anUnknownStyleThrows: typeof out.forms.unknown.threw === 'string' &&
    out.forms.unknown.threw.indexOf('unknown style') >= 0,
  /* the log dedupes but the THROW does not - a second call must still fail */
  theDedupeOnlySilencesTheLog: typeof out.forms.unknownAgain.threw === 'string',
  itRecordedTheBadStyle: !!(out.badFormsRecorded &&
    out.badFormsRecorded.indexOf('squircle') >= 0),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
