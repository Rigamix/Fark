/* Does the 3D layer leak GPU objects as a match goes on?
 *
 * THE REPORT SAYS "AS I PLAYED", AND THAT IS THE CLUE. Images went, then the
 * dice, while the game kept running. A fixed allocation cannot do that - a
 * canvas budget blown at 120MB is blown on the first frame, not after twenty
 * minutes. Something has to CLIMB. And the eviction order is the renderer's:
 * decoded images first, then textures and contexts, which is what a GPU
 * running out of room looks like from the outside.
 *
 * WHERE IT WOULD CLIMB. syncMatch drops and re-registers every match die
 * whenever the mount changes - `this.dice.forEach(self._drop)` then a fresh
 * _mkDie per chip. Three.js does not free GPU memory when a mesh leaves the
 * scene: geometries, materials and textures are released only by an explicit
 * .dispose(). If _drop does not dispose, every reroll, every deal and every
 * rival turn adds another set that nothing will ever collect.
 *
 * renderer.info.memory IS THE INSTRUMENT, and it is the right one because it
 * counts what the DRIVER holds, not what JS still references - a mesh can be
 * unreachable from the scene graph and its texture still resident.
 *
 * THE CONTROL IS THE SHAPE OF THE SERIES, not any single reading. A flat line
 * across rolls says no leak; a staircase says a leak and its slope says how
 * fast. One before-and-after pair could not tell either from noise, and a
 * single sample could not tell a leak from a large constant.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};

const mem = () => {
  const r = D3X.renderer;
  if (!r || !r.info) return null;
  return {geometries: r.info.memory.geometries, textures: r.info.memory.textures,
          programs: (r.info.programs || []).length,
          calls: r.info.render ? r.info.render.calls : null};
};
/* THE RENDERER IS NOT UP YET. D3X boots asynchronously - three.js, the loader,
   the model and cannon - so sampling here reported "no renderer" and said
   nothing about the code under test. Wait for it on STATE, the way everything
   else in this harness does. */
await FXH.until(() => !!(D3X.renderer && D3X.renderer.info), 40000);
out.instrument = {rendererPresent: !!D3X.renderer,
                  infoPresent: !!(D3X.renderer && D3X.renderer.info),
                  first: mem()};
if (!out.instrument.infoPresent)
  return Object.assign(out, {err: 'renderer never came up - cannot count GPU objects'});

/* what _drop actually does, read off the shipped source rather than assumed */
const dropSrc = D3X._drop ? D3X._drop.toString() : '';
out.dropDisposes = {
  hasDrop: !!D3X._drop,
  callsDispose: /\.dispose\s*\(/.test(dropSrc),
  mentionsMaterial: /material/.test(dropSrc),
  mentionsGeometry: /geometry/.test(dropSrc),
  mentionsTexture: /map|texture/i.test(dropSrc),
  source: dropSrc.slice(0, 400),
};

const rolling = () => D3X.dice.filter(d => d.match && d.roll).length;
const series = [];
const sample = (label) => series.push(Object.assign({label,
  dice: D3X.dice.length, sceneChildren: D3X.scene ? D3X.scene.children.length : null,
  domDice: document.querySelectorAll('#screen-match .die.d3on').length}, mem()));

const r0 = await FXH.rollAndSettle();
out.gotToTheDice = {ok: r0.ok, why: r0.why};
if (!r0.ok) return Object.assign(out, {err: 'never got to the dice: ' + r0.why});
sample('after roll 1');

/* REROLL REPEATEDLY THROUGH A REAL PATH. Grog's Flask re-throws in place,
   which is what syncMatch's drop-and-rebuild responds to, and it is reachable
   without card state. Ten of them: enough for a staircase to be a staircase
   rather than two points and a hope. */
const free0 = G.pool.filter(d => !d.committed && !d._frozen && d.el);
out.rerollsAttempted = 0;
for (let i = 0; i < 10; i++) {
  try {
    const free = G.pool.filter(d => !d.committed && !d._frozen && d.el);
    if (free.length < 2) break;
    free[0].val = 2; free[1].val = 3;
    try { reDrawDieFace(free[0]); reDrawDieFace(free[1]); } catch (e) {}
    await FXH.until(() => rolling() === 0, 15000);
    activateGrogsFlask();
    out.rerollsAttempted++;
    await FXH.until(() => rolling() > 0, 4000);
    await FXH.until(() => rolling() === 0, 20000);
    try { D3X.syncMatch(); } catch (e) {}
    sample('after reroll ' + (i + 1));
  } catch (e) { series.push({label: 'reroll ' + (i + 1) + ' threw', why: e.message}); break; }
}
out.series = series;

/* the slope, over the samples that have numbers */
const nums = series.filter(s => typeof s.geometries === 'number');
const first = nums[0] || {}, last = nums[nums.length - 1] || {};
out.slope = nums.length >= 3 ? {
  samples: nums.length,
  geometries: [first.geometries, last.geometries],
  textures: [first.textures, last.textures],
  programs: [first.programs, last.programs],
  sceneChildren: [first.sceneChildren, last.sceneChildren],
  diceTracked: [first.dice, last.dice],
  geometryGrowth: last.geometries - first.geometries,
  textureGrowth: last.textures - first.textures,
  /* monotonic climb is the signature; a flat line with jitter is not a leak */
  everyStepNonDecreasing: nums.every((s, i) => i === 0 || s.geometries >= nums[i - 1].geometries),
} : null;

out.VERDICT = {
  theProbeActuallyRerolled: out.rerollsAttempted >= 5,
  theSeriesHasEnoughPoints: !!out.slope && out.slope.samples >= 5,
  /* the finding, either way - a flat line here EXONERATES the 3D layer and
     sends the search somewhere else, which is worth as much as a leak */
  geometriesDoNotClimb: !!out.slope && out.slope.geometryGrowth <= 2,
  texturesDoNotClimb: !!out.slope && out.slope.textureGrowth <= 2,
  theDiceListStaysBounded: !!out.slope &&
    out.slope.diceTracked[1] <= out.slope.diceTracked[0] + 1,
  theSceneStaysBounded: !!out.slope &&
    out.slope.sceneChildren[1] <= out.slope.sceneChildren[0] + 2,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
