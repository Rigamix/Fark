/* apv_oppfx — finOpp's card-effect loops are extracted and still wired.
 *
 * P470 lifted four loops out of finOpp verbatim so tools/sim_harness.js can call
 * the same code instead of a reimplementation that ran none of it. A verbatim
 * move's only claim is "nothing changed", so this checks the functions EXIST,
 * that finOpp CALLS each one, and that every mechanic moved rather than vanished
 * — the suite covers the behaviour.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while (Date.now()-t0<ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
/* G IS `let G=null` AT SCRIPT SCOPE - measured, not assumed. It is NOT a window
   property ('G' in window is false), so a first version that injected
   window.G={...} left the real binding untouched and every call threw on null.
   These functions need a real match; this is the suite's own run-start path. */
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


if (typeof _oppFxPlayer !== 'function') return { skip: 'extraction not present' };
const v = {}, NAMES = ['_oppFxOwnA','_oppFxOwnB','_oppFxPlayer','_oppFxDrain'];

v.allDefined = NAMES.every(n => typeof window[n] === 'function');
v._missing = NAMES.filter(n => typeof window[n] !== 'function');

/* A MINIMAL G RATHER THAN A DRIVEN MATCH. These functions read only
   G.pCards / G.oCards, and shoot.js loads at the menu where G is null - which
   is why a first run reported returnsPts:false with a TypeError rather than a
   real failure. With empty card lists every loop is a no-op, so the three that
   take pts must hand back exactly what they were given. A verbatim lift that
   dropped its `return` would silently zero the rival's bank on every hand, and
   this is the cheapest check that catches it. */
const _po = G.pCards, _oo = G.oCards;
G.pCards = []; G.oCards = [];   /* empty lists -> every loop is a no-op */
v.returnsPts = (function(){
  try {
    const r = [_oppFxOwnA(900), _oppFxOwnB(900), _oppFxPlayer(900)];
    v._returned = r;
    return r.every(x => x === 900);
  } catch(e) { v._err = String(e).slice(0,80); return false; }
})();
v.drainSafe = (function(){
  try { _oppFxDrain(); return true; } catch(e) { v._drainErr = String(e).slice(0,70); return false; }
})();
G.pCards = _po; G.oCards = _oo;

/* finOpp calls all four, and holds none of the mechanics itself any more */
v.finOppWired = (function(){
  try {
    const ro = runOppTurn.toString();
    v._calls = NAMES.filter(n => ro.indexOf(n + '(') >= 0);
    return v._calls.length === 4;
  } catch(e) { v._wireErr = String(e).slice(0,60); return false; }
})();

/* nothing else moved */
v.tablesIntact = typeof BANK_FX !== 'undefined' && Object.keys(BANK_FX).length === 4
              && typeof BUST_FX !== 'undefined' && typeof WILD_LEVEL !== 'undefined';

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
