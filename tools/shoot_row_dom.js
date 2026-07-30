/* WHAT HAPPENS TO THE ROW BETWEEN ROLLS, on each side.
 *
 * Both sides append new dice. So the divergence has to be in what becomes of the
 * dice already there. Records, per roll and per row: how many .die children, how
 * many are kept-still, and the DOM ORDER against each die's recorded seat
 * (pool.lane / oppDice.lane). If a row re-flows, order and seat come apart.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el) => { if (!vis(el)) return false;
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(1900);
const p = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (p) { tap(p); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

/* seat recorded on the game-side record for a DOM die element */
const seatOf = (el) => {
  const look = (arr) => { if (!arr) return undefined;
    for (const r of arr) if (r && r.el === el) return r.lane;
    return undefined; };
  let s = look(G.pool); if (s !== undefined) return s;
  s = look(G.oppDice); if (s !== undefined) return s;
  s = look(G._oppHeld); if (s !== undefined) return s;
  return null;
};
const snap = (rowId) => {
  const els = [...document.querySelectorAll('#' + rowId + ' .die')];
  return {
    children: els.length,
    keptStill: els.filter(e => e.classList.contains('kept-still')).length,
    domOrderSeats: els.map(seatOf),
    centres: els.map(e => { const r = e.getBoundingClientRect(); return Math.round(r.left + r.width / 2); }),
  };
};

const log = { player: [], opp: [] };

/* ── our turn: three rolls, keeping as we go ── */
for (let k = 0; k < 3; k++) {
  tap(document.getElementById('btnRoll'));
  await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
  await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
  await sleep(700);
  log.player.push({ roll: k + 1, ...snap('playerDiceRow') });
  const free = G.pool.filter(d => !d.committed);
  const keep = free.find(d => d.val === 1 || d.val === 5);
  if (!keep) break;
  tap(keep.el); await sleep(400);
  if (document.getElementById('btnRoll').classList.contains('disabled')) break;
}
const bankBtn = document.getElementById('btnBank');
if (vis(bankBtn) && !bankBtn.classList.contains('disabled')) tap(bankBtn);

/* ── the rival's turn: snapshot the row whenever its child count changes ── */
await until(() => G && G.phase === 'opp', 20000);
let lastSig = '';
for (let s = 0; s < 40; s++) {
  await sleep(450);
  const sn = snap('oppDiceRow');
  const sig = sn.children + '|' + sn.keptStill + '|' + sn.domOrderSeats.join(',');
  if (sn.children && sig !== lastSig) { lastSig = sig; log.opp.push({ t: s * 450, ...sn }); }
  if (G.phase !== 'opp') break;
}
return log;
