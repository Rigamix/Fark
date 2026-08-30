/* STEP 7's CONTROL - the two surfaces are the same surface.
 *
 * The question step 7 raised was whether moving a state from #dgCanvas (z3,
 * under the dice) to #stCanvas (z42, over them) changes how it looks, since a
 * hull painted under a die is partly hidden by the die and the same hull over
 * it is not. The answer is that the die was never doing the hiding:
 * _paintHalo punches its subject out of its own glow with a destination-out
 * pass on the hull widened by GLOW.clear, on a scratch surface, BEFORE
 * compositing. The ring is a ring by construction, so z-order cannot change
 * its shape and the verdict is byte-identical rather than "identical where it
 * was visible".
 *
 * SO NOTHING IS PORTED. Painting a shadow copy of ONE hull onto BOTH canvases
 * in the SAME frame isolates the surface from die pose, timing and renderer
 * state - none of which a comparison across frames or builds could hold still.
 * The shadow is deleted afterwards and `selected`/`cardmark` stay on dgCanvas
 * with their tuned dials untouched.
 *
 * THE COMPARATOR IS CONTROLLED. "Zero differing bytes" is worthless from a
 * differ that cannot see a difference, so the same comparison is run on two
 * deliberately different paints and must report a large one. Both orders are
 * run too: _paintHalo uses shared scratch canvases (_glowTmp, _haloS, _mips,
 * _mups) sized to the target, and if any of them were not fully cleared
 * between calls the second paint would inherit the first and the diff would be
 * an artefact rather than a finding.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const die = D3X.dice.filter(d => d.match && d.phys && d.obj && d.obj.visible)[0];
if (!die) return Object.assign(out, {err: 'no settled die'});

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);

const dg = D3X._glowCv(), st = D3X._stateCv();
if (!dg || !st) return Object.assign(out, {err: 'a canvas is missing'});

/* both surfaces set up by the same formula the two passes use */
const setup = (cv) => {
  cv.width = Math.round(sc.width * dpr);
  cv.height = Math.round(sc.height * dpr);
  const x = cv.getContext('2d');
  x.setTransform(dpr, 0, 0, dpr, 0, 0);
  x.clearRect(0, 0, sc.width, sc.height);
  return x;
};
const readPx = cv => cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
const compare = (a, b) => {
  let bytes = 0, px = 0, max = 0;
  for (let i = 0; i < a.length; i += 4) {
    let any = 0;
    for (let c = 0; c < 4; c++) {
      const d = Math.abs(a[i + c] - b[i + c]);
      if (d) { bytes++; any = 1; if (d > max) max = d; }
    }
    if (any) px++;
  }
  return {bytes, px, max};
};
const lit = a => { let n = 0; for (let i = 3; i < a.length; i += 4) if (a[i] > 8) n++; return n; };

/* ONE hull, computed once, painted on both */
const hull = D3X._hullOf(die, sc, D3X.GLOW.grow);
out.hullPoints = hull ? hull.length : 0;
if (!hull) return Object.assign(out, {err: 'no hull'});

const paint = (cv, col, soft) => {
  const x = setup(cv);
  D3X._paintHalo(cv, x, sc, dpr, [hull], col, soft, 1);
  return readPx(cv);
};

/* dims are read AFTER a setup(), not before: a freshly created canvas is
   300x150 by default, and reading it there would have compared two defaults
   and passed without saying anything about the surfaces under test. */
setup(dg); setup(st);
out.dims = {dgW: dg.width, dgH: dg.height, stW: st.width, stH: st.height, dpr};

/* WARM THE PAINTER, and discard the result. Measured: the FIRST _paintHalo
   after the scratch canvases are created or resized differs from every later
   one by a constant 216 bytes, max 1 per channel on ~160 pixels - and paints
   two through twelve are mutually identical to the byte. So the first call is
   a one-off, almost certainly the newly-created mip canvases (430x900 down to
   54x113) backing differently from resized-and-cleared ones. It is invisible
   at 1/255 on 0.04% of pixels, but it is not nothing, and a probe claiming
   BYTE-identical has to either explain it or stop claiming bytes. Warming up
   is the honest fix: it is a property of the instrument's first call, not of
   the surfaces under test. */
paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
paint(st, D3X.SEL_COL, D3X.SEL_SOFT);

/* ══ 1. same hull, same args, dg painted FIRST ══════════════════════ */
const aDg = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
const aSt = paint(st, D3X.SEL_COL, D3X.SEL_SOFT);
out.orderDgFirst = Object.assign(compare(aDg, aSt), {litDg: lit(aDg), litSt: lit(aSt)});

/* ══ 2. the other order, to rule out a shared-scratch artefact ══════ */
const bSt = paint(st, D3X.SEL_COL, D3X.SEL_SOFT);
const bDg = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
out.orderStFirst = Object.assign(compare(bDg, bSt), {litDg: lit(bDg), litSt: lit(bSt)});

/* ══ THE REPEATABILITY FLOOR, and what perturbs it ══════════════════
   A first pass found the two SURFACES byte-identical while the same surface
   painted twice across rounds drifted by 1 in 193 pixels. That is either
   elapsed time (there is no time term in _paintHalo, so no) or something
   shared between calls being keyed to the target. Both are measured here
   rather than assumed, because a shared scratch that carries state from one
   target to the next would make the headline comparison an artefact. */
const rep1 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
const rep2 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
out.backToBackSameSurface = compare(rep1, rep2);

const int1 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
paint(st, D3X.SEL_COL, D3X.SEL_SOFT);
const int2 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
out.sameSurfaceAcrossAnInterleave = compare(int1, int2);

/* and the same surface after a DIFFERENT-sized intermediate, which is the
   only thing that would resize the shared scratch canvases */
const sz1 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
const tmp = document.createElement('canvas');
tmp.width = 64; tmp.height = 64;
const tx = tmp.getContext('2d'); tx.setTransform(dpr,0,0,dpr,0,0);
try { D3X._paintHalo(tmp, tx, sc, dpr, [hull], D3X.SEL_COL, D3X.SEL_SOFT, 1); } catch (e) {}
const sz2 = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
out.sameSurfaceAfterAResize = compare(sz1, sz2);

/* the confound check. The drift above was found in a run that ALSO read the
   canvases before they were sized, and two things changed at once - the
   pre-size and the switch to back-to-back comparisons - so neither can claim
   the fix. This compares the FIRST measured paint against the LAST one, many
   paints apart: if it is zero, the pre-size was the cause and the painter is
   deterministic across rounds after all. */
out.firstPaintVsLast = compare(aDg, sz2);

/* ══ 3. THE COMPARATOR CAN SEE A DIFFERENCE ═════════════════════════ */
const nDg = paint(dg, D3X.SEL_COL, D3X.SEL_SOFT);
const nSt = paint(st, (window.OPP_INK || '#d94c3d'), (window.OPP_INK || '#d94c3d'));
out.negativeControl = compare(nDg, nSt);

/* a second, geometric control: a different hull must also differ */
const other = D3X.dice.filter(d => d.match && d.phys && d.obj && d.obj.visible && d !== die)[0];
if (other) {
  const h2 = D3X._hullOf(other, sc, D3X.GLOW.grow);
  const x2 = setup(st);
  D3X._paintHalo(st, x2, sc, dpr, [h2], D3X.SEL_COL, D3X.SEL_SOFT, 1);
  out.differentHullControl = compare(paint(dg, D3X.SEL_COL, D3X.SEL_SOFT), readPx(st));
}

/* ══ 4. DELETE THE SHADOW ═══════════════════════════════════════════
   the surfaces go back to their owners; nothing of this test survives it */
[dg, st].forEach(cv => {
  const x = cv.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0);
  x.clearRect(0, 0, cv.width, cv.height);
});
D3X._glowInk = false; D3X._stateInk = false;
try { D3X._drawGlow(); } catch (e) {}
try { D3X._drawStates(); } catch (e) {}
out.afterCleanup = {dg: FXH.ink('dgCanvas'), st: FXH.ink('stCanvas')};

/* selected and cardmark were never moved - assert that too, since the whole
   point of this control is that nothing tuned had to be disturbed */
/* P889: this used to assert the state registry was EMPTY, which the roster
   made meaningless - the roster is where selected and cardmark now live. The
   intent was always "nothing tuned was moved to the other surface", so that
   is what it says: both live rows still paint UNDER the dice. */
const rows = D3X.MARKS || [];
out.roster = {
  n: rows.length,
  under: rows.filter(r => r.layer === 'under').map(r => r.id),
  over:  rows.filter(r => r.layer === 'over').map(r => r.id),
};

out.VERDICT = {
  bothCanvasesExist:     !!dg && !!st,
  identicalDimensions:   out.dims.dgW === out.dims.stW && out.dims.dgH === out.dims.stH,
  somethingWasActuallyPainted: out.orderDgFirst.litDg > 100 && out.orderDgFirst.litSt > 100,
  /* the claim: byte-identical, full stop */
  byteIdenticalDgFirst:  out.orderDgFirst.bytes === 0,
  byteIdenticalStFirst:  out.orderStFirst.bytes === 0,
  repeatableBackToBack:        out.backToBackSameSurface.bytes === 0,
  unperturbedByTheOtherSurface: out.sameSurfaceAcrossAnInterleave.bytes === 0,
  deterministicAcrossRounds:    out.firstPaintVsLast.bytes === 0,
  /* the comparator could have failed and did not */
  comparatorSeesADifferentInk:  out.negativeControl.bytes > 1000,
  comparatorSeesADifferentHull: !out.differentHullControl ||
                                out.differentHullControl.bytes > 1000,
  /* nothing tuned was moved, and nothing of the shadow survives */
  shadowRemoved: out.afterCleanup.dg.px === 0 && out.afterCleanup.st.px === 0,
  selectionAndCardmarkStillPaintUnder:
    out.roster.under.indexOf('sel') >= 0 && out.roster.under.indexOf('card') >= 0,
  nothingWasMovedOver: out.roster.over.length === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
