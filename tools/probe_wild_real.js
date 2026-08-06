/* RE-RUN AFTER P489. Now compares _legalKeeps' best against the CORRECTED
   rival maximal (_scoreRollBest). If the divergences are gone, the keep
   wiring is inert against the fixed baseline - which is the whole reason
   Denis ruled 'fix it first'.

   Original header follows.

   The wild measurement, redone so the wild can actually fire.
   SUITE: exclude — investigates.

   probe_wild_divergence reported 0 divergences over 394 rolls with a jade.
   probe_wild_instrument then showed swapping bone->jade changed the score in
   0 of 461 rolls, so the material never reached the scorer and that zero was
   VOID, not clean.

   CAUSE, found by reading rather than guessing: scoreRoll L17353 is
       if(!eff||vals[i]!==6)continue;
   A wild only activates on a die SHOWING 6. My sweep built non-decreasing
   sequences and put the jade at index 0 - by construction the lowest value -
   so the jade showed 6 only when every die was a 6. The generator and the
   material placement conspired to never produce a jade 6.

   Here the jade is placed ON a 6. The code comment names the expected effect:
   "four Jade 6s scored 600 where four Bone 6s score 1200". If bone and jade
   still score identically now, the instrument is still blind and nothing here
   can be trusted. */
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
function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}
/* jade goes on the LAST die, which in a non-decreasing sequence is the highest
   - and we only keep sequences whose last value is 6 */
function jadeOnSix(vals) {
  const i = vals.lastIndexOf(6);
  if (i < 0) return null;
  return vals.map((_, k) => (k === i ? 'jade' : 'bone'));
}

/* THE INSTRUMENT CHECK FIRST. If this is 0 again, stop reading the rest. */
let matDiff = 0, matCompared = 0;
const matEx = [];
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const jm = jadeOnSix(vals); if (!jm) continue;
  const bm = vals.map(() => 'bone');
  try {
    const b = scoreRoll(vals, [], 0, {}, bm).total;
    const j = scoreRoll(vals, [], 0, {}, jm).total;
    matCompared++;
    if (j !== b) { matDiff++; if (matEx.length < 6) matEx.push(vals.join('') + ' bone=' + b + ' jade=' + j); }
  } catch (e) {}
}
out.rollsWithAJadeSix = matCompared;
out.rollsWhereJadeChangesScore = matDiff;      /* MUST be > 0 */
out.materialExamples = matEx;

/* now the real question, only meaningful if the above is non-zero */
let checked = 0, ptsDiff = 0, diceDiff = 0, selBeatsRoll = 0;
const ex = [];
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const jm = jadeOnSix(vals); if (!jm) continue;
  let r, K, se;
  try {
    r = _scoreRollBest(vals, [], 0, {}, jm);/* P489: the rival's maximal is now this */
    se = scoreSelection(vals, [], 0, {}, jm);
    K = _legalKeeps(vals.map((v, i) => ({ val: v, mat: jm[i] })), 'o');
  } catch (e) { continue; }
  if (se > r.total) { selBeatsRoll++; if (ex.length < 8) ex.push('SEL>ROLL ' + vals.join('') + ' sel=' + se + ' roll=' + r.total); }
  if (!r.total || r.total <= 0) continue;
  if (!K.length) { ptsDiff++; if (ex.length < 8) ex.push(vals.join('') + ' scores ' + r.total + ' but 0 candidates'); continue; }
  checked++;
  const usedN = r.used ? r.used.filter(Boolean).length : 0;
  if (K[0].pts !== r.total) { ptsDiff++; if (ex.length < 8) ex.push(vals.join('') + ' best=' + K[0].pts + ' maximal=' + r.total); }
  else if (K[0].sel.length !== usedN) { diceDiff++; if (ex.length < 8) ex.push(vals.join('') + ' bestKeeps=' + K[0].sel.length + ' used=' + usedN); }
}
out.rollsChecked = checked;
out.scoreSelectionBeatsScoreRoll = selBeatsRoll;
out.ptsDivergences = ptsDiff;
out.diceDivergences = diceDiff;
out.examples = ex;
return out;
