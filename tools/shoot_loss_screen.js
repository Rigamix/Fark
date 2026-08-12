/* PHOTOGRAPH THE LOSS SCREEN, and measure where its four layers landed.
 *
 * The widths came from the files (the three layers share a 1084px canvas, so
 * banner = 96% and panel = 72.8% of it). Only the TOP positions were placed by
 * eye against Denis's mockup, so those are what this is for: render, look,
 * adjust, render again.
 *
 * THE LOSS IS FORCED with endMatch(false) rather than played to. Every layer
 * under test is placed by CSS and switched by one class; none of it reads how
 * the match went, so playing three minutes to a real defeat would photograph
 * the same pixels. The seat is a real launched patron, so the buy-in on the
 * sign is the real number.
 *
 * THREE ARMS, because the sign has three states and one of them is blank:
 *   (default)          patron loss - the sign carries the seat's buy-in
 *   ?boss=1            boss loss WITH an Innkeep's Book stake - carries that
 *   ?boss=1&nostake=1  boss loss with no stake - the sign must be EMPTY, not
 *                      "-0g", and only this arm can show that
 * The boss arms also cost a life, and the heart that says so is polled rather
 * than sampled at the end: it fades in at 700ms and has burst by ~2300, so a
 * single late reading reports it invisible whether it played or was suppressed.
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
await sleep(1400);

const BOSS = /(?:\?|&)boss=1/.test(location.search);
const NOSTAKE = /(?:\?|&)nostake=1/.test(location.search);
if (BOSS) { G._isBoss = true;
  try { S.run._bookResult = NOSTAKE ? { lost: 0 } : { lost: 120 }; } catch (e) {} }
G.pPts = Math.max(0, (G.target || 2800) - 900); G.oPts = G.target;

const ov = document.getElementById('end-ov');
/* ?win=1 photographs the WIN screen through the same harness - useful for
   putting the two paintings side by side, and for checking P635's shortened
   draft delay did not disturb the win layout. */
const WIN = /(?:\?|&)win=1/.test(location.search);
endMatch(WIN);

/* THE HEART IS GONE BY THE TIME THE SCREEN SETTLES, and that is the animation
   working: the boss loss fades the wrapper in at 700ms, drains at 1400 and
   bursts at ~2000, after which coinDrainBurst leaves nothing on screen. A
   single sample at 4.2s therefore reports the wrapper invisible whether it
   played or was hidden outright - which is exactly the false zero P640 was
   chasing. Sampled continuously instead, and the PEAK is what is reported. */
let heartSeen = false, heartPeak = null;
const heartPoll = setInterval(() => {
  const w = document.querySelector('#end-ov .res-gold-wrap');
  if (w && vis(w)) { heartSeen = true;
    const b = w.getBoundingClientRect(), r0 = ov.getBoundingClientRect();
    heartPeak = { top: +(((b.top - r0.top) / r0.height) * 100).toFixed(1),
                  bot: +(((b.bottom - r0.top) / r0.height) * 100).toFixed(1),
                  isHeart: !!document.querySelector('#end-ov .res-coin-big.as-heart') }; }
}, 40);
await sleep(4200);                       /* past the reveal and the draft delay */
clearInterval(heartPoll);

const r = ov.getBoundingClientRect();
const pct = el => { if (!el) return null; const b = el.getBoundingClientRect();
  return { top: +(((b.top - r.top) / r.height) * 100).toFixed(1),
           bot: +(((b.bottom - r.top) / r.height) * 100).toFixed(1),
           left:+(((b.left - r.left) / r.width) * 100).toFixed(1),
           w:   +((b.width / r.width) * 100).toFixed(1) }; };
const q = s => document.querySelector(s);
const board = q('#end-ov .loss-board');

return {
  arm: WIN ? 'win' : (BOSS ? (NOSTAKE ? 'boss-loss-no-stake' : 'boss-loss') : 'patron-loss'),
  /* CONTROL: the class must be on and the art must actually be opaque, or the
     placements below are of an invisible layer */
  control: { lossArtOn: ov.classList.contains('loss-art-on'),
             artOpacity: +getComputedStyle(q('#end-ov .loss-art')).opacity,
             winArtOff: !ov.classList.contains('win-art-on') },

  layers: { bg: pct(q('.loss-bg')), panel: pct(q('.loss-panel')),
            hands: pct(q('.loss-hands')), banner: pct(q('.loss-banner')) },
  panelBox: pct(q('#end-ov .loss-panel-box')),

  sign: { text: board ? board.textContent.trim().replace(/\s+/g, '') : null,
          hidden: board ? board.classList.contains('empty') : null,
          transform: board ? getComputedStyle(board).transform : null,
          box: pct(board) },

  /* what else is on screen, so a collision shows up as numbers not just pixels */
  title: (q('#end-ov .res-title') || {}).textContent,
  scoresVisible: vis(q('#end-ov .res-scores')),
  /* at settle time - expected false once the burst has finished */
  goldWrapVisible: vis(q('#end-ov .res-gold-wrap')),
  /* what actually played: did the heart ever reach the screen, and where */
  heart: { everVisible: heartSeen, peak: heartPeak },
  exitParchment: pct(q('#exitParchment')),
  continueBtn: pct(q('#endBtns')),
  resCard: pct(q('#end-ov .res-card')),
  /* Denis: the win and loss primary buttons should land in the same place.
     Reported as a number on both arms so "they match" is checkable. */
  primaryBtn: pct(q('#end-ov.win-art-on .fo-skip') || q('#end-btns')),
  deckSlots: [...document.querySelectorAll('#end-ov .fo-slot')].map(pct),
};
