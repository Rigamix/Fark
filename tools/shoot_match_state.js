/* THE MATCH TABLE, dressed the way a player sees it mid-turn.
 *
 * For showing three of this session's changes in one frame:
 *   P633  the rival's cards, upright and reading the right way up
 *   P632  a dialogue line in the PARCHMENT BOX, not in the status strip
 *   P591+ both card rows leaning into the same table plane
 *
 * The hands are forced and the line is fired directly, which is honest for a
 * photograph: what is under test is where things are DRAWN, and every one of
 * those paths is the real renderer - famRenderRow for the rows, DLG.show for the
 * box. Nothing about the markup is faked, only which cards are held and when the
 * rival happens to speak.
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
await sleep(2200);

const ids = FAM_CARDS.filter(c => c.fam !== 'tavern').slice(0, 5).map(c => c.id);
const inst = id => ({ id, tier: 1, charges: 1, state: {}, broken: false });
G.pF = [inst(ids[0]), inst(ids[1]), inst(ids[2])];
G.oF = [inst(ids[3]), inst(ids[4])];
famRenderRow();
await sleep(500);

/* a real line through the real box */
try { DLG.show("Count it twice. I always do."); } catch (e) {}
await sleep(900);

const box = document.getElementById('dlgBox');
/* IS THE PARCHMENT PAINTED, or is the cream rectangle a CSS fallback? The box
   draws its scroll onto #dlgCanvas inside a double-rAF. A canvas whose width is
   0 was never sized, so nothing was drawn on it - and that is a different fact
   from "the headless compositor did not composite it". */
const cv = document.getElementById('dlgCanvas');
let scroll = { present: !!cv, w: cv ? cv.width : null, h: cv ? cv.height : null, paintedPx: null };
try { if (cv && cv.width > 0) { const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
  let p = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 8) p++; scroll.paintedPx = p; } }
catch (e) { scroll.err = String(e).slice(0,80); }

return {
  arm: 'match-table',
  scroll,
  control: { oppCards: document.querySelectorAll('#famRowO .fcv').length,
             playerCards: document.querySelectorAll('#famRowP .fcv').length,
             dlgBoxShowing: !!(box && box.classList.contains('show')) },
  /* the P633 claim in one number: a>0 means the rival's faces are upright */
  oppRowMatrixA: +new DOMMatrix(getComputedStyle(document.getElementById('famRowO')).transform).a.toFixed(3),
  statusStrip: (document.getElementById('statusMsg') || {}).textContent || '',
};
