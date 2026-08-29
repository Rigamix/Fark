/* SUPERSEDED IN PART BY tools/apv_frozen_vs_sacrifice.js - READ THIS FIRST.
 *
 * This probe's headline verdict is `wholeLegacyActiveLayerIsDead`, and that
 * WAS true when it was written and is NOT true now. The boss-reward brief's
 * section 2 re-pointed the eight boss cards onto the surviving CARDS actives,
 * so frozen_die IS Brutus's Grip: won from his spoils, equipped in the boss
 * slot, and able to freeze a die for the first time.
 *
 * The verdict still returns true here only because this probe drives an EMPTY
 * loadout, where nothing is activatable by definition. Scoped that narrowly it
 * is still a true statement; read as a headline it is reassurance about a world
 * that has moved, which is the more expensive kind of stale.
 *
 * The live question - can Sacrifice destroy a die the player has frozen - is
 * re-asked against the mechanism in apv_frozen_vs_sacrifice.js, with Brutus's
 * Grip actually equipped. Answer: no. CFX.sacrifice._targets() carries
 * `!d._frozen`, so the D18 defect was fixed after this probe was written, and
 * that exclusion is what is load-bearing now that the layer is reachable.
 */
/* D18 - "Transmute and Sacrifice both admit `_frozen` dice; every other card
 * excludes them", and Sacrifice has no targeting, so a held die can be
 * destroyed without being chosen.
 *
 * TWO HALVES, AND ONLY ONE SURVIVES READING.
 *
 * Transmute is a NON-FINDING. Its `use` runs `var d=free[pick-1]` - the player
 * picks. A card with targeting that lets you transmute your own held die is a
 * choice, not a defect. The entry paired it with Sacrifice on the strength of
 * the filter alone.
 *
 * Sacrifice is real: `_targets()` is `!committed && !_shattered && lane!==ftLane`
 * and `use` takes `free[free.length-1]` with no prompt at all. That filter has
 * been curated - it carves out the loan lane and the one-die floor - so `_frozen`
 * was not excluded on purpose, it was never considered.
 *
 * BUT IS IT REACHABLE? `_frozen` has exactly two writers, both inside the legacy
 * player-active layer that OPEN section 1c reports dead:
 *
 *     25761  Gambler's Eye resolution, behind G._gamblersEyeActive
 *     32515  activateFrozenDie
 *
 * Both are entered only through `activateCard`, whose gate needs
 * `usedCards[cardId] > 0` against a `pCards` that `initMatchScreen` declares
 * empty. A GREP CANNOT SETTLE THAT - seven zeros from name searches became
 * claims in this project - so this probe DRIVES the gate instead of reading it,
 * and asks the running game three questions:
 *
 *   A  is any die on a live table frozen after a normal roll?
 *   B  does the activation gate admit either freezing card?
 *   C  CONTROL: does the gate admit ANYTHING? If it refuses every id including
 *      ones that are supposed to work, then "refuses gamblers_eye" measures a
 *      broken harness rather than a dead layer, and the arm is void.
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

/* A - roll for real and look at the table */
tap(document.getElementById('btnRoll'));
await until(() => G && (G.pool || []).length > 0, 9000);
await sleep(900);
const pool = G.pool || [];
notes._armA = { poolLen: pool.length, frozen: pool.filter(d => d._frozen).length,
                phase: G.phase, gamblersEyeActive: !!G._gamblersEyeActive,
                frozenDie: G._frozenDie || null };
v.rolledTableHasNoFrozenDie = pool.length > 0 && pool.filter(d => d._frozen).length === 0;

/* B/C - the activation gate, driven. `gamblers_eye` and `frozen_die` are the
   two freezing cards; the controls are ids from the layers that ARE live. */
function gate(id) {
  try { return { canActivate: !!(typeof canActivateCard === 'function' && canActivateCard(id)),
                 uses: ((G.activeCardState && G.activeCardState.usedCards) || {})[id] }; }
  catch (e) { return { err: String(e).slice(0, 60) }; }
}
const IDS = ['gamblers_eye', 'frozen_die', 'double_down', 'seven_dice', 'grogs_flask'];
const gates = {}; IDS.forEach(id => { gates[id] = gate(id); });
let eff = null; try { eff = (effectiveCards() || []).slice(0, 12); } catch (e) { eff = 'err'; }
let pc2 = null; try { pc2 = (G.pCards || []).slice(0, 12); } catch (e) {}
notes._armBC = { gates: gates, effectiveCards: eff, pCards: pc2,
                 usedCards: Object.keys((G.activeCardState && G.activeCardState.usedCards) || {}) };

v.neitherFreezingCardCanBeActivated = !gates.gamblers_eye.canActivate && !gates.frozen_die.canActivate;
/* THE VOID CHECK. If NOTHING in the legacy list activates, that is the dead
   layer OPEN 1c describes and the arm above is a statement about the layer, not
   about these two cards. Reported separately so the distinction is visible
   rather than folded into a pass. */
v.wholeLegacyActiveLayerIsDead = IDS.every(id => !gates[id].canActivate);

/* and the filters themselves, read off the live objects rather than the source */
let sacTargets = null, sacExcludesFrozen = null;
try {
  G.pool.forEach(d => { d._frozen = false; });
  const before = CFX.sacrifice._targets().length;
  G.pool.filter(d => !d.committed)[0]._frozen = true;
  const after = CFX.sacrifice._targets().length;
  sacTargets = { before: before, after: after };
  sacExcludesFrozen = after === before - 1;
  G.pool.forEach(d => { d._frozen = false; });
} catch (e) { notes._sacErr = String(e).slice(0, 80); }
notes._sacrifice = { targets: sacTargets, excludesFrozen: sacExcludesFrozen };
v.sacrificeExcludesAFrozenDie = !!sacExcludesFrozen;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
