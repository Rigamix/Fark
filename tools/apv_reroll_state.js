/* P899 - the reroll as a MARKS row, and the harness's new `sized`.
 *
 * WHAT HAS TO BE TRUE, and each is measured as a mechanism rather than as a
 * pixel count that a dead wire would also produce:
 *
 *   A  `sized` catches the case that lied. A canvas at its 300x150 default is
 *      not zero-width, so the old width check passed it; a read from it comes
 *      back 0 lit with no error. Three values, because absence and mis-sizing
 *      are different findings.
 *   B  the predicate needs BOTH the flight and the tag. Tag alone: dead. Roll
 *      alone: dead - and that is the important half, because bare d.roll would
 *      light every die in an ordinary roll.
 *   C  it survives a roll, which is the whole point of the row. through:true is
 *      load-bearing here in a way it is not for the other states.
 *   D  one _paintForm call per distinct ink, read off a spy rather than
 *      inferred from the picture.
 *   E  the tag's one exit fires on landing, and NOT before the flight starts -
 *      the transition, not a bare absence.
 *   F  after it clears, an ordinary roll does not wear the card's colour.
 *   G  and a real call site drives all of it end to end.
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
const row = (D3X.MARKS || []).filter(w => w.id === 'reroll')[0] || null;
out.row = row ? {layer: row.layer, through: row.through, style: row.style,
                 hasInkOf: typeof row.inkOf === 'function'} : null;
if (!row) return Object.assign(out, {err: 'no reroll row'});

const rolling = () => D3X.dice.filter(d => d.match && d.roll).length;
const live = () => { try { return D3X._markDice(row).length; } catch (e) { return -1; } };
const clearTags = () => dice.forEach(d => { d.chip._rrInk = null; d._rrSeen = 0; });
const fakeRoll = (d, on) => { d.roll = on ? {sol: {frames: []}, i: 0, t0: 0, val: 1} : null; };

/* ── A. sized, on all three of its answers ─────────────────────────── */
const stray = document.createElement('canvas');   /* 300x150, the liar */
document.body.appendChild(stray);
out.sized = {
  expected: FXH.expectedSize(),
  defaultCanvas: FXH.sizedOf(stray),
  missingCanvas: FXH.sizedOf(null),
  strayIsNotZeroWidth: stray.width > 0,
};
stray.remove();

/* ── B. the predicate needs both halves ────────────────────────────── */
clearTags();
const before = live();
dice[0].chip._rrInk = '#ffb428';
const tagOnly = live();
dice[0].chip._rrInk = null;
fakeRoll(dice[0], true);
const rollOnly = live();
dice[0].chip._rrInk = '#ffb428';
const both = live();
out.predicate = {neither: before, tagOnly, rollOnly, both};

/* ── C. it survives a roll, and D. one call per ink ────────────────── */
fakeRoll(dice[1], true);
dice[1].chip._rrInk = '#8fa8ff';      /* a second, different cause */
fakeRoll(dice[2], true);
dice[2].chip._rrInk = '#ffb428';      /* same ink as die 0 */
const realForm = D3X._paintForm;
const seen = [];
D3X._paintForm = function (style, cv, x, sc, dpr, hulls, col, soft, am, over) {
  seen.push({style, col, hulls: hulls.length, over: !!over});
  return realForm.apply(this, arguments);
};
let drawThrew = null;
try { D3X._drawGlow(); } catch (e) { drawThrew = e.message; }
finally { D3X._paintForm = realForm; }
const dg = FXH.ink('dgCanvas');
out.whileRolling = {
  diceMatched: live(),
  paintCalls: seen.length,
  callsForThisRow: seen.filter(c => c.col === '#ffb428' || c.col === '#8fa8ff'),
  underCanvas: {px: dg.px, exists: dg.exists, sized: dg.sized},
  threw: drawThrew,
  rollingFlagWasTrue: D3X._rolling(),
};

/* ── E. the tag's exit: not before the flight, yes after it ────────── */
clearTags();
dice[0].chip._rrInk = '#ffb428';       /* armed, flight not started yet */
try { D3X._drawGlow(); } catch (e) {}
const survivedTheGap = dice[0].chip._rrInk;
fakeRoll(dice[0], true);
try { D3X._drawGlow(); } catch (e) {}  /* seen in the air */
const heldWhileFlying = dice[0].chip._rrInk;
fakeRoll(dice[0], false);
try { D3X._drawGlow(); } catch (e) {}  /* landed */
const clearedOnLanding = dice[0].chip._rrInk;
out.tagExit = {survivedTheGap, heldWhileFlying, clearedOnLanding,
               seenFlag: dice[0]._rrSeen};

/* ── F. an ordinary roll must not wear a card's colour ─────────────── */
clearTags();
dice.forEach(d => fakeRoll(d, true));
out.ordinaryRollIsUnmarked = live();
dice.forEach(d => fakeRoll(d, false));

/* ── G. a real call site, end to end ───────────────────────────────── */
clearTags();
let siteWhy = null, sawLive = 0, sawInk = null, sawRolling = 0;
try {
  const free = G.pool.filter(d => !d.committed && !d._frozen && d.el);
  if (free.length < 2) siteWhy = 'need two free dice';
  else {
    /* the flask rerolls NON-SCORING dice, so give it two */
    free[0].val = 2; free[1].val = 3;
    try { reDrawDieFace(free[0]); reDrawDieFace(free[1]); } catch (e) {}
    await FXH.until(() => rolling() === 0, 20000);
    clearTags();
    activateGrogsFlask();
    /* poll for the row going live DURING the flight */
    const t0 = Date.now();
    while (Date.now() - t0 < 8000) {
      const n = live();
      if (n > sawLive) { sawLive = n;
        sawInk = (D3X._markDice(row)[0] || {chip: {}}).chip._rrInk || null;
        sawRolling = rolling(); }
      if (sawLive && rolling() === 0) break;
      await FXH.sleep(50);
    }
    await FXH.until(() => rolling() === 0, 20000);
    try { D3X._drawGlow(); } catch (e) {}
  }
} catch (e) { siteWhy = 'threw: ' + e.message; }
out.realSite = {
  why: siteWhy, markedDuringFlight: sawLive, inkSeen: sawInk,
  diceInTheAirThen: sawRolling,
  liveAfterLanding: live(),
  tagsAfterLanding: dice.filter(d => d.chip._rrInk).length,
};

out.VERDICT = {
  /* A */
  sizedCatchesTheDefaultCanvas: out.sized.defaultCanvas === false &&
                                out.sized.strayIsNotZeroWidth === true,
  sizedIsNullWhenThereIsNoCanvas: out.sized.missingCanvas === null,
  sizedKnowsWhatThePaintersUse: !!out.sized.expected && out.sized.expected.w > 100,
  /* B */
  aTagAloneDoesNotLight: out.predicate.neither === 0 && out.predicate.tagOnly === 0,
  aRollAloneDoesNotLight: out.predicate.rollOnly === 0,
  bothTogetherDo: out.predicate.both === 1,
  /* C */
  itPaintsWhileTheDiceAreRolling: out.whileRolling.rollingFlagWasTrue === true &&
                                  out.whileRolling.diceMatched === 3 &&
                                  out.whileRolling.underCanvas.px > 200,
  andOnAProperlySizedSurface: out.whileRolling.underCanvas.sized === true,
  nothingThrew: !out.whileRolling.threw,
  /* D - two inks across three dice means two calls, not three and not one */
  oneCallPerDistinctInk: out.whileRolling.callsForThisRow.length === 2,
  theCallsCarryBothInks: out.whileRolling.callsForThisRow.some(c => c.col === '#ffb428') &&
                         out.whileRolling.callsForThisRow.some(c => c.col === '#8fa8ff'),
  andTheGroupsAreRight: out.whileRolling.callsForThisRow
    .some(c => c.col === '#ffb428' && c.hulls === 2),
  itIsAnUnderRow: out.whileRolling.callsForThisRow.every(c => c.over === false),
  /* E */
  theTagSurvivesTheArmingGap: out.tagExit.survivedTheGap === '#ffb428',
  theTagHoldsWhileFlying: out.tagExit.heldWhileFlying === '#ffb428',
  theTagClearsOnLanding: out.tagExit.clearedOnLanding === null,
  /* F */
  anOrdinaryRollIsNotMarked: out.ordinaryRollIsUnmarked === 0,
  /* G */
  theRealSiteRan: out.realSite.why === null,
  theRealSiteMarkedItsDice: out.realSite.markedDuringFlight >= 1,
  inTheRerollInk: out.realSite.inkSeen === '#ffb428',
  andTheDiceWereActuallyInTheAir: out.realSite.diceInTheAirThen >= 1,
  theMarkEndsWithTheFlight: out.realSite.liveAfterLanding === 0 &&
                            out.realSite.tagsAfterLanding === 0,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
