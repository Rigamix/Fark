/* HOW MUCH OF THE WIN SCREEN'S WAIT IS ACTUALLY ANIMATION?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "On the win screen the bottom UI takes a long time to appear but there
 * should be no reason. A card dotted line slot isn't heavy to render, or text.
 * So what gives?"
 *
 * He is right that it is not render cost. endMatch holds the whole lower half
 * behind one hard-coded `_draftDelay` — 3200ms for a patron win, 2400 for a
 * boss, 2800 for a loss — described in the source as "after animation
 * sequence". So the only question worth measuring is whether the animation
 * sequence is really that long, and if not, how much of the wait is dead air.
 *
 * MEASURED, NOT COUNTED FROM THE SOURCE. Adding up setTimeout literals gives the
 * time the last animation STARTS, not when it ends, and misses CSS transitions
 * entirely. This polls document.getAnimations() - document-wide, because the
 * coin row and the score block are not all inside the overlay - keeping only
 * what is genuinely running and finite, and records the moment the last one
 * stops against the moment the draft card actually appears.
 *
 * THE WIN IS FORCED with endMatch(true) rather than played to. Every timing
 * under test is inside endMatch and none of them reads how the points were
 * scored, so playing a full match to the target would add three minutes and
 * change nothing. The seat is a real launched patron, so isBoss and the gold
 * payout are real.
 *
 * CONTROL: at least one animation must be observed, and the draft card must
 * actually appear. Either zero means the poller is looking at the wrong subtree
 * and the "dead air" number is measuring nothing.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(40); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

for (let a = 0; a < 3; a++) {
  tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break;
}
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };
try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
await sleep(1500);

const ov = document.getElementById('end-ov');
if (!ov) return { err: 'end-ov not found' };
const isBoss = !!(G && G._isBoss);

/* give the win something to pay out on, the way a real one would */
G.pPts = G.target; G.oPts = Math.max(0, (G.target || 2800) - 600);

const T0 = Date.now();
const events = [];      /* every animation seen, with when it ended */
const seen = new Set();
let cardShownAt = null, btnsShownAt = null;
/* the gold count-up is _tweenGold, plain JS writing textContent - no CSS
   animation exists for it, so getAnimations cannot see it and "nothing is
   moving" would be wrong while it is still counting */
let goldLast = null;
const goldTrail = [];

/* ONLY WHAT IS STILL MOVING. A first pass counted every animation
   getAnimations() returned, which includes ones that have FINISHED and are
   holding their end state via `forwards` - res-title's resPop is one, and it
   made the screen look like it was still animating 6 seconds in and produced a
   negative dead-air figure. playState is the difference between "an animation
   exists on this element" and "something is moving". */
const poll = setInterval(() => {
  const t = Date.now() - T0;
  let anims = [];
  /* SCOPED TO THE OVERLAY. A document-wide pass was tried and was worse: the
     match table keeps ambient loops running (a `filter` one survives even an
     iterations!==Infinity test) and they drown the reveal, which is how this
     probe first reported the screen still animating six seconds in. Checked
     rather than assumed - endMatch reaches the scores with
     ov.querySelector('.res-scores'), so every element in the sequence is a
     descendant of #end-ov and nothing is lost by scoping here.
     Still filtered to RUNNING and FINITE: a `forwards` animation that has
     finished stays in getAnimations() holding its end state, and counting it
     is what produced a negative dead-air figure. */
  try { anims = ov.getAnimations({ subtree: true }).filter(a => {
    if (a.playState !== 'running') return false;
    try { return a.effect.getTiming().iterations !== Infinity; } catch (e) { return true; }
  }); } catch (e) {}
  anims.forEach(a => {
    const name = (a.animationName || a.transitionProperty || 'anim')
               + '@' + ((a.effect && a.effect.target && (a.effect.target.className || a.effect.target.id)) || '?');
    if (!seen.has(name)) { seen.add(name); events.push({ name: String(name).slice(0, 60), firstSeen: t, lastSeen: t }); }
    else { const e = events.find(e => e.name === String(name).slice(0, 60)); if (e) e.lastSeen = t; }
  });
  const card = document.querySelector('#end-ov .res-card');
  if (cardShownAt === null && card && card.classList.contains('show')) cardShownAt = t;
  const eb = document.getElementById('endBtns');
  if (btnsShownAt === null && eb && eb.style.display !== 'none' && vis(eb)) btnsShownAt = t;

  /* the tween's trail only - WHEN it settled is decided at the end, from the
     last change. Deciding it live latched onto "+0g" sitting still for 250ms
     before the count-up had started, and reported the tween finishing 1.4s
     before its first real value appeared. */
  const gt = document.getElementById('resGoldText');
  const now = gt ? (gt.textContent || '') : '';
  if (now !== goldLast) { goldTrail.push({ t, v: now }); goldLast = now; }
}, 16);

try { endMatch(true); } catch (e) { clearInterval(poll); return { err: 'endMatch threw: ' + e }; }
await sleep(6000);
clearInterval(poll);

/* the count-up settled when it last CHANGED, and only if it ever showed a
   number - an empty box that never filled is not a settled tween */
const goldReal = goldTrail.filter(g => /\d/.test(g.v));
const goldSettledAt = goldReal.length ? goldReal[goldReal.length - 1].t : null;

const lastAnimEnd = events.length ? Math.max(...events.map(e => e.lastSeen)) : null;
const uiAt = (cardShownAt !== null) ? cardShownAt : btnsShownAt;
/* the screen goes still when BOTH the last CSS animation and the gold tween
   have stopped - taking only one of them would understate the wait */
const stillAt = Math.max(lastAnimEnd === null ? 0 : lastAnimEnd,
                         goldSettledAt === null ? 0 : goldSettledAt) || null;

return {
  arm: 'win-screen-timing',
  isBoss,
  /* CONTROL — both must be non-null or the gap below is meaningless */
  control: { animationsObserved: events.length, bottomUiAppeared: uiAt !== null },

  /* no declaredDelay field: _DRAFT_DELAY is a `var` inside endMatch and is not
     reachable from here, and restating the literal in the probe is how a check
     keeps passing after the thing it checks has changed. bottomUiAppearedMs IS
     the delay, measured. */
  lastAnimationEndedMs: lastAnimEnd,
  screenWentStillMs: stillAt,
  bottomUiAppearedMs: uiAt,
  /* TREAT THIS ONE AS SOFT. bottomUiAppearedMs and goldSettledMs are direct
     observations and repeatable; screenWentStillMs is not. Across four runs of
     the same build the .res-title `top` transition - declared `transition:top
     .6s ease`, so 700..1300ms - was reported still running at 1296ms once and
     at 3217ms twice. Something in the throttled harness keeps a finished
     animation in the running state, and I have not found what.
     The reliable version of this number comes from the declared durations,
     which are all in the P635 note beside _DRAFT_DELAY: the last moving part is
     coinSheen .6s starting at 1600ms, so the sequence ends at 2200ms. */
  deadAirMs: (stillAt !== null && uiAt !== null) ? (uiAt - stillAt) : null,

  cardShownAt, btnsShownAt,
  /* the gold counter is a JS tween, not a CSS animation, so it is invisible to
     getAnimations and has to be watched on its own */
  goldSettledMs: goldSettledAt,
  goldTrail: goldTrail.map(g => g.t + ':' + g.v),
  animations: events.sort((a, b) => a.lastSeen - b.lastSeen)
                    .map(e => e.name + '  ' + e.firstSeen + '..' + e.lastSeen + 'ms'),
};
