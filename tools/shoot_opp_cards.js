/* PHOTOGRAPH THE RIVAL'S HAND. Denis, from play: "UI issue with the boss cards?
 * Looks like my card mirrored on top of theirs."
 *
 * #famRowO carries `rotate(180deg)`. That was written when the row held .mcBack
 * — a flat CSS rectangle with a rim and a centred diamond — and the comment on
 * it says so outright: "It reverses their order too, which is meaningless for
 * identical backs." P591 then replaced .mcBack with famCardArt, so the row now
 * holds PAINTED FACES and nothing counter-rotates them.
 *
 * That predicts the rival's cards render upside down, which from across the
 * table reads exactly as "my card mirrored on top of theirs". A prediction from
 * CSS is not a photograph, so this takes one, and puts a player card in frame at
 * the same time so the two rows can be compared in a single image rather than
 * across two.
 *
 * THE HAND IS FORCED, and that is honest here: the question is what the row's
 * transform does to a painted face, which is the same element and the same
 * builder in every match. famRenderRow is the real renderer — nothing about the
 * markup is faked, only which cards are in the hand.
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

/* two real cards each side, so both rows are in frame at once */
/* FAM_CARDS is an ARRAY of definitions, not a keyed map — Object.keys would
   hand back indices and famDef would return nothing for every one of them. */
const ids = FAM_CARDS.filter(c => c.fam !== 'tavern').slice(0, 4).map(c => c.id);
if (ids.length < 4) return { err: 'not enough non-tavern cards to fill both rows' };
const inst = id => ({ id, tier: 1, charges: 1, state: {}, broken: false });
G.pF = [inst(ids[0]), inst(ids[1])];
G.oF = [inst(ids[2]), inst(ids[3])];
famRenderRow();
await sleep(900);

const rowO = document.getElementById('famRowO');
const imgO = document.querySelector('#famRowO .fcv img');
const imgP = document.querySelector('#famRowP .fcv img');
/* the number that decides it: a 180deg rotation shows up as a negative-x,
   negative-y matrix. m11 < 0 means the face is flipped, full stop. */
const mat = s => { const m = new DOMMatrix(getComputedStyle(s).transform); return {a:+m.a.toFixed(3), d:+m.d.toFixed(3)}; };

return {
  arm: 'photo',
  oppCardsOnScreen: document.querySelectorAll('#famRowO .fcv').length,
  playerCardsOnScreen: document.querySelectorAll('#famRowP .fcv').length,
  oppRowTransform: getComputedStyle(rowO).transform,
  oppRowMatrix: mat(rowO),
  /* an <img> inside the row inherits the flip unless something undoes it */
  oppImgFlipped: mat(rowO).a < 0,
  oppImgSrc: imgO ? imgO.getAttribute('src') : null,
  playerImgSrc: imgP ? imgP.getAttribute('src') : null,
  /* Denis's second ask: is anything still painting a degradation state? */
  brokenRuleStillTargetsMcBack: [...document.styleSheets].some(ss => {
    try { return [...ss.cssRules].some(r => r.selectorText && /\.mcBack\.broken/.test(r.selectorText)); }
    catch(e) { return false; } }),
  fcvBrokenRuleExists: [...document.styleSheets].some(ss => {
    try { return [...ss.cssRules].some(r => r.selectorText && /\.fcv\.broken|\.broken\b/.test(r.selectorText)
                                            && !/\.mcBack/.test(r.selectorText)); }
    catch(e) { return false; } }),
};
