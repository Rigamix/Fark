/* NOTE 8a - the deadRoll seam fires while the dice are still in the air.
 *
 * Denis: "it rerolls dice even before they land so you don't even understand
 * what it's doing". That is a RACE, not a duration, and this measures it as one:
 * the question is not "how long is the effect" but "does the hook fire before or
 * after the throw it is judging has stopped".
 *
 * THE TWO TIMESTAMPS, both taken from the game's own notion of the world:
 *   tDeadRoll  when famFire('deadRoll', {actor:'p'}) is dispatched
 *   tSettled   the first moment _rowSettled('#playerDiceRow') returns true
 * _rowSettled is the file's own predicate - the same one _delayedDoBust waits on
 * - so this is not a second opinion about when dice have landed.
 *
 * A NEGATIVE GAP IS THE BUG: the hook fired that many ms before the dice
 * stopped. The file already records the sibling case, for the bust verdict that
 * fires immediately after this hook: "the word BUST hit the screen 1119ms after
 * the ROLL tap ... while the dice were still tumbling until 2037ms."
 *
 * HOW A DEAD ROLL IS PRODUCED, without waiting for a 2.3% farkle: numDice is set
 * to 2, where P(neither die is a 1 or a 5) = (4/6)^2 = 44%. Rolls are driven
 * until one lands dead, and the ATTEMPT COUNT is reported - "it did not happen"
 * in three tries would prove nothing.
 *
 * CONTROLS
 *   - a dead roll actually occurred (the hook dispatched at all). Without this,
 *     a probe that never triggered the branch reports a clean zero.
 *   - the row genuinely settles at some point, rather than _rowSettled being
 *     vacuously true from the start - which it IS whenever physics is off or the
 *     renderer failed, and would make every gap read as a comfortable positive.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(30); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
/* physics must actually be on, or _rowSettled short-circuits to true and every
   gap reads as fine. Reported as a control rather than assumed. */
notes._physics = { on: !!(window.D3X && D3X.PHYS && D3X.PHYS.on),
                   ready: !!(window.D3X && D3X.ready), fail: !!(window.D3X && D3X.fail) };

/* A TOKEN PER ATTEMPT, because the thing under test is a DELAY. Once the seam
   waits for the dice, attempt N's hook can land during attempt N+1 and be
   credited to it - which is exactly what happened on the first post-patch run:
   sawFlying false, peakFlying 0, and a nonsensical 7610ms from "roll" to
   "deadRoll". Same trial-contamination shape as the drill-cap arm earlier; a
   stale callback is only distinguishable from a real one if each attempt is
   labelled. */
let tDead = null, fired = false, token = 0, firedToken = -1;
const realFire = window.famFire;
window.famFire = function (hook, ev) {
  if (hook === 'deadRoll' && ev && ev.actor === 'p' && !fired) {
    fired = true; firedToken = token; tDead = performance.now();
  }
  return realFire.apply(this, arguments);
};

/* THE THROW MUST BE SEEN IN THE AIR BEFORE "SETTLED" MEANS ANYTHING.
   _rowSettled has four early `return true` escapes - no D3X, no physics, no row,
   and `n===0` when the DOM row holds no dice yet. My first version began polling
   as soon as G.pool was populated, which is BEFORE the dice elements exist, so it
   caught the n===0 escape and recorded "settled" 53ms after the tap. The gap then
   read +429ms and the probe cheerfully reported no bug at all.
   Counting flying dice the same way _rowSettled does, and refusing to accept a
   settle until at least one has been seen airborne, is what makes the timestamp
   mean what its name says. */
function flyingIn(sel) {
  try {
    if (!window.D3X || !D3X.dice) return 0;
    let f = 0;
    D3X.dice.forEach(d => { if (d.chip && d.chip.closest && d.chip.closest(sel) && d.roll) f++; });
    return f;
  } catch (e) { return 0; }
}

let attempts = 0, tRoll = null, tSettled = null, settledSeen = false, sawFlying = false, peakFlying = 0;
try {
  for (; attempts < 18 && !fired; attempts++) {
    /* DRAIN BEFORE RE-ARMING: the previous attempt's seam may still be waiting
       on its own settle poll. A generous quiet period plus the phase gate is
       what keeps attempt N's callback out of attempt N+1's numbers. */
    await until(() => G && (G.phase === 'idle' || G.phase === 'choosing'), 15000);
    await sleep(900);
    token++;
    G.numDice = 2; G.pool = []; G.kept = []; G.turnPts = 0;
    try { clearRow('playerDiceRow'); } catch (e) {}
    settledSeen = false; tSettled = null; tDead = null; fired = false; firedToken = -1;
    sawFlying = false; peakFlying = 0;
    tRoll = performance.now();
    tap(document.getElementById('btnRoll'));
    const t0 = performance.now();
    while (performance.now() - t0 < 9000) {
      const fly = flyingIn('#playerDiceRow');
      if (fly > peakFlying) peakFlying = fly;
      if (fly > 0) sawFlying = true;
      /* only once the throw has been observed in the air */
      if (sawFlying && !settledSeen) {
        let s = false; try { s = _rowSettled('#playerDiceRow'); } catch (e) {}
        if (s) { settledSeen = true; tSettled = performance.now(); }
      }
      if (fired && settledSeen) break;
      await sleep(20);
    }
    /* only a fire belonging to THIS attempt counts */
    if (fired && firedToken === token) break;
    fired = false; firedToken = -1; tDead = null;
  }
} finally { window.famFire = realFire; }
notes._throw = { sawFlying: sawFlying, peakFlyingDice: peakFlying };

notes._run = { attempts: attempts + 1, deadRollFired: fired && firedToken === token,
               msFromRollToDeadRoll: (tDead && tRoll) ? +(tDead - tRoll).toFixed(0) : null,
               msFromRollToSettled: (tSettled && tRoll) ? +(tSettled - tRoll).toFixed(0) : null };

/* CONTROL 1: the branch under test actually ran */
v.aDeadRollActuallyHappened = fired === true && firedToken === token;
/* CONTROL 2: settling is a real event here, not vacuously true from frame one.
   _rowSettled returns true immediately when physics is off or D3X failed, which
   would make every gap below look comfortable. */
v.theRowGenuinelySettles = settledSeen === true && sawFlying === true
                        && notes._run.msFromRollToSettled > 120;

const gap = (tDead != null && tSettled != null) ? (tDead - tSettled) : null;
notes._gapMs = gap == null ? null : +gap.toFixed(0);
notes._reading = gap == null ? 'not measured'
  : (gap < 0 ? 'the hook fired ' + Math.abs(gap).toFixed(0) + 'ms BEFORE the dice stopped'
             : 'the hook fired ' + gap.toFixed(0) + 'ms after the dice stopped');

/* THE FINDING. Positive means the seam waited for the throw it is judging. */
v.deadRollFiresAfterTheDiceLand = fired && settledSeen && gap != null && gap >= 0;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
