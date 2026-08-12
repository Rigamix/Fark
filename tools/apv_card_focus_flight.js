/* DOES A TAPPED CARD FLY, AND DOES THE SHELF'S PLANE LIE DOWN WHILE IT DOES?
 * SUITE: exclude   (a measurement)
 *
 * Denis, second half of the shelf note: "ensure that when focusing on a card it
 * animates smoothly from that position to the focus screen like dice do. Same
 * with me tapping a patron card on their peek panel, etc."
 *
 * Three things have to be true and each is checked separately, because any one
 * of them failing looks the same from the outside - a card that appears rather
 * than travels:
 *   1. THE TAP REACHES THE OPENER. Checked by tapping the real element through
 *      the real delegate, not by calling _loCardFocus by hand. A focus function
 *      that works when called and is wired to nothing is the exact failure this
 *      project has shipped twice.
 *   2. THE CARD TRAVELS. Its inline transform must carry a translate, and its
 *      rect must actually end up near the focus panel rather than at its slot.
 *   3. P636'S PLANE FLATTENS. Otherwise the card arrives at 36% of the screen -
 *      far above the plane's 71.4% origin - drawn small and hard trapezoidal by
 *      the perspective divide.
 *
 * AND THE PEEK PANEL IS THE SECOND HALF OF DENIS'S SENTENCE, so _ptCardFocus is
 * checked for the same wiring rather than assumed to work because it is older.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(50); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tapReal = el => { const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); };

const out = {};
try { _getS(); } catch (e) { return { err: '_getS threw: ' + e }; }
if (!S || !S.run) return { err: 'no run' };

/* ── the shelf ── */
S.run.fcards = FAM_CARDS.filter(c => c.fam !== 'tavern').slice(0, 3).map(c => ({ id: c.id, tier: 1 }));
famLoadoutShow();
if (!await until(() => document.querySelectorAll('#loStage .loCard').length === 3, 8000))
  return { err: 'shelf cards never rendered' };
await sleep(1200);

const plane = document.getElementById('loCardPlane');
const card = document.querySelector('#loStage .loCard');
out.planeExists = !!plane;
out.planeTransformAtRest = plane ? getComputedStyle(plane).transform : null;

const before = card.getBoundingClientRect();
tapReal(card);                                   /* through the real delegate */
await sleep(120);
out.focusOpened = document.getElementById('gbLoadout').classList.contains('lo-focus');
out.planeFlatClass = plane ? plane.classList.contains('flat') : null;
out.inlineTransformSet = /translate/.test(card.style.transform || '');
await sleep(900);                                /* let the .55s flight land */

const after = card.getBoundingClientRect();
const ovr = document.getElementById('gbLoadout').getBoundingClientRect();
const pan = document.getElementById('loFocusPanel');
out.shelf = {
  movedPx: +Math.hypot((after.left+after.width/2)-(before.left+before.width/2),
                       (after.top+after.height/2)-(before.top+before.height/2)).toFixed(1),
  grewBy: +((after.width / before.width)).toFixed(2),
  restedAtPctOfScreen: +((((after.top+after.height/2)-ovr.top)/ovr.height)*100).toFixed(1),
  planeTransformWhileFocused: plane ? getComputedStyle(plane).transform : null,
  panelVisible: !!(pan && +getComputedStyle(pan).opacity > 0.5),
  zoomAbovescrim: (() => { const z = getComputedStyle(plane).zIndex,
                                 sc = document.getElementById('loFocusScrim');
    return { plane: z, scrim: sc ? getComputedStyle(sc).zIndex : null }; })(),
};

_loUnfocus();
await sleep(700);
out.shelf.planeRestoredAfterUnfocus = plane ? getComputedStyle(plane).transform : null;
out.shelf.cardTransformCleared = !(card.style.transform || '').includes('translate');
try { document.getElementById('gbLoadout').remove(); } catch (e) {}

/* ── the peek panel, the second half of Denis's sentence ── */
out.peek = { openerExists: typeof _ptCardFocus === 'function' };
/* wiring, read from the source of whatever calls it - a function that works
   when called by hand and is wired to nothing is the failure being ruled out */
out.peek.callSites = (() => {
  try {
    const src = [...document.scripts].map(s => s.textContent || '').join('\n');
    return (src.match(/_ptCardFocus\s*\(/g) || []).length;   /* 1 = the definition only */
  } catch (e) { return null; }
})();

out.control = { tapDeliveredToRealHandler: out.focusOpened === true,
                cardActuallyMoved: out.shelf.movedPx > 20 };
return out;
