/* P896 - beats armed with their ink, and the eight inert classes routed.
 *
 * THE CLAIM UNDER TEST is a design one, so most of this is about the shape:
 * an ink that belongs to the FIRING rather than to the die, a clock per
 * entry, and no change to the roster. Each is measured as a mechanism, not
 * inferred from a pixel count that a dead wire would also produce.
 *
 * THE SPY IS THE POINT OF SECTION F. "The beat and the state now share one
 * painter" is exactly the kind of claim a byte-comparison cannot settle -
 * two identical drawings look identical whether or not they came from the
 * same code. So _paintForm is wrapped and the beat path has to be seen
 * calling it, with the form it claims.
 *
 * BEATS ARE SAMPLED BY BACKDATING, and that is not a workaround. Measured
 * here: arming and drawing inside one probe tick gives performance.now() the
 * SAME value twice - the clock is clamped - so t is exactly 0, the envelope
 * correctly returns 0, and every beat assertion reads a blank canvas for a
 * reason that has nothing to do with the code. Backdating t0 to a chosen
 * phase is the same technique this harness already uses for d.nudge.t0, and
 * it is what makes the phase deliberate rather than whatever the scheduler
 * happened to give. In the shipped game the arm and the paint are always at
 * least a frame apart, so the t<=0 branch is only ever the arming instant.
 *
 * SECTION H DRIVES A REAL CALL SITE. Everything above it exercises the
 * primitive, which is where a routing patch is least likely to be wrong; the
 * risk is in the eighteen substitutions. refreshSelUI is the one site a probe
 * can reach without a card, so a forced combo goes through the shipped path
 * and the beats are read off the other end.
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

const clearBeats = () => { D3X.FX_MARKS = []; };
const paintOver = () => { try { D3X._drawStates(); } catch (e) { return 'threw: ' + e.message; }
                          return null; };
const overPx = () => FXH.ink('stCanvas');

/* ── A. the envelope, as a function ─────────────────────────────── */
const mk = (delay, env, ms) => ({t0: 0, delay: delay, env: env || null, ms: ms || 400});
const E = {'in': 100, hold: 140, out: 200};
out.envelope = {
  beforeDelay: D3X._beatAlpha(mk(140, E), 100),
  atDelay: D3X._beatAlpha(mk(140, E), 140),
  midRampIn: +D3X._beatAlpha(mk(140, E), 190).toFixed(3),
  onHold: D3X._beatAlpha(mk(140, E), 300),
  midFadeOut: +D3X._beatAlpha(mk(140, E), 480).toFixed(3),
  afterOut: D3X._beatAlpha(mk(140, E), 600),
  /* and with no sheet, the old sine swell is unchanged */
  sineAtPeak: +D3X._beatAlpha(mk(0, null, 400), 200).toFixed(3),
  sineAtStart: +D3X._beatAlpha(mk(0, null, 400), 1).toFixed(3),
};

/* ── B. arm through the real helper the 18 sites call ───────────── */
clearBeats();
const armedB = _dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
out.arm = {
  returned: armedB,
  entries: D3X.FX_MARKS.length,
  entry: D3X.FX_MARKS[0] ? {kind: D3X.FX_MARKS[0].kind, ink: D3X.FX_MARKS[0].ink,
                            ms: D3X.FX_MARKS[0].ms, delay: D3X.FX_MARKS[0].delay,
                            boundToTheRightDie: D3X.FX_MARKS[0].d === dice[0]} : null,
  /* a chip that is not in the 3D layer must be answered false, not silently
     swallowed - "no die" and "no beat" were the same thing under the classes */
  unknownChip: _dieBeat(document.createElement('div'), 'rim', '#ffffff', 700),
};
/* mid-life, deliberately: sin(0.5*PI) = 1, the beat at its peak */
const phase = (ms) => { if (D3X.FX_MARKS[0]) D3X.FX_MARKS[0].t0 -= ms; };
phase(350);
const bThrew = paintOver();
const bInk = overPx();
const bHue = FXH.hue('stCanvas');
out.arm.painted = {px: bInk.px, exists: bInk.exists, threw: bThrew,
                   hex: bHue.hex || null, rgb: bHue.rgb || null};

/* ── C. two firings, one die - what the CSS could never hold ────── */
clearBeats();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.red, 700);
out.twoFiringsOneDie = {
  entries: D3X.FX_MARKS.length,
  inks: D3X.FX_MARKS.map(k => k.ink),
  sameDie: D3X.FX_MARKS.length === 2 && D3X.FX_MARKS[0].d === D3X.FX_MARKS[1].d,
};

/* ── D. the tag is "this beat, again" ───────────────────────────── */
clearBeats();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.combo, {ms: 450, tag: 'combo'});
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.combo, {ms: 450, tag: 'combo'});
const tagged = D3X.FX_MARKS.length;
_dieBeat(dice[1].chip, 'rim', D3X.BEAT_INK.combo, {ms: 450, tag: 'combo'});
const taggedTwoDice = D3X.FX_MARKS.length;
clearBeats();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
out.tag = {sameDieSameTag: tagged, sameTagTwoDice: taggedTwoDice,
           untaggedStack: D3X.FX_MARKS.length};

/* ── E. a delayed beat is armed, invisible, and NOT expired ─────── */
clearBeats();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, {ms: 200, delay: 4000});
const delayedThrew = paintOver();
const delayedInk = overPx();
out.delayed = {
  entriesAfterPaint: D3X.FX_MARKS.length,   /* the expiry must count the delay */
  px: delayedInk.px, threw: delayedThrew,
  alphaNow: D3X._beatAlpha(D3X.FX_MARKS[0] || mk(0), performance.now()),
};

/* ── F. THE SPY: is the beat really going through _paintForm? ───── */
clearBeats();
const realForm = D3X._paintForm;
const seen = [];
D3X._paintForm = function (style, cv, x, sc, dpr, hulls, col, soft, am) {
  seen.push({style: style, col: col, am: am == null ? null : +am.toFixed(3),
             hulls: hulls.length});
  return realForm.apply(this, arguments);
};
try {
  _dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.blue, 700);
  phase(350);
  paintOver();
} finally { D3X._paintForm = realForm; }
out.sharedPainter = {
  calls: seen.length,
  formsUsed: seen.map(s => s.style),
  beatCall: seen.filter(s => s.col === D3X.BEAT_INK.blue)[0] || null,
};

/* ── G. DIM is not a canvas form, and its three real routes are ─── */
out.dim = {
  dialGone: D3X.DIM === undefined,
  spentLook: typeof D3X._spentLook === 'function',
  keptLook: typeof D3X._keptLook === 'function',
  trayTint: typeof D3X._trayTint === 'function',
  formsInPainter: (function () {
    const src = D3X._paintForm.toString();
    return ['crust', 'veil', 'dim'].filter(f => src.indexOf("'" + f + "'") >= 0);
  })(),
};

/* ── H. A REAL CALL SITE, driven through the shipped path ───────── */
clearBeats();
let comboWhy = null;
try {
  const free = G.pool.filter(d => !d.committed && !d._frozen);
  if (free.length < 3) comboWhy = 'need three free dice, had ' + free.length;
  else {
    free.forEach(d => { d.sel = false; if (d.el) d.el.classList.remove('selected'); });
    free.slice(0, 3).forEach(d => { d.val = 1; d.sel = true;
      if (d.el) d.el.classList.add('selected'); });
    refreshSelUI();
  }
} catch (e) { comboWhy = 'threw: ' + e.message; }
out.realCallSite = {
  why: comboWhy,
  beats: D3X.FX_MARKS.length,
  tags: D3X.FX_MARKS.map(k => k.tag),
  inks: D3X.FX_MARKS.map(k => k.ink),
  delays: D3X.FX_MARKS.map(k => k.delay),
  /* the bookkeeping that existed only for the class must be gone */
  comboFlagGone: G._comboGlow === undefined,
  comboTimerGone: G._comboTimer === undefined,
};

/* ── I. completeness, against the served file ───────────────────── */
const page = await (await fetch('/fark_proto.html')).text();
const count = re => (page.match(re) || []).length;
out.sites = {
  dieBeatCalls: count(/_dieBeat\(/g) - 1,      /* minus the declaration */
  helperDeclared: count(/function _dieBeat\(/g),
  effGlowAdds: count(/classList\.add\([^)]*'eff-glow-/g),
  effGlowComposed: count(/'eff-glow-'\+/g),
  cardRerollAdds: count(/classList\.add\([^)]*'card-reroll/g),
  comboGlowAdds: count(/classList\.add\([^)]*'combo-glow'/g),
  /* the PROPERTY, not the word: the comment recording its deletion contains
     the string, and a probe that counts raw text would fail on its own
     tombstone */
  gdProperty: count(/(?:set|remove)Property\('--gd'/g),
};

/* ── the verdict ────────────────────────────────────────────────── */
const en = out.envelope;
out.VERDICT = {
  /* A - the sheet's shape, and the old default untouched */
  delayHoldsTheBeatBack: en.beforeDelay === 0,
  rampsInOverItsIn: en.atDelay === 0 && en.midRampIn > 0.4 && en.midRampIn < 0.6,
  holdsAtFull: en.onHold === 1,
  fadesOverItsOut: en.midFadeOut > 0.4 && en.midFadeOut < 0.6,
  endsAtZero: en.afterOut === 0,
  sineIsStillTheDefault: en.sineAtPeak > 0.99 && en.sineAtStart < 0.02,

  /* B - the helper the 18 sites call actually arms and paints */
  armReturnsTrue: out.arm.returned === true,
  armMakesOneEntry: out.arm.entries === 1,
  armBindsTheRightDie: !!out.arm.entry && out.arm.entry.boundToTheRightDie === true,
  armCarriesItsInk: !!out.arm.entry && out.arm.entry.ink === D3X.BEAT_INK.gold,
  anUnknownChipIsAnswered: out.arm.unknownChip === false,
  theBeatPaints: out.arm.painted.px > 200 && out.arm.painted.exists === true,
  nothingThrew: !out.arm.painted.threw && !out.delayed.threw,
  itPaintsItsOwnInk: !!out.arm.painted.rgb &&
    out.arm.painted.rgb[0] > out.arm.painted.rgb[2] + 40 &&
    out.arm.painted.rgb[1] > out.arm.painted.rgb[2] + 20,

  /* C - the reason a row could not hold this */
  twoFiringsCoexistOnOneDie: out.twoFiringsOneDie.entries === 2 &&
    out.twoFiringsOneDie.sameDie === true &&
    out.twoFiringsOneDie.inks[0] !== out.twoFiringsOneDie.inks[1],

  /* D - re-arming under a tag replaces; without one it stacks */
  tagReplaces: out.tag.sameDieSameTag === 1,
  tagIsPerDie: out.tag.sameTagTwoDice === 2,
  untaggedStillStacks: out.tag.untaggedStack === 2,

  /* E - a staggered beat must survive to its turn */
  delayedBeatSurvivesTheExpiry: out.delayed.entriesAfterPaint === 1,
  delayedBeatPaintsNothingYet: out.delayed.px === 0,
  delayedAlphaIsZero: out.delayed.alphaNow === 0,

  /* F - the mechanism, not a matching picture */
  beatGoesThroughPaintForm: !!out.sharedPainter.beatCall,
  andAsksForARim: !!out.sharedPainter.beatCall &&
                  out.sharedPainter.beatCall.style === 'rim',
  withItsEnvelopeAlpha: !!out.sharedPainter.beatCall &&
                        out.sharedPainter.beatCall.am > 0 &&
                        out.sharedPainter.beatCall.am <= 1,

  /* G - DIM was never a canvas form */
  dimDialGone: out.dim.dialGone === true,
  dimBranchGone: out.dim.formsInPainter.indexOf('dim') < 0,
  crustAndVeilRemain: out.dim.formsInPainter.indexOf('crust') >= 0 &&
                      out.dim.formsInPainter.indexOf('veil') >= 0,
  allThreeMaterialRoutesPresent: out.dim.spentLook && out.dim.keptLook && out.dim.trayTint,

  /* H - a real site, through the shipped path */
  theRealSiteRan: out.realCallSite.why === null,
  itArmedOnePerSelectedDie: out.realCallSite.beats === 3,
  taggedCombo: out.realCallSite.tags.every(t => t === 'combo'),
  inTheComboInk: out.realCallSite.inks.every(i => i === D3X.BEAT_INK.combo),
  staggeredSeventyApart: JSON.stringify(out.realCallSite.delays) === '[0,70,140]',
  theClassBookkeepingIsGone: out.realCallSite.comboFlagGone === true &&
                             out.realCallSite.comboTimerGone === true,

  /* I - all eighteen, and no survivors */
  eighteenSitesRouted: out.sites.dieBeatCalls === 18,
  oneHelper: out.sites.helperDeclared === 1,
  noEffGlowAddsLeft: out.sites.effGlowAdds === 0 && out.sites.effGlowComposed === 0,
  noCardRerollAddsLeft: out.sites.cardRerollAdds === 0,
  noComboGlowAddsLeft: out.sites.comboGlowAdds === 0,
  theGdPropertyIsGone: out.sites.gdProperty === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
