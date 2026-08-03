/* apv_lane_lifetime — the lane-marker primitive, and the one behaviour it changed.
 *
 * P444 put Snare, Snuff and Fog on _lmArm/_lmDue/_lmSpend/_lmRetire. Two of the
 * three already gated on `turn===oppTurnCount`; SNUFF DID NOT, and now does.
 * The patch claims that change is behaviour-identical on today's paths. A claim
 * like that is exactly the kind this project keeps catching itself asserting
 * instead of testing, so this tests it.
 *
 * THE DECISIVE CHECK is `dueOnArmedTurn` together with `notDueOnLaterTurn`:
 *   - arm at oppTurnCount = N, exactly as placement does
 *   - advance to N+1 (placement arms for +1, and oppTurnCount increments before
 *     every one of these checks) -> the marker MUST be due. This is the path
 *     that runs today, and the old `live`-only test also fired here. Identical.
 *   - advance to N+2 -> the marker MUST NOT be due. This is where old and new
 *     differ: `live` alone would still have fired. That divergence is the
 *     point of the change, so the test asserts the new answer rather than
 *     treating any answer as fine.
 *
 * WHY IT UNIT-TESTS THE PRIMITIVE RATHER THAN DRIVING A SNUFFED TURN. Getting a
 * real Snuff onto a real opponent turn needs an enchant placed on a specific
 * lane and an opponent turn to run, which the roll decides - the same
 * precondition problem that makes apv_break_borrowed a designed skip. A test
 * that usually declines proves less than one that always runs. The turn
 * arithmetic IS the changed behaviour, and it is fully determined by these
 * four functions.
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

/* the precondition gate apv_preserve had to learn the hard way */
if (!_atMatch || !_idle || typeof G === 'undefined' || !G) {
  return { skip: 'setup did not reach an idle match (atMatch=' + _atMatch + ' idle=' + _idle + ')' };
}
if (typeof _lmArm !== 'function' || typeof _lmDue !== 'function') {
  return { err: 'the lane-marker primitive is not defined' };
}

const out = {};
const N = 5;

/* ── arm exactly as placement does, then walk the turn counter ── */
G.oppTurnCount = N;
_lmArm('_snuff', 2, 1);
out.armed = JSON.parse(JSON.stringify(G._snuff));
out.dueOnPlacementTurn = _lmDue('_snuff');      // N — must be false, armed for N+1
G.oppTurnCount = N + 1;
out.dueOnArmedTurn = _lmDue('_snuff');          // N+1 — the live path
G.oppTurnCount = N + 2;
out.dueOnLaterTurn = _lmDue('_snuff');          // N+2 — where old and new diverge

/* ── spend: a 1-turn marker retires, a 2-turn marker re-arms for the next ── */
G.oppTurnCount = N; _lmArm('_fog', 3, 1);
G.oppTurnCount = N + 1; _lmSpend('_fog');
out.oneTurnRetires = (G._fog.live === false);

G.oppTurnCount = N; _lmArm('_fog', 3, 2);
G.oppTurnCount = N + 1; _lmSpend('_fog');
out.twoTurnStillLive = (G._fog.live === true);
out.twoTurnRearmed = (G._fog.turn === N + 2);
G.oppTurnCount = N + 2;
out.dueAgainNextTurn = _lmDue('_fog');
_lmSpend('_fog');
out.secondSpendRetires = (G._fog.live === false);

/* ── retire is not spend: it kills a marker with turns left ── */
G.oppTurnCount = N; _lmArm('_snare', 1, 2);
_lmRetire('_snare');
G.oppTurnCount = N + 1;
out.retireBeatsTurnsLeft = (G._snare.live === false) && !_lmDue('_snare');

/* ── extra fields survive arming (snare's x2) ── */
_lmArm('_snare', 1, 1, { x2: true });
out.extraKept = (G._snare.x2 === true);

/* leave no armed markers behind for whatever runs next */
G._snuff = null; G._fog = null; G._snare = null;

return {
  ...out,
  verdict: {
    notDueOnPlacementTurn: out.dueOnPlacementTurn === false,
    /* the today path: unchanged by the patch */
    dueOnArmedTurn:        out.dueOnArmedTurn === true,
    /* the changed path: `live` alone would have fired here */
    notDueOnLaterTurn:     out.dueOnLaterTurn === false,
    oneTurnRetires:        out.oneTurnRetires === true,
    twoTurnStillLive:      out.twoTurnStillLive === true,
    twoTurnRearmed:        out.twoTurnRearmed === true,
    dueAgainNextTurn:      out.dueAgainNextTurn === true,
    secondSpendRetires:    out.secondSpendRetires === true,
    retireBeatsTurnsLeft:  out.retireBeatsTurnsLeft === true,
    extraKept:             out.extraKept === true
  }
};
