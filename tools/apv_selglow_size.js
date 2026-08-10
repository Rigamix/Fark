/* NOTE 1 - the selected-die glow is too large and a bit too strong on a phone.
 *
 * MEASURED IN THE UNITS OF THE COMPLAINT, not derived from the source. Denis
 * said "much too large and a bit too strong", which are two different numbers:
 *   SIZE     how far the halo reaches past the die's silhouette, as a fraction
 *            of the die's own width
 *   STRENGTH how much light it puts on the table - lit-pixel count and mean alpha
 *
 * The file already counts this way: _cfBlur's comment at 9380 reports "the
 * selection glow fell from 22,321 lit pixels to 2,414 ... while the stroke
 * fallback this gate exists to select paints 25,394", so lit-pixel count is the
 * established unit here rather than one invented for this probe.
 *
 * WHICH BRANCH IS REPORTED, and it decides whether a fix reaches Denis at all.
 * D3X._drawGlow has two paths: a ctx.filter blur (desktop, iOS Safari 18+) and a
 * stroked-rings fallback for devices without a working ctx.filter, chosen by
 * _cfBlur and cached in window.__cfBlur. The fallback paints MORE ink than the
 * path it replaces, and it only recently became reachable - so a phone is the
 * likeliest device to be on it, and tuning only the filter branch would change
 * nothing for the person reporting the bug. GLOW.soft drives both (the fallback
 * reads widest = Math.max(6, soft*2)), which is why the fix belongs in the dial.
 *
 * CONTROLS
 *   - a die is actually SELECTED and the canvas actually has ink. A glow probe
 *     on an unselected table measures zero and reads like a very small glow.
 *   - the die's own width is measured from the DOM, so the size figure is a
 *     ratio rather than a raw px count that means nothing without the die.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
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

/* roll for real, then select exactly ONE die so the ink on the canvas belongs to
   a single known silhouette */
tap(document.getElementById('btnRoll'));
await until(() => G && (G.pool || []).length > 0 && G.phase === 'choosing', 12000);
await sleep(1200);
const live = (G.pool || []).filter(d => !d.committed && d.el);
if (!live.length) return { skip: 'no live dice after the roll' };
const target = live[0];
tap(target.el);
/* WAIT FOR THE CANVAS, NOT FOR A CLOCK. _drawGlow's `skip` test includes
   this._rolling(), and it returns BEFORE _glowCv() creates #dgCanvas - so while
   the settle animation is still running there is no canvas to read at all.
   Measured: rolling is still true 400ms after the tap and false by 800ms. A
   fixed sleep(700) sat exactly on that boundary and passed twice then failed
   twice, which reads precisely like the patch under test having broken the
   glow. It had not. */
await until(() => !!document.getElementById('dgCanvas') && D3X._glowInk === true, 8000);
await sleep(300);

const box = target.el.getBoundingClientRect();
notes._die = { w: +box.width.toFixed(1), h: +box.height.toFixed(1),
               selected: target.el.classList.contains('selected'), sel: !!target.sel };
/* CONTROL: the tap actually selected it. An unselected table draws no glow and
   would read as a beautifully small one. */
v.aDieIsActuallySelected = !!target.el.classList.contains('selected');

const cv = document.getElementById('dgCanvas');
if (!cv) return { verdict: v, notes: Object.assign(notes, { _err: 'no #dgCanvas' }) };

/* BOTH BRANCHES, and this is the whole point of the probe rather than a bonus.
   Headless Chrome has a working ctx.filter, so an unmodified run measures the
   branch a DESKTOP takes. Denis is reporting a phone, and iOS Safari before 18
   has no working ctx.filter, so his device very likely takes the stroked-rings
   fallback - which the file's own count at 9380 puts at 25,394 lit pixels
   against the filter path's 22,321. Measuring only what this machine happens to
   render would tune the branch the reporter cannot see.
   D3X._cf is the cached decision (set from _cfBlur at 21454) and _drawGlow reads
   it every frame off the rAF loop, so flipping it and waiting a few frames is
   enough to make the other path draw. Restored in a finally. */
function measure() {
  const cx = cv.getContext('2d');
  const cw = cv.width, ch = cv.height;
  const img = cx.getImageData(0, 0, cw, ch).data;
  const dpr = cw / cv.getBoundingClientRect().width;
  let lit = 0, aSum = 0, minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
  for (let y = 0; y < ch; y++) {
    for (let x = 0; x < cw; x++) {
      const a = img[(y * cw + x) * 4 + 3];
      if (a > 8) { lit++; aSum += a;
        if (x < minX) minX = x; if (x > maxX) maxX = x;
        if (y < minY) minY = y; if (y > maxY) maxY = y; }
    }
  }
  if (!lit) return { litPixels: 0, meanAlpha: 0, reachPastDiePx: 0, reachAsFractionOfDieWidth: 0 };
  const host = cv.getBoundingClientRect();
  const gl = minX / dpr + host.left, gr = maxX / dpr + host.left;
  const gt = minY / dpr + host.top,  gb = maxY / dpr + host.top;
  const reach = Math.max(box.left - gl, gr - box.right, box.top - gt, gb - box.bottom);
  return { litPixels: lit, meanAlpha: +(aSum / lit).toFixed(1),
           reachPastDiePx: +reach.toFixed(1),
           reachAsFractionOfDieWidth: +(reach / box.width).toFixed(2) };
}

const wasCf = D3X._cf;
let filterB = null, strokeB = null;
try {
  D3X._cf = true;  await sleep(400); filterB = measure();
  D3X._cf = false; await sleep(400); strokeB = measure();
} finally { D3X._cf = wasCf; await sleep(300); }

notes._dial = (window.D3X && D3X.GLOW) ? JSON.parse(JSON.stringify(D3X.GLOW)) : null;
notes._thisMachineTakes = (wasCf === false ? 'stroke-fallback' : 'ctx.filter blur');
notes._filterBranch = filterB;
notes._strokeBranch = strokeB;

/* CONTROL: there is ink at all, on BOTH branches. A zero on either would make
   its numbers meaningless rather than good. */
v.theGlowActuallyDrewSomething = filterB.litPixels > 0 && strokeB.litPixels > 0;

/* A REGRESSION GUARD, NOT A QUALITY BAR, and the difference is deliberate.
   My first pass set these at 0.34 and 80 — numbers invented BEFORE the fix was
   measured. P571 landed at 0.36 and 111.4 on the worse branch, so both keys went
   red, and the tempting move was to turn the dial further until my own guess
   went green. That is backwards: whether the glow now LOOKS right is Denis's
   call on his own phone, and no number here can stand in for it.
   So these bound what P571 actually shipped, with about 25% headroom, and the
   claim they make is the one a probe can honestly make: THE GLOW HAS NOT GROWN
   BACK. Before P571 the worse branch measured 0.60 and 132.5, so both bounds
   would have caught the state Denis reported.
   Applied to the WORSE of the two branches, because the fix has to land for
   whoever is on it. */
const worstReach = Math.max(filterB.reachAsFractionOfDieWidth, strokeB.reachAsFractionOfDieWidth);
const worstAlpha = Math.max(filterB.meanAlpha, strokeB.meanAlpha);
notes._worst = { reachAsFractionOfDieWidth: worstReach, meanAlpha: worstAlpha };
notes._boundsAre = 'a regression guard on P571 (shipped 0.36 / 111.4; pre-P571 was 0.60 / 132.5)';
v.glowHasNotGrownBackInSize = worstReach > 0 && worstReach < 0.45;
v.glowHasNotGrownBackInStrength = worstAlpha > 0 && worstAlpha < 125;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
