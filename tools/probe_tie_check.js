/* Is _tieAmbiguous:0 a property, or a blind detector?
   SUITE: exclude — this investigates, it does not claim.

   Prediction that failed: I expected keeping [5,2] to score 50 (same as [5]
   alone) and so produce a same-points/different-size tie. The sweep found zero.
   Either scoreSelection refuses partial keeps - making every candidate an
   all-scoring subset, and zero ties a real property - or my tie test cannot
   fire at all. */
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
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000);
if (typeof G === 'undefined' || !G) return { skip: 'no match' };

const mk = vals => vals.map(x => ({ val: x, mat: 'bone' }));
const out = {};

/* 1. does the scorer accept a keep containing a non-scoring die? */
out.scoreSel_5      = scoreSelection([5],   [], 0, {}, ['bone']);
out.scoreSel_5_2    = scoreSelection([5,2], [], 0, {}, ['bone','bone']);
out.scoreSel_1_5    = scoreSelection([1,5], [], 0, {}, ['bone','bone']);
out.scoreSel_1_2_3  = scoreSelection([1,2,3], [], 0, {}, ['bone','bone','bone']);

/* 2. so what does _legalKeeps actually return for [5,2]? */
out.cands_5_2 = _legalKeeps(mk([5,2]), 'p').map(k => k.sel.map(d => d.val).join('') + '=' + k.pts);

/* 3. a case with a real size spread: 1,1,1,5 */
out.cands_1115 = _legalKeeps(mk([1,1,1,5]), 'p').map(k => k.sel.map(d => d.val).join('') + '=' + k.pts);

/* 4. CAN the detector fire at all? Feed it a hand-built list where two
      entries share points and differ in size. If this reports false, the
      zero in the sweep is meaningless. */
const fake = [{pts:100, sel:[1,2]}, {pts:100, sel:[1]}, {pts:50, sel:[1]}];
const top = fake.filter(k => k.pts === fake[0].pts);
out.detectorFiresOnSynthetic = (top.length > 1 && new Set(top.map(k => k.sel.length)).size > 1);

/* 5. and the same test over every real roll, counting SAME-size ties too, to
      show the sweep was looking at populated data rather than empty lists */
let sameSizeTies = 0, multiTop = 0, checked = 0;
for (let a = 1; a <= 6; a++) for (let b = a; b <= 6; b++) for (let c = b; c <= 6; c++) {
  const K = _legalKeeps(mk([a,b,c]), 'p');
  if (!K.length) continue;
  checked++;
  const t = K.filter(k => k.pts === K[0].pts);
  if (t.length > 1) { multiTop++; if (new Set(t.map(k => k.sel.length)).size === 1) sameSizeTies++; }
}
out.rolls3 = checked;
out.rollsWithMultipleTopCandidates = multiTop;
out.ofThoseSameSize = sameSizeTies;

return out;
