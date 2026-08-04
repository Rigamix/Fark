/* apv_opp_seams — the opponent's turnStart and roll seams fire, and change nothing.
 *
 * P459 raised two seams on the opponent's turn. Two things must be true, and
 * they fail in opposite directions:
 *
 *   THEY FIRE. A seam that is never raised is indistinguishable from one that
 *   was never added — and this whole area has already produced two findings
 *   that turned out to be "the moment does not exist". So a real opponent turn
 *   is driven and the seams are counted by observation.
 *
 *   NOTHING ELSE CHANGED. The patch deliberately ungates no card: every CFX
 *   hook still tests _fxMine and still returns early for an opponent. If a
 *   card started firing for a boss, that is a behaviour change nobody
 *   authorised — the direction was seams first, personality later, precisely
 *   so those two do not arrive tangled together.
 *
 * COUNTED BY WRAPPING famFire, not by watching for effects, because the
 * correct outcome IS no effect. Watching for effects would confirm the seam
 * only when something went wrong.
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

const ready = await until(() => typeof famFire === 'function', 15000);
if (!ready) return { err: 'famFire not defined' };

/* wrap famFire and record every raise with its actor */
const seen = [];
const _real = famFire;
famFire = function (hook, ev) { try { seen.push(hook + ':' + ((ev && ev.actor) || '?')); } catch (e) {}
  return _real.apply(this, arguments); };

/* and record any card whose hook actually does something for the opponent */
const fired = [];
Object.keys(CFX).forEach(id => {
  ['turnStart', 'roll'].forEach(h => {
    const fn = CFX[id] && CFX[id][h];
    if (typeof fn !== 'function') return;
    CFX[id][h] = function (ev) {
      const before = JSON.stringify([G && G.oPts, G && G.pPts]);
      const r = fn.apply(this, arguments);
      if (ev && ev.owner === 'o' && JSON.stringify([G && G.oPts, G && G.pPts]) !== before) fired.push(id + '.' + h);
      return r;
    };
  });
});

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
const atMatch = await until(() => vis(document.getElementById('screen-match')), 9000);
const idle = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000);
if (!atMatch || !idle) return { skip: 'setup did not reach an idle match' };

/* CALL THE RIVAL'S TURN DIRECTLY. Driving the UI to a handover failed twice -
   eight roll/bank cycles left oppTurnCount at 0 - and the seams are what is
   under test, not the path to them. runOppTurn is a global taking no
   arguments, and it is what setTimeout(runOppTurn, ...) invokes at 27022, so
   calling it is the same entry the game uses.
   (En route: `grep "runOppTurn("` reported NO callers, because the real one
   passes it as a REFERENCE to setTimeout with no paren after the name. The
   game visibly plays rival turns, so "never called" was a grep shape, not a
   fact - checked before believing it.) */
G.phase = 'opp';
try { runOppTurn(); } catch (e) { /* it schedules and returns */ }
const oppRan = await until(() => (G && (G.oppTurnCount || 0) > 0), 20000);
/* WAIT FOR THE TURN TO END, NOT A FIXED SLEEP. bust and bankBonus fire at the
   CONCLUSION of the rival's turn, and a 4s sleep caught turnStart and roll but
   ended before either terminal seam - which reads as "those two seams do not
   fire" when the turn simply had not got there. runOppTurn sets
   G._oppTurnActive true at entry and false when it finishes; that flag is the
   real end, so wait on it. */
const oppFinished = await until(() => G && G._oppTurnActive === false, 30000);
await sleep(1200);

const oppSeams = seen.filter(x => x.endsWith(":'o'") || x.endsWith(':o'));
return {
  oppRan, oppFinished, oppTurnCount: G && G.oppTurnCount,
  oppTurnStart: seen.filter(x => x === 'turnStart:o').length,
  oppRoll:      seen.filter(x => x === 'roll:o').length,
  oppBust:      seen.filter(x => x === 'bust:o').length,
  oppBankBonus: seen.filter(x => x === 'bankBonus:o').length,
  allOppSeams:  [...new Set(seen.filter(x => x.endsWith(':o')))].sort(),
  playerStill:  seen.filter(x => x === 'turnStart:p').length,
  cardsThatFiredForOpponent: fired,
  verdict: {
    /* the seams exist and were raised on a real rival turn */
    turnStartRaised: seen.filter(x => x === 'turnStart:o').length >= 1,
    rollRaised:      seen.filter(x => x === 'roll:o').length >= 1,
    /* P461: the rival's turn either busts or banks, so at least ONE of these
       must raise on any completed turn - asserting both would flap on the
       roll. Which one fired is reported above. */
    bustOrBankRaised: (seen.filter(x => x === 'bust:o').length
                     + seen.filter(x => x === 'bankBonus:o').length) >= 1,
    /* the player's own seams are untouched */
    playerSeamsIntact: seen.filter(x => x === 'turnStart:p').length >= 1,
    /* and NOTHING started firing for the boss - the patch ungates nobody */
    noCardBehaviourChanged: fired.length === 0
  }
};
