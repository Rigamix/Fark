/* D15 - Mabel's Pinch announces a die it did not take.
 *
 * The clamp `G.numDice=Math.min(G.numDice,5)` is CORRECT and stays: both cards
 * carrying `reduce_first_roll` say "leaving you with five instead of six", so
 * reducing an already-shattered player to four would contradict their own text.
 * D15's own entry corrects two earlier write-ups that proposed exactly that.
 *
 * What was wrong is that the announcement did not depend on the effect. With
 * the player already at five - an obsidian die shattered earlier, or a per-turn
 * penalty already armed - the clamp is a no-op and the game still said
 * "MABEL'S PINCH - 5 DICE!". A message vouching for something that did not
 * happen.
 *
 * TWO ARMS, and the first is the control: at six the card must still fire and
 * still announce. A fix that silenced it everywhere would pass an
 * announcement-only check and break the card.
 *
 * triggerCard is STUBBED TO OBSERVE, not replaced - the probe records what the
 * game chose to announce and hands the call straight back.
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

/* observe the announcements without replacing the card machinery */
const realTrigger = window.triggerCard;
let announced = [];
window.triggerCard = function (cid) { announced.push(cid); return realTrigger.apply(this, arguments); };
/* the chance roll is 50% - force it so the arms are deterministic */
const realRandom = Math.random;

function arm(numDice) {
  announced = [];
  G.oCards = ['mabels_pinch'];
  G.numDice = numDice;
  G.turnRollCount = 0;
  G.phase = 'idle';
  G.pool = [];
  G.kept = [];
  Math.random = function () { return 0; };   /* always inside _rfrChance */
  let err = null;
  try { handleRoll(); } catch (e) { err = String(e).slice(0, 80); }
  Math.random = realRandom;
  return { after: G.numDice, said: announced.indexOf('mabels_pinch') >= 0, err: err };
}

const atSix = arm(6);
const atFive = arm(5);
notes._atSix = atSix;
notes._atFive = atFive;
window.triggerCard = realTrigger;

/* the card is in the pool and the mechanic resolves - otherwise both arms are
   vacuously silent and the probe proves nothing */
const card = typeof getNpcCard === 'function' ? getNpcCard('mabels_pinch') : null;
notes._card = card ? card.effect.mechanic : null;
v.mechanicResolves = !!(card && card.effect.mechanic === 'reduce_first_roll');

/* ARM 1, the control: at six it must still take a die AND still say so */
v.stillFiresAtSix = atSix.after === 5 && atSix.said;
/* ARM 2, the finding: at five it takes nothing, so it must say nothing */
v.silentWhenNothingToTake = atFive.after === 5 && !atFive.said;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
