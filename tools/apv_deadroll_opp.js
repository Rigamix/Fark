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


if (typeof famFire !== 'function') return { skip: 'famFire missing' };
const v = {}, seen = [], fired = [];
const _real = famFire;
famFire = function (hook, ev) {
  try {
    if (hook === 'deadRoll' && ev && ev.actor === 'o')
      seen.push({ free: (ev.free && ev.free.length), isArr: Array.isArray(ev.free) });
  } catch (e) {}
  return _real.apply(this, arguments);
};
/* anything firing FOR the opponent would mean the seam ungated a card */
const _tc = (typeof triggerCard === 'function') ? triggerCard : null;
if (_tc) window.triggerCard = function (cid) { try { fired.push(cid); } catch (e) {} return _tc.apply(null, arguments); };

/* WIRED AT ALL - static, cheap, and independent of whether a bust happens */
v.wiredInStep = (function(){
  try { return runOppTurn.toString().indexOf("deadRoll',{actor:'o'") >= 0; }
  catch (e) { return false; }
})();
/* placed after the Encore rescue and before the bust-save cascade */
v.placedCorrectly = (function(){
  try {
    const t = runOppTurn.toString();
    const r = t.indexOf("deadRoll',{actor:'o'");
    const enc = t.indexOf("_npcFamCard('encore')");
    const sav = t.indexOf('var bustSaved=false');
    return enc >= 0 && sav >= 0 && enc < r && r < sav;
  } catch (e) { return false; }
})();

/* LIVE: hand the turn over and wait for the rival to roll nothing. A dead roll
   is PROBABILISTIC - "it did not happen" is not a failure, so the live checks
   report null rather than false when the rival never busts in the window. */
const G0 = () => (typeof G !== 'undefined' ? G : null);
let drove = false;
if (typeof endPTurn === 'function' && G0()) {
  for (let turn = 0; turn < 6 && !seen.length; turn++) {
    G0()._endMatchFired = false;
    try { endPTurn(); } catch (e) {}
    await until(() => seen.length > 0 || (G0() && G0()._oppTurnActive === false), 14000);
    await sleep(400);
  }
  drove = seen.length > 0;
}
v._seen = seen; v._turnsDriven = drove;
v.raisesWithArray = drove ? seen.every(x => x.isArr) : null;
v.ungatedNothing   = drove ? fired.length === 0 : null;
v._firedCards = fired.slice(0, 5);

famFire = _real; if (_tc) window.triggerCard = _tc;
const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
