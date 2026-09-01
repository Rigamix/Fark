/* P897 - does a beat's ring wash the dice it is not about?
 *
 * THE THIRD CASE. P777 names two punches: the dice's, which WIDENS by G.clear
 * because their canvas is over the painted table and a wash on the die is the
 * failure; and punchUnder, which cuts INWARD for a canvas beneath its subject.
 * A canvas over the DICE is neither, and P896 put beat rims there.
 *
 * The widening cut cannot wash the beat's OWN die - that is what it is for.
 * The gap it can leave is sub-pixel and hidden under the dice, visible over
 * them. Neither is the interesting case.
 *
 * THE INTERESTING CASE IS THE NEIGHBOUR, and it follows from how the punch is
 * built rather than from its direction: _paintHalo punches with the shapes in
 * `sel`, and `sel` is also what it paints. A ROW collects every die it applies
 * to into one call, so each die's glow is cut by all of them. A BEAT paints one
 * die - `[hb]` - so its glow is cut by its own silhouette and by nothing else.
 * Under the dice that is invisible: a neighbour occludes the spill. Over them
 * nothing does, and the soft pass reaches ~11px with a 1.14/1.24 stretch, which
 * is further than dice in a row sit apart.
 *
 * SO THE MEASUREMENT IS POINT-IN-POLYGON, not a pixel count: ink is located
 * against each die's TRUE silhouette (grow 1.0, not the painted 1.004), and the
 * question is whose die it landed on. A count alone cannot tell a correct ring
 * from one painted across the die next to it.
 *
 * FOUR CONTROLS, because "0 wash" is the kind of answer an empty canvas gives:
 *   the same scan with no beat armed must be 0 everywhere;
 *   total lit must be large, so the scan is looking at a real ring;
 *   the ring must be found OUTSIDE the subject and absent INSIDE it, which is
 *     the widening punch doing its job and proves the locator is oriented;
 *   and the blind VEIL - a fill on the hull, on the same canvas - must show no
 *     neighbour ink, separating "beats spill" from "this canvas spills".
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const dice = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip);
out.usableDice = dice.length;
if (dice.length < 3) return Object.assign(out, {err: 'need three drawable dice'});

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);

/* TRUE silhouettes - grow 1.0. The painter traces 1.004, and measuring
   against the grown hull would hide exactly the band this is about. */
const hulls = dice.map(d => D3X._hullOf(d, sc, 1.0));
if (hulls.some(h => !h)) return Object.assign(out, {err: 'a die had no hull'});

const inside = (h, px, py) => {
  let n = false;
  for (let i = 0, j = h.length - 1; i < h.length; j = i++) {
    const xi = h[i][0], yi = h[i][1], xj = h[j][0], yj = h[j][1];
    if (((yi > py) !== (yj > py)) &&
        (px < (xj - xi) * (py - yi) / ((yj - yi) || 1e-9) + xi)) n = !n;
  }
  return n;
};

/* how far apart the dice actually are, so the reader can see whether a spill
   was ever plausible rather than taking the 11px soft radius on trust */
const centre = h => { let cx = 0, cy = 0; h.forEach(p => { cx += p[0]; cy += p[1]; });
                      return [cx / h.length, cy / h.length]; };
const c0 = centre(hulls[0]);
out.geometry = {
  dieWidthPx: Math.round(Math.max.apply(null, hulls[0].map(p => p[0])) -
                         Math.min.apply(null, hulls[0].map(p => p[0]))),
  centreGapsFromDie0: hulls.slice(1).map(h => {
    const c = centre(h);
    return Math.round(Math.hypot(c[0] - c0[0], c[1] - c0[1]));
  }),
  softReach: D3X.GLOW.soft, softStretch: [D3X.GLOW.sx, D3X.GLOW.sy],
  clear: D3X.GLOW.clear, grow: D3X.GLOW.grow,
};

/* locate every lit pixel on the over canvas against the true silhouettes */
const scan = () => {
  const cv = document.getElementById('stCanvas');
  if (!cv || !cv.width) return {exists: !!cv, lit: 0, onDie: null, why: 'no canvas'};
  const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
  const onDie = hulls.map(() => 0);
  let lit = 0, outsideEveryDie = 0;
  for (let j = 0; j < cv.height; j++) {
    for (let i = 0; i < cv.width; i++) {
      if (d[(j * cv.width + i) * 4 + 3] <= 8) continue;
      lit++;
      const px = i / dpr, py = j / dpr;
      let hitAny = false;
      for (let k = 0; k < hulls.length; k++)
        if (inside(hulls[k], px, py)) { onDie[k]++; hitAny = true; }
      if (!hitAny) outsideEveryDie++;
    }
  }
  return {exists: true, lit, onDie, outsideEveryDie};
};

const clearBeats = () => { D3X.FX_MARKS = []; };
const wipe = () => { FXH.clearMarks();
  dice.forEach(d => d.chip.classList.remove('die-frozen', 'die-dampened',
                                            'dampen-fade', 'die-blind')); };
const paint = () => { try { D3X._drawStates(); return null; }
                      catch (e) { return 'threw: ' + e.message; } };

/* ── 0. the empty control - the scan must be able to report nothing ── */
wipe(); clearBeats();
paint();
out.control = scan();

/* ── 1. a beat on die 0, sampled at its peak ───────────────────────── */
wipe(); clearBeats();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
if (D3X.FX_MARKS[0]) D3X.FX_MARKS[0].t0 -= 350;   /* peak: sin(0.5*PI) = 1 */
const beatThrew = paint();
out.beat = scan();
out.beat.threw = beatThrew;
out.beat.onItsOwnDie = out.beat.onDie ? out.beat.onDie[0] : null;
out.beat.onNeighbours = out.beat.onDie
  ? out.beat.onDie.slice(1).reduce((a, b) => a + b, 0) : null;

/* ── 2. the blind VEIL, same canvas, a fill on the hull ────────────── */
wipe(); clearBeats();
dice[0].chip.classList.add('die-blind');
const veilThrew = paint();
out.veil = scan();
out.veil.threw = veilThrew;
out.veil.onItsOwnDie = out.veil.onDie ? out.veil.onDie[0] : null;
out.veil.onNeighbours = out.veil.onDie
  ? out.veil.onDie.slice(1).reduce((a, b) => a + b, 0) : null;
wipe();

/* ── 3. and the same beat on the UNDER canvas, for the comparison ───
   painted through the identical call, so the difference is the surface and
   nothing else. Under the dice this ink is occluded; the number is here to
   show the spill is a property of the halo, not of the beat path. */
clearBeats();
const dgc = D3X._glowCv && D3X._glowCv();
let underSpill = null;
if (dgc) {
  /* SIZE IT FIRST. _glowCv only creates the element; _drawGlow is what sets
     its backing store to sc*dpr, and the sleep path returns before that. A
     freshly created canvas is 300x150, so painting into it at a dpr transform
     put the ring off the surface entirely and the reference read 0 lit - which
     would have said "the under layer has no inner line", the opposite of the
     truth, with no error anywhere. */
  if (dgc.width !== Math.round(sc.width * dpr) ||
      dgc.height !== Math.round(sc.height * dpr)) {
    dgc.width = Math.round(sc.width * dpr);
    dgc.height = Math.round(sc.height * dpr);
  }
  const gx = dgc.getContext('2d');
  gx.setTransform(dpr, 0, 0, dpr, 0, 0);
  gx.clearRect(0, 0, sc.width, sc.height);
  D3X._paintForm('rim', dgc, gx, sc, dpr, [D3X._hullOf(dice[0], sc, D3X.GLOW.grow)],
                 D3X.BEAT_INK.gold, D3X.BEAT_INK.gold, 1);
  const d = gx.getImageData(0, 0, dgc.width, dgc.height).data;
  let n = 0, own = 0, lit = 0;
  for (let j = 0; j < dgc.height; j++)
    for (let i = 0; i < dgc.width; i++) {
      if (d[(j * dgc.width + i) * 4 + 3] <= 8) continue;
      lit++;
      if (inside(hulls[0], i / dpr, j / dpr)) own++;
      for (let k = 1; k < hulls.length; k++)
        if (inside(hulls[k], i / dpr, j / dpr)) { n++; break; }
    }
  underSpill = {neighbourInk: n, onItsOwnDie: own, lit: lit};
}
/* THE REFERENCE FOR THE CUT. The same _paintForm call with `over` absent, so
   the only difference is the new pass. Under the dice the line's inner half is
   occluded by the die and this number is invisible - which is exactly why it
   is the right baseline: it is what the over canvas WOULD show if nothing
   trimmed it, and what the dial was tuned against. */
out.sameCallOnTheUnderCanvas = underSpill || {neighbourInk: null};

const B = out.beat;
out.VERDICT = {
  /* the controls first - a zero below means nothing without these */
  scanCanReportNothing: out.control.lit === 0,
  /* the reference has to have painted, or every ratio below divides by a
     canvas that was never the right size */
  theUnderReferenceReallyPainted: out.sameCallOnTheUnderCanvas.lit > 2000,
  theRingIsReallyThere: B.lit > 2000,
  itPaintsOutsideEveryDie: B.outsideEveryDie > 1000,
  /* THE FIX, measured against the untrimmed call in the same run. The line
     is stroked after the punch by design and straddles the silhouette, so
     about 1.5px of it lands inside the die; the over cut takes that back to
     the 0.6px hair G.clear leaves. Not zero, deliberately - a cut exactly on
     the silhouette has to line up perfectly or it seams. */
  theOverCutTrimsTheLine:
    out.sameCallOnTheUnderCanvas.onItsOwnDie > 0 &&
    B.onItsOwnDie < out.sameCallOnTheUnderCanvas.onItsOwnDie * 0.6,
  aHairSurvivesRatherThanASeam: B.onItsOwnDie > 0,
  /* and the under layer is untouched: same call, still the full inner half */
  theUnderLayerStillCarriesTheWholeLine:
    out.sameCallOnTheUnderCanvas.onItsOwnDie > out.sameCallOnTheUnderCanvas.lit * 0.05,
  nothingThrew: !B.threw && !out.veil.threw,
  /* the locator is oriented: the veil is a FILL on die 0's hull, so it must
     land almost entirely ON die 0 - the opposite result to the ring */
  theVeilLandsOnItsOwnDie: out.veil.onItsOwnDie > out.veil.lit * 0.9,
  theVeilDoesNotSpill: out.veil.onNeighbours === 0,
  /* THE QUESTION */
  theBeatDoesNotWashItsNeighbours: B.onNeighbours === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
