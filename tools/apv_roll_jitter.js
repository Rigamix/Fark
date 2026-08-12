/* DOES THE ROLL BUTTON MOVE SIDEWAYS WHEN THE PLAYER BANKS?
 * SUITE: exclude   (a measurement)
 *
 * Denis, twice: "when I bank and pass my turn to the npc, the bank button
 * slides to the left side for no reason before settling back" and then, after
 * two attempts at it, "Roll button still jitters to the side".
 *
 * P599 and P601 both went after transform-origin. Neither fixed it, and the
 * handover from that session says in as many words: do not guess a third
 * mechanism, get a repro. This is the repro.
 *
 * WHY THE ~7fps THROTTLE DOES NOT MATTER HERE, which is the thing that killed
 * the two previous attempts to sample this. They were trying to catch the SHAPE
 * of a .28s transition, and at 7fps there is nothing to catch. The suspect here
 * is different: @keyframes rollBounce declares translateX(-50%) at BOTH 0% and
 * 100%, so if it is the cause the offset is CONSTANT for the whole 150ms window
 * rather than a curve through it. One sample anywhere inside is enough, and a
 * throttled clock still lands one.
 *
 * WHAT IS MEASURED is the button's own left edge in screen pixels, sampled
 * continuously across a real player bank driven through the real BANK button.
 * Not the computed transform: a matrix can be read wrongly, an edge that moved
 * 130px cannot.
 *
 * CONTROL, and it is the whole reason this is trustworthy: the same sampler runs
 * for two seconds BEFORE the bank. If that window also shows movement the
 * sampler is measuring layout noise and the after-window proves nothing; if it
 * shows a flat line and the bank window shows a jump, the jump is the bank's.
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
await sleep(1800);

const roll = document.getElementById('btnRoll');
const bank = document.getElementById('btnBank');
if (!roll || !bank) return { err: 'buttons not found' };
const on = el => el && !el.classList.contains('disabled') && vis(el);

/* the sampler: rAF plus a timer, so neither a throttled rAF nor a throttled
   timer can be the single thing that misses the window */
let samples = [], sampling = false;
const take = tag => { if (!sampling) return;
  samples.push({ t: Date.now(), tag, left: +roll.getBoundingClientRect().left.toFixed(1),
                 anim: roll.style.animation || '', tf: getComputedStyle(roll).transform }); };
const pump = () => { if (!sampling) return; take('raf'); requestAnimationFrame(pump); };
const timer = setInterval(() => take('tick'), 8);

/* ── CONTROL WINDOW: two seconds of nothing happening ── */
sampling = true; requestAnimationFrame(pump);
let phase = 'control';
const mark = () => samples.length;
const c0 = mark();
await sleep(2000);
const c1 = mark();

/* ── drive one real player turn and bank it through the real button ── */
let banked = false;
const DEADLINE = Date.now() + 60000;
while (Date.now() < DEADLINE && !banked) {
  await sleep(200);
  if (on(bank)) { tap(bank); banked = true; await sleep(1500); break; }
  if (G && G.phase === 'choosing' && G.pool) {
    let took = false;
    for (const d of G.pool.filter(x => !x.committed && !x.sel)) {
      try { toggleDie(d); } catch(e) { continue; }
      await sleep(60);
      if (on(bank) || on(document.getElementById('btnRoll'))) { took = true; break; }
      try { toggleDie(d); } catch(e) {}
    }
    if (took) continue;
  }
  if (on(roll)) tap(roll);
}
const b1 = mark();
sampling = false; clearInterval(timer);

const ctrl  = samples.slice(c0, c1);
const after = samples.slice(c1, b1);
const spread = arr => { if (!arr.length) return null;
  const xs = arr.map(s => s.left); return { min: Math.min(...xs), max: Math.max(...xs),
    swing: +(Math.max(...xs) - Math.min(...xs)).toFixed(1) }; };

/* every distinct transform the button wore while the bank resolved */
const seenTf = [...new Set(after.map(s => s.tf))];
const bounceSeen = after.filter(s => /rollBounce/.test(s.anim));

return {
  arm: 'repro',
  banked,
  /* CONTROL: a still button must not move. If controlSwing is not ~0 the
     sampler is reading layout noise and nothing below means anything. */
  control: { samples: ctrl.length, controlSwing: spread(ctrl) ? spread(ctrl).swing : null,
             sampledAfterBank: after.length },
  rollWidth: +roll.getBoundingClientRect().width.toFixed(1),
  controlSpread: spread(ctrl),
  bankSpread: spread(after),
  /* the number Denis is describing, in pixels of sideways travel */
  sidewaysTravelPx: spread(after) ? spread(after).swing : null,
  /* and whether the button was wearing rollBounce when it happened */
  bounceSamples: bounceSeen.length,
  bounceTransforms: [...new Set(bounceSeen.map(s => s.tf))],
  transformsDuringBank: seenTf,
};
