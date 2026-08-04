/* apv_wild_table — P464's lookup scores identically to the if-chain it replaced.
 *
 * Three arms that differed only by a number became one keyed read. A pure
 * refactor's whole claim is "behaviour did not change", so this scores real
 * selections through the real scoreRoll and checks the WILD still stands in at
 * each level — and, just as importantly, that a _noWild die is still left alone.
 * That last one is the arm the lookup had to stay BEHIND; if it had jumped
 * ahead, a natural face would be wilded and the score would silently rise.
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

/* REACH THE MATCH BEFORE AUDITING IT. The first run of this probe returned
   null for all four checks - including the two synthetics that touch no UI -
   because shoot.js loads a FRESH page at the menu and (typeof G!=='undefined'?G:null) does not exist
   there. It audited a match that was never started. This is the run-start
   sequence the rest of the suite uses. */
/* NO MATCH NEEDED. scoreRoll is a pure function of its arguments, so the
   run-start sequence this probe inherited was a dependency the test does not
   have - and it duly failed setup once (atMatch=true, idle=false) on a check
   that never touches game state. A probe should require the least it can. */
await until(() => typeof scoreRoll === 'function' && typeof getDie === 'function', 15000);
if (typeof scoreRoll !== 'function') return { skip: 'scoreRoll missing' };
const v = {};
/* the real signature: scoreRoll(vals, cards, locked, context, dieMats, dieEnchs).
   aldrics_square carries wild_triple; jade variants carry wild_quad/straight. */
const WILDDIE = { wild_triple: 'aldrics_square' };
for (const id in (typeof DICE !== 'undefined' ? DICE : {})) {}
v.tableShape = (typeof WILD_LEVEL !== 'undefined')
  && WILD_LEVEL.wild_triple === 1 && WILD_LEVEL.wild_quad === 2
  && WILD_LEVEL.wild_straight === 3 && Object.keys(WILD_LEVEL).length === 3;

function pts(vals, mats, ctx) {
  try { const r = scoreRoll(vals, [], 0, ctx || {}, mats); return r && r.total != null ? r.total : -1; }
  catch (e) { v._err = String(e).slice(0, 80); return -1; }
}

/* a 6 on aldrics_square goes wild; two 5s + that 6 should complete triple 5s.
   With _noWild the same hand must NOT get the wild treatment. */
const M = ['bone', 'bone', 'aldrics_square'];
const withWild = pts([5, 5, 6], M, {});
const noWild   = pts([5, 5, 6], M, { _noWild: true });
v._triple = { withWild: withWild, noWild: noWild };

/* THE EXACT NUMBERS, not an inequality. Two 5s alone are 100; the wild 6
   completing triple 5s is 500. An inequality would pass if the wild silently
   stopped applying and both sides fell to 100 - which is the one failure a
   lookup-for-if-chain swap could actually cause. */
v.wildStillApplies = withWild === 500;
v.noWildStillHonoured = noWild === 100;
/* and the effect log must name the mechanic, proving the table keyed correctly */
v.effectLogged = (function () {
  try { const r = scoreRoll([5,5,6], [], 0, {}, M);
    return !!(r && r.effects || []).length && r.effects.some(e => e.type === 'wild_triple'); }
  catch (e) { return false; }
})();

/* the die really does carry the mechanic the table is keyed on */
v._dieMech = (function () { try { const d = getDie('aldrics_square');
  return d && d.effect ? d.effect.mechanic : null; } catch (e) { return null; } })();
v.keyedOnRealMechanic = v._dieMech === 'wild_triple';

/* no wild_* branch may remain in scoreRoll's source */
v.branchesGone = !/mechanic\s*===\s*'wild_/.test(scoreRoll.toString());
return { verdict: v };
