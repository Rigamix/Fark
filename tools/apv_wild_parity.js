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

/* apv_wild_parity — LAW 6: whatever the player can do, an NPC can do.
 *
 * P489 gives the rival wild-as-option scoring. The player has always had it:
 * every player keep goes through scoreSelection, which scores a wild both ways
 * and keeps the better. The rival called scoreRoll directly and was stuck with
 * the substitution - 23456 with a jade 6 scored 50 for the rival and 750 for
 * the player, off identical dice.
 *
 * TWO ARMS, and the control matters as much as the fix:
 *   CONTROL - with no wild in the dice, _scoreRollBest must be scoreRoll
 *             EXACTLY, on total and on `used`. If it is not, this patch
 *             changed the game everywhere rather than only where wilds are,
 *             and the difficulty delta that follows would be unattributable.
 *   FIX     - with a wild, it must land the PLAYER'S number, not merely a
 *             bigger one. Parity is the ruling; "better" is not the claim.
 */
if (typeof _scoreRollBest !== 'function') return { skip: '_scoreRollBest missing' };
const v = {}, notes = {};

function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}
const sameUsed = (a, b) => a.length === b.length && a.every((x, i) => !!x === !!b[i]);

/* ── CONTROL: no wild present → byte-identical to scoreRoll ── */
let ctlChecked = 0, ctlDiff = 0;
const ctlEx = [];
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const mats = vals.map(() => 'bone');
  let a, b;
  try { a = scoreRoll(vals, [], 0, {}, mats); b = _scoreRollBest(vals, [], 0, {}, mats); }
  catch (e) { continue; }
  ctlChecked++;
  if (a.total !== b.total || !sameUsed(a.used || [], b.used || [])) {
    ctlDiff++;
    if (ctlEx.length < 4) ctlEx.push(vals.join('') + ' roll=' + a.total + ' best=' + b.total);
  }
}
notes._controlRolls = ctlChecked;
notes._controlDiffs = ctlDiff;
notes._controlExamples = ctlEx;
v.controlRan = ctlChecked > 400;
v.noWildIsExactlyScoreRoll = ctlDiff === 0;

/* ── FIX: with a jade on a 6, the rival gets what the player gets ── */
function jadeOnSix(vals) { const i = vals.lastIndexOf(6); return i < 0 ? null : vals.map((_, k) => (k === i ? 'jade' : 'bone')); }

let fixChecked = 0, improved = 0, worse = 0, mismatchPlayer = 0;
const fixEx = [], mmEx = [];
for (let n = 1; n <= 6; n++) for (const vals of multisets(n)) {
  const jm = jadeOnSix(vals); if (!jm) continue;
  let raw, best, plain, nowild;
  try {
    raw  = scoreRoll(vals, [], 0, {}, jm);
    best = _scoreRollBest(vals, [], 0, {}, jm);
    plain  = raw.total;
    nowild = scoreRoll(vals, [], 0, Object.assign({}, {}, {_noWild: true}), jm).total;
  } catch (e) { continue; }
  fixChecked++;
  if (best.total > plain) { improved++; if (fixEx.length < 5) fixEx.push(vals.join('') + ' was=' + plain + ' now=' + best.total); }
  if (best.total < plain) worse++;
  /* the claim is PARITY: the better of the two passes, which is exactly what
     scoreSelection gives the player */
  const expected = Math.max(plain, nowild);
  if (best.total !== expected) { mismatchPlayer++; if (mmEx.length < 4) mmEx.push(vals.join('') + ' got=' + best.total + ' expected=' + expected); }
}
notes._wildRolls = fixChecked;
notes._improved = improved;
notes._worse = worse;
notes._examples = fixEx;
notes._parityMismatches = mmEx;

v.wildArmRan = fixChecked > 300;
v.neverScoresWorse = worse === 0;
v.takesTheBetterPass = mismatchPlayer === 0;
v.wildActuallyImproves = improved > 0;   /* if 0, the fix does nothing and the arm is blind */

/* ── the named case from the ruling, against the PLAYER's own function ── */
const straightMats = [2,3,4,5,6].map((x) => (x === 6 ? 'jade' : 'bone'));
const sRaw  = scoreRoll([2,3,4,5,6], [], 0, {}, straightMats).total;
const sBest = _scoreRollBest([2,3,4,5,6], [], 0, {}, straightMats).total;
const sPlayer = scoreSelection([2,3,4,5,6], [], 0, {}, straightMats);
notes._straight = { wasRival: sRaw, nowRival: sBest, player: sPlayer };
v.straightCaseFixed = sBest > sRaw;
v.rivalNowMatchesPlayerOnStraight = sBest === sPlayer;

/* ── structural: EVERY rival site converted, not just the easy ones ── */
v.allRivalSitesConverted = (function () {
  try {
    const src = runOppTurn.toString();
    const raw = (src.match(/scoreRoll\([^;]{0,90}/g) || [])
      .filter(m => m.indexOf('G.oCards') >= 0 && m.indexOf('_scoreRollBest') < 0);
    notes._unconvertedInOppTurn = raw.length;
    return raw.length === 0;
  } catch (e) { notes._structErr = String(e).slice(0, 70); return false; }
})();

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
