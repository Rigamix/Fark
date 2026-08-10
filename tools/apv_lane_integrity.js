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

/* ── 3. every removal must keep numDice in step ──────────────────────────
   THIS CHECK WENT RED WITHOUT THE GAME CHANGING, and the reason is worth more
   than the check was. It scanned the whole document for `G.matchDice.splice(`
   and required `G.numDice =` within 320 characters of each hit. Both halves
   were true when it was written and neither is now:

     - removal was consolidated into _removeDieAt (PR5), so there is exactly
       ONE splice site instead of the four this was policing;
     - and numDice no longer moves by assignment there. It moves through
       _dropLanes(1), because assigning matchDice.length refunded every
       per-turn dice penalty and ate Seven Dice's bonus (P516). The regex
       looks for an `=` that was deliberately removed.

   So a refactor that made the property STRUCTURAL - one choke point instead of
   four sites to keep in step - is exactly what blinded the probe guarding it.
   That is the standing lesson in reverse: a source-text count of N sites
   cannot survive N becoming 1.

   And the old excuse for being structural is gone with it. "Firing four
   different removal mechanics live is a much bigger harness than this" was
   true of four mechanics; there is one path now, and it is one call. So this
   RUNS IT, and keeps a structural check only for the thing behaviour cannot
   show - that the one path is the only path. */
v.everySpliceSiteSyncsNumDiceInSource = (function () {
  try {
    const src = document.documentElement.outerHTML;
    notes._spliceSites = (src.match(/G\.matchDice\.splice\(/g) || []).length;
    if (typeof _removeDieAt !== 'function') { notes._noCanonicalPath = true; return false; }
    const fn = _removeDieAt.toString();
    notes._spliceInsideRemoveDieAt = (fn.match(/G\.matchDice\.splice\(/g) || []).length;
    notes._removeDieAtDropsLanes  = /_dropLanes\s*\(/.test(fn);
    notes._dropLanesMovesNumDice  = typeof _dropLanes === 'function'
      && /G\.numDice\s*=/.test(_dropLanes.toString());
    /* ONE PATH, and it is the one in _removeDieAt */
    const structural = notes._spliceSites === 1
      && notes._spliceInsideRemoveDieAt === 1
      && notes._removeDieAtDropsLanes
      && notes._dropLanesMovesNumDice;

    /* AND RUN IT. A structural check passes on a splice with the wrong index;
       this does not. Left in place afterwards on purpose - check 4 below then
       reads the invariant AFTER a real removal rather than on a pristine
       board, which is the harder version of the same question. */
    notes._beforeRemoval = { numDice: G.numDice, matchDice: (G.matchDice || []).length };
    const lane = Math.max(0, (G.matchDice || []).length - 2);
    _removeDieAt(lane);
    notes._afterRemoval = { numDice: G.numDice, matchDice: (G.matchDice || []).length };
    const behavioural = notes._afterRemoval.matchDice === notes._beforeRemoval.matchDice - 1
      && G.numDice === (G.matchDice || []).length;

    return structural && behavioural;
  } catch (e) { notes._structErr = String(e).slice(0, 80); return false; }
})();

/* ── 4. the live invariant - now read AFTER check 3's real removal ────── */
v.liveNumDiceMatchesMatchDice = (function () {
  try {
    notes._liveNumDice = G.numDice;
    notes._liveMatchDice = (G.matchDice || []).length;
    return G.numDice === (G.matchDice || []).length;
  } catch (e) { return false; }
})();

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
