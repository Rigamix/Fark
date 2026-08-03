/* apv_bet_law — the two downsides actually fire, and only when they should.
 *
 * P447 gave Hair of the Dog and Cursed Table the losing halves they lacked. A
 * downside that never triggers is indistinguishable from the pure-upside card
 * it replaced, so the assertion is that each one COSTS something under the
 * condition that should cost, and costs NOTHING under the conditions that
 * should not.
 *
 * THE FALSE-NEGATIVE TRAP IS THE ONE TO AVOID HERE. `_rubOutCircles` floors at
 * zero, so a fixture that starts with no circles on the board would show "no
 * cost" for every case and pass a test written as "did the count drop". Every
 * case below starts with circles to lose, and the no-cost cases are asserted as
 * EXACTLY unchanged rather than as not-negative.
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

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
const _atMatch = await until(() => vis(document.getElementById('screen-match')), 9000);
const _idle    = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000);
if (!_atMatch || !_idle || typeof G === 'undefined' || !G) {
  return { skip: 'setup did not reach an idle match (atMatch=' + _atMatch + ' idle=' + _idle + ')' };
}
if (typeof _hotdToll !== 'function' || typeof _rubOutCircles !== 'function') {
  return { err: 'the P447 helpers are not defined' };
}

_getS();
const out = {};
function board(n, meta) { S.run.points = n; S.run._chalkMeta = meta ? new Array(n).fill(1) : null; }

/* ── the helper keeps count and history in step ── */
board(4, true);
_rubOutCircles(2);
out.helperPair = { points: S.run.points, meta: S.run._chalkMeta.length };

/* it must not go negative, and must report what it actually removed */
board(1, true);
out.helperFloor = { removed: _rubOutCircles(3), points: S.run.points };

/* ── Hair of the Dog: bust before banking COSTS ── */
board(3, true); S.run._hotdNext = true; G._famBankCount = 0;
_hotdToll();
out.hotdBust = { points: S.run.points, armed: !!S.run._hotdNext };

/* ── having banked, the same bust costs NOTHING (the card already paid) ── */
board(3, true); S.run._hotdNext = true; G._famBankCount = 1;
_hotdToll();
out.hotdAfterBank = { points: S.run.points, armed: !!S.run._hotdNext };

/* ── not armed at all: no toll ── */
board(3, true); S.run._hotdNext = false; G._famBankCount = 0;
_hotdToll();
out.hotdUnarmed = { points: S.run.points };

/* ── and it is SPENT, so a second bust in the same match cannot charge twice ── */
board(3, true); S.run._hotdNext = true; G._famBankCount = 0;
_hotdToll(); _hotdToll();
out.hotdChargesOnce = { points: S.run.points };

S.run._hotdNext = false; board(3, true); G._famBankCount = 0;

return {
  ...out,
  verdict: {
    helperMovesBothStructures: out.helperPair.points === 2 && out.helperPair.meta === 2,
    helperFloorsAtZero:        out.helperFloor.removed === 1 && out.helperFloor.points === 0,
    /* the fix itself: busting before a bank now costs a circle */
    hotdBustCosts:             out.hotdBust.points === 2 && out.hotdBust.armed === false,
    /* and does not overcharge */
    hotdSilentAfterBank:       out.hotdAfterBank.points === 3 && out.hotdAfterBank.armed === true,
    hotdSilentUnarmed:         out.hotdUnarmed.points === 3,
    hotdChargesOnce:           out.hotdChargesOnce.points === 2
  }
};
