/* Two questions that are each one run, and both were half-answered.
 *
 * A. IS THERE A FLOOR, OR IS IT CREATION-SCOPED? My last table had one nonzero
 *    cell in four and I read a main effect off it; both marginals were that one
 *    cell counted twice. So: warm, then twenty adjacent full paints, every pair
 *    diffed. All zero says creation-scoped. Sporadic nonzero says a real floor.
 *
 *    AND IT IS ESTABLISHED POSITIVELY, not by absence. A second block FORCES the
 *    scratches to be re-created - _glowTmp, _haloS and both mip arrays dropped -
 *    and repeats the twenty. If instability appears there and only there, the
 *    cause is creation rather than "somewhere early in a sequence", which is all
 *    the last run could have shown. (The previous run's reset resized dgCanvas
 *    only; _paintHalo re-backs its scratches when their dimensions DIFFER from
 *    cv's, and assigning the same width changes nothing - so that block was not
 *    against fresh scratches, which is why it could not have decided this.)
 *
 * B. WHAT THE KEPT TRAY DOES TO THE BAND. #aboveDiceInfo measured zero height,
 *    and the reason is CSS rather than state: min-height 0, and its only child
 *    .kept-tray is display:none until .has-items. So the band cannot be read
 *    while the tray is empty - a mark on a tray die would be clipped, and a
 *    tray die can be d3on.
 *    The same measurement answers a second question the markup raises against
 *    itself: the comment says the tray is fixed-height to prevent shifts. If
 *    #throwLine MOVES when the tray populates, then the throwing row shifts on
 *    the player's first keep, which is a gameplay defect independent of any
 *    canvas work.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const rs = await FXH.rollAndSettle();
out.rolled = {ok: rs.ok, why: rs.why, freeDice: rs.freeDice};
if (!(rs.freeDice > 0)) return Object.assign(out, {err: 'no dice: ' + rs.why});

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
const GL = D3X.GLOW;                       /* never `G` - P904 */
const dice = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip);
if (!dice.length) return Object.assign(out, {err: 'no drawable dice'});

/* ══ A. the floor ═══════════════════════════════════════════════════ */
const STATE = ['die-frozen', 'die-dampened', 'dampen-fade', 'die-blind', 'selected'];
dice.forEach(d => d.chip.classList.remove.apply(d.chip.classList, STATE));
dice[0].chip.classList.add('die-dampened');
if (dice[1]) dice[1].chip.classList.add('die-frozen');

const px = () => { const cv = document.getElementById('dgCanvas');
  return cv && cv.width
    ? new Uint8ClampedArray(cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data)
    : null; };
const diff = (a, b) => { if (!a || !b || a.length !== b.length) return -1;
  let n = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) n++; return n; };
const paint = () => { D3X._glowSig = ''; try { D3X._drawGlow(); } catch (e) {} };

/* drop every scratch surface so the next paint has to create them again */
const dropScratches = () => {
  D3X._glowTmp = null; D3X._haloS = null; D3X._mips = []; D3X._mups = [];
};

const run20 = () => {
  const pairs = [];
  paint(); let prev = px();
  for (let i = 0; i < 20; i++) { paint(); const cur = px();
    pairs.push(diff(prev, cur)); prev = cur; }
  return pairs;
};

/* block 1: scratches already exist and are warm from the run above */
paint(); paint(); paint();                 /* settle past any creation effect */
out.warmBlock = run20();
/* block 2: force creation, then the same twenty */
dropScratches();
out.freshBlock = run20();
/* block 3: and again warm, to show block 2 was the creation and not the order */
out.warmAgainBlock = run20();

const nz = a => a.filter(x => x > 0);
out.floor = {
  warm: {nonzero: nz(out.warmBlock).length, max: Math.max.apply(null, out.warmBlock)},
  fresh: {nonzero: nz(out.freshBlock).length, max: Math.max.apply(null, out.freshBlock),
          firstThree: out.freshBlock.slice(0, 3)},
  warmAgain: {nonzero: nz(out.warmAgainBlock).length,
              max: Math.max.apply(null, out.warmAgainBlock)},
};
/* WHERE in the fresh block does it sit? Creation-scoped means the front. */
out.floor.fresh.indexesNonzero = out.freshBlock
  .map((v, i) => v > 0 ? i : -1).filter(i => i >= 0);

dice.forEach(d => d.chip.classList.remove.apply(d.chip.classList, STATE));
paint();

/* ══ B. the tray, and whether the throwing row moves ════════════════ */
const box = id => { const el = document.getElementById(id); if (!el) return null;
  const r = el.getBoundingClientRect();
  return {top: +(r.top - sc.top).toFixed(1), bottom: +(r.bottom - sc.top).toFixed(1),
          h: +r.height.toFixed(1)}; };
const shot = () => ({above: box('aboveDiceInfo'), tray: box('keptTray'),
                     throwLine: box('throwLine'), keptZone: box('keptZone')});
out.trayHidden = shot();
out.trayCss = (function () {
  const t = document.getElementById('keptTray');
  if (!t) return null;
  const cs = getComputedStyle(t);
  const a = document.getElementById('aboveDiceInfo');
  const acs = a ? getComputedStyle(a) : null;
  return {trayDisplay: cs.display, trayHasItems: t.classList.contains('has-items'),
          aboveMinHeight: acs ? acs.minHeight : null};
})();

/* populate it the way the game does - the class, and a real die node, so the
   height comes from content rather than from a guess */
const tray = document.getElementById('keptTray');
let clone = null;
if (tray) {
  tray.classList.add('has-items');
  const src = dice[0].chip;
  clone = src.cloneNode(true);
  clone.removeAttribute('id');
  tray.appendChild(clone);
}
await FXH.sleep(150);
out.trayShown = shot();
out.trayShownCss = tray ? {trayDisplay: getComputedStyle(tray).display} : null;

const d = (a, b, k) => (a && b && a[k] != null && b[k] != null)
  ? +(b[k] - a[k]).toFixed(1) : null;
out.shift = {
  aboveGrewBy: d(out.trayHidden.above, out.trayShown.above, 'h'),
  throwLineMovedBy: d(out.trayHidden.throwLine, out.trayShown.throwLine, 'top'),
  keptZoneMovedBy: d(out.trayHidden.keptZone, out.trayShown.keptZone, 'top'),
};

/* the band, with the tray up - which is the only state it can be read in */
const reachY = GL.soft * GL.sy + GL.line / 2 + GL.clear;
const boxes = [out.trayShown.above, out.trayShown.throwLine, out.trayShown.keptZone]
  .filter(b => b && b.h > 0);
out.bandWithTray = boxes.length ? (function () {
  const top = Math.min.apply(null, boxes.map(b => b.top)) - reachY;
  const bottom = Math.max.apply(null, boxes.map(b => b.bottom)) + reachY;
  return {top: +top.toFixed(1), bottom: +bottom.toFixed(1),
          h: +(bottom - top).toFixed(1),
          fractionOfScreen: +((bottom - top) / sc.height).toFixed(3)};
})() : null;

/* AND IN cqw, because the dice are 13cqw and the kept zone reserves 15cqw - a
   hard-coded pixel pad clips on a different viewport */
const cq = sc.width / 100;
out.inCqw = out.bandWithTray ? {
  containerWidthPx: +sc.width.toFixed(1),
  bandTopCqw: +(out.bandWithTray.top / cq).toFixed(2),
  bandHeightCqw: +(out.bandWithTray.h / cq).toFixed(2),
  reachYCqw: +(reachY / cq).toFixed(2),
} : null;

if (tray) { tray.classList.remove('has-items'); if (clone) clone.remove(); }

out.VERDICT = {
  /* A - the instrument has to be able to see instability at all */
  freshScratchesShowIt: out.floor.fresh.nonzero > 0,
  andItIsAtTheFront: out.floor.fresh.indexesNonzero.length > 0 &&
                     Math.max.apply(null, out.floor.fresh.indexesNonzero) <= 3,
  warmIsClean: out.floor.warm.nonzero === 0,
  warmAgainIsClean: out.floor.warmAgain.nonzero === 0,
  /* B */
  theTrayIsHiddenUntilPopulated: !!out.trayCss && out.trayCss.trayDisplay === 'none',
  populatingItGivesTheContainerHeight: out.shift.aboveGrewBy > 0,
  /* the question the markup raises against itself */
  theThrowingRowDoesNotMove: out.shift.throwLineMovedBy === 0,
  theBandIsStillWorthCutting: !!out.bandWithTray &&
                              out.bandWithTray.fractionOfScreen < 0.5,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
