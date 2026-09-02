/* P903 - a mark paints cheaper while its die is in the air.
 *
 * THE COST IS COUNTED, NOT TIMED. Wall-clock in this harness is SwiftShader at
 * about 1fps and says nothing about a phone. drawImage calls are the actual
 * traffic - the pyramid build and the per-pass composites are all drawImage -
 * and the count is the same on any machine, so that is the measurement and the
 * times are not reported at all.
 *
 * A DIAL THAT CHANGES NOTHING WOULD PASS A COST TEST. Fewer composites of the
 * same blur must also make a visibly dimmer mark, so the surfaces are compared
 * as well: cheap and full must DIFFER. A saving with identical output would
 * mean the passes were never doing anything and the shipped rimPasses:5 is
 * four wasted screens per paint - a different and larger finding, so it is
 * asserted rather than assumed either way.
 *
 * AND THE SNAP BACK IS THE RISK. If settle did not repaint, the table would
 * keep the flight-quality mark for as long as the dice sat still - which is
 * exactly the frames anyone actually looks at. The quality flag is in the
 * signature for that reason, so the test is: same hulls, rolling flipped off,
 * must repaint and must be full quality.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const dice = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip);
if (dice.length < 3) return Object.assign(out, {err: 'need three drawable dice'});

const STATE = ['die-frozen', 'die-dampened', 'dampen-fade', 'die-blind', 'selected'];
const wipe = () => { D3X.FX_MARKS = [];
  dice.forEach(d => { d.chip.classList.remove.apply(d.chip.classList, STATE);
    d.chip._rrInk = null; d._rrSeen = 0; d.sel = false; }); };

/* the traffic counter */
const proto = CanvasRenderingContext2D.prototype;
const realDraw = proto.drawImage;
let draws = 0;
proto.drawImage = function () { draws++; return realDraw.apply(this, arguments); };

const realRolling = D3X._rolling;
const paint = (flying) => {
  D3X._rolling = function () { return !!flying; };
  D3X._glowSig = '';                  /* force it - we are measuring a paint */
  const before = draws;
  try { D3X._drawGlow(); } catch (e) {}
  D3X._rolling = realRolling;
  return draws - before;
};
const surface = () => { const cv = document.getElementById('dgCanvas');
  return cv && cv.width
    ? new Uint8ClampedArray(cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data)
    : null; };
const diff = (a, b) => { if (!a || !b || a.length !== b.length) return -1;
  let n = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) n++; return n; };
const lit = a => { let n = 0; for (let i = 3; i < a.length; i += 4) if (a[i] > 8) n++; return n; };
const brightness = a => { let t = 0; for (let i = 3; i < a.length; i += 4) t += a[i]; return t; };

/* ── the two qualities, same dice, same pose ───────────────────────── */
wipe();
dice[0].chip.classList.add('die-dampened');
dice[1].chip.classList.add('die-frozen');
paint(false);                          /* warm: P889b's first-paint artefact */
const fullDraws = paint(false);
const fullPx = surface();
/* REPEATABILITY IS MEASURED BACK TO BACK. The first version of this compared
   two full paints with a CHEAP one between them and read 205 differing bytes,
   then blamed the warm-up. Two adjacent paints of the same frame is the
   question "is full quality deterministic"; anything else is a different
   question wearing its name. */
const fullDraws2 = paint(false);
const fullPxAdjacent = surface();
const cheapDraws = paint(true);
const cheapPx = surface();
paint(false);
const fullPx2 = surface();

out.dials = {shipped: {softPasses: D3X.GLOW.softPasses, rimPasses: D3X.GLOW.rimPasses},
             flight: D3X.FLIGHT};
out.traffic = {
  drawImageFullQuality: fullDraws,
  drawImageInFlight: cheapDraws,
  saved: fullDraws - cheapDraws,
  ratio: cheapDraws ? +(fullDraws / cheapDraws).toFixed(2) : null,
};
out.picture = {
  litFull: lit(fullPx), litCheap: lit(cheapPx),
  bytesFullVsCheap: diff(fullPx, cheapPx),
  bytesTwoAdjacentFullPaints: diff(fullPx, fullPxAdjacent),
  bytesFullAfterACheapOne: diff(fullPx, fullPx2),
  drawsFullSecondTime: fullDraws2,
  brightnessFull: brightness(fullPx), brightnessCheap: brightness(cheapPx),
};

/* ── the snap back, which is where a mistake would live ────────────── */
wipe();
dice[0].chip.classList.add('die-dampened');
/* ONE state here against two above, so the settle cost has to be compared with
   a one-group full paint rather than with the two-group number - which is what
   the first run of this got wrong, reporting a correct 15 against a 30 that
   described a different frame. */
paint(false);
const oneGroupFull = paint(false);
D3X._rolling = function () { return true; };
D3X._glowSig = '';
let b = draws; try { D3X._drawGlow(); } catch (e) {}
const flightPaint = draws - b;
const sigWhileFlying = D3X._glowSig.slice(0, 2);
b = draws; try { D3X._drawGlow(); } catch (e) {}
const flightHit = draws - b;                 /* still flying, nothing moved */
D3X._rolling = function () { return false; };
b = draws; try { D3X._drawGlow(); } catch (e) {}
const settlePaint = draws - b;
const sigAfterSettle = D3X._glowSig.slice(0, 2);
D3X._rolling = realRolling;
out.snapBack = {
  oneGroupFullQuality: oneGroupFull,
  paintedWhileFlying: flightPaint > 0,
  cachedWhileFlying: flightHit === 0,
  sigWhileFlying, sigAfterSettle,
  repaintedOnSettle: settlePaint > 0,
  settleCostFullQuality: settlePaint,
};

wipe();
proto.drawImage = realDraw;

out.VERDICT = {
  /* the instrument saw real work */
  aFullPaintDoesRealTraffic: out.traffic.drawImageFullQuality > 15,
  /* the saving, and it must be substantial rather than a rounding difference */
  flightCostsLess: out.traffic.drawImageInFlight < out.traffic.drawImageFullQuality,
  /* THE MECHANISM, not a threshold I picked before measuring. rimPasses 5 to 1
     removes exactly four full-screen composites per _paintHalo call, and this
     frame has two groups, so the saving is exactly 8. Asserting the arithmetic
     means a change to the dial fails here loudly instead of drifting. */
  theSavingIsExactlyTheComposites:
    out.traffic.saved === 4 * 2 &&
    D3X.GLOW.rimPasses - D3X.FLIGHT.rimPasses === 4,
  /* the dial must actually be doing something to the picture */
  theTwoQualitiesDiffer: out.picture.bytesFullVsCheap > 1000,
  flightIsTheDimmerOne: out.picture.brightnessCheap < out.picture.brightnessFull,
  /* THE NOISE FLOOR, MEASURED, AND A CORRECTION TO P889b. That note called the
     ~216-byte difference a FIRST-paint artefact - the scratch canvases backing
     differently before they have been resized once. It is not first-paint
     only: two adjacent full-quality paints of the same frame, same inputs,
     identical draw counts, differ by ~211 bytes every time. So it is a floor
     under every comparison on this surface, not an initial transient, and the
     honest test is not "zero" but "the signal beats the floor by an order of
     magnitude". Widening a tolerance to swallow it would have hidden exactly
     the thing worth knowing. */
  theNoiseFloorIsSmallAndBounded: out.picture.bytesTwoAdjacentFullPaints < 600,
  theQualityDifferenceBeatsTheFloor:
    out.picture.bytesFullVsCheap > out.picture.bytesTwoAdjacentFullPaints * 10,
  fullQualityCostsTheSameTwice: out.picture.drawsFullSecondTime ===
                                out.traffic.drawImageFullQuality,
  /* and both still paint a real mark - cheaper must not mean absent, which is
     the one thing through:true exists to guarantee */
  theMarkIsPresentInFlight: out.picture.litCheap > 2000,
  theMarkIsPresentAtRest: out.picture.litFull > 2000,
  /* the snap back */
  itPaintsWhileFlying: out.snapBack.paintedWhileFlying === true,
  itStillCachesWhileFlying: out.snapBack.cachedWhileFlying === true,
  theSignatureCarriesTheQuality: out.snapBack.sigWhileFlying === 'F|' &&
                                 out.snapBack.sigAfterSettle === 'S|',
  settlingRepaints: out.snapBack.repaintedOnSettle === true,
  andSettlingIsFullQuality: out.snapBack.settleCostFullQuality ===
                            out.snapBack.oneGroupFullQuality,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
