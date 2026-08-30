/* P885 - the owned motion path plays the AUTHORED keyframes.
 *
 * REWRITTEN. The previous version had four verdicts that could not fail. The
 * settled branch re-bases position, scale and quaternion from d.phys at the
 * top of EVERY frame, so "the mesh was still before", "still again after" and
 * "it ends where it began" were all testing the re-basing rather than the
 * effect - true whenever d.nudge is null, whatever the nudge did. And "the
 * twist keeps the face up" was arithmetically forced: upness is the max
 * y-component over the six face normals, and ANY rotation about world Y
 * preserves every y-component exactly, so it only ever tested that the axis
 * constant is (0,1,0). That IS a real guard against P821's local-frame bug, so
 * it is kept below under a name that says what it actually checks.
 *
 * SAMPLING. D3X.frame() is callable, so time is not waited out: the nudge's t0
 * is BACKDATED to put the effect at a chosen phase and one real frame is
 * driven. Every sample below is therefore deterministic and immune to the
 * ~1fps headless render - which is also the only way to sample a 240ms effect
 * here at all.
 *
 * The yaw is recovered exactly rather than estimated. The frame premultiplies
 * the settled pose by a rotation about world up, so off = obj.q * phys.q^-1 is
 * that rotation and 2*atan2(off.y, off.w) is its SIGNED angle. An unsigned
 * angleTo() would read a clean 360 turn as up-then-down and could not tell it
 * from the whirl that is the thing under test.
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

const atPhase = (t) => {
  if (!die.nudge) return false;
  die.nudge.t0 = performance.now() - t * die.nudge.ms;
  D3X.frame();
  return true;
};
const yawDeg = () => {
  const off = die.obj.quaternion.clone().multiply(die.phys.q.clone().invert());
  return 2 * Math.atan2(off.y, off.w) * 180 / Math.PI;
};
const sweep = (read, n) => {
  const xs = [];
  for (let i = 0; i <= n; i++) { atPhase(i / n * 0.985); xs.push(read()); }
  return xs;
};
const arm = (keys) => { die.nudge = null; FKFX._motion(die.chip, keys); return die.nudge; };
const spread = a => Math.max(...a) - Math.min(...a);

/* the shipped families' literal keyframes */
const KEYS = {
  SET:       [{o:0,sc:1},{o:.18,sc:.95,rt:-2,e:'ease-in'},{o:.35,sc:.93,rt:2},
              {o:.6,sc:.93,rt:-1},{o:1,sc:1,rt:0,e:'cubic-bezier(.3,1.4,.4,1)'}],
  ARM:       [{o:0,sc:1},{o:.23,sc:1.08,e:'cubic-bezier(.3,1.4,.4,1)'},{o:.5,sc:1},
              {o:.73,sc:1.05},{o:1,sc:1,t:600}],
  TRANSFORM: [{o:0},{o:.5,rt:180,sc:1.08},{o:1,rt:360,sc:1,t:620,e:'cubic-bezier(.3,1.4,.4,1)'}],
  STRIKE:    [{o:0},{o:.25,dx:-7,e:'ease-in'},{o:.5,dx:7},{o:.75,dx:-3},{o:1,dx:0,t:240}],
  LANDED:    [{o:0,sc:1},{o:.5,sc:1.06},{o:1,sc:1,t:200}],
  DYONLY:    [{o:0},{o:.5,dy:9},{o:1,dy:0,t:240}],
};

/* ══ A. THE AUTHORED DURATION SURVIVES ═══════════════════════════════
   Every owned effect used to run at one global 260ms. */
out.durations = {};
for (const k of Object.keys(KEYS)) {
  const n = arm(KEYS[k]);
  out.durations[k] = n ? n.ms : null;
}

/* ══ B. TRANSFORM IS ONE TURN, NOT A WHIRL ═══════════════════════════ */
arm(KEYS.TRANSFORM);
const yaws = sweep(yawDeg, 16);
let dips = 0, signFlips = 0;
for (let i = 1; i < yaws.length; i++) if (yaws[i] < yaws[i - 1] - 2) dips++;
for (let i = 1; i < yaws.length; i++)
  if (Math.sign(yaws[i]) && Math.sign(yaws[i - 1]) &&
      Math.sign(yaws[i]) !== Math.sign(yaws[i - 1])) signFlips++;
out.transform = {yaws: yaws.map(v => +v.toFixed(1)),
                 peak: +Math.max(...yaws.map(Math.abs)).toFixed(1),
                 backwardSteps: dips, signFlips};

/* ══ C. ARM KEEPS ITS TWO BUMPS ══════════════════════════════════════ */
arm(KEYS.ARM);
const arms = sweep(() => die.obj.scale.x, 24);
let peaks = 0;
for (let i = 1; i < arms.length - 1; i++)
  if (arms[i] > arms[i - 1] && arms[i] >= arms[i + 1] && arms[i] > 1.015) peaks++;
out.armShape = {series: arms.map(v => +v.toFixed(4)),
                localMaxima: peaks, max: +Math.max(...arms).toFixed(4)};

/* ══ D. SET REACHES ITS AUTHORED DEPTH ═══════════════════════════════
   The old envelope halved it: an authored .93 arrived as about .96. */
arm(KEYS.SET);
const sets = sweep(() => die.obj.scale.x, 20);
out.setDepth = {min: +Math.min(...sets).toFixed(4), series: sets.map(v => +v.toFixed(3))};

/* ══ E. THE PULSE NO LONGER ERASES THE BEAT ══════════════════════════ */
const wasPulse = die.pulseOn;
die.pulseOn = true;  arm(KEYS.LANDED); atPhase(0.5);
const withPulse = die.obj.scale.x;
die.pulseOn = false; arm(KEYS.LANDED); atPhase(0.5);
const withoutPulse = die.obj.scale.x;
die.pulseOn = true;  die.nudge = null; D3X.frame();
const pulseAlone = die.obj.scale.x;
die.pulseOn = wasPulse; die.nudge = null;
out.pulseCompose = {withPulse: +withPulse.toFixed(4),
                    withoutPulse: +withoutPulse.toFixed(4),
                    pulseAlone: +pulseAlone.toFixed(4), pulseAmp: D3X.PULSE.amp};

/* ══ F. dy IS ITS OWN AXIS ═══════════════════════════════════════════ */
arm(KEYS.DYONLY); const ys = sweep(() => die.obj.position.y, 10);
arm(KEYS.DYONLY); const xs = sweep(() => die.obj.position.x, 10);
out.dyAxis = {ySpread: +spread(ys).toFixed(5), xSpread: +spread(xs).toFixed(5)};

/* ══ G. STRIKE STILL SHAKES; the face is still held; easing is real ══ */
arm(KEYS.STRIKE);
const shake = sweep(() => die.obj.position.x, 16);
out.strike = {spread: +spread(shake).toFixed(5)};

const AX = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
const upness = q => Math.max.apply(null, AX.map(a =>
  new THREE.Vector3(a[0],a[1],a[2]).applyQuaternion(q).y));
die.nudge = null; D3X.frame();
const upRest = upness(die.obj.quaternion);
arm(KEYS.TRANSFORM); atPhase(0.5);
out.faceAxis = {atRest: +upRest.toFixed(5), midTurn: +upness(die.obj.quaternion).toFixed(5)};
die.nudge = null;

out.easing = {
  overshoots: D3X._ease('cubic-bezier(.3,1.4,.4,1)', 0.55),
  linearIsIdentity: Math.abs(D3X._ease('linear', 0.5) - 0.5) < 1e-6,
  easeOutIsAhead: D3X._ease('ease-out', 0.5) > 0.5,
  unknownFallsBack: D3X._ease('nonsense-easing', 0.5) > 0,
};

/* ══ H. the chip is left alone, and the DOM path is intact ═══════════ */
const chipKids = die.chip.children.length, chipAnims = die.chip.getAnimations().length;
arm(KEYS.SET);
out.chipUntouched = {kidsAdded: die.chip.children.length - chipKids,
                     animationsAdded: die.chip.getAnimations().length - chipAnims};
die.nudge = null;

const spare = document.createElement('div');
spare.style.cssText = 'position:absolute;left:0;top:0;width:10px;height:10px';
document.body.appendChild(spare);
FKFX._motion(spare, [{o:0,op:1},{o:.5,op:0},{o:1,op:1,t:300}]);
const anims = spare.getAnimations();
const kf = anims.length ? anims[0].effect.getKeyframes() : [];
out.domPath = {animated: anims.length > 0,
               opacities: kf.map(k => +Number(k.opacity).toFixed(3)),
               hasTranslate: kf.some(k => k.translate && k.translate !== 'none')};
spare.remove();

const pool = ((typeof G !== 'undefined' && G && G.pool) || []).filter(x => x.el);
out.liveRoute = {poolWithElements: pool.length,
                 resolved: pool.map(x => D3X._byChip(x.el)).filter(Boolean).length};

out.VERDICT = {
  /* A - authored duration, which used to be one global number */
  transformRunsFor620: out.durations.TRANSFORM === 620,
  armRunsFor600:       out.durations.ARM === 600,
  strikeRunsFor240:    out.durations.STRIKE === 240,
  landedRunsFor200:    out.durations.LANDED === 200,
  setFallsBackTo500:   out.durations.SET === 500,
  /* B - the regression P882 shipped, and the shape that replaces it */
  transformTurnsOneWay:   out.transform.backwardSteps === 0,
  transformNeverReverses: out.transform.signFlips === 0,
  transformReaches360:    Math.abs(out.transform.peak - 360) < 20,
  /* C/D - shape and depth survive the trip */
  armKeepsBothBumps:  out.armShape.localMaxima >= 2,
  armReachesItsPeak:  Math.abs(out.armShape.max - 1.08) < 0.02,
  setReachesItsDepth: Math.abs(out.setDepth.min - 0.93) < 0.02,
  /* E - the beat composes with the pulse instead of losing to it */
  pulseDoesNotEraseTheBeat: out.pulseCompose.withPulse >
                            out.pulseCompose.pulseAlone + 0.005,
  beatAloneStillSwells:     out.pulseCompose.withoutPulse > 1.005,
  pulseAloneIsJustThePulse: out.pulseCompose.pulseAlone <= 1 + D3X.PULSE.amp + 1e-6,
  /* F - the axis trap */
  dyMovesY:       out.dyAxis.ySpread > 1e-4,
  dyDoesNotMoveX: out.dyAxis.xSpread < 1e-6,
  /* G - nothing regressed; the easing is honoured; the axis is still world-up.
     NOTE this last one is near-tautological by construction - any rotation
     about world Y preserves every y-component - so it is a guard that the AXIS
     CONSTANT has not drifted back to P821's local frame, and nothing more. */
  strikeStillShakes:       out.strike.spread > 1e-3,
  yawAxisIsStillWorldUp:   Math.abs(out.faceAxis.midTurn - out.faceAxis.atRest) < 1e-3,
  bezierOvershootsPastOne: out.easing.overshoots > 1,
  linearIsIdentity:        out.easing.linearIsIdentity === true,
  easeOutLeadsLinear:      out.easing.easeOutIsAhead === true,
  unknownEasingFallsBack:  out.easing.unknownFallsBack === true,
  /* H - unchanged guarantees */
  ownedDieGetsNoDomAnimation: out.chipUntouched.kidsAdded === 0 &&
                              out.chipUntouched.animationsAdded === 0,
  unownedElementStillAnimates: out.domPath.animated === true &&
                               out.domPath.hasTranslate === true,
  opacityIsClamped: out.domPath.opacities.length > 0 &&
                    out.domPath.opacities.every(o => o >= 0.05),
  clampDidNotFlattenIt: out.domPath.opacities.some(o => o < 1),
  liveCallSiteResolves: out.liveRoute.poolWithElements > 0 &&
                        out.liveRoute.resolved === out.liveRoute.poolWithElements,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
