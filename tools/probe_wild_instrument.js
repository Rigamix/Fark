/* Did the wild second-pass actually FIRE, or is the zero a blind detector?
   SUITE: exclude — investigates.

   probe_wild_divergence found 0 divergences over 394 rolls with a jade present.
   That is the exact shape of result that has been wrong all night, on the exact
   path I predicted would break, so it gets checked rather than believed.

   Two ways the zero could be empty:
     a) candidates never contained the wild die, so scoreSelection's _hasWild
        branch never ran
     b) it ran but can never beat the default, because a wild is strictly more
        flexible than a fixed face - in which case 0 is a real property

   Tests the MECHANISM directly (scoreSelection vs scoreRoll on identical
   dice), not the K[0]-vs-used[] comparison built on top of it. */
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

tap(document.getElementById('hsBtnBottom')); await sleep(2000);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 12000);
tap(document.querySelector('.nrdie')); await sleep(1500);
tap(document.getElementById('nrTakeBtn')); await sleep(2400);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 12000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1800); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 12000);
const ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 40000);
if (!ok || typeof G === 'undefined' || !G) return { skip: 'no idle match' };

const out = {};

/* (a) do candidates ever CONTAIN the wild? If not, the branch never ran. */
let candsWithWild = 0, candsTotal = 0;
function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}
for (let n = 2; n <= 4; n++) for (const vals of multisets(n)) {
  const dice = vals.map((v, i) => ({ val: v, mat: i === 0 ? 'jade' : 'bone' }));
  let K; try { K = _legalKeeps(dice, 'o'); } catch (e) { continue; }
  for (const k of K) { candsTotal++; if (k.sel.some(d => d.mat === 'jade')) candsWithWild++; }
}
out.candidatesTotal = candsTotal;
out.candidatesContainingWild = candsWithWild;

/* (b) the MECHANISM: does scoreSelection ever beat scoreRoll on the same dice?
       That difference is the only way _legalKeeps can outscore used[]. */
let seBeatsSr = 0, seLtSr = 0, compared = 0;
const diffs = [];
for (let n = 1; n <= 5; n++) for (const vals of multisets(n)) {
  const mats = vals.map((_, i) => (i === 0 ? 'jade' : 'bone'));
  let sr, se;
  try {
    sr = scoreRoll(vals, [], 0, {}, mats).total;
    se = scoreSelection(vals, [], 0, {}, mats);
  } catch (e) { continue; }
  compared++;
  if (se > sr) { seBeatsSr++; if (diffs.length < 8) diffs.push('jade@0 ' + vals.join('') + ': sel=' + se + ' roll=' + sr); }
  else if (se >= 0 && se < sr) { seLtSr++; if (diffs.length < 8) diffs.push('jade@0 ' + vals.join('') + ': sel=' + se + ' < roll=' + sr); }
}
out.compared = compared;
out.scoreSelectionBeatsScoreRoll = seBeatsSr;
out.scoreSelectionBelowScoreRoll = seLtSr;
out.diffExamples = diffs;

/* (c) can the detector fire at all? An ALL-BONE control run of the same
       comparison - if bone and jade give identical counts, the material is
       not reaching the scorer and (a)/(b) prove nothing. */
let boneBeats = 0, boneCompared = 0, anyMatDiff = 0;
for (let n = 1; n <= 5; n++) for (const vals of multisets(n)) {
  const bm = vals.map(() => 'bone'), jm = vals.map((_, i) => (i === 0 ? 'jade' : 'bone'));
  try {
    const b = scoreRoll(vals, [], 0, {}, bm).total;
    const j = scoreRoll(vals, [], 0, {}, jm).total;
    boneCompared++;
    if (j !== b) anyMatDiff++;
    const bs = scoreSelection(vals, [], 0, {}, bm);
    if (bs > b) boneBeats++;
  } catch (e) {}
}
out.boneCompared = boneCompared;
out.rollsWhereJadeChangesScore = anyMatDiff;   /* must be > 0 or material is inert */
out.boneScoreSelectionBeatsRoll = boneBeats;
return out;
