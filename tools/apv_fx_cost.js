/* What does the mark layer cost per frame, and what changed this week?
 *
 * DENIS'S REPORT: a boss match where the images went, then the dice, while the
 * game kept playing and the UI stayed. That is the signature of a renderer
 * running out of memory - decoded images are evicted first, canvases and
 * textures after - not of a logic fault, and the context-loss handler (P551)
 * would have suspended into the DOM dice if the GL context had simply dropped.
 *
 * SO THE QUESTION IS COST, AND THE SUSPECT IS MINE. Before this week _drawGlow
 * slept unless a die carried `selected`, and it skipped entirely while
 * _rolling(). During a RIVAL's turn nothing is selected, so the whole pass was
 * asleep for the whole turn. P895 put four states on the roster with
 * through:true - which is correct, a state must survive a roll - and the
 * consequence is that one dampened or blinded rival die now keeps the pass
 * awake, every frame, for the entire rival turn.
 *
 * WHAT ONE CALL COSTS. _paintHalo runs blurOnto twice, and each build is a
 * five-level mip chain down and back up over a full-screen scratch. That is
 * about ten large drawImage operations per call, per row, per frame.
 *
 * COUNTS ARE THE MEASUREMENT; TIMES ARE CONTEXT. This harness renders through
 * SwiftShader at about 1fps, so wall-clock here is not a phone's. Call counts
 * and allocated pixels are machine-independent, so the verdict rides on those
 * and the times are reported beside them without being asserted on.
 *
 * THE CONDITIONS ARE VARIED DELIBERATELY. A single number for "the cost" would
 * say nothing - the claim is that the cost CHANGED, so the old behaviour
 * (selection only, asleep while rolling) and the new one (states live through
 * a roll) are measured in the same run on the same dice.
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

const STATE = ['die-frozen', 'die-dampened', 'dampen-fade', 'die-blind'];
const wipe = () => { FXH.clearMarks(); D3X.FX_MARKS = [];
  dice.forEach(d => { d.chip.classList.remove.apply(d.chip.classList, STATE);
    d.chip._rrInk = null; d._rrSeen = 0; }); };

/* every canvas on the page and what it costs to hold */
const canvasBill = () => {
  const all = [].slice.call(document.querySelectorAll('canvas'));
  const rows = all.map(c => ({id: c.id || '(detached/anon)',
                              w: c.width, h: c.height,
                              mb: +(c.width * c.height * 4 / 1048576).toFixed(2)}));
  /* the scratch surfaces are NOT in the DOM - they are properties of D3X and
     cost exactly the same memory, which is the half a querySelectorAll misses */
  const off = [];
  const push = (name, c) => { if (c && c.width) off.push({id: name, w: c.width,
    h: c.height, mb: +(c.width * c.height * 4 / 1048576).toFixed(2)}); };
  push('_glowTmp', D3X._glowTmp); push('_haloS', D3X._haloS);
  (D3X._mips || []).forEach((c, i) => push('_mips[' + i + ']', c));
  (D3X._mups || []).forEach((c, i) => push('_mups[' + i + ']', c));
  const sum = a => +a.reduce((t, x) => t + x.mb, 0).toFixed(2);
  return {inDom: rows, offDom: off, domMB: sum(rows), offDomMB: sum(off),
          totalMB: +(sum(rows) + sum(off)).toFixed(2)};
};

/* one measured frame of the whole mark layer */
const realForm = D3X._paintForm;
const frame = (label, setup, forceRolling) => {
  wipe(); setup();
  const realRolling = D3X._rolling;
  if (forceRolling) D3X._rolling = function () { return true; };
  let calls = 0;
  D3X._paintForm = function () { calls++; return realForm.apply(this, arguments); };
  const t0 = performance.now();
  try { D3X._drawGlow(); D3X._drawStates(); } catch (e) {}
  const ms = performance.now() - t0;
  D3X._paintForm = realForm;
  if (forceRolling) D3X._rolling = realRolling;
  return {label, paintCalls: calls, ms: +ms.toFixed(1),
          under: FXH.ink('dgCanvas').px, over: FXH.ink('stCanvas').px};
};

out.before = canvasBill();

out.frames = [
  /* the old world: nothing selected, so the pass slept - this is what a rival
     turn cost before P895 */
  frame('idle, nothing marked', () => {}, false),
  frame('idle, nothing marked, ROLLING', () => {}, true),
  /* a selection: two rows, and it slept through a roll */
  frame('selection only', () => { dice[0].chip.classList.add('selected'); }, false),
  frame('selection only, ROLLING', () => { dice[0].chip.classList.add('selected'); }, true),
  /* the new world: a rival turn with cards played on their dice */
  frame('one dampened die', () => { dice[0].chip.classList.add('die-dampened'); }, false),
  frame('one dampened die, ROLLING',
        () => { dice[0].chip.classList.add('die-dampened'); }, true),
  frame('three states live', () => {
    dice[0].chip.classList.add('die-frozen');
    dice[1].chip.classList.add('die-dampened');
    dice[2].chip.classList.add('die-blind');
  }, false),
  frame('three states live, ROLLING', () => {
    dice[0].chip.classList.add('die-frozen');
    dice[1].chip.classList.add('die-dampened');
    dice[2].chip.classList.add('die-blind');
  }, true),
  /* and the worst realistic frame: states plus a combo's six beats */
  frame('three states + six beats', () => {
    dice[0].chip.classList.add('die-frozen');
    dice[1].chip.classList.add('die-dampened');
    dice[2].chip.classList.add('die-blind');
    dice.forEach((d, i) => { _dieBeat(d.chip, 'rim', D3X.BEAT_INK.combo,
      {ms: 450, tag: 'combo'}); });
    D3X.FX_MARKS.forEach(k => { k.t0 -= 200; });
  }, false),
];
wipe();
out.after = canvasBill();

/* what one _paintHalo actually moves: two blur builds, each a mip chain */
out.perCall = {
  softPasses: D3X.GLOW.softPasses, rimPasses: D3X.GLOW.rimPasses,
  scratchMB: (function () {
    const g = D3X._glowTmp, S = D3X._haloS;
    return {glowTmp: g ? +(g.width * g.height * 4 / 1048576).toFixed(2) : null,
            haloS: S ? +(S.width * S.height * 4 / 1048576).toFixed(2) : null};
  })(),
  dpr: Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3),
  glowDprMax: D3X.GLOW_DPR_MAX,
  rendererPixelRatio: Math.min(devicePixelRatio || 1, 2),
};

const by = l => out.frames.filter(f => f.label === l)[0] || {};
out.VERDICT = {
  /* the instrument has to be able to tell the conditions apart at all */
  theConditionsDiffer: new Set(out.frames.map(f => f.paintCalls)).size > 1,
  /* the old world: a roll put the whole pass to sleep */
  aSelectionSleepsThroughARoll: by('selection only, ROLLING').paintCalls === 0,
  aSelectionPaintsWhenStill: by('selection only').paintCalls > 0,
  /* THE CHANGE: one state keeps it awake through the roll it used to skip */
  aStatePaintsThroughARoll: by('one dampened die, ROLLING').paintCalls > 0,
  /* and the cost scales with how many marks are live */
  costScalesWithMarks:
    by('three states live').paintCalls > by('one dampened die').paintCalls,
  beatsAddOnTop:
    by('three states + six beats').paintCalls > by('three states live').paintCalls,
  /* nothing leaks frame to frame - the scratch surfaces are reused */
  noCanvasLeak: out.after.inDom.length === out.before.inDom.length &&
                out.after.offDom.length === out.before.offDom.length,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
