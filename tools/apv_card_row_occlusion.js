/* WHAT SITS OVER THE ACTIVATION CARD ROW?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "Can't drag anything in match." A driven touch drag arms and fires in
 * 4 of 5 harness runs; in the fifth the card was not the topmost element at its
 * own centre, so the touch never reached it. That is an occlusion, and this
 * finds what does it rather than guessing.
 *
 * #playerCards lives in .card-bar, which is height:0 with z-index:5 and lets
 * its cards overflow visually. Anything painted above z-index 5 over that strip
 * takes the touch - and #famRowP, the family hand, is z-index:41 and absolutely
 * positioned off the bottom. Whether they actually overlap is a number.
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
S.run.cards = [null,'the_tab',null,null];
S.run.fcards = [{ id: FAM_CARDS.filter(c=>c.fam!=='tavern')[0].id, tier:1 }];
try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
await sleep(2600);

const card = document.querySelector('#playerCards .mcard');
if (!card) return { err: 'no activation card' };
const cr = card.getBoundingClientRect();
const box = el => el ? (r => ({ top:+r.top.toFixed(1), bottom:+r.bottom.toFixed(1),
                                left:+r.left.toFixed(1), right:+r.right.toFixed(1),
                                z:getComputedStyle(el).zIndex,
                                pe:getComputedStyle(el).pointerEvents }))(el.getBoundingClientRect()) : null;

/* probe a grid of points over the card and record what is actually hit */
const hits = {};
for (let fy = 0.15; fy <= 0.86; fy += 0.175) {
  for (let fx = 0.2; fx <= 0.81; fx += 0.3) {
    const el = document.elementFromPoint(cr.left + cr.width*fx, cr.top + cr.height*fy);
    let k = 'null';
    if (el) { k = el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') +
                  (typeof el.className === 'string' && el.className ? '.'+el.className.split(' ')[0] : ''); }
    hits[k] = (hits[k]||0) + 1;
  }
}
const insideCard = [...document.querySelectorAll('*')].filter(el => {
  if (el === card || card.contains(el)) return false;
  const r = el.getBoundingClientRect();
  if (!(r.width > 4 && r.height > 4)) return false;
  const s = getComputedStyle(el);
  if (s.pointerEvents === 'none' || s.display === 'none' || s.visibility === 'hidden') return false;
  const overlaps = r.left < cr.right && r.right > cr.left && r.top < cr.bottom && r.bottom > cr.top;
  if (!overlaps) return false;
  const z = s.zIndex === 'auto' ? 0 : +s.zIndex;
  return z >= 5;
}).map(el => ({ el: el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') +
                     (typeof el.className === 'string' && el.className ? '.'+el.className.split(' ')[0] : ''),
                box: box(el) }));

return { viewport: { w: innerWidth, h: innerHeight },
         card: box(card),
         cardBarZ: getComputedStyle(document.getElementById('playerCards')).zIndex,
         hitGrid: hits,
         /* every hit-testable thing at z>=5 whose box overlaps the card */
         overlappingAbove: insideCard };
