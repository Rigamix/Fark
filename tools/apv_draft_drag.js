/* CAN YOU ACTUALLY DRAG AN OFFERED CARD INTO A SLOT?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "I'd want to be able to drag them in a slot to pick one ... Whatever
 * slot I drag the card in, show the card in."
 *
 * REACHABILITY FIRST, because that is what this project keeps getting wrong: a
 * handler installed on an element the real flow never builds is invisible. The
 * offer is reached by driving endMatch(true), and the gesture is dispatched at
 * real coordinates read off the rendered elements - not by calling _foDropOn.
 *
 * THREE ARMS, and the third is the control that makes the other two mean
 * something:
 *   ?to=empty    drop on an empty slot -> the card is taken and sits THERE
 *   ?to=filled   drop on a held card   -> that card is the one traded away
 *   ?tap=1       move 3px, under the 8px threshold -> NOTHING is picked and the
 *                card's own sheet opens. If a 3px twitch takes a card, the
 *                threshold is not doing its job and both arms above are just
 *                measuring that any pointer sequence picks.
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

/* one card in hand, so there is a filled slot AND empty ones in the same row */
const seed = FAM_CARDS.filter(c => c.fam !== 'tavern')[0].id;
S.run.fcards = [{ id: seed, tier: 1 }];
try { save(); } catch (e) {}

try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
await sleep(1200);
G.pPts = G.target; G.oPts = Math.max(0, (G.target || 2800) - 600);
endMatch(true);

if (!await until(() => document.querySelectorAll('#end-ov .fo-card').length > 0, 12000))
  return { err: 'the offer never rendered' };
await sleep(700);

const offer = document.querySelector('#end-ov .fo-offer');
const out = {
  handlerInstalled: !!(offer && offer._foDrag),
  offerCards: document.querySelectorAll('#end-ov .fo-card').length,
  slotsBefore: [...document.querySelectorAll('#end-ov .fo-slot')].map(
    e => ({ pos: e.getAttribute('data-pos'), ci: e.getAttribute('data-ci'), filled: e.classList.contains('filled') })),
  handBefore: (S.run.fcards || []).map(c => c.id),
  /* Denis's rule, checked directly: one card must sit in the MIDDLE position */
  singleCardIsCentred: (() => { try { return JSON.stringify(_foLayout(1)) === '[null,0,null]'; } catch (e) { return null; } })(),
};

const TAP = /(?:\?|&)tap=1/.test(location.search);
const TO_FILLED = /(?:\?|&)to=filled/.test(location.search);
out.arm = TAP ? 'tap-control' : (TO_FILLED ? 'drop-on-filled' : 'drop-on-empty');

const card = document.querySelector('#end-ov .fo-card');
const slots = [...document.querySelectorAll('#end-ov .fo-slot')];
const target = TO_FILLED ? slots.find(e => e.classList.contains('filled'))
                         : slots.find(e => !e.classList.contains('filled'));
if (!card || !target) return Object.assign(out, { err: 'no card or no target slot' });

const cr = card.getBoundingClientRect(), tr = target.getBoundingClientRect();
out.targetPos = target.getAttribute('data-pos');
const from = { x: cr.left + cr.width / 2, y: cr.top + cr.height / 2 };
const to = TAP ? { x: from.x + 3, y: from.y + 1 }
               : { x: tr.left + tr.width / 2, y: tr.top + tr.height / 2 };

const pe = (t, x, y) => new PointerEvent(t, { bubbles: true, cancelable: true,
  clientX: x, clientY: y, pointerId: 1, isPrimary: true, pointerType: 'touch' });
card.dispatchEvent(pe('pointerdown', from.x, from.y));
await sleep(30);
/* several moves, the way a finger produces them */
for (let i = 1; i <= 6; i++) {
  card.dispatchEvent(pe('pointermove', from.x + (to.x - from.x) * i / 6,
                                       from.y + (to.y - from.y) * i / 6));
  await sleep(25);
}
out.hoverSeen = !!document.querySelector('#end-ov .fo-slot.drop-hover');
card.dispatchEvent(pe('pointerup', to.x, to.y));
/* WHAT A BROWSER ACTUALLY CLICKS: the element under the pointer AT RELEASE, in
   the live tree. Two earlier versions of this line were wrong in opposite
   directions and each invented a bug.
     - dispatching on .fo-card reached nothing (the onclick sits on a CHILD, and
       events bubble up, not down) and reported the tap path broken
     - dispatching on that child reached a DETACHED node after a drop, because
       the drop replaces .res-card - and a detached node does not propagate to
       document, so the capture-phase swallow never saw it and the probe
       reported the sheet opening on every drag
   elementFromPoint after the release is what the browser does. */
const clickTarget = document.elementFromPoint(to.x, to.y)
                 || card.querySelector('[onclick]') || card;
clickTarget.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true,
  clientX: to.x, clientY: to.y }));
await sleep(900);

out.handAfter = (S.run.fcards || []).map(c => c.id);
out.tookACard = out.handAfter.length !== out.handBefore.length
             || out.handAfter.join() !== out.handBefore.join();
out.deckAfter = [...document.querySelectorAll('#end-ov .fo-slot')].map(
  e => ({ pos: e.getAttribute('data-pos'), filled: e.classList.contains('filled') }));
/* did it land WHERE it was dropped? */
const landed = out.deckAfter.find(d => d.pos === out.targetPos);
out.landedInDroppedSlot = !!(landed && landed.filled);
/* P659: the offer must still be THERE after a pick, greyed rather than gone,
   with the layout unmoved. Counted, and the picked one distinguished. */
out.afterPick = { offerCardsStillPresent: document.querySelectorAll('#end-ov .fo-card').length,
                  wrapTaken: !!document.querySelector('#end-ov .fo-wrap.taken'),
                  greyed: document.querySelectorAll('#end-ov .fo-wrap.taken .fo-card:not(.picked)').length,
                  picked: document.querySelectorAll('#end-ov .fo-card.picked').length };
out.sheetOpened = !!document.querySelector('.gbx-sheet.on, #gbSheet.on');
out.continueShown = vis(document.getElementById('end-btns'));

out.control = { handlerInstalled: out.handlerInstalled,
                offerWasReachable: out.offerCards === 3,
                tapMustNotPick: TAP ? (out.tookACard === false) : 'n/a' };
return out;
