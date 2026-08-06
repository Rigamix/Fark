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

/* apv_keep_control — THE CONTROL ARM, exhaustive rather than sampled.
 *
 * P481 landed _legalKeeps deliberately inert so the persona CHOICE could be a
 * separate change with its own before/after. Its control was
 * `bestMatchesMaximal` on ONE dice set, [5,5,5,2,3,4], and it compared POINTS
 * ONLY:  K[0].pts === r.total.
 *
 * Two gaps in that, both load-bearing for the wiring patch that follows:
 *
 *  1. ONE SAMPLE IS NOT A BASELINE. A 6-die bone roll has only 462 distinct
 *     multisets; every size 1..6 together is 923. The whole space is cheap, so
 *     there is no reason to sample it.
 *
 *  2. POINTS ARE NOT THE KEEP. _legalKeeps sorts by pts descending, so K[0] is
 *     *a* maximal-points candidate and ties break arbitrarily. Two candidates
 *     can score identically while keeping a DIFFERENT NUMBER OF DICE - and the
 *     dice left over are what get rerolled. Same points, different dice = a
 *     real behaviour change that a points-only check calls inert.
 *
 * So this asks the question the wiring actually depends on: if the NPC's keep
 * is routed through _legalKeeps and takes K[0], does it keep THE SAME DICE the
 * scorer's used[] already produced - on every possible roll?
 *
 * A divergence here is not a failure of the port. It means the routing is NOT
 * inert, and the persona measurement would be reading two changes at once.
 */
if (typeof _legalKeeps !== 'function') return { skip: '_legalKeeps missing' };
if (typeof scoreRoll   !== 'function') return { skip: 'scoreRoll missing' };

const v = {}, notes = {};
const mk = vals => vals.map(x => ({ val: x, mat: 'bone' }));

/* every non-decreasing sequence of length n over 1..6 = every distinct roll */
function multisets(n) {
  const out = [], cur = [];
  (function rec(start) {
    if (cur.length === n) { out.push(cur.slice()); return; }
    for (let f = start; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); }
  })(1);
  return out;
}

let total = 0, ptsDiff = 0, diceDiff = 0, tieAmbiguous = 0, topNotUnique = 0, topValueDistinct = 0;
const ptsEx = [], diceEx = [], tieEx = [];

for (let n = 1; n <= 6; n++) {
  for (const vals of multisets(n)) {
    const free = mk(vals);
    const r = scoreRoll(free.map(d => d.val), [], 0, {}, free.map(d => d.mat));
    const K = _legalKeeps(mk(vals), 'p');

    /* the scorer's own maximal answer, as a count of dice it consumed */
    const usedN = r && r.used ? r.used.filter(Boolean).length : 0;
    const dead = !r || !r.total || r.total <= 0;

    if (dead) { if (K.length) { diceDiff++; if (diceEx.length < 4) diceEx.push(vals.join('') + ' dead but ' + K.length + ' cands'); } continue; }
    total++;
    if (!K.length) { ptsDiff++; if (ptsEx.length < 4) ptsEx.push(vals.join('') + ' scores ' + r.total + ' but no candidates'); continue; }

    if (K[0].pts !== r.total) { ptsDiff++; if (ptsEx.length < 4) ptsEx.push(vals.join('') + ' best=' + K[0].pts + ' maximal=' + r.total); }
    else if (K[0].sel.length !== usedN) { diceDiff++; if (diceEx.length < 4) diceEx.push(vals.join('') + ' bestKeeps=' + K[0].sel.length + ' usedKeeps=' + usedN + ' (both ' + r.total + 'pts)'); }

    /* AND the tie question: is K[0] even determinate? If several candidates
       share the top score but differ in dice count, which one sorts first is
       arbitrary - so "take K[0]" is not a stable rule even when it happens to
       agree here. */
    const top = K.filter(k => k.pts === K[0].pts);
    if (top.length > 1) {
      topNotUnique++;
      /* index-distinct is fine; VALUE-distinct is not. Keeping the first of
         three identical 1s is the same keep. Keeping [1,1,1] vs [5,5,5] at
         equal points would be a real choice made by sort order. */
      if (new Set(top.map(k => k.sel.map(d => d.val).sort().join(','))).size > 1) {
        topValueDistinct++;
        if (tieEx.length < 4) tieEx.push(vals.join('') + ' -> ' + [...new Set(top.map(k => k.sel.map(d => d.val).sort().join(',')))].join(' | '));
      }
      if (new Set(top.map(k => k.sel.length)).size > 1) tieAmbiguous++;
    }
  }
}

notes._scoringRolls = total;
notes._ptsDiff = ptsDiff;
notes._diceDiff = diceDiff;
notes._tieAmbiguous = tieAmbiguous;
notes._topNotUnique = topNotUnique;
notes._topValueDistinct = topValueDistinct;
notes._ptsExamples = ptsEx;
notes._diceExamples = diceEx;
notes._tieExamples = tieEx;

/* the sweep has to have actually run - a zero divergence over zero rolls is
   the exact false-clean this suite exists to refuse */
v.sweepRan = total > 400;

/* points agree everywhere */
v.ptsMatchesEverywhere = ptsDiff === 0;

/* and so do the DICE - the check P481 did not make */
v.diceMatchEverywhere = diceDiff === 0;

/* WHY THE ABOVE TWO ZEROS ARE A PROPERTY AND NOT A BLIND DETECTOR.
   I predicted ties would be common - keep [5,2] and it should score 50, the
   same as [5] alone but holding one more die. It does not: scoreSelection
   returns -1 for any keep containing a non-scoring die, so _legalKeeps drops
   it at `if(pts<0) continue`. Every candidate is therefore an all-scoring
   subset, the maximal one is the FULL set of scoring dice, and every proper
   subset scores strictly less.
   Measured separately in tools/probe_tie_check.js, which also fed the tie test
   a hand-built same-points/different-size list and confirmed it fires.

   FIRST ASSERTION HERE WAS WRONG, and the probe caught it: I asserted
   `topCandidateIsUnique` (topNotUnique===0) and it FAILED. 7 of 852 rolls do
   have several candidates tied at the top score. Measured in probe_tie_check2:
   all 7 are index-distinct but VALUE-identical - which of three matching 1s to
   keep - and 0 are distinct keeps by value. So the keep is determinate even
   where the index-subset is not, and that is the property inertness needs.
   It replaced a hardcoded `= true`, which could not fail and so asserted
   nothing; the replacement immediately corrected my model of the data.

   LIMIT, stated: this sweep is all-bone. Equal values of DIFFERENT material
   would be value-identical here but not interchangeable in play. */
v.topKeepIsDeterminateByValue = topValueDistinct === 0;
v.noSameScoreSizeTies         = tieAmbiguous === 0;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
