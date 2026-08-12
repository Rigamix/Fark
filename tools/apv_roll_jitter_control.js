/* THE POSITIVE CONTROL apv_roll_jitter WAS MISSING.
 * SUITE: exclude   (a measurement)
 *
 * That probe drove a real bank, took 151 samples across it, and reported the
 * button's left edge never moved by a single pixel — with the rollBounce
 * animation never observed at all. A zero is where checking stops, so this asks
 * the question the zero cannot answer: CAN the sampler see this animation?
 *
 * Three arms, run in one page:
 *   FORCED    call restoreRollButton() directly. This is the function the bank
 *             path calls, so if the keyframe moves the button, it moves here.
 *   RAW       set the same animation by hand on a button with no .disabled
 *             class. Distinguishes "restoreRollButton does not do what it looks
 *             like it does" from "the keyframe does not move anything".
 *   DISABLED  the same raw animation WITH .disabled on. #btnRoll.disabled
 *             declares `transform:none !important`, and an !important author
 *             declaration outranks an animation — so this arm predicts a
 *             suppressed animation, and if it is right, the state of that class
 *             at bank time decides whether Denis ever sees the jump.
 *
 * Sampling is the same as the failed probe's on purpose: if the instrument is
 * the problem, all three arms come back zero and that is the finding.
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
if (!roll) return { err: 'btnRoll not found' };

/* watch for 500ms and report how far the left edge travelled */
async function watch(label, start) {
  const base = roll.getBoundingClientRect().left;
  const seen = [];
  let live = true;
  const grab = () => { if (!live) return;
    seen.push({ left: roll.getBoundingClientRect().left, tf: getComputedStyle(roll).transform }); };
  const iv = setInterval(grab, 8);
  const pump = () => { if (!live) return; grab(); requestAnimationFrame(pump); };
  requestAnimationFrame(pump);
  start();
  await sleep(500);
  live = false; clearInterval(iv);
  const xs = seen.map(s => s.left);
  return { arm: label, samples: seen.length, base: +base.toFixed(1),
           minLeft: +Math.min(...xs).toFixed(1), maxLeft: +Math.max(...xs).toFixed(1),
           travelPx: +(Math.max(...xs) - Math.min(...xs)).toFixed(1),
           transforms: [...new Set(seen.map(s => s.tf))].slice(0, 4) };
}

const out = { arm: 'positive-control', rollWidth: +roll.getBoundingClientRect().width.toFixed(1) };

/* FORCED — the exact function the bank path calls */
roll.style.animation = '';
out.disabledBefore_forced = roll.classList.contains('disabled');
out.forced = await watch('forced', () => { try { restoreRollButton(); } catch(e) { out.forcedErr = String(e); } });
roll.style.animation = '';
await sleep(300);

/* RAW, enabled */
roll.classList.remove('disabled');
out.raw = await watch('raw-enabled', () => { roll.style.animation = 'rollBounce .15s ease-out'; });
roll.style.animation = '';
await sleep(300);

/* RAW, with .disabled — the !important suppression hypothesis */
roll.classList.add('disabled');
out.rawDisabled = await watch('raw-disabled', () => { roll.style.animation = 'rollBounce .15s ease-out'; });
roll.style.animation = ''; roll.classList.remove('disabled');

/* what the keyframe itself says, read from the stylesheet rather than assumed */
out.keyframeText = (() => {
  for (const ss of document.styleSheets) {
    try { for (const r of ss.cssRules) {
      if (r.type === CSSRule.KEYFRAMES_RULE && r.name === 'rollBounce')
        return [...r.cssRules].map(k => k.keyText + ' ' + k.style.transform).join(' | ');
    } } catch(e) {}
  } return null;
})();

/* CONTROL: at least one arm must move, or the sampler is blind and every
   zero in the sibling probe — and here — means nothing. */
out.control = { instrumentCanSeeMovement:
  [out.forced, out.raw, out.rawDisabled].some(a => a && a.travelPx > 1) };
return out;
