/* apv_two_seams — the deadRoll and rivalTurn hooks (P446).
 *
 * WHAT IS TESTED DETERMINISTICALLY AND WHAT IS NOT, stated up front so a green
 * result is not read as more than it is:
 *
 *   rivalTurn  FULLY. Ill Omen's payout is pure arithmetic on G.pPts/G.oPts
 *              given the rival's score, so both branches are pinned exactly.
 *   deadRoll   THE SEAM, NOT THE REROLL. famFoolsGold rerolls real dice and
 *              claims only if the new roll scores, so whether it claims is a
 *              coin toss. What IS deterministic - and what actually broke when
 *              this moved onto a hook - is the plumbing: does a claim cancel
 *              the bust, does no-card mean no-claim, does a spent card decline.
 *              The reroll itself is unchanged code called from a new place.
 *
 * That distinction is the point. A probe that drove a real dead roll would pass
 * or fail on the dice and tell you nothing about the hook.
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
if (typeof famFire !== 'function' || !CFX.ill_omen || !CFX.ill_omen.rivalTurn) {
  return { err: 'the rivalTurn hook is not wired' };
}

const out = {};

/* ── rivalTurn: Ill Omen lands when the rival scored nothing ── */
const P = famDef('ill_omen').p[0];          // tier I payload [take, miss]
G.pF = [{ id: 'ill_omen', tier: 1, charges: 1, state: {} }];
G.pPts = 1000; G.oPts = 1000; G._famIllOmen = { tier: 1 };
famFire('rivalTurn', { actor: 'p', pts: 0 });
out.landed = { p: G.pPts, o: G.oPts, cleared: G._famIllOmen === null };
out.landedExpect = { p: 1000 + Math.min(P[0], 1000), o: 1000 - Math.min(P[0], 1000) };

/* ── and misses when they scored ── */
G.pPts = 1000; G.oPts = 1000; G._famIllOmen = { tier: 1 };
famFire('rivalTurn', { actor: 'p', pts: 500 });
out.missed = { p: G.pPts, o: G.oPts, cleared: G._famIllOmen === null };
out.missedExpect = { p: 1000, o: 1000 + P[1] };

/* ── it does nothing when never declared ── */
G.pPts = 1000; G.oPts = 1000; G._famIllOmen = null;
famFire('rivalTurn', { actor: 'p', pts: 0 });
out.undeclared = { p: G.pPts, o: G.oPts };

/* ── deadRoll: the CLAIM plumbing, which is what the move could break ── */
G.pF = [];
let ev = { actor: 'p', free: [] };
famFire('deadRoll', ev);
out.noCardNoClaim = (ev._claimed === false);

/* a spent card must decline: charges 0 -> famFoolsGold returns false */
G.pF = [{ id: 'fools_gold_f', tier: 1, charges: 0, state: {} }];
ev = { actor: 'p', free: [] };
famFire('deadRoll', ev);
out.spentCardNoClaim = (ev._claimed === false);

/* and a claim must actually set the flag the call site reads */
const saved = CFX._probeTmp;
CFX._probeTmp = { deadRoll: function (e) { e.claim(); } };
G.pF = [{ id: '_probeTmp', tier: 1, charges: 1, state: {} }];
ev = { actor: 'p', free: [] };
famFire('deadRoll', ev);
out.claimSetsFlag = (ev._claimed === true);
if (saved === undefined) delete CFX._probeTmp; else CFX._probeTmp = saved;

/* every existing hook must be unaffected by the new verbs */
const ev2 = { actor: 'p' };
famFire('turnStart', ev2);
out.mulDefaultsToOne = (ev2._mul === 1);
out.claimDefaultsFalse = (ev2._claimed === false);

G.pF = []; G._famIllOmen = null;

const eq = (a, b) => a.p === b.p && a.o === b.o;
return {
  ...out,
  verdict: {
    omenLands:        eq(out.landed, out.landedExpect) && out.landed.cleared,
    omenMisses:       eq(out.missed, out.missedExpect) && out.missed.cleared,
    omenInertIfUndeclared: out.undeclared.p === 1000 && out.undeclared.o === 1000,
    noCardNoClaim:    out.noCardNoClaim === true,
    spentCardNoClaim: out.spentCardNoClaim === true,
    claimSetsFlag:    out.claimSetsFlag === true,
    mulDefaultsToOne: out.mulDefaultsToOne === true,
    claimDefaultsFalse: out.claimDefaultsFalse === true
  }
};
