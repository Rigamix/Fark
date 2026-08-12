/* THE SHELF WITH ONE CARD IN THREE, so the drawn slot and the card it has to
 * match are in the same photograph.
 *
 * Two cards and one empty position: the middle slot is left open, which is the
 * hardest case for P638's claim - a slot drawn from the card's own box should
 * be indistinguishable in size and angle from the two cards beside it, and any
 * mismatch shows up as a step in the row rather than needing a measurement.
 *
 * ?empty=1 clears all three, for the state Denis will actually see at the start
 * of a run.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

if (typeof famLoadoutShow !== 'function') return { err: 'famLoadoutShow missing' };
try { _getS(); } catch (e) { return { err: '_getS threw: ' + e }; }
if (!S || !S.run) return { err: 'no run' };

const EMPTY = /(?:\?|&)empty=1/.test(location.search);
const ids = FAM_CARDS.filter(c => c.fam !== 'tavern').slice(0, 3).map(c => c.id);
/* A HOLE IN THE MIDDLE IS UNREACHABLE, and the first run of this probe proved
   it rather than assuming it: the array was set to [card, null, card] and the
   shelf rendered card, card, slot. famLoadoutShow calls _famDiceMigrate, which
   rebuilds fcards through `if(!c)return` and compacts - so the live model is
   always dense and the empty positions are always the trailing ones. Two cards
   is therefore the real mixed state, not a contrived one. */
S.run.fcards = EMPTY ? [] : [{ id: ids[0], tier: 1 }, { id: ids[2], tier: 1 }];
famLoadoutShow();
if (!await until(() => document.querySelectorAll('#loCardPlane > *').length === 3, 8000))
  return { err: 'plane did not render three positions', got: document.querySelectorAll('#loCardPlane > *').length };
await sleep(1200);

const sr = document.getElementById('loStage').getBoundingClientRect();
const box = el => { const b = el.getBoundingClientRect();
  return { kind: el.className.split(' ')[0],
           leftPct: +(((b.left - sr.left) / sr.width) * 100).toFixed(2),
           topPct:  +(((b.top  - sr.top ) / sr.height) * 100).toFixed(2),
           wPct:    +((b.width / sr.width) * 100).toFixed(2),
           hPct:    +((b.height / sr.height) * 100).toFixed(2) }; };

const items = [...document.querySelectorAll('#loCardPlane > *')].map(box);
const cards = items.filter(i => i.kind === 'fcv');
const slots = items.filter(i => i.kind === 'loSlot');

return {
  arm: EMPTY ? 'all-empty' : 'card-slot-card',
  control: { positionsRendered: items.length, plane: !!document.getElementById('loCardPlane') },
  items,
  /* THE CLAIM, AS A NUMBER: a drawn slot and a card in the same row must be the
     same size. Compared against the MIDDLE card's box in the all-empty arm is
     not possible, so this only means anything on the mixed arm. */
  sizeMatch: (cards.length && slots.length)
    ? { cardHpct: cards[0].hPct, slotHpct: slots[0].hPct,
        deltaPct: +Math.abs(cards[0].hPct - slots[0].hPct).toFixed(3) }
    : null,
  shelfBgLoaded: (() => { const im = document.querySelector('#loStage img.bg');
    return im ? { src: im.getAttribute('src'), natural: im.naturalWidth + 'x' + im.naturalHeight } : null; })(),
};
