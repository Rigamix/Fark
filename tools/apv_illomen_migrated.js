/* apv_illomen_migrated — the boss's omen reads "scored nothing", on one site.
 *
 * P463 deleted the _bustTolls payout and made endPTurn handle BOTH outcomes off
 * _pTurnPts, the value the rivalTurn seam carries. Ruled deliberately: a bank
 * blocked or stolen to zero is a turn that produced nothing, so the boss now
 * pays out on two cases where it previously did not. That behaviour change is
 * the point, not a side effect - so this pins the invariants that must NOT
 * have moved alongside it.
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

if (typeof endPTurn !== 'function' || typeof famDef !== 'function')
  return { skip: 'endPTurn/famDef missing after reaching match' };
const G0 = () => (typeof G !== 'undefined' ? G : null);
if (!G0()) return { skip: 'no match' };
const P = famDef('ill_omen').p[0];          /* tier 1: [take, give] */
const v = {};

function runOmen(turnPts, pPts, oPts) {
  const g = G0();
  g._endMatchFired = false; g._oIllOmen = { tier: 1 };
  g.pPts = pPts; g.oPts = oPts; g.turnPts = turnPts;
  try { endPTurn(); } catch (e) { v._err = String(e).slice(0, 70); }
  return { p: g.pPts, o: g.oPts, cleared: !g._oIllOmen };
}

/* 1. scored nothing -> omen LANDS, boss takes, capped at what the player has */
const a = runOmen(0, 5000, 1000);
v.landsOnZero = (a.p === 5000 - P[0]) && (a.o === 1000 + P[0]) && a.cleared;
v._lands = a;

/* 2. scored something -> omen MISSES, player gains */
const b = runOmen(500, 5000, 1000);
v.missesOnScore = (b.p === 5000 + P[1]) && (b.o === 1000) && b.cleared;
v._misses = b;

/* 3. the cap: a boss cannot take more than the player has */
const c = runOmen(0, 10, 1000);
v.takeIsCapped = (c.p === 0) && (c.o === 1010) && c.cleared;
v._cap = c;

/* 4. THE RULED CHANGE. A blocked/stolen bank reaches endPTurn with turnPts
   cleared but WITHOUT having bust - it is the same arrival as case 1, so what
   must be proven is that the payout keys off the VALUE and not off a bust
   marker. Driving the real block path is not needed for that: if any bust-only
   condition survived, case 1 could not have paid at all. This asserts the old
   two-site shape is gone rather than re-testing the same arithmetic. */
v.oneSiteOnly = (function () {
  const src = (endPTurn.toString() + (typeof _bustTolls === 'function' ? _bustTolls.toString() : ''));
  return /THEIR OMEN LANDS/.test(endPTurn.toString())
      && !(typeof _bustTolls === 'function' && /_oIllOmen/.test(_bustTolls.toString()));
})();

/* the player's own card must be untouched */
v.playerCardIntact = !!(CFX && CFX.ill_omen && typeof CFX.ill_omen.rivalTurn === 'function');
/* DIAGNOSTICS OUT OF THE VERDICT. run_probes marks a probe INDET if ANY verdict
   key is non-boolean, so the _-prefixed values I was returning for debugging
   made every one of these probes indeterminate in the suite - passing when run
   by hand, invisible as a regression guard where it counts. Underscore keys
   move to notes; a genuine null stays in the verdict, because "did not run"
   SHOULD read as indeterminate. */
const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
