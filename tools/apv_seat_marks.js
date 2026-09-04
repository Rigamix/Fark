/* P951: three silhouettes, two endings, and pixels on the table.
 *
 * WHAT THIS HAS TO RULE OUT, stated first because each has a way of passing:
 *  - "a mark paints" passes on a mark painted in the wrong place, so the
 *    geometry is checked against the measured seats independently.
 *  - "three forms exist" passes on one shape in three colours, which is the
 *    exact version the ruling forbids. The polygons are compared to each other:
 *    aspect ratio and point count must differ, not just the ink.
 *  - "the endings work" passes on a fire and a miss that render identically.
 *    Both are driven to the same age and their plans compared.
 *  - and a canvas reading of zero can mean the painter never ran, so `exists`
 *    and `sized` are read separately from `px`, as the harness insists.
 *
 * The screenshot is the point of the exercise, though: a squircle-versus-cloud
 * judgement is Denis's, and only the picture can put it to him.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};

const SR = document.getElementById('screen-match').getBoundingClientRect();

/* land one of each type, entrances already complete */
const land = (type, lane, ageMs, extra) => {
  const mk = {t: type, lane: lane, live: true, turn: 1, turns: 1,
              armedOn: 0, shownAt: Date.now() - (ageMs == null ? 3000 : ageMs),
              flourish: true};
  if (extra) for (const k in extra) mk[k] = extra[k];
  G._laneMark[lane] = mk;
  return mk;
};
try { G._laneMark = {}; } catch (e) {}
land('_fog', 1); land('_snare', 3); land('_snuff', 5);

/* ── geometry ─────────────────────────────────────────────────────── */
out.bounds = [1, 3, 5].map(L => {
  const b = D3X._seatBounds(L, SR);
  return b ? {lane: L, cx: Math.round(b.cx), cy: Math.round(b.cy),
              w: Math.round(b.w), how: b.how} : {lane: L, err: 'null'};
});
out.measuredSeats = [].slice.call(document.getElementById('playerDiceRow').children)
  .map(e => { const q = e.getBoundingClientRect();
              return Math.round(q.left - SR.left + q.width / 2); });

/* ── the three silhouettes must actually differ ───────────────────── */
const box = {cx: 200, cy: 455, w: 56, h: 56};
const shape = (n) => D3X._seatShape(n, box, 0.4, 1);
const metrics = (p) => {
  if (!p || !p.length) return null;
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
  p.forEach(q => { x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]);
                   y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); });
  return {n: p.length, w: +(x1 - x0).toFixed(1), h: +(y1 - y0).toFixed(1),
          aspect: +((x1 - x0) / Math.max(0.001, y1 - y0)).toFixed(2)};
};
out.shapes = {cloud: metrics(shape('cloud')), cord: metrics(shape('cord')),
              wisp: metrics(shape('wisp')), fallback: metrics(shape('nosuch'))};

/* ── the plan, and the wake ───────────────────────────────────────── */
out.plan = (D3X._seatPlan(SR) || []).map(g => ({style: g.style, col: g.col,
  am: +g.am.toFixed(2), pts: g.hulls[0].length}));
out.seatsLive = D3X._seatsLive();
/* an ARMED but unlanded mark must paint nothing */
try { G._laneMark = {}; _lmArm('_fog', 1, 1); } catch (e) {}
out.unlanded = {plan: (D3X._seatPlan(SR) || []).length, live: D3X._seatsLive()};

/* ── pixels, through the real pass ────────────────────────────────── */
try { G._laneMark = {}; } catch (e) {}
land('_fog', 1); land('_snare', 3); land('_snuff', 5);
FXH.clearMarks();
const painted = FXH.paintWith(() => {});
out.painted = {exists: painted.exists, sized: painted.sized, px: painted.px,
               threw: painted.drawThrew || null};
out.hue = FXH.hue('dgCanvas');

/* ── the two endings must not render the same ─────────────────────── */
const endPlan = (outcome) => {
  try { G._laneMark = {}; } catch (e) {}
  land('_fog', 2, 3000, {live: false, outcome: outcome, hit: outcome === 'fire',
                         endedAt: Date.now() - 200});
  const p = D3X._seatPlan(SR) || [];
  return p.length ? {am: +p[0].am.toFixed(3), pts: p[0].hulls[0].length,
                     x: Math.round(p[0].hulls[0][0][0]),
                     y: Math.round(p[0].hulls[0][0][1])} : null;
};
out.endings = {fire: endPlan('fire'), miss: endPlan('miss')};

/* ── the signature must move as the animation does ────────────────── */
try { G._laneMark = {}; } catch (e) {}
const mk = land('_fog', 3, 0);        /* mid-entrance */
const sigA = D3X._planSig(D3X._markPlan('under', SR, false));
mk.shownAt = Date.now() - 300;        /* later in the same entrance */
const sigB = D3X._planSig(D3X._markPlan('under', SR, false));
out.signature = {moves: sigA !== sigB, aLen: sigA.length, bLen: sigB.length};

/* leave the three on screen for the screenshot */
try { G._laneMark = {}; } catch (e) {}
land('_fog', 1); land('_snare', 3); land('_snuff', 5);
FXH.draw();
await FXH.sleep(400);

out.VERDICT = {
  theCanvasWasSized: out.painted.sized === true,
  /* geometry: with the row populated the lanes must line up with real seats */
  boundsAreOnTheSeats: out.bounds.every(b => !b.err) &&
    out.measuredSeats.length > 0 &&
    out.bounds.every(b => out.measuredSeats.some(x => Math.abs(x - b.cx) <= 2)),
  /* THREE FORMS, not one recoloured */
  threeShapesExist: !!(out.shapes.cloud && out.shapes.cord && out.shapes.wisp),
  theShapesActuallyDiffer:
    out.shapes.cloud.aspect !== out.shapes.cord.aspect &&
    out.shapes.cord.aspect !== out.shapes.wisp.aspect &&
    out.shapes.cloud.aspect !== out.shapes.wisp.aspect,
  cordIsWideAndFlat: out.shapes.cord.aspect > 2.2,
  wispIsNarrowAndTall: out.shapes.wisp.aspect < 0.8,
  cloudIsWiderThanTall: out.shapes.cloud.aspect > 1.2 &&
                        out.shapes.cloud.aspect < 2.6,
  /* a missing silhouette falls back to the bounds and looks wrong on purpose */
  theFallbackIsTheBounds: !!out.shapes.fallback && out.shapes.fallback.n === 20,
  /* the plan */
  threeMarksPlanned: out.plan.length === 3,
  eachInItsOwnInk: new Set(out.plan.map(g => g.col)).size === 3,
  /* AN ARMED MARK THAT NEVER BANKED PAINTS NOTHING - 3.13's jeopardy made
     visible, and the check that a landed-only gate actually gates */
  anUnlandedMarkIsInvisible: out.unlanded.plan === 0 && out.unlanded.live === false,
  /* pixels */
  itPaintsOnTheTable: out.painted.px > 0 && !out.painted.threw,
  /* two endings */
  bothEndingsRender: !!(out.endings.fire && out.endings.miss),
  theEndingsDiffer: !!(out.endings.fire && out.endings.miss) &&
    (out.endings.fire.am !== out.endings.miss.am ||
     out.endings.fire.x !== out.endings.miss.x),
  /* and the cache can see the animation */
  theSignatureTracksAlpha: out.signature.moves === true,
  theWakeSeesTheTable: out.seatsLive === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
