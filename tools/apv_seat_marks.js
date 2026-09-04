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
/* P952: a seat group carries a painter and a box, not a hull - its body is
   built from puffs at paint time, so there is nothing to serialise. */
out.plan = (D3X._seatPlan(SR) || []).map(g => ({seat: !!g.seat,
  body: g.form && g.form.body, col: g.col, am: +g.am.toFixed(2),
  w: Math.round(g.b.w), cx: Math.round(g.b.cx), sig: !!g.sig}));
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

/* PER-LANE STRENGTH, because "I cannot see it" is not a measurement and the
   whole-canvas hue cannot say WHICH mark is carrying the pixels. Reads the
   under-canvas in a box around each lane centre and reports mean alpha and the
   mean ink - so a mark that is painting but too faint is distinguishable from
   one that is not painting at all, which look identical in a screenshot. */
out.perLane = (function () {
  const cv = document.getElementById('dgCanvas');
  if (!cv || !cv.width) return null;
  const dpr = cv.width / SR.width;
  const ctx = cv.getContext('2d');
  return [1, 3, 5].map(L => {
    const b = D3X._seatBounds(L, SR);
    if (!b) return {lane: L, err: 'no bounds'};
    const x0 = Math.max(0, Math.round((b.cx - 34) * dpr));
    const y0 = Math.max(0, Math.round((b.cy - 26) * dpr));
    const w = Math.min(cv.width - x0, Math.round(68 * dpr));
    const h = Math.min(cv.height - y0, Math.round(52 * dpr));
    if (w < 2 || h < 2) return {lane: L, err: 'off canvas'};
    const d = ctx.getImageData(x0, y0, w, h).data;
    let n = 0, sa = 0, sr = 0, sg = 0, sb = 0, peak = 0;
    for (let i = 0; i < d.length; i += 4) {
      const a = d[i + 3];
      sa += a; if (a > peak) peak = a;
      if (a > 12) { n++; sr += d[i]; sg += d[i + 1]; sb += d[i + 2]; }
    }
    const px = (d.length / 4);
    return {lane: L, meanAlpha: +(sa / px).toFixed(1), peakAlpha: peak,
            coverage: +(n / px).toFixed(3),
            ink: n ? '#' + [sr / n, sg / n, sb / n].map(v =>
              Math.round(v).toString(16).padStart(2, '0')).join('') : null};
  });
})();

/* ── the two endings must not render the same ─────────────────────── */
const endPlan = (outcome) => {
  try { G._laneMark = {}; } catch (e) {}
  land('_fog', 2, 3000, {live: false, outcome: outcome, hit: outcome === 'fire',
                         endedAt: Date.now() - 200});
  const p = D3X._seatPlan(SR) || [];
  return p.length ? {am: +p[0].am.toFixed(3), w: Math.round(p[0].b.w),
                     x: Math.round(p[0].b.cx), y: Math.round(p[0].b.cy)} : null;
};
out.endings = {fire: endPlan('fire'), miss: endPlan('miss')};

/* ── the signature must move as the animation does ────────────────── */
try { G._laneMark = {}; } catch (e) {}
const mk = land('_fog', 3, 0);        /* mid-entrance */
const sigA = D3X._planSig(D3X._markPlan('under', SR, false));
mk.shownAt = Date.now() - 300;        /* later in the same entrance */
const sigB = D3X._planSig(D3X._markPlan('under', SR, false));
out.signature = {moves: sigA !== sigB, aLen: sigA.length, bLen: sigB.length};

/* THE SCREENSHOT MUST BE OF THE WINDOW THE MARK IS ACTUALLY SEEN IN.
   Every shot so far put the three marks under a FULL row of dice, and
   #d3xCanvas draws those on top by design - so the fog, measured at 138/255
   mean alpha across 99.9% of its footprint, came out looking absent. That is
   the mark working exactly as specified and a probe photographing the one
   state it is never on screen in: 3.12's window is after the player banks,
   when their row has been cleared and the rival's dice have not arrived.
   Both rows are emptied through the game's own clearRow to produce it. */
try { G._laneMark = {}; } catch (e) {}
try { clearRow('playerDiceRow'); clearRow('oppDiceRow'); } catch (e) {}
await FXH.sleep(80);
land('_fog', 1); land('_snare', 3); land('_snuff', 5);
FXH.draw();
out.emptyTable = {
  playerKids: (document.getElementById('playerDiceRow') || {children: []}).children.length,
  oppKids: (document.getElementById('oppDiceRow') || {children: []}).children.length,
};
await FXH.sleep(400);

out.VERDICT = {
  theCanvasWasSized: out.painted.sized === true,
  /* geometry: with the row populated the lanes must line up with real seats */
  boundsAreOnTheSeats: out.bounds.every(b => !b.err) &&
    out.measuredSeats.length > 0 &&
    out.bounds.every(b => out.measuredSeats.some(x => Math.abs(x - b.cx) <= 2)),
  /* THREE FORMS, not one recoloured */
  /* the cord is still a silhouette - it was the one form that read - and is
     now the only body _seatShape serves; cloud and smoke are puffs. */
  cordIsWideAndFlat: out.shapes.cord.aspect > 2.2,
  /* a missing silhouette falls back to the bounds and looks wrong on purpose */
  theFallbackIsTheBounds: !!out.shapes.fallback && out.shapes.fallback.n === 20,
  /* the plan */
  threeMarksPlanned: out.plan.length === 3,
  eachInItsOwnInk: new Set(out.plan.map(g => g.col)).size === 3,
  eachWithItsOwnBody: new Set(out.plan.map(g => g.body)).size === 3,
  /* P952: every one bypasses the halo family, which is the whole patch */
  allRoutePastTheHaloPainter: out.plan.every(g => g.seat === true && g.sig === true),
  /* THE FOOTPRINT: the mark takes the seat rather than a patch between two
     dice. P951's forms were narrower than a die and read as artefacts of them. */
  theMarkFillsItsSeat: out.plan.every(g => g.w >= 56),
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
