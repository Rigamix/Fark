/* CAN YOU ACTUALLY DRAG A CARD IN A MATCH?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "The card activation new mechanic doesn't work at all? Can't drag
 * anything in match."
 *
 * apv_loadout_reaches_table already proves the card REACHES the row with
 * initCardDrag bound to it. So the question is the gesture, and this drives it:
 * a real touch sequence on the real element, reported stage by stage, because
 * "doesn't work" can mean the drag never starts, never arms, or never fires and
 * those are three different bugs.
 *
 * TOUCH, NOT POINTER. initCardDrag listens for mousedown/touchstart - it
 * predates the pointer-event handlers elsewhere in this file - so a probe that
 * dispatches PointerEvents would measure nothing and report the feature broken.
 * Both are driven here, in separate arms, so a difference between them is
 * visible rather than assumed.
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

/* equip a card the way the draft does, then take a seat */
S.run.cards = [null, null, null, null];
S.run.fcards = S.run.fcards || [];
/* P862: RE-POINTED. This probe's subject used to be a non-boss active in a
   REGULAR slot, and section 2 deleted every one of those - so the equip
   silently produced an empty hand and this instrument, one of only two
   covering the whole player-active layer, went VACUOUS rather than red.
   The subject is now the_pyre (Ambrose's Pyre) in the BOSS slot, because
   slot 0 is the only place an active can live now. */
S.run.cards[0] = 'the_pyre';
try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
/* SETTLE FIRST. The cards animate into the row at match start, so a rect read
   too early is a moving target: elementFromPoint then lands on the screen
   behind and the probe reports an occlusion that is really its own impatience.
   Waited on the card's own box being stable across two frames instead of on a
   fixed delay. */
await sleep(2200);
{ let last = null, stable = 0;
  for (let i = 0; i < 60 && stable < 3; i++) {
    const c = document.querySelector('#playerCards .mcard');
    const r = c ? Math.round(c.getBoundingClientRect().top) : null;
    stable = (r !== null && r === last) ? stable + 1 : 0;
    last = r; await sleep(80);
  } }

const card = document.querySelector('#playerCards .mcard');
if (!card) return { err: 'no card in the row', row: document.getElementById('playerCards') ? 'row exists' : 'no row' };

const out = {
  cardId: card.dataset.cid,
  hasUse: typeof _cardHasUse === 'function' ? _cardHasUse(card.dataset.cid) : null,
  strut: (() => { const s = document.getElementById('armLiftStrut');
    return s ? { present: true, connected: s.isConnected, height: +s.getBoundingClientRect().height.toFixed(1) }
             : { present: false }; })(),
  thresholdY: typeof _cardThresholdY === 'function' ? +_cardThresholdY().toFixed(1) : null,
  rowTop: +document.getElementById('playerCards').getBoundingClientRect().top.toFixed(1),
  /* WHAT IS OVER THE CARD. If something else is on top, the touch never
     reaches it however good the handler is. */
  topmostAtCardCentre: (() => { const r = card.getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return el ? el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
                (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '')
              : null; })(),
  cardTouchAction: getComputedStyle(card).touchAction,
};

const POINTER = /(?:\?|&)pointer=1/.test(location.search);
out.arm = POINTER ? 'pointer-events' : 'touch-events';

const r0 = card.getBoundingClientRect();
const from = { x: r0.left + r0.width / 2, y: r0.top + r0.height / 2 };
/* well past the threshold: the strut is the lift, so go twice it */
const lift = (out.strut.height || 70) * 2;
const to = { x: from.x, y: from.y - lift };

function touch(type, x, y) {
  const t = new Touch({ identifier: 1, target: card, clientX: x, clientY: y });
  return new TouchEvent(type, { bubbles: true, cancelable: true,
    touches: type === 'touchend' ? [] : [t],
    targetTouches: type === 'touchend' ? [] : [t], changedTouches: [t] });
}
function mouse(type, x, y) {
  return new MouseEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0 });
}

const stages = [];
if (POINTER) {
  card.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: from.x, clientY: from.y, pointerId: 1, isPrimary: true }));
} else {
  card.dispatchEvent(touch('touchstart', from.x, from.y));
}
await sleep(50);
stages.push({ after: 'start', dragState: !!(typeof _dragState !== 'undefined' && _dragState),
              dragging: !!(typeof _dragState !== 'undefined' && _dragState && _dragState.dragging),
              hasClass: card.classList.contains('dragging') });

for (let i = 1; i <= 8; i++) {
  const y = from.y + (to.y - from.y) * i / 8;
  if (POINTER) card.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, cancelable: true, clientX: from.x, clientY: y, pointerId: 1 }));
  else document.dispatchEvent(touch('touchmove', from.x, y));
  await sleep(30);
}
const rMid = card.getBoundingClientRect();
stages.push({ after: 'move', dragging: !!(typeof _dragState !== 'undefined' && _dragState && _dragState.dragging),
              hasClass: card.classList.contains('dragging'),
              cardCentreY: +(rMid.top + rMid.height / 2).toFixed(1),
              armed: typeof _cardIsArmed === 'function' ? _cardIsArmed(card) : null });

const usesBefore = (G.activeCardState && G.activeCardState.usedCards) ? G.activeCardState.usedCards[out.cardId] : null;
if (POINTER) card.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, cancelable: true, clientX: to.x, clientY: to.y, pointerId: 1 }));
else document.dispatchEvent(touch('touchend', to.x, to.y));
await sleep(1200);

out.stages = stages;
out.usesBefore = usesBefore;
out.usesAfter = (G.activeCardState && G.activeCardState.usedCards) ? G.activeCardState.usedCards[out.cardId] : null;
out.fired = out.usesAfter !== out.usesBefore;
out.control = { cardPresent: true, dragStarted: stages[0].dragState === true,
                dragEngaged: stages[1].dragging === true };
return out;
