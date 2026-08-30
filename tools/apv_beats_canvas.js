/* P883 - _glow, _flash and _beam reach a match die (FX brief step 5, the rest).
 *
 * SAMPLING. Glow and beam carry their alpha on a sine, so a draw at t=0 reads
 * exactly zero BY CONSTRUCTION - a probe that fires the effect and measures
 * immediately would report "nothing painted" for a painter working perfectly.
 * Both are given a long duration and sampled at mid-life. Flash decays from
 * full, so it is measured immediately, which is also the only honest window
 * for a 150ms effect on a ~1fps harness.
 *
 * Every claim has the control that could refute it: the same call on an
 * element D3X does not own must still build the DOM it always built.
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

/* states empty on purpose: everything below must hold on beats alone, which
   is the early-return P880 shipped and P883 had to widen. */
D3X.MARKS.length = 0;
D3X.FX_MARKS.length = 0;
const draw = () => { try { D3X._drawStates(); return null; } catch (e) { return e.message; } };
const kidsOf = el => el.children.length;

const chipKids0 = kidsOf(die.chip);
const chipAnims0 = die.chip.getAnimations().length;

/* ══ FLASH - decays from full, so t=0 is its strongest moment ════════ */
FKFX._flash(die.chip);
out.flash = {marks: D3X.FX_MARKS.length,
             kind: (D3X.FX_MARKS[0] || {}).kind,
             threw: draw()};
out.flash.ink = FXH.ink('stCanvas');
out.flash.hue = FXH.hue('stCanvas');
D3X.FX_MARKS.length = 0; draw();
out.flash.clearsAfter = FXH.ink('stCanvas');

/* ══ GLOW - sampled at mid-life ══════════════════════════════════════ */
FKFX._glow(die.chip, '#33cc66', 8, 9000);
out.glow = {marks: D3X.FX_MARKS.length, kind: (D3X.FX_MARKS[0] || {}).kind};
await FXH.sleep(4200);
out.glow.threw = draw();
out.glow.ink = FXH.ink('stCanvas');
out.glow.hue = FXH.hue('stCanvas');
D3X.FX_MARKS.length = 0; draw();

/* ══ BEAM - likewise ═════════════════════════════════════════════════ */
FKFX._beam(die.chip, '#c66058', 9000);
out.beam = {marks: D3X.FX_MARKS.length, kind: (D3X.FX_MARKS[0] || {}).kind};
await FXH.sleep(4200);
out.beam.threw = draw();
out.beam.ink = FXH.ink('stCanvas');
out.beam.hue = FXH.hue('stCanvas');

/* ══ a beat cannot outlive its die ═══════════════════════════════════ */
const wasVisible = die.obj.visible;
die.obj.visible = false;
draw();
out.orphaned = {marksLeft: D3X.FX_MARKS.length, ink: FXH.ink('stCanvas')};
die.obj.visible = wasVisible;

/* ══ they expire on their own ════════════════════════════════════════ */
D3X.FX_MARKS.length = 0;
FKFX._flash(die.chip);
const gone = await FXH.until(() => { draw(); return D3X.FX_MARKS.length === 0; }, 8000);
out.expiry = {cleared: gone != null, ink: FXH.ink('stCanvas')};

/* ══ nothing was built on the chip ═══════════════════════════════════ */
out.chipUntouched = {
  kidsAdded: kidsOf(die.chip) - chipKids0,
  animationsAdded: die.chip.getAnimations().length - chipAnims0,
};

/* ══ CONTROLS - the DOM path is intact for an unowned element ════════ */
const spare = document.createElement('div');
spare.style.cssText = 'position:absolute;left:0;top:0;width:40px;height:40px';
document.body.appendChild(spare);
FKFX._flash(spare);
const afterFlash = spare.children.length;
FKFX._beam(spare, '#c66058', 400);
const afterBeam = spare.children.length;
FKFX._glow(spare, '#33cc66', 8, 400);
out.domPath = {flashBuilt: afterFlash > 0, beamBuilt: afterBeam > afterFlash,
               glowAnimates: spare.getAnimations().length > 0,
               marksNotUsed: D3X.FX_MARKS.length === 0};
spare.remove();

out.VERDICT = {
  /* each primitive registers a beat rather than building DOM */
  flashRegisters: out.flash.marks === 1 && out.flash.kind === 'flash',
  glowRegisters:  out.glow.marks === 1 && out.glow.kind === 'glow',
  beamRegisters:  out.beam.marks === 1 && out.beam.kind === 'beam',
  nothingThrew:   !out.flash.threw && !out.glow.threw && !out.beam.threw,
  /* and each actually paints, on beats alone with no state registered */
  flashPaints: out.flash.ink.exists === true && out.flash.ink.px > 0,
  glowPaints:  out.glow.ink.exists === true && out.glow.ink.px > 0,
  beamPaints:  out.beam.ink.exists === true && out.beam.ink.px > 0,
  /* in the ink they were handed - the flash is the one that is white */
  glowWearsItsInk: !!(out.glow.hue.rgb && out.glow.hue.rgb[1] > out.glow.hue.rgb[0]),
  beamWearsItsInk: !!(out.beam.hue.rgb && out.beam.hue.rgb[0] > out.beam.hue.rgb[2]),
  flashIsWhite: !!(out.flash.hue.rgb && Math.min.apply(null, out.flash.hue.rgb) > 180),
  /* teardown */
  clearingMarksClearsTheSurface: out.flash.clearsAfter.exists === true &&
                                 out.flash.clearsAfter.px === 0,
  aBeatCannotOutliveItsDie: out.orphaned.marksLeft === 0 &&
                            out.orphaned.ink.px === 0,
  beatsExpireOnTheirOwn: out.expiry.cleared === true && out.expiry.ink.px === 0,
  /* the chip is left alone */
  noDomBuiltOnTheChip: out.chipUntouched.kidsAdded === 0 &&
                       out.chipUntouched.animationsAdded === 0,
  /* controls */
  unownedFlashStillBuildsDom: out.domPath.flashBuilt === true,
  unownedBeamStillBuildsDom:  out.domPath.beamBuilt === true,
  unownedGlowStillAnimates:   out.domPath.glowAnimates === true,
  unownedNeverRegistersABeat: out.domPath.marksNotUsed === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
