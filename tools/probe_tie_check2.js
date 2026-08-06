/* What are the non-unique top candidates? SUITE: exclude — investigates.
   topCandidateIsUnique failed while noSameScoreSizeTies passed, so several
   candidates share the top score but all keep the same NUMBER of dice.
   Hypothesis: they are index-distinct but value-identical - picking WHICH of
   three 1s to keep. If so the keep is effectively unique and inertness holds. */
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

tap(document.getElementById('hsBtnBottom')); await sleep(2200);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 12000);
tap(document.querySelector('.nrdie')); await sleep(1600);
tap(document.getElementById('nrTakeBtn')); await sleep(2600);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 12000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(2000); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 12000);
const ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 40000);
if (!ok || typeof G === 'undefined' || !G) return { skip: 'no idle match' };

const mk = vals => vals.map(x => ({ val: x, mat: 'bone' }));
const out = { examples: [], byValueUnique: 0, byValueNotUnique: 0, notUniqueRolls: 0, scoringRolls: 0 };

function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}

for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const K = _legalKeeps(mk(vals), 'p');
  if (!K.length) continue;
  out.scoringRolls++;
  const top = K.filter(k => k.pts === K[0].pts);
  if (top.length <= 1) continue;
  out.notUniqueRolls++;
  /* are they the same keep by VALUE, or genuinely different keeps? */
  const sigs = new Set(top.map(k => k.sel.map(d => d.val).sort().join(',')));
  if (sigs.size === 1) out.byValueUnique++;
  else {
    out.byValueNotUnique++;
    if (out.examples.length < 6) out.examples.push(vals.join('') + ' -> ' + top.length + ' cands @' + K[0].pts + 'pts, distinct value-keeps: ' + [...sigs].join(' | '));
  }
}
return out;
