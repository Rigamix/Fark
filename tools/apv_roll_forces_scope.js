/* D7 - the roll-forces buffer outlives the roll it was armed for, and the turn.
 *
 * famApplyRollForces clears _famPeekVals ONLY inside the branch that applies it:
 *
 *     if(G._famPeekVals && G._famPeekVals.length===free.length){ ...; G._famPeekVals=null; }
 *
 * so a count mismatch leaves it armed. And the mismatch is the NORMAL case, by
 * construction: CFX.stargazer.canUse requires phase==='choosing', and to roll
 * again from 'choosing' you must commit at least one die - so the next roll has
 * strictly fewer free dice than the peek was rolled over. The only equal-count
 * route is hot dice.
 *
 * Honeytrap has no count gate at all, but it is tied to a KEPT PAIR ("tap a
 * kept pair... guaranteed triple"), and banking destroys the pair. Surviving a
 * bank means forcing a face on next turn's opening roll to match a pair that no
 * longer exists.
 *
 * FOUR ARMS, each a separate claim, because "the buffer is stale" is three
 * different bugs wearing one name:
 *   A  a missed peek stays armed          (the roll it was armed for is over)
 *   B  it survives a turn boundary        (so it lands on a later roll)
 *   C  honeytrap survives a bank          (its pair is gone)
 *   D  honeytrap overwrites a peeked die  (the two clobber, same roll)
 *
 * Arm D is CURRENT BEHAVIOUR and is left as a measurement rather than an
 * assertion: honeytrap's promise is the stronger one ("guaranteed"), so it
 * winning is defensible. It is recorded so a later change to the order is a
 * decision rather than a surprise.
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
const mkPool = n => { G.pool = []; for (let i = 0; i < n; i++)
  G.pool.push({lane:i, mat:'bone', val:2, committed:false, _frozen:false, el:null}); };

/* ── A. a peek that cannot apply must not stay armed ─────────────────── */
G.phase = 'choosing'; mkPool(5);
G._famPeekVals = null; G._famHoneyVal = null;
CFX.stargazer.use({tier:1});
notes._peekArmed = (G._famPeekVals || []).slice();
/* the normal case: one die committed, so the next roll has fewer free */
G.pool[0].committed = true;
famApplyRollForces();
notes._afterMismatch = { peek: G._famPeekVals, freeNow: G.pool.filter(d => !d.committed).length };
v.missedPeekIsSpent = G._famPeekVals === null;

/* ── B. and it must not cross a turn boundary ────────────────────────── */
G.phase = 'choosing'; mkPool(5);
G._famPeekVals = null; CFX.stargazer.use({tier:1});
const peekBefore = (G._famPeekVals || []).slice();
try { endPTurn(); } catch (e) { notes._endErr = String(e).slice(0, 80); }
await sleep(400);
notes._peekAcrossTurn = { before: peekBefore, after: G._famPeekVals };
v.peekDoesNotCrossTheTurn = !G._famPeekVals;

/* ── C. honeytrap is tied to a kept pair; banking destroys the pair ──── */
G.phase = 'choosing'; mkPool(4);
G.kept = [{vals:[4,4]}];
G._famHoneyVal = null;
CFX.honeytrap.use({tier:1});
const honeyBefore = G._famHoneyVal;
try { endPTurn(); } catch (e) {}
await sleep(400);
notes._honeyAcrossTurn = { before: honeyBefore, after: G._famHoneyVal, keptAfter: (G.kept||[]).length };
v.honeytrapDoesNotCrossTheTurn = !G._famHoneyVal;

/* ── D. the two, on the same roll - MEASURED, not asserted ───────────── */
G.phase = 'choosing'; mkPool(3);
G._famPeekVals = [1, 1, 1]; G._famHoneyVal = 6;
famApplyRollForces();
notes._clobber = { vals: G.pool.map(d => d.val),
  reading: G.pool[0].val === 6 ? 'honeytrap wins lane 0 (current, defensible - its promise is the stronger)'
         : 'the peek held lane 0' };

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
