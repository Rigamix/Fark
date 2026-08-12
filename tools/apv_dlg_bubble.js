/* DOES THE PROCEDURAL DIALOGUE BUBBLE ACTUALLY DRAW, AND IS IT THE SHAPE?
 * SUITE: exclude   (a measurement)
 *
 * P649 ports Denis's brief. Three things have to be true and each fails
 * differently, so each is measured on its own:
 *   1. IT IS REACHED. Painted by DLG.show, which is the only door every
 *      dialogue beat goes through - so the bubble is driven by calling that,
 *      not dlgBubblePaint.
 *   2. IT IS THE BUILT SHAPE, not a rounded rectangle. A path built by
 *      buildBubblePoints carries dozens of curve/line commands; a fallback
 *      would carry a handful. Counted rather than eyeballed.
 *   3. THE FLAT PANEL IS GONE. If #dlgScroll still paints its cream background
 *      the bubble is just sitting behind it and looks fine in a screenshot.
 *
 * ?long=1 is the case the brief's shrink-to-fit search exists for: text that
 * has to wrap. The search should give a NARROWER box than the CSS cap while
 * keeping the same line count, so a two-line bubble is as tight as two lines
 * can be. Both arms are needed - a one-line bubble never exercises it.
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
await sleep(1800);

const LONG = /(?:\?|&)long=1/.test(location.search);
const LINE = LONG
  ? "Something's stirring beyond the usual gossip. A royal visit, if you believe the man who told me."
  : "Count it twice. I always do.";

const sc = document.getElementById('dlgScroll'), tx = document.getElementById('dlgText');
/* what the CSS cap alone would give, for the shrink-to-fit comparison */
tx.style.width = ''; const capWidth = tx.clientWidth;

DLG.show(LINE);
await sleep(700);

const bub = sc.querySelector('svg.dlg-bubble');
const paths = bub ? [...bub.querySelectorAll('path')] : [];
const d0 = paths[0] ? paths[0].getAttribute('d') : '';

return {
  arm: LONG ? 'wrapped' : 'one-line',
  control: { reachedByDlgShow: !!bub,
             boxShowing: document.getElementById('dlgBox').classList.contains('show'),
             flatPanelGone: getComputedStyle(sc).backgroundImage === 'none'
                         && getComputedStyle(sc).backgroundColor === 'rgba(0, 0, 0, 0)'
                         && parseFloat(getComputedStyle(sc).borderTopWidth) === 0 },

  /* the shape, as a number: a built perimeter has many commands, a fallback few */
  pathCommands: (d0.match(/[MLCZ]/g) || []).length,
  curveCommands: (d0.match(/C/g) || []).length,
  sharpCommands: (d0.match(/L/g) || []).length,
  layers: paths.length,                    /* parchment + the light layer */
  texture: bub ? ((bub.querySelector('image') || {}).getAttribute
                  ? bub.querySelector('image').getAttribute('href') : null) : null,
  hasTurbulence: !!(bub && bub.querySelector('feTurbulence')),
  hasDisplacement: !!(bub && bub.querySelector('feDisplacementMap')),
  blend: paths[1] ? paths[1].style.mixBlendMode : null,

  /* the box, and whether the tail got room outside it */
  core: { w: sc.offsetWidth, h: sc.offsetHeight },
  svg: bub ? { w: +bub.getAttribute('width'), h: +bub.getAttribute('height'),
               left: bub.style.left, top: bub.style.top } : null,
  overflowsCore: bub ? (+bub.getAttribute('w' + 'idth') > sc.offsetWidth
                     || +bub.getAttribute('height') > sc.offsetHeight) : null,

  /* SHRINK-TO-FIT: on the wrapped arm the pinned width must be BELOW the cap */
  fit: { capWidth, pinned: parseFloat(tx.style.width) || null,
         lines: Math.round(tx.scrollHeight / parseFloat(getComputedStyle(tx).lineHeight)),
         tighterThanCap: LONG ? (parseFloat(tx.style.width) < capWidth - 2) : 'n/a' },

  /* THE ORPHAN GUARANTEE, checked on what is in the DOM rather than on the
     string that was assigned. The browser re-serialises innerHTML - it
     normalises the style attribute among other things - so a check written
     against the pre-parse markup can hunt a substring that no longer exists in
     that exact form, which is how the first version of this reported false on a
     working feature. Counted structurally instead: jitterText emits one span
     per word joined by text nodes, and exactly one of those joins should be a
     non-breaking space. */
  orphan: (() => {
    let plain = 0, nbsp = 0;
    [...tx.childNodes].forEach(k => {
      if (k.nodeType !== 3) return;
      if (k.nodeValue.indexOf(String.fromCharCode(160)) >= 0) nbsp++;
      else if (k.nodeValue.trim() === '') plain++;
    });
    return { wordSpans: tx.querySelectorAll(':scope > span').length,
             plainJoins: plain, nbspJoins: nbsp, lastTwoBound: nbsp === 1 };
  })(),
};
