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

/* apv_lane_integrity — a die's LANE must survive its neighbours being removed.
 *
 * Reported: a die taken by a mechanic, then a reroll, and lanes stop holding.
 *
 * The plan's hypothesis was that lane is read from array index at RENDER time.
 * It is not - `_laneOf` returns a stable per-die id and only falls back to
 * indexOf for legacy dice. The architecture is correct. The corruption is at
 * STAMP time, in the pool build:
 *
 *     var hotN = G.numDice || 6;
 *     for (let i = 0; i < hotN; i++)
 *       G.pool.push({ ..., mat:  G.matchDice[i % G.matchDice.length],
 *                          ench: G._enchArr[i % G.matchDice.length],
 *                          lane: i % G.matchDice.length });
 *
 * The loop LENGTH comes from G.numDice; the INDEX comes from
 * G.matchDice.length. When a die is removed and only one of those two is
 * updated, the modulo wraps: six iterations over five lanes yields
 * 0,1,2,3,4,0 - lane 0 duplicated, lane 5 gone, and the sixth die inheriting
 * lane 0's material AND enchant.
 *
 * Of the four G.matchDice.splice sites, only Break decrements G.numDice.
 * Sacrifice and both steal_die paths do not - the same three sites P480 had to
 * fix for _enchArr.
 *
 * These checks are written to FAIL against the shipped code, so the fix has
 * something to turn green rather than being declared correct by inspection.
 */
const v = {}, notes = {};

/* ── 1. the invariant, exhaustive over WHICH lane is removed ── */
function lanesAfterRemoval(removeAt, total, syncNumDice) {
  const matchDice = [];
  for (let i = 0; i < total; i++) matchDice.push('d' + i);
  matchDice.splice(removeAt, 1);
  const numDice = syncNumDice ? matchDice.length : total;   /* the bug: not synced */
  const lanes = [];
  for (let i = 0; i < numDice; i++) lanes.push(i % matchDice.length);
  return lanes;
}
const dup = a => a.length !== new Set(a).size;

let bad = 0, good = 0;
const badEx = [];
for (let removeAt = 0; removeAt < 6; removeAt++) {
  const broken = lanesAfterRemoval(removeAt, 6, false);
  const fixed  = lanesAfterRemoval(removeAt, 6, true);
  if (dup(broken)) { bad++; if (badEx.length < 3) badEx.push('remove@' + removeAt + ' -> [' + broken + ']'); }
  if (!dup(fixed)) good++;
}
notes._removalPositionsTested = 6;
notes._stalePositionsProducingDuplicates = bad;
notes._syncedPositionsClean = good;
notes._examples = badEx;

/* the NEGATIVE control: the broken state must actually reproduce the symptom.
   If this were 0 the test could never detect the bug it is named for. */
v.staleNumDiceReproducesTheBug = bad > 0;
/* and the corrected state must be clean at every removal position */
v.syncedNumDiceIsCleanEverywhere = good === 6;

/* ── 2. material and enchant wrap with it, not just lane ── */
(function () {
  const md = ['jade', 'iron', 'bone', 'bone', 'bone'];   /* 5, after a removal */
  const mats = [];
  for (let i = 0; i < 6; i++) mats.push(md[i % md.length]);
  notes._materialsAfterWrap = mats;
  v.materialWrapsToo = mats[5] === mats[0] && mats[5] === 'jade';
})();

/* ── 3. THE ONE THAT SHOULD FAIL TODAY: every splice site must sync numDice ──
   Structural by necessity - firing four different removal mechanics live is a
   much bigger harness than this. Named for what it checks, per PROBE_AUDIT.md:
   it reads source, it does not observe behaviour. */
v.everySpliceSiteSyncsNumDiceInSource = (function () {
  try {
    const src = document.documentElement.outerHTML;
    const sites = [];
    const re = /G\.matchDice\.splice\(/g;
    let m;
    while ((m = re.exec(src)) !== null) {
      const win = src.slice(m.index, m.index + 320);
      sites.push(/G\.numDice\s*=/.test(win));
    }
    notes._spliceSites = sites.length;
    notes._spliceSitesThatSyncNumDice = sites.filter(Boolean).length;
    return sites.length > 0 && sites.every(Boolean);
  } catch (e) { notes._structErr = String(e).slice(0, 80); return false; }
})();

/* ── 4. the live invariant, as far as it can be checked without firing cards ── */
v.liveNumDiceMatchesMatchDice = (function () {
  try {
    notes._liveNumDice = G.numDice;
    notes._liveMatchDice = (G.matchDice || []).length;
    return G.numDice === (G.matchDice || []).length;
  } catch (e) { return false; }
})();

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
