/* Two questions, one page load.
 *
 * A. THE BAND, FROM THE CONTAINERS. I measured the contents and got zero-height
 *    rows, then called that a scope limit. It was the wrong measurement: the
 *    three containers reserve their height whether or not dice are in them, and
 *    the file says so three times over ("fixed height to prevent shifts", "so
 *    the throwing row never moves", "RESERVED, not grown into"). Both dice rows
 *    share the throw-line cell, so there is no gap between them to span. The
 *    band is union(#aboveDiceInfo, #throwLine, #keptZone) plus the glow's reach,
 *    readable once per layout instead of sampled across turns.
 *    Reported against the hulls as well: the contents must fall INSIDE the
 *    containers, and if they do not, the containers are the wrong answer too.
 *
 * B. WHY TWO IDENTICAL PAINTS DIFFER. P889b called it a first-paint artefact;
 *    P903 measured it recurring between adjacent paints and called it a noise
 *    floor. Both are descriptions. Denis's hypothesis is a cause: the mip
 *    resample, where imageSmoothingEnabled leaves the browser free to pick a
 *    kernel per call - which PREDICTS the floor falls when there are fewer
 *    resample steps.
 *    The flight path is exactly that experiment, free: rimPasses 5 to 1 removes
 *    four full-screen upscale composites per call, 15 resample steps to 11. So
 *    measure the floor at BOTH qualities.
 *      floor unchanged            -> the hypothesis is wrong, look elsewhere
 *      floor falls ~ 11/15        -> proportional to resample steps
 *      floor falls much further   -> the final upscales dominate (6 to 2)
 *    All three outcomes are informative, which is what makes it worth minutes.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const rs = await FXH.rollAndSettle();
out.rolled = {ok: rs.ok, why: rs.why, freeDice: rs.freeDice};
if (!(rs.freeDice > 0)) return Object.assign(out, {err: 'no dice: ' + rs.why});

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
const GL = D3X.GLOW;                    /* never `G` - see P904 */
out.screen = {w: Math.round(sc.width), h: Math.round(sc.height)};

/* ── A. the containers ─────────────────────────────────────────────── */
const box = id => { const el = document.getElementById(id);
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {id, top: +(r.top - sc.top).toFixed(1), bottom: +(r.bottom - sc.top).toFixed(1),
          left: +(r.left - sc.left).toFixed(1), right: +(r.right - sc.left).toFixed(1),
          h: +r.height.toFixed(1)}; };
const boxes = ['aboveDiceInfo', 'throwLine', 'keptZone'].map(box);
out.containers = boxes;
const present = boxes.filter(Boolean);
const reach = {y: GL.soft * GL.sy + GL.line / 2 + GL.clear,
               x: GL.soft * GL.sx + GL.line / 2 + GL.clear};
const band = present.length ? {
  top: +(Math.min.apply(null, present.map(b => b.top)) - reach.y).toFixed(1),
  bottom: +(Math.max.apply(null, present.map(b => b.bottom)) + reach.y).toFixed(1),
} : null;
if (band) { band.h = +(band.bottom - band.top).toFixed(1);
            band.fractionOfScreen = +(band.h / sc.height).toFixed(3); }
out.band = band;
out.reach = {y: +reach.y.toFixed(1), x: +reach.x.toFixed(1)};

/* the contents must fall inside the containers, or the containers are wrong */
const hulls = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip)
  .map(d => D3X._hullOf(d, sc, GL.grow)).filter(Boolean);
let hTop = 1e9, hBot = -1e9;
hulls.forEach(h => h.forEach(p => { if (p[1] < hTop) hTop = p[1];
                                    if (p[1] > hBot) hBot = p[1]; }));
out.contents = hulls.length ? {top: +hTop.toFixed(1), bottom: +hBot.toFixed(1),
                               dice: hulls.length} : null;

/* HOW FAR THE MESH FLOATS ABOVE ITS SLOT, sampled across a real throw. The
   containers do not contain the dice: a die's mesh is drawn above its DOM slot,
   which the file already documents as the reason anything placed off the row
   lands on the dice. So the band's top needs a pad, and the pad is bigger in
   flight than at rest - it has to be measured, not assumed. */
const throwTop = (box('throwLine') || {}).top;
const riseNow = () => { const hs = D3X.dice
    .filter(d => d.match && d.obj && d.obj.visible && d.chip)
    .map(d => D3X._hullOf(d, sc, GL.grow)).filter(Boolean);
  if (!hs.length || throwTop == null) return null;
  let t = 1e9; hs.forEach(h => h.forEach(p => { if (p[1] < t) t = p[1]; }));
  return +(throwTop - t).toFixed(1); };
const rises = [];
const rAtRest = riseNow();
const freeD = G.pool.filter(d => !d.committed && !d._frozen && d.el);
freeD.slice(0, 2).forEach(d => {
  try { _setDieVal(d, (typeof rollFaceExclude === 'function')
    ? rollFaceExclude(d.mat, d.val, d) : (d.val % 6) + 1); } catch (e) {}
});
const tR = Date.now();
let sawR = false;
while (Date.now() - tR < 12000) {
  const r = riseNow(); if (r != null) rises.push(r);
  const n = D3X.dice.filter(d => d.match && d.roll).length;
  if (n > 0) sawR = true;
  await FXH.sleep(50);
  if (sawR && n === 0) break;
}
out.meshRise = {atRest: rAtRest, samples: rises.length,
                sawFlight: sawR,
                max: rises.length ? Math.max.apply(null, rises) : null,
                min: rises.length ? Math.min.apply(null, rises) : null};
out.meshRise.padNeeded = (out.meshRise.max != null)
  ? +(out.meshRise.max + reach.y).toFixed(1) : null;

const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);
/* the band the measurement actually supports: the containers, the mesh rise
   above them, and the glow's reach on both edges */
out.bandCorrected = (band && out.meshRise.padNeeded != null) ? (function () {
  const top = +(band.top - out.meshRise.max).toFixed(1);
  const h = +(band.bottom - top).toFixed(1);
  return {top, bottom: band.bottom, h,
          fractionOfScreen: +(h / sc.height).toFixed(3)};
})() : null;
out.saving = band ? {
  dpr,
  fullScreenMB: +(sc.width * dpr * sc.height * dpr * 4 / 1048576).toFixed(2),
  bandMB: +(sc.width * dpr * band.h * dpr * 4 / 1048576).toFixed(2),
  correctedMB: out.bandCorrected
    ? +(sc.width * dpr * out.bandCorrected.h * dpr * 4 / 1048576).toFixed(2) : null,
} : null;

/* ── B. the floor, at both qualities ───────────────────────────────── */
const STATE = ['die-frozen', 'die-dampened', 'dampen-fade', 'die-blind', 'selected'];
const dice = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip);
dice.forEach(d => d.chip.classList.remove.apply(d.chip.classList, STATE));
dice[0].chip.classList.add('die-dampened');
if (dice[1]) dice[1].chip.classList.add('die-frozen');

const proto = CanvasRenderingContext2D.prototype;
const realDraw = proto.drawImage;
let draws = 0;
proto.drawImage = function () { draws++; return realDraw.apply(this, arguments); };
const realRolling = D3X._rolling;
const paint = (flying) => {
  D3X._rolling = function () { return !!flying; };
  D3X._glowSig = '';
  const b = draws;
  try { D3X._drawGlow(); } catch (e) {}
  D3X._rolling = realRolling;
  return draws - b;
};
const px = () => { const cv = document.getElementById('dgCanvas');
  return cv && cv.width
    ? new Uint8ClampedArray(cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data)
    : null; };
const diff = (a, b) => { if (!a || !b || a.length !== b.length) return -1;
  let n = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) n++; return n; };

/* COUNTERBALANCED, because the first version was not. It ran three full paints
   then three cheap ones and reported the cheap block byte-identical - but the
   cheap block came fourth through ninth, and the full pairs [219, 0, 219] show
   the surface takes TWO paints to stabilise. "Fewer passes" and "later in the
   sequence" were the same variable. Here each quality runs both first and
   second, so a floor that follows quality shows up in both full blocks and a
   floor that follows position shows up in whichever block leads. */
paint(false);                              /* create/size the scratches */
const trio = (flying) => { const n = paint(flying); const a = px();
  paint(flying); const b = px(); paint(flying); const c = px();
  return {draws: n, pairs: [diff(a, b), diff(b, c), diff(a, c)]}; };

const blockA_cheapFirst = trio(true);
const blockA_fullSecond = trio(false);
/* reset the surfaces the way the run started, so the second block begins from
   the same place the first did rather than from wherever the first left it */
const cv0 = document.getElementById('dgCanvas');
if (cv0) { cv0.width = cv0.width; }        /* a resize clears and re-backs it */
paint(false);
const blockB_fullFirst = trio(false);
const blockB_cheapSecond = trio(true);
proto.drawImage = realDraw;

const mean = a => a.length ? +(a.reduce((t, x) => t + x, 0) / a.length).toFixed(1) : null;
out.floor = {
  drawsFull: blockA_fullSecond.draws, drawsFlight: blockA_cheapFirst.draws,
  cheapWhenFirst: blockA_cheapFirst.pairs, fullWhenSecond: blockA_fullSecond.pairs,
  fullWhenFirst: blockB_fullFirst.pairs, cheapWhenSecond: blockB_cheapSecond.pairs,
};
out.floor.byQuality = {
  full: mean(out.floor.fullWhenFirst.concat(out.floor.fullWhenSecond)),
  flight: mean(out.floor.cheapWhenFirst.concat(out.floor.cheapWhenSecond)),
};
out.floor.byPosition = {
  first: mean(out.floor.cheapWhenFirst.concat(out.floor.fullWhenFirst)),
  second: mean(out.floor.fullWhenSecond.concat(out.floor.cheapWhenSecond)),
};
const qF = out.floor.byQuality.full, qL = out.floor.byQuality.flight;
const pF = out.floor.byPosition.first, pS = out.floor.byPosition.second;
out.prediction = {
  hypothesis: 'the mip resample picks a kernel per call, so fewer resample ' +
              'steps means a smaller floor',
  /* the two explanations, scored against the same numbers */
  qualityEffect: (qF != null && qL != null) ? +(qF - qL).toFixed(1) : null,
  positionEffect: (pF != null && pS != null) ? +(pF - pS).toFixed(1) : null,
  itFollowsQuality: qF != null && qL != null && pF != null && pS != null &&
    Math.abs(qF - qL) > Math.abs(pF - pS) * 2 && qF > qL,
  itFollowsPosition: qF != null && qL != null && pF != null && pS != null &&
    Math.abs(pF - pS) > Math.abs(qF - qL) * 2,
  noFloorAnywhere: qF === 0 && qL === 0,
};

dice.forEach(d => d.chip.classList.remove.apply(d.chip.classList, STATE));

out.VERDICT = {
  /* A */
  allThreeContainersExist: boxes.every(Boolean),
  theyReserveHeight: present.every(b => b.h > 0),
  theyAreContiguous: (function () {
    const s = present.slice().sort((a, b) => a.top - b.top);
    for (let i = 1; i < s.length; i++) if (s[i].top - s[i - 1].bottom > 24) return false;
    return true;
  })(),
  /* the containers alone do NOT contain the dice - that is the finding, so it
     is asserted in the direction it was measured rather than hidden */
  theContainersAloneDoNotContainTheDice: !!out.contents && !!band &&
    out.contents.top < band.top,
  theCorrectedBandDoesContainThem: !!out.bandCorrected && !!out.contents &&
    out.contents.top >= out.bandCorrected.top &&
    out.contents.bottom <= out.bandCorrected.bottom,
  theMeshRiseWasMeasuredInFlight: out.meshRise.sawFlight === true &&
                                  out.meshRise.samples >= 5,
  theBandIsStillWorthCutting: !!out.bandCorrected &&
    out.bandCorrected.fractionOfScreen < 0.5,
  /* B - the instrument first */
  theFloorIsNonZero: out.floor.meanFull > 0,
  theQualitiesReallyDiffer: out.floor.drawsFlight < out.floor.drawsFull,
  /* and the prediction resolves to exactly one of three */
  thePredictionResolves: [out.prediction.falsifiedIfFloorUnchanged,
                          out.prediction.proportionalToSteps,
                          out.prediction.dominatedByFinalUpscales]
                         .filter(Boolean).length === 1,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
