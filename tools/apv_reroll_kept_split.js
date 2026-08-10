/* D3 - reroll_all_kept rescores from a NON-PARALLEL array, folding a face that
 * banks zero by law back into the score.
 *
 * A kept group is pushed as
 *     {vals: selVals,  dice: selDice.map(...)}
 * where selVals comes from `_splitIcons(selDice).rest` (icons WITHHELD from
 * scoring) and `dice` is the pre-split selection. So `vals` is shorter than
 * `dice` whenever any selected die is showing its branded face, and the two are
 * not index-parallel.
 *
 * The reroll then rebuilds vals FROM dice:
 *     k.dice.forEach(dd => dd.val = rollFace(dd.mat));
 *     k.vals = k.dice.map(dd => dd.val);          <-- icons now included
 *     k.pts  = scoreRoll(k.vals, ...)             <-- and scored
 * turning a punishment card into a multiplier and scoring a face the game's own
 * rule says banks nothing.
 *
 * ASSERTED ROLL-INDEPENDENTLY. The faces are random, so the invariant is the
 * claim, not a points total:
 *
 *     k.vals.length === _splitIcons(k.dice).rest.length   after every reroll
 *
 * Re-split rather than remembered, because that is the correct semantics too: a
 * branded die that rerolls OFF its face stops being an icon and should score
 * again, and one that lands back ON it should not.
 *
 * AND THE INSTRUMENT MUST PROVE IT SAW THE CASE. A run where no die ended on
 * its brand face cannot distinguish the bug from the fix, so the probe counts
 * the trials that actually produced an icon and refuses a verdict on zero.
 *
 * IT MUST ALSO PROVE THE DISPATCH RAN, and the first version did not. It
 * reported all four checks GREEN against the unfixed build, because the pool it
 * built showed [2,3] - no 1, no 5, no triple - so `_afterRollImpl` took the
 * bust path at 26372 and returned long before the NPC card block. The kept
 * group was therefore never touched, and an untouched group is trivially
 * parallel. The tell was in the notes: `sawIcon 40/40`, when flint shows face 1
 * one time in six, so a die that stayed an icon in EVERY trial was plainly
 * never rerolled. `dispatchFired` now gates the whole verdict on the block
 * having incremented its own use counter.
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
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
/* a brand whose icon table the game recognises */
const ICON_T = Object.keys(ENCH_ICONS)[0];
notes._iconType = ICON_T;

/* the group D3 describes: one plain scoring die and one branded die sitting on
   its own face, so vals(1) and dice(2) are already out of step */
function armGroup() {
  const dice = [{val:5, mat:'bone', ench:null},
                {val:1, mat:'flint', ench:{t:ICON_T, face:1}}];
  const rest = _splitIcons(dice).rest;
  G.kept = [{vals: rest.map(d => d.val), mat:'bone', pts:50, dice: dice}];
  return G.kept[0];
}
const armed = armGroup();
notes._armed = { valsLen: armed.vals.length, diceLen: armed.dice.length,
                 iconsAtArm: _splitIcons(armed.dice).icons.length };
v.theGroupStartsNonParallel = armed.vals.length !== armed.dice.length;

/* ── drive the REAL dispatch, N times ─────────────────────────────────── */
let trials = 0, sawIcon = 0, parallelOK = 0, scoredAnIcon = 0, fired = 0;
const examples = [];
for (let n = 0; n < 40; n++) {
  const k = armGroup();
  G.oCards = ['crown_authority'];
  G.npcCardState = G.npcCardState || {}; G.npcCardState.usedOnce = {};
  G.turnNum = 3; G.phase = 'choosing'; G.turnRollCount = 1;
  /* A SCORING POOL, WITH REAL NODES. Two things the first attempts got wrong:
     [2,3] busts, and _afterRollImpl returns at the bust path (26372) before the
     NPC card block ever runs - which is how the very first version passed
     against the broken build. And `el:null` throws on d.el.onclick, which the
     roll path sets. A detached div satisfies every use (classList, onclick,
     _d3); it is a DOM node, not a stand-in for game logic. */
  G.pool = [1, 5].map(function (val, i) {
    return {lane:i, mat:'bone', val:val, committed:false, _frozen:false,
            sel:false, ench:null, el:document.createElement('div')};
  });
  try { _afterRollImpl(); } catch (e) { notes._dispatchErr = String(e).slice(0, 90); break; }
  if ((G.npcCardState.usedOnce['crown_authority'] || 0) > 0) fired++;
  trials++;
  const iconsNow = _splitIcons(k.dice).icons;
  const restNow  = _splitIcons(k.dice).rest;
  if (iconsNow.length) sawIcon++;
  if (k.vals.length === restNow.length) parallelOK++;
  /* the sharp version: is a current icon's face sitting in the scored list? */
  const iconVals = iconsNow.map(d => d.val);
  const folded = iconsNow.length && k.vals.length > restNow.length;
  if (folded) { scoredAnIcon++;
    if (examples.length < 3) examples.push({vals:k.vals.slice(), icons:iconVals, pts:k.pts}); }
}
notes._trials = { trials, fired, sawIcon, parallelOK, scoredAnIcon, examples };

/* THE GATE. Everything below is vacuous if the reroll never ran. */
v.dispatchActuallyFired = trials > 0 && fired === trials;
/* and the reroll must have MOVED faces - sawIcon at 100% means it did not */
v.instrumentSawTheCase = trials > 0 && sawIcon > 0 && sawIcon < trials;
v.valsStayParallelToScoredDice = trials > 0 && parallelOK === trials;
v.noIconFaceIsEverScored = scoredAnIcon === 0;

for (const k2 of Object.keys(v)) { if (k2[0] === '_') { notes[k2] = v[k2]; delete v[k2]; } }
return { verdict: v, notes: notes };
