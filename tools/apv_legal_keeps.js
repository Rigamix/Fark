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


/* apv_legal_keeps — the NPC now has options to choose from, and the best of
 * them is what it was already taking.
 *
 * P481 ports the sim harness's legalKeeps into the game, seat-aware. It changes
 * NO behaviour by design: the machinery lands inert so the CHOICE can be a
 * separate change with its own before/after. OPEN.md 6 exists because three
 * difficulty changes landed in one session without being separable.
 *
 * So the load-bearing check is not "does it enumerate" - it is "does its best
 * candidate equal what the scorer's used[] already produced". If those differ,
 * the machinery is not inert and the next patch's before/after would be
 * measuring two changes at once.
 */
if (typeof _legalKeeps !== 'function') return { skip: '_legalKeeps missing' };
const v = {};

const mk = (vals) => vals.map(x => ({val:x, mat:'bone'}));

/* enumeration is real: three 5s should yield more than one legal keep */
const K = _legalKeeps(mk([5,5,5,2,3,4]), 'p');
v._n = K.length;
v.enumeratesOptions = K.length > 1;
v.sortedByPoints = K.every((k,i) => i === 0 || K[i-1].pts >= k.pts);
v._top = K.length ? { pts: K[0].pts, n: K[0].sel.length, left: K[0].left } : null;

/* the SAME dice through the scorer's own maximal answer */
const free = mk([5,5,5,2,3,4]);
const r = scoreRoll(free.map(d=>d.val), [], 0, {}, free.map(d=>d.mat));
const maximal = free.filter((d,i) => r.used && r.used[i]);
v._maximal = { pts: r.total, n: maximal.length };

/* THE INERTNESS CHECK: best candidate scores what the maximal keep scores */
v.bestMatchesMaximal = !!(K.length && r && K[0].pts === r.total);

/* a dead roll yields no candidates - the caller must be able to tell */
v.deadRollEmpty = _legalKeeps(mk([2,3,4,6,6,2]), 'p').length === 0;

/* WAS `rivalSeatWorks`, and it proved "returns a non-empty array" while its
   name claimed the seat worked - it would have passed on candidates with wrong
   points, wrong dice, anything. Named as the archetype of a check verifying
   less than it says, so it is the first one repaired.
   Now asserts what the rival seat actually has to get right: every candidate
   scores, every candidate is a real subset of the dice handed in, and the best
   one equals the scorer's own maximal answer for that seat. */
v.rivalSeatEnumeratesCorrectly = (function(){
  try {
    const free = mk([1,1,1,2,3,4]);
    const O = _legalKeeps(free, 'o', 0);
    v._rivalN = O.length;
    if (!O.length) return false;
    const allScore  = O.every(k => k.pts > 0 || k.icons > 0);
    const allSubset = O.every(k => k.sel.every(d => free.indexOf(d) >= 0));
    const sizesOk   = O.every(k => k.left === free.length - k.sel.length);
    const r = _scoreRollBest(free.map(d=>d.val), G.oCards||[], 0, {}, free.map(d=>d.mat));
    const bestMatches = O[0].pts === r.total;
    v._rivalDetail = {allScore, allSubset, sizesOk, bestMatches, best:O[0].pts, maximal:r.total};
    return allScore && allSubset && sizesOk && bestMatches;
  } catch(e) { v._rivalErr = String(e).slice(0,70); return false; }
})();

/* and nothing calls it yet - the machinery is landed, not wired */
v.notWiredYet = (function(){
  try {
    const src = (typeof runOppTurn === 'function' ? runOppTurn.toString() : '');
    return src.indexOf('_legalKeeps(') < 0;
  } catch(e) { return false; }
})();

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
