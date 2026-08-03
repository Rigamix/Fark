/* apv_commit_hook — famCommitBonus must score identically before and after.
 *
 * P445 moves four cards (short_fuse, bloom, cultivate, vanguard_f) out of
 * famCommitBonus and onto a new `commit` hook. That function is on the scoring
 * path, so the only acceptable evidence is that the same inputs produce the
 * same points.
 *
 * ORDER IS THE RISK, and it is not hypothetical. Today the function does
 * `pts*=2` for short_fuse FIRST and then adds bloom, cultivate and vanguard —
 * so the result is (pts*2)+adds. famFire iterates equipped cards in EQUIP
 * ORDER and offers only ev.add(), so a naive migration would compute
 * ((pts+bloom)*2) whenever short_fuse happened to sit later in the loadout.
 * Same cards, same tiers, different score depending on the order they were
 * drafted in — and no error anywhere.
 *
 * So the hook gets ev.mul() alongside ev.add(), and the caller applies
 * pts*mul + add. That reproduces today's arithmetic exactly AND removes the
 * order dependence that was latent in the hand-written version.
 *
 * THE FIXTURES PIN THE INTERACTIONS, not just the individual cards: every
 * subset that can multiply and add at once, because a bug in the two-phase
 * apply is invisible when only one card is equipped.
 */
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
if (typeof famCommitBonus !== 'function') return { err: 'famCommitBonus is not defined' };

/* dice fixtures: a triple, a straight, and a nothing-special roll */
function die(val, mat) { return { val: val, mat: mat || 'bone' }; }
const ROLLS = {
  triple_jade:   [die(4,'jade'), die(4,'jade'), die(4), die(2), die(6)],
  straight_jade: [die(1,'jade'), die(2), die(3), die(4), die(5)],
  plain:         [die(2), die(3), die(6), die(6), die(4)]
};
const CARDS = ['short_fuse', 'bloom', 'cultivate', 'vanguard_f'];

/* every subset, so multiply-and-add interactions are covered rather than
   assumed - a two-phase apply bug is invisible with one card equipped */
const subsets = [];
for (let m = 0; m < (1 << CARDS.length); m++) {
  subsets.push(CARDS.filter((_, i) => m & (1 << i)));
}

const results = {};
for (const rollName of Object.keys(ROLLS)) {
  for (const set of subsets) {
    for (const rolls of [1, 3]) {           // short_fuse needs turnRollCount>=3
      const sel = ROLLS[rollName].map(d => ({ val: d.val, mat: d.mat, _cult: 0 }));
      G.pF = set.map(id => ({ id: id, tier: 1, charges: 1, state: {} }));
      G.pool = sel.slice();                 // vanguard reads pool[0] / pool[last]
      G.turnRollCount = rolls;
      G._featBloom = 0; G._featJadePend = false;
      let out;
      try { out = famCommitBonus(sel, 1000); } catch (e) { out = 'threw: ' + e; }
      results[rollName + '|' + (set.join('+') || 'none') + '|r' + rolls] = out;
    }
  }
}

G.pF = []; G.turnRollCount = 0;

/* a stable digest so before/after compare in one number as well as per-case */
const keys = Object.keys(results).sort();
let digest = 0;
keys.forEach(k => { const v = results[k];
  digest = (digest * 31 + (typeof v === 'number' ? v : 0)) % 1000000007; });

return {
  cases: keys.length,
  digest: digest,
  results: results,
  verdict: {
    allNumeric: keys.every(k => typeof results[k] === 'number'),
    /* the no-cards case must be untouched at exactly the input */
    noCardsIsIdentity: results['plain|none|r1'] === 1000,
    /* short_fuse alone at 3 rolls doubles, at 1 roll does not */
    shortFuseDoubles: results['plain|short_fuse|r3'] === 2000,
    shortFuseQuietEarly: results['plain|short_fuse|r1'] === 1000
  }
};
