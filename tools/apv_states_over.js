/* P895 - the three states on the roster, and the thirteen CSS rules gone.
 *
 * WHAT THIS HAS TO PROVE, in order of how badly it could be got wrong:
 *
 * 1. THE PREDICATES FIRE AT ALL. The brief's sketch row read `d._frozen`,
 *    which is undefined on a D3X record - a row that never matches paints
 *    nothing and looks exactly like a row that is simply not live. So each
 *    row's `on()` is called directly on the chip that was given the class,
 *    and the verdict is gated on that: a pixel count is only read after the
 *    predicate has been shown to return true.
 *
 * 2. EACH STATE PAINTS ITS OWN CANVAS. frozen and damp are CRUST and belong
 *    under the dice; blind is a VEIL and belongs over. A pass that painted
 *    all three on one surface would still score "ink appeared" if the probe
 *    only counted pixels, so each is measured on BOTH canvases and the wrong
 *    one must stay clean.
 *
 * 3. THEY SURVIVE A ROLL. through:true is the whole difference between a
 *    state and a selection, and the old code could not express it - the
 *    global _rolling() skip put the entire pass to sleep. Measured by
 *    stubbing _rolling true: the states must still paint, and a selection
 *    alone must still sleep the pass, so the optimisation that guard bought
 *    is not quietly lost.
 *
 * 4. THE COLOURS ARE THE DELETED RULES' OWN. Alpha coverage cannot tell a
 *    state wearing another state's ink from a correct one, and with four
 *    forms on two canvases that is now a real way to be wrong.
 *
 * 5. THE CSS IS ACTUALLY GONE FROM THE CASCADE, not just from the file - read
 *    off computed style on a die wearing the class, which is the only check
 *    that a later rule is not still winning.
 *
 * THE CONTROL CAN FAIL: with no state class on any die and nothing selected,
 * neither canvas may hold ink. Measured while writing this - with nothing live
 * the canvases do not merely read empty, they do not EXIST: both passes return
 * before _glowCv/_stateCv create them, which is P889's sleep path. So the
 * control asserts "no ink", and the existence check that carries weight is
 * taken while a state is live. Both sit beside large non-zero counts from the
 * same instrument in the same run, so "clean" cannot mean "blind".
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

const STATE_CLASSES = ['die-frozen', 'die-dampened', 'dampen-fade', 'die-blind'];
const wipe = () => {
  FXH.clearMarks();
  dice.forEach(d => d.chip.classList.remove.apply(d.chip.classList, STATE_CLASSES));
};
/* BOTH canvases, every time - a form on the wrong surface must be visible as
   a failure, not hidden by only ever reading the surface we expect. */
const paint = () => {
  let threw = null;
  try { D3X._drawGlow(); } catch (e) { threw = 'under: ' + e.message; }
  try { D3X._drawStates(); } catch (e) { threw = (threw || '') + ' over: ' + e.message; }
  return {under: FXH.ink('dgCanvas'), over: FXH.ink('stCanvas'), threw};
};
const px = o => (o && o.px) || 0;

/* ── the roster, as shipped ─────────────────────────────────────── */
const rows = (D3X.MARKS || []).map(w => ({id: w.id, layer: w.layer,
  through: w.through, style: w.style, ink: w.ink}));
out.roster = rows;

/* ── 0. THE CONTROL, and it is allowed to fail ──────────────────── */
wipe();
const base = paint();
/* MEASURED, and the first version of this probe asserted the opposite: with no
   row live BOTH canvases are absent, not empty. _glowCv/_stateCv create them
   lazily and the sleep path returns before that, which is the P889 design.
   So the control's invariant is "asleep or empty", and the existence check
   that means something is the one taken while a state IS live, below. */
out.control = {under: px(base.under), over: px(base.over),
               underExists: base.under.exists, overExists: base.over.exists,
               threw: base.threw};

/* ── 1..3. one state at a time, predicate first, then pixels ────── */
const CASES = [
  {id: 'frozen', cls: ['die-frozen'],    layer: 'under', d: dice[0]},
  {id: 'damp',   cls: ['die-dampened'],  layer: 'under', d: dice[1]},
  {id: 'blind',  cls: ['die-blind'],     layer: 'over',  d: dice[2]},
];
out.cases = {};
for (const c of CASES) {
  wipe();
  c.cls.forEach(k => c.d.chip.classList.add(k));
  const row = (D3X.MARKS || []).filter(w => w.id === c.id)[0] || null;
  /* THE GATE: does the row's own predicate see this die? Everything below is
     meaningless if it does not, and a zero would read as "not painted". */
  let fires = null;
  try { fires = row ? !!row.on(c.d) : null; } catch (e) { fires = 'threw: ' + e.message; }
  const hits = row ? D3X._markDice(row).length : 0;
  const p = paint();
  const h = FXH.hue(c.layer === 'under' ? 'dgCanvas' : 'stCanvas');
  out.cases[c.id] = {
    rowFound: !!row, predicateFires: fires, diceMatched: hits,
    under: px(p.under), over: px(p.over), threw: p.threw,
    underExists: p.under.exists, overExists: p.over.exists,
    hue: h.hex || null, hueShare: h.share == null ? null : h.share,
    rgb: h.rgb || null,
    /* and taking the class away must take the ink away - a row that paints
       whatever the classes say is not the same as a row that paints. */
    zeroesOnRemoval: (function () {
      c.cls.forEach(k => c.d.chip.classList.remove(k));
      const q = paint();
      return {under: px(q.under), over: px(q.over)};
    })(),
  };
}

/* ── 4. damp ends when the fade begins ──────────────────────────── */
wipe();
dice[1].chip.classList.add('die-dampened');
const dampOn = paint();
dice[1].chip.classList.add('dampen-fade');
const dampFading = paint();
out.dampenFade = {withState: px(dampOn.under), afterFadeClass: px(dampFading.under)};

/* ── 5. THROUGH A ROLL. The claim through:true exists to make. ───── */
const realRolling = D3X._rolling;
D3X._rolling = function () { return true; };
try {
  wipe();
  dice[0].chip.classList.add('die-frozen');
  dice[2].chip.classList.add('die-blind');
  const rolling = paint();
  out.whileRolling = {under: px(rolling.under), over: px(rolling.over)};

  /* and the optimisation the old global guard bought must survive: a
     selection on its own is through:false, so a roll still sleeps the pass */
  wipe();
  dice[0].chip.classList.add('selected');
  const selRolling = paint();
  out.selectionWhileRolling = {under: px(selRolling.under), over: px(selRolling.over)};
  wipe();
  const selStill = (D3X._rolling = realRolling, dice[0].chip.classList.add('selected'), paint());
  out.selectionWhenStill = {under: px(selStill.under), over: px(selStill.over)};
} finally { D3X._rolling = realRolling; }
wipe();

/* ── 6. THE CASCADE, not the file. Is the rule really gone? ──────── */
const cs = (el, prop) => { try { return getComputedStyle(el)[prop]; } catch (e) { return 'ERR'; } };
dice[0].chip.classList.add('die-frozen');
dice[1].chip.classList.add('die-blind');
dice[2].chip.classList.add('die-dampened', 'die-dampened-fresh');
out.cascade = {
  frozenBoxShadow: cs(dice[0].chip, 'boxShadow'),
  blindBackground: cs(dice[1].chip, 'backgroundColor'),
  dampenedFilter: cs(dice[2].chip, 'filter'),
  frozenBadge: cs(dice[0].chip, 'content'),
};
/* the pseudo-elements the four invisible rules used to author */
const pseudo = (el, which) => { try { return getComputedStyle(el, which).display; } catch (e) { return 'ERR'; } };
out.pseudoDisplay = {
  dampenedBefore: pseudo(dice[2].chip, '::before'),
  freshAfter: pseudo(dice[2].chip, '::after'),
};
wipe();

/* ── 7. spent is already done, and not by a mark ─────────────────── */
out.spent = {
  spentLookExists: typeof D3X._spentLook === 'function',
  noSpentRow: !(D3X.MARKS || []).some(w => w.id === 'spent'),
  derivedEverySync: /_spentLook\(d,d\.chip\.classList/.test(D3X.syncMatch.toString()),
};

/* ── the verdict ────────────────────────────────────────────────── */
const C = out.cases;
out.VERDICT = {
  /* the control can fail, and a big number below proves it was not blind */
  /* asleep or empty, both acceptable - what is NOT acceptable is ink */
  controlIsClean: out.control.under === 0 && out.control.over === 0,
  /* and the existence check that carries weight: the surface a live state
     paints on must really be there, so a px count cannot come from nowhere */
  surfacesExistWhenAStateIsLive: C.frozen.underExists === true &&
                                 C.blind.overExists === true,
  nothingThrew: !out.control.threw && !C.frozen.threw && !C.damp.threw && !C.blind.threw,

  /* 1. the predicates fire - without this every pixel count below is noise */
  frozenPredicateFires: C.frozen.predicateFires === true && C.frozen.diceMatched === 1,
  dampPredicateFires: C.damp.predicateFires === true && C.damp.diceMatched === 1,
  blindPredicateFires: C.blind.predicateFires === true && C.blind.diceMatched === 1,

  /* 2. each on its own canvas, and the other one clean */
  frozenPaintsUnderOnly: C.frozen.under > 200 && C.frozen.over === 0,
  dampPaintsUnderOnly: C.damp.under > 200 && C.damp.over === 0,
  blindPaintsOverOnly: C.blind.over > 200 && C.blind.under === 0,

  /* removing the class removes the ink */
  frozenZeroesOnRemoval: C.frozen.zeroesOnRemoval.under === 0,
  dampZeroesOnRemoval: C.damp.zeroesOnRemoval.under === 0,
  blindZeroesOnRemoval: C.blind.zeroesOnRemoval.over === 0,

  /* 3. and dampen-fade is the file's own end-of-state signal */
  fadeEndsTheDampState: out.dampenFade.withState > 200 &&
                        out.dampenFade.afterFadeClass === 0,

  /* 4. through a roll: the states hold, the selection still sleeps */
  statesSurviveARoll: out.whileRolling.under > 200 && out.whileRolling.over > 200,
  selectionStillSleepsARoll: out.selectionWhileRolling.under === 0,
  andTheSelectionStillPaintsWhenStill: out.selectionWhenStill.under > 200,

  /* 5. the inks are the deleted rules' own */
  frozenIsBlue: !!C.frozen.rgb && C.frozen.rgb[2] > C.frozen.rgb[0] + 24,
  dampIsBrownish: !!C.damp.rgb && C.damp.rgb[0] > C.damp.rgb[2] + 24 &&
                  C.damp.rgb[1] > C.damp.rgb[2],
  blindIsDark: !!C.blind.rgb && C.blind.rgb[0] < 70 && C.blind.rgb[1] < 70,
  huesAreDominant: C.frozen.hueShare > 0.15 && C.damp.hueShare > 0.15,

  /* 6. gone from the cascade, not merely from the file */
  frozenBoxShadowGone: out.cascade.frozenBoxShadow === 'none',
  blindBackgroundGone: !/26, *26, *42/.test(out.cascade.blindBackground),
  dampenedFilterGone: out.cascade.dampenedFilter === 'none',
  invisiblePseudosStillNone: out.pseudoDisplay.dampenedBefore === 'none' &&
                             out.pseudoDisplay.freshAfter === 'none',

  /* 7. the fourth state needed no row */
  spentIsAlreadyOnTheMaterial: out.spent.spentLookExists && out.spent.noSpentRow &&
                               out.spent.derivedEverySync,

  /* the roster grew by exactly three */
  rosterHasFiveRows: rows.length === 5,
  allThreeAreThrough: ['frozen', 'damp', 'blind'].every(id =>
    rows.some(w => w.id === id && w.through === true)),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
