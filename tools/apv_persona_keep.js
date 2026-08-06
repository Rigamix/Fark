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

/* apv_persona_keep — the six keep policies, each checked against its DEFINING
 * property over every roll, not against a few hand-picked hands.
 *
 * The set-up makes one question the only question: the maximal keep is always
 * the full set of scoring dice and it is unique, so choosing is always choosing
 * to score less now for more dice live.
 *
 * straights is the CORRECTED policy: a five-run pays 500-750 against 1500 for
 * the full six, so it protects a secured five and pushes only the remainder.
 * combo deliberately holds at maximal - its value-per-live-die has not been
 * measured, and a placeholder would only be re-derived later.
 */
if (typeof _npcChooseKeep !== 'function') return { skip: '_npcChooseKeep missing' };
const v = {}, notes = {};

function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}
const rung = p => ({ persona: p });

const fail = {}, seen = {};
['hoard','aggro','straights','triples','ones','combo'].forEach(p => { fail[p] = 0; seen[p] = 0; });
let sets = 0, notFromSet = 0, nullPick = 0;

for (let n = 2; n <= 6; n++) for (const vals of multisets(n)) {
  const free = vals.map(x => ({ val: x, mat: 'bone' }));
  let K; try { K = _legalKeeps(free, 'o', 0); } catch (e) { continue; }
  if (!K.length) continue;
  sets++;
  const maxPts  = Math.max.apply(null, K.map(k => k.pts));
  const maxLeft = Math.max.apply(null, K.map(k => k.left));
  const anyFive = K.some(k => k.runLen >= 5);
  const anyTrip = K.some(k => k.isTriple);
  const anyLive = K.some(k => k.left >= 1);

  for (const p of ['hoard','aggro','straights','triples','ones','combo']) {
    let pick; try { pick = _npcChooseKeep(K, rung(p)); } catch (e) { fail[p]++; continue; }
    if (!pick) { nullPick++; continue; }
    if (K.indexOf(pick) < 0) { notFromSet++; continue; }
    seen[p]++;
    let ok = true;
    if (p === 'hoard' || p === 'combo') ok = pick.pts === maxPts;
    else if (p === 'aggro') ok = pick.left === maxLeft;
    else if (p === 'straights') ok = anyFive ? pick.runLen >= 5 : pick.pts === maxPts;
    else if (p === 'triples')  ok = anyTrip ? pick.isTriple === true : pick.pts === maxPts;
    else if (p === 'ones')     ok = anyLive ? pick.left >= 1 : true;
    if (!ok) fail[p]++;
  }
}
notes._candidateSets = sets;
notes._violations = fail;
notes._evaluated = seen;
notes._pickNotInSet = notFromSet;
notes._nullPicks = nullPick;

v.sweepRan = sets > 500;
v.everyPickComesFromTheCandidateSet = notFromSet === 0 && nullPick === 0;
v.hoardTakesMaximal      = fail.hoard === 0;
v.aggroLeavesMostDiceLive= fail.aggro === 0;
v.straightsProtectsAFive = fail.straights === 0;
v.triplesPrefersATriple  = fail.triples === 0;
v.onesNeverEmptiesTheHand= fail.ones === 0;
v.comboHoldsAtMaximal    = fail.combo === 0;

/* THE POLICIES MUST ACTUALLY DIFFER. If every persona picked the same keep the
   checks above would all pass while the feature did nothing - the same
   false-clean shape as a sweep whose inputs never reach the code. */
let differing = 0, compared = 0;
for (let n = 3; n <= 6; n++) for (const vals of multisets(n)) {
  const free = vals.map(x => ({ val: x, mat: 'bone' }));
  let K; try { K = _legalKeeps(free, 'o', 0); } catch (e) { continue; }
  if (K.length < 2) continue;
  compared++;
  const picks = ['hoard','aggro','straights','triples','ones'].map(p => K.indexOf(_npcChooseKeep(K, rung(p))));
  if (new Set(picks).size > 1) differing++;
}
notes._rollsCompared = compared;
notes._rollsWherePersonasDiffer = differing;
v.personasActuallyDiffer = differing > 0;

/* and a named case, so the corrected straights rule is legible */
const sFree = [1,2,3,4,5,1].map(x => ({ val: x, mat: 'bone' }));
const sK = _legalKeeps(sFree, 'o', 0);
const sPick = _npcChooseKeep(sK, rung('straights'));
const aPick = _npcChooseKeep(sK, rung('aggro'));
notes._straightCase = { runLen: sPick.runLen, pts: sPick.pts, left: sPick.left,
                        aggroPts: aPick.pts, aggroLeft: aPick.left };
v.straightsSecuresTheRunNotTheScraps = sPick.runLen >= 5;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
