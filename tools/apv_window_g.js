/* P886 - the three dead `window.G` guards.
 *
 * Each site gets a positive control that could fail, and the premise itself is
 * measured rather than assumed: window.G must be absent while the `var`
 * globals are present, or every claim below is about the wrong thing.
 *
 * Site C's `finally` is exercised by an ACTUAL THROW, not by reading the
 * source. Making the isolation real created a hazard the dead line never had -
 * a throw mid-sim would leave a live match holding a null G - so the thing
 * that must be proven is the recovery, not the assignment.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

/* ══ 0. THE PREMISE ══════════════════════════════════════════════════ */
out.premise = {
  windowG: typeof window.G,
  windowGIsOwnProperty: Object.prototype.hasOwnProperty.call(window, 'G'),
  bindingExists: (typeof G !== 'undefined'),
  varControlD3X: typeof window.D3X,
  varControlFKFX: typeof window.FKFX,
};

const m = await FXH.match(1);
if (!m.ok) return Object.assign(out, {err: m.why});
const savedG = G;

/* ══ A. THE BANK SOUND PITCHES WITH THE RUN ══════════════════════════ */
const TONES = [];
const realTone = SFX._tone, realClick = SFX._click;
SFX._tone = function (f) { TONES.push(Math.round(f)); return realTone.apply(this, arguments); };
SFX._click = function (f) { TONES.push(Math.round(f)); return realClick.apply(this, arguments); };
const bankAt = (p) => {
  TONES.length = 0;
  G = {target: 1000, pPts: Math.round(1000 * p)};
  try { SFX.bank(); } catch (e) { TONES.push('threw:' + e.message); }
  return TONES.slice();
};
out.bank = {
  at20: bankAt(0.20), at70: bankAt(0.70), at88: bankAt(0.88), at98: bankAt(0.98),
};
G = null;
out.bank.gNull = (function () { TONES.length = 0; try { SFX.bank(); } catch (e) {} return TONES.slice(); })();
SFX._tone = realTone; SFX._click = realClick;

const key = a => a.join(',');
out.bank.distinctVariants = new Set([out.bank.at20, out.bank.at70,
  out.bank.at88, out.bank.at98].map(key)).size;
out.bank.hotHarmonicAt88 = out.bank.at88.length > out.bank.at20.length;
out.bank.instrumentSawCalls = out.bank.at20.length;

/* ══ B. TAP-TO-FAST-FORWARD REACHES _ffMult ══════════════════════════ */
const tapAt = (el) => {
  if (!el) return null;
  G = {_oppTurnActive: true, _ffMult: 1};
  const r = el.getBoundingClientRect();
  el.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true,
    clientX: r.left + r.width / 2, clientY: r.top + r.height / 2}));
  return G._ffMult;
};
const board = document.getElementById('matchShadows') ||
              document.getElementById('screen-match');
out.fastForward = {
  onBoard: tapAt(board),
  offBoard: tapAt(document.body),
  onAButton: tapAt(document.querySelector('#screen-match button, #screen-match .btn')),
};
/* the negative control that matters: not during a rival turn */
G = {_oppTurnActive: false, _ffMult: 1};
if (board) board.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true}));
out.fastForward.notRivalTurn = G._ffMult;
/* and the consumer actually reads it */
G = {_oppTurnActive: true, _ffMult: 0.15};
out.fastForward.oppDelayHonoursIt = (typeof _oppDelay === 'function')
  ? {at1900: _oppDelay(1900), at260: _oppDelay(260)} : null;
G = {_oppTurnActive: true, _ffMult: 1};
out.fastForward.oppDelayUnaccelerated = (typeof _oppDelay === 'function')
  ? {at1900: _oppDelay(1900), at260: _oppDelay(260)} : null;

/* ══ C. THE SIM REALLY DOES NEUTRALISE oppShouldBank ═════════════════ */
const LIVE = {_sealRule: 'mending', _oRollNum: 0, target: 4000, pPts: 0};
G = LIVE;
out.simSetup = {
  mendingActiveBeforeSim: (typeof _ruleActive === 'function')
    ? _ruleActive('mending', 'o') : null,
};

const seen = [];
const realOSB = window.oppShouldBank;
window.oppShouldBank = function () {
  seen.push({gIsNull: !G,
             mending: (typeof _ruleActive === 'function') ? _ruleActive('mending', 'o') : null});
  return realOSB.apply(this, arguments);
};
let simErr = null;
try { _runBalanceSim({iters: 4}); } catch (e) { simErr = e.message; }
window.oppShouldBank = realOSB;
out.simIsolation = {
  err: simErr,
  callsObserved: seen.length,
  everSawALiveG: seen.some(s => !s.gIsNull),
  everSawMendingActive: seen.some(s => s.mending === true),
  gRestoredAfter: G === LIVE,
};

/* the finally, exercised by a real throw */
G = LIVE;
const realGP = window.generatePatron;
window.generatePatron = function () { throw new Error('probe-forced'); };
let threw = false;
try { _runBalanceSim({iters: 2}); } catch (e) { threw = true; }
window.generatePatron = realGP;
out.simThrow = {threw, gRestoredAfterThrow: G === LIVE};

G = savedG;

out.VERDICT = {
  /* 0 - the premise the whole patch rests on */
  windowGIsAbsent: out.premise.windowG === 'undefined' &&
                   out.premise.windowGIsOwnProperty === false,
  bindingIsPresent: out.premise.bindingExists === true,
  varGlobalsAreOnWindow: out.premise.varControlD3X === 'object' &&
                         out.premise.varControlFKFX === 'object',
  /* A */
  bankInstrumentSawSomething: out.bank.instrumentSawCalls >= 3,
  bankPitchesWithProgress:    out.bank.distinctVariants === 4,
  bankAddsAHotHarmonic:       out.bank.hotHarmonicAt88 === true,
  bankIsFlatWithNoRun:        key(out.bank.gNull) === key(out.bank.at20),
  /* B */
  tapOnBoardFastForwards: out.fastForward.onBoard === 0.15,
  tapOffBoardDoesNot:     out.fastForward.offBoard === 1,
  tapOnAButtonDoesNot:    out.fastForward.onAButton === null ||
                          out.fastForward.onAButton === 1,
  notDuringRivalTurnDoesNot: out.fastForward.notRivalTurn === 1,
  theDelayActuallyShortens: !!(out.fastForward.oppDelayHonoursIt &&
    out.fastForward.oppDelayHonoursIt.at1900 <
    out.fastForward.oppDelayUnaccelerated.at1900),
  /* C */
  mendingWasLiveBeforeTheSim: out.simSetup.mendingActiveBeforeSim === true,
  simRan:                     out.simIsolation.err === null &&
                              out.simIsolation.callsObserved > 0,
  simNeverSawALiveG:          out.simIsolation.everSawALiveG === false,
  simNeverSawTheSealedRule:   out.simIsolation.everSawMendingActive === false,
  simRestoresTheBinding:      out.simIsolation.gRestoredAfter === true,
  theFinallyIsExercised:      out.simThrow.threw === true,
  aThrowStillRestoresIt:      out.simThrow.gRestoredAfterThrow === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
