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

/* apv_fog_index — under FOG the rival used to keep the WRONG DICE.
 *
 * FOG hides a seat by SPLICING it out of the array that gets scored, so `used`
 * came back one short - while the snare check and the keep loop both index it
 * with positions from the FULL free list. Every index at or above the fogged
 * seat was off by one.
 *
 * The sim had this right all along (`index shift: used is indexed against the
 * fogged array`); the game never got the same treatment. Third instance of the
 * two-copies problem, and the first where the SIM was the correct one.
 *
 * P491 re-expands `used` instead of compensating per read site - `used` is
 * reassigned five times downstream from FULL-length arrays, so shifting those
 * would recreate the bug.
 */
const v = {}, notes = {};

/* ── the arithmetic, with the real scorer ── */
function keepsFor(free, fogAt) {
  const mats = free.map(() => 'bone');
  const fv = free.slice(), fm = mats.slice();
  if (fogAt >= 0) { fv.splice(fogAt, 1); fm.splice(fogAt, 1); }
  const r = _scoreRollBest(fv, [], 0, {}, fm);
  const used = r.used.slice();
  /* exactly what P491 now does in runOppTurn */
  if (fogAt >= 0 && used.length < free.length) used.splice(fogAt, 0, false);
  return { used, kept: free.filter((x, i) => used[i]), total: r.total };
}
/* what it SHOULD be: the fogged seat excluded, everything else by its own
   position in the shortened array - derived independently of the fix */
function correctFor(free, fogAt) {
  const mats = free.map(() => 'bone');
  const fv = free.slice(), fm = mats.slice();
  fv.splice(fogAt, 1); fm.splice(fogAt, 1);
  const r = _scoreRollBest(fv, [], 0, {}, fm);
  return free.filter((x, i) => { if (i === fogAt) return false;
    return r.used[i > fogAt ? i - 1 : i]; });
}

/* sweep every roll and every fog position, not the one case that found it */
function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}
let checked = 0, mismatch = 0, lenBad = 0, fogKept = 0;
const ex = [];
for (let n = 2; n <= 6; n++) for (const vals of multisets(n)) {
  for (let fogAt = 0; fogAt < n; fogAt++) {
    let g, c;
    try { g = keepsFor(vals, fogAt); c = correctFor(vals, fogAt); } catch (e) { continue; }
    checked++;
    if (g.used.length !== vals.length) lenBad++;
    if (g.used[fogAt]) fogKept++;
    if (JSON.stringify(g.kept) !== JSON.stringify(c)) {
      mismatch++;
      if (ex.length < 4) ex.push(vals.join('') + ' fog@' + fogAt + ' got[' + g.kept + '] want[' + c + ']');
    }
  }
}
notes._cases = checked;
notes._mismatches = mismatch;
notes._wrongLength = lenBad;
notes._fogSeatKept = fogKept;
notes._examples = ex;

v.sweepRan = checked > 800;
v.usedIsAlwaysFullLength = lenBad === 0;
v.fogSeatIsNeverKept = fogKept === 0;
v.keepMatchesCorrected = mismatch === 0;

/* ── control: with NO fog, nothing changed at all ── */
let ctl = 0, ctlDiff = 0;
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const mats = vals.map(() => 'bone');
  const r = _scoreRollBest(vals, [], 0, {}, mats);
  const g = keepsFor(vals, -1);
  ctl++;
  if (JSON.stringify(g.used) !== JSON.stringify(r.used)) ctlDiff++;
}
notes._controlCases = ctl;
notes._controlDiffs = ctlDiff;
v.noFogUnchanged = ctlDiff === 0;

/* ── structural: the re-expansion is actually in the shipped turn ── */
/* SOURCE check. The 4,746-case sweep above is the behavioural proof that
   the keep now matches; this only confirms the re-expansion line is still
   in runOppTurn, so a refactor cannot silently drop it. */
v.reExpansionPresentInSource = (function () {
  try {
    const src = runOppTurn.toString();
    const has = src.indexOf('_fogCut') >= 0 && /used\.splice\(_fogCut,0,false\)/.test(src);
    notes._fogCutRefs = (src.match(/_fogCut/g) || []).length;
    return has;
  } catch (e) { notes._structErr = String(e).slice(0, 70); return false; }
})();

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
