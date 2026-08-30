/* P880 - the over-canvas (FX brief step 4).
 *
 * The claim is entirely negative: this pass must NOT do two things _drawGlow
 * does. So the test is _drawGlow itself, run side by side in both conditions.
 * If the state layer paints where the glow refuses to, the guards are gone; if
 * they paint the same, the twin was pointless.
 *
 * The roll condition is the one headless makes EASY for once: _rolling() stays
 * true for ~19s here against ~700ms real, so there is a wide window in which to
 * catch the skip. Every verdict below is gated on proof that the condition it
 * needs was actually in force at the moment of the draw.
 *
 * TWO THINGS THIS PROBE LEARNED THE HARD WAY.
 * 1. WHICH SURFACE, not just how many pixels. The first build of P880 took
 *    #dsCanvas, which was already the dice-shadow canvas, and every paint
 *    assertion here passed at full strength while the rims landed on the
 *    shadow layer. A pixel count cannot say which canvas it counted, so the
 *    parent and the identity of the element are verdicts now, and the shadow
 *    canvas is checked to be a different element that still has its ink.
 * 2. The glow is WARMED first. "The glow refuses this frame" is worthless if
 *    dgCanvas has never existed - absent and refusing look identical from the
 *    outside. So the glow is made to paint once before it is asked to refuse.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};

const r = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

const pick = () => D3X.dice.filter(d => d.match && d.obj.visible && d.chip)[0];
const die = pick();
if (!die) return Object.assign(out, {err: 'no drawable die'});

/* ══ A. WARM THE CONTROL ═════════════════════════════════════════════
   Make the glow paint, so that "the glow refuses" later is a statement
   about a canvas that demonstrably exists and demonstrably can be inked. */
FXH.clearMarks();
die.chip.classList.add('selected'); die.sel = true;
D3X._drawGlow();
out.glowWarmUp = FXH.ink('dgCanvas');

/* ══ B. THE LAYER ════════════════════════════════════════════════════
   Read after the roll, when all three canvases exist. Computed style, not
   the string the patch wrote. */
const cvS = D3X._stateCv();
const zOf = id => {const e = document.getElementById(id);
  return e ? getComputedStyle(e).zIndex : null;};
out.layer = {
  created: !!cvS, id: cvS && cvS.id, parent: cvS && cvS.parentElement.id,
  state: zOf('stCanvas'), dice: zOf('d3xCanvas'), glow: zOf('dgCanvas'),
  cards: getComputedStyle(document.getElementById('playerCards')).zIndex,
};

/* the shadow canvas is a DIFFERENT element and still has its own ink */
const shadow = document.getElementById('dsCanvas');
out.shadowCanvas = {
  exists: !!shadow, sameNode: shadow === cvS,
  parent: shadow && shadow.parentElement.id,
  blend: shadow && getComputedStyle(shadow).mixBlendMode,
  ink: FXH.ink('dsCanvas'),
};

/* ══ C. IT PAINTS WITH NOTHING SELECTED ══════════════════════════════ */
FXH.clearMarks();
die.chip.classList.remove('selected', 'cardmark');
die.chip.classList.add('probe-state');
/* P889: a roster ROW, not the old {cls,form} registry entry. layer:'over'
   puts it on stCanvas and through:true is what lets it survive a roll -
   which is the guard this probe exists to test. */
const savedRoster = D3X.MARKS.slice();
D3X.MARKS.push({id: 'probe', layer: 'over', through: true, style: 'rim',
                ink: '#33cc66',
                on: d => d.chip.classList.contains('probe-state')});

D3X._drawStates(); D3X._drawGlow();
out.settledNothingSelected = {
  anySelected: D3X.dice.some(d => d.chip && (d.chip.classList.contains('selected') ||
                                             d.chip.classList.contains('cardmark'))),
  state: FXH.ink('stCanvas'), stateHue: FXH.hue('stCanvas'),
  glow: FXH.ink('dgCanvas'),
};

/* ══ D. IT SURVIVES A ROLL ═══════════════════════════════════════════
   The other guard. Tap roll and draw while the physics tape is still
   playing - _drawGlow abandons the pass there, and a state must not. */
const restore = FXH.loadDice();
FXH.tap(document.getElementById('btnRoll'));
const rollingAt = await FXH.until(() => D3X._rolling() === true, 20000);
out.caughtMidRoll = rollingAt != null;
if (rollingAt != null) {
  const d2 = pick();
  if (d2) { d2.chip.classList.remove('selected', 'cardmark');
            d2.chip.classList.add('probe-state'); }
  const stillRolling = D3X._rolling();
  D3X._drawStates(); D3X._drawGlow();
  out.midRoll = {
    rollingAtDrawTime: stillRolling,
    state: FXH.ink('stCanvas'), stateHue: FXH.hue('stCanvas'),
    glow: FXH.ink('dgCanvas'),
  };
}

/* ══ E. THE PASS IS WIRED, not merely callable ═══════════════════════
   _statePasses is bumped at the top of the pass, before any guard, so the
   delta across a window this probe does not draw in counts frames the real
   loop delivered. */
const p0 = D3X._statePasses || 0;
await FXH.sleep(3500);
out.framePasses = {before: p0, after: D3X._statePasses || 0,
                   delta: (D3X._statePasses || 0) - p0};

/* ══ F. UNREGISTERING CLEARS IT ══════════════════════════════════════ */
await FXH.settled(45000);
D3X.MARKS.length = 0;
D3X._drawStates();
out.afterUnregister = FXH.ink('stCanvas');
out.shadowStillInked = FXH.ink('dsCanvas');
D3X.MARKS.push.apply(D3X.MARKS, savedRoster);/* put the real rows back */
if (restore) restore();

out.VERDICT = {
  /* the control can fail */
  glowCanPaintAtAll: out.glowWarmUp.exists === true && out.glowWarmUp.px > 0,
  /* identity and layer */
  canvasIsItsOwnElement: out.layer.created === true && out.layer.id === 'stCanvas',
  livesOnTheMatchScreen: out.layer.parent === 'screen-match',
  didNotAdoptTheShadowCanvas: out.shadowCanvas.sameNode === false &&
                              out.shadowCanvas.parent === 'matchShadows',
  shadowCanvasKeptItsInk: out.shadowStillInked.exists === true &&
                          out.shadowStillInked.px > 0,
  sitsAboveTheDice:  (+out.layer.state) > (+out.layer.dice),
  sitsBelowTheCards: (+out.layer.state) < (+out.layer.cards),
  glowIsStillBelowTheDice: (+out.layer.glow) < (+out.layer.dice),
  /* guard 1 - and its control: the glow must refuse the same frame */
  paintsWithNothingSelected: out.settledNothingSelected.state.px > 0,
  nothingWasActuallySelected: out.settledNothingSelected.anySelected === false,
  glowRefusesThatFrame: out.settledNothingSelected.glow.exists === true &&
                        out.settledNothingSelected.glow.px === 0,
  /* guard 2 - the same shape, mid-roll */
  probeCaughtTheRoll: out.caughtMidRoll === true &&
                      out.midRoll && out.midRoll.rollingAtDrawTime === true,
  paintsMidRoll: !!(out.midRoll && out.midRoll.state.px > 0),
  glowRefusesMidRoll: !!(out.midRoll && out.midRoll.glow.exists === true &&
                         out.midRoll.glow.px === 0),
  /* it is the registered ink, not something inherited */
  wearsTheRegisteredInk: !!(out.settledNothingSelected.stateHue.rgb &&
                            out.settledNothingSelected.stateHue.rgb[1] >
                            out.settledNothingSelected.stateHue.rgb[0]),
  /* wiring and teardown */
  theFrameLoopCallsIt: out.framePasses.delta > 0,
  unregisteringClearsTheSurface: out.afterUnregister.exists === true &&
                                 out.afterUnregister.px === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
