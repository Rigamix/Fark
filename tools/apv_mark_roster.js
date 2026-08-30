/* P889 - the mark roster, against the explicit calls it replaced.
 *
 * THE CONTROL IS A REFERENCE IMPLEMENTATION IN THE SAME FRAME. _drawGlow used
 * to collect cardmark hulls and selection hulls itself and make two _paintHalo
 * calls in a fixed order, with a set-level ink swap when any selected die was
 * a rival keep. That logic is reproduced here by hand onto a scratch canvas of
 * the same size, in the same frame, from the same dice - and the roster's
 * output must match it byte for byte. Comparing against a remembered
 * screenshot or a previous build could not hold die pose, timing or renderer
 * state still; this does.
 *
 * THE PAINTER IS WARMED FIRST. Measured in the surface-parity work: the first
 * _paintHalo after the scratch canvases are created or resized differs from
 * every later one by a constant 216 bytes, max 1 per channel. Invisible, but
 * a probe claiming byte-identical has to account for it rather than widen its
 * tolerance.
 *
 * FOUR THINGS ARE ASSERTED THAT THE REFACTOR COULD HAVE BROKEN:
 *   the paint ORDER (cardmark first, selection composites on top),
 *   the set-level oppkeep swap (any rival keep turns the WHOLE selection),
 *   the roll behaviour (both live rows are through:false, so a roll still
 *   sleeps the entire pass - the optimisation the old global skip provided),
 *   and the cost (one _paintHalo per ROW present, not per die).
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};
const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const dice = D3X.dice.filter(d => d.match && d.phys && d.obj && d.obj.visible && d.chip);
out.usableDice = dice.length;
if (dice.length < 3) return Object.assign(out, {err: 'need three drawable dice'});

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);
const W = Math.round(sc.width * dpr), H = Math.round(sc.height * dpr);

const ref = document.createElement('canvas');
const readPx = cv => cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
const fresh = (cv) => {
  cv.width = W; cv.height = H;
  const x = cv.getContext('2d');
  x.setTransform(dpr, 0, 0, dpr, 0, 0);
  x.clearRect(0, 0, sc.width, sc.height);
  return x;
};
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

/* THE OLD LOGIC, reproduced verbatim from what _drawGlow used to do */
const reference = () => {
  const x = fresh(ref);
  const G = D3X.GLOW;
  const selH = [], markH = [];
  let oppSel = false;
  D3X.dice.forEach(d => {
    if (!d.match || !d.obj.visible) return;
    if (d.chip.classList.contains('cardmark')) {
      const mh = D3X._hullOf(d, sc, G.grow); if (mh) markH.push(mh);
    }
    if (!d.chip.classList.contains('selected')) return;
    if (d.chip.classList.contains('oppkeep')) oppSel = true;
    const h = D3X._hullOf(d, sc, G.grow); if (h) selH.push(h);
  });
  if (markH.length) {
    const MK = (window.CARD_MARK_INK || '#c66058');
    D3X._paintHalo(ref, x, sc, dpr, markH, MK, MK, 1);
  }
  if (selH.length) {
    let SOFT = D3X.SEL_SOFT, COL = D3X.SEL_COL;
    if (oppSel) COL = SOFT = (window.OPP_INK || '#d94c3d');
    D3X._paintHalo(ref, x, sc, dpr, selH, COL, SOFT, 1);
  }
  return readPx(ref);
};

const clearAll = () => D3X.dice.forEach(d => {
  if (d.chip) d.chip.classList.remove('selected', 'cardmark', 'oppkeep');
  d.sel = false;
});
const rosterPaint = () => {
  D3X._glowInk = false;
  const dg = D3X._glowCv();
  fresh(dg);
  D3X._drawGlow();
  return readPx(dg);
};

/* warm the painter and discard - see the header */
clearAll(); dice[0].chip.classList.add('selected');
rosterPaint(); reference();

/* ══ 1. SELECTION ONLY ══════════════════════════════════════════════ */
clearAll();
dice[0].chip.classList.add('selected'); dice[0].sel = true;
dice[1].chip.classList.add('selected'); dice[1].sel = true;
let a = rosterPaint(), b = reference();
out.selectionOnly = Object.assign(compare(a, b), {litRoster: lit(a), litRef: lit(b)});

/* ══ 2. CARD MARK ONLY ══════════════════════════════════════════════ */
clearAll();
dice[2].chip.classList.add('cardmark');
a = rosterPaint(); b = reference();
out.cardmarkOnly = Object.assign(compare(a, b), {litRoster: lit(a), litRef: lit(b)});

/* ══ 3. BOTH AT ONCE - this is where paint ORDER shows ══════════════ */
clearAll();
dice[0].chip.classList.add('selected'); dice[0].sel = true;
dice[1].chip.classList.add('selected'); dice[1].sel = true;
dice[2].chip.classList.add('cardmark');
a = rosterPaint(); b = reference();
out.both = Object.assign(compare(a, b), {litRoster: lit(a), litRef: lit(b)});

/* order proof: painting selection FIRST must NOT match, or the test above
   cannot tell the two orders apart */
const wrongOrder = () => {
  const x = fresh(ref);
  const G = D3X.GLOW;
  const selH = [], markH = [];
  D3X.dice.forEach(d => {
    if (!d.match || !d.obj.visible) return;
    if (d.chip.classList.contains('cardmark')) { const h = D3X._hullOf(d, sc, G.grow); if (h) markH.push(h); }
    if (d.chip.classList.contains('selected')) { const h = D3X._hullOf(d, sc, G.grow); if (h) selH.push(h); }
  });
  if (selH.length) D3X._paintHalo(ref, x, sc, dpr, selH, D3X.SEL_COL, D3X.SEL_SOFT, 1);
  if (markH.length) { const MK = (window.CARD_MARK_INK || '#c66058'); D3X._paintHalo(ref, x, sc, dpr, markH, MK, MK, 1); }
  return readPx(ref);
};
out.orderIsDetectable = compare(rosterPaint(), wrongOrder());

/* ORDER IS PROVABLY IRRELEVANT FOR THESE TWO ROWS, and the check above found
   it: _paintHalo composites with 'lighter', and clamped addition commutes, so
   two additive rows on disjoint hulls give the same surface either way. I had
   asserted a difference that cannot exist - the mirror of this session's usual
   mistake. It stops being true the moment a row is NOT additive, which is what
   a veil or a dim is, so the ordering machinery is tested where it can fail:
   a rim and a veil on the SAME die, roster order swapped. */
const savedRoster = D3X.MARKS.slice();
clearAll();
dice[0].chip.classList.add('probe-a');
const rowRim  = {id:'pa',layer:'under',through:true,style:'rim',ink:'#33cc66',
                 on:d=>d.chip.classList.contains('probe-a')};
const rowVeil = {id:'pb',layer:'under',through:true,style:'veil',ink:'#221100',
                 on:d=>d.chip.classList.contains('probe-a')};
D3X.MARKS = [rowRim, rowVeil];
const rimThenVeil = rosterPaint();
D3X.MARKS = [rowVeil, rowRim];
const veilThenRim = rosterPaint();
D3X.MARKS = savedRoster;
dice[0].chip.classList.remove('probe-a');
out.nonAdditiveOrder = compare(rimThenVeil, veilThenRim);
out.nonAdditiveLit = {rimThenVeil: lit(rimThenVeil), veilThenRim: lit(veilThenRim)};

/* ══ 4. THE SET-LEVEL oppkeep SWAP ══════════════════════════════════ */
clearAll();
dice[0].chip.classList.add('selected'); dice[0].sel = true;
dice[1].chip.classList.add('selected'); dice[1].sel = true;
dice[1].chip.classList.add('oppkeep');
a = rosterPaint(); b = reference();
out.oppKeep = Object.assign(compare(a, b), {litRoster: lit(a)});
/* and it must actually differ from the non-opp case, or it proves nothing */
const withOpp = a;
clearAll();
dice[0].chip.classList.add('selected'); dice[0].sel = true;
dice[1].chip.classList.add('selected'); dice[1].sel = true;
out.oppChangesTheLook = compare(withOpp, rosterPaint());

/* ══ 5. COST - one _paintHalo per ROW present, not per die ══════════ */
clearAll();
dice.forEach(d => { d.chip.classList.add('selected'); d.sel = true; });
dice[2].chip.classList.add('cardmark');
let halos = 0;
const realHalo = D3X._paintHalo;
D3X._paintHalo = function () { halos++; return realHalo.apply(this, arguments); };
rosterPaint();
D3X._paintHalo = realHalo;
out.cost = {diceMarked: dice.length, paintHaloCalls: halos};

/* ══ 6. A ROLL STILL SLEEPS THE PASS ════════════════════════════════ */
clearAll();
dice[0].chip.classList.add('selected'); dice[0].sel = true;
out.rowsThroughARoll = (D3X.MARKS || []).filter(m => m.through).length;
out.liveWhenStill   = D3X._marksLive('under', false);
out.liveWhenRolling = D3X._marksLive('under', true);

clearAll();
D3X._glowInk = false;
try { D3X._drawGlow(); } catch (e) {}

out.VERDICT = {
  /* the refactor changed nothing about how anything looks */
  selectionIsIdentical: out.selectionOnly.bytes === 0 && out.selectionOnly.litRoster > 100,
  cardmarkIsIdentical:  out.cardmarkOnly.bytes === 0 && out.cardmarkOnly.litRoster > 100,
  bothTogetherIdentical: out.both.bytes === 0 && out.both.litRoster > 100,
  /* ...and the comparison could have failed: the wrong order is detectable */
  /* the two shipped rows are BOTH additive, so order cannot change the
     surface - clamped addition commutes. Recorded as a fact, not asserted as
     a difference. */
  additiveRowsAreOrderFree: out.orderIsDetectable.bytes === 0,
  /* but the machinery honours roster order where it can matter */
  rosterOrderMattersForANonAdditiveRow: out.nonAdditiveOrder.bytes > 1000,
  nonAdditiveRowsActuallyPainted: out.nonAdditiveLit.rimThenVeil > 100,
  /* the set-level swap survived being turned into a row */
  oppKeepIsIdentical:   out.oppKeep.bytes === 0,
  oppKeepActuallyChangesTheLook: out.oppChangesTheLook.bytes > 1000,
  /* the cost claim, stated in the comment, measured here */
  oneCallPerRowNotPerDie: out.cost.paintHaloCalls === 2 && out.cost.diceMarked >= 3,
  /* the optimisation the old global skip gave, preserved by `through` */
  noRowSurvivesARollToday: out.rowsThroughARoll === 0,
  liveWhenStill:           out.liveWhenStill === true,
  sleepsThroughARoll:      out.liveWhenRolling === false,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
