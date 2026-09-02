/* P902 - the mark layer repaints only when a marked hull changed.
 *
 * THE ONE THING A CACHE MUST PROVE is that it did not change the picture.
 * Everything else is bookkeeping. So the first measurement is a byte compare
 * between the cached path's surface and the same frame forced to repaint -
 * same dice, same pose, same frame, one signature dropped between them.
 *
 * THEN THE TWO WAYS IT CAN BE WRONG:
 *   it never hits, and is only a slower painter;
 *   it hits when it should not, and shows a stale surface.
 * The second is the dangerous one, so every invalidator is driven separately -
 * a die moving, a class arriving, an ink changing, the pass sleeping - rather
 * than trusting that "the signature includes it".
 *
 * AND THE CASE THAT REGRESSED, measured as a rate rather than a state: ten
 * frames of a settled dampened die is what a rival's turn looks like, and it
 * should cost one paint, not ten. Ten frames of a MOVING die should cost ten,
 * because that is the mark following its die and not a saving to be had.
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

const realForm = D3X._paintForm;
let calls = 0;
D3X._paintForm = function () { calls++; return realForm.apply(this, arguments); };
const glow = () => { const before = calls; try { D3X._drawGlow(); } catch (e) {}
                     return calls - before; };
const states = () => { const before = calls; try { D3X._drawStates(); } catch (e) {}
                       return calls - before; };
const pixels = id => { const cv = document.getElementById(id);
  if (!cv || !cv.width) return null;
  return cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data; };
const diff = (a, b) => { if (!a || !b || a.length !== b.length) return -1;
  let n = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) n++; return n; };

/* ── 1. THE PICTURE IS UNCHANGED ─────────────────────────────────────
   THE PAINTER IS WARMED AND THAT RESULT DISCARDED. P889b measured it: the
   first _paintHalo after the scratch canvases are created or resized differs
   from every later one by a constant ~216 bytes, max 1 per channel, almost
   certainly the freshly created mip canvases backing differently from
   resized-and-cleared ones. A probe claiming byte-identical has to account for
   it rather than widen its tolerance to swallow it - and the first run of this
   probe reported exactly 214, which is that artefact and not the cache.
   EVERY STEP IS TRACED. The failure was ambiguous between "the hit repainted"
   and "the first paint was the odd one out", and those want different fixes,
   so each step records its call count, its signature and a checksum. */
const sum = a => { let t = 0; for (let i = 0; i < a.length; i += 997) t += a[i]; return t; };
const trace = [];
const step = (label, fn) => {
  const before = calls; fn(); const c = calls - before;
  const px = pixels('dgCanvas');
  trace.push({label, calls: c, sig: (D3X._glowSig || '').length,
              checksum: px ? sum(px) : null});
  return px ? new Uint8ClampedArray(px) : null;
};
wipe();
dice[0].chip.classList.add('die-dampened');
dice[1].chip.classList.add('die-frozen');
step('warm (discarded)', glow);           /* P889b's first-paint artefact */
D3X._glowSig = '';
const cached = step('paint', glow);
const hitBefore = calls;
const afterHit = step('cache hit', glow);
const hitCalls = calls - hitBefore;
D3X._glowSig = '';                        /* force the same frame to repaint */
const fBefore = calls;
const forced = step('forced repaint', glow);
const forcedCalls = calls - fBefore;
out.trace = trace;
out.identical = {
  litPixels: (() => { let n = 0; for (let i = 3; i < cached.length; i += 4)
    if (cached[i] > 8) n++; return n; })(),
  callsOnFirstPaint: forcedCalls,
  callsOnCacheHit: hitCalls,
  bytesCachedVsHeld: diff(cached, afterHit),
  bytesCachedVsForced: diff(cached, forced),
};

/* ── 2. the invalidators, each driven on its own ───────────────────── */
const invalidate = (label, mutate) => {
  glow();                       /* settle into a hit */
  const idle = glow();          /* confirm it is a hit right now */
  mutate();
  const after = glow();
  return {label, wasHitBefore: idle === 0, repaintedAfter: after > 0};
};
out.invalidators = [
  invalidate('a die moves', () => { dice[0].obj.position.x += 0.12; }),
  invalidate('a class arrives', () => { dice[2].chip.classList.add('die-frozen'); }),
  invalidate('a class leaves', () => { dice[2].chip.classList.remove('die-frozen'); }),
  invalidate('an ink changes', () => {
    dice[0].chip._rrInk = '#8fa8ff'; dice[0].roll = {sol: {frames: []}, t0: 0, val: 1};
  }),
  invalidate('the flight ends', () => { dice[0].roll = null; dice[0]._rrSeen = 1; }),
];

/* ── 3. sleeping clears, and waking repaints ───────────────────────── */
wipe();
const sleepCalls = glow();
const sleptInk = D3X._glowInk, sleptSig = D3X._glowSig;
const sleptPx = FXH.ink('dgCanvas');
dice[0].chip.classList.add('die-dampened');
const wakeCalls = glow();
out.sleepWake = {callsWhileAsleep: sleepCalls, inkFlagAfterSleep: sleptInk,
                 sigAfterSleep: sleptSig, pxAfterSleep: sleptPx.px,
                 sizedAfterSleep: sleptPx.sized, callsOnWake: wakeCalls};

/* ── 4. the rate, which is the thing that regressed ────────────────── */
wipe();
dice[0].chip.classList.add('die-dampened');
let still = 0;
for (let i = 0; i < 10; i++) still += glow();
let moving = 0;
for (let i = 0; i < 10; i++) { dice[0].obj.position.x += 0.05; moving += glow(); }
out.rate = {tenSettledFrames: still, tenMovingFrames: moving};

/* ── 5. beats bypass, because they animate ─────────────────────────── */
wipe();
_dieBeat(dice[0].chip, 'rim', D3X.BEAT_INK.gold, 700);
D3X.FX_MARKS[0].t0 -= 200;
const beatA = states();
D3X.FX_MARKS[0].t0 -= 100;      /* the envelope has moved on */
const beatB = states();
out.beats = {firstFrame: beatA, secondFrame: beatB};

/* and the over pass caches when nothing is beating */
wipe();
dice[0].chip.classList.add('die-blind');
const overFirst = states(), overSecond = states();
out.overCache = {firstFrame: overFirst, secondFrame: overSecond};
wipe();
D3X._paintForm = realForm;

out.VERDICT = {
  /* 1 - the only assertion that really matters */
  itPaintedSomethingToBeginWith: out.identical.litPixels > 2000 &&
                                 out.identical.callsOnFirstPaint > 0,
  aCacheHitCostsNothing: out.identical.callsOnCacheHit === 0,
  theHeldSurfaceIsUntouched: out.identical.bytesCachedVsHeld === 0,
  theForcedRepaintIsByteIdentical: out.identical.bytesCachedVsForced === 0,
  /* 2 - and it must not hit when it should not */
  everyInvalidatorWasAHitFirst: out.invalidators.every(i => i.wasHitBefore),
  everyInvalidatorRepaints: out.invalidators.every(i => i.repaintedAfter),
  /* 3 */
  sleepingPaintsNothing: out.sleepWake.callsWhileAsleep === 0,
  sleepingClearsTheSurface: out.sleepWake.pxAfterSleep === 0 &&
                            out.sleepWake.inkFlagAfterSleep === false,
  sleepingDropsTheSignature: out.sleepWake.sigAfterSleep === '',
  wakingRepaints: out.sleepWake.callsOnWake > 0,
  /* 4 - the regression, as a rate */
  /* AT MOST one: the surface may already hold the right paint when the run
     starts, and a zero there is the cache working rather than failing. Ten was
     the number before. */
  tenSettledFramesCostAtMostOnePaint: out.rate.tenSettledFrames <= 1,
  tenMovingFramesStillPaintTen: out.rate.tenMovingFrames === 10,
  /* 5 */
  aBeatRepaintsEveryFrame: out.beats.firstFrame > 0 && out.beats.secondFrame > 0,
  theOverPassCachesWithoutBeats: out.overCache.firstFrame > 0 &&
                                 out.overCache.secondFrame === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
