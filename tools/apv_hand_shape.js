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

/* apv_hand_shape — ONE derivation of "what kind of hand is this".
 *
 * The straights and triples personas need a candidate's hand TYPE.
 * famCommitBonus already derived it, and its own comment says why a second copy
 * is dangerous: "two derivations of 'is this a straight' would be free to
 * drift, which is what five of tonight's findings turned out to be". So P492
 * EXTRACTED it rather than adding one beside it.
 *
 * The load-bearing check is therefore not "does _handShape work" but "does it
 * reproduce what famCommitBonus computed inline" - and since that code is now
 * gone, the reference below is written independently from the original source
 * rather than by calling the thing under test.
 */
if (typeof _handShape !== 'function') return { skip: '_handShape missing' };
const v = {}, notes = {};

/* the ORIGINAL famCommitBonus derivation, transcribed, not called */
function reference(selD) {
  const _counts = {}; selD.forEach(d => { _counts[d.val] = (_counts[d.val] || 0) + 1; });
  const _isTriple = Object.keys(_counts).some(x => _counts[x] >= 3);
  const _uv = Object.keys(_counts).map(Number).sort((a, b) => a - b);
  let _run = 1, _best = 1;
  for (let _i = 1; _i < _uv.length; _i++) { _run = (_uv[_i] === _uv[_i - 1] + 1) ? _run + 1 : 1; if (_run > _best) _best = _run; }
  return { isTriple: _isTriple, isStraight: _best >= 5, runLen: _best };
}
function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}

let checked = 0, diff = 0;
const ex = [];
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const selD = vals.map(x => ({ val: x, mat: 'bone' }));
  const a = _handShape(selD), b = reference(selD);
  checked++;
  if (a.isTriple !== b.isTriple || a.isStraight !== b.isStraight || a.runLen !== b.runLen) {
    diff++;
    if (ex.length < 4) ex.push(vals.join('') + ' got ' + JSON.stringify({t:a.isTriple,s:a.isStraight,r:a.runLen}) +
                               ' ref ' + JSON.stringify({t:b.isTriple,s:b.isStraight,r:b.runLen}));
  }
}
notes._sweep = checked;
notes._diffs = diff;
notes._examples = ex;
v.sweepRan = checked > 900;
v.matchesTheDerivationItReplaced = diff === 0;

/* runLen has to be real, not just consistent - the corrected straights policy
   keys off "a secured five" */
notes._spot = {
  r_123456: _handShape([1,2,3,4,5,6].map(x=>({val:x,mat:'bone'}))).runLen,
  r_12345:  _handShape([1,2,3,4,5].map(x=>({val:x,mat:'bone'}))).runLen,
  r_2345:   _handShape([2,3,4,5].map(x=>({val:x,mat:'bone'}))).runLen,
  r_111:    _handShape([1,1,1].map(x=>({val:x,mat:'bone'}))).runLen
};
v.runLenIsCorrect = notes._spot.r_123456 === 6 && notes._spot.r_12345 === 5 &&
                    notes._spot.r_2345 === 4 && notes._spot.r_111 === 1;

/* candidates carry it */
const K = _legalKeeps([1,1,1,5,2,3].map(x=>({val:x,mat:'bone'})), 'o', 0);
notes._cands = K.length;
v.candidatesCarryShape = K.length > 0 && K.every(k =>
  typeof k.isTriple === 'boolean' && typeof k.isStraight === 'boolean' && typeof k.runLen === 'number');
v.aTripleCandidateIsFlagged = K.some(k => k.isTriple === true);

/* exactly ONE derivation in the file - the whole point */
v.onlyOneDerivation = (function () {
  try {
    const fc = famCommitBonus.toString();
    const usesShared = fc.indexOf('_handShape(') >= 0;
    const hasOwnCopy = /_best\s*>=\s*5/.test(fc);
    notes._famUsesShared = usesShared; notes._famHasOwnCopy = hasOwnCopy;
    return usesShared && !hasOwnCopy;
  } catch (e) { notes._err = String(e).slice(0, 70); return false; }
})();

/* still inert: P493 is what wires it */
v.notWiredYet = (function () {
  try { return runOppTurn.toString().indexOf('_legalKeeps(') < 0; } catch (e) { return false; }
})();

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
