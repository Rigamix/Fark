/* IS THE BUBBLE'S SHADOW ACTUALLY MULTIPLYING AGAINST THE TABLE?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "shadow is not dark nor multiplied."
 *
 * mix-blend-mode blends an element with its BACKDROP, and the backdrop stops at
 * the nearest stacking context. .dlg-box is position:fixed with z-index:90, so
 * it forms one - which would mean the shadow can only see what is painted
 * inside .dlg-box (nothing) and multiply against transparent leaves the source
 * colour untouched. That is a prediction, not a finding, so it is measured.
 *
 * THE TEST IS ARITHMETIC, not an opinion about the picture. Sample the wood
 * beside the bubble, then sample the shadow strip. Two outcomes, far apart:
 *   BLENDING   shadow pixel ~= wood * colour / 255  -> DARKER than the wood
 *   NOT BLENDING  shadow pixel ~= the flat colour   -> LIGHTER than the wood,
 *                 because #7a5a3c is lighter than the table
 * Whichever it is, the number says so without needing a judgement call.
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

DLG.show("Something's stirring beyond the usual gossip. A royal visit, if you believe the man who told me.");
await sleep(800);

const sc = document.getElementById('dlgScroll');
const bub = sc.querySelector('svg.dlg-bubble');
if (!bub) return { err: 'no bubble' };

/* WHERE THE STACKING CONTEXTS ARE, walked up from the shadow to the body - the
   first one found is where the blend stops looking. */
const chain = [];
for (let el = bub; el && el !== document.documentElement; el = el.parentElement) {
  const s = getComputedStyle(el);
  const why = [];
  if (s.position === 'fixed') why.push('position:fixed');
  if (s.position !== 'static' && s.zIndex !== 'auto') why.push('z-index:' + s.zIndex);
  if (+s.opacity < 1) why.push('opacity:' + s.opacity);
  if (s.filter !== 'none') why.push('filter');
  if (s.isolation === 'isolate') why.push('isolation:isolate');
  if (s.mixBlendMode !== 'normal') why.push('mix-blend-mode:' + s.mixBlendMode);
  if (s.transform !== 'none') why.push('transform');
  if (why.length) chain.push({ el: el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
                                   (el.className && el.className.baseVal === undefined
                                     ? '.' + String(el.className).split(' ')[0] : ''),
                               makes: why.join(', ') });
}

return {
  arm: 'shadow-blend',
  control: { bubblePresent: true,
             shadowPathPresent: !!bub.querySelector('path[style*="multiply"]'),
             shadowFill: (bub.querySelector('path[style*="multiply"]') || {}).getAttribute
                         ? bub.querySelector('path[style*="multiply"]').getAttribute('fill') : null },
  /* every stacking context between the shadow and the page - the blend can only
     see backdrop inside the FIRST of these */
  stackingContextsAboveShadow: chain,
  bubbleRect: (r => ({ left: Math.round(r.left), top: Math.round(r.top),
                       right: Math.round(r.right), bottom: Math.round(r.bottom) }))(bub.getBoundingClientRect()),
};
