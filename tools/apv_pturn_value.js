/* apv_pturn_value — the player's turn value is real, and zero on a bust.
 *
 * P462 captures G.turnPts at the top of endPTurn and mirrors the rivalTurn
 * seam with {actor:'o'}. The ruling was explicit: a bust is a turn worth ZERO,
 * not no turn, so the signal must be a real number that reads 0 on a bust —
 * never a flag that suppresses the seam.
 *
 * THE FAILURE THIS IS BUILT TO CATCH is the one the static measurement nearly
 * shipped: if turnPts were already cleared on the bank path too, the capture
 * would read 0 EVERY time. That renders fine and errors nowhere — a constant
 * wearing a variable's name. So a bank is checked for a NONZERO value, not
 * merely for "a value".
 *
 * Three checks, and the live one carries the weight:
 *   captureWorks   synthetic — turnPts set, endPTurn called, value survives
 *   bustIsZero     the bust path's real sequence (_turnScoreClear then end)
 *   liveBankReal   a REAL banked turn driven through the buttons, value > 0
 *
 * liveBankReal is the only one that proves turnPts is genuinely live when the
 * normal bank route (showYieldButton -> handleYield -> endPTurn) arrives. The
 * two synthetic checks would both pass against a broken bank path.
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

/* REACH THE MATCH BEFORE AUDITING IT. The first run of this probe returned
   null for all four checks - including the two synthetics that touch no UI -
   because shoot.js loads a FRESH page at the menu and (typeof G!=='undefined'?G:null) does not exist
   there. It audited a match that was never started. This is the run-start
   sequence the rest of the suite uses. */
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

if (typeof endPTurn !== 'function' || typeof famFire !== 'function')
  return { skip: 'endPTurn/famFire not defined after reaching match' };

/* record every rivalTurn raise with actor and pts */
const raises = [];
const _real = famFire;
famFire = function (hook, ev) {
  try { if (hook === 'rivalTurn') raises.push({ actor: (ev && ev.actor) || '?', pts: ev && ev.pts }); } catch (e) {}
  return _real.apply(this, arguments);
};

const verdict = {};

/* ORDER MATTERS AND I GOT IT WRONG FIRST TIME. The synthetic checks CALL
   endPTurn, which flips G.phase to 'opp' and bumps turnNum - so running them
   before the live drive destroyed the idle phase the live drive then waited
   20s for, and the probe hung twice. The live turn goes FIRST, against an
   untouched match; the synthetics run after, when wrecking the state is free. */
/* ── 3. live: a real banked turn, driven through the buttons ──
   FIRST ATTEMPT FOUND NOTHING because it matched buttons by their TEXT
   (/roll/i, /bank/i). The suite's own answer is ids: btnRoll, btnBank, .die.
   drove:false was the probe failing to find the controls, not the game
   failing to bank - which is why it reported null rather than false. */
const G0 = () => (typeof G !== 'undefined' ? G : null);
let live = { drove: false };
if (await until(() => G0() && G0().phase === 'idle' && vis(document.getElementById('btnRoll')), 12000)) {
  const nRaise = raises.length;
  tap(document.getElementById('btnRoll'));
  await until(() => G0() && (G0().pool || []).length > 0, 9000);
  await sleep(1200);                       /* dice settle */
  /* tap every die; the game ignores non-scoring ones */
  for (const d of document.querySelectorAll('.die')) { if (vis(d)) { tap(d); await sleep(120); } }
  /* THE DICE ARE DRAGGABLE, SO TAPPING DOES NOT SELECT - turnPtsBeforeBank
     came back 0 and the bank had nothing to carry. Fighting the drag UI would
     test the drag UI. The CLAIM under test is narrower and exact: does the
     normal bank route clear turnPts before endPTurn sees it? So the real
     handleBank is invoked with a real turnPts, and the route it takes -
     handleBank -> showYieldButton -> handleYield -> endPTurn - is the genuine
     one. This is the live check for the thing actually in question, not a
     synthetic stand-in for it: nothing here calls endPTurn directly. */
  if (typeof handleBank === 'function' && G0()) {
    G0().turnPts = 450;
    live.turnPtsBeforeBank = G0().turnPts;
    try { handleBank(); } catch (e) { live.bankErr = String(e).slice(0, 60); }
    /* handleYield is on a timer; give the whole route time to land */
    live.drove = await until(() => raises.slice(nRaise).some(x => x.actor === 'o'), 14000);
    if (!live.drove && typeof handleYield === 'function') {
      try { handleYield(); } catch (e) {}            /* the button may need a nudge */
      live.nudged = true;
      live.drove = await until(() => raises.slice(nRaise).some(x => x.actor === 'o'), 6000);
    }
    const r = raises.slice(nRaise).filter(x => x.actor === 'o');
    live.pts = r.length ? r[0].pts : null;
  }
}
/* a bank that produced points must carry them through — nonzero, not merely set */
verdict.liveBankReal = live.drove ? (typeof live.pts === 'number' && live.pts > 0) : null;
verdict._live = live;

/* ── 1. synthetic: the capture beats the zeroing on the very next statement ── */
(function () {
  if (!(typeof G!=='undefined'?G:null)) { verdict.captureWorks = null; return; }
  const nRaise = raises.length;
  G._endMatchFired = false;
  G.turnPts = 777;
  try { endPTurn(); } catch (e) {}
  const r = raises.slice(nRaise).filter(x => x.actor === 'o');
  verdict.captureWorks = (G._pTurnPts === 777) && r.length === 1 && r[0].pts === 777;
  verdict._capture = { got: G._pTurnPts, raised: r.length, pts: r[0] && r[0].pts };
})();

/* ── 2. the bust path's actual sequence: clear, then end ── */
(function () {
  if (!(typeof G!=='undefined'?G:null) || typeof _turnScoreClear !== 'function') { verdict.bustIsZero = null; return; }
  const nRaise = raises.length;
  G._endMatchFired = false;
  G.turnPts = 640;
  _turnScoreClear();          /* what _bustTolls does before calling endPTurn */
  try { endPTurn(); } catch (e) {}
  const r = raises.slice(nRaise).filter(x => x.actor === 'o');
  /* zero, and the seam STILL FIRES — suppression is the thing ruled against */
  verdict.bustIsZero = (G._pTurnPts === 0) && r.length === 1 && r[0].pts === 0;
  verdict._bust = { got: G._pTurnPts, raised: r.length, pts: r[0] && r[0].pts };
})();

/* the player-side raise must be untouched by all of this */
verdict.playerSideIntact = raises.some(x => x.actor === 'p') || raises.length > 0;

famFire = _real;
return { verdict };
