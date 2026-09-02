# -*- coding: utf-8 -*-
u"""P905: the floor experiment was confounded by order, and the containers do
not contain the dice.

THE FLOOR RESULT WAS NOT A RESULT. Measured full-quality pairs [219, 0, 219]
and flight-quality pairs [0, 0, 0], which looks like the prediction confirmed -
fewer resample steps, no floor. But the flight paints came AFTER four full
paints, so "the passes are fewer" and "the scratches have had longer to settle"
are the same variable. The full pairs say why that matters: the second paint
differs from the third and the third equals the fourth, so it takes TWO paints
to stabilise, not one - and everything measured after that point is stable
whatever its quality.

So the order is counterbalanced: cheap-first-then-full in one block, full-first-
then-cheap in another, in the same run on the same dice. If the floor follows
QUALITY it appears in the full block both times; if it follows POSITION it
appears in whichever block runs first. One run separates them.

AND THE CONTAINERS ARE NOT THE CONTAINER. union(#aboveDiceInfo, #throwLine,
#keptZone) came out at 410.9-565.6, and the dice hulls reach 398.9 - twelve
pixels above the band, twenty-eight above #throwLine's own top. The file
explains it: a die's MESH is drawn above its DOM slot, which is why anything
placed off the row lands on the dice. #aboveDiceInfo also measured zero height
here rather than the reserved height the markup promises.

That does not sink the approach - it adds one constant to it, and the constant
has to be measured rather than assumed, because it is larger in flight than at
rest. So the rise above #throwLine is sampled across a real throw and reported
as what the band's top padding must clear.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'apv_band_and_floor.js')
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    s = s.replace(old, new)
    print('  ' + label)


# ── 1. the floor, counterbalanced ───────────────────────────────────
sub(u"""paint(false);                              /* create/size the scratches */
/* three adjacent paints at each quality, so the floor is a repeated
   measurement rather than one pair that could be a fluke either way */
const fullDraws = paint(false); const f1 = px();
paint(false); const f2 = px();
paint(false); const f3 = px();
const cheapDraws = paint(true); const c1 = px();
paint(true); const c2 = px();
paint(true); const c3 = px();
proto.drawImage = realDraw;

out.floor = {
  drawsFull: fullDraws, drawsFlight: cheapDraws,
  fullPairs: [diff(f1, f2), diff(f2, f3), diff(f1, f3)],
  flightPairs: [diff(c1, c2), diff(c2, c3), diff(c1, c3)],
};""",
    u"""/* COUNTERBALANCED, because the first version was not. It ran three full paints
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
};""",
    '1 the floor is counterbalanced')

sub(u"""const mean = a => a.length ? +(a.reduce((t, x) => t + x, 0) / a.length).toFixed(1) : null;
out.floor.meanFull = mean(out.floor.fullPairs);
out.floor.meanFlight = mean(out.floor.flightPairs);
out.floor.ratioMeasured = out.floor.meanFull
  ? +(out.floor.meanFlight / out.floor.meanFull).toFixed(3) : null;
out.floor.ratioIfProportionalToSteps = +(cheapDraws / fullDraws).toFixed(3);
out.prediction = {
  hypothesis: 'the mip resample picks a kernel per call, so fewer resample ' +
              'steps means a smaller floor',
  falsifiedIfFloorUnchanged: out.floor.meanFlight >= out.floor.meanFull * 0.9,
  proportionalToSteps: out.floor.ratioMeasured != null &&
    Math.abs(out.floor.ratioMeasured - out.floor.ratioIfProportionalToSteps) < 0.15,
  dominatedByFinalUpscales: out.floor.ratioMeasured != null &&
    out.floor.ratioMeasured < out.floor.ratioIfProportionalToSteps - 0.15,
};""",
    u"""const qF = out.floor.byQuality.full, qL = out.floor.byQuality.flight;
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
};""",
    '2 the prediction is scored against both explanations')

# ── 2. the mesh rise above its container ────────────────────────────
sub(u"""const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);""",
    u"""/* HOW FAR THE MESH FLOATS ABOVE ITS SLOT, sampled across a real throw. The
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

const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);""",
    '3 the mesh rise is measured')

sub(u"""out.saving = band ? {
  dpr,
  fullScreenMB: +(sc.width * dpr * sc.height * dpr * 4 / 1048576).toFixed(2),
  bandMB: +(sc.width * dpr * band.h * dpr * 4 / 1048576).toFixed(2),
} : null;""",
    u"""/* the band the measurement actually supports: the containers, the mesh rise
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
} : null;""",
    '4 the corrected band')

sub(u"""  theContentsFallInside: !!out.contents && !!band &&
    out.contents.top >= band.top && out.contents.bottom <= band.bottom,
  theBandIsWorthCutting: !!band && band.fractionOfScreen < 0.75,""",
    u"""  /* the containers alone do NOT contain the dice - that is the finding, so it
     is asserted in the direction it was measured rather than hidden */
  theContainersAloneDoNotContainTheDice: !!out.contents && !!band &&
    out.contents.top < band.top,
  theCorrectedBandDoesContainThem: !!out.bandCorrected && !!out.contents &&
    out.contents.top >= out.bandCorrected.top &&
    out.contents.bottom <= out.bandCorrected.bottom,
  theMeshRiseWasMeasuredInFlight: out.meshRise.sawFlight === true &&
                                  out.meshRise.samples >= 5,
  theBandIsStillWorthCutting: !!out.bandCorrected &&
    out.bandCorrected.fractionOfScreen < 0.5,""",
    '5 the verdict follows the measurement')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done')
