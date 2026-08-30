/* P881 - _motion routes by owner (FX brief step 5, the motion half).
 *
 * Three claims, each with the control that could refute it:
 *   1. a settled match die gets NO DOM animation - so translate is left to
 *      _slaveHost and the hit box stays on the die. Control: the same call on
 *      an element D3X does not own still animates, so the DOM path is intact.
 *   2. the MESH moves instead, and returns to exactly where it started.
 *      Control: the same sampling before the effect is flat.
 *   3. an instrument cannot fade a die out of existence. Control: read the
 *      keyframe back and check the clamp, rather than trusting the source.
 *
 * NUDGE.ms is raised for the run. The effect is 260ms and this harness renders
 * the 3D layer at ~1fps, so at shipped timings the nudge would begin and end
 * between two frames and every sample would be a baseline - a flat series that
 * would read as "the mesh never moved". Restored at the end.
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

const sample = async (ms) => {
  const xs = [], t0 = Date.now();
  while (Date.now() - t0 < ms) { xs.push(die.obj.position.x); await FXH.sleep(150); }
  return xs;
};
const spread = xs => Math.max(...xs) - Math.min(...xs);

const KEYS = [{o:0},{o:.25,dx:-7,e:'ease-in'},{o:.5,dx:7},{o:.75,dx:-3},{o:1,dx:0,t:240}];
/* P882: rt is driven now, so the face-holding claim is tested where it can
   actually fail - a keyframe set that DOES twist. STRIKE's keys carry no rt,
   so the quaternion check above stays a control on the no-rt path. */
const TWIST = [{o:0,rt:0},{o:.5,rt:-2},{o:1,rt:0,t:240}];

/* ══ baseline: the mesh is still ═════════════════════════════════════ */
const before = await sample(2000);
out.before = {n: before.length, spread: +spread(before).toFixed(5)};

/* ══ 1 + 2. the owned path ═══════════════════════════════════════════ */
const wasMs = D3X.NUDGE.ms;
D3X.NUDGE.ms = 9000;
const q0 = {x: die.obj.quaternion.x, y: die.obj.quaternion.y,
            z: die.obj.quaternion.z, w: die.obj.quaternion.w};
const chipAnimBefore = die.chip.getAnimations().length;

FKFX._motion(die.chip, KEYS);

out.owned = {
  nudgeArmed: !!die.nudge,
  nudgeAmp: die.nudge ? +die.nudge.amp.toFixed(4) : null,
  chipAnimationsAdded: die.chip.getAnimations().length - chipAnimBefore,
};
const during = await sample(3000);
out.during = {n: during.length, spread: +spread(during).toFixed(5)};
out.quaternionHeld = ['x','y','z','w'].every(k =>
  Math.abs(die.obj.quaternion[k] - q0[k]) < 1e-6);

/* it must end where it began - a settled die's position is what the hit box
   and the shadow are read from, so a leftover offset is worse than no effect */
const cleared = await FXH.until(() => !die.nudge, 15000);
out.nudgeCleared = cleared != null;
const after = await sample(2000);
out.after = {n: after.length, spread: +spread(after).toFixed(5)};
out.returnedHome = before.length && after.length &&
  Math.abs(after[after.length-1] - before[before.length-1]) < 1e-4;
D3X.NUDGE.ms = wasMs;

/* ══ 3. the DOM path is intact, and the clamp is on it ═══════════════ */
const spare = document.createElement('div');
spare.style.cssText = 'position:absolute;left:0;top:0;width:10px;height:10px';
document.body.appendChild(spare);
FKFX._motion(spare, [{o:0,op:1},{o:.5,op:0},{o:1,op:1,t:300}]);
const anims = spare.getAnimations();
const kf = anims.length ? anims[0].effect.getKeyframes() : [];
out.domPath = {
  animated: anims.length > 0,
  opacities: kf.map(k => +Number(k.opacity).toFixed(3)),
  hasTranslate: kf.some(k => k.translate && k.translate !== 'none'),
};
spare.remove();

/* ══ 4. THE ROUTE THIS PATCH DOES NOT CONTROL ════════════════════════
   Everything above drives _byChip with D3X's own d.chip. The live call site
   (24476) hands it the GAME's d.el instead. If those are different nodes the
   lookup never matches on the real path and none of the above is reachable,
   so the identity is asserted rather than assumed. */
const pool = ((typeof G !== 'undefined' && G && G.pool) || []).filter(x => x.el);
const paired = pool.map(x => ({gameEl: x.el, viaByChip: D3X._byChip(x.el)}))
                   .filter(z => z.viaByChip);
out.liveRoute = {
  poolWithElements: pool.length,
  resolvedByChip: paired.length,
  sameNodeAsChip: paired.length > 0 &&
                  paired.every(z => z.viaByChip.chip === z.gameEl),
};

/* ══ 5. THE TWIST KEEPS THE FACE ═════════════════════════════════════
   A yaw about world up is the kick's own axis (P821): the die turns and the
   scoring face stays up. So the test is not "the quaternion never changes" -
   it is "the quaternion changes AND the up-facing normal does not". */
D3X.NUDGE.ms = 9000;
/* "the face stays up" is not "local Y is unmoved" - a yaw about world up
   rotates every local axis in world space. The invariant is that whichever
   local axis is pointing UP keeps pointing up by exactly as much, which is
   what P821 means by the scoring face staying up. Measured as the best
   y-component over the six face normals. */
const AX = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
const upness = q => Math.max.apply(null, AX.map(a =>
  new THREE.Vector3(a[0],a[1],a[2]).applyQuaternion(q).y));
const upBefore = upness(die.obj.quaternion);
FKFX._motion(die.chip, TWIST);
out.twist = {armed: !!(die.nudge && die.nudge.rt), rtRad: die.nudge ? +die.nudge.rt.toFixed(5) : null};
await FXH.sleep(1200);
const qMid = die.obj.quaternion.clone();
out.twist.quaternionMoved = ['x','y','z','w'].some(k => Math.abs(qMid[k] - q0[k]) > 1e-6);
out.twist.upnessBefore = +upBefore.toFixed(5);
out.twist.upnessDuring = +upness(qMid).toFixed(5);
out.twist.wasRestingFlat = upBefore > 0.99;
out.twist.upAxisHeld = Math.abs(upness(qMid) - upBefore) < 1e-3;
await FXH.until(() => !die.nudge, 15000);
D3X.NUDGE.ms = wasMs;

out.VERDICT = {
  meshWasStillBefore:        out.before.n > 3 && out.before.spread < 1e-4,
  ownedDieGetsNoDomAnimation: out.owned.chipAnimationsAdded === 0,
  /* the sign is meaningful and kept: mx takes the largest-magnitude dx with
     its sign, so STRIKE's leading -7 makes the shake start left the way the
     instrument wrote it. Magnitude is what has to be non-zero. */
  ownedDieGetsANudge:        out.owned.nudgeArmed === true &&
                             Math.abs(out.owned.nudgeAmp) > 0,
  theMeshActuallyMoved:      out.during.n > 3 && out.during.spread > 1e-3,
  /* control: keys with no rt must not rotate anything */
  noRtMeansNoRotation:       out.quaternionHeld === true,
  /* and with rt, it turns without changing the number */
  twistIsArmed:              out.twist.armed === true && Math.abs(out.twist.rtRad) > 0,
  twistActuallyRotates:      out.twist.quaternionMoved === true,
  /* gated on the die actually lying flat first: on a cocked die the yaw
     would not preserve the face and the check would be measuring nothing. */
  dieWasRestingFlat:         out.twist.wasRestingFlat === true,
  twistKeepsTheFaceUp:       out.twist.upAxisHeld === true,
  theNudgeExpires:           out.nudgeCleared === true,
  itEndsWhereItBegan:        out.returnedHome === true,
  meshIsStillAgainAfter:     out.after.n > 3 && out.after.spread < 1e-4,
  /* controls: the DOM path is untouched for anything D3X does not own */
  unownedElementStillAnimates: out.domPath.animated === true &&
                               out.domPath.hasTranslate === true,
  opacityIsClamped:            out.domPath.opacities.length > 0 &&
                               out.domPath.opacities.every(o => o >= 0.05),
  clampDidNotFlattenIt:        out.domPath.opacities.some(o => o < 1),
  /* the route the instruments actually take */
  liveCallSiteElementResolves: out.liveRoute.resolvedByChip > 0 &&
                               out.liveRoute.sameNodeAsChip === true,
  mostOfThePoolResolves:       out.liveRoute.poolWithElements > 0 &&
                               out.liveRoute.resolvedByChip >=
                               out.liveRoute.poolWithElements,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
