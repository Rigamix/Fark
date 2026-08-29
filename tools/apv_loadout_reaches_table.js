/* THE WHOLE CHAIN: equip -> survive _getS() -> launch -> hand -> draggable card.
 *
 * WHY THIS AND NOT THE LAST PROBE. P615 was verified by calling
 * initMatchScreen({pCards:[...]}) myself - which proves the function uses what
 * it is given and says NOTHING about whether the game ever gives it anything.
 * That is the exact mistake that let `const pCards=[]` survive my own review, so
 * repeating it one level up would be the same error with a longer chain.
 * Here nothing is handed to initMatchScreen: a card is equipped the way the
 * draft equips it, _getS() is called repeatedly (that is what used to sell the
 * hand back every time), and the match is started through launchSeat.
 *
 * CONTROL: the identical flow with no card equipped must produce an empty hand
 * and zero initCardDrag calls, or "the card arrived" proves nothing.
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

window.__icd = 0;
const realICD = window.initCardDrag;
window.initCardDrag = function(){ window.__icd++; return realICD.apply(this, arguments); };

/* reach the gauntlet screen, where a seat can be taken */
for (let a = 0; a < 3; a++) {
  tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && typeof _getS === 'function'
                     && S && S.run, 9000)) break;
}
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };

const EQUIP = /(?:\?|&)equip=1/.test(location.search);
const out = { arm: EQUIP ? 'equipped' : 'control' };
window.__icd = 0;
S.run.cards = [null, null, null, null];
/* P862: RE-POINTED. This probe's subject used to be a non-boss active in a
   REGULAR slot, and section 2 deleted every one of those - so the equip
   silently produced an empty hand and this instrument, one of only two
   covering the whole player-active layer, went VACUOUS rather than red.
   The subject is now the_pyre (Ambrose's Pyre) in the BOSS slot, because
   slot 0 is the only place an active can live now. */
if (EQUIP) S.run.cards[0] = 'the_pyre';
out.equippedAtStart = (S.run.cards || []).filter(Boolean).slice();
/* THE LATCH: _getS used to run the legacy cutover on EVERY call and blank this */
for (let i = 0; i < 5; i++) { try { _getS(); } catch (e) {} }
out.survivedGetS = (S.run.cards || []).filter(Boolean).slice();
out.goldBefore = S.run.gold;
try { G = null; } catch (e) {}
try { launchSeat(0); } catch (e) { out.launchErr = String(e); }
out.started = await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000);
await sleep(2000);
out.gPCards = (typeof G !== 'undefined' && G && G.pCards) ? G.pCards.slice() : null;
out.rowCards = [...document.querySelectorAll('#playerCards .mcard')].map(e => e.dataset.cid);
out.icd = window.__icd;
out.usesSeeded = (typeof G !== 'undefined' && G && G.activeCardState && G.activeCardState.usedCards)
  ? (G.activeCardState.usedCards['the_pyre'] === undefined ? null : G.activeCardState.usedCards['the_pyre']) : null;
out.gate = (typeof _cardHasUse === 'function') ? _cardHasUse('the_pyre') : null;
return out;
